"""Complete simulated purchase transaction and per-attempt audit guarantee."""

import re
import secrets
from typing import NamedTuple

from . import audit, catalog, inventory
from .errors import (
    DuplicateConflict,
    EventHubError,
    InvalidQuantity,
    InvalidRequestToken,
    PurchaseLimit,
    UnsupportedCurrency,
)
from .pricing import CURRENCY_DIGITS, compute_quote, eligible_for_usf_discount

TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{16,64}$")
STALE_PAGE = "This page is out of date. Please reload the event page and try again."


class PurchaseResult(NamedTuple):
    order_id: int
    duplicate: bool


def parse_quantity(raw):
    if type(raw) is int:
        value = raw
    elif isinstance(raw, str) and raw.isascii() and raw.isdecimal() and len(raw) <= 5:
        value = int(raw)
    else:
        raise InvalidQuantity("Invalid quantity: enter a positive whole number")
    if not 1 <= value <= 10000:
        raise InvalidQuantity("Invalid quantity: must be between 1 and 10,000")
    return value


def parse_token(raw, *, required=False):
    """The one-time purchase token printed into every checkout and quick-buy form."""
    if raw is None or raw == "":
        if required:
            raise InvalidRequestToken(STALE_PAGE)
        return None
    if not isinstance(raw, str) or not TOKEN_PATTERN.fullmatch(raw):
        raise InvalidRequestToken(STALE_PAGE)
    return raw


def purchase(conn, **kwargs):
    """Compatibility wrapper for callers that only need the order id."""
    return place_order(conn, **kwargs).order_id


def place_order(
    conn,
    *,
    account_id,
    event_id,
    quantity,
    currency,
    discount_percent=None,
    purchase_cap=None,
    simulated_payment="success",
    request_token=None,
    require_token=False,
):
    """Guarantees one audit per authenticated attempt, even on rollback.

    BEGIN IMMEDIATE serializes SQLite writers. Inventory check and order/audit
    inserts commit as one unit; errors rollback, then log the failure separately.

    Call 5 (double purchase): a request that repeats the purchase token of an order
    this account already holds creates no second order and takes no more tickets.
    It returns the original order with duplicate=True. The check runs inside the
    write lock, so two simultaneous submits of one token also produce one order.
    """
    try:
        parsed_event = int(event_id)
    except (ValueError, TypeError):
        parsed_event = None
    parsed_quantity = None
    try:
        parsed_quantity = parse_quantity(quantity)
        token = parse_token(request_token, required=require_token)
        if currency not in CURRENCY_DIGITS:
            raise UnsupportedCurrency("Unsupported currency")
        if simulated_payment != "success":
            raise EventHubError("Simulated payment was declined")
        conn.execute("BEGIN IMMEDIATE")
        buyer = conn.execute(
            "SELECT * FROM accounts WHERE id=?", (account_id,)
        ).fetchone()
        if buyer is None:
            raise EventHubError("Unknown account")
        if token:
            prior = conn.execute(
                """SELECT id, event_id, quantity, currency FROM orders
                WHERE account_id=? AND request_token=?""",
                (account_id, token),
            ).fetchone()
            if prior is not None:
                if (prior["event_id"], prior["quantity"], prior["currency"]) != (
                    parsed_event,
                    parsed_quantity,
                    currency,
                ):
                    raise DuplicateConflict(
                        "This purchase token was already used for a different purchase. "
                        "Please reload the page."
                    )
                audit.record(
                    conn,
                    kind="purchase",
                    account_id=account_id,
                    event_id=parsed_event,
                    quantity=parsed_quantity,
                    currency=currency,
                    outcome="duplicate_suppressed",
                    detail=f"order={prior['id']}",
                )
                conn.commit()
                return PurchaseResult(prior["id"], True)
        event = catalog.get_event(conn, parsed_event)
        if purchase_cap is not None:
            already = conn.execute(
                """SELECT COALESCE(SUM(quantity),0) FROM orders
                 WHERE account_id=? AND event_id=?""",
                (account_id, parsed_event),
            ).fetchone()[0]
            if already + parsed_quantity > purchase_cap:
                raise PurchaseLimit("Purchase limit reached for this event")
        rate = conn.execute(
            "SELECT units_per_usd FROM rates WHERE currency=?", (currency,)
        ).fetchone()
        if rate is None:
            raise UnsupportedCurrency("Unsupported currency")
        # Eligibility is judged from the buyer's email as it is right now, inside this
        # transaction, never from a result remembered earlier (pricing-015).
        quote = compute_quote(
            event["base_price_minor"],
            parsed_quantity,
            eligible_for_usf_discount(buyer["email"]),
            currency,
            rate["units_per_usd"],
            discount_percent,
        )
        inventory.take_tickets(conn, parsed_event, parsed_quantity)
        code = secrets.token_urlsafe(20)
        cursor = conn.execute(
            """INSERT INTO orders(account_id,event_id,quantity,currency,rate,
            discount_percent,total_minor,confirmation_code,unit_usd_minor,request_token)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (
                account_id,
                parsed_event,
                parsed_quantity,
                currency,
                quote.rate,
                quote.discount_percent,
                quote.total_minor,
                code,
                event["base_price_minor"],
                token,
            ),
        )
        audit.record(
            conn,
            kind="purchase",
            account_id=account_id,
            event_id=parsed_event,
            quantity=parsed_quantity,
            currency=currency,
            outcome="success",
            detail=f"order={cursor.lastrowid}",
        )
        conn.commit()
        return PurchaseResult(cursor.lastrowid, False)
    except Exception as exc:
        if conn.in_transaction:
            conn.rollback()
        audit.record(
            conn,
            kind="purchase",
            account_id=account_id,
            event_id=parsed_event,
            quantity=parsed_quantity,
            currency=str(currency)[:20],
            outcome=getattr(exc, "code", "failed"),
            detail=str(exc)[:250],
        )
        raise


def cancel_checkout(conn, *, account_id, event_id):
    audit.record(
        conn,
        kind="checkout",
        account_id=account_id,
        event_id=event_id,
        quantity=None,
        currency=None,
        outcome="abandoned",
        detail="buyer cancelled or left",
    )


def orders_for(conn, account_id):
    return conn.execute(
        """SELECT o.*, e.artist, e.venue, e.starts_at
        FROM orders o JOIN events e ON e.id=o.event_id
        WHERE o.account_id=? ORDER BY o.id DESC""",
        (account_id,),
    ).fetchall()


def order_for(conn, account_id, order_id):
    return conn.execute(
        """SELECT o.*, e.artist, e.venue, e.starts_at
        FROM orders o JOIN events e ON e.id=o.event_id
        WHERE o.account_id=? AND o.id=?""",
        (account_id, order_id),
    ).fetchone()


def redeem(conn, confirmation_code):
    """Single-use door redemption, available only to administrator routes."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        c = conn.execute(
            """UPDATE orders SET checked_in_at=CURRENT_TIMESTAMP
              WHERE confirmation_code=? AND checked_in_at IS NULL""",
            (confirmation_code,),
        )
        if c.rowcount != 1:
            raise EventHubError("Ticket not found or already checked in")
        row = conn.execute(
            "SELECT * FROM orders WHERE confirmation_code=?", (confirmation_code,)
        ).fetchone()
        conn.commit()
        return row
    except Exception:
        conn.rollback()
        raise

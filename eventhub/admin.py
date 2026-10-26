"""Administrator-only service methods; routes enforce roles separately."""

from decimal import Decimal
from .pricing import CURRENCY_DIGITS, validate_rate
from .errors import UnsupportedCurrency
from . import audit


def change_rate(conn, account_id, currency, rate):
    if currency not in CURRENCY_DIGITS:
        raise UnsupportedCurrency("Unsupported currency")
    validated = validate_rate(rate)
    if currency == "USD" and Decimal(validated) != 1:
        raise ValueError("The USD reference exchange rate must stay at 1")
    conn.execute("BEGIN IMMEDIATE")
    try:
        previous = conn.execute(
            "SELECT units_per_usd FROM rates WHERE currency=?", (currency,)
        ).fetchone()
        if previous is None:
            raise UnsupportedCurrency("Unsupported currency")
        conn.execute(
            "UPDATE rates SET units_per_usd=?, updated_at=CURRENT_TIMESTAMP WHERE currency=?",
            (validated, currency),
        )
        audit.record(
            conn,
            kind="rate_change",
            account_id=account_id,
            event_id=None,
            quantity=None,
            currency=currency,
            outcome="changed",
            detail=f"{previous['units_per_usd']} -> {validated}",
        )
        conn.commit()
    except BaseException:
        conn.rollback()
        raise

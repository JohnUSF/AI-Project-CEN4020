"""Thuy: 'If the buy button fires twice, do we create two orders? Nothing defines it.'

Defined in Call 5 follow-up as purchase-024: one order, the original confirmation again.
"""

from concurrent.futures import ThreadPoolExecutor

import pytest

from eventhub import purchase
from eventhub.db import connect
from eventhub.errors import (
    DuplicateConflict,
    InvalidRequestToken,
    PurchaseLimit,
    SoldOut,
)
from .conftest import add_account

TOKEN = "token-abcdefghijklmnop"


def stock(conn, event=1):
    return conn.execute("SELECT available FROM events WHERE id=?", (event,)).fetchone()[
        0
    ]


def audit_outcomes(conn):
    return [r[0] for r in conn.execute("SELECT outcome FROM audit ORDER BY id")]


@pytest.mark.req("purchase-024", "audit-008")
@pytest.mark.call5
def test_same_token_twice_gives_one_order_one_stock_change_and_two_audit_rows(
    connection,
):
    uid = add_account(connection)
    first = purchase.place_order(
        connection,
        account_id=uid,
        event_id=1,
        quantity="2",
        currency="USD",
        request_token=TOKEN,
    )
    second = purchase.place_order(
        connection,
        account_id=uid,
        event_id=1,
        quantity="2",
        currency="USD",
        request_token=TOKEN,
    )
    assert first.duplicate is False and second.duplicate is True
    assert first.order_id == second.order_id
    assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 1
    assert stock(connection) == 118
    assert audit_outcomes(connection) == ["success", "duplicate_suppressed"]


@pytest.mark.req("purchase-026")
@pytest.mark.call5
@pytest.mark.parametrize(
    "quantity,event,currency", [("3", 1, "USD"), ("2", 2, "USD"), ("2", 1, "EUR")]
)
def test_replaying_a_token_for_a_different_purchase_is_refused(
    connection, quantity, event, currency
):
    uid = add_account(connection)
    purchase.place_order(
        connection,
        account_id=uid,
        event_id=1,
        quantity="2",
        currency="USD",
        request_token=TOKEN,
    )
    with pytest.raises(DuplicateConflict):
        purchase.place_order(
            connection,
            account_id=uid,
            event_id=event,
            quantity=quantity,
            currency=currency,
            request_token=TOKEN,
        )
    assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 1
    assert stock(connection) == 118 and stock(connection, 2) == 80
    assert audit_outcomes(connection)[-1] == "duplicate_conflict"


@pytest.mark.req("purchase-024")
@pytest.mark.whitebox
def test_a_token_belongs_to_one_account(connection):
    a, b = (
        add_account(connection, "a@example.com"),
        add_account(connection, "b@example.com"),
    )
    ra = purchase.place_order(
        connection,
        account_id=a,
        event_id=1,
        quantity=1,
        currency="USD",
        request_token=TOKEN,
    )
    rb = purchase.place_order(
        connection,
        account_id=b,
        event_id=1,
        quantity=1,
        currency="USD",
        request_token=TOKEN,
    )
    assert ra.order_id != rb.order_id and not rb.duplicate


@pytest.mark.req("purchase-028", "audit-008")
@pytest.mark.call5
@pytest.mark.parametrize(
    "bad", [None, "", "short", "has spaces in it!!!", "x" * 65, "semi;colon-0123456789"]
)
def test_a_form_without_a_valid_token_is_rejected_when_required(connection, bad):
    uid = add_account(connection)
    with pytest.raises(InvalidRequestToken):
        purchase.place_order(
            connection,
            account_id=uid,
            event_id=1,
            quantity=1,
            currency="USD",
            request_token=bad,
            require_token=True,
        )
    assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0
    assert stock(connection) == 120
    assert audit_outcomes(connection) == ["invalid_request_token"]


@pytest.mark.req("purchase-024")
@pytest.mark.whitebox
def test_a_duplicate_does_not_trip_the_purchase_limit(connection):
    uid = add_account(connection)
    purchase.place_order(
        connection,
        account_id=uid,
        event_id=1,
        quantity=2,
        currency="USD",
        purchase_cap=2,
        request_token=TOKEN,
    )
    again = purchase.place_order(
        connection,
        account_id=uid,
        event_id=1,
        quantity=2,
        currency="USD",
        purchase_cap=2,
        request_token=TOKEN,
    )
    assert again.duplicate
    with pytest.raises(PurchaseLimit):  # a genuinely new purchase still is
        purchase.place_order(
            connection,
            account_id=uid,
            event_id=1,
            quantity=1,
            currency="USD",
            purchase_cap=2,
            request_token="another-token-0123456",
        )


@pytest.mark.req("purchase-024")
@pytest.mark.whitebox
def test_a_failed_attempt_leaves_the_token_reusable(connection):
    """Tokens are stored on orders only, so a sold-out try can be retried after a restock."""
    uid = add_account(connection)
    connection.execute("UPDATE events SET available=0 WHERE id=1")
    with pytest.raises(SoldOut):
        purchase.place_order(
            connection,
            account_id=uid,
            event_id=1,
            quantity=1,
            currency="USD",
            request_token=TOKEN,
        )
    connection.execute("UPDATE events SET available=5 WHERE id=1")
    result = purchase.place_order(
        connection,
        account_id=uid,
        event_id=1,
        quantity=1,
        currency="USD",
        request_token=TOKEN,
    )
    assert result.duplicate is False and stock(connection) == 4


@pytest.mark.req("purchase-024", "inventory-001")
@pytest.mark.call5
def test_two_simultaneous_submits_of_one_token_make_one_order(database):
    with connect(database) as c:
        uid = add_account(c)

    def submit(_):
        with connect(database) as c:
            return purchase.place_order(
                c,
                account_id=uid,
                event_id=1,
                quantity=1,
                currency="USD",
                request_token=TOKEN,
            )

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(submit, range(8)))
    assert len({r.order_id for r in results}) == 1
    assert sum(1 for r in results if not r.duplicate) == 1
    with connect(database) as c:
        assert c.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 1
        assert stock(c) == 119

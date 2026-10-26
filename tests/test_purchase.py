from concurrent.futures import ThreadPoolExecutor
import pytest
from eventhub import audit, purchase
from eventhub.db import connect
from eventhub.errors import (
    SoldOut,
    InvalidQuantity,
    UnsupportedCurrency,
    PurchaseLimit,
    ConfigurationPending,
)
from .conftest import add_account


def test_success_decrements_stock_and_records_order_and_audit(connection):
    uid = add_account(connection)
    before = connection.execute("SELECT available FROM events WHERE id=1").fetchone()[0]
    oid = purchase.purchase(
        connection, account_id=uid, event_id=1, quantity="2", currency="USD"
    )
    order = connection.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()
    assert order["total_minor"] == 3600
    assert (
        connection.execute("SELECT available FROM events WHERE id=1").fetchone()[0]
        == before - 2
    )
    assert (
        connection.execute(
            'SELECT outcome FROM audit WHERE kind="purchase"'
        ).fetchone()[0]
        == "success"
    )


def test_no_hold_until_purchase_success(connection):
    uid = add_account(connection)
    before = connection.execute("SELECT available FROM events WHERE id=1").fetchone()[0]
    purchase.cancel_checkout(connection, account_id=uid, event_id=1)
    assert (
        connection.execute("SELECT available FROM events WHERE id=1").fetchone()[0]
        == before
    )
    assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0
    assert connection.execute("SELECT outcome FROM audit").fetchone()[0] == "abandoned"


def test_invalid_quantity_fails_without_stock_change_and_audited(connection):
    uid = add_account(connection)
    for invalid in ["0", "-3", "2.5", "1e2", " 3", "999999999"]:
        with pytest.raises(InvalidQuantity):
            purchase.purchase(
                connection, account_id=uid, event_id=1, quantity=invalid, currency="USD"
            )
    assert (
        connection.execute("SELECT available FROM events WHERE id=1").fetchone()[0]
        == 120
    )
    assert connection.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 6


def test_sold_out_still_has_exactly_one_failure_audit(connection):
    uid = add_account(connection)
    connection.execute("UPDATE events SET available=1 WHERE id=1")
    with pytest.raises(SoldOut):
        purchase.purchase(
            connection, account_id=uid, event_id=1, quantity=2, currency="USD"
        )
    assert (
        connection.execute("SELECT available FROM events WHERE id=1").fetchone()[0] == 1
    )
    assert connection.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 1
    assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0


def test_invalid_currency_is_rejected_and_audited(connection):
    uid = add_account(connection)
    with pytest.raises(UnsupportedCurrency):
        purchase.purchase(
            connection, account_id=uid, event_id=1, quantity=1, currency="XYZ"
        )
    assert (
        connection.execute("SELECT outcome FROM audit").fetchone()[0]
        == "unsupported_currency"
    )


def test_purchase_limit_combines_previous_orders(connection):
    uid = add_account(connection)
    purchase.purchase(
        connection,
        account_id=uid,
        event_id=1,
        quantity=2,
        currency="USD",
        purchase_cap=2,
    )
    with pytest.raises(PurchaseLimit):
        purchase.purchase(
            connection,
            account_id=uid,
            event_id=1,
            quantity=1,
            currency="USD",
            purchase_cap=2,
        )


def test_missing_discount_blocks_usf_order_and_records_failure(connection):
    uid = add_account(connection, "PERSON@USF.EDU")
    with pytest.raises(ConfigurationPending):
        purchase.purchase(
            connection, account_id=uid, event_id=1, quantity=1, currency="USD"
        )
    assert (
        connection.execute("SELECT available FROM events WHERE id=1").fetchone()[0]
        == 120
    )
    assert (
        connection.execute("SELECT outcome FROM audit").fetchone()[0]
        == "configuration_pending"
    )


def test_rate_snapshot_not_rewritten_for_past_order(connection):
    uid = add_account(connection)
    order_id = purchase.purchase(
        connection, account_id=uid, event_id=1, quantity=1, currency="EUR"
    )
    connection.execute("UPDATE rates SET units_per_usd='0.99' WHERE currency='EUR'")
    order = connection.execute(
        "SELECT rate,total_minor FROM orders WHERE id=?", (order_id,)
    ).fetchone()
    assert order["rate"] == "0.92" and order["total_minor"] == 1656


def test_concurrent_buys_do_not_oversell(database):
    with connect(database) as c:
        c.execute("UPDATE events SET available=1 WHERE id=1")
        u1 = add_account(c, "first@example.com")
        u2 = add_account(c, "second@example.com")

    def attempt(uid):
        with connect(database) as c:
            try:
                purchase.purchase(
                    c, account_id=uid, event_id=1, quantity=1, currency="USD"
                )
                return "success"
            except SoldOut:
                return "sold_out"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(attempt, (u1, u2)))
    assert sorted(outcomes) == ["sold_out", "success"]
    with connect(database) as c:
        assert c.execute("SELECT available FROM events WHERE id=1").fetchone()[0] == 0
        assert c.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 1
        assert (
            c.execute('SELECT COUNT(*) FROM audit WHERE kind="purchase"').fetchone()[0]
            == 2
        )


def test_redeem_code_once_only(connection):
    uid = add_account(connection)
    order_id = purchase.purchase(
        connection, account_id=uid, event_id=1, quantity=1, currency="USD"
    )
    code = connection.execute(
        "SELECT confirmation_code FROM orders WHERE id=?", (order_id,)
    ).fetchone()[0]
    assert purchase.redeem(connection, code)["checked_in_at"] is not None
    from eventhub.errors import EventHubError

    with pytest.raises(EventHubError):
        purchase.redeem(connection, code)

import pytest
from .conftest import add_account
from eventhub.admin import change_rate
from eventhub.errors import UnsupportedCurrency


def test_rate_change_is_audited(connection):
    uid = add_account(connection, "manager@example.com", "administrator")
    change_rate(connection, uid, "EUR", "0.98")
    assert (
        connection.execute(
            "SELECT units_per_usd FROM rates WHERE currency='EUR'"
        ).fetchone()[0]
        == "0.98"
    )
    record = connection.execute("SELECT * FROM audit").fetchone()
    assert record["kind"] == "rate_change" and record["detail"] == "0.92 -> 0.98"


def test_invalid_rate_does_not_change_database(connection):
    uid = add_account(connection, "manager@example.com", "administrator")
    with pytest.raises(ValueError):
        change_rate(connection, uid, "EUR", "-4")
    assert (
        connection.execute(
            "SELECT units_per_usd FROM rates WHERE currency='EUR'"
        ).fetchone()[0]
        == "0.92"
    )
    assert connection.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 0


def test_unknown_currency_rejected(connection):
    uid = add_account(connection, "manager@example.com", "administrator")
    with pytest.raises(UnsupportedCurrency):
        change_rate(connection, uid, "XYZ", "1.2")


def test_usd_reference_rate_must_remain_one(connection):
    uid = add_account(connection, "manager@example.com", "administrator")
    with pytest.raises(ValueError):
        change_rate(connection, uid, "USD", "1.2")
    assert (
        connection.execute(
            "SELECT units_per_usd FROM rates WHERE currency='USD'"
        ).fetchone()[0]
        == "1"
    )

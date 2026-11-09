"""Call 6: specification-first currency, monitor, localization, recovery regressions.

This suite requires no HTTP server. A separate optional browser test exercises the
real admin screen, but these domain tests run even on a machine without Chrome.
"""

import sqlite3

import pytest

from eventhub.admin import change_rate
from eventhub.backups import create_backup, restore_backup, verify_backup
from eventhub.i18n import (
    catalog,
    local_date,
    local_money,
    normalize_language,
    translate,
)
from eventhub.monitor import acknowledge, alerts, scan_orders
from eventhub.pricing import CURRENCY_DIGITS, compute_quote, display_amount
from eventhub.purchase import place_order

from .conftest import add_account


@pytest.mark.call6
@pytest.mark.req("pricing-018", "pricing-020")
@pytest.mark.parametrize(
    "currency,rate,expected",
    [
        ("USD", "1", 3000),
        ("EUR", "0.92", 2760),
        ("GBP", "0.78", 2340),
        ("JPY", "150", 4500),
    ],
)
def test_exact_price_every_supported_currency(connection, currency, rate, expected):
    """In Part 6, a $30 order must never become ¥45 through display cleanup."""
    assert set(CURRENCY_DIGITS) == {"USD", "EUR", "GBP", "JPY"}
    quote = compute_quote(3000, 1, False, currency, rate)
    assert quote.total_minor == expected
    assert quote.currency == currency
    assert isinstance(quote.total_minor, int)
    if currency == "JPY":
        assert display_amount(expected, currency) == "JPY 4,500"


@pytest.mark.call6
@pytest.mark.req("pricing-018", "pricing-020", "admin-009")
@pytest.mark.parametrize(
    "currency,expected",
    [
        ("USD", 1800),
        ("EUR", 1656),
        ("GBP", 1404),
        ("JPY", 2700),
    ],
)
def test_real_purchase_persists_exact_currency_total(connection, currency, expected):
    """Place a real order through the domain transaction, not a mocked quote."""
    buyer = add_account(connection, f"buyer-{currency.lower()}@example.org")
    result = place_order(
        connection,
        account_id=buyer,
        event_id=1,
        quantity=1,
        currency=currency,
        discount_percent="10",
    )
    saved = connection.execute(
        "SELECT total_minor,currency FROM orders WHERE id=?", (result.order_id,)
    ).fetchone()
    assert saved["total_minor"] == expected
    assert saved["currency"] == currency


@pytest.mark.call6
@pytest.mark.req("pricing-018", "pricing-019", "pricing-020", "system-011")
def test_display_never_changes_stored_minor_units():
    original = compute_quote(3000, 1, False, "JPY", "150")
    english = local_money(original.total_minor, "JPY", "en")
    spanish = local_money(original.total_minor, "JPY", "es")
    assert english == "JPY 4,500"
    assert "4500" in spanish.replace(".", "").replace(",", "").replace(
        "\u00a0", ""
    ).replace("\u202f", "")
    assert ",00" not in spanish and ".00" not in spanish
    assert original.total_minor == 4500
    assert local_date("2026-11-07 19:00", "en") != local_date("2026-11-07 19:00", "es")


@pytest.mark.call6
@pytest.mark.req("system-010", "system-011")
def test_spanish_strings_and_fallback_without_changing_events():
    assert normalize_language("es") == "es"
    assert normalize_language("fr") == "en"
    assert translate("nav.discover", "en") == "Discover"
    assert translate("nav.discover", "es") == "Explorar"
    assert translate("order.amount", "es") == "IMPORTE COBRADO"
    assert all(key in catalog("es") for key in catalog("en"))
    assert "2026" in local_date("2026-11-07 19:00", "es")


@pytest.mark.call6
@pytest.mark.req("admin-009", "pricing-010", "pricing-020")
def test_admin_rate_change_is_used_by_next_purchase_not_previous(connection):
    manager = add_account(connection, "rate-admin@example.org", "administrator")
    buyer = add_account(connection, "buyer-for-rate@example.org")
    before = place_order(
        connection,
        account_id=buyer,
        event_id=1,
        quantity=1,
        currency="EUR",
        discount_percent="10",
    )
    old = connection.execute(
        "SELECT total_minor,rate FROM orders WHERE id=?", (before.order_id,)
    ).fetchone()
    assert old["rate"] == "0.92" and old["total_minor"] == 1656
    change_rate(connection, manager, "EUR", "1.10")
    after = place_order(
        connection,
        account_id=buyer,
        event_id=1,
        quantity=1,
        currency="EUR",
        discount_percent="10",
    )
    new = connection.execute(
        "SELECT total_minor,rate FROM orders WHERE id=?", (after.order_id,)
    ).fetchone()
    assert new["rate"] == "1.10" and new["total_minor"] == 1980
    assert (
        connection.execute(
            "SELECT total_minor,rate FROM orders WHERE id=?", (before.order_id,)
        ).fetchone()["total_minor"]
        == 1656
    )


@pytest.mark.call6
@pytest.mark.req("audit-009", "audit-010")
def test_undercharge_generates_one_durable_alert_without_repeating(connection):
    buyer = add_account(connection, "undercharge@example.org")
    result = place_order(
        connection,
        account_id=buyer,
        event_id=1,
        quantity=1,
        currency="JPY",
        discount_percent="10",
    )
    assert (
        connection.execute(
            "SELECT total_minor FROM orders WHERE id=?", (result.order_id,)
        ).fetchone()[0]
        == 2700
    )
    assert scan_orders(connection) == 0
    # Model the fictional Call 6 display/charge bug on a *copy* of a test order.
    connection.execute(
        "UPDATE orders SET total_minor=27 WHERE id=?", (result.order_id,)
    )
    assert scan_orders(connection, deviation_percent=25) == 1
    assert scan_orders(connection, deviation_percent=25) == 0
    found = alerts(connection)
    assert len(found) == 1 and found[0]["category"] == "charge_outlier"
    assert "expected 2700" in found[0]["description"]


@pytest.mark.call6
@pytest.mark.req("audit-011", "audit-010")
def test_admin_acknowledgement_keeps_alert_history(connection):
    buyer = add_account(connection, "alerts@example.org")
    manager = add_account(connection, "reviewer@example.org", "administrator")
    order = place_order(
        connection,
        account_id=buyer,
        event_id=2,
        quantity=1,
        currency="USD",
        discount_percent=None,
    )
    connection.execute("UPDATE orders SET total_minor=1 WHERE id=?", (order.order_id,))
    assert scan_orders(connection) == 1
    alert_id = alerts(connection)[0]["id"]
    assert acknowledge(connection, alert_id, manager) is True
    assert acknowledge(connection, alert_id, manager) is False
    record = alerts(connection)[0]
    assert record["status"] == "acknowledged" and record["acknowledged_by"] == manager


@pytest.mark.call6
@pytest.mark.req("system-012", "system-013")
def test_online_backup_integrity_and_guarded_restore(database, tmp_path):
    destination = tmp_path / "saved" / "backup.sqlite3"
    metadata = create_backup(database, destination)
    assert metadata["bytes"] > 0
    assert verify_backup(destination)["sha256"] == metadata["sha256"]
    restored = tmp_path / "restore.sqlite3"
    with pytest.raises(PermissionError):
        restore_backup(destination, restored)
    restore_backup(destination, restored, confirmed=True)
    with sqlite3.connect(restored) as db:
        assert db.execute("SELECT count(*) FROM rates").fetchone()[0] == 4
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    # Verify that a corrupted backup is rejected BEFORE it overwrites the good DB.
    with destination.open("ab") as f:
        f.write(b"TAMPER")
    with pytest.raises(ValueError, match="checksum"):
        restore_backup(destination, restored, confirmed=True)
    with sqlite3.connect(restored) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"

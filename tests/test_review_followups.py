"""Regression checks for findings from the pinned Part 8 code review."""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from babel.support import Translations

from eventhub.backups import create_backup, restore_backup
from eventhub.i18n import catalog

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.call6
@pytest.mark.req("system-013")
@pytest.mark.parametrize("suffix", ["-wal", "-shm"])
def test_restore_rejects_leftover_sqlite_sidecar_without_overwriting(
    database, tmp_path, suffix
):
    backup = tmp_path / "clean-backup.sqlite3"
    create_backup(database, backup)
    target = tmp_path / "existing.sqlite3"
    with sqlite3.connect(target) as conn:
        conn.execute("CREATE TABLE existing_marker (value INTEGER)")
        conn.execute("INSERT INTO existing_marker VALUES (42)")
    original = target.read_bytes()
    sidecar = Path(f"{target}{suffix}")
    sidecar.write_bytes(b"unresolved previous SQLite state")

    with pytest.raises(RuntimeError, match="WAL/SHM"):
        restore_backup(backup, target, confirmed=True)
    assert target.read_bytes() == original
    assert sidecar.read_bytes() == b"unresolved previous SQLite state"


@pytest.mark.call6
@pytest.mark.req("audit-010")
def test_authenticated_alert_email_without_starttls_is_refused_before_network(database):
    with sqlite3.connect(database) as conn:
        account = conn.execute(
            "INSERT INTO accounts(name,email,password_hash) VALUES (?,?,?)",
            ("Alert Test", "smtp-test@example.org", "test"),
        ).lastrowid
        order = conn.execute(
            """INSERT INTO orders(account_id,event_id,quantity,currency,rate,
               discount_percent,total_minor,confirmation_code,unit_usd_minor)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (account, 1, 1, "USD", "1", "0", 1800, "SMTP-CHECK-1", 1800),
        ).lastrowid
        conn.execute(
            "INSERT INTO maintenance_alerts(order_id,category,description) VALUES (?,?,?)",
            (order, "test_alert", "Alert pending notification"),
        )
    env = os.environ.copy()
    env.update(
        EVENTHUB_ALERT_TO="owner@example.org",
        EVENTHUB_ALERT_FROM="alerts@example.org",
        EVENTHUB_SMTP_HOST="smtp.invalid",
        EVENTHUB_SMTP_USER="test-user",
        EVENTHUB_SMTP_PASSWORD="fake-password",
        EVENTHUB_SMTP_STARTTLS="0",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/check_order_anomalies.py"),
            "--database",
            str(database),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 2, (result.stdout, result.stderr)
    assert "authentication requires STARTTLS" in result.stdout
    assert "Notification failed" not in result.stdout


@pytest.mark.part8
@pytest.mark.req("localization-002", "localization-007")
def test_legacy_english_interface_copy_is_served_from_gettext_catalog():
    known = {
        "checkout.currency_note": (
            "You will be charged in the currency selected above. "
            "It starts as your preferred currency ({currency}); "
            "changing it here applies to this purchase only."
        ),
        "checkout.discount_pending": (
            "USF student discount percent is not provided yet; "
            "eligible purchases are paused until configured."
        ),
        "checkout.demo": (
            "This is a classroom prototype with simulated payments. "
            "No real tickets are issued."
        ),
        "auth.noaccount": "Don't have an account?",
        "auth.register_intro": "Discover the best events on campus.",
        "order.note": (
            "This is the only amount charged, in {currency}, "
            "the currency you picked at checkout."
        ),
        "order.simulated": (
            "Simulated payment: no real money moved. In a live system, "
            "the amount charged above is what would reach your card."
        ),
    }
    translations = Translations.load(
        str(ROOT / "translations"), locales=["en_US"], domain="messages"
    )
    for key, expected in known.items():
        assert catalog("en")[key] == expected
        assert translations.gettext(key) == expected
    templates = {
        "checkout.html": (
            "checkout.currency_note",
            "checkout.discount_pending",
            "checkout.demo",
        ),
        "login.html": ("auth.noaccount",),
        "register.html": ("auth.register_intro",),
        "order.html": ("order.note", "order.simulated"),
    }
    for name, keys in templates.items():
        source = (ROOT / "templates" / name).read_text()
        for key in keys:
            assert f't("{key}"' in source or f"t('{key}'" in source

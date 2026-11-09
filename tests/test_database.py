from pathlib import Path

import pytest

from eventhub.db import connect, initialize


@pytest.mark.req("catalog-006", "inventory-002")
def test_seed_is_idempotent(database):
    root = Path(__file__).resolve().parents[1]
    initialize(database, root / "config" / "setup.json")
    with connect(database) as c:
        assert c.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 4
        assert c.execute("SELECT COUNT(*) FROM rates").fetchone()[0] == 4
        assert c.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"


@pytest.mark.req("inventory-004")
def test_atomic_inventory_constraint_blocks_negative_counts(connection):
    from sqlite3 import IntegrityError

    try:
        connection.execute("UPDATE events SET available=-1 WHERE id=1")
        assert False, "expected a database constraint"
    except IntegrityError:
        pass
    assert (
        connection.execute("SELECT available FROM events WHERE id=1").fetchone()[0]
        == 120
    )


@pytest.mark.req("admin-008")
def test_audit_records_newest_first(connection):
    from eventhub.audit import recent, record

    record(
        connection,
        kind="test",
        account_id=None,
        event_id=None,
        quantity=None,
        currency=None,
        outcome="first",
    )
    record(
        connection,
        kind="test",
        account_id=None,
        event_id=None,
        quantity=None,
        currency=None,
        outcome="second",
    )
    assert [row["outcome"] for row in recent(connection)] == ["second", "first"]

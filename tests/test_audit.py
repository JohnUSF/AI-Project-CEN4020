"""Audit writes and newest-first read ordering tested as a standalone component."""

import pytest

from eventhub import audit


@pytest.mark.req("admin-008")
def test_audit_recent_returns_newest_first(connection):
    audit.record(
        connection,
        kind="purchase",
        account_id=None,
        event_id=1,
        quantity=1,
        currency="USD",
        outcome="first",
    )
    audit.record(
        connection,
        kind="purchase",
        account_id=None,
        event_id=1,
        quantity=1,
        currency="USD",
        outcome="second",
    )
    assert [row["outcome"] for row in audit.recent(connection)] == [
        "second",
        "first",
    ]


@pytest.mark.req("audit-001")
def test_audit_limits_untrusted_detail_length(connection):
    audit.record(
        connection,
        kind="rate_change",
        account_id=None,
        event_id=None,
        quantity=None,
        currency="EUR",
        outcome="changed",
        detail="x" * 1000,
    )
    detail = connection.execute("SELECT detail FROM audit").fetchone()[0]
    assert len(detail) == 250

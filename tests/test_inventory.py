"""Inventory's atomic decrement can be verified separately from purchase routes."""

import pytest

from eventhub.errors import SoldOut
from eventhub.inventory import take_tickets


def test_inventory_decrement_succeeds_with_enough_stock(connection):
    before = connection.execute("SELECT available FROM events WHERE id=1").fetchone()[0]
    take_tickets(connection, 1, 2)
    after = connection.execute("SELECT available FROM events WHERE id=1").fetchone()[0]
    assert after == before - 2


def test_inventory_rejects_oversell_without_negative_count(connection):
    connection.execute("UPDATE events SET available=1 WHERE id=1")
    with pytest.raises(SoldOut):
        take_tickets(connection, 1, 2)
    remaining = connection.execute(
        "SELECT available FROM events WHERE id=1"
    ).fetchone()[0]
    assert remaining == 1

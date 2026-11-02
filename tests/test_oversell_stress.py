"""Thuy: 'Ran it two hundred times. Exactly one success, one polite failure, every time.'

Priya: 'Keep it forever; it quietly starts failing after someone reorganizes the code.'
"""

import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from eventhub import purchase
from eventhub.db import connect
from eventhub.errors import SoldOut
from .conftest import add_account

ROUNDS = 200


@pytest.mark.req("inventory-001", "inventory-003", "inventory-004", "audit-008")
@pytest.mark.call5
def test_two_buyers_one_ticket_two_hundred_times(database):
    with connect(database) as c:
        a, b = add_account(c, "first@example.com"), add_account(c, "second@example.com")
        for i in range(ROUNDS):
            c.execute(
                """INSERT INTO events(id,artist,venue,starts_at,description,base_price_minor,available)
                         VALUES(?,?,?,?,?,?,1)""",
                (
                    1000 + i,
                    f"Last Ticket {i}",
                    "Test Hall",
                    "2026-12-01 20:00",
                    "x",
                    1500,
                ),
            )

    def attempt(args):
        uid, event_id, barrier = args
        with connect(database) as c:
            barrier.wait(timeout=10)
            try:
                purchase.purchase(
                    c, account_id=uid, event_id=event_id, quantity=1, currency="USD"
                )
                return "success"
            except SoldOut:
                return "sold_out"

    bad = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        for i in range(ROUNDS):
            barrier = threading.Barrier(2)
            outcomes = sorted(
                pool.map(attempt, [(a, 1000 + i, barrier), (b, 1000 + i, barrier)])
            )
            if outcomes != ["sold_out", "success"]:
                bad.append((i, outcomes))
    assert bad == []
    with connect(database) as c:
        assert (
            c.execute(
                "SELECT COUNT(*) FROM events WHERE id>=1000 AND available<>0"
            ).fetchone()[0]
            == 0
        )
        assert (
            c.execute(
                "SELECT COUNT(*) FROM events WHERE id>=1000 AND available<0"
            ).fetchone()[0]
            == 0
        )
        assert c.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == ROUNDS
        assert (
            c.execute("SELECT COUNT(*) FROM audit WHERE kind='purchase'").fetchone()[0]
            == ROUNDS * 2
        )


@pytest.mark.req("inventory-001", "inventory-004")
@pytest.mark.whitebox
def test_many_buyers_few_tickets_sells_exactly_the_stock(database):
    with connect(database) as c:
        c.execute("UPDATE events SET available=5 WHERE id=1")
        ids = [add_account(c, f"buyer{i}@example.com") for i in range(30)]
    barrier = threading.Barrier(30)

    def attempt(uid):
        with connect(database) as c:
            barrier.wait(timeout=20)
            try:
                purchase.purchase(
                    c, account_id=uid, event_id=1, quantity=1, currency="USD"
                )
                return "success"
            except SoldOut:
                return "sold_out"

    with ThreadPoolExecutor(max_workers=30) as pool:
        outcomes = list(pool.map(attempt, ids))
    assert outcomes.count("success") == 5 and outcomes.count("sold_out") == 25
    with connect(database) as c:
        assert c.execute("SELECT available FROM events WHERE id=1").fetchone()[0] == 0

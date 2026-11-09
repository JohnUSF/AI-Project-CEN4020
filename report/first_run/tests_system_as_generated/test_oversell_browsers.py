"""Kenji: 'And the same-moment case. Two buyers, one ticket.' Two real browsers press buy together."""

import os
import threading

import pytest
from selenium.webdriver.common.by import By

from .helpers import body_text, css, signed_in, wait

ROUNDS = int(os.environ.get("EVENTHUB_OVERSELL_ROUNDS", "5"))


@pytest.mark.req(
    "inventory-001", "inventory-003", "inventory-004", "purchase-006", "audit-008"
)
@pytest.mark.call5
def test_two_browsers_one_ticket_exactly_one_wins_every_round(
    browser, second_browser, server
):
    a, b = server.new_user(), server.new_user()
    signed_in(browser, server.url, a)
    signed_in(second_browser, server.url, b)
    for round_number in range(ROUNDS):
        event = server.new_event(
            available=1, artist=f"Last Ticket Round {round_number}"
        )
        for d in (browser, second_browser):
            d.get(f"{server.url}/checkout/{event}")
            css(d, "#checkout-form button[type=submit]")
        gate = threading.Barrier(2)
        errors = []

        def press(driver):
            try:
                gate.wait(timeout=10)
                driver.find_element(
                    By.CSS_SELECTOR, "#checkout-form button[type=submit]"
                ).click()
            except Exception as exc:  # surfaced below, not swallowed
                errors.append(repr(exc))

        threads = [
            threading.Thread(target=press, args=(d,)) for d in (browser, second_browser)
        ]
        [t.start() for t in threads]
        [t.join() for t in threads]
        assert errors == []
        for d in (browser, second_browser):
            wait(d).until(lambda x: "/checkout/" not in x.current_url)
        pages = [body_text(browser), body_text(second_browser)]
        wins = sum("AMOUNT CHARGED" in p for p in pages)
        losses = sum("Sold out" in p for p in pages)
        assert (wins, losses) == (1, 1), f"round {round_number}: {pages}"
        assert server.scalar("SELECT available FROM events WHERE id=?", (event,)) == 0
        assert (
            server.scalar("SELECT COUNT(*) FROM orders WHERE event_id=?", (event,)) == 1
        )
        assert (
            server.scalar(
                "SELECT COUNT(*) FROM audit WHERE kind='purchase' AND event_id=?",
                (event,),
            )
            == 2
        )

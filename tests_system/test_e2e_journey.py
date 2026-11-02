"""End-to-end journeys through a real browser (Thuy's third test layer)."""

import time

import pytest
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from .helpers import (
    alerts,
    body_text,
    buy_via_checkout,
    click,
    css,
    login,
    order_id_from_url,
    register_ui,
    shot,
    signed_in,
    visible,
    wait,
    wait_for_text,
    wait_for_url,
    wait_for_url_not,
)


@pytest.mark.req(
    "identity-001",
    "identity-008",
    "catalog-002",
    "catalog-004",
    "pricing-006",
    "purchase-004",
    "purchase-013",
    "purchase-016",
    "purchase-017",
    "purchase-029",
    "purchase-030",
)
def test_full_journey_register_login_search_buy_in_euros_and_find_it_in_history(
    browser, server
):
    """Register, sign in, search, open an event, buy in EUR, read the confirmation, find it in order history."""
    email = f"journey{int(time.time() * 1000)}@example.com"
    register_ui(browser, server.url, "Journey Student", email)
    wait_for_text(browser, "Account created")
    login(browser, server.url, email)
    wait_for_text(browser, "Upcoming events")

    css(browser, "#q").send_keys("jazz")
    click(browser, browser.find_element(By.CSS_SELECTOR, ".search button"))
    wait_for_text(browser, "Search results")
    cards = browser.find_elements(By.CSS_SELECTOR, ".event-card")
    assert len(cards) == 1 and "Campus Jazz Collective" in cards[0].text

    cards[0].click()  # a single click opens the detail page
    wait_for_url(browser, "/events/1")
    browser.find_element(By.PARTIAL_LINK_TEXT, "Get tickets").click()
    wait_for_url(browser, "/checkout/1")
    Select(browser.find_element(By.ID, "currency")).select_by_value("EUR")
    qty = browser.find_element(By.ID, "quantity")
    qty.clear()
    qty.send_keys("2")
    wait(browser).until(
        lambda d: "EUR 33.12" in css(d, "#price-preview").text
    )  # live estimate
    click(
        browser,
        browser.find_element(By.CSS_SELECTOR, "#checkout-form button[type=submit]"),
    )

    wait_for_url(browser, "/orders/")
    assert css(browser, "#charged-total").text == "EUR 33.12"
    assert "reference only, not charged" in body_text(browser)
    assert "1 USD = 0.92 EUR" in body_text(browser)
    shot(browser, "journey_confirmation_eur")
    order_id = order_id_from_url(browser)

    browser.find_element(By.LINK_TEXT, "My tickets").click()
    wait_for_url(browser, "/orders")
    row = css(browser, ".order-row")
    assert (
        "Campus Jazz Collective" in row.text
        and "EUR 33.12" in row.text
        and "2 tickets" in row.text
    )
    row.click()
    wait_for_url(browser, f"/orders/{order_id}")
    assert css(browser, "#charged-total").text == "EUR 33.12"


@pytest.mark.req("identity-010", "identity-011", "identity-013", "identity-007")
def test_signed_out_checkout_goes_to_login_and_returns_after_sign_in(browser, server):
    user = server.new_user()
    browser.get(f"{server.url}/checkout/1")
    wait_for_url(browser, "/login?next=")
    assert "Almost there" not in body_text(browser)
    login(browser, server.url, user["email"], next_path="/checkout/1")
    wait_for_url(browser, "/checkout/1")
    assert "Almost there" in body_text(browser)


@pytest.mark.req("identity-009", "identity-007")
def test_signing_out_ends_the_session(browser, server):
    signed_in(browser, server.url, server.new_user())
    click(browser, browser.find_element(By.CSS_SELECTOR, ".nav-form .nav-button"))
    wait_for_text(browser, "Join EventHub")  # the sign-out has finished
    browser.get(f"{server.url}/orders")
    wait_for_url(browser, "/login")


@pytest.mark.req("purchase-001", "catalog-004")
def test_double_clicking_a_card_buys_one_ticket_in_the_preferred_currency(
    browser, server
):
    user = server.new_user(currency="GBP")
    signed_in(browser, server.url, user)
    card = css(browser, ".event-card")
    ActionChains(browser).double_click(card).perform()
    wait_for_url(browser, "/orders/")
    assert "GBP" in css(browser, "#charged-total").text
    assert css(browser, "#order-quantity").text == "1"
    assert (
        server.scalar("SELECT COUNT(*) FROM orders WHERE account_id=?", (user["id"],))
        == 1
    )


@pytest.mark.req("catalog-001", "catalog-005")
def test_home_page_lists_every_event_with_its_ticket_count(browser, server):
    browser.get(server.url)
    cards = browser.find_elements(By.CSS_SELECTOR, ".event-card")
    assert len(cards) == server.scalar("SELECT COUNT(*) FROM events")
    assert (
        "120 left" in body_text(browser)
        or server.scalar("SELECT available FROM events WHERE id=1") != 120
    )


@pytest.mark.req("purchase-003", "identity-012")
def test_double_clicking_while_signed_out_goes_to_login_and_buys_nothing(
    browser, server
):
    before = server.scalar("SELECT COUNT(*) FROM orders")
    browser.get(server.url)
    ActionChains(browser).double_click(css(browser, ".event-card")).perform()
    wait_for_url(browser, "/login")
    assert server.scalar("SELECT COUNT(*) FROM orders") == before


@pytest.mark.req("purchase-002", "purchase-006", "purchase-011")
def test_sold_out_quick_buy_names_the_cause_and_returns_to_the_event(browser, server):
    event = server.new_event(available=0)
    signed_in(browser, server.url, server.new_user())
    browser.get(f"{server.url}/events/{event}")
    click(browser, browser.find_element(By.XPATH, "//button[contains(., 'Quick buy')]"))
    wait_for_text(browser, "Sold out")
    assert f"/events/{event}" in browser.current_url


@pytest.mark.req("purchase-021", "purchase-020")
def test_cancelling_checkout_records_an_abandoned_checkout_and_takes_no_tickets(
    browser, server
):
    user = server.new_user()
    signed_in(browser, server.url, user)
    event = server.new_event(available=10)
    browser.get(f"{server.url}/checkout/{event}")
    click(
        browser, browser.find_element(By.CSS_SELECTOR, "[data-checkout-cancel] button")
    )
    wait_for_text(browser, "Checkout cancelled")
    assert (
        server.scalar(
            "SELECT COUNT(*) FROM audit WHERE outcome='abandoned' AND account_id=?",
            (user["id"],),
        )
        == 1
    )
    assert server.scalar("SELECT available FROM events WHERE id=?", (event,)) == 10
    assert (
        server.scalar("SELECT COUNT(*) FROM orders WHERE account_id=?", (user["id"],))
        == 0
    )


@pytest.mark.req("purchase-022")
def test_leaving_the_checkout_page_records_an_abandoned_checkout(browser, server):
    user = server.new_user()
    signed_in(browser, server.url, user)
    browser.get(f"{server.url}/checkout/1")
    css(browser, "#checkout-form")
    browser.get(server.url)  # walk away without buying
    wait(browser, 5).until(
        lambda d: (
            server.scalar(
                "SELECT COUNT(*) FROM audit WHERE outcome='abandoned' AND account_id=?",
                (user["id"],),
            )
            == 1
        )
    )


@pytest.mark.req("purchase-023")
def test_the_back_button_still_works_during_checkout(browser, server):
    signed_in(browser, server.url, server.new_user())
    browser.get(f"{server.url}/events/1")
    browser.find_element(By.PARTIAL_LINK_TEXT, "Get tickets").click()
    wait_for_url(browser, "/checkout/1")
    browser.back()
    wait_for_url_not(browser, "/checkout/")
    assert browser.current_url.endswith("/events/1")


@pytest.mark.req("system-003")
@pytest.mark.parametrize("path", ["/", "/events/1", "/login", "/register"])
def test_phone_sized_screen_has_no_sideways_scrolling(browser, server, path):
    browser.set_window_size(375, 800)
    browser.get(server.url + path)
    css(browser, "main")
    overflow = browser.execute_script(
        "return document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    assert overflow <= 1
    assert (
        browser.find_element(By.CSS_SELECTOR, "meta[name=viewport]")
        .get_attribute("content")
        .startswith("width=device-width")
    )

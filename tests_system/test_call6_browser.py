"""Browser-level Call 6 regressions. Run with installed Flask, Selenium and Chrome."""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from .helpers import (
    css,
    click,
    csrf_and_token,
    fetch_post,
    signed_in,
    buy_via_checkout,
    wait_for_url,
    wait,
)

pytestmark = pytest.mark.call6


@pytest.mark.req("system-010", "system-011", "pricing-019")
def test_spanish_browser_flow_uses_regional_display_without_changing_charge(
    browser, server
):
    user, event = server.new_user(currency="JPY"), server.new_event(price_minor=3000)
    signed_in(browser, server.url, user)
    browser.get(server.url + "/")
    form = browser.find_element(By.CSS_SELECTOR, ".language-form")
    Select(form.find_element(By.NAME, "language")).select_by_value("es")
    click(browser, form.find_element(By.CSS_SELECTOR, "button[type=submit]"))
    css(browser, 'html[lang="es"]')
    assert "Explorar" in browser.find_element(By.TAG_NAME, "body").text
    buy_via_checkout(browser, server.url, event, "1", "JPY")
    assert "IMPORTE COBRADO" in browser.find_element(By.TAG_NAME, "body").text
    assert (
        server.scalar(
            "SELECT total_minor FROM orders WHERE account_id=?", (user["id"],)
        )
        == 4500
    )
    assert ".00" not in css(browser, "#charged-total").text


@pytest.mark.req("admin-009", "pricing-018")
def test_admin_web_rate_change_then_next_yen_order_uses_new_rate(browser, server):
    manager = server.new_user(role="administrator")
    buyer = server.new_user(currency="JPY")
    event = server.new_event(price_minor=3000)
    original = server.scalar("SELECT units_per_usd FROM rates WHERE currency='JPY'")
    try:
        signed_in(browser, server.url, manager)
        browser.get(server.url + "/admin")
        form = browser.find_element(By.CSS_SELECTOR, 'form[action$="/admin/rates"]')
        Select(form.find_element(By.NAME, "currency")).select_by_visible_text("JPY")
        rate = form.find_element(By.NAME, "rate")
        rate.clear()
        rate.send_keys("200")
        click(browser, form.find_element(By.CSS_SELECTOR, 'button[type="submit"]'))
        # Selenium click() can return before the POST and SQLite commit finish.
        wait(browser).until(
            lambda _: (
                server.scalar("SELECT units_per_usd FROM rates WHERE currency='JPY'")
                == "200"
            )
        )
        browser.delete_all_cookies()
        signed_in(browser, server.url, buyer)
        buy_via_checkout(browser, server.url, event, "1", "JPY")
        assert css(browser, "#charged-total").text == "JPY 6,000"
        assert (
            server.scalar(
                "SELECT total_minor FROM orders WHERE account_id=?", (buyer["id"],)
            )
            == 6000
        )
    finally:
        # The server fixture is shared across system tests. Restore the original
        # value so later yen regressions still exercise the initial 150 JPY/USD.
        server.run("UPDATE rates SET units_per_usd=? WHERE currency='JPY'", (original,))

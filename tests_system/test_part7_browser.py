"""Part 7 browser check: Spanish reaches the page title, the script's messages and error pages.

Run with installed Flask, Selenium and Chrome, like the other system tests.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from .helpers import body_text, click, css, signed_in, wait

pytestmark = pytest.mark.part7


def _choose_language(browser, code):
    form = browser.find_element(By.CSS_SELECTOR, ".language-form")
    Select(form.find_element(By.NAME, "language")).select_by_value(code)
    click(browser, form.find_element(By.CSS_SELECTOR, "button[type=submit]"))
    css(browser, f'html[lang="{code}"]')


@pytest.mark.req("system-015", "system-016", "system-017")
def test_spanish_checkout_title_preview_and_error_page_in_the_browser(browser, server):
    user, event = server.new_user(currency="JPY"), server.new_event(price_minor=3000)
    signed_in(browser, server.url, user)
    browser.get(server.url + "/")
    _choose_language(browser, "es")

    browser.get(f"{server.url}/checkout/{event}")
    css(browser, "#checkout-form")
    assert browser.title == "Pago · EventHub"
    wait(browser).until(lambda d: "Total estimado" in css(d, "#price-preview").text)
    assert "Estimated total" not in body_text(browser)

    quantity = browser.find_element(By.ID, "quantity")
    quantity.clear()
    quantity.send_keys("0")
    wait(browser).until(
        lambda d: "Precio no disponible" in css(d, "#price-preview").text
    )
    assert "Price not available" not in body_text(browser)

    browser.get(server.url + "/no-such-page")
    wait(browser).until(lambda d: "No se encontró la página solicitada" in body_text(d))
    assert browser.title.startswith("No se puede continuar")

    _choose_language(browser, "en")  # the reader can switch back
    browser.get(f"{server.url}/checkout/{event}")
    wait(browser).until(lambda d: "Estimated total" in css(d, "#price-preview").text)

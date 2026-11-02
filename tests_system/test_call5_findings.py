"""One test group per thing the Call 5 meeting raised."""

import re
import time

import pytest
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from .helpers import (
    click,
    alerts,
    body_text,
    buy_via_checkout,
    css,
    csrf_and_token,
    fetch_post,
    order_id_from_url,
    register_ui,
    shot,
    signed_in,
    wait,
    wait_for_text,
    wait_for_url,
)

pytestmark = pytest.mark.call5


def orders_for(server, user, event=None):
    if event:
        return server.scalar(
            "SELECT COUNT(*) FROM orders WHERE account_id=? AND event_id=?",
            (user["id"], event),
        )
    return server.scalar(
        "SELECT COUNT(*) FROM orders WHERE account_id=?", (user["id"],)
    )


# ================================================================ Thuy: "the buy button fires twice"
@pytest.mark.req("purchase-024", "purchase-027")
def test_double_clicking_the_checkout_button_makes_one_order(browser, server):
    user, event = server.new_user(), server.new_event(available=10)
    signed_in(browser, server.url, user)
    browser.get(f"{server.url}/checkout/{event}")
    button = css(browser, "#checkout-form button[type=submit]")
    ActionChains(browser).double_click(button).perform()
    wait_for_url(browser, "/orders/")
    assert orders_for(server, user, event) == 1
    assert server.scalar("SELECT available FROM events WHERE id=?", (event,)) == 9


@pytest.mark.req("purchase-024", "purchase-027")
def test_three_instant_clicks_from_a_script_still_make_one_order(browser, server):
    user, event = server.new_user(), server.new_event(available=10)
    signed_in(browser, server.url, user)
    browser.get(f"{server.url}/checkout/{event}")
    browser.execute_script(
        "const b=document.querySelector('#checkout-form button[type=submit]'); b.click(); b.click(); b.click();"
    )
    wait_for_url(browser, "/orders/")
    time.sleep(0.5)
    assert orders_for(server, user, event) == 1


@pytest.mark.req("purchase-024", "purchase-027", "purchase-001")
def test_triple_clicking_an_event_card_makes_one_quick_buy(browser, server):
    user = server.new_user()
    signed_in(browser, server.url, user)
    card = css(browser, ".event-card")
    # Three genuine click events with detail 1, 2, 3, as a browser sends for a triple-click.
    browser.execute_script(
        "for (const n of [1, 2, 3]) arguments[0].dispatchEvent("
        "new MouseEvent('click', {bubbles: true, cancelable: true, detail: n}));",
        card,
    )
    wait_for_url(browser, "/orders/")
    time.sleep(0.5)
    assert orders_for(server, user) == 1


@pytest.mark.req("purchase-024", "purchase-027")
def test_double_clicking_quick_buy_on_the_event_page_makes_one_order(browser, server):
    user, event = server.new_user(), server.new_event(available=10)
    signed_in(browser, server.url, user)
    browser.get(f"{server.url}/events/{event}")
    ActionChains(browser).double_click(
        browser.find_element(By.XPATH, "//button[contains(., 'Quick buy')]")
    ).perform()
    wait_for_url(browser, "/orders/")
    assert orders_for(server, user, event) == 1


@pytest.mark.req("purchase-024", "purchase-025")
def test_even_with_the_page_script_bypassed_the_server_refuses_to_buy_twice(
    browser, server
):
    """The browser guard is a convenience. This sends the same form twice from outside the page's own code."""
    user, event = server.new_user(), server.new_event(available=10)
    signed_in(browser, server.url, user)
    browser.get(f"{server.url}/checkout/{event}")
    fields = csrf_and_token(browser)
    form = {
        "csrf_token": fields["csrf"],
        "purchase_token": fields["token"],
        "quantity": "2",
        "currency": "USD",
    }
    first = fetch_post(browser, f"/checkout/{event}", form)
    second = fetch_post(browser, f"/checkout/{event}", form)
    assert re.search(r"/orders/\d+$", first["url"]) and first["url"] == second["url"]
    assert "not charged twice" in second["text"]
    assert orders_for(server, user, event) == 1
    assert server.scalar("SELECT available FROM events WHERE id=?", (event,)) == 8
    assert [
        r[0]
        for r in server.sql(
            "SELECT outcome FROM audit WHERE account_id=? ORDER BY id", (user["id"],)
        )
    ] == ["success", "duplicate_suppressed"]


@pytest.mark.req("purchase-026")
def test_a_purchase_token_cannot_be_reused_for_a_different_purchase(browser, server):
    user, event = server.new_user(), server.new_event(available=10)
    signed_in(browser, server.url, user)
    browser.get(f"{server.url}/checkout/{event}")
    fields = csrf_and_token(browser)
    base = {
        "csrf_token": fields["csrf"],
        "purchase_token": fields["token"],
        "currency": "USD",
    }
    fetch_post(browser, f"/checkout/{event}", {**base, "quantity": "1"})
    result = fetch_post(browser, f"/checkout/{event}", {**base, "quantity": "5"})
    assert "already used for a different purchase" in result["text"]
    assert orders_for(server, user, event) == 1


@pytest.mark.req("purchase-028")
def test_a_purchase_form_without_its_token_is_refused_with_a_reload_message(
    browser, server
):
    user, event = server.new_user(), server.new_event(available=10)
    signed_in(browser, server.url, user)
    browser.get(f"{server.url}/checkout/{event}")
    browser.execute_script("document.querySelector('[name=purchase_token]').remove()")
    click(
        browser,
        browser.find_element(By.CSS_SELECTOR, "#checkout-form button[type=submit]"),
    )
    wait_for_text(browser, "out of date")
    assert orders_for(server, user) == 0


@pytest.mark.req("purchase-025")
def test_each_page_view_gets_a_new_purchase_token(browser, server):
    signed_in(browser, server.url, server.new_user())
    seen = set()
    for _ in range(3):
        browser.get(f"{server.url}/checkout/1")
        seen.add(csrf_and_token(browser)["token"])
    assert len(seen) == 3
    browser.get(server.url)
    tokens = [
        e.get_attribute("value")
        for e in browser.find_elements(
            By.CSS_SELECTOR, ".quick-buy-form [name=purchase_token]"
        )
    ]
    assert len(tokens) == len(set(tokens)) >= 4


# ================================================================ Kenji finding 2: request speed
@pytest.mark.req("purchase-032", "audit-007", "audit-008")
def test_a_script_hammering_the_purchase_endpoint_is_stopped_and_logged_once(
    browser, server
):
    user, event = server.new_user(), server.new_event(available=1000)
    signed_in(browser, server.url, user)
    browser.get(f"{server.url}/events/{event}")
    csrf = csrf_and_token(browser)["csrf"]
    results = browser.execute_async_script(
        """
        const done = arguments[arguments.length - 1]; const [csrf, event] = arguments; const out = [];
        (async () => {
          for (let i = 0; i < 40; i++) {
            const r = await fetch('/quick-buy/' + event, {method: 'POST', credentials: 'same-origin', redirect: 'manual',
              headers: {'Content-Type': 'application/x-www-form-urlencoded'},
              body: new URLSearchParams({csrf_token: csrf, purchase_token: 'hammer-' + Date.now() + '-' + i + '-xxxxxxxx'})});
            out.push([r.status, r.type, r.headers.get('Retry-After')]);
          }
          done(out);
        })();""",
        csrf,
        event,
    )
    statuses = [r[0] for r in results]  # status 0 = opaque redirect = accepted (302)
    accepted = sum(1 for r in results if r[1] == "opaqueredirect")
    limited = sum(1 for s in statuses if s == 429)
    assert accepted == 20 and limited == 20  # provisional limit: 20 per 60 s (Q19)
    assert orders_for(server, user, event) == 20
    assert (
        server.scalar(
            "SELECT COUNT(*) FROM audit WHERE outcome='rate_limited' AND account_id=?",
            (user["id"],),
        )
        == 1
    )
    assert int(next(r[2] for r in results if r[0] == 429)) >= 1
    browser.get(f"{server.url}/events/{event}")
    click(browser, browser.find_element(By.XPATH, "//button[contains(., 'Quick buy')]"))
    wait_for_text(browser, "Too many purchase requests")
    shot(browser, "rate_limited_message")


@pytest.mark.req("purchase-032")
def test_a_limited_account_does_not_stop_other_buyers(browser, server):
    noisy, calm = server.new_user(), server.new_user()
    event = server.new_event(available=500)
    signed_in(browser, server.url, noisy)
    browser.get(f"{server.url}/events/{event}")
    csrf = csrf_and_token(browser)["csrf"]
    for i in range(22):
        fetch_post(
            browser,
            f"/quick-buy/{event}",
            {"csrf_token": csrf, "purchase_token": f"noisy-{i:04d}-xxxxxxxxxxxx"},
        )
    assert orders_for(server, noisy) == 20
    browser.delete_all_cookies()
    signed_in(browser, server.url, calm)
    buy_via_checkout(browser, server.url, event, "1")
    assert css(browser, "#charged-total").text.startswith("USD")


# ================================================================ Darnell: "which amount hit my card?"
@pytest.mark.req("purchase-029", "purchase-030")
def test_the_confirmation_makes_the_charged_amount_the_biggest_thing_on_the_page(
    browser, server
):
    user, event = server.new_user(), server.new_event(available=10, price_minor=2000)
    signed_in(browser, server.url, user)
    buy_via_checkout(browser, server.url, event, "2", "EUR")
    sizes = browser.execute_script("""
        const px = e => parseFloat(getComputedStyle(e).fontSize);
        const charged = px(document.getElementById('charged-total'));
        const others = [...document.querySelectorAll('.receipt strong, .receipt code')]
                         .filter(e => e.id !== 'charged-total').map(px);
        return {charged, biggestOther: Math.max(...others)};""")
    assert sizes["charged"] > sizes["biggestOther"]
    text = body_text(browser)
    assert css(browser, "#charged-total").text == "EUR 36.80"
    assert "This is the only amount charged, in EUR" in text
    assert re.search(r"USD 40\.00\s+reference only, not charged", text)
    shot(browser, "confirmation_wording_eur")


@pytest.mark.req("purchase-029")
def test_a_dollar_order_does_not_show_a_second_confusing_amount(browser, server):
    user, event = server.new_user(), server.new_event(available=10, price_minor=2000)
    signed_in(browser, server.url, user)
    buy_via_checkout(browser, server.url, event, "1", "USD")
    assert css(browser, "#charged-total").text == "USD 20.00"
    assert "not charged" not in body_text(browser) and not browser.find_elements(
        By.ID, "rate-row"
    )


@pytest.mark.req("purchase-030", "purchase-019")
def test_the_order_history_page_repeats_the_same_amounts(browser, server):
    user, event = server.new_user(), server.new_event(available=10, price_minor=2000)
    signed_in(browser, server.url, user)
    buy_via_checkout(browser, server.url, event, "1", "JPY")
    charged = css(browser, "#charged-total").text
    browser.get(server.url + "/orders")
    assert charged == "JPY 3,000" and charged in css(browser, ".order-row").text


# ================================================================ Darnell: "where does the default currency come from?"
@pytest.mark.req(
    "identity-018",
    "pricing-016",
    "pricing-017",
    "identity-019",
    "purchase-031",
    "purchase-001",
)
def test_the_currency_chosen_at_registration_is_visible_explained_and_used(
    browser, server
):
    email = f"euro{int(time.time() * 1000)}@example.com"
    register_ui(browser, server.url, "Euro Student", email, currency="EUR")
    wait_for_text(browser, "Account created")
    browser.get(server.url + "/login")
    css(browser, "#email").send_keys(email)
    browser.find_element(By.ID, "password").send_keys("correct-horse-battery")
    click(
        browser, browser.find_element(By.CSS_SELECTOR, "form.panel button[type=submit]")
    )
    wait(browser).until(lambda d: "/login" not in d.current_url)
    for path in ("/", "/events/1", "/checkout/1", "/orders"):  # visible on every page
        browser.get(server.url + path)
        assert (
            Select(css(browser, "#nav-currency")).first_selected_option.get_attribute(
                "value"
            )
            == "EUR"
        )
    browser.get(server.url)
    assert "one ticket in EUR" in css(browser, "#quick-buy-hint").text
    browser.get(f"{server.url}/checkout/1")
    assert "preferred currency (EUR)" in css(browser, "#currency-source").text
    assert (
        Select(css(browser, "#currency")).first_selected_option.get_attribute("value")
        == "EUR"
    )
    browser.get(f"{server.url}/events/1")
    assert (
        "EUR 16.56" in body_text(browser)
        and "your preferred currency" in css(browser, "#currency-note").text
    )
    shot(browser, "currency_visible_event_page")


@pytest.mark.req("identity-019", "pricing-016")
def test_changing_the_currency_in_the_header_sticks_on_the_next_pages(browser, server):
    signed_in(browser, server.url, server.new_user())
    browser.get(f"{server.url}/events/2")
    Select(css(browser, "#nav-currency")).select_by_value("JPY")
    click(browser, browser.find_element(By.CSS_SELECTOR, "#currency-form button"))
    wait_for_text(browser, "Preferred currency updated")
    assert browser.current_url.endswith("/events/2")  # returned to the same page
    assert "JPY 3,750" in body_text(browser)
    browser.get(server.url + "/orders")
    assert (
        Select(css(browser, "#nav-currency")).first_selected_option.get_attribute(
            "value"
        )
        == "JPY"
    )


@pytest.mark.req("pricing-016")
def test_signed_out_visitors_have_no_currency_control(browser, server):
    browser.get(server.url)
    assert not browser.find_elements(By.ID, "nav-currency")
    assert "Sign in to use double-click quick-buy" in body_text(browser)


# ================================================================ Kenji finding 1: the discount that stayed
@pytest.mark.req("identity-020")
def test_there_is_no_way_to_change_an_email_address_from_the_website(browser, server):
    user = server.new_user("only-way-in@example.com")
    signed_in(browser, server.url, user)
    for path in ("/", "/orders", "/events/1", "/checkout/1"):
        browser.get(server.url + path)
        links = [
            a.get_attribute("href") or ""
            for a in browser.find_elements(By.TAG_NAME, "a")
        ]
        assert not [
            h for h in links if re.search(r"account|profile|settings|email", h, re.I)
        ]
    for path in (
        "/account",
        "/profile",
        "/settings",
        "/account/email",
        "/change-email",
    ):
        browser.get(server.url + path)
        assert "not found" in body_text(browser).lower()
    assert (
        server.scalar("SELECT email FROM accounts WHERE id=?", (user["id"],))
        == "only-way-in@example.com"
    )


@pytest.mark.req("pricing-015", "pricing-003")
def test_when_the_qualifying_email_goes_away_the_next_purchase_is_full_price(
    browser, server
):
    """No screen changes emails yet, so an operator's database edit stands in for the future feature."""
    user, event = (
        server.new_user("moving-on@usf.edu"),
        server.new_event(available=10, price_minor=2000),
    )
    signed_in(browser, server.url, user)
    buy_via_checkout(browser, server.url, event, "1")
    assert css(browser, "#charged-total").text == "USD 18.00"
    server.run(
        "UPDATE accounts SET email='moving-on@gmail.com' WHERE id=?", (user["id"],)
    )
    buy_via_checkout(browser, server.url, event, "1")
    assert css(
        browser, "#charged-total"
    ).text == "USD 20.00" and "Student discount" not in body_text(browser)


@pytest.mark.req("pricing-011")
def test_known_risk_registering_with_any_usf_address_earns_the_discount(
    browser, server
):
    """RISK-001 / open item Q3: nobody checks that the registrant owns the mailbox. Documented, not fixed."""
    email = f"friend-of-student{int(time.time() * 1000)}@usf.edu"
    register_ui(browser, server.url, "Not A Student", email)
    wait_for_text(browser, "Account created")
    event = server.new_event(available=5, price_minor=2000)
    signed_in(
        browser, server.url, {"email": email, "password": "correct-horse-battery"}
    )
    buy_via_checkout(browser, server.url, event, "1")
    assert css(browser, "#charged-total").text == "USD 18.00"

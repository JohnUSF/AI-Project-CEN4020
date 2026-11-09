"""White-box edge cases: chosen by reading the source (branches, transactions, settings, templates)."""

import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from .conftest import Server
from .helpers import (
    alerts,
    body_text,
    buy_via_checkout,
    click,
    css,
    csrf_and_token,
    fetch_post,
    shot,
    signed_in,
    submit_checkout_raw,
    wait,
    wait_for_text,
    wait_for_url,
)

pytestmark = pytest.mark.whitebox


def quick_buy_from_event_page(browser, base, event_id):
    browser.get(f"{base}/events/{event_id}")
    click(browser, browser.find_element(By.XPATH, "//button[contains(., 'Quick buy')]"))


# ---------------------------------------------------------------- money (pricing.py)
@pytest.mark.req("pricing-008", "pricing-004", "pricing-006")
def test_yen_has_no_decimals_and_rounds_once(browser, server):
    event = server.new_event(
        available=10, price_minor=125
    )  # USD 1.25 * 150 = JPY 187.5
    signed_in(browser, server.url, server.new_user())
    text = buy_via_checkout(browser, server.url, event, "1", "JPY")
    assert css(browser, "#charged-total").text == "JPY 188"  # half-up, whole yen


@pytest.mark.req("pricing-008", "pricing-007")
def test_the_live_estimate_and_the_final_charge_use_the_same_price(browser, server):
    event = server.new_event(available=10, price_minor=1999)
    signed_in(browser, server.url, server.new_user())
    browser.get(f"{server.url}/checkout/{event}")
    Select(css(browser, "#currency")).select_by_value("GBP")
    q = browser.find_element(By.ID, "quantity")
    q.clear()
    q.send_keys("3")
    wait(browser).until(
        lambda d: "Estimated total: GBP 46.78" in css(d, "#price-preview").text
    )
    estimate = (
        css(browser, "#price-preview").text.split("Estimated total: ")[1].split(" (")[0]
    )
    click(
        browser,
        browser.find_element(By.CSS_SELECTOR, "#checkout-form button[type=submit]"),
    )
    wait_for_url(browser, "/orders/")
    assert (
        css(browser, "#charged-total").text == estimate == "GBP 46.78"
    )  # 59.97 * 0.78


@pytest.mark.req("pricing-011", "pricing-012", "pricing-013")
@pytest.mark.parametrize(
    "address", ["grad@usf.edu", "GRAD@USF.EDU", "nick+club@usf.edu"]
)
def test_usf_addresses_get_the_discount_whatever_their_case_or_plus_tag(
    browser, server, address
):
    user = server.new_user(
        f"p{Server._counter + 1}-{address}"
    )  # unique, but keeps the case and domain under test
    event = server.new_event(available=10, price_minor=2000)
    signed_in(browser, server.url, user)
    buy_via_checkout(browser, server.url, event, "1", "USD")
    assert css(
        browser, "#charged-total"
    ).text == "USD 18.00" and "10% off" in body_text(browser)


@pytest.mark.req("pricing-014", "pricing-003")
@pytest.mark.parametrize(
    "address",
    ["kid@mail.usf.edu", "kid@usf.edu.evil.org", "kid@notusf.edu", "usf.edu@gmail.com"],
)
def test_lookalike_and_subdomain_addresses_pay_the_standard_price(
    browser, server, address
):
    user = server.new_user(address)
    event = server.new_event(available=10, price_minor=2000)
    signed_in(browser, server.url, user)
    buy_via_checkout(browser, server.url, event, "1", "USD")
    assert css(
        browser, "#charged-total"
    ).text == "USD 20.00" and "Student discount" not in body_text(browser)


@pytest.mark.req("pricing-011", "purchase-005", "inventory-004")
def test_with_no_discount_configured_a_student_checkout_stops_before_taking_tickets(
    browser, server_no_discount
):
    srv = server_no_discount
    student, other = srv.new_user("stu@usf.edu"), srv.new_user("other@example.com")
    event = srv.new_event(available=10)
    signed_in(browser, srv.url, student)
    browser.get(f"{srv.url}/checkout/{event}")
    assert "discount percent is not provided" in body_text(browser)
    tokens = csrf_and_token(browser)
    # Use the browser's session to POST the exact fields explicitly. This checks
    # the fail-closed server behavior independently of asynchronous page scripts.
    response = fetch_post(
        browser,
        f"/checkout/{event}",
        {
            "csrf_token": tokens["csrf"],
            "purchase_token": tokens["token"],
            "quantity": "1",
            "currency": "USD",
        },
    )
    assert "discount percentage is still pending" in response["text"].lower()
    assert srv.scalar("SELECT available FROM events WHERE id=?", (event,)) == 10
    assert (
        srv.scalar("SELECT COUNT(*) FROM orders WHERE account_id=?", (student["id"],))
        == 0
    )
    assert (
        srv.scalar(
            "SELECT outcome FROM audit WHERE account_id=? ORDER BY id DESC",
            (student["id"],),
        )
        == "configuration_pending"
    )
    browser.delete_all_cookies()
    signed_in(browser, srv.url, other)
    buy_via_checkout(browser, srv.url, event, "1", "USD")
    assert "charged-total" in browser.page_source


# ---------------------------------------------------------------- exchange rates (admin.py)
@pytest.mark.req("admin-006", "pricing-010", "purchase-019", "audit-004")
def test_a_rate_change_applies_to_new_orders_and_never_rewrites_old_ones(
    browser, server
):
    admin, buyer = server.new_user(role="administrator"), server.new_user()
    event = server.new_event(available=10, price_minor=1000)
    signed_in(browser, server.url, buyer)
    buy_via_checkout(browser, server.url, event, "1", "EUR")
    first_url = browser.current_url
    assert css(browser, "#charged-total").text == "EUR 9.20"
    browser.delete_all_cookies()

    signed_in(browser, server.url, admin)
    browser.get(server.url + "/admin")
    Select(css(browser, "#currency")).select_by_visible_text("EUR")
    css(browser, "#rate").send_keys("1.10")
    click(browser, browser.find_element(By.XPATH, "//button[contains(., 'Save rate')]"))
    wait_for_text(browser, "Exchange rate saved and audited")
    assert "0.92 -&gt; 1.10" in browser.page_source or "0.92 -> 1.10" in body_text(
        browser
    )
    browser.delete_all_cookies()

    signed_in(browser, server.url, buyer)
    buy_via_checkout(browser, server.url, event, "1", "EUR")
    assert css(browser, "#charged-total").text == "EUR 11.00"
    browser.get(first_url)
    assert css(
        browser, "#charged-total"
    ).text == "EUR 9.20" and "1 USD = 0.92 EUR" in body_text(browser)
    server.run(
        "UPDATE rates SET units_per_usd='0.92' WHERE currency='EUR'"
    )  # leave the shared rate as found


@pytest.mark.req("admin-007")
@pytest.mark.parametrize(
    "bad", ["-1", "0", "abc", "1e2", "1.123456789", "", "1000000", "1;DROP"]
)
def test_bad_exchange_rates_are_refused_and_the_old_rate_stays(browser, server, bad):
    signed_in(browser, server.url, server.new_user(role="administrator"))
    browser.get(server.url + "/admin")
    Select(css(browser, "#currency")).select_by_visible_text("GBP")
    css(browser, "#rate").send_keys(bad or " ")
    browser.execute_script(
        "document.getElementById('rate').removeAttribute('required')"
    )
    click(browser, browser.find_element(By.XPATH, "//button[contains(., 'Save rate')]"))
    wait(browser).until(lambda d: any("Rate" in a or "rate" in a for a in alerts(d)))
    assert (
        server.scalar("SELECT units_per_usd FROM rates WHERE currency='GBP'") == "0.78"
    )


@pytest.mark.req("admin-007")
def test_the_dollar_reference_rate_cannot_be_changed(browser, server):
    signed_in(browser, server.url, server.new_user(role="administrator"))
    browser.get(server.url + "/admin")
    Select(css(browser, "#currency")).select_by_visible_text("USD")
    css(browser, "#rate").send_keys("1.5")
    click(browser, browser.find_element(By.XPATH, "//button[contains(., 'Save rate')]"))
    wait_for_text(browser, "must stay at 1")
    assert server.scalar("SELECT units_per_usd FROM rates WHERE currency='USD'") == "1"


# ---------------------------------------------------------------- audit (audit.py, purchase.py)
@pytest.mark.req("audit-001", "audit-008", "admin-008")
def test_every_purchase_attempt_leaves_exactly_one_audit_row_and_the_admin_sees_newest_first(
    browser, server
):
    buyer, admin = server.new_user(), server.new_user(role="administrator")
    event = server.new_event(available=2)
    signed_in(browser, server.url, buyer)
    for quantity in ("0", "5", "1"):  # invalid, sold out, success
        browser.get(f"{server.url}/checkout/{event}")
        css(browser, "#checkout-form")
        submit_checkout_raw(browser, quantity)
        wait(browser).until(lambda d: "/checkout/" not in d.current_url)
    rows = server.sql(
        'SELECT outcome FROM audit WHERE account_id=? AND kind="purchase" ORDER BY id',
        (buyer["id"],),
    )
    assert [r[0] for r in rows] == ["invalid_quantity", "sold_out", "success"]
    browser.delete_all_cookies()
    signed_in(browser, server.url, admin)
    browser.get(server.url + "/admin")
    first_row = browser.find_elements(By.CSS_SELECTOR, ".audit-table tbody tr")[0].text
    assert (
        "success" in first_row or "rate_change" in first_row or "purchase" in first_row
    )
    shot(browser, "admin_audit_log")


@pytest.mark.req("purchase-018")
def test_a_confirmation_code_checks_in_once_and_only_once(browser, server):
    buyer, admin = server.new_user(), server.new_user(role="administrator")
    event = server.new_event(available=5)
    signed_in(browser, server.url, buyer)
    buy_via_checkout(browser, server.url, event, "1")
    code = css(browser, ".code-panel code").text
    order_url = browser.current_url
    browser.delete_all_cookies()
    signed_in(browser, server.url, admin)
    for expected in ("marked used", "already checked in"):
        browser.get(server.url + "/admin")
        css(browser, "#confirmation_code").send_keys(code)
        click(
            browser, browser.find_element(By.XPATH, "//button[contains(., 'Check in')]")
        )
        wait_for_text(browser, expected)
    browser.delete_all_cookies()
    signed_in(browser, server.url, buyer)
    browser.get(order_url)
    assert "Used" in body_text(browser)


@pytest.mark.req("admin-005", "purchase-018")
def test_an_unknown_confirmation_code_is_refused(browser, server):
    signed_in(browser, server.url, server.new_user(role="administrator"))
    browser.get(server.url + "/admin")
    css(browser, "#confirmation_code").send_keys("not-a-real-code")
    click(browser, browser.find_element(By.XPATH, "//button[contains(., 'Check in')]"))
    wait_for_text(browser, "not found or already checked in")


# ---------------------------------------------------------------- inventory display (catalog.py)
@pytest.mark.req("catalog-005", "inventory-002")
def test_the_tickets_left_count_on_the_pages_drops_after_a_purchase(browser, server):
    event = server.new_event(available=8, artist="Countdown Quartet")
    signed_in(browser, server.url, server.new_user())
    buy_via_checkout(browser, server.url, event, "3")
    browser.get(f"{server.url}/events/{event}")
    assert "5 tickets" in body_text(browser)
    browser.get(f"{server.url}/?q=Countdown")
    assert "5 left" in body_text(browser)


# ---------------------------------------------------------------- settings (web.py create_app)
@pytest.mark.req("purchase-008")
def test_the_per_account_ticket_cap_counts_earlier_orders(browser, server_capped):
    srv = server_capped
    event = srv.new_event(available=50)
    signed_in(browser, srv.url, srv.new_user())
    buy_via_checkout(browser, srv.url, event, "2")
    browser.get(f"{srv.url}/checkout/{event}")
    css(browser, "#checkout-form")
    submit_checkout_raw(browser, "2")
    wait_for_text(browser, "Purchase limit reached")
    assert (
        srv.scalar("SELECT SUM(quantity) FROM orders WHERE event_id=?", (event,)) == 2
    )


@pytest.mark.req("identity-006", "system-004", "system-005")
def test_an_idle_session_expires_and_asks_for_sign_in(browser, server_fast_session):
    srv = server_fast_session
    signed_in(browser, srv.url, srv.new_user())
    browser.get(srv.url + "/orders")
    assert "My tickets" in body_text(browser)
    time.sleep(4.5)  # idle timeout is 3 s on this server
    browser.get(srv.url + "/orders")
    wait_for_url(browser, "/login")
    assert "My tickets" not in css(browser, "h1").text


@pytest.mark.req("system-002")
def test_security_headers_and_no_caching_of_signed_in_pages(browser, server):
    signed_in(browser, server.url, server.new_user())
    headers = browser.execute_async_script(
        "const d=arguments[arguments.length-1]; fetch('/orders').then(r=>d(Object.fromEntries(r.headers.entries())));"
    )
    assert (
        headers["x-frame-options"] == "DENY"
        and headers["x-content-type-options"] == "nosniff"
    )
    assert "default-src 'self'" in headers["content-security-policy"]
    assert headers["cache-control"] == "no-store"


@pytest.mark.req("system-002")
def test_an_oversized_request_body_is_refused(browser, server):
    browser.get(server.url + "/login")
    token = csrf_and_token(browser)["csrf"]
    result = fetch_post(
        browser,
        "/login",
        {"csrf_token": token, "email": "a@b.co", "password": "x" * 40000},
    )
    assert result["status"] == 413 and "Traceback" not in result["text"]


@pytest.mark.req("pricing-006", "pricing-007")
def test_the_event_page_shows_the_price_in_the_buyers_currency(browser, server):
    signed_in(browser, server.url, server.new_user(currency="JPY"))
    browser.get(f"{server.url}/events/1")
    assert "JPY 2,700" in body_text(browser)

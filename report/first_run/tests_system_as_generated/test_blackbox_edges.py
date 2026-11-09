"""Black-box edge cases: derived from the EARS requirements and the Call 5 transcript only.

Techniques: equivalence classes, boundary values, error guessing. Each test says which
requirement it protects. None of them looks at how the code is written.
"""

import time

import pytest
from selenium.webdriver.common.by import By

from .helpers import (
    alerts,
    body_text,
    csrf_and_token,
    css,
    fetch_post,
    login,
    register_ui,
    signed_in,
    submit_checkout_raw,
    wait,
    wait_for_text,
    wait_for_url,
)

pytestmark = pytest.mark.blackbox


# ----------------------------------------------------------------- quantity (purchase-007/010/011)
@pytest.mark.req("purchase-007", "purchase-010", "purchase-011")
@pytest.mark.parametrize(
    "quantity",
    [
        "0",
        "-1",
        "-100",
        "abc",
        "1.5",
        "1e2",
        " 3",
        "",
        "２",
        "10001",
        "999999999",
        "00000000001",
    ],
)
def test_invalid_quantities_are_rejected_on_the_server_with_a_quantity_message(
    browser, server, quantity
):
    user = server.new_user()
    event = server.new_event(available=20)
    signed_in(browser, server.url, user)
    browser.get(f"{server.url}/checkout/{event}")
    css(browser, "#checkout-form")
    submit_checkout_raw(browser, quantity)
    wait_for_text(browser, "Invalid quantity")
    assert (
        server.scalar("SELECT COUNT(*) FROM orders WHERE account_id=?", (user["id"],))
        == 0
    )
    assert server.scalar("SELECT available FROM events WHERE id=?", (event,)) == 20


@pytest.mark.req("purchase-006", "purchase-011", "inventory-004")
def test_asking_for_more_than_remain_says_sold_out_not_invalid_quantity(
    browser, server
):
    event = server.new_event(available=3)
    signed_in(browser, server.url, server.new_user())
    browser.get(f"{server.url}/checkout/{event}")
    css(browser, "#checkout-form")
    submit_checkout_raw(browser, "4")
    wait_for_text(browser, "Sold out")
    assert "Invalid quantity" not in body_text(browser)
    assert server.scalar("SELECT available FROM events WHERE id=?", (event,)) == 3


@pytest.mark.req("purchase-004", "inventory-003")
def test_buying_exactly_the_remaining_tickets_works_and_the_next_buyer_is_told_sold_out(
    browser, server
):
    event = server.new_event(available=5)
    signed_in(browser, server.url, server.new_user())
    browser.get(f"{server.url}/checkout/{event}")
    css(browser, "#checkout-form")
    submit_checkout_raw(browser, "5")
    wait_for_url(browser, "/orders/")
    assert server.scalar("SELECT available FROM events WHERE id=?", (event,)) == 0
    browser.get(f"{server.url}/events/{event}")
    wait_for_text(browser, "0 tickets")
    browser.get(f"{server.url}/checkout/{event}")
    submit_checkout_raw(browser, "1")
    wait_for_text(browser, "Sold out")


@pytest.mark.req("purchase-004")
def test_buying_one_ticket_is_the_smallest_valid_order(browser, server):
    event = server.new_event(available=2)
    signed_in(browser, server.url, server.new_user())
    browser.get(f"{server.url}/checkout/{event}")
    css(browser, "#checkout-form")
    submit_checkout_raw(browser, "1")
    wait_for_url(browser, "/orders/")
    assert server.scalar("SELECT available FROM events WHERE id=?", (event,)) == 1


# ----------------------------------------------------------------- currency (pricing-001)
@pytest.mark.req("pricing-001", "purchase-005", "purchase-011")
@pytest.mark.parametrize(
    "currency", ["XYZ", "usd", "USD ", "BTC", "USD'; DROP TABLE orders;--", ""]
)
def test_unsupported_currency_values_are_rejected_whatever_the_browser_sends(
    browser, server, currency
):
    event = server.new_event(available=10)
    user = server.new_user()
    signed_in(browser, server.url, user)
    browser.get(f"{server.url}/checkout/{event}")
    css(browser, "#checkout-form")
    submit_checkout_raw(browser, "1", currency)
    wait_for_text(browser, "Unsupported currency")
    assert (
        server.scalar("SELECT COUNT(*) FROM orders WHERE account_id=?", (user["id"],))
        == 0
    )
    assert (
        server.scalar("SELECT COUNT(*) FROM orders") >= 0
    )  # orders table still exists


@pytest.mark.req("pricing-006", "pricing-001")
@pytest.mark.parametrize("currency", ["USD", "EUR", "GBP", "JPY"])
def test_every_supported_currency_can_be_bought_in(browser, server, currency):
    event = server.new_event(available=10, price_minor=2000)
    signed_in(browser, server.url, server.new_user())
    browser.get(f"{server.url}/checkout/{event}")
    css(browser, "#checkout-form")
    submit_checkout_raw(browser, "1", currency)
    wait_for_url(browser, "/orders/")
    assert css(browser, "#charged-total").text.startswith(currency)


# ----------------------------------------------------------------- logged-out behaviour
@pytest.mark.req("identity-010", "identity-011", "identity-012")
@pytest.mark.parametrize(
    "path", ["/checkout/1", "/orders", "/orders/1", "/quote/1?quantity=1"]
)
def test_protected_pages_redirect_signed_out_visitors_to_login(browser, server, path):
    before = (
        server.scalar("SELECT COUNT(*) FROM orders"),
        server.scalar("SELECT COUNT(*) FROM audit"),
    )
    browser.get(server.url + path)
    wait_for_url(browser, "/login")
    assert (
        "Almost there" not in body_text(browser)
        and "My tickets" not in css(browser, "h1").text
    )
    assert (
        server.scalar("SELECT COUNT(*) FROM orders"),
        server.scalar("SELECT COUNT(*) FROM audit"),
    ) == before


@pytest.mark.req("identity-007", "identity-012", "purchase-005")
def test_a_forged_purchase_post_from_a_signed_out_browser_buys_nothing(browser, server):
    browser.get(server.url)
    csrf = browser.find_element(By.NAME, "csrf_token").get_attribute("value")
    before = server.scalar("SELECT COUNT(*) FROM orders")
    result = fetch_post(
        browser,
        "/checkout/1",
        {
            "csrf_token": csrf,
            "quantity": "1",
            "currency": "USD",
            "purchase_token": "forged-token-0123456789",
        },
    )
    assert "/login" in result["url"]
    assert server.scalar("SELECT COUNT(*) FROM orders") == before


# ----------------------------------------------------------------- search (catalog-002/003/007/008)
@pytest.mark.req("catalog-002", "catalog-003")
@pytest.mark.parametrize(
    "term,expected",
    [
        ("JAZZ", "Campus Jazz Collective"),
        ("jazz", "Campus Jazz Collective"),
        ("  jazz  ", "Campus Jazz Collective"),
        ("marshall", "Indie Nights"),
        ("Bulls Arena", "Tampa Dance Lab"),
        ("acou", "Acoustic Afternoon"),
    ],
)
def test_search_matches_artist_or_venue_ignoring_case_and_padding(
    browser, server, term, expected
):
    browser.get(f"{server.url}/?q={term}")
    cards = browser.find_elements(By.CSS_SELECTOR, ".event-card")
    assert any(
        expected in c.text for c in cards
    ) and "No events match" not in body_text(browser)


@pytest.mark.req("catalog-007")
@pytest.mark.parametrize(
    "term", ["zzzz-no-such-band", "%", "_", "%%", "' OR '1'='1", "Café ☕", "\\"]
)
def test_a_search_with_no_match_says_so_and_then_lists_everything(
    browser, server, term
):
    browser.get(server.url)
    box = css(browser, "#q")
    box.send_keys(term)
    browser.find_element(By.CSS_SELECTOR, ".search button").click()
    wait_for_text(browser, "No events match")
    assert len(browser.find_elements(By.CSS_SELECTOR, ".event-card")) == server.scalar(
        "SELECT COUNT(*) FROM events"
    )


@pytest.mark.req("catalog-001")
@pytest.mark.parametrize("term", ["", "   "])
def test_an_empty_search_shows_the_full_list_without_a_complaint(browser, server, term):
    browser.get(f"{server.url}/?q={term}")
    assert "No events match" not in body_text(browser)
    assert len(browser.find_elements(By.CSS_SELECTOR, ".event-card")) == server.scalar(
        "SELECT COUNT(*) FROM events"
    )


@pytest.mark.req("catalog-008", "system-002")
@pytest.mark.parametrize(
    "payload",
    [
        "<script>window.__xss=1</script>",
        '"><img src=x onerror=window.__xss=1>',
        "'><svg onload=window.__xss=1>",
    ],
)
def test_search_text_is_echoed_as_plain_text_never_as_markup(browser, server, payload):
    browser.get(server.url)
    box = css(browser, "#q")
    box.send_keys(payload)
    browser.find_element(By.CSS_SELECTOR, ".search button").click()
    wait_for_text(browser, "No events match")
    time.sleep(0.3)
    assert browser.execute_script("return window.__xss") is None
    assert not browser.find_elements(
        By.CSS_SELECTOR, ".notice img, .notice svg, .notice script"
    )
    assert payload in body_text(browser)  # shown literally, as text


@pytest.mark.req("system-002")
def test_a_very_long_search_term_does_not_break_the_page(browser, server):
    browser.get(f"{server.url}/?q=" + "a" * 5000)
    assert "Upcoming events" in body_text(browser) or "No events match" in body_text(
        browser
    )


# ----------------------------------------------------------------- registration / login
@pytest.mark.req("identity-001", "system-002")
@pytest.mark.parametrize(
    "name,email,password,message",
    [
        ("Short Pass", "shortpass@example.com", "abc123", "Password must be between"),
        ("Nine Chars", "nine@example.com", "123456789", "Password must be between"),
        ("", "noname@example.com", "correct-horse-battery", "valid name"),
        ("   ", "blankname@example.com", "correct-horse-battery", "valid name"),
        ("N" * 101, "longname@example.com", "correct-horse-battery", "valid name"),
        ("Long Pass", "longpass@example.com", "p" * 257, "Password must be between"),
    ],
)
def test_registration_rejects_bad_names_and_passwords(
    browser, server, name, email, password, message
):
    register_ui(browser, server.url, name, email, password, raw=True)
    wait_for_text(browser, message)
    assert server.scalar("SELECT COUNT(*) FROM accounts WHERE email=?", (email,)) == 0


@pytest.mark.req("identity-001")
def test_the_same_email_cannot_register_twice_whatever_its_case(browser, server):
    server.new_user("Dup.Person@Example.com")
    register_ui(browser, server.url, "Dup Two", "dup.person@example.COM", raw=True)
    wait_for_text(browser, "already registered")


@pytest.mark.req("identity-001", "identity-015")
def test_a_name_with_html_in_it_is_stored_and_shown_as_text(browser, server):
    register_ui(
        browser,
        server.url,
        "<b>Bold</b>",
        f"html{int(time.time() * 1000)}@example.com",
        raw=True,
    )
    wait_for_text(browser, "Account created")
    assert (
        server.scalar("SELECT role FROM accounts WHERE name='<b>Bold</b>'") == "buyer"
    )


@pytest.mark.req("identity-005")
def test_wrong_password_and_unknown_email_get_the_same_message(browser, server):
    user = server.new_user()
    login(browser, server.url, user["email"], "wrong-password-123")
    wait_for_text(browser, "Invalid credentials")
    first = alerts(browser)
    login(browser, server.url, "nobody-here@example.com", "wrong-password-123")
    wait_for_text(browser, "Invalid credentials")
    assert alerts(browser) == first


@pytest.mark.req("identity-008")
def test_email_case_and_padding_do_not_stop_a_valid_login(browser, server):
    user = server.new_user("MiXeD.Case@Example.com")
    login(browser, server.url, "  MIXED.case@example.COM ")
    wait(browser).until(lambda d: "/login" not in d.current_url)
    assert "Sign out" in body_text(browser)


@pytest.mark.req("identity-014")
@pytest.mark.parametrize(
    "target",
    [
        "//evil.example/x",
        "https://evil.example",
        "/\\evil.example",
        "javascript:alert(1)",
    ],
)
def test_sign_in_never_sends_the_visitor_to_another_site(browser, server, target):
    user = server.new_user()
    browser.get(f"{server.url}/login?next={target}")
    css(browser, "#email").send_keys(user["email"])
    browser.find_element(By.ID, "password").send_keys(user["password"])
    browser.find_element(By.CSS_SELECTOR, "form.panel button[type=submit]").click()
    wait(browser).until(lambda d: "/login" not in d.current_url)
    assert (
        browser.current_url.startswith(server.url)
        and "evil.example" not in browser.current_url
    )


@pytest.mark.req("system-002")
def test_a_tampered_security_token_is_refused(browser, server):
    user = server.new_user()
    browser.get(server.url + "/login")
    css(browser, "#email").send_keys(user["email"])
    browser.find_element(By.ID, "password").send_keys(user["password"])
    browser.execute_script(
        "document.querySelector('[name=csrf_token]').value='tampered';"
    )
    browser.find_element(By.CSS_SELECTOR, "form.panel button[type=submit]").click()
    wait_for_text(browser, "security token")
    assert "Sign out" not in body_text(browser)


# ----------------------------------------------------------------- roles and privacy
@pytest.mark.req("admin-002")
def test_signed_out_visitors_cannot_reach_the_admin_area(browser, server):
    browser.get(server.url + "/admin")
    wait_for_url(browser, "/login")
    assert "Exchange rates" not in body_text(browser)


@pytest.mark.req("admin-003", "admin-004", "admin-005")
def test_a_buyer_is_refused_the_admin_pages_and_actions(browser, server):
    signed_in(browser, server.url, server.new_user())
    browser.get(server.url + "/admin")
    assert (
        "Exchange rates" not in body_text(browser)
        and "Admin" not in css(browser, "nav").text
    )
    token = csrf_and_token(browser)["csrf"]
    result = fetch_post(
        browser, "/admin/rates", {"csrf_token": token, "currency": "EUR", "rate": "9"}
    )
    assert result["status"] == 403
    assert (
        server.scalar("SELECT units_per_usd FROM rates WHERE currency='EUR'") == "0.92"
    )


@pytest.mark.req("purchase-016", "identity-007")
def test_one_buyer_cannot_open_another_buyers_order(browser, server):
    owner, intruder = server.new_user(), server.new_user()
    event = server.new_event(available=5)
    signed_in(browser, server.url, owner)
    browser.get(f"{server.url}/checkout/{event}")
    submit_checkout_raw(browser, "1")
    wait_for_url(browser, "/orders/")
    order_url = browser.current_url
    browser.delete_all_cookies()
    signed_in(browser, server.url, intruder)
    browser.get(order_url)
    assert "charged" not in body_text(
        browser
    ).lower() and "CONFIRMATION CODE" not in body_text(browser)


@pytest.mark.req("purchase-016")
def test_a_new_buyer_sees_an_empty_order_history(browser, server):
    signed_in(browser, server.url, server.new_user())
    browser.get(server.url + "/orders")
    assert "No orders yet" in body_text(browser)


@pytest.mark.req("catalog-001", "system-002")
@pytest.mark.parametrize(
    "path", ["/events/99999", "/events/0", "/events/-1", "/events/abc", "/nonexistent"]
)
def test_unknown_pages_show_a_clean_error_not_a_crash(browser, server, path):
    browser.get(server.url + path)
    text = body_text(browser)
    assert (
        "Event not found" in text or "not found" in text.lower()
    ) and "Traceback" not in text

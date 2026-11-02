"""HTTP-level tests for behaviour decided or changed after Call 5."""

import re
import sqlite3

import pytest

pytest.importorskip("flask")
from eventhub import db as db_module
from eventhub.db import connect
from eventhub.identity import register
from .test_web import csrf, sign_in

TOKEN = "tok-web-0123456789ab"


def post_checkout(client, token, **fields):
    data = {
        "csrf_token": token,
        "quantity": "1",
        "currency": "USD",
        "purchase_token": TOKEN,
    }
    data.update(fields)
    return client.post("/checkout/1", data=data)


def count(database, table, where="1=1"):
    with connect(database) as c:
        return c.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}").fetchone()[0]


# ---- double purchase ---------------------------------------------------------------
@pytest.mark.req("purchase-028")
@pytest.mark.call5
def test_checkout_without_a_token_is_refused_and_logged(app_factory):
    app, database = app_factory(DISCOUNT_PERCENT="10")
    client = app.test_client()
    sign_in(client, database)
    token = csrf(client)
    response = client.post(
        "/checkout/1", data={"csrf_token": token, "quantity": "1", "currency": "USD"}
    )
    assert response.status_code == 302 and "/events/1" in response.location
    assert "out of date" in client.get(response.location).get_data(as_text=True)
    assert count(database, "orders") == 0
    assert count(database, "audit", "outcome='invalid_request_token'") == 1


@pytest.mark.req("purchase-024")
@pytest.mark.call5
def test_pressing_buy_twice_with_one_form_makes_one_order(app_factory):
    app, database = app_factory(DISCOUNT_PERCENT="10")
    client = app.test_client()
    sign_in(client, database)
    token = csrf(client)
    first = post_checkout(client, token, quantity="2")
    second = post_checkout(client, token, quantity="2")
    assert first.location == second.location and "/orders/" in first.location
    assert count(database, "orders") == 1
    with connect(database) as c:
        assert c.execute("SELECT available FROM events WHERE id=1").fetchone()[0] == 118
    page = client.get(second.location).get_data(as_text=True)
    assert "not charged twice" in page


@pytest.mark.req("purchase-024")
@pytest.mark.call5
def test_quick_buy_pressed_three_times_makes_one_order(app_factory):
    app, database = app_factory(DISCOUNT_PERCENT="10")
    client = app.test_client()
    sign_in(client, database)
    token = csrf(client)
    locations = {
        client.post(
            "/quick-buy/1", data={"csrf_token": token, "purchase_token": TOKEN}
        ).location
        for _ in range(3)
    }
    assert len(locations) == 1 and count(database, "orders") == 1


@pytest.mark.req("purchase-026")
@pytest.mark.call5
def test_reusing_a_token_for_another_event_is_refused(app_factory):
    app, database = app_factory(DISCOUNT_PERCENT="10")
    client = app.test_client()
    sign_in(client, database)
    token = csrf(client)
    post_checkout(client, token)
    response = client.post(
        "/checkout/2",
        data={
            "csrf_token": token,
            "quantity": "1",
            "currency": "USD",
            "purchase_token": TOKEN,
        },
    )
    assert response.status_code == 302 and "/events/2" in response.location
    assert (
        count(database, "orders") == 1
        and count(database, "audit", "outcome='duplicate_conflict'") == 1
    )


@pytest.mark.req("purchase-025")
@pytest.mark.call5
def test_every_purchase_form_gets_its_own_fresh_token(app_factory):
    app, database = app_factory(DISCOUNT_PERCENT="10")
    client = app.test_client()
    sign_in(client, database)
    pattern = re.compile(r'name="purchase_token" value="([^"]+)"')
    home = pattern.findall(client.get("/").get_data(as_text=True))
    assert len(home) == 4 and len(set(home)) == 4
    first = pattern.findall(client.get("/checkout/1").get_data(as_text=True))
    second = pattern.findall(client.get("/checkout/1").get_data(as_text=True))
    assert len(first) == 1 and len(second) == 1 and first != second
    assert len(pattern.findall(client.get("/events/1").get_data(as_text=True))) == 1


# ---- request speed -----------------------------------------------------------------
@pytest.mark.req("purchase-032", "audit-007")
@pytest.mark.call5
def test_two_hundred_requests_a_minute_are_stopped_and_logged_once(app_factory):
    app, database = app_factory(
        DISCOUNT_PERCENT="10", PURCHASE_RATE_LIMIT=5, PURCHASE_RATE_WINDOW=60
    )
    client = app.test_client()
    sign_in(client, database, "script@example.com")
    token = csrf(client)
    codes = [
        client.post(
            "/quick-buy/1",
            data={"csrf_token": token, "purchase_token": f"script-token-{i:08d}"},
        ).status_code
        for i in range(200)
    ]
    assert codes[:5] == [302] * 5 and codes[5:] == [429] * 195
    assert count(database, "orders") == 5
    assert count(database, "audit", "outcome='rate_limited'") == 1  # not 195 rows
    blocked = client.post(
        "/quick-buy/1",
        data={"csrf_token": token, "purchase_token": "script-token-99999999"},
    )
    assert int(blocked.headers["Retry-After"]) >= 1
    assert "wait" in blocked.get_data(as_text=True)


@pytest.mark.req("purchase-032")
@pytest.mark.call5
def test_one_account_being_limited_does_not_block_another(app_factory):
    app, database = app_factory(
        DISCOUNT_PERCENT="10", PURCHASE_RATE_LIMIT=2, PURCHASE_RATE_WINDOW=60
    )
    noisy, quiet = app.test_client(), app.test_client()
    sign_in(noisy, database, "noisy@example.com")
    sign_in(quiet, database, "quiet@example.com")
    tn, tq = csrf(noisy), csrf(quiet)
    for i in range(3):
        noisy.post(
            "/quick-buy/1",
            data={"csrf_token": tn, "purchase_token": f"noisy-token-{i:09d}"},
        )
    assert (
        quiet.post(
            "/quick-buy/1",
            data={"csrf_token": tq, "purchase_token": "quiet-token-000000001"},
        ).status_code
        == 302
    )


@pytest.mark.req("purchase-032")
@pytest.mark.whitebox
def test_a_validation_failure_still_counts_toward_the_limit(app_factory):
    app, database = app_factory(PURCHASE_RATE_LIMIT=2, PURCHASE_RATE_WINDOW=60)
    client = app.test_client()
    sign_in(client, database)
    token = csrf(client)
    codes = [
        post_checkout(
            client, token, quantity="0", purchase_token=f"bad-quantity-{i:08d}"
        ).status_code
        for i in range(3)
    ]
    assert codes == [302, 302, 429]


# ---- confirmation wording ----------------------------------------------------------
def buy(client, token, **fields):
    return client.get(post_checkout(client, token, **fields).location).get_data(
        as_text=True
    )


@pytest.mark.req("purchase-029")
@pytest.mark.call5
def test_foreign_currency_confirmation_says_what_was_charged(app_factory):
    app, database = app_factory(DISCOUNT_PERCENT="10")
    client = app.test_client()
    sign_in(client, database)
    page = buy(client, csrf(client), quantity="2", currency="EUR")
    assert re.search(r'id="charged-total">EUR 33\.12<', page)
    assert "only amount charged, in EUR" in page
    assert "USD 36.00" in page and "reference only, not charged" in page
    assert "1 USD = 0.92 EUR" in page
    assert "no real money moved" in page


@pytest.mark.req("purchase-029")
@pytest.mark.call5
def test_dollar_confirmation_has_no_conversion_noise(app_factory):
    app, database = app_factory(DISCOUNT_PERCENT="10")
    client = app.test_client()
    sign_in(client, database)
    page = buy(client, csrf(client), quantity="2", currency="USD")
    assert re.search(r'id="charged-total">USD 36\.00<', page)
    assert (
        "not charged" not in page
        and "Exchange rate" not in page
        and "Student discount" not in page
    )


@pytest.mark.req("purchase-029", "pricing-011")
@pytest.mark.call5
def test_student_confirmation_shows_the_discount_and_the_charge(app_factory):
    app, database = app_factory(DISCOUNT_PERCENT="10")
    client = app.test_client()
    sign_in(client, database, "grad@usf.edu")
    page = buy(client, csrf(client), quantity="2", currency="EUR")
    assert "EUR 29.81" in page and "10% off" in page  # 36.00 * 0.9 * 0.92 = 29.808


@pytest.mark.req("purchase-030")
@pytest.mark.call5
def test_order_history_detail_uses_the_same_wording(app_factory):
    app, database = app_factory(DISCOUNT_PERCENT="10")
    client = app.test_client()
    sign_in(client, database)
    token = csrf(client)
    location = post_checkout(client, token, currency="JPY").location
    assert "JPY 2,700" in client.get("/orders").get_data(as_text=True)
    detail = client.get(location).get_data(as_text=True)
    assert (
        'id="charged-total">JPY 2,700<' in detail
        and "reference only, not charged" in detail
    )


@pytest.mark.req("purchase-019", "purchase-030")
@pytest.mark.whitebox
def test_a_part4_database_is_upgraded_and_its_old_orders_still_open(
    tmp_path, app_factory
):
    """Part 4 orders have no stored unit price. They must still display, without the USD line."""
    old = tmp_path / "part4.sqlite3"
    conn = sqlite3.connect(old)
    conn.executescript(
        db_module.SCHEMA.replace(",\n  unit_usd_minor INTEGER, request_token TEXT", "")
    )
    conn.execute(
        "INSERT INTO accounts(id,name,email,password_hash) VALUES(1,'Old','old@example.com','x')"
    )
    conn.execute(
        """INSERT INTO events VALUES(1,'Old Show','Hall','2026-11-07 19:00','d',1800,10)"""
    )
    conn.execute("""INSERT INTO orders(id,account_id,event_id,quantity,currency,rate,discount_percent,
                    total_minor,confirmation_code) VALUES(1,1,1,2,'EUR','0.92','0',3312,'oldcode')""")
    conn.commit()
    conn.close()
    from eventhub.web import create_app

    app = create_app({"TESTING": True, "SECRET_KEY": "x" * 20, "DATABASE": str(old)})
    with connect(old) as c:
        cols = {r[1] for r in c.execute("PRAGMA table_info(orders)")}
        register(c, "Old", "old2@example.com", "correct-horse-battery")
        c.execute(
            "UPDATE accounts SET password_hash=(SELECT password_hash FROM accounts WHERE id=2) WHERE id=1"
        )
    assert {"unit_usd_minor", "request_token"} <= cols
    client = app.test_client()
    token = csrf(client, "/login")
    client.post(
        "/login",
        data={
            "csrf_token": token,
            "email": "old@example.com",
            "password": "correct-horse-battery",
        },
    )
    page = client.get("/orders/1").get_data(as_text=True)
    assert 'id="charged-total">EUR 33.12<' in page and 'id="usd-reference"' not in page


# ---- currency visibility -----------------------------------------------------------
@pytest.mark.req("pricing-016")
@pytest.mark.call5
@pytest.mark.parametrize("path", ["/", "/events/1", "/checkout/1", "/orders"])
def test_header_shows_the_preferred_currency_on_every_signed_in_page(app_factory, path):
    app, database = app_factory(DISCOUNT_PERCENT="10")
    client = app.test_client()
    sign_in(client, database)
    html = client.get(path).get_data(as_text=True)
    assert 'id="nav-currency"' in html and '<option value="USD" selected>' in html


@pytest.mark.req("pricing-016")
@pytest.mark.call5
def test_signed_out_visitors_see_no_currency_control(app_factory):
    app, _ = app_factory()
    assert 'id="nav-currency"' not in app.test_client().get("/").get_data(as_text=True)


@pytest.mark.req("identity-018")
@pytest.mark.call5
def test_registration_stores_the_chosen_currency(app_factory):
    app, database = app_factory()
    client = app.test_client()
    token = csrf(client, "/register")
    client.post(
        "/register",
        data={
            "csrf_token": token,
            "name": "Ana",
            "email": "ana@example.com",
            "password": "correct-horse-battery",
            "currency": "EUR",
        },
    )
    with connect(database) as c:
        assert c.execute("SELECT currency FROM accounts").fetchone()[0] == "EUR"


@pytest.mark.req("identity-018")
@pytest.mark.whitebox
def test_registration_rejects_a_currency_that_is_not_supported(app_factory):
    app, database = app_factory()
    client = app.test_client()
    token = csrf(client, "/register")
    client.post(
        "/register",
        data={
            "csrf_token": token,
            "name": "Ana",
            "email": "ana@example.com",
            "password": "correct-horse-battery",
            "currency": "BTC",
        },
    )
    assert count(database, "accounts") == 0


@pytest.mark.req("identity-019", "purchase-001")
@pytest.mark.call5
def test_a_changed_preferred_currency_is_what_quick_buy_uses(app_factory):
    app, database = app_factory(DISCOUNT_PERCENT="10")
    client = app.test_client()
    sign_in(client, database)
    token = csrf(client)
    client.post("/currency", data={"csrf_token": token, "currency": "GBP", "next": "/"})
    client.post("/quick-buy/1", data={"csrf_token": token, "purchase_token": TOKEN})
    with connect(database) as c:
        assert c.execute("SELECT currency, total_minor FROM orders").fetchone()[:] == (
            "GBP",
            1404,
        )


@pytest.mark.req("pricing-017")
@pytest.mark.call5
def test_checkout_says_which_currency_you_will_be_charged_in_and_why(app_factory):
    app, database = app_factory(DISCOUNT_PERCENT="10")
    client = app.test_client()
    sign_in(client, database)
    token = csrf(client)
    client.post("/currency", data={"csrf_token": token, "currency": "JPY"})
    html = client.get("/checkout/1").get_data(as_text=True)
    assert "charged in the currency selected above" in html
    assert (
        "preferred currency (JPY)" in html and '<option value="JPY" selected>' in html
    )


@pytest.mark.req("purchase-031")
@pytest.mark.call5
def test_the_home_page_names_the_currency_a_double_click_will_use(app_factory):
    app, database = app_factory()
    client = app.test_client()
    assert "Sign in to use double-click quick-buy" in client.get("/").get_data(
        as_text=True
    )
    sign_in(client, database)
    assert "one ticket in USD" in client.get("/").get_data(as_text=True)


@pytest.mark.req("pricing-011", "pricing-007")
@pytest.mark.whitebox
def test_the_pending_discount_notice_uses_the_same_rule_as_pricing(app_factory):
    """Part 4's template used its own endswith('@usf.edu'); it must use the one eligibility rule."""
    app, database = app_factory()  # no discount configured
    student, other = app.test_client(), app.test_client()
    sign_in(student, database, "kid@usf.edu")
    sign_in(other, database, "kid@mail.usf.edu")
    assert "USF student discount percent is not provided" in student.get(
        "/checkout/1"
    ).get_data(as_text=True)
    assert "USF student discount percent is not provided" not in other.get(
        "/checkout/1"
    ).get_data(as_text=True)


# ---- registration edge cases found by the black-box pass ---------------------------
@pytest.mark.req("identity-017")
@pytest.mark.blackbox
@pytest.mark.parametrize(
    "email",
    [
        "a@b@usf.edu",
        "no-at-sign.example.com",
        "space in@example.com",
        "user@nodot",
        "user@.example.com",
        "user@example..com",
        "user@example.com.",
        "@example.com",
        "user@",
    ],
)
def test_malformed_email_addresses_create_no_account(app_factory, email):
    app, database = app_factory()
    client = app.test_client()
    token = csrf(client, "/register")
    client.post(
        "/register",
        data={
            "csrf_token": token,
            "name": "X",
            "email": email,
            "password": "correct-horse-battery",
            "currency": "USD",
        },
    )
    assert count(database, "accounts") == 0

"""Kenji's finding 1: 'Eligibility was checked at registration and never again.'

In this build eligibility is judged from the account's *current* email at every quote
and purchase. These tests pin that down so a later email-change feature cannot break it
(pricing-015), and document the one real hole that remains (RISK-001, open item Q3/Q18).
"""

import pytest

from eventhub import purchase
from eventhub.identity import register

from .conftest import add_account


def last_order(conn):
    return conn.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 1").fetchone()


@pytest.mark.req("pricing-015", "pricing-003")
@pytest.mark.call5
def test_discount_disappears_when_the_qualifying_email_goes_away(connection):
    uid = add_account(connection, "student@usf.edu")
    purchase.purchase(
        connection,
        account_id=uid,
        event_id=1,
        quantity=1,
        currency="USD",
        discount_percent="10",
    )
    assert last_order(connection)["total_minor"] == 1620  # USD 16.20, discounted
    connection.execute(
        "UPDATE accounts SET email='student@gmail.com' WHERE id=?", (uid,)
    )
    purchase.purchase(
        connection,
        account_id=uid,
        event_id=1,
        quantity=1,
        currency="USD",
        discount_percent="10",
    )
    assert last_order(connection)["total_minor"] == 1800  # standard price again
    assert last_order(connection)["discount_percent"] == "0"


@pytest.mark.req("pricing-015")
@pytest.mark.whitebox
def test_discount_follows_the_email_in_the_other_direction_too(connection):
    uid = add_account(connection, "someone@gmail.com")
    connection.execute("UPDATE accounts SET email='someone@usf.edu' WHERE id=?", (uid,))
    purchase.purchase(
        connection,
        account_id=uid,
        event_id=1,
        quantity=1,
        currency="USD",
        discount_percent="10",
    )
    assert last_order(connection)["total_minor"] == 1620


@pytest.mark.req("pricing-015", "pricing-011")
@pytest.mark.whitebox
def test_the_quote_page_follows_the_current_email_not_a_remembered_result(app_factory):
    app, database = app_factory(DISCOUNT_PERCENT="10")
    client = app.test_client()
    from .test_web import sign_in

    sign_in(client, database, "grad@usf.edu")
    assert (
        client.get("/quote/1?quantity=1&currency=USD").get_json()["total"]
        == "USD 16.20"
    )
    from eventhub.db import connect

    with connect(database) as c:
        c.execute(
            "UPDATE accounts SET email='grad@alumni.example' WHERE email='grad@usf.edu'"
        )
    assert (
        client.get("/quote/1?quantity=1&currency=USD").get_json()["total"]
        == "USD 18.00"
    )


@pytest.mark.req("identity-020")
@pytest.mark.call5
def test_no_website_route_changes_an_email_address(app_factory):
    app, database = app_factory()
    names = {
        rule.rule.lower() + " " + rule.endpoint.lower()
        for rule in app.url_map.iter_rules()
    }
    assert not [n for n in names if "email" in n or "account" in n or "profile" in n]


@pytest.mark.req("identity-020")
@pytest.mark.whitebox
def test_posting_an_email_field_to_the_currency_route_does_not_change_it(app_factory):
    app, database = app_factory()
    client = app.test_client()
    from .test_web import csrf, sign_in

    sign_in(client, database, "keep@example.com")
    token = csrf(client)
    client.post(
        "/currency",
        data={"csrf_token": token, "currency": "EUR", "email": "evil@usf.edu"},
    )
    from eventhub.db import connect

    with connect(database) as c:
        row = c.execute("SELECT email, currency FROM accounts").fetchone()
    assert row["email"] == "keep@example.com" and row["currency"] == "EUR"


@pytest.mark.req("pricing-011")
@pytest.mark.call5
def test_known_risk_an_unverified_usf_address_is_eligible(connection):
    """RISK-001 (open item Q3): nothing proves the registrant owns the @usf.edu mailbox.

    This test documents today's behaviour. When the customer decides how to verify
    addresses, this test is the one that should change.
    """
    uid = register(
        connection,
        "Not A Student",
        "friend-of-a-student@usf.edu",
        "correct-horse-battery",
    )
    purchase.purchase(
        connection,
        account_id=uid,
        event_id=1,
        quantity=1,
        currency="USD",
        discount_percent="10",
    )
    assert last_order(connection)["total_minor"] == 1620


@pytest.mark.req("pricing-014", "pricing-003")
@pytest.mark.whitebox
@pytest.mark.parametrize(
    "address",
    ["kid@mail.usf.edu", "kid@notusf.edu", "kid@usf.edu.evil.org", "usf.edu@gmail.com"],
)
def test_lookalike_addresses_pay_full_price_through_the_whole_purchase_path(
    connection, address
):
    """Found by the mutation check: the rule was only tested on the function, not on the order it prices."""
    uid = add_account(connection, address)
    purchase.purchase(
        connection,
        account_id=uid,
        event_id=1,
        quantity=1,
        currency="USD",
        discount_percent="10",
    )
    assert last_order(connection)["total_minor"] == 1800

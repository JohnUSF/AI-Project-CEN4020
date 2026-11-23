"""Executable backfill of tagged Gherkin beside every older feature folder.

This preserves the original automated unit/system tests and gives the pre-Part 8
feature folders an executable Gherkin entry point, as Part 8 requires.
"""

import pytest
from pytest_bdd import given, scenario, then, when

from eventhub.admin import change_rate
from eventhub.catalog import list_events
from eventhub.errors import InvalidQuantity, SoldOut
from eventhub.identity import authenticate, register
from eventhub.inventory import take_tickets
from eventhub.pricing import compute_quote
from eventhub.purchase import parse_quantity

from .conftest import add_account


@pytest.fixture
def case():
    return {}


@pytest.mark.req("admin-007")
@scenario(
    "../features/admin/scenarios/admin_core.feature",
    "An unsupported administrator rate is rejected",
)
def test_admin_scenario():
    pass


@pytest.mark.req("audit-004")
@scenario(
    "../features/audit/scenarios/audit_core.feature",
    "An administrator rate change is audited",
)
def test_audit_scenario():
    pass


@pytest.mark.req("catalog-007")
@scenario(
    "../features/catalog/scenarios/catalog_core.feature",
    "A search without matches shows all events",
)
def test_catalog_scenario():
    pass


@pytest.mark.req("identity-005")
@scenario(
    "../features/identity/scenarios/identity_core.feature",
    "A failed login does not reveal account existence",
)
def test_identity_scenario():
    pass


@pytest.mark.req("inventory-004")
@scenario(
    "../features/inventory/scenarios/inventory_core.feature",
    "Inventory is never reduced for an oversold request",
)
def test_inventory_scenario():
    pass


@pytest.mark.req("pricing-008")
@scenario(
    "../features/pricing/scenarios/pricing_core.feature",
    "A yen quote is rounded using integer minor units",
)
def test_pricing_scenario():
    pass


@pytest.mark.req("purchase-007")
@scenario(
    "../features/purchase/scenarios/purchase_core.feature",
    "Zero ticket quantity is rejected",
)
def test_purchase_scenario():
    pass


@pytest.mark.req("system-002")
@scenario(
    "../features/system/scenarios/system_core.feature",
    "Invalid incoming language is refused",
)
def test_system_scenario():
    pass


@given("an administrator account is available")
def administrator_available(case, connection):
    case["account_id"] = add_account(
        connection, "review-admin@example.org", "administrator"
    )


@when("the administrator tries to set a negative exchange rate")
def invalid_admin_rate(case, connection):
    try:
        change_rate(connection, case["account_id"], "EUR", "-2")
    except ValueError as exc:
        case["error"] = exc


@then("the current exchange rate is not changed")
def unchanged_rate(case, connection):
    assert isinstance(case.get("error"), ValueError)
    assert (
        connection.execute(
            "SELECT units_per_usd FROM rates WHERE currency='EUR'"
        ).fetchone()[0]
        == "0.92"
    )


@when("the administrator changes the EUR exchange rate")
def set_admin_rate(case, connection):
    change_rate(connection, case["account_id"], "EUR", "0.98")


@then("an audit record contains the rate change")
def rate_was_audited(connection):
    row = connection.execute(
        "SELECT kind,detail FROM audit ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert row["kind"] == "rate_change" and "0.92 -> 0.98" in row["detail"]


@given("the event catalog contains seeded events")
def seeded_catalog(connection):
    assert connection.execute("SELECT COUNT(*) FROM events").fetchone()[0] >= 4


@when("a search term matches no event")
def no_match_search(case, connection):
    case["events"], case["unmatched"] = list_events(connection, "missing-band-98765")


@then("the search reports no matches and offers the full list")
def full_list_fallback(case, connection):
    assert case["unmatched"] is True
    assert (
        len(case["events"])
        == connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    )


@given("a registered buyer account exists")
def buyer_registered(connection):
    register(
        connection, "Test Buyer", "scenario-buyer@example.com", "a-good-password-123"
    )


@when("a wrong password and an unknown email are submitted")
def bad_logins(case, connection):
    errors = []
    for email, password in (
        ("scenario-buyer@example.com", "wrong-password"),
        ("not-here@example.org", "wrong-password"),
    ):
        try:
            authenticate(connection, email, password)
        except Exception as exc:
            errors.append(str(exc))
    case["errors"] = errors


@then("both attempts return the same invalid credentials error")
def no_user_enumeration(case):
    assert case["errors"] == ["Invalid credentials", "Invalid credentials"]


@given("only one event ticket remains")
def one_ticket(connection):
    connection.execute("UPDATE events SET available=1 WHERE id=1")


@when("a buyer tries to reserve two tickets")
def oversell_attempt(case, connection):
    try:
        take_tickets(connection, 1, 2)
    except SoldOut as exc:
        case["error"] = exc


@then("the inventory rejects the request and retains one ticket")
def stock_remains(case, connection):
    assert isinstance(case.get("error"), SoldOut)
    assert (
        connection.execute("SELECT available FROM events WHERE id=1").fetchone()[0] == 1
    )


@given("a ticket costs 125 US cents")
def price_input(case):
    case["unit_cents"] = 125


@when("a three-ticket yen quote is computed")
def yen_quote(case):
    case["quote"] = compute_quote(case["unit_cents"], 3, False, "JPY", "150")


@then("the result is a whole number of yen without a floating-point amount")
def yen_is_integer(case):
    assert isinstance(case["quote"].total_minor, int)
    assert case["quote"].total_minor == 563


@given("a purchase quantity of zero was submitted")
def quantity_zero(case):
    case["quantity"] = "0"


@when("the purchase form quantity is validated")
def validate_quantity(case):
    try:
        parse_quantity(case["quantity"])
    except InvalidQuantity as exc:
        case["error"] = exc


@then("the purchase is rejected with a quantity error")
def invalid_quantity_error(case):
    assert isinstance(case.get("error"), InvalidQuantity)


@given("a reader has a valid form session")
def reader_session(case, app_factory):
    app, _ = app_factory(DEFAULT_LANGUAGE="en")
    case["client"] = app.test_client()
    case["client"].get("/")
    with case["client"].session_transaction() as session:
        case["token"] = session["_csrf"]


@when("the reader submits an unsupported language")
def reject_bad_language(case):
    case["response"] = case["client"].post(
        "/language", data={"language": "xx", "csrf_token": case["token"]}
    )


@then("the HTTP request is rejected without saving a language cookie")
def no_cookie_for_invalid_language(case):
    assert case["response"].status_code == 400
    assert "eventhub_lang=" not in case["response"].headers.get("Set-Cookie", "")

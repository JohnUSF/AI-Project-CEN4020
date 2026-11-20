"""Executable Part 8 feature scenarios, linked to the requirements beside them."""

import pytest
from pytest_bdd import given, scenario, then, when

from eventhub import i18n

FEATURE = "../features/localization/scenarios/spanish_interface.feature"


@pytest.fixture
def case():
    return {}


@pytest.mark.part8
@pytest.mark.req("localization-001", "localization-002", "localization-007")
@scenario(FEATURE, "Spanish text comes from a compiled message catalog")
def test_spanish_catalog_scenario():
    pass


@pytest.mark.part8
@pytest.mark.req("localization-003", "localization-004")
@scenario(FEATURE, "Explicit language selection takes precedence")
def test_reader_choice_scenario():
    pass


@pytest.mark.part8
@pytest.mark.req("localization-005")
@scenario(FEATURE, "Spanish formatting keeps yen as an integer without decimals")
def test_yen_format_scenario():
    pass


@pytest.mark.part8
@pytest.mark.req("localization-006")
@scenario(FEATURE, "Unknown translation keys fall back instead of disappearing")
def test_missing_catalog_key_scenario():
    pass


@pytest.mark.part8
@pytest.mark.req("localization-008")
@scenario(FEATURE, "Bad operator language is rejected")
def test_bad_default_scenario():
    pass


@given("the operator has configured Spanish as the default language")
def spanish_default(case, app_factory):
    app, _ = app_factory(DEFAULT_LANGUAGE="es")
    case["client"] = app.test_client()


@when("a reader visits the home page")
def visit_spanish_home(case):
    case["response"] = case["client"].get("/")


@then("the home page has a Spanish title and Spanish navigation")
def homepage_is_spanish(case):
    page = case["response"].get_data(as_text=True)
    assert 'lang="es"' in page
    assert i18n.catalog("es")["title.home"] in page
    assert i18n.catalog("es")["nav.register"] in page


@when("the reader explicitly switches to English")
def choose_english(case):
    client = case["client"]
    client.get("/")
    with client.session_transaction() as session:
        token = session["_csrf"]
    client.post("/language", data={"language": "en", "csrf_token": token})


@then("the site remains in English on the next page")
def following_page_is_english(case):
    response = case["client"].get("/login")
    assert response.headers["Content-Language"] == "en"


@given("an order total of 4500 minor yen units")
def yen_total(case):
    case["minor"] = 4500


@when("the amount is displayed using the Spanish locale")
def spanish_money(case):
    case["money"] = i18n.local_money(case["minor"], "JPY", "es")


@then("it is displayed without a fraction")
def no_fractional_yen(case):
    rendered = case["money"]
    assert "4500" in rendered.replace(".", "").replace(",", "").replace(" ", "")
    assert ".00" not in rendered and ",00" not in rendered


@given("the Spanish catalog is missing a translated message")
def missing_message(case, monkeypatch):
    class MissingSpanishEntry:
        def gettext(self, key):
            return key

    monkeypatch.setattr(
        i18n, "_gettext_for_language", lambda lang: MissingSpanishEntry()
    )
    case["unknown"] = "nav.register"


@when("that English message is displayed")
def lookup_missing(case):
    case["translated"] = i18n.translate(case["unknown"], "es")


@then("the reader sees English instead of a missing key")
def english_fallback(case):
    assert case["translated"] == i18n.catalog("en")[case["unknown"]]


@given("the operator configured an unsupported language")
def bad_default(case):
    case["default"] = "xx"


@when("the application starts")
def start_bad_config(case, app_factory):
    try:
        app_factory(DEFAULT_LANGUAGE=case["default"])
    except ValueError as exc:
        case["error"] = exc


@then("startup is rejected with a configuration error")
def rejected_bad_config(case):
    assert "Unsupported default language" in str(case.get("error", ""))

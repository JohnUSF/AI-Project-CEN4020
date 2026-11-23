"""Part 8: Flask-Babel catalog integration, Call 7 choices, and safe regression checks.

Every test references its owning requirement in features/localization/requirements.md.
The Selenium suite still checks the actual browser, including pricing and yen.
"""

import json
from pathlib import Path

import pytest
from babel.support import Translations
from flask import jsonify
from flask_babel import get_locale, gettext

from eventhub import i18n

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.part8
@pytest.mark.req("localization-001", "localization-007")
def test_flask_babel_message_catalogs_are_compiled_and_complete(app_factory):
    """Both compiled catalogs must contain the Part 7 interface keys."""
    en = i18n.catalog("en")
    es = i18n.catalog("es")
    assert set(en) == set(es)
    assert len(en) >= 190
    assert (ROOT / "translations/es_ES/LC_MESSAGES/messages.mo").is_file()
    assert (ROOT / "translations/en_US/LC_MESSAGES/messages.mo").is_file()
    for language, locale, strings in (
        ("en", "en_US", en),
        ("es", "es_ES", es),
    ):
        translations = Translations.load(
            str(ROOT / "translations"), locales=[locale], domain="messages"
        )
        assert translations.gettext("nav.register") == strings["nav.register"]
        assert i18n.translate("nav.register", language) == strings["nav.register"]


@pytest.mark.part8
@pytest.mark.req("localization-001", "localization-002", "localization-007")
def test_flask_babel_is_active_during_a_spanish_request(app_factory):
    app, _ = app_factory(DEFAULT_LANGUAGE="es")

    @app.get("/_part8_probe")
    def babel_probe():
        return jsonify(locale=str(get_locale()), translated=gettext("nav.register"))

    response = app.test_client().get("/_part8_probe")
    assert response.status_code == 200
    assert response.json == {
        "locale": "es_ES",
        "translated": i18n.catalog("es")["nav.register"],
    }


@pytest.mark.part8
@pytest.mark.req("localization-002")
def test_spanish_covers_home_and_login_using_compiled_catalogs(app_factory):
    app, _ = app_factory(DEFAULT_LANGUAGE="es")
    client = app.test_client()
    for route, title_key in (("/", "title.home"), ("/login", "title.login")):
        response = client.get(route)
        html = response.get_data(as_text=True)
        assert response.status_code == 200
        assert response.headers["Content-Language"] == "es"
        assert 'lang="es"' in html
        assert i18n.translate(title_key, "es") in html


@pytest.mark.part8
@pytest.mark.req("localization-003", "localization-004")
def test_explicit_choice_overrides_default_not_accept_language(app_factory):
    app, _ = app_factory(DEFAULT_LANGUAGE="en")
    client = app.test_client()
    response = client.get("/", headers={"Accept-Language": "es-ES,es;q=0.9"})
    assert response.headers["Content-Language"] == "en"
    with client.session_transaction() as saved:
        token = saved["_csrf"]
    response = client.post(
        "/language",
        data={"language": "es", "next": "/", "csrf_token": token},
    )
    assert response.status_code in (302, 303)
    for url in ("/", "/login"):
        assert client.get(url).headers["Content-Language"] == "es"


@pytest.mark.part8
@pytest.mark.req("localization-005")
def test_spanish_babel_money_and_date_keep_yen_without_decimals(app_factory):
    app, _ = app_factory(DEFAULT_LANGUAGE="es")

    @app.get("/_part8_money_probe")
    def formatted_probe():
        return jsonify(
            money=i18n.local_money(4500, "JPY", "es"),
            date=i18n.local_date("2026-11-21 18:30", "es"),
        )

    output = app.test_client().get("/_part8_money_probe").json
    normalized = output["money"].replace("\u00a0", " ").replace("\u202f", " ")
    assert "4500" in normalized.replace(".", "").replace(",", "").replace(" ", "")
    assert ",00" not in normalized and ".00" not in normalized
    assert "2026" in output["date"] and "nov" in output["date"].lower()


@pytest.mark.part8
@pytest.mark.req("localization-006")
def test_missing_spanish_message_falls_back_to_english(monkeypatch):
    class MissingTranslations:
        def gettext(self, key):
            return key

    monkeypatch.setattr(
        i18n, "_gettext_for_language", lambda language: MissingTranslations()
    )
    assert i18n.translate("nav.register", "es") == i18n.catalog("en")["nav.register"]


@pytest.mark.part8
@pytest.mark.req("localization-007")
def test_translations_do_not_modify_saved_prices_or_requirements():
    en = json.loads((ROOT / "locales/en.json").read_text(encoding="utf-8"))
    es = json.loads((ROOT / "locales/es.json").read_text(encoding="utf-8"))
    assert set(en) == set(es)
    assert i18n.local_money(4500, "JPY", "en") == "JPY 4,500"
    assert i18n.local_money(4500, "JPY", "es") != ""


@pytest.mark.part8
@pytest.mark.req("localization-008")
def test_unsupported_operator_language_is_rejected_before_requests(app_factory):
    with pytest.raises(ValueError, match="Unsupported default language"):
        app_factory(DEFAULT_LANGUAGE="unsupported")


@pytest.mark.part8
@pytest.mark.req("localization-009")
def test_translation_provenance_covers_every_message_key():
    source = json.loads(
        (ROOT / "docs/part8-translation-provenance.json").read_text(encoding="utf-8")
    )
    assert set(source["entries"]) == set(i18n.catalog("en"))
    for entry in source["entries"].values():
        for language in ("en", "es"):
            assert entry[language]["source"]
            assert entry[language]["review_status"]


@pytest.mark.part8
@pytest.mark.req("localization-010")
def test_language_cookie_has_csrf_httponly_and_samesite(app_factory):
    app, _ = app_factory(DEFAULT_LANGUAGE="en")
    client = app.test_client()
    client.get("/")
    with client.session_transaction() as saved:
        token = saved["_csrf"]
    assert client.post("/language", data={"language": "es"}).status_code == 400
    response = client.post("/language", data={"language": "es", "csrf_token": token})
    assert response.status_code in (302, 303)
    cookie = response.headers["Set-Cookie"]
    assert "eventhub_lang=es" in cookie
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie
    assert client.get("/login").headers["Content-Language"] == "es"


@pytest.mark.part8
@pytest.mark.req("localization-011", "localization-012")
def test_translation_placeholders_and_versioned_release_validation(tmp_path):
    import shutil
    from scripts.validate_translation_catalogs import validate_catalogs

    assert validate_catalogs(ROOT) == []
    root = tmp_path / "draft"
    for dirname in ("locales", "translations", "docs"):
        shutil.copytree(ROOT / dirname, root / dirname)
    edited_path = root / "locales" / "es.json"
    translated = json.loads(edited_path.read_text(encoding="utf-8"))
    key = "msg.rate_limited"
    assert "{seconds}" in i18n.catalog("en")[key]
    translated[key] = translated[key].replace("{seconds}", "{different_placeholder}")
    edited_path.write_text(json.dumps(translated, ensure_ascii=False), encoding="utf-8")
    assert any("Placeholders differ" in err for err in validate_catalogs(root))

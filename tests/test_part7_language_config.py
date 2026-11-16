"""Part 7: the interface language is a configuration choice, and Spanish covers every screen.

These tests use the real templates, session and role gates. They protect system-014 to
system-017 and keep the English wording unchanged.
"""

import ast
import json
import re
import time
from html.parser import HTMLParser
from pathlib import Path

import pytest

from eventhub import i18n
from eventhub.errors import (
    DuplicateConflict,
    EventHubError,
    NotFound,
    RateLimited,
    SoldOut,
)
from eventhub.purchase import place_order

from .conftest import ROOT, add_account

ENGLISH = i18n.catalog("en")
SPANISH = i18n.catalog("es")
VISIBLE_PREFIXES = (
    "title.",
    "nav.",
    "home.",
    "event.",
    "order.",
    "admin.",
    "msg.",
    "http.",
    "js.",
    "error.",
    "flash.",
)


def _csrf(client):
    client.get("/")
    with client.session_transaction() as s:
        return s["_csrf"]


def _sign_in(client, uid):
    with client.session_transaction() as s:
        s["uid"] = uid
        s["last_active"] = time.time()


def _english_leaks(page):
    """English catalog sentences that appear on a page that should be Spanish."""
    leaks = []
    for key, english in ENGLISH.items():
        if not key.startswith(VISIBLE_PREFIXES) or len(english) < 8:
            continue
        if english == SPANISH.get(key) or "{" in english:
            continue
        if english in page:
            leaks.append(key)
    return leaks


# ---------------------------------------------------------------- system-014
@pytest.mark.part7
@pytest.mark.req("system-014")
def test_setup_file_sets_the_default_language(app_factory, tmp_path):
    setup = json.loads((ROOT / "config" / "setup.json").read_text(encoding="utf-8"))
    assert setup["default_language"] == "en"
    setup["default_language"] = "es"
    path = tmp_path / "setup-es.json"
    path.write_text(json.dumps(setup), encoding="utf-8")
    app, _ = app_factory(SETUP_PATH=str(path))
    page = app.test_client().get("/")
    assert 'lang="es"' in page.get_data(as_text=True)
    assert page.headers["Content-Language"] == "es"


@pytest.mark.part7
@pytest.mark.req("system-014")
def test_environment_variable_overrides_the_setup_file(app_factory, monkeypatch):
    monkeypatch.setenv("EVENTHUB_LANGUAGE", "es")
    app, _ = app_factory()
    assert 'lang="es"' in app.test_client().get("/").get_data(as_text=True)


@pytest.mark.part7
@pytest.mark.req("system-014")
def test_english_is_the_default_when_nothing_is_configured(app_factory):
    app, _ = app_factory()
    assert 'lang="en"' in app.test_client().get("/").get_data(as_text=True)


@pytest.mark.part7
@pytest.mark.req("system-014")
@pytest.mark.parametrize("bad", ["fr", "ES-mx", "klingon"])
def test_a_mistyped_default_language_stops_start_up(app_factory, bad):
    with pytest.raises(ValueError, match="Unsupported default language"):
        app_factory(DEFAULT_LANGUAGE=bad)


# ---------------------------------------------------------------- system-015
@pytest.mark.part7
@pytest.mark.req("system-015")
@pytest.mark.parametrize("default,choice", [("es", "en"), ("en", "es")])
def test_the_readers_choice_beats_the_configured_default(app_factory, default, choice):
    app, _ = app_factory(DEFAULT_LANGUAGE=default)
    c = app.test_client()
    assert f'lang="{default}"' in c.get("/").get_data(as_text=True)
    c.post("/language", data={"csrf_token": _csrf(c), "language": choice, "next": "/"})
    for path in ("/", "/login", "/events/1"):
        assert f'lang="{choice}"' in c.get(path).get_data(as_text=True)


# ---------------------------------------------------------------- system-016
@pytest.fixture
def spanish_pages(app_factory):
    """Every kind of screen, rendered in Spanish by a signed-in buyer and an administrator."""
    app, db_path = app_factory(DEFAULT_LANGUAGE="es", DISCOUNT_PERCENT="10")
    from eventhub.db import connect

    with connect(db_path) as cn:
        buyer = add_account(cn, "part7-buyer@usf.edu")
        admin = add_account(cn, "part7-admin@example.org", "administrator")
        order = place_order(
            cn,
            account_id=buyer,
            event_id=1,
            quantity=1,
            currency="JPY",
            discount_percent="10",
        )
        cn.commit()
        order_id = order.order_id
    pages = {}
    anon = app.test_client()
    for name, path in {
        "home": "/",
        "event": "/events/1",
        "login": "/login",
        "register": "/register",
        "missing page (404)": "/this-page-does-not-exist",
    }.items():
        pages[name] = anon.get(path)
    buyer_client = app.test_client()
    _sign_in(buyer_client, buyer)
    for name, path in {
        "home signed in": "/",
        "event signed in": "/events/1",
        "checkout": "/checkout/1",
        "orders": "/orders",
        "order detail": f"/orders/{order_id}",
        "admin forbidden (403)": "/admin",
    }.items():
        pages[name] = buyer_client.get(path)
    admin_client = app.test_client()
    _sign_in(admin_client, admin)
    pages["admin"] = admin_client.get("/admin")
    return pages


@pytest.mark.part7
@pytest.mark.req("system-016")
def test_no_english_sentence_is_left_on_any_spanish_screen(spanish_pages):
    problems = {}
    for name, response in spanish_pages.items():
        found = _english_leaks(response.get_data(as_text=True))
        if found:
            problems[name] = found
    assert problems == {}


@pytest.mark.part7
@pytest.mark.req("system-016")
def test_spanish_page_titles_and_accessible_labels(spanish_pages):
    def title(name):
        return re.search(
            r"<title>(.*?)</title>", spanish_pages[name].get_data(as_text=True)
        ).group(1)

    assert title("home") == "Descubrir eventos · EventHub"
    assert title("login") == "Iniciar sesión · EventHub"
    assert title("register") == "Crear cuenta en EventHub · EventHub"
    assert title("orders") == "Mis entradas · EventHub"
    assert title("checkout") == "Pago · EventHub"
    assert title("missing page (404)") == "No se puede continuar · EventHub"
    home = spanish_pages["home"].get_data(as_text=True)
    assert 'aria-label="Navegación principal"' in home
    assert 'aria-label="Ver el evento de Campus Jazz Collective"' in home
    assert "Buscar artistas o lugares</label>" in home


@pytest.mark.part7
@pytest.mark.req("system-016")
def test_spanish_error_pages_for_missing_and_forbidden(spanish_pages):
    assert spanish_pages["missing page (404)"].status_code == 404
    assert "No se encontró la página solicitada" in spanish_pages[
        "missing page (404)"
    ].get_data(as_text=True)
    assert spanish_pages["admin forbidden (403)"].status_code == 403
    assert "No tienes permiso" in spanish_pages["admin forbidden (403)"].get_data(
        as_text=True
    )


@pytest.mark.part7
@pytest.mark.req("system-016")
def test_spanish_signed_in_hint_and_event_note_name_the_currency(spanish_pages):
    home = spanish_pages["home signed in"].get_data(as_text=True)
    assert "<strong>una entrada en USD</strong>, tu moneda preferida" in home
    assert "Precio mostrado en USD, tu moneda preferida." in spanish_pages[
        "event signed in"
    ].get_data(as_text=True)


@pytest.mark.part7
@pytest.mark.req("system-016")
def test_spanish_order_detail_keeps_the_yen_amount_without_decimals(spanish_pages):
    page = spanish_pages["order detail"].get_data(as_text=True)
    assert "Confirmación del pedido" in page
    assert "de descuento" in page and "% off" not in page
    assert re.search(
        r"[\d.,]+\s?¥|¥\s?[\d.,]+|JPY", page
    )  # yen shown with its own symbol
    assert not re.search(r"¥\s?\d+[.,]\d{2}\b", page)  # and never with two decimals


@pytest.mark.part7
@pytest.mark.req("system-016")
def test_spanish_validation_errors_reach_the_reader_in_spanish(app_factory):
    app, _ = app_factory(DEFAULT_LANGUAGE="es")
    c = app.test_client()
    csrf = _csrf(c)
    bad_login = c.post(
        "/login",
        data={
            "csrf_token": csrf,
            "email": "no@example.org",
            "password": "wrong-password-1",
        },
    )
    text = bad_login.get_data(as_text=True)
    assert "Credenciales no válidas" in text or "La cuenta no existe" in text
    assert "Invalid credentials" not in text
    short = c.post(
        "/register",
        data={
            "csrf_token": csrf,
            "name": "Ana",
            "email": "ana@example.org",
            "password": "short",
        },
    )
    assert "La contraseña debe tener entre 10 y 256 caracteres" in short.get_data(
        as_text=True
    )
    assert "Password must be" not in short.get_data(as_text=True)
    stale = c.post("/language", data={"csrf_token": "wrong", "language": "es"})
    assert "Token de seguridad no válido o ausente" in stale.get_data(as_text=True)


@pytest.mark.part7
@pytest.mark.req("system-016")
def test_the_price_preview_service_answers_in_the_readers_language(app_factory):
    app, db_path = app_factory(DEFAULT_LANGUAGE="es")
    from eventhub.db import connect

    with connect(db_path) as cn:
        uid = add_account(cn, "part7-preview@example.org")
        cn.commit()
    c = app.test_client()
    _sign_in(c, uid)
    bad = c.get("/quote/1?quantity=0&currency=USD")
    assert bad.status_code == 400
    assert "Cantidad no válida" in bad.get_json()["error"]
    good = c.get("/quote/1?quantity=1&currency=JPY")
    assert good.status_code == 200
    assert good.get_json()["localized_total"]  # the script shows this value in Spanish


@pytest.mark.part7
@pytest.mark.req("system-016")
def test_error_text_translates_messages_codes_and_the_wait_time():
    es = lambda exc: i18n.error_text(exc, "es")  # noqa: E731
    assert es(SoldOut("Sold out: not enough tickets remain")).startswith("Agotado")
    assert (
        es(NotFound()) == "evento no encontrado"
    )  # default text taken from the error's code
    assert "7 segundos" in es(RateLimited(7))
    assert (
        es(EventHubError("A brand-new message nobody translated yet"))
        == "A brand-new message nobody translated yet"
    )  # English fallback
    for exc in (
        SoldOut("Sold out: not enough tickets remain"),
        RateLimited(7),
        NotFound(),
    ):
        assert i18n.error_text(exc, "en") == str(exc)  # English never changes
    assert "ya se usó" in es(
        DuplicateConflict(
            "This purchase token was already used for a different purchase. Please reload the page."
        )
    )
    assert i18n.http_text(500, "Something odd", "es") == SPANISH["http.default"]
    assert i18n.http_text(404, "any", "en") == "any"


# ---------------------------------------------------------------- system-017
class _TextFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        self.skip += tag in ("script", "style")
        for name, value in attrs:
            if (
                name in ("aria-label", "placeholder", "title", "alt")
                and value
                and "{{" not in value
            ):
                if re.search(r"[A-Za-z]{3,}", value):
                    self.found.append(f"{name}={value!r}")

    def handle_endtag(self, tag):
        self.skip -= tag in ("script", "style")

    def handle_data(self, data):
        if self.skip:
            return
        text = re.sub(r"\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\}", "", data, flags=re.S).strip()
        if re.search(r"[A-Za-z]{3,}", text):
            self.found.append(repr(text[:60]))


#: Names that are the same in every language (the product name, the language picker labels).
LANGUAGE_NEUTRAL = {
    "'EventHub'",
    "'EventHub · EventHub'",
    "'/ USF'",
    "'English'",
    "'Español'",
}


@pytest.mark.part7
@pytest.mark.req("system-017")
def test_page_templates_hold_no_reader_facing_text():
    leftovers = {}
    for path in sorted((ROOT / "templates").glob("*.html")):
        finder = _TextFinder()
        finder.feed(path.read_text(encoding="utf-8"))
        extra = [
            t
            for t in finder.found
            if t not in LANGUAGE_NEUTRAL and t != "attr aria-label='EventHub'"
        ]
        extra = [t for t in extra if "EventHub" not in t or len(t) > 12]
        if extra:
            leftovers[path.name] = extra
    assert leftovers == {}, "text found in templates instead of locales/*.json"


@pytest.mark.part7
@pytest.mark.req("system-017")
def test_the_script_holds_no_reader_facing_text():
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    for word in (
        "Estimated total",
        "Total estimado",
        "Working...",
        "Procesando",
        "Price not available",
        "Precio no disponible",
    ):
        assert word not in script


@pytest.mark.part7
@pytest.mark.req("system-017")
def test_language_files_match_and_every_key_is_used_once_defined():
    assert set(ENGLISH) == set(SPANISH)
    placeholders = lambda text: sorted(re.findall(r"\{(\w+)\}", text))  # noqa: E731
    assert [
        k for k in ENGLISH if placeholders(ENGLISH[k]) != placeholders(SPANISH[k])
    ] == []
    used = set()
    for path in [*ROOT.glob("templates/*.html"), *ROOT.glob("eventhub/*.py")]:
        text = path.read_text(encoding="utf-8")
        used |= set(re.findall(r"""\bt\(\s*['"]([\w.\-]+)['"]""", text))
        used |= set(re.findall(r"""translate\(\s*['"]([\w.\-]+)['"]""", text))
    dynamic = {
        k for k in ENGLISH if k.startswith(("msg.", "http."))
    }  # looked up by message text
    assert used - set(ENGLISH) == set()
    assert set(ENGLISH) - used - dynamic == set()


def _raised_messages():
    """Every literal message that pricing, purchase, identity, catalog, inventory or admin raise."""
    found = {}
    for name in (
        "admin",
        "catalog",
        "identity",
        "inventory",
        "pricing",
        "purchase",
        "web",
    ):
        path = ROOT / "eventhub" / f"{name}.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        constants = {
            n.targets[0].id: n.value.value
            for n in tree.body
            if isinstance(n, ast.Assign)
            and isinstance(n.value, ast.Constant)
            and isinstance(n.value.value, str)
        }
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Raise)
                and isinstance(node.exc, ast.Call)
                and node.exc.args
            ):
                continue
            func = node.exc.func
            kind = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
            if not (
                kind.endswith("Error")
                or kind
                in {
                    "NotFound",
                    "SoldOut",
                    "PurchaseLimit",
                    "InvalidQuantity",
                    "UnsupportedCurrency",
                    "ConfigurationPending",
                    "InvalidRequestToken",
                    "DuplicateConflict",
                    "Forbidden",
                }
            ):
                continue
            arg = node.exc.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                found[arg.value] = f"{name}.py:{node.lineno}"
            elif isinstance(arg, ast.Name) and arg.id in constants:
                found[constants[arg.id]] = f"{name}.py:{node.lineno}"
    return found


@pytest.mark.part7
@pytest.mark.req("system-016", "system-017")
def test_every_message_the_code_can_raise_has_a_spanish_translation():
    known = {
        ENGLISH[k]
        for k in ENGLISH
        if k.startswith("msg.") and not k.startswith("msg.code.")
    }
    missing = {
        text: where for text, where in _raised_messages().items() if text not in known
    }
    assert missing == {}, "add these messages to locales/en.json and locales/es.json"
    for text in known:
        key = next(k for k, v in ENGLISH.items() if v == text and k.startswith("msg."))
        assert (
            SPANISH[key]
            and SPANISH[key] != text
            or key in {"msg.rate_limited"}
            and SPANISH[key]
        )


# ----------------------------------------------- English must not change
@pytest.mark.part7
@pytest.mark.req("system-016")
def test_english_wording_is_exactly_what_it_was_before_part_7(app_factory):
    app, db_path = app_factory(DISCOUNT_PERCENT="10")
    from eventhub.db import connect

    with connect(db_path) as cn:
        uid = add_account(cn, "part7-english@example.org")
        cn.commit()
    anon = app.test_client()
    home = anon.get("/").get_data(as_text=True)
    assert (
        "Click a card to view details. Sign in to use double-click quick-buy. This demo does not charge real money."
        in home
    )
    assert "<title>Discover events · EventHub</title>" in home
    assert 'aria-label="View Campus Jazz Collective event"' in home
    event = anon.get("/events/1").get_data(as_text=True)
    assert (
        "Price shown in USD. Pricing and student discounts are finalized at checkout based on configured rules."
        in event
    )
    assert "USD 18.00" in event
    signed = app.test_client()
    _sign_in(signed, uid)
    assert (
        "Double-click a card to instantly buy <strong>one ticket in USD</strong>, your preferred currency (change it in the header)."
        in signed.get("/").get_data(as_text=True)
    )
    assert "Unable to continue" in anon.get("/nope").get_data(as_text=True)
    quote = signed.get("/quote/1?quantity=1&currency=JPY").get_json()
    assert (
        quote["localized_total"] == quote["total"]
    )  # script shows the same text as before

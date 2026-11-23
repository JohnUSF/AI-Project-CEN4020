"""Display-only translations and formatting. Never changes an amount charged.

Translations live in locales/*.json so adding a language does not affect pricing.
Money uses Babel's currency metadata; JPY is displayed without a fraction.
"""

import json
from datetime import datetime
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from babel.dates import format_datetime
from babel.numbers import format_currency
from babel.support import Translations
from flask import g, has_request_context
from flask_babel import (
    format_currency as flask_format_currency,
    format_datetime as flask_format_datetime,
    gettext as flask_gettext,
)

from .pricing import CURRENCY_DIGITS, display_amount

ROOT = Path(__file__).resolve().parent.parent
SUPPORTED_LANGUAGES = {"en": "English", "es": "Español"}
LANGUAGE_LOCALES = {"en": "en_US", "es": "es_ES"}


def normalize_language(value):
    value = str(value or "").strip().lower()
    return value if value in SUPPORTED_LANGUAGES else "en"


def validate_language_setting(value):
    """Check a configured default language; a typo must stop start-up, not silently show English."""
    value = str(value or "").strip().lower()
    if value not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported default language {value!r}; choose one of: "
            + ", ".join(sorted(SUPPORTED_LANGUAGES))
        )
    return value


def default_language_from_setup(setup_path):
    """The `default_language` entry of config/setup.json, or English when it has none."""
    try:
        data = json.loads(Path(setup_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "en"
    return validate_language_setting(data.get("default_language", "en"))


def pick_language(cookie_value, default="en"):
    """The reader's saved choice wins; otherwise the configured default applies."""
    value = str(cookie_value or "").strip().lower()
    return value if value in SUPPORTED_LANGUAGES else default


@lru_cache(maxsize=4)
def catalog(language):
    language = normalize_language(language)
    return json.loads(
        (ROOT / "locales" / f"{language}.json").read_text(encoding="utf-8")
    )


@lru_cache(maxsize=4)
def _gettext_for_language(language):
    """Load version-controlled compiled message catalogs for non-request callers."""
    return Translations.load(
        str(ROOT / "translations"),
        locales=[LANGUAGE_LOCALES[language]],
        domain="messages",
    )


def translate(key, language="en", **variables):
    """Look up UI text through gettext while preserving the Part 7 key-based API.

    Explicit language arguments still work in plain Python (unit tests, scripts),
    where a Flask request/locale selector does not exist. Missing entries fall
    back to the original English catalog, never a blank string.
    """
    language = normalize_language(language)
    if has_request_context() and g.get("language") == language:
        template = flask_gettext(key)
    else:
        template = _gettext_for_language(language).gettext(key)
    if template == key:
        template = catalog("en").get(key, key)
    return template.format(**variables)


@lru_cache(maxsize=1)
def _english_message_keys():
    """English text -> catalog key, built from en.json so no sentence is written twice."""
    return {
        text: key
        for key, text in catalog("en").items()
        if key.startswith("msg.") and not key.startswith("msg.code.")
    }


def error_text(exc, language="en"):
    """Reader-facing wording of an error. The error itself (and the audit trail) stays English."""
    message = str(exc)
    if normalize_language(language) == "en":
        return message
    retry_after = getattr(exc, "retry_after", None)
    if retry_after is not None:
        return translate("msg.rate_limited", language, seconds=retry_after)
    key = _english_message_keys().get(message)
    code = getattr(exc, "code", None)
    if key is None and code and message == code.replace("_", " "):
        key = f"msg.code.{code}"
    return translate(key, language) if key else message


def http_text(status, description, language="en"):
    """Reader-facing wording for a Flask/Werkzeug HTTP error page."""
    if normalize_language(language) == "en":
        return description
    if status in (403, 404):
        return translate(f"http.{status}", language)
    key = _english_message_keys().get(str(description))
    return translate(key, language) if key else translate("http.default", language)


def local_money(minor_units, currency, language="en"):
    """Only a presentational adapter: input is an *integer* charge in minor units.

    This function must never be used to recalculate the amount stored in orders.
    """
    language = normalize_language(language)
    if type(minor_units) is not int or currency not in CURRENCY_DIGITS:
        raise ValueError(
            "Money formatting needs integer minor units and a supported currency"
        )
    if language == "en":
        # Keep previously tested English receipts stable (for instance JPY 4,500).
        # The legacy English formatter already respects zero-decimal currencies.
        return display_amount(minor_units, currency)
    value = Decimal(minor_units).scaleb(-CURRENCY_DIGITS[currency])
    if has_request_context() and g.get("language") == language:
        return flask_format_currency(value, currency)
    return format_currency(value, currency, locale=LANGUAGE_LOCALES[language])


def local_date(value, language="en"):
    """Format venue-local text without changing a timestamp or choosing a timezone.

    English retains the previous ISO-like display, while Spanish uses Babel.
    This keeps template code independent of language-specific decisions.
    """
    language = normalize_language(language)
    if language == "en":
        return str(value)
    try:
        dt = datetime.strptime(str(value), "%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return str(value)
    if has_request_context() and g.get("language") == language:
        return flask_format_datetime(dt, format="medium")
    return format_datetime(dt, format="medium", locale=LANGUAGE_LOCALES[language])

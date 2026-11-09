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

from .pricing import CURRENCY_DIGITS, display_amount

ROOT = Path(__file__).resolve().parent.parent
SUPPORTED_LANGUAGES = {"en": "English", "es": "Español"}
LANGUAGE_LOCALES = {"en": "en_US", "es": "es_ES"}


def normalize_language(value):
    value = str(value or "").strip().lower()
    return value if value in SUPPORTED_LANGUAGES else "en"


@lru_cache(maxsize=4)
def catalog(language):
    language = normalize_language(language)
    return json.loads(
        (ROOT / "locales" / f"{language}.json").read_text(encoding="utf-8")
    )


def translate(key, language="en", **variables):
    language = normalize_language(language)
    # For any unfinished translation use clear English instead of a blank string.
    template = catalog(language).get(key, catalog("en").get(key, key))
    return template.format(**variables)


def local_money(minor_units, currency, language="en"):
    """Only a presentational adapter: input is an *integer* charge in minor units.

    This function must never be used to recalculate the amount stored in orders.
    """
    if type(minor_units) is not int or currency not in CURRENCY_DIGITS:
        raise ValueError(
            "Money formatting needs integer minor units and a supported currency"
        )
    if normalize_language(language) == "en":
        # Keep previously tested English receipts stable (for instance JPY 4,500).
        # The legacy English formatter already respects zero-decimal currencies.
        return display_amount(minor_units, currency)
    value = Decimal(minor_units).scaleb(-CURRENCY_DIGITS[currency])
    return format_currency(
        value, currency, locale=LANGUAGE_LOCALES[normalize_language(language)]
    )


def local_date(value, language="en"):
    """Display a naive event timestamp as venue-local time; no invented timezone."""
    try:
        dt = datetime.strptime(str(value), "%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return str(value)
    return format_datetime(
        dt, format="medium", locale=LANGUAGE_LOCALES[normalize_language(language)]
    )

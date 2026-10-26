"""The ONLY module that calculates charge amounts and exchange conversions.

Money at the boundaries and in the database is in integer minor units.
Exchange rates are exact decimal strings. No binary floating point is used.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re

from .eligibility import normalize_email, eligible_for_usf_discount

from .errors import ConfigurationPending, InvalidQuantity, UnsupportedCurrency

CURRENCY_DIGITS = {"USD": 2, "EUR": 2, "GBP": 2, "JPY": 0}
RATE_PATTERN = re.compile(r"^(?:0|[1-9]\d{0,5})(?:\.\d{1,8})?$")


def validate_rate(rate):
    text = str(rate).strip()
    if not RATE_PATTERN.fullmatch(text):
        raise ValueError(
            "Rate must be a positive decimal with at most 8 fractional digits"
        )
    value = Decimal(text)
    if value <= 0:
        raise ValueError("Rate must be positive")
    return text


def display_amount(minor_units, currency):
    digits = CURRENCY_DIGITS[currency]
    sign = "-" if minor_units < 0 else ""
    absolute = abs(minor_units)
    if digits == 0:
        return f"{sign}{currency} {absolute:,}"
    return f"{sign}{currency} {absolute // (10**digits):,}.{absolute % (10**digits):0{digits}d}"


@dataclass(frozen=True)
class Quote:
    currency: str
    rate: str
    base_usd_minor: int
    quantity: int
    discount_percent: str
    total_minor: int

    @property
    def displayed_total(self):
        return display_amount(self.total_minor, self.currency)


def compute_quote(
    base_usd_minor,
    quantity,
    eligible,
    currency,
    rate,
    discount_percent=None,
    *,
    conversion_order="discount_then_convert",
):
    """Single central price function used by event views and purchase transactions.

    Discount, conversion and rounding order are provisional and configurable,
    pending the exact customer-email decisions from Call 4.
    """
    if type(base_usd_minor) is not int or base_usd_minor < 0:
        raise ValueError("Invalid price")
    if type(quantity) is not int or quantity < 1:
        raise InvalidQuantity("Quantity must be a positive whole number")
    if currency not in CURRENCY_DIGITS:
        raise UnsupportedCurrency("Unsupported currency")
    rate_text = validate_rate(rate)
    if eligible and discount_percent is None:
        raise ConfigurationPending(
            "USF discount percentage is still pending; ask an administrator"
        )
    try:
        discount = Decimal(str(discount_percent)) if eligible else Decimal(0)
    except InvalidOperation as exc:
        raise ConfigurationPending("Discount configuration is invalid") from exc
    if not discount.is_finite() or not (Decimal(0) <= discount <= Decimal(100)):
        raise ConfigurationPending("Discount must be between 0 and 100 percent")
    if conversion_order != "discount_then_convert":
        raise ConfigurationPending(
            "Discount and conversion order has not been approved"
        )
    factor = Decimal(10) ** CURRENCY_DIGITS[currency]
    dollars = Decimal(base_usd_minor) * Decimal(quantity) / Decimal(100)
    charged = (dollars * (Decimal(100) - discount) / Decimal(100)) * Decimal(rate_text)
    final_minor = int((charged * factor).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    return Quote(
        currency, rate_text, base_usd_minor, quantity, str(discount), final_minor
    )

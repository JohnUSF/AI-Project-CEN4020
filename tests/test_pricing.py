from decimal import Decimal
import pytest
from eventhub.pricing import (compute_quote, eligible_for_usf_discount, normalize_email,
                              validate_rate, display_amount)
from eventhub.errors import ConfigurationPending, InvalidQuantity, UnsupportedCurrency


def test_normalize_usf_email_uppercase():
    assert normalize_email('  STUDENT@USF.EDU  ') == 'student@usf.edu'
    assert eligible_for_usf_discount(' STUDENT@USF.EDU ')
    assert eligible_for_usf_discount('name+party@usf.edu')
    assert not eligible_for_usf_discount('member@mail.usf.edu')  # Policy pending
    assert not eligible_for_usf_discount('student@usf.edu.evil.example')


def test_integer_money_usd():
    q = compute_quote(1999, 3, False, 'USD', '1')
    assert q.total_minor == 5997
    assert q.displayed_total == 'USD 59.97'
    assert isinstance(q.total_minor, int)


def test_jpy_rounds_to_zero_decimal_places():
    assert compute_quote(125, 1, False, 'JPY', '150').total_minor == 188
    assert display_amount(188, 'JPY') == 'JPY 188'


def test_eur_discount_single_aggregate_round():
    q = compute_quote(4999, 2, True, 'EUR', '0.92', '10')
    assert q.total_minor == 8278
    assert q.discount_percent == '10'


def test_rate_validation_and_no_floats():
    for bad in ['-1', '0', 'nan', 'inf', '1e2', '1.123456789', '1;DROP TABLE', '1000000']:
        with pytest.raises(ValueError):
            validate_rate(bad)
    assert validate_rate('0.92000000') == '0.92000000'


def test_missing_discount_fails_closed_for_eligible_student():
    with pytest.raises(ConfigurationPending):
        compute_quote(2500, 1, True, 'USD', '1')
    assert compute_quote(2500, 1, False, 'USD', '1').total_minor == 2500


def test_invalid_discount_and_conversion_order():
    for value in ['-1', '101', 'nan']:
        with pytest.raises(ConfigurationPending):
            compute_quote(1000, 1, True, 'USD', '1', value)
    with pytest.raises(ConfigurationPending):
        compute_quote(1000, 1, True, 'USD', '1', '10', conversion_order='unapproved')


def test_invalid_currency_quantity():
    with pytest.raises(UnsupportedCurrency):
        compute_quote(1000, 1, False, 'BTC', '1')
    with pytest.raises(InvalidQuantity):
        compute_quote(1000, 0, False, 'USD', '1')


@pytest.mark.parametrize('money,code,expected', [(150,'USD','USD 1.50'),(0,'GBP','GBP 0.00'),(1000,'JPY','JPY 1,000')])
def test_money_format(money,code,expected):
    assert display_amount(money,code) == expected

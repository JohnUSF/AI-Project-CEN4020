"""Standalone Call 4 regression tests for normalized discount eligibility."""

import pytest

from eventhub.eligibility import eligible_for_usf_discount, normalize_email


@pytest.mark.parametrize(
    "address, normalized, expected",
    [
        (" STUDENT@USF.EDU ", "student@usf.edu", True),
        ("NAME+ALIAS@USF.EDU", "name+alias@usf.edu", True),
        ("member@mail.usf.edu", "member@mail.usf.edu", False),
        ("student@usf.edu.evil.org", "student@usf.edu.evil.org", False),
        ("student@example.org", "student@example.org", False),
    ],
)
def test_email_normalization_and_provisional_domain_rule(address, normalized, expected):
    assert normalize_email(address) == normalized
    assert eligible_for_usf_discount(address) is expected


def test_empty_address_is_not_eligible():
    assert normalize_email(None) == ""
    assert not eligible_for_usf_discount(None)

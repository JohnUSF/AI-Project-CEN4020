"""Call 4: independently testable student-email domain classifier.

The email alias/subdomain decisions below are explicit provisional assumptions,
not customer-approved business rules. See docs/open-items.md Q17.
"""


def normalize_email(email):
    """Normalize email for both account lookup and discount eligibility."""
    return (email or "").strip().casefold()


def eligible_for_usf_discount(email):
    """True for the exact usf.edu domain; plus tags qualify by provisional policy.

    Example: NAME+ALIAS@USF.EDU qualifies; student@mail.usf.edu does not.
    """
    return normalize_email(email).partition("@")[2] == "usf.edu"

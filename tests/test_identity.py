"""Identity tests are run on environments with the Werkzeug dependency installed."""

import pytest

pytest.importorskip("werkzeug.security")
from eventhub.errors import EventHubError
from eventhub.identity import authenticate, promote_from_cli, register, user_by_id


@pytest.mark.req("identity-001", "identity-002", "identity-008", "identity-015")
def test_registration_stores_hash_and_buyer_only(connection):
    uid = register(
        connection, "Student One", "STUDENT@USF.EDU", "correct-horse-battery"
    )
    row = user_by_id(connection, uid)
    assert row["email"] == "student@usf.edu"
    assert row["role"] == "buyer"
    assert "correct-horse-battery" not in row["password_hash"]
    assert (
        authenticate(connection, "student@usf.edu", "correct-horse-battery")["id"]
        == uid
    )


@pytest.mark.req("identity-005")
def test_wrong_password_does_not_reveal_account(connection):
    register(connection, "Student One", "student@usf.edu", "correct-horse-battery")
    with pytest.raises(EventHubError, match="Invalid credentials"):
        authenticate(connection, "student@usf.edu", "wrong")
    with pytest.raises(EventHubError, match="Invalid credentials"):
        authenticate(connection, "missing@usf.edu", "wrong")


@pytest.mark.req("identity-001", "system-002")
def test_duplicate_email_and_short_password_rejected(connection):
    register(connection, "Student One", "student@usf.edu", "correct-horse-battery")
    with pytest.raises(EventHubError):
        register(connection, "Second Student", "STUDENT@USF.EDU", "some-other-password")
    with pytest.raises(EventHubError):
        register(connection, "Third Student", "third@usf.edu", "short")


@pytest.mark.req("identity-016")
def test_admin_only_promoted_via_server_method(connection):
    uid = register(
        connection, "Student One", "student@usf.edu", "correct-horse-battery"
    )
    assert user_by_id(connection, uid)["role"] == "buyer"
    promote_from_cli(connection, "student@usf.edu")
    assert user_by_id(connection, uid)["role"] == "administrator"

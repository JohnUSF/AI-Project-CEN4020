"""Account registration, credentials, user roles and session helpers."""

import re
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from .errors import EventHubError, UnsupportedCurrency
from .pricing import normalize_email, CURRENCY_DIGITS

# One '@', no spaces, and a dotted domain with no empty label (identity-017).
EMAIL_SHAPE = re.compile(r"^[^@\s]+@[^@\s.]+(?:\.[^@\s.]+)+$")
# Explicit, portable hash method. Werkzeug's default (scrypt) is missing from some
# Python builds, which broke the Mac test run in Part 4.
PASSWORD_HASH_METHOD = "pbkdf2:sha256:600000"


def register(conn, name, email, password, currency="USD"):
    name = (name or "").strip()
    email = normalize_email(email)
    if (
        not 1 <= len(name) <= 100
        or not (3 <= len(email) <= 254)
        or not EMAIL_SHAPE.fullmatch(email)
    ):
        raise EventHubError("Enter a valid name and email address")
    if currency not in CURRENCY_DIGITS:
        raise UnsupportedCurrency("Unsupported currency")
    if not isinstance(password, str) or len(password) < 10 or len(password) > 256:
        raise EventHubError("Password must be between 10 and 256 characters")
    try:
        cursor = conn.execute(
            "INSERT INTO accounts(name,email,password_hash,role,currency) VALUES (?,?,?,?,?)",
            (
                name,
                email,
                generate_password_hash(password, method=PASSWORD_HASH_METHOD),
                "buyer",
                currency,
            ),
        )
    except sqlite3.IntegrityError as exc:
        raise EventHubError("This email is already registered") from exc
    return cursor.lastrowid


def authenticate(conn, email, password):
    row = conn.execute(
        "SELECT * FROM accounts WHERE email=?", (normalize_email(email),)
    ).fetchone()
    if row is None or not check_password_hash(row["password_hash"], password or ""):
        raise EventHubError("Invalid credentials")
    return row


def user_by_id(conn, user_id):
    try:
        return conn.execute(
            "SELECT * FROM accounts WHERE id=?", (int(user_id),)
        ).fetchone()
    except (ValueError, TypeError):
        return None


def set_currency(conn, account_id, currency):
    if currency not in CURRENCY_DIGITS:
        raise EventHubError("Unsupported currency")
    conn.execute("UPDATE accounts SET currency=? WHERE id=?", (currency, account_id))


def promote_from_cli(conn, email):
    row = conn.execute(
        "SELECT id FROM accounts WHERE email=?", (normalize_email(email),)
    ).fetchone()
    if row is None:
        raise EventHubError("Account does not exist; register first")
    conn.execute("UPDATE accounts SET role='administrator' WHERE id=?", (row["id"],))

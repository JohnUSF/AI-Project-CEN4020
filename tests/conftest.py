import pytest
from eventhub.db import initialize, connect
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def database(tmp_path):
    path = tmp_path / "eventhub.sqlite3"
    initialize(path, ROOT / "config" / "setup.json")
    return path


@pytest.fixture
def connection(database):
    conn = connect(database)
    yield conn
    conn.close()


def add_account(c, email="buyer@example.com", role="buyer"):
    c.execute(
        "INSERT INTO accounts(name,email,password_hash,role) VALUES (?,?,?,?)",
        ("Sample Buyer", email, "demo-test-hash", role),
    )
    return c.execute("SELECT id FROM accounts WHERE email=?", (email,)).fetchone()[0]


@pytest.fixture
def app_factory(database):
    """Build a Flask app on the temporary database with chosen settings."""
    pytest.importorskip("flask")
    from eventhub.web import create_app

    def make(**settings):
        config = {
            "TESTING": True,
            "SECRET_KEY": "testing-123456789",
            "DATABASE": str(database),
        }
        config.update(settings)
        return create_app(config), database

    return make

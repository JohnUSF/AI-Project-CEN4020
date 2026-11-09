"""SQLite connection lifecycle, schema migration and deterministic seed helpers."""

import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'buyer'
    CHECK(role IN ('buyer','administrator')),
  currency TEXT NOT NULL DEFAULT 'USD', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY, artist TEXT NOT NULL, venue TEXT NOT NULL,
  starts_at TEXT NOT NULL, description TEXT NOT NULL,
  base_price_minor INTEGER NOT NULL CHECK(base_price_minor >= 0),
  available INTEGER NOT NULL CHECK(available >= 0)
);
CREATE TABLE IF NOT EXISTS rates (
  currency TEXT PRIMARY KEY, units_per_usd TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY, account_id INTEGER NOT NULL REFERENCES accounts(id),
  event_id INTEGER NOT NULL REFERENCES events(id),
  quantity INTEGER NOT NULL CHECK(quantity > 0), currency TEXT NOT NULL,
  rate TEXT NOT NULL, discount_percent TEXT NOT NULL, total_minor INTEGER NOT NULL,
  confirmation_code TEXT NOT NULL UNIQUE, checked_in_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  unit_usd_minor INTEGER, request_token TEXT
);
CREATE TABLE IF NOT EXISTS audit (
  id INTEGER PRIMARY KEY, kind TEXT NOT NULL, account_id INTEGER, event_id INTEGER,
  quantity INTEGER, currency TEXT, outcome TEXT NOT NULL,
  detail TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_events_artist ON events(artist);
CREATE INDEX IF NOT EXISTS idx_orders_account ON orders(account_id, created_at);
CREATE TABLE IF NOT EXISTS maintenance_alerts (
  id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL REFERENCES orders(id),
  category TEXT NOT NULL, description TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','acknowledged')),
  acknowledged_by INTEGER REFERENCES accounts(id),
  acknowledged_at TEXT, notified_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(order_id, category)
);
CREATE INDEX IF NOT EXISTS idx_alert_status ON maintenance_alerts(status, created_at);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit(created_at);
"""


def connect(db_path):
    conn = sqlite3.connect(
        str(db_path), timeout=15, isolation_level=None, check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=15000")
    return conn


def migrate(c):
    """Bring a Part 3/4 database up to the Part 5 schema. Safe to run every start.

    unit_usd_minor: the USD unit price at purchase time, so a confirmation can show it.
    request_token: the one-time purchase token that makes a repeated submit harmless.
    """
    columns = {row[1] for row in c.execute("PRAGMA table_info(orders)")}
    if "unit_usd_minor" not in columns:
        c.execute("ALTER TABLE orders ADD COLUMN unit_usd_minor INTEGER")
    if "request_token" not in columns:
        c.execute("ALTER TABLE orders ADD COLUMN request_token TEXT")
    c.execute("""CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_token
        ON orders(account_id, request_token) WHERE request_token IS NOT NULL""")


def initialize(db_path, setup_path):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as c:
        c.executescript(SCHEMA)
        migrate(c)
        setup = json.loads(Path(setup_path).read_text(encoding="utf-8"))
        for event in setup["events"]:
            c.execute(
                """INSERT OR IGNORE INTO events
                (id, artist, venue, starts_at, description, base_price_minor, available)
                VALUES (:id,:artist,:venue,:starts_at,:description,:base_price_minor,:available)""",
                event,
            )
        for code, rate in setup["rates"].items():
            c.execute(
                "INSERT OR IGNORE INTO rates(currency,units_per_usd) VALUES (?,?)",
                (code, str(rate)),
            )

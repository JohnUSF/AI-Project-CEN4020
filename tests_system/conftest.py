"""Fixtures for the Selenium system tests.

* `server` starts the real app (same create_app() as run.py) in a subprocess with a
  throw-away SQLite file, so the tests run against the final build, not a test double.
* `browser` is headless Chrome driven by Selenium.
* A small plugin records every test with its requirement IDs and takes a screenshot
  when one fails, so the run produces its own evidence (report/system_run/).
"""

import json
import os
import re
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
REPORT_DIR = Path(os.environ.get("EVENTHUB_REPORT_DIR", ROOT / "report" / "system_run"))
PASSWORD = "correct-horse-battery"


# --------------------------------------------------------------------------- servers
class Server:
    def __init__(self, tmp_path, **env):
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        self.port = s.getsockname()[1]
        s.close()
        self.url = f"http://127.0.0.1:{self.port}"
        self.db = tmp_path / "system.sqlite3"
        self.log = open(tmp_path / "server.log", "w")
        settings = {
            "EVENTHUB_DB": str(self.db),
            "EVENTHUB_SECRET_KEY": "system-test-secret-key-0123456789",
        }
        settings.update({k: str(v) for k, v in env.items()})
        self.proc = subprocess.Popen(
            [sys.executable, str(ROOT / "tests_system" / "serve.py"), str(self.port)],
            cwd=ROOT,
            env={**os.environ, **settings},
            stdout=self.log,
            stderr=subprocess.STDOUT,
        )
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                urllib.request.urlopen(self.url + "/", timeout=1).read()
                return
            except Exception:
                if self.proc.poll() is not None:
                    raise RuntimeError(
                        "EventHub server exited: "
                        + (tmp_path / "server.log").read_text()
                    )
                time.sleep(0.15)
        raise RuntimeError("EventHub server did not start")

    # -- white-box helpers: the tests seed and inspect the database directly
    def conn(self):
        c = sqlite3.connect(self.db, timeout=15)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA busy_timeout=15000")
        return c

    def sql(self, query, args=()):
        c = self.conn()
        try:
            return c.execute(query, args).fetchall()
        finally:
            c.close()

    def scalar(self, query, args=()):
        rows = self.sql(query, args)
        return rows[0][0] if rows else None

    def run(self, query, args=()):
        c = self.conn()
        try:
            c.execute(query, args)
            c.commit()
        finally:
            c.close()

    _counter = 0

    def new_user(self, email=None, currency="USD", role="buyer"):
        from eventhub.identity import register

        Server._counter += 1
        email = (
            email
            or f"user{Server._counter}-{int(time.time() * 1000) % 100000}@example.com"
        )
        c = self.conn()
        try:
            c.execute("BEGIN")
            uid = register(c, "System Tester", email, PASSWORD, currency)
            if role != "buyer":
                c.execute("UPDATE accounts SET role=? WHERE id=?", (role, uid))
            c.commit()
        finally:
            c.close()
        return {
            "id": uid,
            "email": email.strip().casefold(),
            "password": PASSWORD,
            "raw_email": email,
        }

    def new_event(self, available=50, price_minor=1500, artist=None):
        Server._counter += 1
        artist = artist or f"Scratch Act {Server._counter}"
        c = self.conn()
        try:
            cur = c.execute(
                """INSERT INTO events(artist,venue,starts_at,description,base_price_minor,available)
                VALUES(?,?,?,?,?,?)""",
                (
                    artist,
                    "Scratch Hall",
                    "2027-01-15 20:00",
                    "Seeded by a system test",
                    price_minor,
                    available,
                ),
            )
            c.commit()
            return cur.lastrowid
        finally:
            c.close()

    def stop(self):
        self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self.log.close()


def _server_fixture(**env):
    def fixture(tmp_path_factory):
        srv = Server(tmp_path_factory.mktemp("eventhub"), **env)
        yield srv
        srv.stop()

    return fixture


# Default build: discount configured for the demo, request limit at its provisional default.
server = pytest.fixture(scope="session")(
    _server_fixture(EVENTHUB_DISCOUNT_PERCENT="10")
)
# Same build with the customer's discount percentage still unconfigured (fails closed).
server_no_discount = pytest.fixture(scope="session")(_server_fixture())
server_capped = pytest.fixture(scope="session")(
    _server_fixture(EVENTHUB_DISCOUNT_PERCENT="10", EVENTHUB_PURCHASE_CAP="3")
)
server_fast_session = pytest.fixture(scope="session")(
    _server_fixture(EVENTHUB_DISCOUNT_PERCENT="10", EVENTHUB_SESSION_IDLE="3")
)


# --------------------------------------------------------------------------- browser
def _chrome_service():
    from selenium.webdriver.chrome.service import Service

    explicit = os.environ.get("CHROMEDRIVER")
    if explicit:
        return Service(explicit)
    try:  # offline machines: a driver bundled in a wheel
        from chromedriver_py import binary_path

        return Service(binary_path)
    except ImportError:
        return Service()  # normal machines: Selenium Manager picks the driver


def make_driver(width=1280, height=900):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    if os.environ.get("EVENTHUB_HEADED") != "1":
        options.add_argument("--headless=new")
    for arg in (
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        f"--window-size={width},{height}",
    ):
        options.add_argument(arg)
    if os.environ.get("CHROME_BIN"):
        options.binary_location = os.environ["CHROME_BIN"]
    driver = webdriver.Chrome(service=_chrome_service(), options=options)
    driver.implicitly_wait(0)
    return driver


@pytest.fixture(scope="session")
def _driver():
    driver = make_driver()
    yield driver
    driver.quit()


@pytest.fixture
def browser(_driver, request):
    _driver.delete_all_cookies()
    _driver.set_window_size(1280, 900)
    _driver.get("about:blank")
    request.node._driver = _driver
    return _driver


@pytest.fixture
def second_browser(request):
    driver = make_driver()
    yield driver
    driver.quit()

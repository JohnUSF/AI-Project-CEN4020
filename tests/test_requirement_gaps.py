"""Tests for requirements the Call 5 traceability check found had no test at all."""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULES = [
    "admin",
    "audit",
    "catalog",
    "db",
    "eligibility",
    "errors",
    "identity",
    "inventory",
    "pricing",
    "purchase",
    "ratelimit",
]


@pytest.mark.req("system-001")
def test_the_application_is_a_flask_application(app_factory):
    pytest.importorskip("flask")
    import flask

    app, _ = app_factory()
    assert isinstance(app, flask.Flask)


@pytest.mark.req("system-007")
@pytest.mark.parametrize("module", MODULES)
def test_each_component_imports_on_its_own_without_the_web_layer(module):
    """A fresh interpreter, so one module cannot lean on another having been imported first."""
    code = f"import sys, eventhub.{module}; assert 'flask' not in sys.modules or '{module}' == 'identity'"
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.req("system-008")
def test_the_shared_workflow_runs_the_tests_and_the_system_suite():
    workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text()
    assert "python -m pytest -q" in workflow and "pytest tests_system" in workflow
    assert "on: [push, pull_request]" in workflow


@pytest.mark.req("system-009")
def test_a_test_without_a_requirement_tag_is_refused_at_collection():
    probe = ROOT / "tests" / "test_zz_untagged_probe.py"
    probe.write_text("def test_untagged():\n    assert True\n")
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(probe),
                "-q",
                "-p",
                "no:cacheprovider",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
    finally:
        probe.unlink()
    assert result.returncode != 0
    assert "Tests without a @pytest.mark.req" in (result.stdout + result.stderr)


@pytest.mark.req("admin-001", "audit-005")
def test_the_admin_area_shows_rates_and_audit_log_to_administrators_only(app_factory):
    pytest.importorskip("flask")
    from .test_web import sign_in

    app, database = app_factory()
    admin, buyer, visitor = app.test_client(), app.test_client(), app.test_client()
    sign_in(admin, database, "boss@example.com")
    sign_in(buyer, database, "buyer@example.com")
    from eventhub.db import connect

    with connect(database) as c:
        c.execute(
            "UPDATE accounts SET role='administrator' WHERE email='boss@example.com'"
        )
    page = admin.get("/admin").get_data(as_text=True)
    assert "Exchange rates" in page and "Audit log" in page
    for client, expected in ((buyer, 403), (visitor, 302)):
        response = client.get("/admin")
        assert (
            response.status_code == expected
            and "Audit log" not in response.get_data(as_text=True)
        )
    audit_routes = [r.rule for r in app.url_map.iter_rules() if "audit" in r.rule]
    assert audit_routes == []  # the only way to read the log is inside /admin


@pytest.mark.req("pricing-009", "pricing-010")
def test_prices_follow_the_rate_stored_in_the_database_with_no_outside_provider(
    app_factory,
):
    pytest.importorskip("flask")
    from eventhub.db import connect

    from .test_web import sign_in

    app, database = app_factory()
    client = app.test_client()
    sign_in(client, database)
    assert client.get("/quote/1?currency=EUR").get_json()["total"] == "EUR 16.56"
    with connect(database) as c:
        c.execute("UPDATE rates SET units_per_usd='2' WHERE currency='EUR'")
    assert (
        client.get("/quote/1?currency=EUR").get_json()["total"] == "EUR 36.00"
    )  # no restart needed
    imported = {
        n.names[0].name.split(".")[0]
        for n in ast.walk(ast.parse((ROOT / "eventhub/pricing.py").read_text()))
        if isinstance(n, (ast.Import, ast.ImportFrom)) and n.names
    }
    assert not imported & {"urllib", "requests", "http", "socket", "httpx"}


@pytest.mark.req("purchase-012", "purchase-014")
def test_payment_is_simulated_and_no_payment_or_email_service_is_wired_in(connection):
    from eventhub import purchase
    from eventhub.errors import EventHubError

    from .conftest import add_account

    uid = add_account(connection)
    with pytest.raises(EventHubError, match="declined"):
        purchase.purchase(
            connection,
            account_id=uid,
            event_id=1,
            quantity=1,
            currency="USD",
            simulated_payment="declined",
        )
    forbidden = {
        "stripe",
        "paypal",
        "braintree",
        "smtplib",
        "sendgrid",
        "boto3",
        "twilio",
        "email",
    }
    for path in (ROOT / "eventhub").glob("*.py"):
        tree = ast.parse(path.read_text())
        names = {
            n.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for n in (a.name for a in node.names)
        }
        names |= {
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert not names & forbidden, (path.name, names & forbidden)
    requirements = (ROOT / "requirements.txt").read_text().lower()
    assert "stripe" not in requirements and "mail" not in requirements


@pytest.mark.req("system-001", "system-007")
def test_run_py_builds_the_same_application_the_system_tests_start(
    monkeypatch, tmp_path
):
    """The system tests start eventhub.web.create_app(); run.py must be nothing more than that."""
    pytest.importorskip("flask")
    import runpy

    monkeypatch.setenv("EVENTHUB_DB", str(tmp_path / "entry.sqlite3"))
    namespace = runpy.run_path(str(ROOT / "run.py"), run_name="not_main")
    from eventhub.web import create_app

    entry_rules = {r.rule for r in namespace["app"].url_map.iter_rules()}
    assert entry_rules == {
        r.rule
        for r in create_app(
            {"DATABASE": str(tmp_path / "other.sqlite3")}
        ).url_map.iter_rules()
    }
    assert namespace["app"].test_client().get("/").status_code == 200
    source = (ROOT / "run.py").read_text()
    assert "create_app()" in source and "debug=False" in source

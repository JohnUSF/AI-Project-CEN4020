"""Call 6 Flask tests: these use the real templates, session and role gates."""

import pytest

from eventhub.monitor import scan_orders
from eventhub.purchase import place_order

from .conftest import add_account


def _csrf(client):
    client.get("/")
    with client.session_transaction() as s:
        return s["_csrf"]


def _signed_in(client, uid):
    with client.session_transaction() as s:
        s["uid"] = uid
        s["last_active"] = __import__("time").time()


@pytest.mark.call6
@pytest.mark.req("system-010", "system-011", "pricing-019")
def test_spanish_switch_changes_text_date_and_receipt_not_amount(app_factory):
    app, path = app_factory(DISCOUNT_PERCENT="10")
    c = app.test_client()
    csrf = _csrf(c)
    response = c.post(
        "/language", data={"csrf_token": csrf, "language": "es", "next": "/"}
    )
    assert response.status_code == 302
    assert "eventhub_lang=es" in response.headers["Set-Cookie"]
    home = c.get("/").get_data(as_text=True)
    assert 'lang="es"' in home and "Explorar" in home
    assert "nov" in home.lower()
    assert 'lang="en"' in c.post(
        "/language",
        data={"csrf_token": csrf, "language": "en", "next": "/"},
        follow_redirects=True,
    ).get_data(as_text=True)


@pytest.mark.call6
@pytest.mark.req("audit-010", "audit-011")
def test_admin_alert_page_requires_role_and_can_acknowledge(app_factory):
    app, db_path = app_factory(DISCOUNT_PERCENT="10")
    from eventhub.db import connect

    with connect(db_path) as cn:
        buyer = add_account(cn, "call6-buyer@example.org")
        admin = add_account(cn, "call6-admin@example.org", "administrator")
        placed = place_order(
            cn,
            account_id=buyer,
            event_id=1,
            quantity=1,
            currency="USD",
            discount_percent="10",
        )
        cn.execute("UPDATE orders SET total_minor=5 WHERE id=?", (placed.order_id,))
        assert scan_orders(cn) == 1
        aid = cn.execute("SELECT id FROM maintenance_alerts").fetchone()[0]
    client = app.test_client()
    _signed_in(client, buyer)
    assert client.get("/admin").status_code == 403
    _signed_in(client, admin)
    assert "Order anomaly alerts" in client.get("/admin").get_data(as_text=True)
    csrf = _csrf(client)
    response = client.post(
        f"/admin/alerts/{aid}/acknowledge", data={"csrf_token": csrf}
    )
    assert response.status_code == 302
    with connect(db_path) as cn:
        assert (
            cn.execute(
                "SELECT status FROM maintenance_alerts WHERE id=?", (aid,)
            ).fetchone()[0]
            == "acknowledged"
        )

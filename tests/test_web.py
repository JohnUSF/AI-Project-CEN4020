"""HTTP integration tests run in CI after pip installs Flask/Werkzeug."""
import re
import pytest
pytest.importorskip('flask')
from eventhub.web import create_app, safe_next
from eventhub.db import connect
from eventhub.identity import register


@pytest.fixture
def app(database):
    return create_app({'TESTING': True, 'SECRET_KEY': 'testing-123456789',
                       'DATABASE': str(database), 'DISCOUNT_PERCENT': '10',
                       'PURCHASE_CAP': 5})


@pytest.fixture
def client(app):
    return app.test_client()


def csrf(client, path='/'):
    client.get(path)
    with client.session_transaction() as session:
        return session['_csrf']


def sign_in(client, database, email='buyer@example.com'):
    with connect(database) as conn:
        register(conn, 'Example Buyer', email, 'secure-password-1234')
    token = csrf(client, '/login')
    return client.post('/login', data={'csrf_token':token,'email':email,'password':'secure-password-1234'},follow_redirects=False)


def test_home_responsive_and_xss_escaped(client):
    html = client.get('/?q=%3Cscript%3Ealert(1)%3C/script%3E').get_data(as_text=True)
    assert 'No events match' in html
    assert '&lt;script&gt;' in html
    assert '<script>alert(1)</script>' not in html
    assert 'viewport' in html


def test_anonymous_checkout_redirect_and_no_records(client,database):
    response = client.get('/checkout/1')
    assert response.status_code==302 and '/login?next=' in response.location
    response = client.get('/orders')
    assert response.status_code==302
    with connect(database) as c:
        assert c.execute('SELECT COUNT(*) FROM orders').fetchone()[0] == 0
        assert c.execute('SELECT COUNT(*) FROM audit').fetchone()[0] == 0


def test_no_open_redirects():
    for url in ['//evil.example','https://evil.example','/\\evil.example','javascript:alert(1)']:
        assert safe_next(url) is None
    assert safe_next('/checkout/1') == '/checkout/1'


def test_logged_out_admin_denied(client):
    assert client.get('/admin').status_code == 302


def test_buyer_cannot_manage_rates_or_view_admin(client,database):
    sign_in(client,database)
    assert client.get('/admin').status_code == 403
    token=csrf(client)
    response=client.post('/admin/rates',data={'csrf_token':token,'currency':'EUR','rate':'3'})
    assert response.status_code==403
    with connect(database) as c:
        assert c.execute("SELECT units_per_usd FROM rates WHERE currency='EUR'").fetchone()[0]=='0.92'


def test_checkout_to_order_with_correct_locking(client,database):
    sign_in(client,database)
    token=csrf(client)
    response=client.post('/checkout/1',data={'csrf_token':token,'quantity':'2','currency':'USD'})
    assert response.status_code==302 and '/orders/' in response.location
    result=client.get(response.location)
    assert result.status_code==200 and b'USD 32.40' not in result.data
    assert b'USD 36.00' in result.data
    with connect(database) as c:
        assert c.execute('SELECT COUNT(*) FROM audit WHERE outcome="success"').fetchone()[0]==1


def test_csrf_missing_rejected(client,database):
    sign_in(client,database)
    result=client.post('/checkout/1',data={'quantity':'1','currency':'USD'})
    assert result.status_code == 400


def test_login_return_and_session_expiry(client,database,app):
    sign_in(client,database)
    assert client.get('/orders').status_code==200
    with client.session_transaction() as sess:
        sess['last_active'] = 1
    assert client.get('/orders').status_code==302


def test_admin_can_change_rate(client,database):
    sign_in(client,database)
    with connect(database) as c:
        c.execute("UPDATE accounts SET role='administrator' WHERE email='buyer@example.com'")
    token=csrf(client)
    assert client.post('/admin/rates',data={'csrf_token':token,'currency':'EUR','rate':'0.95'}).status_code==302
    with connect(database) as c:
        assert c.execute('SELECT units_per_usd FROM rates WHERE currency="EUR"').fetchone()[0]=='0.95'


def test_anonymous_quick_buy_returns_to_event_not_post_only_route(client,database):
    token=csrf(client)
    res=client.post('/quick-buy/1',data={'csrf_token':token})
    assert res.status_code == 302 and ('/events/1' in res.location or '%2Fevents%2F1' in res.location)
    with connect(database) as c:
        assert c.execute('SELECT COUNT(*) FROM orders').fetchone()[0] == 0


def test_quote_uses_single_price_service(client,database):
    sign_in(client,database)
    response = client.get('/quote/1?quantity=2&currency=EUR')
    assert response.status_code==200
    assert response.get_json()['total'] == 'EUR 33.12'


def test_quote_blocks_invalid_currency(client,database):
    sign_in(client,database)
    assert client.get('/quote/1?quantity=1&currency=XYZ').status_code == 400

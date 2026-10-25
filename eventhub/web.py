"""Flask HTTP boundary. Business logic resides in importable testable modules."""
import os
import secrets
import time
from datetime import timedelta
from functools import wraps
from pathlib import Path
from urllib.parse import urlsplit

from flask import (Flask, abort, flash, g, jsonify, redirect, render_template, request,
                   session, url_for)
from werkzeug.exceptions import HTTPException

from . import admin, audit, catalog, db, identity, purchase
from .errors import EventHubError
from .pricing import CURRENCY_DIGITS, compute_quote, display_amount, eligible_for_usf_discount

ROOT = Path(__file__).resolve().parent.parent


def safe_next(target):
    """Only allow relative in-app paths, never scheme-relative or backslash URLs."""
    if not target or not isinstance(target, str):
        return None
    if len(target) > 1024 or '\\' in target or any(ord(c) < 32 for c in target):
        return None
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or not target.startswith('/') or target.startswith('//'):
        return None
    return target


def create_app(test_config=None):
    app = Flask(__name__, template_folder=str(ROOT / 'templates'),
                static_folder=str(ROOT / 'static'))
    app.config.update(
        SECRET_KEY=os.environ.get('EVENTHUB_SECRET_KEY') or secrets.token_hex(32),
        DATABASE=os.environ.get('EVENTHUB_DB', str(ROOT / 'instance' / 'eventhub.sqlite3')),
        SETUP_PATH=str(ROOT / 'config' / 'setup.json'),
        SESSION_IDLE_SECONDS=int(os.environ.get('EVENTHUB_SESSION_IDLE', '1800')),
        DISCOUNT_PERCENT=os.environ.get('EVENTHUB_DISCOUNT_PERCENT') or None,
        PURCHASE_CAP=int(os.environ['EVENTHUB_PURCHASE_CAP']) if os.environ.get('EVENTHUB_PURCHASE_CAP') else None,
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.environ.get('EVENTHUB_HTTPS', '') == '1',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
        MAX_CONTENT_LENGTH=32 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    if app.config.get('TESTING'):
        app.config['SECRET_KEY'] = app.config.get('SECRET_KEY', 'test-key')
    db.initialize(app.config['DATABASE'], app.config['SETUP_PATH'])

    def connection():
        if 'db' not in g:
            g.db = db.connect(app.config['DATABASE'])
        return g.db

    @app.teardown_appcontext
    def close_connection(exc):
        c = g.pop('db', None)
        if c is not None:
            c.close()

    @app.before_request
    def check_session_and_csrf():
        now = int(time.time())
        if session.get('uid'):
            last = session.get('last_active', now)
            if now - last > app.config['SESSION_IDLE_SECONDS']:
                session.clear()
                flash('Your session expired. Please sign in again.', 'warning')
            else:
                session['last_active'] = now
        g.user = identity.user_by_id(connection(), session.get('uid')) if session.get('uid') else None
        if request.method == 'POST':
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            if not token or not secrets.compare_digest(str(token), str(session.get('_csrf', ''))):
                abort(400, description='Invalid or missing security token')

    @app.context_processor
    def context():
        if '_csrf' not in session:
            session['_csrf'] = secrets.token_urlsafe(24)
        return {'current_user': g.get('user'), 'csrf_token': session['_csrf'],
                'currencies': list(CURRENCY_DIGITS), 'money': display_amount,
                'discount_pending': app.config['DISCOUNT_PERCENT'] is None}

    @app.after_request
    def secure_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'; form-action 'self'"
        response.headers['Cache-Control'] = 'no-store' if g.get('user') else 'private, no-cache'
        return response

    def require_user(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if g.user is None:
                target = (request.full_path.rstrip('?') if request.method == 'GET'
                          else (url_for('event_page', event_id=kwargs['event_id'])
                                if request.endpoint == 'quick_buy' else request.path))
                return redirect(url_for('login', next=target))
            return fn(*args, **kwargs)
        return wrapper

    def require_admin(fn):
        @wraps(fn)
        @require_user
        def wrapper(*args, **kwargs):
            if g.user['role'] != 'administrator':
                abort(403)
            return fn(*args, **kwargs)
        return wrapper

    @app.get('/')
    def home():
        term = request.args.get('q', '')[:150]
        events, unmatched = catalog.list_events(connection(), term)
        return render_template('home.html', events=events, query=term, unmatched=unmatched)

    @app.get('/events/<int:event_id>')
    def event_page(event_id):
        event = catalog.get_event(connection(), event_id)
        preview_currency = g.user['currency'] if g.user is not None else 'USD'
        rate = connection().execute('SELECT units_per_usd FROM rates WHERE currency=?',
                                    (preview_currency,)).fetchone()
        try:
            quote = compute_quote(event['base_price_minor'], 1,
                    eligible_for_usf_discount(g.user['email']) if g.user else False,
                    preview_currency, rate['units_per_usd'], app.config['DISCOUNT_PERCENT'])
            price_text = quote.displayed_total
        except EventHubError:
            price_text = 'Price pending configuration'
        return render_template('event.html', event=event, price_text=price_text)

    @app.get('/quote/<int:event_id>')
    @require_user
    def price_quote(event_id):
        try:
            event = catalog.get_event(connection(), event_id)
            count = purchase.parse_quantity(request.args.get('quantity', '1'))
            target = request.args.get('currency', g.user['currency'])
            if target not in CURRENCY_DIGITS:
                raise EventHubError('Unsupported currency')
            rate = connection().execute('SELECT units_per_usd FROM rates WHERE currency=?', (target,)).fetchone()
            if rate is None:
                raise EventHubError('Unsupported currency')
            q = compute_quote(event['base_price_minor'], count,
                              eligible_for_usf_discount(g.user['email']), target,
                              rate['units_per_usd'], app.config['DISCOUNT_PERCENT'])
            return jsonify({'total': q.displayed_total, 'rate': q.rate,
                            'discount_percent': q.discount_percent, 'currency': target})
        except EventHubError as exc:
            return jsonify({'error': str(exc)}), exc.status

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            try:
                identity.register(connection(), request.form.get('name'),
                                  request.form.get('email'), request.form.get('password'))
                flash('Account created. Please sign in.', 'success')
                return redirect(url_for('login'))
            except EventHubError as exc:
                flash(str(exc), 'error')
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            try:
                user = identity.authenticate(connection(), request.form.get('email'),
                                             request.form.get('password'))
                target = safe_next(request.form.get('next')) or url_for('home')
                session.clear()
                session['uid'] = user['id']
                session['last_active'] = int(time.time())
                session['_csrf'] = secrets.token_urlsafe(24)
                return redirect(target)
            except EventHubError as exc:
                flash(str(exc), 'error')
        return render_template('login.html', next_page=safe_next(request.values.get('next')) or '')

    @app.post('/logout')
    @require_user
    def logout():
        session.clear()
        return redirect(url_for('home'))

    @app.get('/checkout/<int:event_id>')
    @require_user
    def checkout(event_id):
        event = catalog.get_event(connection(), event_id)
        return render_template('checkout.html', event=event)

    def perform_purchase(event_id, *, quick=False):
        try:
            order_id = purchase.purchase(connection(), account_id=g.user['id'],
                event_id=event_id, quantity='1' if quick else request.form.get('quantity'),
                currency=g.user['currency'] if quick else request.form.get('currency'),
                discount_percent=app.config['DISCOUNT_PERCENT'],
                purchase_cap=app.config['PURCHASE_CAP'])
            flash('Your simulated purchase was successful.', 'success')
            return redirect(url_for('order_page', order_id=order_id))
        except EventHubError as exc:
            flash(str(exc), 'error')
            return redirect(url_for('event_page', event_id=event_id))

    @app.post('/checkout/<int:event_id>')
    @require_user
    def complete_checkout(event_id):
        return perform_purchase(event_id)

    @app.post('/quick-buy/<int:event_id>')
    @require_user
    def quick_buy(event_id):
        return perform_purchase(event_id, quick=True)

    @app.post('/checkout/<int:event_id>/cancel')
    @require_user
    def cancel_checkout(event_id):
        catalog.get_event(connection(), event_id)
        purchase.cancel_checkout(connection(), account_id=g.user['id'], event_id=event_id)
        flash('Checkout cancelled. No tickets were reserved.', 'warning')
        return redirect(url_for('event_page', event_id=event_id))

    @app.post('/checkout/<int:event_id>/leave')
    @require_user
    def leave_checkout(event_id):
        catalog.get_event(connection(), event_id)
        purchase.cancel_checkout(connection(), account_id=g.user['id'], event_id=event_id)
        return ('', 204)

    @app.get('/orders')
    @require_user
    def orders():
        return render_template('orders.html', orders=purchase.orders_for(connection(), g.user['id']))

    @app.get('/orders/<int:order_id>')
    @require_user
    def order_page(order_id):
        order = purchase.order_for(connection(), g.user['id'], order_id)
        if order is None:
            abort(404)
        return render_template('order.html', order=order)

    @app.post('/currency')
    @require_user
    def currency():
        try:
            identity.set_currency(connection(), g.user['id'], request.form.get('currency'))
            flash('Preferred currency updated.', 'success')
        except EventHubError as exc:
            flash(str(exc), 'error')
        return redirect(safe_next(request.form.get('next')) or url_for('home'))

    @app.get('/admin')
    @require_admin
    def admin_home():
        c = connection()
        return render_template('admin.html', rates=c.execute('SELECT * FROM rates ORDER BY currency').fetchall(),
                               audits=audit.recent(c))

    @app.post('/admin/rates')
    @require_admin
    def admin_rate():
        try:
            admin.change_rate(connection(), g.user['id'], request.form.get('currency'),
                              request.form.get('rate'))
            flash('Exchange rate saved and audited.', 'success')
        except (ValueError, EventHubError) as exc:
            flash(str(exc), 'error')
        return redirect(url_for('admin_home'))

    @app.post('/admin/checkin')
    @require_admin
    def admin_checkin():
        try:
            purchase.redeem(connection(), request.form.get('confirmation_code', ''))
            flash('Confirmation accepted and marked used.', 'success')
        except EventHubError as exc:
            flash(str(exc), 'error')
        return redirect(url_for('admin_home'))

    @app.errorhandler(EventHubError)
    def domain_error(exc):
        return render_template('error.html', message=str(exc)), exc.status

    @app.errorhandler(HTTPException)
    def http_error(exc):
        return render_template('error.html', message=exc.description), exc.code

    return app

"""Flask HTTP boundary. Business logic resides in importable testable modules."""

import os
import secrets
import time
from datetime import timedelta
from functools import wraps
from pathlib import Path
from urllib.parse import urlsplit

from flask import (
    Flask,
    abort,
    flash,
    g,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.exceptions import HTTPException

from . import admin, audit, catalog, db, i18n, identity, monitor, purchase
from .errors import EventHubError, RateLimited
from .pricing import (
    CURRENCY_DIGITS,
    compute_quote,
    display_amount,
    eligible_for_usf_discount,
    order_breakdown,
)
from .ratelimit import RateLimiter

ROOT = Path(__file__).resolve().parent.parent


def safe_next(target):
    """Only allow relative in-app paths, never scheme-relative or backslash URLs."""
    if not target or not isinstance(target, str):
        return None
    if len(target) > 1024 or "\\" in target or any(ord(c) < 32 for c in target):
        return None
    parts = urlsplit(target)
    if (
        parts.scheme
        or parts.netloc
        or not target.startswith("/")
        or target.startswith("//")
    ):
        return None
    return target


def create_app(test_config=None):
    app = Flask(
        __name__,
        template_folder=str(ROOT / "templates"),
        static_folder=str(ROOT / "static"),
    )
    app.config.update(
        SECRET_KEY=os.environ.get("EVENTHUB_SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.environ.get(
            "EVENTHUB_DB", str(ROOT / "instance" / "eventhub.sqlite3")
        ),
        SETUP_PATH=str(ROOT / "config" / "setup.json"),
        SESSION_IDLE_SECONDS=int(os.environ.get("EVENTHUB_SESSION_IDLE", "1800")),
        DISCOUNT_PERCENT=os.environ.get("EVENTHUB_DISCOUNT_PERCENT") or None,
        PURCHASE_CAP=int(os.environ["EVENTHUB_PURCHASE_CAP"])
        if os.environ.get("EVENTHUB_PURCHASE_CAP")
        else None,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("EVENTHUB_HTTPS", "") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
        MAX_CONTENT_LENGTH=32 * 1024,
        # Provisional (Q19): purchase requests allowed per account per window. 0 turns it off.
        PURCHASE_RATE_LIMIT=int(os.environ.get("EVENTHUB_PURCHASE_RATE_LIMIT", "20")),
        PURCHASE_RATE_WINDOW=int(os.environ.get("EVENTHUB_PURCHASE_RATE_WINDOW", "60")),
    )
    if test_config:
        app.config.update(test_config)
    if app.config.get("TESTING"):
        app.config["SECRET_KEY"] = app.config.get("SECRET_KEY", "test-key")
    db.initialize(app.config["DATABASE"], app.config["SETUP_PATH"])
    app.extensions["purchase_limiter"] = RateLimiter(
        app.config["PURCHASE_RATE_LIMIT"], app.config["PURCHASE_RATE_WINDOW"]
    )

    def connection():
        if "db" not in g:
            g.db = db.connect(app.config["DATABASE"])
        return g.db

    @app.teardown_appcontext
    def close_connection(exc):
        c = g.pop("db", None)
        if c is not None:
            c.close()

    @app.before_request
    def check_session_and_csrf():
        g.language = i18n.normalize_language(request.cookies.get("eventhub_lang"))
        now = int(time.time())
        if session.get("uid"):
            last = session.get("last_active", now)
            if now - last > app.config["SESSION_IDLE_SECONDS"]:
                session.clear()
                flash(i18n.translate("flash.session", g.language), "warning")
            else:
                session["last_active"] = now
        g.user = (
            identity.user_by_id(connection(), session.get("uid"))
            if session.get("uid")
            else None
        )
        if request.method == "POST":
            token = request.form.get("csrf_token") or request.headers.get(
                "X-CSRF-Token"
            )
            if not token or not secrets.compare_digest(
                str(token), str(session.get("_csrf", ""))
            ):
                abort(400, description="Invalid or missing security token")

    @app.context_processor
    def context():
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_urlsafe(24)
        return {
            "current_user": g.get("user"),
            "csrf_token": session["_csrf"],
            "currencies": list(CURRENCY_DIGITS),
            "money": display_amount,
            "lang": g.get("language", "en"),
            "t": lambda key, **data: i18n.translate(
                key, g.get("language", "en"), **data
            ),
            "local_money": lambda minor, currency: (
                display_amount(minor, currency)
                if g.get("language", "en") == "en"
                else i18n.local_money(minor, currency, g.get("language", "en"))
            ),
            "local_date": lambda value: (
                str(value)
                if g.get("language", "en") == "en"
                else i18n.local_date(value, g.get("language", "en"))
            ),
            "new_purchase_token": lambda: secrets.token_urlsafe(18),
            "discount_pending": app.config["DISCOUNT_PERCENT"] is None,
        }

    @app.after_request
    def secure_headers(response):
        response.headers["Content-Language"] = g.get("language", "en")
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'; form-action 'self'"
        )
        response.headers["Cache-Control"] = (
            "no-store" if g.get("user") else "private, no-cache"
        )
        return response

    def require_user(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if g.user is None:
                target = (
                    request.full_path.rstrip("?")
                    if request.method == "GET"
                    else (
                        url_for("event_page", event_id=kwargs["event_id"])
                        if request.endpoint == "quick_buy"
                        else request.path
                    )
                )
                return redirect(url_for("login", next=target))
            return fn(*args, **kwargs)

        return wrapper

    def require_admin(fn):
        @wraps(fn)
        @require_user
        def wrapper(*args, **kwargs):
            if g.user["role"] != "administrator":
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    @app.post("/language")
    def set_language():
        language = request.form.get("language")
        if language not in i18n.SUPPORTED_LANGUAGES:
            abort(400, description="Unsupported language")
        target = safe_next(request.form.get("next")) or url_for("home")
        response = make_response(redirect(target))
        response.set_cookie(
            "eventhub_lang",
            language,
            max_age=60 * 60 * 24 * 365,
            samesite="Lax",
            httponly=True,
            secure=bool(app.config.get("SESSION_COOKIE_SECURE")),
        )
        return response

    @app.get("/")
    def home():
        term = request.args.get("q", "")[:150]
        events, unmatched = catalog.list_events(connection(), term)
        return render_template(
            "home.html", events=events, query=term, unmatched=unmatched
        )

    @app.get("/events/<int:event_id>")
    def event_page(event_id):
        event = catalog.get_event(connection(), event_id)
        preview_currency = g.user["currency"] if g.user is not None else "USD"
        rate = (
            connection()
            .execute(
                "SELECT units_per_usd FROM rates WHERE currency=?", (preview_currency,)
            )
            .fetchone()
        )
        try:
            quote = compute_quote(
                event["base_price_minor"],
                1,
                eligible_for_usf_discount(g.user["email"]) if g.user else False,
                preview_currency,
                rate["units_per_usd"],
                app.config["DISCOUNT_PERCENT"],
            )
            price_text = quote.displayed_total
            localized_price_text = i18n.local_money(
                quote.total_minor, quote.currency, g.language
            )
        except EventHubError:
            price_text = "Price pending configuration"
            localized_price_text = price_text
        return render_template(
            "event.html",
            event=event,
            price_text=price_text,
            localized_price_text=localized_price_text,
            price_currency=preview_currency,
        )

    @app.get("/quote/<int:event_id>")
    @require_user
    def price_quote(event_id):
        try:
            event = catalog.get_event(connection(), event_id)
            count = purchase.parse_quantity(request.args.get("quantity", "1"))
            target = request.args.get("currency", g.user["currency"])
            if target not in CURRENCY_DIGITS:
                raise EventHubError("Unsupported currency")
            rate = (
                connection()
                .execute("SELECT units_per_usd FROM rates WHERE currency=?", (target,))
                .fetchone()
            )
            if rate is None:
                raise EventHubError("Unsupported currency")
            q = compute_quote(
                event["base_price_minor"],
                count,
                eligible_for_usf_discount(g.user["email"]),
                target,
                rate["units_per_usd"],
                app.config["DISCOUNT_PERCENT"],
            )
            return jsonify(
                {
                    "total": q.displayed_total,
                    "localized_total": i18n.local_money(
                        q.total_minor, target, g.language
                    ),
                    "rate": q.rate,
                    "discount_percent": q.discount_percent,
                    "currency": target,
                }
            )
        except EventHubError as exc:
            return jsonify({"error": str(exc)}), exc.status

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            try:
                identity.register(
                    connection(),
                    request.form.get("name"),
                    request.form.get("email"),
                    request.form.get("password"),
                    request.form.get("currency") or "USD",
                )
                flash(i18n.translate("flash.account", g.language), "success")
                return redirect(url_for("login"))
            except EventHubError as exc:
                flash(str(exc), "error")
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            try:
                user = identity.authenticate(
                    connection(),
                    request.form.get("email"),
                    request.form.get("password"),
                )
                target = safe_next(request.form.get("next")) or url_for("home")
                session.clear()
                session["uid"] = user["id"]
                session["last_active"] = int(time.time())
                session["_csrf"] = secrets.token_urlsafe(24)
                return redirect(target)
            except EventHubError as exc:
                flash(str(exc), "error")
        return render_template(
            "login.html", next_page=safe_next(request.values.get("next")) or ""
        )

    @app.post("/logout")
    @require_user
    def logout():
        session.clear()
        return redirect(url_for("home"))

    @app.get("/checkout/<int:event_id>")
    @require_user
    def checkout(event_id):
        event = catalog.get_event(connection(), event_id)
        return render_template(
            "checkout.html",
            event=event,
            usf_eligible=eligible_for_usf_discount(g.user["email"]),
        )

    def perform_purchase(event_id, *, quick=False):
        limiter = app.extensions["purchase_limiter"]
        allowed, retry_after, first_block = limiter.check(g.user["id"])
        if not allowed:
            if first_block:
                audit.record(
                    connection(),
                    kind="purchase",
                    account_id=g.user["id"],
                    event_id=event_id,
                    quantity=None,
                    currency=None,
                    outcome="rate_limited",
                    detail=f"more than {limiter.max_requests} requests in {int(limiter.window)}s",
                )
            raise RateLimited(retry_after)
        try:
            result = purchase.place_order(
                connection(),
                account_id=g.user["id"],
                event_id=event_id,
                quantity="1" if quick else request.form.get("quantity"),
                currency=g.user["currency"] if quick else request.form.get("currency"),
                discount_percent=app.config["DISCOUNT_PERCENT"],
                purchase_cap=app.config["PURCHASE_CAP"],
                request_token=request.form.get("purchase_token"),
                require_token=True,
            )
            if result.duplicate:
                flash(
                    i18n.translate("flash.duplicate", g.language),
                    "success",
                )
            else:
                flash(i18n.translate("flash.order", g.language), "success")
            return redirect(url_for("order_page", order_id=result.order_id))
        except EventHubError as exc:
            flash(str(exc), "error")
            return redirect(url_for("event_page", event_id=event_id))

    @app.post("/checkout/<int:event_id>")
    @require_user
    def complete_checkout(event_id):
        return perform_purchase(event_id)

    @app.post("/quick-buy/<int:event_id>")
    @require_user
    def quick_buy(event_id):
        return perform_purchase(event_id, quick=True)

    @app.post("/checkout/<int:event_id>/cancel")
    @require_user
    def cancel_checkout(event_id):
        catalog.get_event(connection(), event_id)
        purchase.cancel_checkout(
            connection(), account_id=g.user["id"], event_id=event_id
        )
        flash(i18n.translate("flash.cancel", g.language), "warning")
        return redirect(url_for("event_page", event_id=event_id))

    @app.post("/checkout/<int:event_id>/leave")
    @require_user
    def leave_checkout(event_id):
        catalog.get_event(connection(), event_id)
        purchase.cancel_checkout(
            connection(), account_id=g.user["id"], event_id=event_id
        )
        return ("", 204)

    @app.get("/orders")
    @require_user
    def orders():
        return render_template(
            "orders.html", orders=purchase.orders_for(connection(), g.user["id"])
        )

    @app.get("/orders/<int:order_id>")
    @require_user
    def order_page(order_id):
        order = purchase.order_for(connection(), g.user["id"], order_id)
        if order is None:
            abort(404)
        return render_template("order.html", order=order, b=order_breakdown(order))

    @app.post("/currency")
    @require_user
    def currency():
        try:
            identity.set_currency(
                connection(), g.user["id"], request.form.get("currency")
            )
            flash(i18n.translate("flash.currency", g.language), "success")
        except EventHubError as exc:
            flash(str(exc), "error")
        return redirect(safe_next(request.form.get("next")) or url_for("home"))

    @app.get("/admin")
    @require_admin
    def admin_home():
        c = connection()
        return render_template(
            "admin.html",
            rates=c.execute("SELECT * FROM rates ORDER BY currency").fetchall(),
            audits=audit.recent(c),
            maintenance_alerts=monitor.alerts(c),
        )

    @app.post("/admin/alerts/<int:alert_id>/acknowledge")
    @require_admin
    def acknowledge_alert(alert_id):
        if not monitor.acknowledge(connection(), alert_id, g.user["id"]):
            abort(404)
        flash(i18n.translate("flash.alert_ack", g.language), "success")
        return redirect(url_for("admin_home") + "#maintenance-alerts")

    @app.post("/admin/rates")
    @require_admin
    def admin_rate():
        try:
            admin.change_rate(
                connection(),
                g.user["id"],
                request.form.get("currency"),
                request.form.get("rate"),
            )
            flash(i18n.translate("flash.rate", g.language), "success")
        except (ValueError, EventHubError) as exc:
            flash(str(exc), "error")
        return redirect(url_for("admin_home"))

    @app.post("/admin/checkin")
    @require_admin
    def admin_checkin():
        try:
            purchase.redeem(connection(), request.form.get("confirmation_code", ""))
            flash(i18n.translate("flash.checkin", g.language), "success")
        except EventHubError as exc:
            flash(str(exc), "error")
        return redirect(url_for("admin_home"))

    @app.errorhandler(EventHubError)
    def domain_error(exc):
        response = app.make_response(
            (render_template("error.html", message=str(exc)), exc.status)
        )
        if getattr(exc, "retry_after", None):
            response.headers["Retry-After"] = str(exc.retry_after)
        return response

    @app.errorhandler(HTTPException)
    def http_error(exc):
        return render_template("error.html", message=exc.description), exc.code

    return app

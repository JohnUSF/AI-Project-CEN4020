"""Independent purchase-anomaly detection and durable human-review queue.

This is a prototype monitor, not a staffed incident-response service. The CLI can
send email through an explicitly configured SMTP relay; otherwise alerts remain in
SQLite for a real administrator to inspect and acknowledge.
"""

from decimal import Decimal

from .errors import EventHubError
from .pricing import compute_quote


def scan_orders(conn, *, deviation_percent=25, max_rows=10000):
    """Compare the *stored* charged amount to a recomputed expected amount.

    Uses the rate and unit USD price stored with each historic order, NOT current
    exchange rates. This matters after admins update currency rates. Idempotent:
    one alert per order/reason even when repeatedly scheduled.
    """
    threshold = Decimal(str(deviation_percent))
    if not 0 < threshold < 100:
        raise ValueError("deviation_percent must be between 0 and 100")
    created = 0
    orders = conn.execute(
        """SELECT id, unit_usd_minor, quantity, currency, rate,
                  discount_percent, total_minor FROM orders ORDER BY id DESC LIMIT ?""",
        (max_rows,),
    ).fetchall()
    for order in orders:
        if order["unit_usd_minor"] is None:  # Part 4 legacy orders lack original price
            continue
        try:
            disc = Decimal(str(order["discount_percent"]))
            expected = compute_quote(
                order["unit_usd_minor"],
                order["quantity"],
                disc > 0,
                order["currency"],
                order["rate"],
                str(disc),
            ).total_minor
        except (ValueError, ArithmeticError, EventHubError):
            # Unsafe or corrupt order data is actionable too.
            category = "unverifiable_order"
            description = "Cannot reconstruct price from stored rate and quantity"
        else:
            difference = abs(Decimal(order["total_minor"]) - Decimal(expected))
            percent = Decimal(100) * difference / max(Decimal(expected), Decimal(1))
            if percent <= threshold:
                continue
            category = "charge_outlier"
            description = (
                f"Stored charge {order['total_minor']} {order['currency']} minor units; "
                f"expected {expected}; deviation {percent.quantize(Decimal('0.1'))}%"
            )
        cursor = conn.execute(
            """INSERT OR IGNORE INTO maintenance_alerts
                 (order_id, category, description) VALUES (?, ?, ?)""",
            (order["id"], category, description),
        )
        created += int(cursor.rowcount == 1)
    return created


def alerts(conn, limit=100):
    return conn.execute(
        "SELECT * FROM maintenance_alerts ORDER BY id DESC LIMIT ?", (min(limit, 250),)
    ).fetchall()


def acknowledge(conn, alert_id, account_id):
    changed = conn.execute(
        """UPDATE maintenance_alerts SET status='acknowledged',
           acknowledged_by=?, acknowledged_at=CURRENT_TIMESTAMP
           WHERE id=? AND status='open'""",
        (account_id, alert_id),
    )
    return bool(changed.rowcount)

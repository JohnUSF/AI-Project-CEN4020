#!/usr/bin/env python3
"""Scheduled monitor: find pricing anomalies and notify a configured human via SMTP.

To send an alert: EVENTHUB_ALERT_TO, EVENTHUB_SMTP_HOST, EVENTHUB_ALERT_FROM.
No contact configured -> keep alerts visible to admins, return code 2 when new.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import os
import smtplib
from email.message import EmailMessage

from eventhub.db import connect
from eventhub.monitor import alerts, scan_orders

p = argparse.ArgumentParser()
p.add_argument(
    "--database", default=os.environ.get("EVENTHUB_DB", "instance/eventhub.sqlite3")
)
p.add_argument("--threshold-percent", type=float, default=25.0)
a = p.parse_args()
with connect(a.database) as db:
    new = scan_orders(db, deviation_percent=a.threshold_percent)
    waiting = [
        row
        for row in alerts(db)
        if row["status"] == "open" and row["notified_at"] is None
    ]
    print(f"{new} new; {len(waiting)} open anomaly alert(s)")
    if not waiting:
        raise SystemExit(0)
    recipient = os.environ.get("EVENTHUB_ALERT_TO")
    host = os.environ.get("EVENTHUB_SMTP_HOST")
    sender = os.environ.get("EVENTHUB_ALERT_FROM")
    if not all((recipient, host, sender)):
        print(
            "ALERT DELIVERY UNCONFIGURED. Open the admin dashboard, assign an owner and configure SMTP."
        )
        raise SystemExit(2)
    msg = EmailMessage()
    msg["Subject"] = "EventHub needs review: order anomaly alerts"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(
        "EventHub order anomalies (no customer PII):\n"
        + "\n".join(
            f"Order {row['order_id']}: {row['category']} - {row['description']}"
            for row in waiting
        )
    )
    try:
        with smtplib.SMTP(
            host, int(os.environ.get("EVENTHUB_SMTP_PORT", "25")), timeout=10
        ) as smtp:
            if os.environ.get("EVENTHUB_SMTP_STARTTLS") == "1":
                smtp.starttls()
            if os.environ.get("EVENTHUB_SMTP_USER"):
                smtp.login(
                    os.environ["EVENTHUB_SMTP_USER"],
                    os.environ["EVENTHUB_SMTP_PASSWORD"],
                )
            smtp.send_message(msg)
        db.executemany(
            "UPDATE maintenance_alerts SET notified_at=CURRENT_TIMESTAMP WHERE id=?",
            [(item["id"],) for item in waiting],
        )
        print("SMTP accepted message for", recipient, "; receipt by human not verified")
    except Exception as exc:
        print("Notification failed:", type(exc).__name__, str(exc))
        raise SystemExit(3)

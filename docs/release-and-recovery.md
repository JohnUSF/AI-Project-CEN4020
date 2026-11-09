# Call 6 maintenance: rollback, backup and monitoring runbook

**This is a classroom prototype, not evidence that we operated a real EventHub production system.** The Call 6 incident (release 1.3 charged ¥45 instead of ¥4,500) is a scenario supplied by the professor. We did not deploy either fictional release.

## Before a new release

1. Freeze and tag the last verified release, record its Git commit ID and the deployment settings. Do not place secrets or a live `.sqlite3` file in Git.
2. Run `python run_all_tests.py --with-mutation` with Chrome and Selenium installed. Include the Call 6 four-currency purchase, all yen receipt checks, and a browser test of an administrator changing rates.
3. Back up the SQLite database with `python scripts/backup_db.py --database instance/eventhub.sqlite3 --output backups/before-release.sqlite3`. Store its generated manifest and SHA-256 file securely **off the host** after an owner and retention policy have been approved.
4. Verify backup integrity with the built-in backup function or `scripts/restore_db.py` in a throwaway stopped test environment. Record the exercise outcome. Backup frequency, offsite destination and owner are unresolved (Q25).
5. Perform human review of the release diff, especially code touching pricing, date/currency formatting, and exchange-rate configuration. Mark the version as approved before publishing.

## If a currency incident happens

1. **Stop or disable checkout** using the host/deployment mechanism; do not try to hot-fix a live undercharge without containment.
2. Restore the previously tested **application release** through the real deployment system (known-good tag). Do not roll back database records or erase orders as a side effect. The incident narrative says this took 11 minutes; **we have not reproduced that production timing**.
3. Confirm smoke tests: USD/EUR/GBP/JPY exact checkout totals and a rate update followed by a new order. The prior order must keep its original rate.
4. Preserve event logs, rate-change audit records, and data snapshots for review. Contact affected customers based on an approved policy.
5. Patch in a separate branch; run the full suite and review before release.

## Monitoring setup (requires a human owner)

- `python scripts/check_order_anomalies.py --database instance/eventhub.sqlite3` compares stored purchase totals with recomputed totals from each order's original USD unit price, discount and exchange rate. It writes a durable idempotent alert to `maintenance_alerts` when deviation exceeds a **provisional** 25% threshold (Q22); it does not reprice the order.
- Alerts are visible and acknowledgeable only in the administrator area. To have an external human receive them, set `EVENTHUB_ALERT_TO`, `EVENTHUB_ALERT_FROM`, `EVENTHUB_SMTP_HOST` and optional SMTP settings. The CLI returns exit code 2 when alerts exist without delivery configuration, or 3 on failed delivery; an alert is not marked `notified_at` unless SMTP accepts the message.
- A scheduler (cron, host job, or monitor service) and an on-call owner must be designated by the team. No regular monitoring is active just because this code exists. Do not claim a staffed or production alert mechanism until tested and assigned (Q23).

## SQLite backups / restoration

- **Why not `cp database.sqlite3`?** WAL mode may hold recently committed changes in a separate file. `eventhub.backups.create_backup()` uses SQLite's backup API, checks `PRAGMA integrity_check`, and writes a SHA-256 manifest.
- **Restoring:** Stop the app first; verify you have a separate good database backup; then run `python scripts/restore_db.py --backup backups/before-release.sqlite3 --destination instance/eventhub.sqlite3 --confirm-restore`. The tool rejects changed bytes before replacing the file.
- This only solves the local-copy part of disaster recovery. Retention, offsite storage, owner, secure access, recovery-time objective, recovery-point objective and real-host drills remain open (Q25).

## Maintenance decisions intentionally pending

The incident does not define an anomaly threshold, alert channel/rotation, backup ownership, production deployment tool, date timezone, or translated text approver. Those are tracked in `docs/open-items.md` (Q22–Q26) and `docs/risk-register.md` (RISK-006–010), not silently treated as approved.

## Release status after the final assignment review

This classroom submission is documented, but it is **not approved for real operations**: Call 6 required backup ownership by Friday and no named person was recorded. Alert email also has no named recipient or tested schedule. English yen is numerically correct with no decimal places but still reads `JPY 4,500` rather than `¥4,500`; language is a manual cookie preference rather than region detection. These are visible blockers in `docs/part6-release-decisions.md`, not assumed fixes.

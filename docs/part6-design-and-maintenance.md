# Part 6 change record and maintainability decisions

| Call 6 concern | Previous Part 5 design | Part 6 change and why | Evidence |
|---|---|---|---|
| Yen undercharge described in incident | `compute_quote` uses integer minor units; `display_amount` knows JPY has zero digits. No actual undercharge reproduced in our Part 5 baseline. | Preserve central pricing. Isolate all presentation in `eventhub/i18n.py`, using `Decimal` and Babel only to show localized text. Charge still uses stored integer minor units. | `tests/test_call6_maintenance.py`, `tests_system/test_call6_browser.py` |
| Admin exchange-rate edits | `change_rate` is already atomic and audited. | Add specific rate-change-followed-by-next-purchase regression, checking previous order rate unchanged. | `test_admin_rate_change_is_used_by_next_purchase_not_previous`, browser admin test |
| Audit entries were not watched | Audit table and admin audit view, but no anomaly scan. | `eventhub/monitor.py` independently checks orders against their saved price/rate, persists unique alerts, admin acknowledgement, optional SMTP scheduler. | `tests/test_call6_maintenance.py`, `scripts/check_order_anomalies.py` |
| Database disaster question | SQLite WAL with migration but no backup/restore scripts. | `eventhub/backups.py` safely snapshots with SQLite API, SHA-256 manifest, integrity check; guarded restore. | `test_online_backup_integrity_and_guarded_restore` |
| Rollback-first operational practice | Previously no release-switch runbook. | Added `docs/release-and-recovery.md`, including release ID, smoke tests, rollback and backup recovery practice. We cannot test a host we do not operate. | documented operational protocol |
| International localization | HTML English-only and ISO timestamps; `pricing.display_amount` shared for money. | English/Spanish JSON catalogs, client language selector, Spanish date and money formatting, pure translation adapter independent of business logic. Preserves English receipt data contract for Part 5 regression tests. | `tests/test_call6_maintenance.py`, optional real-browser test |

## Design boundaries

- **`pricing.compute_quote`** is the only money computation; no template modifies stored `orders.total_minor`.
- **`i18n.local_money`** accepts integer minor units and returns a display-only string; it cannot write orders, alter rates or calculate a charge.
- **`monitor.scan_orders`** operates on persisted orders using each order's original rate, not the administrator's current rate. It never modifies purchases; alerts are separate rows.
- **`backups`** has no dependency on Flask, users, or templates; scripts call it independently.
- **Current system:** no real credit-card payments; no genuine uptime/rollback deployment, SMS/Slack on-call rotation, or multilingual content review.

## Maintainability improvements

1. Adding a third language requires one new JSON dictionary and a locale mapping instead of changing dozens of page/business functions.
2. Price display cannot accidentally mutate purchase amounts because localization accepts the completed integer total after `compute_quote` returns.
3. Monitoring is testable without a browser or SMTP server. The notifier is a separate optional script; failures leave alert rows intact.
4. Backups use a standard SQLite API and are testable in temporary directories rather than coupling recovery to hosting.
5. All new functions have standalone tests and matching EARS IDs, with the original Part 5 requirements and C4 history retained.

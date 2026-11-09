# EventHub — Part 6 maintenance (Team 5, Gold member: Jaideep Yarasingu)

This extends John Bachta's Part 5 project. The existing modules, requirements, Part 5 browser tests, and saved test evidence have been preserved. **This is a simulated ticketing application, not a real production service.** The release 1.3 yen incident is a scenario from the Call 6 assignment, not a crash we witnessed on this build.

## Main changes

- **One price computation:** `pricing.compute_quote()` still uses integer smallest currency units. `i18n.local_money()` only formats finished values, supports Spanish conventions, and cannot recalculate charges. A configurable English/Spanish language selector appears in the header; event dates use display-only formatting.
- **Maintenance regression:** new tests verify actual persisted purchases in USD, EUR, GBP, JPY and a changed administrator exchange rate applied to subsequent purchases, not earlier ones.
- **Audit monitoring:** `monitor.scan_orders()` compares order totals against original stored unit price and rate. Outliers are stored once in a new `maintenance_alerts` table, viewed and acknowledged by administrators, with an optional SMTP notification script. No alert delivery is claimed unless configured.
- **Disaster recovery:** `backups.py` uses SQLite online backup, integrity checks, SHA-256 manifests, and explicit offline restore confirmation. No offsite schedule/owner is assigned.
- **Source traceability:** 11 new EARS requirements, added `Part6Components` C4 view and Graphviz diagram, and `docs/part6-traceability.md`. Existing Part 5 files remain available.

## Test and run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt -r requirements-system.txt
python run_all_tests.py                 # entire Part 5 + Part 6 suite and Selenium system tests
python run_all_tests.py --with-mutation # optional existing mutation suite too
```

Requires Google Chrome with an accessible matching ChromeDriver for Selenium. `run_all_tests.py` will produce new `report/last_run.json` and dashboard once you run it. The saved Part 5 dashboard is **historical**; don't call it Part 6 verification.

Run the smaller Call 6 tests with:

```bash
python -m pytest tests/test_call6_maintenance.py tests/test_call6_http.py -q
python -m pytest tests_system/test_call6_browser.py -q
python grading/check_part3.py .
python grading/check_test_traceability.py .
ruff format --check eventhub tests tests_system scripts
ruff check eventhub tests tests_system scripts --select E4,E7,E9,F63,F7,F82
```

### Developer demo (not a live production deployment)

```bash
export EVENTHUB_DISCOUNT_PERCENT=10  # only a demo rate; Q1 is still open
python run.py
# open http://127.0.0.1:5000
```

Use the English/Spanish language selector in the header. The admin area shows stored order alerts; `scripts/check_order_anomalies.py` must be scheduled and configured for human email delivery (see `docs/release-and-recovery.md`).

### Database maintenance

```bash
python scripts/backup_db.py --database instance/eventhub.sqlite3 --output backups/eventhub.sqlite3
# STOP THE APP before restoring:
python scripts/restore_db.py --backup backups/eventhub.sqlite3 --destination instance/eventhub.sqlite3 --confirm-restore
python scripts/check_order_anomalies.py --database instance/eventhub.sqlite3
```

The scheduled backup and alert jobs are **not active** until an operator configures and tests them. Customer decisions on alert owner/threshold, backup retention, timezone and localization approval remain open.

## Final team submission notes

This is the completed **classroom Part 6 submission package** for Team 5. Source, requirements, diagrams, the assignment report, and retained test evidence are included. The **final reviewed branch state**, including the small locale-formatting refactor and its new regression test, passed **161 unit/integration and 139 Selenium tests (300 total, 0 failed)** on macOS on November 9, 2026. Saved evidence: `report/last_run.json` (13:20:04), `report/test_dashboard.html`, `report/unit_run/results.json`, and `report/system_run/results.json`. The latest PR #3 revision passed the GitHub Actions quality and system-test jobs. These are classroom verification results, not a production-service approval.

The report distinguishes finished coursework from real production readiness. Call 6 did not provide a named backup owner, a staffed alert recipient, a region-detection policy, or a production rollout/rollback platform. They remain explicit open operational decisions, not completed infrastructure. Refer to `docs/part6-ai-simplification-review.md` and `docs/part6-release-decisions.md`.

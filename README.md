# EventHub (CEN 4020, Team 5) — Part 6 Maintenance

This is a Python/Flask/SQLite **classroom prototype** with simulated ticket purchases. It extends John's Part 5 implementation; the Part 5 baseline report, test dashboard and original README remain available under `report/` and `docs/part5-readme-baseline.md`.

**Read first:** `PART6_README.md`, `report/EventHub_Part6_Assignment_Report.pdf`, and `docs/part6-traceability.md`.

## What changed in Call 6

- Yen-safe currency regression tests and a separate Spanish-language display layer (`eventhub/i18n.py`, `locales/`). Pricing still uses integer minor units.
- Administrator exchange-rate updates covered by a persisted-order regression test.
- Order-anomaly monitoring with durable administrator-visible alerts and optional configured SMTP notification.
- Verified SQLite online backup and guarded offline restore tools.
- Revised EARS requirements and C4 view (`workspace.dsl`, `diagrams/Part6Components.*`) plus rollback and recovery documentation.
- Original unit, integration, Selenium and mutation tests preserved, with new Call 6 test files added.

## Quick start

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt -r requirements-system.txt
python run_all_tests.py       # full local verification including headless Chrome
```

The complete tests need Flask, Werkzeug, Selenium, Ruff and ChromeDriver. The last verified pre-review revision completed 160 unit/integration and 139 browser tests on a Mac, and all four GitHub quality/system checks passed. The later formatting-helper refactor still needs its full-suite and CI rerun before being described as verified. Historical Part 5 evidence is archived under `report/baseline/`; the dashboard in `report/test_dashboard.html` is the Part 6 run.

## Important open decisions

All real-world sales are simulated. No approved discount rate, staffed anomaly alert rotation, production release mechanism, offsite backup schedule or localized content review was provided. Read `docs/open-items.md` and `docs/risk-register.md` before claiming readiness for a live release. These decisions are tracked explicitly for the next deployment phase. The classroom submission is complete as a report/code handoff; it is not a production-release sign-off.

## What was actually simplified for maintainability

`eventhub/web.py` now delegates both date and currency display to the existing `eventhub/i18n.py` adapter. That module owns the English and Spanish branches and preserves the previous English date and charge strings. A new test protects that behavior; no pricing or order transaction was refactored. See `docs/part6-ai-simplification-review.md` for the AI review and larger refactors intentionally deferred.

## Status of international formatting

The selector stores an explicit English/Spanish **language preference** in a cookie; it does not read the browser's geographic region. English yen remains the legacy `JPY 4,500` display (correct amount and zero decimals, but not the requested `¥4,500` symbol). Spanish formatting uses Babel. This outstanding presentation gap and the customer-approval steps are recorded in `docs/part6-release-decisions.md`.

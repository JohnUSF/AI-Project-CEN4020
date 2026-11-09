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

The complete tests need Flask, Werkzeug, Selenium, Ruff and ChromeDriver. They **have not** all been rerun in the offline environment used to assemble this package; refer to the new report for the actual verification results. The original Part 5 dashboard represents earlier evidence, not Part 6 testing.

## Important open decisions

All real-world sales are simulated. No approved discount rate, staffed anomaly alert rotation, production release mechanism, offsite backup schedule or localized content review was provided. Read `docs/open-items.md` and `docs/risk-register.md` before claiming readiness for a live release. This work should be reviewed by John on a separate branch rather than overwriting the team's existing repository.

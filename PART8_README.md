# EventHub — Part 8: Software Quality (Team 5)

**Starting point:** the team's merged Part 7 `main` snapshot. **Goal:** release 1.5 introduces Flask-Babel internationalization and a fixed-version code-review skill assessment of the Part 5→Part 8 changes. This classroom prototype does not process real payments.

## Start here (Mac)

Read `PART8_MAC_STEPS.md`, then run `bash scripts/verify_part8_mac.sh`. You need Python **3.12 or 3.13**, Google Chrome (for Selenium), Homebrew optional, and internet for dependency installation. This script makes a separate `.venv-part8`, so older Mac Python 3.9 and existing virtual environments are not modified.

## Submission layout

- `features/localization/requirements.md` — eight separately testable EARS requirements from Call 7, including written decisions on languages, pages, translation source, selection precedence, and persistence.
- `features/localization/scenarios/spanish_interface.feature` — tagged, executable pytest-bdd scenarios next to requirements.
- `translations/{en_US,es_ES}/LC_MESSAGES/messages.po` and `messages.mo` — editable and compiled **gettext** message catalogs, generated from Part 7's 199-key translations. English and Spanish translations remain in `locales/*.json` for compatibility with earlier tests, but Flask-Babel serves gettext translation strings on actual pages.
- `eventhub/web.py`, `eventhub/i18n.py` — Flask-Babel integration, active locale resolver, formatted dates/currencies; no changes to purchasing, rates, order persistence, or stock.
- `tests/test_part8_flask_babel.py`, `tests/test_part8_scenarios.py` — focused integration and executable behavior scenarios, plus all original tests preserved.
- `.github/workflows/quality.yml`, `.github/workflows/check_part5.yml` — continuous existing quality checks plus named Part 5 eligibility workflow.
- `docs/part8-discussion7-decisions.md` — discussion/requirements/design/code/test trace and open customer decisions.
- `docs/part8-genai-process.md` — AI assistance, corrections, and review of its mistakes.
- `docs/part8-review-record.md` — single-pass five-axis review using the exact pinned skill text, with findings and provisional decisions that the human team must approve.
- `scripts/install_part8_review_skill_mac.sh` — installs **code-review-and-quality** from `addyosmani/agent-skills` at exact SHA `301b02b12bff98e4688e6984af6556802322bbde` into `.agents/skills` and `.claude/skills`. Run on a Mac that has GitHub access; do not put credentials into agent config.

## Scope choices

- English and Spanish. User's explicit language cookie wins over operator `default_language`; the `Accept-Language` header does *not* override that configuration in version 1.5. No account language column is added.
- Spain Spanish (`es_ES`) and US English (`en_US`) are provisional display locales. The customer's intended region, native-speaker validation, and production translation ownership remain open.
- Dates and currency amounts are display-only; stored times, exchange rates, inventories and charge calculations never change.
- Existing English receipts still show legacy `JPY 4,500` instead of a currency-native yen sign; fixing this requires a separately reviewed compatibility/test update. The existing yen zero-decimal and all previous behaviors must remain green.
- Customer event descriptions and venues are data, not UI catalogs. Operators' logs are not translated.

## Evidence and verification policy

`report/last_run.json` and its dashboard are the **Part 7 baseline**, recording 182 unit/integration and 140 Selenium tests (322); these are not proof that Part 8 passed. This draft has been checked with compileall, the Part 3 EARS/C4 gate, requirement traceability, compiled catalog consistency, and the scenario tag check **inside the authoring environment**. The full Flask/Selenium suite cannot be run there because the dependencies cannot be downloaded. Do not report Part 8 test passes until `bash scripts/verify_part8_mac.sh` succeeds locally and GitHub Actions is green.

## What must happen before final submission

1. Run the Mac verification script; fix any failures, and save `report/last_run.json` and the dashboard from **that** run.
2. Install the pinned skill with the provided script and have an AI coding agent run it in **read-only review mode** on the diff from the actual Part 5 submission commit `cc73d4f5b85bd269e122438c7d8e450e70f0b279` to the **new Part 8 commit**. The code reviewer may provide findings, not modify the repository itself.
3. You and John decide accept/reject on **each** finding and initial `docs/part8-team-signoff.md`. Apply accepted changes in a separate normal coding step and rerun all tests.
4. Open a PR from `part8-jaideep-gold` to `main`; confirm both `quality.yml` and `check_part5.yml` pass on the exact commit. Get John to review and merge **before the deadline**. Part 5 eligibility is a zero-grade gate.
5. Generate the finished PDF report *after* the actual Mac and CI results are available; replace the verification-pending text rather than pretending they passed.

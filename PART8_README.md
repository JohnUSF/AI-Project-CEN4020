# EventHub — Part 8: Software Quality (Team 5)

**Starting point:** the team's merged Part 7 `main` snapshot. **Goal:** planned release 1.5 introduces Flask-Babel internationalization and a fixed-version code-review skill assessment of the Part 5→Part 8 changes. This classroom prototype does not process real payments.

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
- `docs/part8-review-record.md` — single-pass five-axis review using the exact pinned skill text, with four findings and recorded team accept/reject decisions.
- `scripts/install_part8_review_skill_mac.sh` — installs **code-review-and-quality** from `addyosmani/agent-skills` at exact SHA `301b02b12bff98e4688e6984af6556802322bbde` into `.agents/skills` and `.claude/skills`. Run on a Mac that has GitHub access; do not put credentials into agent config.

## Scope choices

- English and Spanish. User's explicit language cookie wins over operator `default_language`; the `Accept-Language` header does *not* override that configuration in version 1.5. No account language column is added.
- Spain Spanish (`es_ES`) and US English (`en_US`) are provisional display locales. The customer's intended region, native-speaker validation, and production translation ownership remain open.
- Dates and currency amounts are display-only; stored times, exchange rates, inventories and charge calculations never change.
- Existing English receipts still show legacy `JPY 4,500` instead of a currency-native yen sign; fixing this requires a separately reviewed compatibility/test update. The existing yen zero-decimal and all previous behaviors must remain green.
- Customer event descriptions and venues are data, not UI catalogs. Operators' logs are not translated.

## Verified Mac / GitHub results (2026-11-19)

After the pinned AI code review and three required follow-up fixes, `bash scripts/verify_part8_mac.sh` completed successfully on the Gold member's Mac: 199 unit/integration tests plus 140 Selenium/system tests, totaling **339 passed**, with Ruff lint/format, Part 3 EARS/C4 eligibility and traceability also green. The 8 newly registered localization markers ran without the previous warnings. Real screenshots are `report/part8_mac_339_passed.png` and `report/part8_ci_successful_rerun.png`. The older generated `report/last_run.json` may describe an earlier baseline; refer to `report/PART8_FINAL_VERIFICATION.md` for the final observed run instead of confusing historical artifacts with Part 8 evidence.

GitHub PR #5 (`part8-jaideep-gold` at `dbebb63`) has green PR quality/system tests and Part 5 eligibility. The first push system run failed a 500 ms **placeholder** p95 latency budget (observed 639.8 ms); one rerun passed, so the source of latency variation and the customer's actual performance threshold are still open. This is not evidence of a functional checkout failure.

## Updated Call 7 additions and scope clarification

- Older feature folders now have tagged and executable `.feature` scenarios beside their requirements (the earlier ZIP only had the localization scenario); see `tests/test_part8_legacy_scenarios.py`.
- Languages (`en`, `es`), covered pages, and translation source/provenance are explicitly described under `features/localization/requirements.md`; source metadata is recorded per key in `docs/part8-translation-provenance.json`.
- Language persistence has a tested CSRF-protected, HttpOnly, SameSite=Lax cookie; key/placeholder validation for externally edited drafts is in `scripts/validate_translation_catalogs.py` and candidate version policy is in `config/release.json`. The external spreadsheet is *not* the release source of truth; changes must go through version-controlled gettext catalogs.
- The current English date/JPY presentation is a **known compatibility exception** pending the customer decision; `es_ES` uses Babel presentation. Neither path changes stored amounts or timestamps.
- Version 1.5 is a **proposed language-only release**; no live version tag or production deployment is asserted. PR #5 includes *additional* follow-up backup and SMTP corrections in a separate commit, so a true language-only release would need those changes split during release planning. This classroom deliverable reports both change sets transparently.
- The pinned review produced three Required findings accepted by Jai and John plus one Optional yen-format change rejected for this submission. Review reason summaries and Kenji's conditions are in `docs/part8-review-record.md`.

## Before Canvas submission

1. Apply this final candidate's added requirements, scenarios, diagram and documentation to `part8-jaideep-gold` using the supplied patch. Run the **entire expanded** Mac unit + Selenium suite, not only the 339-test previous baseline, and record the actual new number. Do not assume a particular passing total.
2. Push the candidate, confirm *all* GitHub Actions checks including `check_part5` pass, and merge reviewed PR #5 into `main` before the deadline. GitHub's default-branch source and test results, not a detached review ZIP, determine eligibility.
3. Download the *merged-main* source ZIP and include the updated Part 8 report. This packaged candidate cannot itself prove the merge; retain the final GitHub commit/CI link.

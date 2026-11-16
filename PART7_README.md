# EventHub — Part 7 configuration management (Team 5)

The customer asked for EventHub to run in English or Spanish by configuration. Part 6 already had a Spanish selector, so this part found everything still in English, traced it to the code, and made the language a setting.

## Choose the language

- **Default language:** set `"default_language": "es"` (or `"en"`) in `config/setup.json`, or start the app with `EVENTHUB_LANGUAGE=es`. The variable wins. Any other value stops start-up with a clear message.
- **Reader's choice:** the language picker in the page header stores a cookie, and the reader's choice beats the default on every later page.
- **Add a language:** see the last section of `docs/part7-traceability.md`.

## What changed

- Four new requirements, `system-014` to `system-017` (`features/system/requirements.md`), written before the code. The design file `workspace.dsl` was updated to match.
- Page titles, accessibility labels, hints, notes, order lines, the admin table header, 26 error messages, the framework's 403/404/400 pages and the browser script's messages now come from `locales/en.json` and `locales/es.json` (199 entries each). English wording is unchanged.
- Translation happens when text is shown. Pricing, purchase, inventory, the audit trail and stored orders were not touched.
- `docs/part7-traceability.md` links each requirement to its design, code and tests.

## Verification (November 15, 2026)

| Check | Result |
|---|---|
| Unit and integration tests | 182 passed (161 before; 21 new in `tests/test_part7_language_config.py`) |
| Browser system tests + load | 140 passed (139 before; 1 new in `tests_system/test_part7_browser.py`) |
| EARS and design gate | Eligible; 122 requirements, 115 active, 0 failures |
| Requirement-to-test traceability | 0 failures |
| Ruff lint and format | Passed |

Run on Linux with Chrome 153 and a matching ChromeDriver, using `python run_all_tests.py`. Evidence: `report/last_run.json`, `report/unit_run/results.json`, `report/system_run/results.json`, `report/test_dashboard.html`, and screenshots in `report/part7_evidence/`. The GitHub Actions workflow has not been run on the Part 7 changes yet.

## Still open

- Event names, venues and descriptions are event data and remain English.
- The Spanish wording has not been reviewed by a native speaker, and the locale variant (Spain Spanish, from Part 6) is not confirmed by the customer.
- Items left open in Part 6 (alert recipient, backup owner, production rollback drill) are unchanged: see `docs/open-items.md`.

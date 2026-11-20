# Part 8 requirement → design → code → tests

| ID | Purpose | C4/design | Code | Tests |
|---|---|---|---|---|
| localization-001 | Flask-Babel message catalogs | Localization component | `web.py`, `i18n.py`, `translations/*` | `test_flask_babel_message_catalogs_are_compiled_and_complete`, `test_flask_babel_is_active_during_a_spanish_request`, `test_spanish_catalog_scenario` |
| localization-002 | Spanish UI across buyer/admin/error screens | Existing page templates + localization | `templates/*`, `web.py` | `test_spanish_covers_home_and_login_using_compiled_catalogs`, `test_spanish_catalog_scenario` + Part 7 `spanish_pages` and Selenium |
| localization-003 | Saved user preference | HTTP language form | `web.py:/language` | `test_explicit_choice_overrides_default_not_accept_language`, `test_reader_choice_scenario` |
| localization-004 | Operator default vs browser header | Config container | `web.py:before_request`, `config/setup.json` | `test_explicit_choice_overrides_default_not_accept_language`, `test_reader_choice_scenario` |
| localization-005 | Babel dates/currencies, no stored price mutation | Localization / Pricing boundary | `i18n.local_money`, `i18n.local_date` | `test_spanish_babel_money_and_date_keep_yen_without_decimals`, `test_yen_format_scenario`, old yen regressions |
| localization-006 | Missing translation falls back to English | i18n adapter | `i18n.translate` | `test_missing_spanish_message_falls_back_to_english`, `test_missing_catalog_key_scenario` |
| localization-007 | Version-controlled catalogs not price code | Localization component | `.po`, `.mo`, `i18n.py` | `test_translations_do_not_modify_saved_prices_or_requirements`, `test_spanish_catalog_scenario` |
| localization-008 | Invalid config rejected | Config validation | `i18n.validate_language_setting` | `test_unsupported_operator_language_is_rejected_before_requests`, `test_bad_default_scenario` |

Review the requirements before coding. Traceability checker, EARS gate and executable pytest-bdd scenarios are kept next to the code. The ZIP includes old requirements and tests rather than replacing them with Part 8-only snippets.

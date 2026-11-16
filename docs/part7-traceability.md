# Part 7: requirement -> design -> code -> tests (configurable English/Spanish interface)

Part 7 asks for the interface to be configurable for English or Spanish, with the change traced from the requirement to the code. The Part 6 localization already covered the menus and the main pages. This pass found and closed the gaps, and made the language a configuration setting. No earlier requirement ID was changed or removed.

| Requirement (`features/system/requirements.md`) | Design (`workspace.dsl`) | Code that implements it | Tests that protect it (`tests/test_part7_language_config.py` unless noted) |
|---|---|---|---|
| **system-014** default language comes from application settings | Localization component reads the default-language setting from the config container | `config/setup.json` (`default_language`); `EVENTHUB_LANGUAGE` environment variable; `i18n.default_language_from_setup`, `i18n.validate_language_setting`; `web.create_app` | `test_setup_file_sets_the_default_language`, `test_environment_variable_overrides_the_setup_file`, `test_english_is_the_default_when_nothing_is_configured`, `test_a_mistyped_default_language_stops_start_up` |
| **system-015** the reader's choice replaces the default | Boundary chooses the language: reader choice first, then the configured default | `i18n.pick_language`; `web.check_session_and_csrf` | `test_the_readers_choice_beats_the_configured_default` (both directions); browser: `tests_system/test_part7_browser.py` |
| **system-016** Spanish covers every reader-facing text | Localization formats text, titles, labels and error messages, not only dates and money | `templates/*.html` (titles, accessible labels, hints, notes); `locales/en.json` + `locales/es.json` (+74 entries); `i18n.error_text`, `i18n.http_text`; `web.py` error handlers, flash messages and price-preview service; `static/app.js` | `test_no_english_sentence_is_left_on_any_spanish_screen` (12 screens), `test_spanish_page_titles_and_accessible_labels`, `test_spanish_error_pages_for_missing_and_forbidden`, `test_spanish_signed_in_hint_and_event_note_name_the_currency`, `test_spanish_order_detail_keeps_the_yen_amount_without_decimals`, `test_spanish_validation_errors_reach_the_reader_in_spanish`, `test_the_price_preview_service_answers_in_the_readers_language`, `test_error_text_translates_messages_codes_and_the_wait_time`, `test_every_message_the_code_can_raise_has_a_spanish_translation`, `test_english_wording_is_exactly_what_it_was_before_part_7` |
| **system-017** all reader-facing text lives in the language files | Language dictionaries are the only place text is kept | Templates and `static/app.js` read text from the catalogs (the script gets its text through `data-msg-*` attributes on `<body>`) | `test_page_templates_hold_no_reader_facing_text`, `test_the_script_holds_no_reader_facing_text`, `test_language_files_match_and_every_key_is_used_once_defined` |

Existing requirements still protected by the same files: system-010, system-011, pricing-019 (`tests/test_call6_http.py`, `tests_system/test_call6_browser.py`). The yen regression tests from Call 6 are unchanged and still green.

## What did not change

Prices, rates, discounts, stock, the audit trail and the stored order records are untouched. Language code only receives finished integer amounts and returns text, as before (`i18n.local_money`). English wording is byte-for-byte what it was; `test_english_wording_is_exactly_what_it_was_before_part_7` and the earlier English browser tests hold it there.

## Left in English on purpose (open items for the customer)

- Event artist, venue and description text. These are event data in `config/setup.json` and the database, not interface text. Spanish event descriptions would need translated event data (a customer decision).
- Messages for operators on the command line (`backups.py`, `monitor.py`, the scripts), and the audit-log record kinds. They are not shown to ticket buyers.
- Spanish wording is machine-assisted and has not been reviewed by a native speaker (Call 6 left customer translation approval open).

## How to configure and extend (for the operator)

- **Choose the default language:** set `"default_language": "es"` in `config/setup.json`, or start the app with `EVENTHUB_LANGUAGE=es` (the variable wins). Any value other than `en` or `es` stops start-up with a clear message. A reader can still pick the other language in the page header; the choice is saved in a cookie and wins over the default.
- **Add a language:** copy `locales/en.json` to `locales/<code>.json` and translate the values (keep each `{placeholder}` exactly), then add the code to `SUPPORTED_LANGUAGES` and `LANGUAGE_LOCALES` in `eventhub/i18n.py`. The test `test_language_files_match_and_every_key_is_used_once_defined` fails if a key or placeholder is missing, and the language picker in `templates/base.html` needs one more `<option>`.

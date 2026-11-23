# Call 7 / Part 8 — requirements, model, code, and test decisions

This note is based on Discussion 7 in the course's five-page Part 8 PDF, not assumptions from the earlier Part 7 assignment. It records the team's implementation choices and reviewed decisions; where customer answers are absent, that is stated explicitly.

| Call 7 decision or question | Requirement | Design | Code | Test |
|---|---|---|---|---|
| Use Flask-Babel rather than homegrown date and string formatting | localization-001, 005 | Localization C4 component now says Flask-Babel/gettext | `eventhub/web.py`, `eventhub/i18n.py`, `translations/*` | `tests/test_part8_flask_babel.py` |
| Two release languages (English/Spanish) | localization-001, 002 | `LANGUAGE_LOCALES=en_US/es_ES` | `locales/*.json` + .po/.mo | compiled catalog parity, UI/screen coverage |
| Screens covered: home, event list/details, registration, sign-in, checkout, orders, admin, error pages | localization-002 | existing website page templates routed through `t()` | `templates/*.html`, existing Part 7 layer | Part 7 end-to-end + Part 8 scenario |
| Translations produced for course by team/AI, not approved by customer | localization-007 | gettext message catalogs separate from pricing | `translations/*`; previous `locales/*` are reference/compatibility | catalog parity test |
| Precedence: explicit reader cookie > operator configuration; ignore browser header until approved | localization-003, 004 | language resolver at Flask request boundary | `web.py:check_session_and_csrf` | cookie override and `Accept-Language` no-override tests |
| Cookie persistence; no account preference field | localization-003 | CSRF-protected `/language`, SameSite=Lax cookie | existing `set_language()` route | unchanged Part 7 tests + new scenario |
| Dates and amounts are display-only | localization-005 | C4 localization component isolated from Pricing | `i18n.local_date`, `i18n.local_money` | Spanish Babel date and JPY tests |
| Missing message => English, no missing key shown | localization-006 | fallback in i18n adapter | `i18n.translate()` | simulated missing locale entry test |
| Invalid operator setting must fail on startup | localization-008 | config validation boundary | `i18n.validate_language_setting` | startup rejection test |
| Every earlier test and Part 5 gate must keep working | all | separate named `check_part5.yml` check | workflows, tagged Gherkin | course gate, traceability, CI and Selenium |

**Scope and open requirements:** Call 7 does not name the exact geographic locale or approved browser-versus-operator precedence. We propose English (US) and Spanish (Spain), with reader cookie first and operator default second. Darnell/Marcus must approve the regional preference/translation source and decide whether to store language on accounts. Region and language are different properties. Customer data (event titles/venues) remains English; translating it would be a separate content-management feature. All payments in EventHub are simulated.

**Release boundary:** Part 8 documentation calls the future product release 1.5 for localization only. No live release, rate update, or production approval is asserted here. Before a release, verify code review by another person, tests, spec and all automatic checks as Thuy required.

## Additional written feature decisions after the independent review

- **Languages** (`localization-001`): exactly English (`en_US`) and Spanish (`es_ES`) in the classroom release candidate; no automatic browser-language detection.
- **Pages** (`localization-002`): home, search/event detail, registration, login, checkout, order/receipt, order history, administration, and error pages. Event titles/venues entered as database content are not translated.
- **Translation source** (`localization-009`): each key is mapped in `docs/part8-translation-provenance.json` to existing English team-authored text or AI-assisted Spanish draft text. Team tested, not certified by Darnell or a native speaker.
- **Choice and persistence** (`localization-003`, `-004`, `-010`): explicit language form choice in an HttpOnly/SameSite=Lax cookie, verified through CSRF on POST; otherwise operator config wins, regardless of Accept-Language header.
- **Spreadsheet irregularity** (`localization-011`, `-012`): external spreadsheet drafts are not copied straight into a release. We require review and version control, enforce key/placeholder parity, and check that compiled gettext entries agree. **Canvas discussion/TA response has not been supplied**; our question and provisional ADR are in `docs/decisions/ADR-009-translation-sources.md`.
- **Regional currency/date** (`localization-005`): Spanish uses Babel locale; English ISO date and legacy `JPY` code notation remain a documented compatibility exception pending the customer's locale policy. No stored amount/time is modified.
- **Release**: 1.5 is the proposed language-only release number, **not a deployed or tagged version**. The Part 8 PR also contains independently committed maintenance/security review fixes; this is a classroom integration PR, not evidence that a production release mixed them.

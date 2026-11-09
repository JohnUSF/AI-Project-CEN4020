# Part 6: AI-assisted simplification review and what we actually changed

**Context:** In the last teammate review, Claude's suggestions were supplied to the gold member. We checked the suggestions against the code, the Call 6 requirements and the passing test suite. The complete text of the original Claude prompt was not retained, so no exact prompt transcript is claimed here.

| Review finding | Risk and tradeoff | Decision in this final change |
|---|---|---|
| `create_app()` in `eventhub/web.py` is roughly 446 lines | Routes, session and CSRF control, and error handling live together. Splitting routes now would touch authentication/security behavior and create regression risk. | **Deferred.** Proposed future modules: authentication routes, checkout/order routes and administration routes, each registered from a small app factory. Keep CSRF/session middleware centralized. |
| `place_order()` in `eventhub/purchase.py` is roughly 138 lines | Validation, duplicate tokens, rate lookup, inventory update, order insert and audit log happen in one large transaction. An aggressive split could break atomicity or the one-order-per-click guarantee. | **Deferred.** Proposed future helpers for duplicate detection, cap checks and record construction, but retain `BEGIN IMMEDIATE` as the sole transaction owner and re-run concurrency and idempotency tests. |
| `web.py` repeats English/Spanish money and date branches | Presentation decisions are scattered across the HTTP boundary and locale adapter. Adding a third language would mean editing both places. | **Implemented.** Both template helpers call `i18n.local_money` and `i18n.local_date`. The locale module owns the English compatibility case and Babel Spanish case. No price calculation changes. |

## Evidence before and after

**Before:** `web.create_app().context` selected `str(value)` or `display_amount` for English and used `i18n` for Spanish. `i18n.local_date` formatted English using Babel when called directly, inconsistent with the template behavior.

**After:** the context passes the requested language into a single adapter for both dates and money. `i18n.local_date` returns the legacy string in English and Babel-formatted regional text in Spanish. The change removes duplicated conditional presentation logic; the database, pricing and purchase APIs are unchanged.

**New automated check:** `tests/test_call6_maintenance.py::test_locale_adapter_keeps_old_english_values_and_spanish_display` verifies English dates, unrecognized-language fallback, English zero-decimal yen text, and Spanish regional output. Existing tests protect persisted yen amounts, admin exchange-rate edits and purchase behavior.

## Human review of the AI suggestions

We deliberately did not split `create_app` or `place_order` in the final student submission. These changes would be valuable later, but they affect CSRF, login/session rules and transactional consistency. We chose a small, testable refactor that addresses a concrete duplicate responsibility rather than rewriting a stable purchase path for appearance.

## What is **not** completed by this change

English yen is still `JPY 4,500` instead of `¥4,500`; the amount/rounding are correct, but this symbol issue remains. The language toggle is a cookie preference, not detection of the reader's region, and timezone policy is not approved. A real anomaly alert recipient and a named backup operator were not provided. These are explicitly recorded as operational/product decisions in `docs/part6-release-decisions.md` and are not described as implemented.

**Verification provenance:** Before this review change, 160 unit/integration tests and 139 browser tests passed on macOS; the PR had four green GitHub Actions checks. That does not automatically verify the new refactor. Re-run `python run_all_tests.py` and GitHub checks on the revised code before marking this revision verified.

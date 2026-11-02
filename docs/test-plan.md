# Part 5 test plan: how the test cases were chosen

Thuy's structure (Call 5): unit tests on functions, integration tests on how pieces work together, end-to-end tests through the browser, Kenji's security pass, then a real user trying to break it. Part 5 adds to the first three layers and automates what it can of the rest.

| Layer | Where | Tool | Count (final run) |
|---|---|---|---|
| Unit | `tests/test_*.py` (component level) | pytest | see `report/test_dashboard.html` |
| Integration | `tests/test_web*.py`, `test_oversell_stress.py`, `test_idempotent_purchase.py` | pytest + Flask test client + threads | |
| End-to-end and edge cases | `tests_system/test_e2e_journey.py`, `test_blackbox_edges.py`, `test_whitebox_edges.py`, `test_call5_findings.py`, `test_oversell_browsers.py` | **Selenium 4, headless Chrome**, against the real app in a subprocess | |
| Load | `tests_system/test_performance.py` | plain HTTP threads (a browser would measure Chrome, not the server) | |
| Security pass (Kenji) | CSRF, open redirect, XSS echo, role checks, oversized body, headers, rate limit | spread through the layers above | |
| Real-user pass (Darnell) | not automatable | a repeat of the student-union session is listed as RISK-005 | |

## 1. Black-box edge cases (from the specification only)

Input: the EARS requirements in `features/*/requirements.md` and the Call 5 transcript. No source code was consulted to *choose* these cases. (Claude had read the code earlier in the same session, so the separation is one of method, not of knowledge. The cases below follow from the requirement text, and each cites it.)

Techniques used and what each produced:

| Technique | Applied to | Cases |
|---|---|---|
| Equivalence classes | quantity (purchase-007/010) | valid; zero; negative; non-numeric; decimal; exponent (`1e2`); padded (` 3`); empty; fullwidth digit (`２`); leading zeros; above the limit |
| Boundary values | quantity vs stock (purchase-006, inventory-003/004); quantity max (10,000/10,001); password length (9/10/256/257); name length (0/100/101) | buy exactly the remaining tickets; ask for one more; 1 ticket; 5 of 5 |
| Error guessing | currency (pricing-001) | `XYZ`, lowercase `usd`, trailing space, `BTC`, SQL text, empty |
| Error guessing | search (catalog-002/003/007/008) | `%`, `_`, `\`, SQL quote, emoji/accents, whitespace only, 5,000 characters, three XSS payloads |
| Error guessing | registration/login (identity-001/005/014) | case-variant duplicate email, HTML in name, padded/mixed-case login, wrong password vs unknown email, four open-redirect targets, tampered CSRF token |
| State | logged-out access (identity-007/010..012) | four protected URLs, forged purchase POST with no session |
| Role | admin (admin-002..005) | signed-out, buyer, forged rate POST |
| Privacy | one buyer opening another buyer's order | purchase-016 |
| Unknown pages | `/events/99999`, `/events/0`, `/events/-1`, `/events/abc`, `/nonexistent` | clean error, no traceback |

Black-box tests are tagged `@pytest.mark.blackbox`.

## 2. White-box edge cases (from reading the source)

| What the code showed | Case | Requirement |
|---|---|---|
| `compute_quote` rounds once with ROUND_HALF_UP; JPY has 0 digits | USD 1.25 in JPY is exactly 187.5, must show JPY 188 | pricing-004, pricing-008 |
| Price shown by the live estimate (JS) and charged by the server come from one function | estimate text equals the confirmation total (GBP 46.78) | pricing-007 |
| `eligible_for_usf_discount` does `partition("@")[2] == "usf.edu"` | uppercase, `+tag`, `mail.usf.edu`, `usf.edu.evil.org`, `notusf.edu`, `usf.edu@gmail.com` | pricing-011..014 |
| `DISCOUNT_PERCENT` unset makes eligible quotes raise `ConfigurationPending` | separate server with no discount: student cannot buy, stock unchanged, audit row says why; other buyers unaffected | pricing-011 |
| Rates are read inside the purchase transaction; orders store the rate | change EUR rate in the admin screen: new order uses new rate, old order keeps old | pricing-010, purchase-019 |
| `validate_rate` regex | `-1`, `0`, `abc`, `1e2`, 9 decimals, empty, 1,000,000, `1;DROP`; USD rate must stay 1 | admin-007 |
| `purchase()` audits in the `except` branch after rollback | invalid, sold out, success for one account leave exactly three rows in the right order | audit-001, audit-008 |
| `redeem` is an UPDATE ... WHERE `checked_in_at IS NULL` | same code twice; unknown code | purchase-018 |
| `PURCHASE_CAP` read from settings | separate server with cap 3: 2 + 2 refused | purchase-008 |
| `SESSION_IDLE_SECONDS` read from settings | separate server with a 3-second timeout | system-004/005 |
| `MAX_CONTENT_LENGTH` = 32 KB | 40 KB POST body returns 413 | system-002 |
| `after_request` sets headers | `X-Frame-Options`, CSP, `no-store` on signed-in pages | system-002 |
| `leave_checkout` is reached by `sendBeacon` on `pagehide` | walk away from checkout: abandoned row appears | purchase-022 |
| Checkout template had its own `endswith('@usf.edu')` | found by reading, fixed; unit test pins notice to the one rule | pricing-007 |
| `identity.register` only checked `'@' in email` | `a@b@usf.edu` and eight other malformed addresses | identity-017 |
| `/currency` route existed but nothing linked to it | header control; preferred currency drives quick-buy | identity-019 |
| `purchase.place_order` reads the buyer's email inside the transaction | change the email in the database between purchases; discount follows | pricing-015 |
| SQLite `BEGIN IMMEDIATE` + conditional UPDATE | 200 rounds of two buyers, one ticket; 30 buyers, 5 tickets; two real browsers | inventory-001 |
| `db.migrate` adds columns to an old database | a Part 4 database is upgraded and its old order still opens | purchase-030 |

White-box tests are tagged `@pytest.mark.whitebox`. Call 5 tests are tagged `@pytest.mark.call5`.

## 3. What is not tested, and why
- **purchase-015** (prevent screenshots): a website cannot. Exempt, with the reason in `grading/check_test_traceability.py`.
- **purchase-009** (student-organisation exception) and **audit-006** (retention): the customer has not defined the behaviour.
- **Real devices.** Headless Chrome at desktop size plus a 375 px layout check. No Safari, Firefox, or physical phones.
- **Back-button restore from the browser cache.** Whether it carries a stale purchase token depends on the browser; the server rule makes the outcome safe, but the exact click sequence is not automated.
- **Multi-process deployment.** The rate limiter is per process (ADR-007). Not tested because it is not claimed.
- **Real payment.** Payment is simulated by requirement purchase-012.
- **Re-test of the reworded confirmation with real students.** RISK-005.

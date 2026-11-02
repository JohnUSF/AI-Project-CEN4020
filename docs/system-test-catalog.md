# Test case catalog

Generated from the last full run (2026-11-01 15:47:15) by `scripts/build_test_catalog.py`. Do not edit by hand.
Each row is one test function; parametrized functions show how many cases they cover.
**137 browser and load cases + 144 unit and integration cases = 281.**

## Browser (Selenium) and load tests: `tests_system/`

| File | Test case | Cases | Requirements | Technique | Result |
|---|---|---:|---|---|---|
| `test_blackbox_edges.py` | invalid quantities are rejected on the server with a quantity message | 12 | purchase-007, purchase-010, purchase-011 | black-box | pass |
| `test_blackbox_edges.py` | asking for more than remain says sold out not invalid quantity | 1 | purchase-006, purchase-011, inventory-004 | black-box | pass |
| `test_blackbox_edges.py` | buying exactly the remaining tickets works and the next buyer is told sold out | 1 | purchase-004, inventory-003 | black-box | pass |
| `test_blackbox_edges.py` | buying one ticket is the smallest valid order | 1 | purchase-004 | black-box | pass |
| `test_blackbox_edges.py` | unsupported currency values are rejected whatever the browser sends | 6 | pricing-001, purchase-005, purchase-011 | black-box | pass |
| `test_blackbox_edges.py` | every supported currency can be bought in | 4 | pricing-006, pricing-001 | black-box | pass |
| `test_blackbox_edges.py` | protected pages redirect signed out visitors to login | 4 | identity-010, identity-011, identity-012 | black-box | pass |
| `test_blackbox_edges.py` | a forged purchase post from a signed out browser buys nothing | 1 | identity-007, identity-012, purchase-005 | black-box | pass |
| `test_blackbox_edges.py` | search matches artist or venue ignoring case and padding | 6 | catalog-002, catalog-003 | black-box | pass |
| `test_blackbox_edges.py` | a search with no match says so and then lists everything | 7 | catalog-007 | black-box | pass |
| `test_blackbox_edges.py` | an empty search shows the full list without a complaint | 2 | catalog-001 | black-box | pass |
| `test_blackbox_edges.py` | search text is echoed as plain text never as markup | 3 | catalog-008, system-002 | black-box | pass |
| `test_blackbox_edges.py` | a very long search term does not break the page | 1 | system-002 | black-box | pass |
| `test_blackbox_edges.py` | registration rejects bad names and passwords | 6 | identity-001, system-002 | black-box | pass |
| `test_blackbox_edges.py` | the same email cannot register twice whatever its case | 1 | identity-001 | black-box | pass |
| `test_blackbox_edges.py` | a name with html in it is stored and shown as text | 1 | identity-001, identity-015 | black-box | pass |
| `test_blackbox_edges.py` | wrong password and unknown email get the same message | 1 | identity-005 | black-box | pass |
| `test_blackbox_edges.py` | email case and padding do not stop a valid login | 1 | identity-008 | black-box | pass |
| `test_blackbox_edges.py` | sign in never sends the visitor to another site | 4 | identity-014 | black-box | pass |
| `test_blackbox_edges.py` | a tampered security token is refused | 1 | system-002 | black-box | pass |
| `test_blackbox_edges.py` | signed out visitors cannot reach the admin area | 1 | admin-002 | black-box | pass |
| `test_blackbox_edges.py` | a buyer is refused the admin pages and actions | 1 | admin-003, admin-004, admin-005 | black-box | pass |
| `test_blackbox_edges.py` | one buyer cannot open another buyers order | 1 | purchase-016, identity-007 | black-box | pass |
| `test_blackbox_edges.py` | a new buyer sees an empty order history | 1 | purchase-016 | black-box | pass |
| `test_blackbox_edges.py` | unknown pages show a clean error not a crash | 5 | catalog-001, system-002 | black-box | pass |
| `test_call5_findings.py` | double clicking the checkout button makes one order | 1 | purchase-024, purchase-027 | Call 5 | pass |
| `test_call5_findings.py` | three instant clicks from a script still make one order | 1 | purchase-024, purchase-027 | Call 5 | pass |
| `test_call5_findings.py` | triple clicking an event card makes one quick buy | 1 | purchase-024, purchase-027, purchase-001 | Call 5 | pass |
| `test_call5_findings.py` | double clicking quick buy on the event page makes one order | 1 | purchase-024, purchase-027 | Call 5 | pass |
| `test_call5_findings.py` | even with the page script bypassed the server refuses to buy twice | 1 | purchase-024, purchase-025 | Call 5 | pass |
| `test_call5_findings.py` | a purchase token cannot be reused for a different purchase | 1 | purchase-026 | Call 5 | pass |
| `test_call5_findings.py` | a purchase form without its token is refused with a reload message | 1 | purchase-028 | Call 5 | pass |
| `test_call5_findings.py` | each page view gets a new purchase token | 1 | purchase-025 | Call 5 | pass |
| `test_call5_findings.py` | a script hammering the purchase endpoint is stopped and logged once | 1 | purchase-032, audit-007, audit-008 | Call 5 | pass |
| `test_call5_findings.py` | a limited account does not stop other buyers | 1 | purchase-032 | Call 5 | pass |
| `test_call5_findings.py` | the confirmation makes the charged amount the biggest thing on the page | 1 | purchase-029, purchase-030 | Call 5 | pass |
| `test_call5_findings.py` | a dollar order does not show a second confusing amount | 1 | purchase-029 | Call 5 | pass |
| `test_call5_findings.py` | the order history page repeats the same amounts | 1 | purchase-030, purchase-019 | Call 5 | pass |
| `test_call5_findings.py` | the currency chosen at registration is visible explained and used | 1 | identity-018, pricing-016, pricing-017, identity-019, purchase-031, purchase-001 | Call 5 | pass |
| `test_call5_findings.py` | changing the currency in the header sticks on the next pages | 1 | identity-019, pricing-016 | Call 5 | pass |
| `test_call5_findings.py` | signed out visitors have no currency control | 1 | pricing-016 | Call 5 | pass |
| `test_call5_findings.py` | there is no way to change an email address from the website | 1 | identity-020 | Call 5 | pass |
| `test_call5_findings.py` | when the qualifying email goes away the next purchase is full price | 1 | pricing-015, pricing-003 | Call 5 | pass |
| `test_call5_findings.py` | known risk registering with any usf address earns the discount | 1 | pricing-011 | Call 5 | pass |
| `test_e2e_journey.py` | full journey register login search buy in euros and find it in history | 1 | identity-001, identity-008, catalog-002, catalog-004, pricing-006, purchase-004, purchase-013, purchase-016, purchase-017, purchase-029, purchase-030 | - | pass |
| `test_e2e_journey.py` | signed out checkout goes to login and returns after sign in | 1 | identity-010, identity-011, identity-013, identity-007 | - | pass |
| `test_e2e_journey.py` | signing out ends the session | 1 | identity-009, identity-007 | - | pass |
| `test_e2e_journey.py` | double clicking a card buys one ticket in the preferred currency | 1 | purchase-001, catalog-004 | - | pass |
| `test_e2e_journey.py` | home page lists every event with its ticket count | 1 | catalog-001, catalog-005 | - | pass |
| `test_e2e_journey.py` | double clicking while signed out goes to login and buys nothing | 1 | purchase-003, identity-012 | - | pass |
| `test_e2e_journey.py` | sold out quick buy names the cause and returns to the event | 1 | purchase-002, purchase-006, purchase-011 | - | pass |
| `test_e2e_journey.py` | cancelling checkout records an abandoned checkout and takes no tickets | 1 | purchase-021, purchase-020 | - | pass |
| `test_e2e_journey.py` | leaving the checkout page records an abandoned checkout | 1 | purchase-022 | - | pass |
| `test_e2e_journey.py` | the back button still works during checkout | 1 | purchase-023 | - | pass |
| `test_e2e_journey.py` | phone sized screen has no sideways scrolling | 4 | system-003 | - | pass |
| `test_oversell_browsers.py` | two browsers one ticket exactly one wins every round | 1 | inventory-001, inventory-003, inventory-004, purchase-006, audit-008 | Call 5 | pass |
| `test_performance.py` | purchase latency with concurrent buyers against the placeholder budget | 1 | system-006 | load | pass |
| `test_whitebox_edges.py` | yen has no decimals and rounds once | 1 | pricing-008, pricing-004, pricing-006 | white-box | pass |
| `test_whitebox_edges.py` | the live estimate and the final charge use the same price | 1 | pricing-008, pricing-007 | white-box | pass |
| `test_whitebox_edges.py` | usf addresses get the discount whatever their case or plus tag | 3 | pricing-011, pricing-012, pricing-013 | white-box | pass |
| `test_whitebox_edges.py` | lookalike and subdomain addresses pay the standard price | 4 | pricing-014, pricing-003 | white-box | pass |
| `test_whitebox_edges.py` | with no discount configured a student checkout stops before taking tickets | 1 | pricing-011, purchase-005, inventory-004 | white-box | pass |
| `test_whitebox_edges.py` | a rate change applies to new orders and never rewrites old ones | 1 | admin-006, pricing-010, purchase-019, audit-004 | white-box | pass |
| `test_whitebox_edges.py` | bad exchange rates are refused and the old rate stays | 8 | admin-007 | white-box | pass |
| `test_whitebox_edges.py` | the dollar reference rate cannot be changed | 1 | admin-007 | white-box | pass |
| `test_whitebox_edges.py` | every purchase attempt leaves exactly one audit row and the admin sees newest first | 1 | audit-001, audit-008, admin-008 | white-box | pass |
| `test_whitebox_edges.py` | a confirmation code checks in once and only once | 1 | purchase-018 | white-box | pass |
| `test_whitebox_edges.py` | an unknown confirmation code is refused | 1 | admin-005, purchase-018 | white-box | pass |
| `test_whitebox_edges.py` | the tickets left count on the pages drops after a purchase | 1 | catalog-005, inventory-002 | white-box | pass |
| `test_whitebox_edges.py` | the per account ticket cap counts earlier orders | 1 | purchase-008 | white-box | pass |
| `test_whitebox_edges.py` | an idle session expires and asks for sign in | 1 | identity-006, system-004, system-005 | white-box | pass |
| `test_whitebox_edges.py` | security headers and no caching of signed in pages | 1 | system-002 | white-box | pass |
| `test_whitebox_edges.py` | an oversized request body is refused | 1 | system-002 | white-box | pass |
| `test_whitebox_edges.py` | the event page shows the price in the buyers currency | 1 | pricing-006, pricing-007 | white-box | pass |

## Unit and integration tests: `tests/`

| File | Test case | Cases | Requirements | Technique | Result |
|---|---|---:|---|---|---|
| `test_admin.py` | rate change is audited | 1 | admin-006, audit-004 | - | pass |
| `test_admin.py` | invalid rate does not change database | 1 | admin-007 | - | pass |
| `test_admin.py` | unknown currency rejected | 1 | admin-007 | - | pass |
| `test_admin.py` | usd reference rate must remain one | 1 | admin-007 | - | pass |
| `test_audit.py` | audit recent returns newest first | 1 | admin-008 | - | pass |
| `test_audit.py` | audit limits untrusted detail length | 1 | audit-001 | - | pass |
| `test_catalog.py` | catalog lists all events | 1 | catalog-001 | - | pass |
| `test_catalog.py` | search matches artist or venue case insensitive | 1 | catalog-002, catalog-003 | - | pass |
| `test_catalog.py` | no match shows full list and flag | 1 | catalog-007 | - | pass |
| `test_catalog.py` | literal sql wildcards are not patterns | 1 | catalog-007, system-002 | - | pass |
| `test_catalog.py` | nonexistent event | 1 | system-002 | - | pass |
| `test_database.py` | seed is idempotent | 1 | catalog-006, inventory-002 | - | pass |
| `test_database.py` | atomic inventory constraint blocks negative counts | 1 | inventory-004 | - | pass |
| `test_database.py` | audit records newest first | 1 | admin-008 | - | pass |
| `test_eligibility.py` | email normalization and provisional domain rule | 5 | pricing-011, pricing-012, pricing-013, pricing-014 | - | pass |
| `test_eligibility.py` | empty address is not eligible | 1 | pricing-012 | - | pass |
| `test_eligibility_timing.py` | discount disappears when the qualifying email goes away | 1 | pricing-015, pricing-003 | Call 5 | pass |
| `test_eligibility_timing.py` | discount follows the email in the other direction too | 1 | pricing-015 | white-box | pass |
| `test_eligibility_timing.py` | the quote page follows the current email not a remembered result | 1 | pricing-015, pricing-011 | white-box | pass |
| `test_eligibility_timing.py` | no website route changes an email address | 1 | identity-020 | Call 5 | pass |
| `test_eligibility_timing.py` | posting an email field to the currency route does not change it | 1 | identity-020 | white-box | pass |
| `test_eligibility_timing.py` | known risk an unverified usf address is eligible | 1 | pricing-011 | Call 5 | pass |
| `test_eligibility_timing.py` | lookalike addresses pay full price through the whole purchase path | 4 | pricing-014, pricing-003 | white-box | pass |
| `test_idempotent_purchase.py` | same token twice gives one order one stock change and two audit rows | 1 | purchase-024, audit-008 | Call 5 | pass |
| `test_idempotent_purchase.py` | replaying a token for a different purchase is refused | 3 | purchase-026 | Call 5 | pass |
| `test_idempotent_purchase.py` | a token belongs to one account | 1 | purchase-024 | white-box | pass |
| `test_idempotent_purchase.py` | a form without a valid token is rejected when required | 6 | purchase-028, audit-008 | Call 5 | pass |
| `test_idempotent_purchase.py` | a duplicate does not trip the purchase limit | 1 | purchase-024 | white-box | pass |
| `test_idempotent_purchase.py` | a failed attempt leaves the token reusable | 1 | purchase-024 | white-box | pass |
| `test_idempotent_purchase.py` | two simultaneous submits of one token make one order | 1 | purchase-024, inventory-001 | Call 5 | pass |
| `test_identity.py` | registration stores hash and buyer only | 1 | identity-001, identity-002, identity-008, identity-015 | - | pass |
| `test_identity.py` | wrong password does not reveal account | 1 | identity-005 | - | pass |
| `test_identity.py` | duplicate email and short password rejected | 1 | identity-001, system-002 | - | pass |
| `test_identity.py` | admin only promoted via server method | 1 | identity-016 | - | pass |
| `test_inventory.py` | inventory decrement succeeds with enough stock | 1 | inventory-003 | - | pass |
| `test_inventory.py` | inventory rejects oversell without negative count | 1 | inventory-004 | - | pass |
| `test_oversell_stress.py` | two buyers one ticket two hundred times | 1 | inventory-001, inventory-003, inventory-004, audit-008 | Call 5 | pass |
| `test_oversell_stress.py` | many buyers few tickets sells exactly the stock | 1 | inventory-001, inventory-004 | white-box | pass |
| `test_pricing.py` | normalize usf email uppercase | 1 | pricing-012, pricing-013, pricing-014 | - | pass |
| `test_pricing.py` | integer money usd | 1 | pricing-007, pricing-008 | - | pass |
| `test_pricing.py` | jpy rounds to zero decimal places | 1 | pricing-004, pricing-008 | - | pass |
| `test_pricing.py` | eur discount single aggregate round | 1 | pricing-004 | - | pass |
| `test_pricing.py` | rate validation and no floats | 1 | admin-007, pricing-008 | - | pass |
| `test_pricing.py` | missing discount fails closed for eligible student | 1 | pricing-003, pricing-011 | - | pass |
| `test_pricing.py` | invalid discount and conversion order | 1 | pricing-004 | - | pass |
| `test_pricing.py` | invalid currency quantity | 1 | pricing-001, purchase-007 | - | pass |
| `test_pricing.py` | money format | 3 | pricing-008 | - | pass |
| `test_purchase.py` | success decrements stock and records order and audit | 1 | purchase-004, inventory-003, audit-001, audit-002 | - | pass |
| `test_purchase.py` | no hold until purchase success | 1 | purchase-020, purchase-021, inventory-005 | - | pass |
| `test_purchase.py` | invalid quantity fails without stock change and audited | 1 | purchase-007, purchase-010, purchase-011, audit-008 | - | pass |
| `test_purchase.py` | sold out still has exactly one failure audit | 1 | purchase-006, inventory-004, audit-008 | - | pass |
| `test_purchase.py` | invalid currency is rejected and audited | 1 | pricing-001, purchase-005, purchase-011 | - | pass |
| `test_purchase.py` | purchase limit combines previous orders | 1 | purchase-008 | - | pass |
| `test_purchase.py` | missing discount blocks usf order and records failure | 1 | pricing-011 | - | pass |
| `test_purchase.py` | rate snapshot not rewritten for past order | 1 | purchase-019, pricing-010 | - | pass |
| `test_purchase.py` | concurrent buys do not oversell | 1 | inventory-001, inventory-002, audit-008 | - | pass |
| `test_purchase.py` | redeem code once only | 1 | purchase-018 | - | pass |
| `test_ratelimit.py` | requests up to the limit pass and the next is refused | 1 | purchase-032 | Call 5 | pass |
| `test_ratelimit.py` | retry after counts down and the window slides | 1 | purchase-032 | Call 5 | pass |
| `test_ratelimit.py` | accounts are limited independently | 1 | purchase-032 | Call 5 | pass |
| `test_ratelimit.py` | only the first rejection of a blocked period is flagged for the audit log | 1 | audit-007 | Call 5 | pass |
| `test_ratelimit.py` | hammering does not extend the block | 1 | purchase-032 | Call 5 | pass |
| `test_ratelimit.py` | a zero setting turns the limiter off | 3 | purchase-032 | white-box | pass |
| `test_requirement_gaps.py` | the application is a flask application | 1 | system-001 | - | pass |
| `test_requirement_gaps.py` | each component imports on its own without the web layer | 11 | system-007 | - | pass |
| `test_requirement_gaps.py` | the shared workflow runs the tests and the system suite | 1 | system-008 | - | pass |
| `test_requirement_gaps.py` | a test without a requirement tag is refused at collection | 1 | system-009 | - | pass |
| `test_requirement_gaps.py` | the admin area shows rates and audit log to administrators only | 1 | admin-001, audit-005 | - | pass |
| `test_requirement_gaps.py` | prices follow the rate stored in the database with no outside provider | 1 | pricing-009, pricing-010 | - | pass |
| `test_requirement_gaps.py` | payment is simulated and no payment or email service is wired in | 1 | purchase-012, purchase-014 | - | pass |
| `test_requirement_gaps.py` | run py builds the same application the system tests start | 1 | system-001, system-007 | - | pass |
| `test_web.py` | home responsive and xss escaped | 1 | catalog-008, system-003, system-002 | - | pass |
| `test_web.py` | anonymous checkout redirect and no records | 1 | identity-007, identity-010, identity-012 | - | pass |
| `test_web.py` | no open redirects | 1 | identity-014 | - | pass |
| `test_web.py` | logged out admin denied | 1 | admin-002 | - | pass |
| `test_web.py` | buyer cannot manage rates or view admin | 1 | admin-003, admin-004, admin-005 | - | pass |
| `test_web.py` | checkout to order with correct locking | 1 | purchase-004, purchase-013, audit-001 | - | pass |
| `test_web.py` | csrf missing rejected | 1 | system-002 | - | pass |
| `test_web.py` | login return and session expiry | 1 | identity-006, system-005 | - | pass |
| `test_web.py` | admin can change rate | 1 | admin-006 | - | pass |
| `test_web.py` | anonymous quick buy returns to event not post only route | 1 | purchase-003, identity-012 | - | pass |
| `test_web.py` | quote uses single price service | 1 | pricing-006, pricing-007 | - | pass |
| `test_web.py` | quote blocks invalid currency | 1 | pricing-001 | - | pass |
| `test_web_call5.py` | checkout without a token is refused and logged | 1 | purchase-028 | Call 5 | pass |
| `test_web_call5.py` | pressing buy twice with one form makes one order | 1 | purchase-024 | Call 5 | pass |
| `test_web_call5.py` | quick buy pressed three times makes one order | 1 | purchase-024 | Call 5 | pass |
| `test_web_call5.py` | reusing a token for another event is refused | 1 | purchase-026 | Call 5 | pass |
| `test_web_call5.py` | every purchase form gets its own fresh token | 1 | purchase-025 | Call 5 | pass |
| `test_web_call5.py` | two hundred requests a minute are stopped and logged once | 1 | purchase-032, audit-007 | Call 5 | pass |
| `test_web_call5.py` | one account being limited does not block another | 1 | purchase-032 | Call 5 | pass |
| `test_web_call5.py` | a validation failure still counts toward the limit | 1 | purchase-032 | white-box | pass |
| `test_web_call5.py` | foreign currency confirmation says what was charged | 1 | purchase-029 | Call 5 | pass |
| `test_web_call5.py` | dollar confirmation has no conversion noise | 1 | purchase-029 | Call 5 | pass |
| `test_web_call5.py` | student confirmation shows the discount and the charge | 1 | purchase-029, pricing-011 | Call 5 | pass |
| `test_web_call5.py` | order history detail uses the same wording | 1 | purchase-030 | Call 5 | pass |
| `test_web_call5.py` | a part4 database is upgraded and its old orders still open | 1 | purchase-019, purchase-030 | white-box | pass |
| `test_web_call5.py` | header shows the preferred currency on every signed in page | 4 | pricing-016 | Call 5 | pass |
| `test_web_call5.py` | signed out visitors see no currency control | 1 | pricing-016 | Call 5 | pass |
| `test_web_call5.py` | registration stores the chosen currency | 1 | identity-018 | Call 5 | pass |
| `test_web_call5.py` | registration rejects a currency that is not supported | 1 | identity-018 | white-box | pass |
| `test_web_call5.py` | a changed preferred currency is what quick buy uses | 1 | identity-019, purchase-001 | Call 5 | pass |
| `test_web_call5.py` | checkout says which currency you will be charged in and why | 1 | pricing-017 | Call 5 | pass |
| `test_web_call5.py` | the home page names the currency a double click will use | 1 | purchase-031 | Call 5 | pass |
| `test_web_call5.py` | the pending discount notice uses the same rule as pricing | 1 | pricing-011, pricing-007 | white-box | pass |
| `test_web_call5.py` | malformed email addresses create no account | 9 | identity-017 | black-box | pass |

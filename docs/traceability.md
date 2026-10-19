# Traceability: Part 2 requirements to the repository IDs

Part 2 numbered requirements REQ-1 to REQ-39 in one list. After Call 3 they live in feature folders that follow the component design. IDs are never reused.

| Part 2 | Now | Note |
|---|---|---|
| REQ-1 | identity-001 | |
| REQ-2 | identity-002 | |
| REQ-3 | identity-003, superseded by pricing-002 | discount eligibility moves to the pricing component |
| REQ-4 | identity-004, superseded by pricing-003 | same |
| REQ-5, 6, 7 | identity-005, 006, 007 | |
| REQ-8, 9, 10, 11 | catalog-001, 002, 003, 004 | |
| REQ-12, 13 | purchase-001, 002 | |
| REQ-14 | catalog-005 | |
| REQ-15 | inventory-005 | |
| REQ-16, 17, 18, 19, 20 | purchase-006, 007, 008, 009, 010 | |
| REQ-21 | pricing-001 | |
| REQ-22 | pricing-005, superseded by pricing-009 | rates move from a file to the database (Call 3) |
| REQ-23 | purchase-012 | |
| REQ-24 | pricing-004 | |
| REQ-25, 26, 27, 28, 29, 30 | purchase-013, 014, 015, 016, 017, 018 | |
| REQ-31 | audit-001 | |
| REQ-32 | purchase-011 | |
| REQ-33 | system-003 | |
| REQ-34 | system-004 | |
| REQ-35 | not a requirement | UX goal, under two minutes for a purchase. No "shall", so it is not an EARS line. |
| REQ-36 | system-001 | |
| REQ-37 | inventory-001 | |
| REQ-38 | system-002 | |
| REQ-39 | catalog-006 | |

## New after Call 3
- Admin area: admin-001 to admin-008; identity-015, identity-016 (roles); audit-004 (rate changes logged).
- Signed-out access to checkout and order history: identity-010 to identity-014; purchase-003.
- Search with no result: catalog-007, catalog-008.
- Pricing in one place, money as whole units, rates from the database: pricing-007, 008, 009, 010.
- Inventory and audit in the purchase path: inventory-002, 003, 004; audit-002, 003; purchase-005.
- Abandoned checkouts: purchase-019 to purchase-023.
- Session timeout as a setting; performance placeholder: system-005, system-006.

## Gaps found while splitting the work into components (not from Call 3)
- identity-008, identity-009: sign-in and sign-out had no positive requirement (Part 1 FR-6 asked for them).
- pricing-006: Call 1 said buyers pick a currency and we display and charge in it. Part 2 only had the validation rule.
- purchase-004: no requirement for the basic act of submitting a quantity and completing checkout (Part 1 FR-12).

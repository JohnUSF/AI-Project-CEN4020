# Open items (nothing here was guessed)

Q numbers 1 to 11 come from Part 1. Q12 onward are new in Part 3. All of these stay marked [TBD] in the requirements.

| Q | Open item | Where it shows up |
|---|---|---|
| Q1 | USF discount amount | pricing-002 |
| Q2 | USF discount scope (USF events only or every event) | pricing-002 |
| Q3 | @usf.edu email verification method | no requirement yet |
| Q4 | Order confirmation by email | closed for v1 by Call 2 (on-screen only) |
| Q5 | Ticket hold or no hold during checkout | inventory-005 |
| Q6 | Purchase cap number and student-organization exception | purchase-008, purchase-009 |
| Q7 | Final supported currency list | pricing-001 |
| Q8 | Discount before or after conversion, and the rounding rule | pricing-004 |
| Q9 | Exact meaning of "real-time" availability | catalog-005 |
| Q10 | Door check-in mechanism to stop a confirmation being reused | purchase-018 |
| Q11 | Session idle timeout (Kenji suggested 30 minutes, Marcus disputed it, no decision). Held as a setting. | system-004 |
| Q12 | How administrators search or filter the audit log | admin-008 |
| Q13 | Peak load and response-time target (Marcus is getting sales data) | system-006, ADR-001 |
| Q14 | Which people hold the administrator role and who reads the audit log | ADR-003, ADR-004 |
| Q15 | Where a visitor lands after signing in from a quick-buy attempt (must not buy automatically) | purchase-003 |

## Other notes
- purchase-015 (prevent screenshots) was asked for by Darnell. A website cannot reliably block screenshots, so this can be tested only as a best effort. Worth raising with the TA.
- Audit log retention and whether records can ever be edited were not discussed in any call.
- Out of scope for v1: native iPhone app, venue seat map.

# Open items (nothing here was guessed)

Q numbers 1 to 11 come from Part 1. Q12 onward are new in Part 3. Items are either pending, provisionally assumed, or reported resolved in emails not provided with this submission. The list preserves original Q IDs and distinguishes these statuses.

| Q | Open item | Where it shows up |
|---|---|---|
| Q1 | USF discount amount | pricing-011 |
| Q2 | USF discount scope (reported settled by Call 4; actual email wording needed) | pricing-011 |
| Q3 | @usf.edu email verification method | identity-001 and customer approval still needed |
| Q4 | Order confirmation by email | Call 2 said on-screen only; Call 4 says confirmation was settled in later emails, not provided |
| Q5 | Ticket hold or no hold during checkout (reported settled by emails; text unavailable) | inventory-005 [provisional no-hold behavior] |
| Q6 | Purchase cap number and student-organization exception (reported settled by emails; text unavailable) | purchase-008, purchase-009 |
| Q7 | Final supported currency list | pricing-001 |
| Q8 | Discount before or after conversion, and the rounding rule | pricing-004 |
| Q9 | Exact meaning of "real-time" availability | catalog-005 |
| Q10 | Door check-in mechanism to stop a confirmation being reused | purchase-018 |
| Q11 | Session idle timeout (Kenji suggested 30 minutes, Marcus disputed it, no decision). Held as a setting. | system-004 |
| Q12 | How administrators search or filter the audit log | admin-008 |
| Q13 | Peak load and response-time target (Marcus is getting sales data) | system-006, ADR-001 |
| Q14 | Which people hold the administrator role and who reads the audit log | ADR-003, ADR-004 |
| Q15 | Where a visitor lands after signing in from a quick-buy attempt (must not buy automatically) | purchase-003 |
| Q16 | Audit retention duration, deletion policy and legal constraints: newly raised by Call 4; administrator read is already restricted | audit-005, audit-006, `eventhub/audit.py` |
| Q17 | Email plus-tag and subdomain rules; provisional policy allows name+alias@usf.edu, excludes @mail.usf.edu (not customer-approved) | pricing-011–014, `eventhub/eligibility.py` |


## Other notes
- purchase-015 (prevent screenshots) was asked for by Darnell. A website cannot reliably block screenshots, so this can be tested only as a best effort. Worth raising with the TA.
- Audit log retention and whether records can ever be edited were not discussed in any call.
- Out of scope for v1: native iPhone app, venue seat map.

## Call 4 status clarifications (as of this review revision)

- **Reported resolved in customer emails, contents unavailable:** Q2 scope, Q4 confirmation, Q5 holds and Q6 caps. We cannot change the product rule to an unknown answer; these are blocked pending the actual email text, not settled in this package.
- **Explicitly unresolved in Call 4:** Q1 discount percentage. The prototype refuses to invent a student discount rate.
- **Provisional model assumptions pending approval:** plus-tag `NAME+ALIAS@USF.EDU` is eligible after case normalization, but `@mail.usf.edu` is not; Q17 is not a customer decision.
- **Call 4 adds a privacy question:** Q16 audit retention remains unspecified. Existing admin-only access is enforced; deletion is deliberately not implemented until a retention policy is approved.

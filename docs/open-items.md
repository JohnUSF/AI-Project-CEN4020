# Open items (nothing here was guessed)

Q numbers 1 to 11 come from Part 1. Q12 to Q17 came from Parts 3 and 4. **Q18 to Q21 are new in Part 5.** Items are either pending, provisionally assumed, or reported resolved in emails not provided with this submission. The list preserves original Q IDs and distinguishes these statuses.

| Q | Open item | Where it shows up | Status after Part 5 |
|---|---|---|---|
| Q1 | USF discount amount | pricing-011 | open; the build refuses to invent one. Demo servers set `EVENTHUB_DISCOUNT_PERCENT=10` as a labelled test value |
| Q2 | USF discount scope (reported settled by Call 4; email wording needed) | pricing-011 | open |
| Q3 | @usf.edu email verification method | identity-001, **RISK-001** | open since Part 1, now the root of Kenji's finding 1 |
| Q4 | Order confirmation by email | purchase-014 | open (on-screen only) |
| Q5 | Ticket hold or no hold during checkout (reported settled; text unavailable) | inventory-005 | provisional no-hold behaviour |
| Q6 | Purchase cap number and student-organization exception | purchase-008, purchase-009 | open; cap works when `EVENTHUB_PURCHASE_CAP` is set |
| Q7 | Final supported currency list | pricing-001 | open |
| Q8 | Discount before or after conversion, and the rounding rule | pricing-004 | open |
| Q9 | Exact meaning of "real-time" availability | catalog-005 | open |
| Q10 | Door check-in mechanism | purchase-018 | open; admin one-time check-in exists |
| Q11 | Session idle timeout | system-004 | held as a setting (default 1800 s) |
| Q12 | How administrators search or filter the audit log | admin-008 | open |
| Q13 | Peak load and response-time target | system-006, ADR-001, RISK-003 | **still open; Call 5 asked Marcus for one sentence.** We measured instead (see report). The load test judges against a team placeholder, not a requirement |
| Q14 | Who holds the administrator role | ADR-003, ADR-004 | open |
| Q15 | Where a visitor lands after signing in from a quick-buy attempt | purchase-003 | open |
| Q16 | Audit retention, deletion policy, legal constraints | audit-005, audit-006 | open |
| Q17 | Email plus-tag and subdomain rules | pricing-011..014 | provisional, not customer-approved |
| **Q18** | May buyers change their email address, and must a changed address be verified? What happens to the discount when the qualifying email goes away? | identity-020, pricing-015, ADR-008, RISK-001 | **new.** Today there is no email-change feature; discount follows the current email |
| **Q19** | How many purchase requests per account per window are too many? | purchase-032, ADR-007, RISK-002 | **new.** Provisional 20 per 60 s |
| **Q20** | Confirm that a repeated buy returns the original order (not an error, not a second order) | purchase-024..028, ADR-006, RISK-004 | **new.** Implemented as the team's proposal |
| **Q21** | Should the preferred currency come from registration, from the browser locale, or be asked at first purchase? | identity-018, identity-019, pricing-016 | **new.** Implemented: choose at registration (USD preselected), visible and changeable in the header |

## Other notes
- purchase-015 (prevent screenshots) was asked for by Darnell. A website cannot reliably block screenshots, so this can be tested only as a best effort. It is exempt in the traceability check with that reason.
- Audit log retention and whether records can ever be edited were not discussed in any call.
- Out of scope for v1: native iPhone app, venue seat map. Darnell: "Tell Marcus the students still want an app."

## Call 5 status clarifications
- **Customer sign-off still needed:** Q18 to Q21, plus the Part 4 items above. Nothing in Part 5 was decided on the customer's behalf except where a row says "provisional".
- **Call 5 exit criteria** (Thuy): requirement-linked tests pass (yes, see report); Kenji's two findings fixed or formally accepted (**not yet signed**, see `docs/risk-register.md`); confirmation page reworded (done, not re-tested with students); double-purchase behaviour defined and tested (done, awaiting Q20); performance sentence exists (**no, Marcus owes it**).

## Call 6 maintenance items (not customer-approved)

| Q | Open item | Current prototype choice | Required owner |
|---|---|---|---|
| Q22 | Alert threshold for anomalous purchase totals | Compare current charged total to expected stored-rate total; flag deviation over 25% (configurable) | Marcus / Kenji |
| Q23 | Who is paged, when, and by which system | Alerts persist in SQLite and appear for admins; SMTP requires an explicit recipient, relay and scheduled job. **No named human recipient or staffed rotation is assigned** | Darnell / operations |
| Q24 | Reader region, locale preference, timezone and translated content approval | Explicit en/es cookie preference only; no browser-region detection, no timezone conversion. English yen uses `JPY 4,500` instead of `¥4,500`; Spanish uses Babel | Darnell / product |
| Q25 | Backup operator, frequency, retention, secure storage and drill | Call 6 requested an owner **by Friday**; no named person was provided by the assignment or team evidence. On-demand SQLite backup exists, but owner, schedule, offsite copy and drill **are not assigned** | Kenji / operations to name owner (OVERDUE for production) |
| Q26 | Exact release orchestration and rollback acceptance | Documented rollback-first procedure and release-source snapshot; no actual production switch is claimed | Priya / operations |

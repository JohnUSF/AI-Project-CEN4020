# Risk register (Call 5 exit criteria)

Thuy's exit criteria: both of Kenji's findings must be **fixed or formally accepted as risks**. Kenji: "my two findings block release."

**Nothing in this file has been accepted by anyone yet.** "Formal acceptance" needs a named person to sign. The rows below are written so the right people can sign or reject them. Until then each risk is *open* and, by Kenji's rule, release is blocked.

| ID | Finding | What we did | Residual risk | Proposed decision | Owner to sign | Status |
|---|---|---|---|---|---|---|
| RISK-001 | Discount outlives the qualifying email (Kenji 1) | Could not reproduce: eligibility is judged from the current email at every price (ADR-008, `pricing-015`, tests). No email-change feature exists (`identity-020`). | Anyone can register with any `@usf.edu` address and get the discount: nobody verifies mailbox ownership (Q3). Customer's budget exposure is unquantified. | Customer chooses: (a) accept for the pilot and re-check after the first weeks of real use, or (b) fund a confirmation-link step. Email-change policy Q18 decided at the same time. | Darnell (customer), Kenji (security) | OPEN |
| RISK-002 | No limit on purchase request speed (Kenji 2) | Per-account sliding-window limiter, 429 + wait time, one audit entry per blocked period (ADR-007). Tested at unit, HTTP and browser level. | Numbers are placeholders (Q19). Limiter is per process and resets on restart. One person with many accounts is not slowed. Login attempts are not limited. | Accept the placeholders for launch if Kenji agrees the residual risks are tolerable; ask Marcus for the real number with the performance sentence. | Kenji (security), Marcus (product) | OPEN, partly fixed |
| RISK-003 | No performance target (Thuy) | Load measurement exists (`tests_system/test_performance.py`) and reports p50/p95/max. It judges against a **team placeholder**, not a requirement. | We cannot say pass or fail against a customer number because none exists (Q13). | Marcus supplies the sentence in the form of `system-006`. Until then performance is reported, not approved. | Marcus (product) | OPEN |
| RISK-004 | Double purchase behaviour was undefined (Thuy) | Defined as ADR-006 and `purchase-024`..`028`; tested at all three layers. | The definition (original order is shown again) was chosen by the team and has not been confirmed by the customer (Q20). | Customer confirms or changes the rule; tests follow the requirement. | Darnell (customer), Thuy (QA) | OPEN, implemented |
| RISK-005 | Confirmation page confused students (Darnell) | Reworded: amount charged is the largest figure, all other amounts labelled "reference only", rate and discount shown. Automated checks on wording and font size. | Nobody has re-tested with real students. Wording passes our tests, which cannot judge whether it feels "sketchy" to a person. | Repeat Darnell's student-union session with the new page before go-live. | Darnell (customer) | OPEN, implemented |

## Call 6 additional production-maintenance risks (all open)

| ID | Risk and current mitigation | Outstanding decision / owner | Status |
|---|---|---|---|
| RISK-006 | Decimal formatting regression could undercharge JPY. Kept charge calculation separate from Babel/UI and added exact four-currency purchase tests. | Priya and Thuy review regression release evidence | OPEN until reviewed |
| RISK-007 | Audit data is recorded but previously unmonitored. Added durable flagged-order queue, admin screen and optional SMTP CLI. | Darnell appoints on-call human and confirms thresholds Q22/Q23 | OPEN - no notification rotation |
| RISK-008 | SQLite file can be lost. Added checksum-verified backup and guarded offline restore utilities. | Kenji appoints backup owner, frequency, offsite copy and recovery drill Q25 | OPEN |
| RISK-009 | Spanish translations are student-authored; dates use event-local time without an approved timezone rule. | Darnell approves translation / locale / timezone Q24 | OPEN |
| RISK-010 | No actual production release pipeline or rollback infrastructure was supplied. | Priya validates real host and release mechanism Q26 | OPEN |

# Part 8 - pinned AI review and team decision record (final decisions)

**Agent:** GitHub Copilot Fusion in VS Code.  **Skill:** `code-review-and-quality` from `addyosmani/agent-skills`, commit `301b02b12bff98e4688e6984af6556802322bbde`.  **Review range:** Part 5 baseline `cc73d4f5b85bd269e122438c7d8e450e70f0b279` to initial Part 8 `4f037f342a35148712603242e040fa3b407cb82a` (the release 1.4 corrections plus the Spanish/Flask-Babel interface).  **Implementation fixes:** `dbebb636a200b6067bc2ef228f6cb3cdbd09930a`.

The agent performed one **read-only** review on November 19, 2026. As confirmed by Jai, John approved the four team decisions below. The separate first-person statements are **short decision summaries for the report, not verbatim quotations or signed GitHub review comments**. The pending *customer* choices are not represented as John approving production specifications.

## One row per skill finding (Call 7 format)

| Check | Severity | File and line | Decision | Reason |
|---|---|---|---|---|
| correctness | Required | `eventhub/backups.py:96` | **accepted** | Jai: This can affect a restored database, so I kept the fail-closed check and regression tests. John: The restore needs to be safe before we submit, and the two sidecar tests make this easier to check. |
| security | Required | `scripts/check_order_anomalies.py:59-64` | **accepted** | Jai: We should not let the notifier send credentials without encryption; I kept the STARTTLS guard. John: I agree with rejecting insecure SMTP settings instead of silently sending a login. |
| correctness | Required | `templates/checkout.html:2; login.html:2; register.html:2; order.html:3,10` | **accepted** | Jai: These strings should go through the same catalog as the rest of the interface, without changing old English wording. John: The catalog fix is small and tested, and it helps us avoid missing translations later. |
| correctness | Optional | `eventhub/i18n.py:144` | **rejected** | Jai: I want to keep the older English display test stable until the customer confirms the format change. John: I agree this should be a separate reviewed change because it alters the established receipt display contract. |

### Corrections and regression evidence

| Finding | Actual correction | Regression evidence |
|---|---|---|
| SQLite sidecars | Offline restore refuses destination WAL/SHM leftovers before replacement | `tests/test_review_followups.py`, two suffix cases |
| SMTP | Reject authenticated send without STARTTLS; verify TLS settings before login | `tests/test_review_followups.py`, one negative case |
| Catalog bypass | Replace seven hard-coded English strings with catalog lookups, preserving wording | `tests/test_review_followups.py`, one catalog/template case |
| Yen symbol | No source change; explicit compatibility exception until Darnell/Marcus approve the regional display requirement | Existing pricing/yen regression tests; documented open item |

### Five review axes, including no-finding axes

- **Correctness:** restore safety, catalog consistency and the optional English yen compatibility issue were recorded; the first two were corrected.
- **Readability:** inspected changed code and templates; **no distinct new readability finding** returned by the pinned pass.
- **Architecture:** inspected the Flask-Babel-to-pricing boundary; **no distinct new architecture finding** returned by the pinned pass.
- **Security:** insecure SMTP credential use identified and corrected.
- **Performance:** no independent performance finding in the pinned pass. A *later* CI measurement exceeded a **customer-unapproved** 500 ms p95 placeholder once and passed on one rerun; this is a known stability risk, not a performance guarantee.

The four findings did **not** directly change the release 1.4 display fix; the yen notation was the display-related exception carried forward from previous work. The language feature and the three maintenance/security corrections are separately identified in the PR/release documentation.

### Three Call 7 review lists

1. **Problems the review caught that our team had not addressed:** stale SQLite sidecar restore, authenticated SMTP without TLS, and English strings bypassing gettext. All three were corrected and given regression coverage.
2. **False positives:** no confirmed false positive among the four findings in the actual pinned review. Earlier candidate warnings about the CSRF-protected language cookie and translation JSON changing purchase totals were checked and not treated as proven defects. We do **not** fabricate a false-positive count.
3. **Problems or gaps the review did not solve:** cookie/regional customer policy and native Spanish translation validation; the independent translation-draft placeholder/import hazard; historic feature folders lacking local Gherkin; a repeatable approved p95 budget; owner/recipient of operational alerts. We addressed the Gherkin and draft-validation documentation/testing gaps after this review. Other customer questions remain open.

### Kenji's three safeguards (explicitly applied)

1. **Read-only agent:** Copilot inspected code and Git history, but a person selected and applied every source change.
2. **No secrets in agent config:** credentials were not added to the installed skill or agent settings; SMTP test uses synthetic values.
3. **Pinned and identified skill:** the reviewer was Copilot Fusion and the skill commit was fixed to `301b02b12bff98e4688e6984af6556802322bbde`, recorded alongside these findings.

**Verification:** Jai's Mac full suite on the reviewed fix commit passed **199 unit/integration + 140 Selenium/system = 339 tests**. GitHub PR quality, eligibility, and system checks passed; the initial push p95 placeholder failure passed on one rerun. The follow-up documentation and scenario additions in this final candidate still need a fresh complete run and a green default-branch check before Canvas submission. See `report/PART8_FINAL_VERIFICATION.md`.

**Team approval provenance:** Jai reports that he and John agreed to all four decisions. GitHub PR #5 currently remains open according to the last direct status check; this report does not invent a merge SHA or a signed GitHub approval.

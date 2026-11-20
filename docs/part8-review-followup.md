# Pinned AI review follow-up — proposed corrections (human acceptance pending)

**Review scope:** Part 5 `cc73d4f5b85bd269e122438c7d8e450e70f0b279` → Part 8 `4f037f3`.
**Reviewer:** Copilot using the installed `code-review-and-quality` skill pinned at
`301b02b12bff98e4688e6984af6556802322bbde`. This follow-up records a
**proposed developer patch**, not a completed human review.

| Finding | Proposed action in this patch | Jai decision and reason | John decision and reason |
|---|---|---|---|
| Required: stale SQLite WAL/SHM on offline restore | Refuse restore without deleting/mixing sidecars; regression tests for each suffix | Pending | Pending |
| Required: SMTP authentication without transport encryption | Reject authenticated sends without STARTTLS, use verifying SSL context, check missing password; regression test | Pending | Pending |
| Required: hardcoded English UI messages | Route seven prose strings through gettext in four templates, updating the English PO/MO and JSON catalogs with exact legacy wording; regression test | Pending | Pending |
| Optional: English yen symbol | Deferred; compatibility/product approval needed before modifying amount display | Pending | Pending |

## Three lists for Discussion #7 (verify with the team)

1. **Candidate missed problems identified by the pinned review:** WAL/SHM guard,
   SMTP TLS before credentials, catalog bypass for English UI. Whether these were
   unknown to the team must be confirmed by Jai and John.
2. **False positives:** no *new* false positives were proven in the review output;
   the review described older dismissed concerns (language-cookie authorization,
   JSON catalog pricing effects). The team must confirm its final classification.
3. **Known issues outside or unresolved by the review:** English yen display
   contract, native-speaker localization approval, named backup/alert ownership,
   production readiness and final CI status. Do not call them implemented.

## To finish

- [ ] Jai reviews and makes an accept/reject decision with reason for each finding.
- [ ] John independently reviews the findings and confirms the decisions.
- [ ] Accepted fixes are applied on a Part 8 feature branch (not `main`).
- [ ] Run `python run_all_tests.py` and `bash scripts/verify_part8_mac.sh` on final files.
- [ ] Check GitHub quality and Part 5 eligibility workflows on exact final SHA.
- [ ] Update Part 8 PDF report with 335 previous tests vs **actual final run** results.
- [ ] Get PR reviewed and merged only after gates pass.

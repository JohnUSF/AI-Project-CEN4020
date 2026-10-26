# Response to John's Part 4 review

This is an actionable review ledger for the Gold-member branch. None of these corrections are represented as having been approved or merged by John.

| Finding from John | File-level corrective action | Verification |
|---|---|---|
| EARS no email normalization | `pricing-002` marked superseded; `pricing-011`–`014` added with correct links | `check_ears`, `check_supersedes`, whole Part 3 gate |
| Missing Eligibility C4 component | `workspace.dsl` Eligibility component, Pricing → Eligibility and `Part4Components` view; PNG/SVG rendering | Diagram image; DSL static checker |
| Audit admin access & retention absent | `audit-005/006`, `docs/open-items.md` Q16 | EARS gate and admin/audit tests |
| Plus aliases/subdomains ambiguous | Explicit **provisional** yes/no policy in new requirements and code; Q17 unapproved | `test_eligibility.py` |
| Unchanged trace/open items | Additive `docs/part4-traceability.md`; updated open-items; old mappings kept | Manual review |
| AI process vague | Component-contract format, prompt recipes carefully labeled as reconstructions, original Mac traceback, before/after code, review evidence | `docs/ai-process-log.md` |
| Old 33 passed / stale modules | Re-run local suite, include updated numbers and environment scope | `report/local_test_results.txt` |
| AI tool attribution | Part 4 ChatGPT; Part 3 Claude remain correctly credited | Report, process log |
| Reviewer placeholders in draft | Rewrite report as final **review-ready submission narrative**, factual status of John review | New PDF/DOCX |
| Missing Ruff formatting check | Add `ruff format --check` in hook and GitHub Actions; provided fix-and-verify uploader runs `ruff format` on Mac | Full CI required before merge; formatter unavailable offline |
| Four boxes not codified | `CONTRIBUTING.md` review+tests+spec+CI | Checklist |
| No separate inventory / audit tests | `tests/test_inventory.py`, `tests/test_audit.py`, and eligibility tests | Pytest |
| Explicit hashing fix undocumented | Mac failure evidence + PBKDF2 code diff | Report + log |
| README stale | Append Part 4 entry to root README; update `PART4_README.md` | Readme audit |
| CI not enforced | Explain branch ruleset requirement; **John must enable it** | Manual repo administration |

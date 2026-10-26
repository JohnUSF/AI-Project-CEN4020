# Teammate review checklist — John (Part 4)

Review this as a **separate draft**; your original Part 3 repo files were not edited or pushed.

- [ ] Verify that original requirements, ADRs, DSL and diagrams remain byte-for-byte compatible with Part 3.
- [ ] Review and supply the customer email decisions cited in Call 4; update pending policies before final grading.
- [ ] Set up Python virtual environment (`requirements-dev.txt`) and run `python -m pytest -q`; **zero skipped tests required** before claiming full verification.
- [ ] Run `python grading/check_part3.py .` and (if available) Structurizr CLI validation.
- [ ] Register/login/logout, browse/search, open detail, simulate checkout, inspect history; check mobile widths.
- [ ] Test admin access/denial, rates, audit, single-use check-in and CSRF enforcement.
- [ ] Confirm the branch pipeline completes successfully; require CI via GitHub branch protection/rulesets.
- [ ] Review the AI development narrative in `report/` and add any additional observed corrections from review.
- [ ] Do not merge until code review, tests, updated requirement alignment and automatic checks are green.
- [ ] Keep the existing shared repository intact unless both teammates agree on final integration.

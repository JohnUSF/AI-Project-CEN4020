# Part 8 - verified test evidence and release-gate status

**Date of observed Mac full run:** November 19, 2026; report timestamp from screenshot `2026-11-19 23:07:49`.  
**Source SHA on GitHub:** `dbebb636a200b6067bc2ef228f6cb3cdbd09930a`, branch `part8-jaideep-gold`; PR https://github.com/JohnUSF/AI-Project-CEN4020/pull/5.

| Stage | Actual evidence |
|---|---|
| Python compilation | Pass |
| Ruff lint | Pass |
| Ruff format | Pass, 60 Python files already formatted |
| Unit/integration | **199 passed** |
| Selenium/system | **140 passed** |
| Full result | **339 tests passed, 0 failed** |
| Course Part 3 eligibility | ELIGIBLE for grading |
| Requirement/test traceability | 0 failures |
| Part 8 tagged scenarios | 8 requirements, 5 tagged scenarios, no gaps |
| GitHub PR checks | quality and system-tests passed |
| GitHub push checks | quality and eligibility passed; system-tests passed on rerun |

**Performance caveat:** The first GitHub push system-test run failed the p95 placeholder load benchmark: 639.8 ms measured vs 500 ms team-chosen limit. It processed 100 purchases with no order failures. The retried run was green. This does not demonstrate consistent production performance, and the 500 ms threshold is **not a customer-approved requirement (Q13)**.

**Provenance:** These are observed screenshots and PR status, not a fabricated local test-run JSON. Images: `part8_mac_339_passed.png`, `part8_ci_successful_rerun.png`, `part8_ci_first_latency_failure.png`. Older saved files such as `last_run.json` and `test_dashboard.html` may be historical from Part 7 and should not be cited as Part 8 proof.

**Team decisions:** Jai reports John agreed with the four accept/reject findings, documented in `docs/part8-team-signoff.md`. **Not yet verified:** final merged-main commit, expanded scenario tests, customer locale/performance policy.

**Important later changes:** This record describes the observed 339-test run at `dbebb63` and does not include the newly added legacy Gherkin/scenario and catalog-governance tests. The expanded candidate must be rerun on a Mac/GitHub before the total can be updated. No result for those added tests has been invented.

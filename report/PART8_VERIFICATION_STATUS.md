# Part 8 verification status — NOT YET A FULL PASS

Authoring snapshot: 2026-11-19. Based on merged Part 7 project ZIP.

| Check | Status |
|---|---|
| Python source compiles | PASS (local authoring sandbox, `python -m compileall`) |
| Part 3 EARS / C4 course checker | PASS, `grading/check_part3.py .` |
| Requirement-to-test traceability | PASS, `grading/check_test_traceability.py .` (0 failures) |
| Part 8 adjacent Gherkin tags | PASS, `python scripts/check_part8_scenarios.py` |
| Compiled gettext catalogs available | PASS, manual Babel library read of en_US/es_ES `.mo` |
| Full unit + integration tests | **NOT RUN** on the new code in the authoring environment (Flask and pytest-bdd unavailable) |
| Full Selenium suite | **NOT RUN** on the new code (Chrome/Selenium dependencies unavailable) |
| GitHub `quality.yml` and named `check_part5.yml` | **NOT RUN** on a Part 8 commit yet |
| Human team review + pinned skill install on Mac | **PENDING** |

The old saved Part 7 record reports 182 + 140 = 322 passes for the earlier version only. A green record for Part 7 must never be represented as a Part 8 test result. Use `bash scripts/verify_part8_mac.sh` and update the report with the actual output before Canvas submission.

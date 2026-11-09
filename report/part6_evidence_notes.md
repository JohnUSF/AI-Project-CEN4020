> **Historical development note (November 8).** This note describes the early offline assembly period, not the later verified Mac/PR state. The pre-review revision subsequently passed 160 unit/integration and 139 Selenium tests locally and four GitHub checks. A new locale-adapter refactor added during final review still requires new full-suite/CI verification. See `SUBMIT_THIS_VERSION.txt` and `docs/part6-ai-simplification-review.md`.

# Part 6 execution evidence and limits — prepared November 8, 2026

Evidence provenance matters in the 20% testing deliverable.

- The baseline **281/281 passing** tests come from the Part 5 files supplied by John, including `report/test_dashboard.html`, dated November 1, 2026. We did not independently reproduce all of them here.
- This Part 6 build adds new tests for four currencies, historic and current exchange rates, Spanish text and display, an audit anomaly queue, acknowledgement, SQLite online backup, checksum integrity and restore protection.
- The Part 6 source was checked by Python compilation and the course Part 3 EARS/C4 structural script. The traceability script also checks that each active requirement has a tagged test or a documented exemption.
- Flask, Werkzeug, Selenium and Ruff are absent from the current offline container; attempted package installation could not reach PyPI. Therefore the web, Selenium, lint and full system tests require a repeat in a complete development/CI environment. The application and its browser tests must not be represented as fully re-verified until that occurs.
- The first written Part 6 currency test contained an *incorrect test assertion* applied to non-yen currencies (3 failures). We corrected the test to check JPY display only for the JPY case; no pricing source code change was needed. This is a real example of why generated tests need review.
- The fictional production incident describes ¥4,500 becoming ¥45 under release 1.3. Our actual Part 5 pricing code already used zero decimal places for JPY. We did not reproduce that bug or run a production rollback. We added regression coverage and isolated formatting to prevent it.

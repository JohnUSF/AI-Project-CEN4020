# Call 6: final classroom status and outstanding production decisions

This is the team's completed classroom maintenance implementation, **not** a production go-live approval. The following items are intentionally not claimed as finished.

| Topic | Present prototype behavior | What's still needed for a real release |
|---|---|---|
| Backup owner (Q25) | SQLite online backup/verified offline restore utilities exist. | Call 6 required an owner by Friday. **No individual was actually assigned** in the provided evidence. Kenji/operations must name the owner, backup frequency, destination, retention and test a restore drill. |
| Human anomaly-alert recipient (Q22-23) | Admin-visible durable alerts, optional SMTP script with configurable threshold. | Darnell/operations must name a human inbox/on-call rotation, configure SMTP, schedule scanning, test delivery and approve the 25% placeholder threshold. |
| English yen formatting (Q24) | Charges use correct zero-decimal yen integer units; English prints `JPY 4,500`. | Customer requested currency-native display (`¥4,500`), which is not implemented throughout English receipt/quote strings. Update display contracts and expected test strings in a separate reviewed change. |
| Reader region and dates (Q24) | Manual English/Spanish cookie; Spanish date/money formatting uses Babel; dates are venue-local text. | Decide region-detection/preference rules, currency locale policy, timezone conversion and human translation approval. Language != geographical region. |
| Production rollback (Q26) | Written rollback/backup runbook. | Assign real deployment tool, known-good release artifact, hosting/operator, live rollback test and operational sign-off. |

## Grading and implementation evidence

Course requirements, C4 diagrams, maintenance functions and regression tests are included. The earlier pre-refactor revision passed **160 unit/integration + 139 Selenium tests (299)**. The final reviewed revision **includes the locale refactor and its new regression test**: the Mac record in `report/last_run.json`, completed **November 9, 2026 at 13:20:04**, reports **161 unit/integration + 139 Selenium = 300 passing tests, 0 failures**, along with passing compilation, configured Ruff lint/format, EARS/C4 and traceability. The latest PR #3 commit passed both quality and system-test checks on GitHub Actions. These checks verify the coursework code, not the outstanding production assignments above. Historical Part 5 first-run failures and scratch backups were excluded from the submission, while formal baseline records remain in `report/baseline/`.

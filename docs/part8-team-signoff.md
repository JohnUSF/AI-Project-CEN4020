# Part 8 - team decisions and final submission gate

**Jai (Gold member)** and **John**: decision agreement reported by Jai, November 23, 2026. This is a team decision record, **not a forged signature** or a claim of a GitHub submitted review.

| Skill finding | Jai | John | Short reason |
|---|---|---|---|
| SQLite restore WAL/SHM | **accepted** | **accepted** | A restored copy must not mix with old SQLite sidecar state; reject unsafe restores and test both filenames. |
| SMTP TLS before login | **accepted** | **accepted** | Refuse to authenticate without STARTTLS rather than exposing credentials. |
| UI catalog bypass | **accepted** | **accepted** | All seven strings should use gettext while retaining expected English text. |
| Legacy English JPY symbol | **rejected** | **rejected** | Keep the tested English receipt behavior for this submission; require a new explicit customer decision and regression review before switching to a yen sign. |

Technical review scope: Part 5 `cc73d4f5` to initial Part 8 `4f037f3`, pinned skill `301b02b12bff98e4688e6984af6556802322bbde`, Copilot Fusion read-only. Accepted source changes in `dbebb63`; original Mac suite **339/339 passed** after the fixes.

**Release/Canvas gate:** This new documentation-and-Gherkin candidate has **not** been verified with the expanded tests yet. PR #5 was still open and `main` had not been verified with these new files at the last GitHub check. The team must apply the final patch, run `bash scripts/verify_part8_mac.sh`, confirm required GitHub Actions green, then merge into `main` and download the merged-main source ZIP. Customer approval of language region, translation nuance and p95 performance SLA is not asserted.

# Part 8 — code-review-and-quality review record (AI findings; human decisions required)

**Agent:** ChatGPT, GPT-6. **Skill source:** `https://github.com/addyosmani/agent-skills`, `skills/code-review-and-quality/SKILL.md`, **pinned at exact commit** `301b02b12bff98e4688e6984af6556802322bbde` (GitHub blob SHA `15ea44c93c61dcec705720342c1fd78755702f85`). Reviewed the pinned instructions through read-only GitHub access. **Review date:** 2026-11-19. The source text specifies five axes: correctness, readability, architecture, security, performance.

**Review range:** from the actual Part 5 report commit `cc73d4f5b85bd269e122438c7d8e450e70f0b279` to the **Part 8 candidate working tree** built on the merged Part 7 PR #4 commit `f97fb2506c001392157201aa928b8e8c0c64841d`. The range includes both Call 6's display fix/corrective items and Call 7's localization work. The compared Part 5 source package and GitHub comparison were inspected; the Part 8 working tree has not yet been committed to GitHub. **After the candidate is committed, rerun the pinned review once against its exact final SHA on your Mac** and reconcile any new findings.

**Read-only condition:** This was an advisory code-review pass of already prepared changes. No credentials were supplied to a review agent and no reviewer-side auto-fixes were enabled. Separately, the candidate implementation was authored at the Gold member's request. The **human team must explicitly approve/reject each finding**, implement accepted changes through the normal developer workflow, and rerun the tests. The table below contains **recommendations, not invented human sign-offs**.

| Check | Severity assigned in pinned-skill-guided review | File and line (candidate) | Proposed decision | Reason / what changed |
|---|---|---|---|---|
| Correctness | Required | `eventhub/web.py:102` | Accept (implemented) | Part 7 did not actually configure Flask-Babel; Part 8 now installs the Babel locale selector at the request boundary. |
| Correctness | Required | `eventhub/i18n.py:91` | Accept (implemented) | Missing Spanish gettext entries must fall back to English rather than another copy of Spanish from a JSON file; regression test added. |
| Architecture | Optional | `eventhub/i18n.py:79` | Reject for Part 8 (documented) | Existing JSON dictionaries are retained for older unit tests while gettext PO/MO is canonical at runtime. Delete the compatibility layer only in a separately tested migration. |
| Correctness | Critical for eligibility | `.github/workflows/check_part5.yml:3` | Accept (implemented) | The previous branch had `quality.yml` but not the explicitly required named workflow; add a real runnable Part 5 gate. |
| Correctness | Required | `features/localization/requirements.md:1` | Accept (implemented) | New Call 7 requirements must be EARS-valid, traceable to tests, and have tagged adjacent feature scenarios; covered with pytest-bdd tests and a static scenario check. |
| Security | FYI | `eventhub/web.py:223` | Reject as a vulnerability claim | The language cookie only stores a whitelisted `en` or `es` value and the POST is CSRF-protected; it does not grant roles or bypass authentication. |
| Performance | Optional | `eventhub/i18n.py:68` | Reject as current blocker | Catalogs and non-request gettext loaders use bounded `lru_cache`, avoiding repeated filesystem loads for every rendered string. |
| Correctness | Required (pre-existing issue) | `eventhub/i18n.py:138` | Reject from this localization-only release; track open | Legacy English yen is displayed `JPY 4,500`, not `¥4,500`. Making it native would change exact text asserted by earlier regression tests and needs an explicitly approved compatibility change. Spanish yen still has no decimal places. |
| Readability | Optional | `eventhub/web.py:59` | Reject from this release; track debt | `create_app` is long, but splitting unrelated routes during a localization-only release makes regression review less reliable; revisit separately. |
| Architecture | FYI | `workspace.dsl:32` | Accept (implemented) | The C4 localization component should name the actual Flask-Babel/gettext boundary instead of only Python Babel/JSON. |
| Security | FYI | `requirements.txt:1` | Accept (sample pins) | The assignment explicitly lists six exact package versions, including Flask-Login and Flask-SQLAlchemy, even though EventHub uses its own identity/SQLite modules. Dependencies must be reviewed before a production deployment. |
| Correctness | Required | `tests/test_part8_scenarios.py:40` | Accept (implemented) | A test of a wholly nonexistent key cannot prove fallback; the test now simulates a missing Spanish translation for an English key. |

### Required three lists from Call 7

**A. Issues the review caught that we had missed:** missing named `check_part5.yml` eligibility workflow; custom translation layer did not use Flask-Babel; missing `.mo` fallback to English; absent tagged localized scenarios; old C4 model still described JSON/Babel only. All have been addressed in the draft.

**B. Findings rejected after checking code:** the language cookie is not an authentication/security escalation; the cached catalog does not reload files for each string; the duplicate JSON source is temporary compatibility, not evidence that checkout amounts are recalculated; giant `create_app()` was pre-existing and not changed as part of this focused release.

**C. Issues the skill/review did not resolve, but we know remain:** native-speaker approval and final Spanish regional variant; geographical region distinct from language, and timezone/format preferences; English yen currency-native symbol compatibility; real ownership of operational backup/alerts from Call 6; whether all GitHub checks pass on the **actual submitted** commit at the deadline. These are not quietly described as complete.

### Human decision checklist (complete with John)

- [ ] Jaideep/Jai reviewed every row, corrected any wrong assertion and approved the accept/reject recommendation.
- [ ] John performed the independent human code review and approved/rejected every row.
- [ ] Pinned skill installed in your Mac coding agent at exact SHA and the final PR commit reviewed in **read-only mode**.
- [ ] All accepted fixes applied; tests rerun on final files; the full `quality.yml` and `check_part5.yml` workflows passed.
- [ ] PR merged to `main` before the deadline. Paste links/SHAs into `docs/part8-team-signoff.md`.

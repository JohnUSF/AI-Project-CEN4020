# Part 8 — GenAI construction and correction log

## Task and instructions

We used ChatGPT (GPT-6) to examine the complete Part 8 PDF and the merged Part 7 source ZIP. The tool was asked to keep earlier requirements, pricing and tests stable, build the Spanish feature with Flask-Babel, update the course-style requirements/model, and apply the exact code-review skill stated in Call 7. The code was verified in a later macOS run; the team has since reported its decisions; the GitHub merge remains a separate verification step.

## What the AI got right

1. It identified that Part 7 used **Python Babel and JSON catalogs**, but **not Flask-Babel**. It proposed a Flask-Babel locale selector at the HTTP boundary and standard `.po/.mo` catalogs without rewriting purchase logic.
2. It mapped new requirements to tagged pytest tests and executable Gherkin scenarios, retaining old IDs.
3. It separated buyer language preference from monetary values and did not touch the stored order totals, rates, or inventory.
4. It located a grading-risk gap: the old repository did not have a workflow named `check_part5.yml` or Gherkin scenario files next to feature requirements.

## What it got wrong and how it was checked

| AI mistake / unsupported assumption | How it was caught | Correction |
|---|---|---|
| Proposed an `if` EARS requirement without the required `then`. | The real `grading/check_part3.py` reported `localization-006` as invalid. | Reworded it using `If ..., then the {EventHub} shall ...`; the gate was rerun successfully. |
| Initial test used translation key `nav.events`, which the JSON catalog does not contain. | Static inspection of the 199-key catalog and manual compiled gettext lookup returned the original key. | Replaced with the existing `nav.register` key and verified Spanish/English compiled translations load. |
| A naive missing Spanish message fallback would still read Spanish JSON text, hiding a missing `.mo` entry. | Five-axis review of the translation call path. | Now uses the English catalog when gettext cannot translate a key; added a regression test. |
| Suggested existing 322 passing tests would prove the **new** Part 8 code. | Compared the date and contents of the saved test record with the new source files. | Classified 322 passes as **Part 7 baseline only**. The later Part 8 macOS run passed 199 unit/integration tests and 140 browser/system tests (339 total). |
| Early scenario fallback case tested a totally unknown key, which has no English counterpart. | Read the scenario wording against the requirement. | Changed the test to simulate a missing Spanish translation for an existing English key. |

## Verification method and limitation

The authoring environment ran Python syntax/compileall, the real Part 3 EARS/C4 eligibility gate, the requirement-to-test traceability checker, and compiled gettext catalog loading/parity checks. The original authoring environment **did not have Flask, Flask-Babel, Selenium, or Ruff**, and could not run the full suite. This limitation was later resolved by the student on a Mac: the complete suite passed **199 unit/integration + 140 system tests** after the AI review fixes (339 total). GitHub PR checks also passed; the initial push performance check exceeded an unapproved placeholder p95 budget, but passed on one rerun. The genuine Mac and CI screenshots are under `report/part8_*png`.

The review record is at `docs/part8-review-record.md`. Jai has confirmed John approved the recorded human decisions. We do not claim a separate GitHub review submission.

## Actual pinned skill review and corrections

Copilot Fusion in VS Code read and used the pinned `code-review-and-quality` skill at commit `301b02b12bff98e4688e6984af6556802322bbde` in read-only mode, compared the Part 5 baseline with Part 8 commit `4f037f3`, and returned **three Required** findings plus **one Optional** currency-display issue. The Required items concerned (1) SQLite restore sidecars, (2) authenticated SMTP without TLS, and (3) several untranslated template strings. We evaluated them, prepared fixes in a separate developer step, added four regression cases, and committed the changes as `dbebb63`. The following Mac run passed 339 tests. The original one-pass review and the four team accept/reject decisions reported by Jai are recorded in `docs/part8-review-record.md`. This is not a claim of a formal GitHub review submission.

## Additional independent review after John's feedback

The original AI assessment correctly distinguished Part 7 Spanish JSON support from the **missing Flask-Babel integration**. We made a separate mistake when summarizing that initial comparison too broadly as “Part 7 had no Spanish support”; that wording was corrected here. The AI also missed the lack of older-feature Gherkin scenario files and the risk of copying unvalidated spreadsheet translations. We added tagged executable backfill examples, per-key provenance, language-cookie checks, and placeholder parity validation. These are post-review additions; **the original pinned skill was not rerun**, preserving the one-pass rule.

# Part 8 — GenAI construction and correction log

## Task and instructions

We used ChatGPT (GPT-6) to examine the complete Part 8 PDF and the merged Part 7 source ZIP. The tool was asked to keep earlier requirements, pricing and tests stable, build the Spanish feature with Flask-Babel, update the course-style requirements/model, and apply the exact code-review skill stated in Call 7. The code and report are drafts until the team verifies and approves them.

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
| Suggested existing 322 passing tests would prove the **new** Part 8 code. | Compared the date and contents of the saved test record with the new source files. | Classified 322 passes as **Part 7 baseline only**. The Part 8 full test run remains pending until the Mac and CI runs are complete. |
| Early scenario fallback case tested a totally unknown key, which has no English counterpart. | Read the scenario wording against the requirement. | Changed the test to simulate a missing Spanish translation for an existing English key. |

## Verification method and limitation

The authoring environment ran Python syntax/compileall, the real Part 3 EARS/C4 eligibility gate, the requirement-to-test traceability checker, and compiled gettext catalog loading/parity checks. The local Python environment **did not have Flask, Flask-Babel, Selenium, or Ruff**, and the package index could not be reached, so an honest full test result cannot be claimed. Run `scripts/verify_part8_mac.sh` on macOS and inspect GitHub Actions before final submission.

The review record is at `docs/part8-review-record.md`. It must receive John's explicit approval on each finding; AI results are suggestions, not decisions made by a human teammate.

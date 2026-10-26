# EventHub Part 4 — Team 5 Gold-member handoff

**Prepared by Jaideep (Gold) for John's review. No changes were pushed to John's repository.**

Start with `report/EventHub_Part4_Assignment_Report.pdf`. The report follows the professor's Part 4 grading weights (20%, 60%, 15%, 5%). This folder also contains the modular working-code draft and tests, plus all the original Part 3 requirements, ADRs and C4 material **preserved without edits**.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
python grading/check_part3.py .
python run.py
```

## Observed local results (October 25, 2026)

- 33 passing domain tests; `test_identity.py` and `test_web.py` skipped as Flask/Werkzeug could not be installed in this build environment.
- 0 Part 3 eligibility failures (Structurizr CLI validation unchecked).
- `compileall` succeeded.
- **HTTP test suite and GitHub Actions CI not yet observed passing.** Please do not mark the project fully validated before running them in a dependency-enabled environment.

## Blocking decisions for John to check

Call 4 refers to customer emails that were **not supplied**: ticket holds, discount scope, purchase caps and confirmation details. Discount percentage remains unprovided. The prototype uses explicitly provisional values and blocks USF discounted purchases without the real percentage. See `docs/implementation-alignment.md`.

## Submission recommendation

Have John install dependencies, run the full test suite with **no skips**, check the UI and CI, provide the missing customer decisions, and review the report before submitting the ZIP. The code is separate from the shared repository so your earlier project is untouched.

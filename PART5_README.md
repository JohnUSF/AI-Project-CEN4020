# EventHub (CEN 4020, Team 5): Part 5, integration and system testing

Python / Flask / SQLite classroom prototype. Tickets and payment are **simulated**.

**Start here:** `report/EventHub_Part5_Assignment_Report.pdf` (or `.docx`), then `report/test_dashboard.html`.

## Run everything with one command

```sh
python3 -m venv .venv && source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt -r requirements-system.txt
python run_all_tests.py                    # about 4 minutes; needs Google Chrome
python run_all_tests.py --with-mutation    # about 8 minutes; also breaks the code on purpose
python run_all_tests.py --skip-system      # no browser, about 30 seconds
```

It compiles, lints, formats, runs the unit and integration tests, the course EARS/C4 gate, the requirement-to-test traceability check and the Selenium suite, then writes `report/test_dashboard.html`. Exit code 0 only if everything passed. On a machine with no internet, Selenium cannot download a driver: set `CHROMEDRIVER=/path/to/chromedriver` or `pip install chromedriver-py==<your Chrome major version>.*`.

To use the app: `python run.py`, then open http://127.0.0.1:5000. To try the student discount, set `EVENTHUB_DISCOUNT_PERCENT=10` first (a labelled **test value**; the real percentage is still unknown, Q1).

## What is in the box

| Path | What it is |
|---|---|
| `eventhub/`, `templates/`, `static/`, `run.py` | the application (Part 4 plus the Call 5 changes) |
| `features/*/requirements.md` | EARS requirements, 107 in total, with supersession links |
| `workspace.dsl`, `diagrams/` | C4 model and exports. `Part5Components` and `Part5PurchasePath` are Graphviz renderings of the DSL, not Structurizr Lite exports |
| `tests/` | 144 unit and integration tests |
| `tests_system/` | **137 Selenium and load tests** (black-box, white-box, Call 5, two-browser oversell, performance) |
| `run_all_tests.py`, `conftest.py`, `scripts/mutation_check.py`, `grading/check_test_traceability.py` | the one-button runner, the requirement-tag rule, the "do the tests fail when the code breaks" check, the requirement coverage check |
| `docs/part5-traceability.md` | each Call 5 finding to requirement, design, code and test |
| `docs/test-plan.md`, `docs/system-test-catalog.md` | how cases were chosen; every test with its requirements and result |
| `docs/decisions/ADR-006..008`, `docs/risk-register.md`, `docs/open-items.md` | decisions, risks awaiting signature, open questions Q18 to Q21 |
| `report/` | the assignment report, dashboard, final run output, `first_run/` (the first run as generated, untouched), `baseline/` (Part 4 as delivered, measured) |

## Not repeated from Part 4
`PART4_README.md`, `docs/ai-process-log.md`, `docs/implementation-alignment.md`, `docs/review-*.md`, `docs/original-genai/`, `SUBMISSION_CHECKLIST.md` and the Part 4 report describe Part 4 and are unchanged. They are in the `EventHub_Team5_Part4` package.

## Things to know before trusting this
- `.github/workflows/quality.yml` is the Part 4 workflow with two additions (the traceability step and a Selenium job). It ran on GitHub: 13 attempts on the branch, 7 passed and 6 failed (five different causes, all in tests or a placeholder number, none in the app). The final commit passed the one attempt I waited for. See report Section 2.9.
- The Selenium run, mutation check and load numbers come from one Linux sandbox with headless Chrome 153. Not run on macOS or Windows, and not on Firefox or Safari.
- The performance budget (500 ms at the 95th percentile) is a **team placeholder**, not a customer requirement (Q13). It sits inside run-to-run noise on the 20-buyer test. If it fails on your machine, that is the placeholder, not necessarily a bug: set `EVENTHUB_PERF_P95_MS`.
- RISK-001 to RISK-005 in `docs/risk-register.md` are **open**. Kenji's findings block release until a named person signs.
- The customer-email decisions and discount percentage from Part 4 are still unknown.

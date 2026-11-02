# Contributing to EventHub (Part 5 rules)

## Definition of done (the four boxes from Call 4, plus two from Call 5)

A feature is **done only when all of these are true**:

- [ ] **Human code review:** a teammate other than the author has read the actual code and resolved feedback.
- [ ] **Tests:** unit, HTTP and browser tests pass, with no unexpected skips.
- [ ] **Specification:** `features/<name>/requirements.md` has new EARS IDs and valid `supersedes:` links if the requirement changed; `workspace.dsl`, `diagrams/` and `docs/part5-traceability.md` follow when components or relationships change.
- [ ] **Automated gates:** compile, `ruff check`, `ruff format --check`, pytest, the Part 3 EARS/C4 gate, and `python grading/check_test_traceability.py .` all pass on the latest commit.
- [ ] **Every test names its requirement** (`@pytest.mark.req("purchase-024")`). The suite refuses to collect a test without one (system-009).
- [ ] **A new rule has a test that would fail without it.** `python scripts/mutation_check.py` shows how: add a mutant for the new rule and confirm a test that names the requirement kills it.

## One button

```sh
python -m pip install -r requirements-dev.txt -r requirements-system.txt
python run_all_tests.py                   # everything except the slow mutation check
python run_all_tests.py --with-mutation   # also break the code on purpose
python run_all_tests.py --skip-system     # no browser
```

Open `report/test_dashboard.html`. The browser tests need Google Chrome. Selenium 4 finds a matching driver itself; on a machine with no internet, set `CHROMEDRIVER=/path/to/driver` or `pip install chromedriver-py==<your Chrome major>.*`.

## Work process

1. Branch from the latest `main`; small related commits.
2. When asking AI for code or tests, give it the requirement text, the component contract, and the failing output. Review every generated line.
3. Do not weaken a test to make it pass. Decide first whether the test or the code is wrong, and write that decision in the commit message.
4. A test that cannot fail is a defect (no `or True`, no assertion-free tests).
5. Never commit credentials, database files, discount numbers invented for production, or real customer emails.

## Enforced checks vs repository settings
The workflow in `.github/workflows/quality.yml` runs on every push and pull request. It cannot block a merge by itself. A repository maintainer must require the `EventHub quality` checks and one approving review in the branch rules. This setting has not been verified from within this package. The workflow has run on GitHub (see report Section 2.9); the load-test budget is set to a placeholder 1000 ms there (open item Q13).

## Open product decisions
Q1 discount percentage, Q3 address verification, Q13 performance sentence, Q16 retention, and Q18 to Q21 from Call 5 are open. Do not guess them. See `docs/open-items.md` and `docs/risk-register.md`.

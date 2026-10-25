# Part 4 — AI development process record (actual work)

**Authoring date:** October 25, 2026. **Gold-member working draft:** for review by John before any final team merge. **Tool used:** ChatGPT GPT-6 in this conversation; project code, templates, tests, and report drafted with AI assistance and independently reviewed by inspecting the requirements and executing the checks available here. Prior Part 3 report attributes its original DSL to Claude; we did not reproduce the old diagrams with a new claim of authorship.

## Input and scope

Read the 5-page Part 4 assignment, the full Call 4 transcript, all eight Part 3 feature requirement files, five ADRs, open-items and existing C4 DSL. We chose to preserve old Part 3 files unchanged and put new code/services/tests in separate folders, to respect the teammate's work.

## Representative instructions used while generating the code

These are **faithful summaries** of the instructions guiding the AI construction, not fabricated verbatim transcripts from a stored prompt tool:

1. Implement the existing modular Flask / SQLite architecture, keeping each behavior in a separate Python module that is directly unit-testable; do not change the Part 3 original requirements.
2. Create one decimal-exact `compute_quote` function; use whole currency minor units and test yen, rate input and student domain case normalization.
3. Guarantee an atomic stock decrement and an audit record per purchase attempt; explicitly test two buyers racing for one remaining ticket.
4. Add routes for account registration, login, catalog search, checkout, history, rates administration, audit viewing, one-use confirmation verification and double-click quick-buy; protect private actions server-side.
5. Create local quality checks, a GitHub Actions workflow, readme, known-issues notes and a straightforward report that distinguishes measured results from unavailable integration checks.

## What the first review found and what changed

- **Redirect concern (review before final test):** a POST to `/quick-buy/<id>` cannot be used as the post-login GET destination. The auth decorator was adjusted to return signed-out users to the *event details page*, not the POST-only endpoint. This awaits HTTP integration confirmation.
- **Currency preview concern:** an event detail page initially used USD even for a signed-in buyer whose preference was EUR. The detail route was changed to use the saved currency and central quote calculation; an unresolved student discount displays a pending-configuration message rather than a made-up amount.
- **Reference-rate concern:** allowing an admin to change `USD` away from 1 would break the base-currency convention. The admin service now rejects that change; a unit test covers it.
- **CI/repo concern:** merely adding a hook does not prevent a broken change from merging. The workflow runs on push and pull request, and the contributing document explicitly calls for branch protection to require the check.
- **Policy concern:** Call 4 says certain customer emails resolved four product questions but the emails were not attached. The code keeps policy-dependent values configurable and documents the exceptions; it does not claim that demo settings are officially approved.

## Recorded local verification

Commands actually run here:

```text
python -m compileall -q eventhub tests scripts
python -m pytest -q
python grading/check_part3.py .
```

Latest local result (before packaging): **33 tests passed, 2 files skipped**, because this offline environment lacks Flask and Werkzeug. The skipped files contain the identity and HTTP integration tests; they are included and are intended to run in GitHub Actions after dependencies are installed. Part 3 eligibility checker: **0 failures / ELIGIBLE**, with Structurizr CLI unavailable and that one validation reported as unchecked. The checker only verifies eligibility structure and EARS form; it does not assess code correctness.

Tests that executed include: search by artist/venue and no-results fallback, escaping SQL wildcards, normalizing uppercase USF addresses, eligible aliases, precise USD/EUR/JPY calculations, rejecting invalid rates and quantities, successful simulated orders, missing discount configuration, canceled checkouts, order rate snapshots, purchase caps, admin rate changes, and two concurrent purchases contending for the final ticket.

## How correct behavior is established (and what remains)

The source modules are executed by direct unit tests without HTTP dependencies, with a real temporary SQLite file in each test. Those tests prove key domain invariants in this environment. Full HTTP/session/security flows must still pass the included integration tests on a machine with Flask and Werkzeug; their outcomes have **not** been observed locally. This is a real limitation, not a reported pass.

Before final submission, John should test the application in a normal Python virtualenv, run all tests with **zero skips**, look through the UI, review the email-policy gaps, and approve the source. If these checks expose bugs, record the failing test, correction and final rerun here, rather than inventing an AI-perfect first attempt.

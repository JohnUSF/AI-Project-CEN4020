# EventHub — AI Project Part 4 (Team 5, Gold-member reviewed revision)

**A review-ready revision of the Gold-member working branch; not merged into John's `main`.** This package builds from the provided Part 3 EventHub EARS requirements, DSL diagrams and ADRs. The original Call 3 DSL is preserved at `docs/part4-design-baseline/workspace-call3.dsl`. Part 4 **updates** EARS requirements with supersession links and revises the component view; the earlier exported diagrams and decisions are retained for comparison. This package is intended for the existing Part 4 PR review branch, not `main`.

The app is a responsive modular **Python / Flask / SQLite classroom prototype**. Tickets and payment are **simulated**; it does not charge customers or issue real tickets.

## Quick start (Mac / Windows / Linux)

Use Python 3.10 or newer. In the extracted project root:

```sh
python3 -m venv .venv
source .venv/bin/activate                 # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
ruff format eventhub tests scripts  # run once after reviewing formatter changes
ruff format --check eventhub tests scripts
python -m pytest -q
python grading/check_part3.py .
python run.py
```

Open **http://127.0.0.1:5000**. Register a buyer account (e.g. `demo@example.com`) and sign in. Browse, search, simulate a purchase, and open My Tickets. Four clearly fictional sample events are seeded from `config/setup.json` on first launch. The database is created under `instance/` and intentionally excluded from source control.

> **Important Call 4 blocker:** The transcript says four decisions were settled in emails (ticket holds, discount scope, confirmation, purchase cap), but those emails were not supplied. See `docs/implementation-alignment.md`. Do not claim this demo implements undisclosed customer decisions. USF accounts cannot finish purchase until the real discount percentage is supplied, rather than applying an invented discount.

### Demo configuration (not approved production policies)

- `EVENTHUB_SECRET_KEY`: set to a long random value; required for predictable sessions across server restarts in real deployment.
- `EVENTHUB_DB`: optional path to SQLite database file.
- `EVENTHUB_DISCOUNT_PERCENT`: **do not configure until the agreed percentage is received**; for a controlled demo only, you may temporarily set an explicitly labeled test value such as `10` and remove it afterward. A USF account without this value receives an explicit pending-configuration error rather than a fabricated price.
- `EVENTHUB_PURCHASE_CAP`: optional server-side per-account-per-event cap. Leave unset pending the customer email; once known, supply the agreed integer.
- `EVENTHUB_SESSION_IDLE`: seconds idle until logout. Default 1800 (30 minutes) is a provisional demo setting; session duration is still disputed in Part 3.
- `EVENTHUB_HTTPS`: set `1` behind HTTPS before deploying, so cookies use Secure.

**Supported demo currencies:** USD, EUR, GBP, JPY. Seed exchange rates are **fictional example rates**, not live rates or market data. USD is fixed at 1. Administrators may update other rates from the admin screen.

### Administrators

1. Create an ordinary buyer account through `/register`.
2. Stop the server and run `python scripts/promote_admin.py buyer@example.com` on the server machine.
3. Start the server and sign in again; `Admin` appears in navigation. The server verifies the administrator role on every request.

No website request can grant administrator access. Admin can update rates (audited), see the newest audit rows, and mark confirmation codes as checked in once. Real door-staff workflow remains a pending customer decision.

## Repo structure

| Path | Purpose |
|---|---|
| `eventhub/` | Standalone service modules: identity, catalog, pricing, inventory, purchase, audit, administration, SQLite, Flask routes |
| `templates/` and `static/` | Responsive buyer/admin UI (single-click details, double-click one-ticket quick-buy) |
| `tests/` | Domain tests, concurrency tests, and Flask HTTP integration tests |
| `.github/workflows/quality.yml` | Compile, lint, unit/integration tests, Part 3 eligibility gate on pushes/PRs |
| `CONTRIBUTING.md` and `.githooks/pre-commit` | Review policy and optional local safety checks |
| `features/`, `workspace.dsl`, `diagrams/`, `docs/decisions/` | **Call 4 revisions** to EARS and component DSL; prior diagrams and ADRs retained; baseline snapshot in `docs/part4-design-baseline/` |
| `docs/implementation-alignment.md` | Requirement-to-code traceability, Call 4 changes and outstanding decisions |
| `docs/ai-process-log.md` | Component contract cards, before/after correction evidence, actual review findings and proof limits |
| `report/EventHub_Part4_Assignment_Report.pdf` | Assignment narrative for teammate review and submission |

## Testing notes

Run `python -m pytest -q`, `ruff format --check eventhub tests scripts` and `python grading/check_part3.py .`; the same test command runs automatically in GitHub Actions. Tests cover rate validation, JPY and USD integer amounts, case-insensitive USF email eligibility, error cases, search fallback, atomic inventory protection, the race for one remaining ticket, per-attempt audit, immutable order-rate snapshots, admin rate edits and one-use check-in. Tests under `test_identity.py` and `test_web.py` require the dependencies in `requirements-dev.txt`.

To enable optional local hook: `git config core.hooksPath .githooks`. For **hard** merge blocking, a repo maintainer must also require `EventHub quality` via GitHub branch protection/rulesets. The app itself is not deployed or connected to a live payment processor.

## Known limitations and review requests

- **Customer policy emails missing:** hold behavior, discount scope, purchase caps, and confirmation details cannot be finalized without them; see alignment document.
- **Discount percentage still pending**; USF purchases intentionally fail closed until configured.
- **Call 4 email variants still unresolved:** this demo treats case-normalized `@usf.edu` as eligible, including `name+alias@usf.edu` but excludes `@mail.usf.edu`.
- **Browsers cannot prevent screenshots**; `purchase-015` cannot be satisfied reliably by an ordinary website.
- **Checkout abandonment on browser close is best-effort**, as accepted in ADR-005; no guarantee of one abandonment event for an abrupt disconnect.
- **Peak load, retention and login abuse policies are not confirmed**; the application is a course prototype, not a production deployment.
- **This review environment lacks Flask/Werkzeug**, so its HTTP and authentication test files are skipped. GitHub Actions installs dependencies and must be checked on the latest revision commit; prior green checks do not certify this later revision.

© Team 5 educational prototype. Design contributions from prior team work remain credited in the original files.

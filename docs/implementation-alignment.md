# Part 4 — requirements, model and implementation alignment

## Starting point (Part 3, preserved verbatim)

The team's Part 3 architecture was a **single modular Flask app** with SQLite in WAL mode, a configuration/setup seed, an administrator role, and separate identity, catalog, pricing, inventory, purchase, audit and admin responsibilities. The earlier C4 diagrams and 80 EARS lines remain unchanged in this handoff; we did **not** quietly rewrite or reuse requirement IDs.

## What Call 4 changes

| Call 4 point | Implementation choice and concrete file | Why / unresolved issue |
|---|---|---|
| Build modular, independently testable components | `eventhub/identity.py`, `catalog.py`, `pricing.py`, `inventory.py`, `purchase.py`, `audit.py`, `admin.py`, `db.py`; `tests/` | Modules own rules rather than burying them in Flask routes |
| Dependency-first delivery | Identity, catalog, pricing and purchasing modules; integration from the start in `eventhub/web.py` | Matches the suggested order and prevents disconnected feature work |
| Human review and small changes | `CONTRIBUTING.md`, `.githooks/pre-commit` | AI code needs human review before merge; hook is opt-in |
| Tests locally and on shared side | `tests/`, `.github/workflows/quality.yml` | CI runs compile, minimal critical lint, pytest, and Part 3 eligibility; branch protections must be enabled separately |
| Warn when code changes without specs | `.githooks/pre-commit`, this file | Warning only; the original EARS IDs are never silently changed |
| One pricing entry point | `eventhub/pricing.py::compute_quote()` | Centralized integer-money math, Decimal-only rate conversion and final rounding |
| Normalized discount emails | `eventhub/pricing.py::normalize_email()`, `eligible_for_usf_discount()` | Uppercase `@USF.EDU` qualifies; plus aliases and subdomains remain a policy question |
| Integrated audit | `purchase.purchase()` and `eventhub/audit.py` | Commit successful purchase + one audit event atomically; rollback then log failure |
| Event list interactions early | `templates/home.html`, `static/app.js` | Click opens detail, double-click submits a quick-buy POST (simulated payment) |
| Code-review definition of done | `CONTRIBUTING.md` and CI | Complete only after review, tests, updated specification alignment and passing checks |

## Selected implementation mapping

| EARS ID(s) | Implementation | Tests |
|---|---|---|
| identity-001, 002, 005, 008, 015, 016 | `identity.py` register/hash/authenticate/promote; `web.py` sessions | `test_identity.py`, `test_web.py` |
| identity-006, 007, 010–014 | `web.py` session expiry, private routes, safe return URL | `test_web.py` |
| catalog-001–008 | `catalog.py`, homepage search, Jinja escaping | `test_catalog.py`, `test_web.py` |
| pricing-001–010 | `pricing.py`, admin rate service, database rates | `test_pricing.py`, `test_admin.py`, `test_purchase.py` |
| inventory-001–004 | `inventory.py` single conditional SQL update inside transaction | `test_purchase.py` |
| purchase-001–014, 016–017, 019–023 | `purchase.py`, Flask checkout and orders, audit integration | `test_purchase.py`, `test_web.py` |
| purchase-018 | `purchase.redeem()` + `/admin/checkin` demo route | `test_purchase.py` (staff workflow TBD) |
| audit-001–004, admin-001–008 | `audit.py`, `admin.py`, protected routes | `test_admin.py`, `test_purchase.py`, `test_web.py` |
| system-001–005 | Flask application, boundary validation, responsive CSS, configurable expiry | `test_web.py`, static review |

## Policy gaps that cannot be resolved from files provided

Call 4 states that emails resolved **ticket hold (Q5), discount scope (Q2), confirmation (Q4) and purchase limit (Q6)**. The actual email text is absent. We cannot know the approved values or update the specs correctly without seeing it. Existing Part 3 `inventory-005` says no holds but marks Q5 pending. The prototype follows that *existing demo behavior* while explicitly flagging that the settled email rule could differ.

The **discount percentage (Q1)** is explicitly still unknown in Call 4. `EVENTHUB_DISCOUNT_PERCENT` is required for eligible purchases, otherwise purchases stop with an explanatory message. The **discount operation order (Q8)** and rounding policy are also not supplied; `compute_quote()` isolates the provisional discount-then-convert, ROUND_HALF_UP behavior in one testable place. A real team decision could require changing that function and updating the EARS requirement with a new ID if the rule is rewritten.

The sample currency list and exchange rates in `config/setup.json` are illustrative placeholders; Q7 remains open. The **purchase cap** defaults to unconfigured, rather than inventing a cap. The **session timeout** of 1,800 seconds is explicitly a provisional demonstration setting, not agreement on Q11. No answer has been supplied for audit retention and detailed staff check-in workflow.

`purchase-015` literally asks a website to prevent screenshots. Browsers generally cannot reliably do this, so no false promise is made. A real-world product revision needs the customer to replace or scope the requirement.

## Further changes before declaring release-ready

1. Obtain Call 4 email decisions and update EARS lines without reusing original IDs; record supersedes links if wording changes.
2. Set the actual discount percentage, scope, purchase cap, currency list, session expiry and money policy.
3. Run **all** Flask integration tests in an environment with dependencies installed and inspect GitHub Actions results; review CLI administrator onboarding.
4. Human-review the checkout path and audit retention, verify UI at mobile widths and enforce CI branch protection.
5. Run measured performance/concurrency tests against the agreed peak traffic (Q13); this version only covers a deterministic two-writer race.

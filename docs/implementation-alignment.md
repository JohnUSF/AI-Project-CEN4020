# Part 4 — requirements, model and implementation reconciliation

## Baseline and controlled changes

Part 3 had 80 EARS requirements, a modular Flask application and SQLite. Its original C4 DSL was saved **verbatim** at `docs/part4-design-baseline/workspace-call3.dsl` before this revision. The C4 source at root **is now intentionally updated** and includes a separate **USF Discount Eligibility** component and a `Part4Components` view; `diagrams/Part4Components.svg` is a readable rendering of the revised component relationships. The original Part 3 exported diagrams remain for comparison, not as current views. We retained all prior EARS IDs and represented revisions with the checker-compatible two-way `superseded by` / `supersedes:` mechanism rather than renaming old requirements.

## Actual Call 4 deltas — not just code-level claims

| Call 4 discussion / source | Requirement change | Architecture/model change | Implementation/test |
|---|---|---|---|
| Case-insensitive USF email; email comparison its own testable function | Old pricing-002 is superseded by pricing-011. New pricing-012 covers trimming and casefolding; pricing-013/014 state provisional plus-tag/subdomain assumptions | New **USF Discount Eligibility** C4 component, linked from Pricing in `workspace.dsl` | `eventhub/eligibility.py`, standalone `tests/test_eligibility.py` |
| Audit records readable by admin; retention raised but not decided | audit-005 restricts read access; audit-006 records retention as [TBD: Q16] without guessing a period | Existing Admin → Audit path retained, audit description now includes retention undecided | `eventhub/web.py` enforces role; `eventhub/audit.py` stores records; tests in `test_admin.py` / `test_audit.py` |
| Modular features must be importable and unit tested | system-007 adds independently importable service rule | Service modules map 1-to-1 to C4 responsibilities, eligibility split out | `eventhub/`, tests in matching files including separate audit/inventory tests |
| Tests locally/CI; automatic checks and spec alignment | system-008 adds automated test requirement; engineering policy in `CONTRIBUTING.md` | Shared Flask container unchanged; dev workflow changes outside product model | `.github/workflows/quality.yml` requires pytest, compile, Ruff lint + **Ruff formatting check** and Part 3 gate; `.githooks/pre-commit` checks local |
| Pricing remains centralized | pricing-007 remains in force; pricing-011 clarifies discount eligibility | Pricing → Eligibility edge; *only Pricing* calculates final amounts | `compute_quote()` retains currency/discount arithmetic; `eligibility.py` returns Boolean classification only |
| Component purchase path and integrated audit | inventory-003, audit-002/003 preserved | Inventory and Audit remain distinct components; transaction design retained | SQLite `BEGIN IMMEDIATE` and conditional update, failure logs on rollback; test for final ticket contention |

## Contradictions resolved explicitly

The old `docs/open-items.md` said that Q2/Q4/Q5/Q6 were unresolved, even though Call 4 says emails had settled them. It now distinguishes **reported settled but missing approved text** from truly undecided rules. We must obtain the emails before replacing provisional behavior or claiming final product alignment. The demo currently implements no holds (inventory-005) but *does not claim* that is the approved final decision.

For email patterns, the **documented provisional policy** is: trim surrounding whitespace, casefold, allow `NAME+ALIAS@USF.EDU`, reject `@mail.usf.edu`; this is encoded in pricing-011 to pricing-014 and tested. This is **not confirmed by the customer** (Q17). No customer-approved discount *percentage* exists in the supplied evidence (Q1); qualifying checkout remains blocked without an explicit configured value. Discount scope (Q2) remains conditional on the missing email text.

Audit access is admin-only; **retention duration is not specified**. Q16 was added; the system retains its records but does not implement automatic deletion until the policy is approved. The data model and implementation do not claim otherwise.

## Implementation contracts used to guide AI assistance

| Component | Inputs, invariants and outputs | Edges / failure contract |
|---|---|---|
| Eligibility | `normalize_email(value)->str`, `eligible_for_usf_discount(email)->bool`; case-insensitive exact domain; no pricing math | Pricing and Identity call eligibility module; no database writes |
| Pricing | `compute_quote(base_usd_minor:int, quantity:int, eligible:bool, currency:str, rate:str, discount_percent)->Quote`; integers, Decimal, target currency rounding; no template money math | Calls eligibility for student classification; invalid currency/quantity/missing rate rejected; unknown Q1 fails closed |
| Inventory | `take_tickets(conn,event_id:int,quantity:int)`; never allow stock below zero | Purchase calls within `BEGIN IMMEDIATE`, SQL conditional UPDATE; raises SoldOut |
| Purchase | `purchase(conn,account_id,event_id,quantity,currency,...) -> order_id`; exactly one audit per attempt; atomic successful order/stock/audit | Identity → Catalog → Pricing → Inventory → Audit; rollback failure, then audit failure |
| Audit | `record(conn, kind, account_id,...,outcome)` and `recent(conn,limit)`; ordered by latest | Admin alone can reach audit viewing HTTP routes; retention policy pending |

## Requirements history

See `docs/part4-traceability.md` for new and superseded IDs and existing `docs/traceability.md` for the unchanged Part 2 → Part 3 history. **No prior original requirement ID was reused or deleted.**

## Unresolved work and proof boundaries

- Obtain the actual customer-email decisions covering Q2 discount scope, Q4 confirmation, Q5 holds and Q6 purchase caps. The Call 4 PDF only *reports* their existence.
- Confirm Q1 discount percentage, Q16 audit retention and Q17 email alias/subdomain rules. `config/setup.json` rates and example events are demo values.
- Session timeout Q11 and performance requirements Q13 also remain unapproved.
- Full Flask integration tests require Flask/Werkzeug. This sandbox runs core domain tests only; GitHub Actions can execute the full tests and must be checked after pushing.
- The new `Part4Components.svg` is a **Graphviz rendering from the same documented component relationships**, not falsely labeled a Structurizr Lite export; the DSL source is provided and remains the authoritative model.
- Branch protection/rulesets are repository settings; adding CI alone does not enforce merge blocking. John must confirm the protection and human approval.

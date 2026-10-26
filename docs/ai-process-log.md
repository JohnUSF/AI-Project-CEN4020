# Part 4 — AI generation, human review and correction evidence

**Team:** Team 5 | **Gold member:** Jaideep Yarasingu | **Review:** John Bachta.  **AI assistance for Part 4:** ChatGPT. The earlier Part 3 report credited **Claude** for its own DSL work; these are different phases, not an inconsistency.

> Scope: This is an evidence-based account of the supplied work and review. We do not have a verbatim archive of each internal code-generation instruction, so representative prompts below are explicitly labeled **reconstructed / reusable prompt recipes**, NOT exact historic chat messages. We do have test outputs, John's written feedback, two actual implementations and changed files.

## 1. How we converted a C4 picture into an implementable AI contract

A visual box and arrow are not enough for safe code generation. We gave each component a **contract card** with: named responsibility, Python module, typed/function inputs and outputs, DB tables owned, invariants, error behavior, collaborating components and required test examples. This format made the requirements operational and caught the temptation to place eligibility logic in the UI.

For example:

```text
COMPONENT: Pricing (eventhub/pricing.py)
INPUT: base_usd_minor: int; quantity: int; eligible: bool; currency: str; rate: decimal-string;
       discount_percent: approved config or None
OUTPUT: Quote(total_minor: int, rate_snapshot: str, currency: str)
INVARIANTS: only one price computation function; Decimal, not float; JPY 0 decimals;
            student discount unknown -> explicit configuration error
COLLABORATOR: Eligibility component returns normalized exact-domain classification; never computes money
TESTS: USD exact cents; EUR discount/rounding; JPY; unsupported currency; unknown discount
```

```text
COMPONENT: Purchase (eventhub/purchase.py)
INPUT: buyer_id, event_id, quantity, currency, optional approved cap/discount settings
OUTPUT: order ID or typed error
COLLABORATORS: Identity -> Catalog -> Pricing (+ Eligibility) -> Inventory -> Audit
INVARIANTS: stock cannot go negative; successful order/stock/audit commit atomically;
            failed attempt records one audit after rollback
TESTS: one remaining ticket + two threads = one success and one sold-out;
       audit count exactly two, final stock zero
```

This component-contract format is what we would use as the **preferred prompt structure going forward**, instead of a generic instruction such as “write the EventHub Flask app.”

## 2. Before/after prompting: faithful instruction comparisons, not fabricated transcripts

| Stage | Initial broad direction (faithful summary, not verbatim) | Precise corrective AI instruction (reconstructed from actual review request and applied changes) | Observable artifact |
|---|---|---|---|
| Identity compatibility | “Build Flask registration/login and hash passwords securely.” | “Use a portable explicitly configured Werkzeug PBKDF2-SHA256 method rather than the environment-dependent scrypt default; keep passwords hashed, add/execute the login test.” | `eventhub/identity.py`, Mac test error screenshot (`hashlib.scrypt`) and corrected commit |
| Requirements/model alignment | “Keep Part 3 untouched while implementing Call 4.” | “Preserve existing EARS IDs but add checker-valid supersession links and new requirement IDs for normalized exact-domain eligibility; add an Eligibility component/edge to the Part 4 C4 view.” | `pricing-002 → pricing-011`, `pricing-012–014`, `workspace.dsl`, `Part4Components.svg` |
| Audit privacy | “Add audit logging and an admin page.” | “Explicitly add an admin-read access requirement; add retention as an unresolved policy question, **without inventing days or automatic deletion**; test the audit component standalone.” | `audit-005`, `audit-006`, Q16, `tests/test_audit.py` |
| Code quality | “Run compile, pytest and a narrow lint check.” | “Define all four completion criteria, configure a Ruff formatting check as well as lint, and explain why CI requires branch protection to block merges.” | `.github/workflows/quality.yml`, `CONTRIBUTING.md`, `.githooks/pre-commit` |
| Grading narrative | “Summarize how GenAI generated the code.” | “Document exact component contracts, real fail/pass evidence, code review findings from John, outdated counts and what was not independently verified.” | this log, revised report, test outputs |

## 3. Actual failure evidence and code-level correction

**Mac test failure** (provided in conversation): `AttributeError: module 'hashlib' has no attribute 'scrypt'`. The screenshot showed **1 failed, 38 passed**. It came from Werkzeug's default password hashing on that Mac Python build.

**Before** (`eventhub/identity.py`, prior draft):

```python
# Prior draft passed no hashing method and Werkzeug chose its default.
generate_password_hash(password)
```

**After** (current branch):

```python
# Explicit portable PBKDF2 SHA-256 with a high iteration count.
generate_password_hash(password, method="pbkdf2:sha256:600000")
```

This changes the default selection, not the use of secure password hashing. A password verification regression test already exists under `tests/test_identity.py`. It was executed by the developer on the Mac after dependency installation; the teammate later reported a **49-passing-test** run. **That latter number is teammate-reported, not independently reproduced in this sandbox**. Earlier PR screenshots showed **two passing GitHub checks**, but those checks apply to the earlier commit, not automatically to this later revision.

## 4. Human review (John) exposed deeper errors than a green test badge

John inspected the October 25 draft and identified: missing EARS and C4 deltas; stale Q status and contradictory alias/subdomain notes; missing explanation of component-to-prompt encoding; no real before/after or failing evidence; a stale 33-pass claim; no formatting check; no four-box completion gate; separate audit/inventory tests missing; and a README/version mismatch. He also correctly identified that merge protection is an administrator-controlled setting. These were substantive human-review findings **not discovered by AI syntax checks**.

**Changes implemented in this revision:** case-normalized eligibility moved to `eventhub/eligibility.py`; `pricing-002` superseded with new IDs; a dedicated C4 component and rendered Part 4 view added; Q16/Q17 added; independent audit/inventory/eligibility tests added; formatting check added to CI and the local hook; both readmes aligned; reviewer checklist and this evidence log rewritten; test counts rerun locally.

## 5. Tests — describe the precise execution environment

- Original offline package: **33 passed, 2 test modules skipped** because Flask/Werkzeug were not installed.
- Mac run prior to explicit PBKDF2 fix: **38 passed, 1 failed** (`hashlib.scrypt` missing), per actual screenshot.
- Teammate review cited **49 passed** after the Mac fix; this is **reported, not directly observed in this sandbox**.
- **This revision:** run `python -m pytest -q`, `python grading/check_part3.py .`, `python -m compileall -q eventhub tests scripts`. Attach/update the resulting output in `report/` before final submission; counts must come from those commands rather than guesswork.
- Full HTTP suite and `ruff format --check` require installed dependencies/formatter; **do not claim a verified zero-skip/full-format pass without running them**.

## 6. What worked and what we would change next time

**Worked:** contracts with inputs, outputs, collaborators and invariants; transaction-first concurrency tests; one pricing function; human review catching architectural omissions; evidence-based revision and EARS regression gate.

**Didn't work initially:** keeping all Part 3 files frozen after a requirements-changing call; asking AI for modules without separately modeling discount eligibility; omitting the actual change log and old failure logs; treating green CI as equivalent to human review; under-specifying acceptance criteria for formatter/retention.

**Next time:** before code generation, give AI one **machine-checkable component contract per box**, updated EARS acceptance tests, the customer email answers and explicit definition of done; generate a small module and focused tests together; attach failing trace to corrective prompt; rerun full CI on the revised commit; preserve the before/after diff in `docs/`.

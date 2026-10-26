# Call 4 traceability (additive to the original Part 2→3 map)

The original `docs/traceability.md` records how Part 2 IDs became Part 3 IDs.
It is kept intact; this supplement records Part 4 changes without hiding history.

| Call 3 EARS ID | Call 4 status | Replacement or extension | Source | Implementation/test |
|---|---|---|---|---|
| pricing-002 | superseded; still supersedes identity-003 | pricing-011 (normalized exact domain) | Call 4 security discussion | `eventhub/eligibility.py`, `test_eligibility.py` |
| pricing-003 | unchanged; standard price for non-USF accounts | pricing-012 adds pre-check normalization | Call 4 email case | `eventhub/eligibility.py`, `test_eligibility.py` |
| pricing-007 | retained | pricing-012 makes testable eligibility explicit | Call 4 pricing function rule | `eventhub/pricing.py`, C4 component view |
| pricing-011 | new | pricing-013 (provisional plus tags), pricing-014 (provisional subdomain exclusions) | Call 4 unresolved variants | `test_eligibility.py`, Q17 |
| audit-001–004, admin-008 | retained | audit-005 (administrator read-only), audit-006 (retention TBD) | Call 4 QA privacy issue | `eventhub/web.py`, `eventhub/audit.py`, Q16 |
| system-001–006 | retained | system-007 (testable modules), system-008 (CI) | Call 4 modularity / gates | `tests/`, `.github/workflows/quality.yml` |

## Format, governance and completion criteria

The CI pipeline now checks `ruff format --check` as well as compilation, lint, pytest and EARS/Structurizr structure.
See `CONTRIBUTING.md` for the four-box feature completion gate. CI is configured but **blocking merge is an admin-level branch protection setting**, not proven by the workflow itself.

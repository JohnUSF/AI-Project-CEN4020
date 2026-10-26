# EventHub (CEN 4020, Part 3)

- `features/<component>/requirements.md`: EARS requirements by feature (`system` holds the cross-cutting ones).
- `workspace.dsl`: Structurizr DSL for the context, container, component and purchase-path views.
- `diagrams/`: PNG exports of each view, exported from Structurizr Lite (file names are Lite's own).
- `docs/decisions/`: decision records (database, money, rates storage, administrator role, abandoned checkout).
- `docs/traceability.md`, `docs/open-items.md`.
- `docs/original-genai/`: the original container and component diagrams from before Call 3.

Check before committing: `python3 grading/check_part3.py .`


---

## Part 4 implementation (Call 4, Gold-member review branch)

Part 4 builds on the above Part 3 requirements and C4 model. Start with [`PART4_README.md`](PART4_README.md) for installation, sample app/demo limits and tests. Part 4 adds standalone `eventhub/eligibility.py`, dedicated inventory/audit unit tests, and a revised `Part4Components` diagram alongside the original exports. See [`docs/implementation-alignment.md`](docs/implementation-alignment.md) and [`docs/part4-traceability.md`](docs/part4-traceability.md) for requirement changes with preserved ID history; see [`docs/review-response.md`](docs/review-response.md) for John's review resolution. The original Part 3 model snapshot is in `docs/part4-design-baseline/`.

Final checks: `python -m pytest -q`, `ruff format --check eventhub tests scripts`, and `python grading/check_part3.py .`. **The customer-email decisions and discount percentage still require confirmation.**

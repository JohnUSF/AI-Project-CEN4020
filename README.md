# EventHub (CEN 4020, Part 3)

- `features/<component>/requirements.md`: EARS requirements by feature (`system` holds the cross-cutting ones).
- `workspace.dsl`: Structurizr DSL for the context, container, component and purchase-path views.
- `diagrams/`: PNG exports of each view, exported from Structurizr Lite (file names are Lite's own).
- `docs/decisions/`: decision records (database, money, rates storage, administrator role, abandoned checkout).
- `docs/traceability.md`, `docs/open-items.md`.
- `docs/original-genai/`: the original container and component diagrams from before Call 3.

The provided eligibility checker scripts are included in `grading/`.

Check before committing: `python3 grading/check_part3.py .`

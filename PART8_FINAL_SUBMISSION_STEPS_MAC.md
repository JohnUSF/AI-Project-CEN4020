# Part 8 final steps on a Mac (after John approved the four finding decisions)

The complete source ZIP is a candidate, not evidence that GitHub `main` has been updated. Part 8 eligibility is determined **from the default branch at the deadline**. Use the accompanying patch to update the existing `part8-jaideep-gold` branch. Back up unrelated uncommitted files before applying it.

If you are applying this update through the `EventHub_Part8_Safe_Update_For_Mac.zip` bundle,
**use the supplied `apply_update.py`** rather than the older `git apply` patch.
That patch was generated against a handoff copy and is not a reliable match for the
existing Git branch. The safe updater checks your branch and protects dirty files.

After extraction to Downloads, from the repository folder run:

```bash
python3 ~/Downloads/EventHub_Part8_Safe_Update_For_Mac/apply_update.py
source .venv-part8/bin/activate
python scripts/check_part8_scenarios.py
python scripts/validate_translation_catalogs.py
bash scripts/verify_part8_mac.sh
```

Do not stage generated `report/last_run.json` or screenshots automatically. Stage
only intentional source, report and documentation updates after the full suite passes.


Wait until every PR check (including `check_part5/eligibility`, `quality` and `system-tests`) is green on the new commit. Keep the 500 ms **unapproved** placeholder benchmark unchanged; if it intermittently fails, diagnose the logged p95 performance. Ask John to verify the final diff and merge PR #5 into `main`. Confirm the default-branch workflows remain green. On GitHub select `main` → Code → Download ZIP and submit **that ZIP** with `report/EventHub_Part8_Assignment_Report.pdf` on Canvas.

The documented previous Mac run passed 199 unit/integration + 140 Selenium = 339. Additional Gherkin and governance tests were added afterward and were **not** run here; do not write “339 passed in final candidate” unless the new run actually shows that number. Python compilation, course Part 3 eligibility, traceability, feature scenario-folder audit and gettext catalog/provenance checks have been rerun and passed here.

**Canvas irregular-requirement follow-up:** Post the drafted spreadsheet/translation workflow question in `docs/decisions/ADR-009-translation-sources.md` and record any TA response. Do not invent a response.

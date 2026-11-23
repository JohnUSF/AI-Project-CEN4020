# ADR-009 - Translation draft source, approval and controlled import

**Status:** Accepted for course prototype; customer/TA confirmation requested but not received.

**Context (Call 7):** Marcus suggested letting Darnell's office edit Spanish strings in a shared spreadsheet and copying the latest sheet into each release. That creates a risk of unreviewed text changes, lost version history, and broken substitution fields such as `{seconds}`.

**Decision:** Treat a spreadsheet as an *incoming draft* only. The repository's version-controlled gettext `.po/.mo` catalogs are the release source of truth. Each key has a declared source and review status in `docs/part8-translation-provenance.json`. Before any translation draft is accepted, `python scripts/validate_translation_catalogs.py` must pass key parity, placeholder parity, provenance and compiled gettext checks. Source code changes go through a human PR review and system tests. The team-produced Spanish translation is AI-assisted and not independently certified.

**Consequences:** Darnell's office can still author wording in a spreadsheet, but a developer must review and import it, and tests must pass. Spanish copy may change only in a tracked commit. This does not settle the future production owner, locale/region or native-speaker approval.

**Canvas discussion question to post:** “Call 7 proposes keeping Spanish translations in a shared spreadsheet and copying them into each release. Should this be considered an irregular requirement? May the team accept spreadsheet drafts only after version-controlled gettext review, placeholder validation and tests, or is another approval workflow required?” This is a prepared question; **we have not posted it or received a TA answer**.

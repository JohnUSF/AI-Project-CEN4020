# Contributing to EventHub

1. Branch from the shared branch; use descriptive commit messages and small pull requests.
2. Review AI-generated code yourself before committing. Explain the intended behavior and test it.
3. Update EARS specifications or `docs/implementation-alignment.md` when behavior changes.
4. Run `python -m pytest -q` and `python grading/check_part3.py .` locally.
5. Run `python -m compileall -q eventhub tests scripts` and a small `ruff check` before pushing.
6. Optionally enable local checks with `git config core.hooksPath .githooks`.
7. The `EventHub quality` GitHub Action re-runs tests on every push and pull request; enable branch protection to require it before merge. A workflow alone cannot block merges without protection.
8. Pair-programming credit: include `Co-authored-by: Name <email>` only for actual shared work.
9. Never commit credentials, database files, tickets, private emails, or API keys.

**The Part 3 requirements and decision records are preserved unchanged in this review package.** The implementation departures and unresolved questions are listed in `docs/implementation-alignment.md`.

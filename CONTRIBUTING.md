# Contributing to EventHub — Call 4 implementation protocol

## Definition of done (four mandatory boxes adopted in Call 4)

A feature is **done only when all four conditions are true**:

- [ ] **Human code review:** a teammate other than the author has reviewed the actual code and resolved feedback.
- [ ] **Tests:** standalone unit tests and related HTTP/integration tests pass, with no unexpected skipped files.
- [ ] **Specification:** update `features/<name>/requirements.md` with new EARS IDs and valid supersedes links if the requirement changed; update `docs/part4-traceability.md` and `workspace.dsl`/diagram when component relationships change.
- [ ] **Automated gates:** compile, `ruff check`, `ruff format --check`, pytest and Part 3 structural/EARS gate all pass on the PR's **latest commit**.

## Work process

1. Branch from the latest `main`; make small related commits and preserve the Gold/Silver review split.
2. Use the component contracts in `docs/implementation-alignment.md` when requesting AI code; review every generated line before merge.
3. Test locally with `python -m pip install -r requirements-dev.txt` and `python -m pytest -q`.
4. Run `ruff format eventhub tests scripts` **to apply formatting**, then `ruff format --check eventhub tests scripts` and `ruff check eventhub tests scripts`.
5. Run `python -m compileall -q eventhub tests scripts` and `python grading/check_part3.py .`.
6. Opt into the pre-commit hook via `git config core.hooksPath .githooks` (not installed automatically).
7. Never commit credentials, user database files, discount numbers invented for production, or actual customer emails containing private data.
8. Co-author trailers are only for work actually performed together.

## Enforced checks vs repository settings

The GitHub Actions workflow runs automatically on push/PR. **It does not block merging without a repository rule:** John (repository maintainer) must configure **Settings → Rules → Rulesets** (or Branch protection) to require the named quality checks on `main` and one approving review. This setting has not been verified from within this package.

## Open product decisions

The Call 4 transcript says decisions Q2/Q4/Q5/Q6 were recorded in customer emails, but these emails are not in the shared files. Request them; do not guess. Q1 discount percentage and Q16 retention remain [TBD]; Q17 alias/subdomain behavior is a documented **provisional assumption**.

# Gold member — Mac instructions (Part 8)

This ZIP is based on the merged Part 7 project. The **ZIP alone is not the final Canvas artifact until** you run the tests, install the pinned skill, record the team's human review decisions and merge a green PR.

## 1. Prepare the project and copy files

Create the branch from the latest `main` and apply the companion `EventHub_Part8_Changes.patch` supplied alongside this ZIP. Work in your actual Git clone, **not** in an unzipped GitHub download with no `.git` directory:

```bash
cd ~/AI-Project-CEN4020
git status --short                # preserve any uncommitted work first
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c part8-jaideep-gold
git apply --check ~/Downloads/EventHub_Part8_Changes.patch
git apply --index ~/Downloads/EventHub_Part8_Changes.patch
```

If `git apply --check` fails, **do not force apply**: the base may have changed. Contact your teammate and inspect `git status`.

## 2. Verify on macOS

Use a new Python virtual environment; the script selects Python 3.13 or 3.12, installs exact assignment dependencies and all development/system packages, and runs the full test suite. Chrome must be available locally.

```bash
bash scripts/verify_part8_mac.sh
```

Expected outcomes: Python compiles, Ruff checks pass, course eligibility/traceability both pass, **new Part 8 tests plus every existing test pass**, and the Selenium run succeeds. The Part 7 record of 322 passing tests is **not** an expected new total, because Part 8 adds more tests. Save exact results shown on your Mac; don't write made-up counts.

## 3. Pinned skill and review

```bash
bash scripts/install_part8_review_skill_mac.sh
```

In the coding agent where the skill is installed (e.g. Claude Code), request a **read-only** `code-review-and-quality` review once, comparing Part 5 commit `cc73d4f5b85bd269e122438c7d8e450e70f0b279` with your new Part 8 commit. Provide no secrets or credentials. The review must check correctness, readability, architecture, security, and performance, report severity and file:line for every finding, and supply the three lists (missed issues, false alarms, known missed issues). Record all findings and you/John's actual accepted/rejected decisions in `docs/part8-review-record.md` and `docs/part8-team-signoff.md`. This is part of the graded **30% review deliverable**.

## 4. Commit, push, request review, merge

```bash
git diff --cached --check
git status --short
git commit -m "Implement Flask-Babel Spanish interface and Part 8 review evidence"
git push -u origin part8-jaideep-gold
```

Open PR with base `main`, compare `part8-jaideep-gold`. Verify the `quality` and `check_part5` workflows. Request John's review. Merge only after a team member checks all required results.

## 5. Final Canvas package

After merge: `main` → Code → Download ZIP, plus the **updated** `report/EventHub_Part8_Assignment_Report.pdf` whose verification and team-review sections now reflect your real results. Submit only what the Canvas assignment actually asks for.

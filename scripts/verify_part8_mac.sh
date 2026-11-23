#!/usr/bin/env bash
# Read-only against implementation; creates an isolated venv and test evidence files.
set -euo pipefail
cd "$(dirname "$0")/.."
if command -v python3.13 >/dev/null 2>&1; then PYTHON=python3.13;
elif command -v python3.12 >/dev/null 2>&1; then PYTHON=python3.12;
else echo 'Install Python 3.12 or 3.13 from python.org or brew.' >&2; exit 2; fi
if [[ ! -e .venv-part8/bin/python ]]; then "$PYTHON" -m venv .venv-part8; fi
source .venv-part8/bin/activate
python -m pip install -r requirements-dev.txt -r requirements-system.txt
python -m compileall -q eventhub tests tests_system scripts
python -m ruff check eventhub tests tests_system scripts --select E4,E7,E9,F63,F7,F82
python -m ruff format --check eventhub tests tests_system scripts
python grading/check_part3.py .
python grading/check_test_traceability.py .
python scripts/check_part8_scenarios.py
python scripts/validate_translation_catalogs.py
python -m pytest tests tests_system -q -rfE
python run_all_tests.py
printf '\nMac verification complete. Check report/last_run.json and PR workflows.\n'

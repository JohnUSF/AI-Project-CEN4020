#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m compileall -q eventhub tests tests_system scripts
python grading/check_part3.py .
python grading/check_test_traceability.py .
python -m pytest -q tests/test_call6_maintenance.py tests/test_call6_http.py

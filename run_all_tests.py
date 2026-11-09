#!/usr/bin/env python3
"""One button: run every check EventHub has and build the HTML report.

    python run_all_tests.py                 # everything except the (slow) mutation check
    python run_all_tests.py --with-mutation # also break the code on purpose and confirm the tests notice
    python run_all_tests.py --skip-system   # no browser (fast suite and gates only)
    python run_all_tests.py --headed        # watch Chrome do it

Needs: pip install -r requirements-dev.txt -r requirements-system.txt, and Google Chrome.
Writes report/last_run.json and report/test_dashboard.html. Exit code 0 only if everything passed.
"""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable


def step(name, cmd, env=None):
    started = time.time()
    proc = subprocess.run(
        cmd, cwd=ROOT, env={**os.environ, **(env or {})}, capture_output=True, text=True
    )
    seconds = round(time.time() - started, 1)
    tail = [l for l in (proc.stdout + proc.stderr).strip().splitlines() if l.strip()][
        -3:
    ]
    ok = proc.returncode == 0
    print(
        f"{'🟢' if ok else '🔴'} {name:<44} {seconds:>7.1f}s   {tail[-1][:80] if tail else ''}"
    )
    if not ok:
        print(
            "\n".join(
                "      " + l[:160]
                for l in (proc.stdout + proc.stderr).strip().splitlines()[-25:]
            )
        )
    return {
        "name": name,
        "ok": ok,
        "seconds": seconds,
        "summary": tail[-1] if tail else "",
        "returncode": proc.returncode,
    }


def main(argv):
    results = []
    print(f"EventHub full test run, {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    results.append(
        step(
            "Python compiles",
            [
                PY,
                "-m",
                "compileall",
                "-q",
                "eventhub",
                "tests",
                "tests_system",
                "scripts",
            ],
        )
    )
    ruff = shutil.which("ruff")
    if ruff is None:
        # Call 6: a green dashboard must never hide a missing quality dependency.
        print(
            "🔴 Ruff is required for a complete quality run (install requirements-dev.txt)"
        )
        results.append(
            {
                "name": "Ruff lint/format dependency",
                "ok": False,
                "seconds": 0.0,
                "summary": "ruff not installed",
                "returncode": 2,
            }
        )
    else:
        results.append(
            step(
                "Ruff lint",
                [
                    ruff,
                    "check",
                    "eventhub",
                    "tests",
                    "tests_system",
                    "scripts",
                    "--select",
                    "E4,E7,E9,F63,F7,F82",
                ],
            )
        )
        results.append(
            step(
                "Ruff format check",
                [
                    ruff,
                    "format",
                    "--check",
                    "eventhub",
                    "tests",
                    "tests_system",
                    "scripts",
                ],
            )
        )
    results.append(
        step(
            "Unit + integration tests (pytest tests)",
            [
                PY,
                "-m",
                "pytest",
                "tests",
                "-q",
                "--no-header",
                "-p",
                "no:cacheprovider",
            ],
        )
    )
    results.append(step("Course EARS / C4 gate", [PY, "grading/check_part3.py", "."]))
    results.append(
        step(
            "Requirement-to-test traceability",
            [
                PY,
                "grading/check_test_traceability.py",
                ".",
                "--markdown",
                "report/test_traceability.md",
            ],
        )
    )
    if "--skip-system" not in argv:
        env = {"EVENTHUB_HEADED": "1"} if "--headed" in argv else {}
        results.append(
            step(
                "Selenium system tests + load measurement",
                [
                    PY,
                    "-m",
                    "pytest",
                    "tests_system",
                    "-q",
                    "--no-header",
                    "-p",
                    "no:cacheprovider",
                    "-rfE",
                ],
                env,
            )
        )
    if "--with-mutation" in argv:
        results.append(
            step(
                "Mutation check (20 deliberate bugs)",
                [
                    PY,
                    "scripts/mutation_check.py",
                    "--json",
                    "report/mutation_check.json",
                ],
            )
        )
    (ROOT / "report").mkdir(exist_ok=True)
    (ROOT / "report" / "last_run.json").write_text(
        json.dumps(
            {"finished_at": time.strftime("%Y-%m-%d %H:%M:%S"), "steps": results},
            indent=1,
        )
    )
    subprocess.run([PY, "scripts/build_dashboard.py"], cwd=ROOT)
    failed = [r for r in results if not r["ok"]]
    print(
        f"\n{'🟢 ALL PASSED' if not failed else '🔴 ' + str(len(failed)) + ' STEP(S) FAILED'}: open report/test_dashboard.html"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

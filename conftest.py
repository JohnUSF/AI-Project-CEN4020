"""Project-wide pytest hooks (apply to tests/ and tests_system/).

1. Thuy's rule: a test with no requirement tag is refused at collection (system-009).
2. Every run records, per test, its requirement IDs, black/white-box tag, timing and (for browser
   tests) a screenshot of any failure. scripts/build_dashboard.py turns that into the HTML report.
"""

import json
import os
import re
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
RESULTS = {"unit": [], "system": []}


def _suite(item):
    return "system" if "tests_system" in Path(str(item.fspath)).parts else "unit"


def _report_dir(suite):
    if suite == "system":
        return Path(
            os.environ.get("EVENTHUB_REPORT_DIR", ROOT / "report" / "system_run")
        )
    return Path(
        os.environ.get("EVENTHUB_UNIT_REPORT_DIR", ROOT / "report" / "unit_run")
    )


def pytest_collection_modifyitems(config, items):
    missing = [i.nodeid for i in items if i.get_closest_marker("req") is None]
    if missing:
        raise pytest.UsageError(
            'Tests without a @pytest.mark.req("<requirement-id>") marker:\n  '
            + "\n  ".join(missing)
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if not (
        report.when == "call" or (report.when == "setup" and report.outcome != "passed")
    ):
        return
    suite = _suite(item)
    shot = None
    driver = getattr(item, "_driver", None)
    if report.failed and driver is not None:
        try:
            folder = _report_dir(suite) / "screenshots"
            folder.mkdir(parents=True, exist_ok=True)
            name = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.nodeid)[:120] + ".png"
            driver.save_screenshot(str(folder / name))
            shot = "screenshots/" + name
        except Exception:
            shot = None
    RESULTS[suite].append(
        {
            "nodeid": item.nodeid,
            "name": item.name,
            "file": item.fspath.basename,
            "outcome": report.outcome,
            "seconds": round(report.duration, 2),
            "reqs": [a for m in item.iter_markers("req") for a in m.args],
            "blackbox": item.get_closest_marker("blackbox") is not None,
            "whitebox": item.get_closest_marker("whitebox") is not None,
            "call5": item.get_closest_marker("call5") is not None,
            "perf": item.get_closest_marker("perf") is not None,
            "doc": (item.function.__doc__ or "").strip().split("\n")[0],
            "failure": (str(report.longrepr)[-1500:] if report.failed else ""),
            "screenshot": shot,
        }
    )


def pytest_sessionfinish(session, exitstatus):
    for suite, rows in RESULTS.items():
        if rows:
            folder = _report_dir(suite)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "results.json").write_text(
                json.dumps(
                    {
                        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "suite": suite,
                        "tests": rows,
                    },
                    indent=1,
                )
            )

"""Write docs/system-test-catalog.md from the recorded results (every test, its requirements, its result)."""

import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def human(name):
    return re.sub(r"^test_", "", name.split("[")[0]).replace("_", " ")


def section(title, tests):
    groups = collections.OrderedDict()
    for t in tests:
        groups.setdefault((t["file"], t["name"].split("[")[0]), []).append(t)
    lines = [
        f"## {title}",
        "",
        "| File | Test case | Cases | Requirements | Technique | Result |",
        "|---|---|---:|---|---|---|",
    ]
    for (file, fn), rows in groups.items():
        first = rows[0]
        tech = (
            ", ".join(
                x
                for x, f in (
                    ("black-box", first["blackbox"]),
                    ("white-box", first["whitebox"]),
                    ("Call 5", first["call5"]),
                    ("load", first["perf"]),
                )
                if f
            )
            or "-"
        )
        ok = all(r["outcome"] == "passed" for r in rows)
        lines.append(
            f"| `{file}` | {human(fn)} | {len(rows)} | {', '.join(first['reqs'])} | {tech} | {'pass' if ok else 'FAIL'} |"
        )
    return "\n".join(lines) + "\n"


system = json.loads((ROOT / "report/system_run/results.json").read_text())
unit = json.loads((ROOT / "report/unit_run/results.json").read_text())
text = (
    f"""# Test case catalog

Generated from the last full run ({system["finished_at"]}) by `scripts/build_test_catalog.py`. Do not edit by hand.
Each row is one test function; parametrized functions show how many cases they cover.
**{len(system["tests"])} browser and load cases + {len(unit["tests"])} unit and integration cases = {len(system["tests"]) + len(unit["tests"])}.**

"""
    + section("Browser (Selenium) and load tests: `tests_system/`", system["tests"])
    + "\n"
    + section("Unit and integration tests: `tests/`", unit["tests"])
)
(ROOT / "docs" / "system-test-catalog.md").write_text(text, encoding="utf-8")
print("catalog:", len(system["tests"]), "system +", len(unit["tests"]), "unit cases")

#!/usr/bin/env python3
"""Every active requirement needs a test that names it, or a written reason it has none.

Thuy (Call 5): 'my bar is every requirement has a test that would actually fail if the
behavior broke.' This script checks the first half of that sentence (a test names it);
scripts/mutation_check.py checks the second half (the test really fails when code breaks).

usage: check_test_traceability.py <repo-path> [--markdown out.md]
"""
import ast
import re
import sys
from pathlib import Path

REQ = re.compile(r"^- \*\*(?P<id>[a-z0-9-]+-\d{3})\*\* \((?P<pattern>[^)]*)\): (?P<text>.+)$")
SUPERSEDED = re.compile(r"\bsuperseded by [a-z0-9-]+-\d{3}\.?\s*$")

# Requirements that cannot be proven by an automated test, and why. Reviewed by hand.
EXEMPT = {
    "purchase-009": "student-organization exception: verification process undefined (Q6), no behaviour exists",
    "purchase-015": "a website cannot prevent screenshots (open-items.md); nothing testable exists",
    "audit-006": "retention policy undecided (Q16); the app deletes nothing and there is no behaviour to assert",
}


def requirements(repo):
    found = {}
    for md in sorted((repo / "features").glob("*/requirements.md")):
        for line in md.read_text(encoding="utf-8").splitlines():
            m = REQ.match(line)
            if m:
                found[m["id"]] = {"superseded": bool(SUPERSEDED.search(m["text"])), "file": md.parent.name}
    return found


def tagged_tests(repo):
    """Map requirement id -> [test ids], read from @pytest.mark.req(...) without importing anything."""
    mapping = {}
    for folder in ("tests", "tests_system"):
        for path in sorted((repo / folder).glob("test_*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                    for deco in node.decorator_list:
                        if (isinstance(deco, ast.Call) and isinstance(deco.func, ast.Attribute)
                                and deco.func.attr == "req"):
                            for arg in deco.args:
                                if isinstance(arg, ast.Constant):
                                    mapping.setdefault(arg.value, []).append(f"{folder}/{path.name}::{node.name}")
    return mapping


def main(argv):
    repo = Path(argv[1]).resolve()
    reqs, tests = requirements(repo), tagged_tests(repo)
    active = {k: v for k, v in reqs.items() if not v["superseded"]}
    uncovered = sorted(k for k in active if k not in tests and k not in EXEMPT)
    unknown = sorted(k for k in tests if k not in reqs)
    on_superseded = sorted(k for k in tests if k in reqs and reqs[k]["superseded"])
    covered = [k for k in active if k in tests]
    print(f"requirements: {len(reqs)} total, {len(active)} active, {len(reqs) - len(active)} superseded")
    print(f"covered by at least one tagged test: {len(covered)}  |  exempt (written reason): {len(EXEMPT)}")
    print(f"tests carrying a requirement tag: {len({t for v in tests.values() for t in v})}")
    for rid in uncovered:
        print(f"   🔴 {rid}: active requirement with no test and no exemption")
    for rid in unknown:
        print(f"   🔴 {rid}: a test names this ID but no such requirement exists")
    for rid in on_superseded:
        print(f"   ⚪ {rid}: tests still point at a superseded requirement (fine for history)")
    if "--markdown" in argv:
        out = Path(argv[argv.index("--markdown") + 1])
        lines = ["| Requirement | Tests naming it | Status |", "|---|---:|---|"]
        for rid in sorted(reqs):
            n = len(tests.get(rid, []))
            status = ("superseded" if reqs[rid]["superseded"] else
                      "exempt: " + EXEMPT[rid] if rid in EXEMPT else "covered" if n else "UNCOVERED")
            lines.append(f"| {rid} | {n} | {status} |")
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    failures = len(uncovered) + len(unknown)
    print(("🟢" if not failures else "🔴"), f"test traceability: {failures} failure(s)")
    return min(failures, 255)


if __name__ == "__main__":
    sys.exit(main(sys.argv))

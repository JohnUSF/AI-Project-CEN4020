"""Break the code on purpose and check that the tests notice.

Thuy (Call 5): 'every requirement has a test that would actually fail if the behavior broke.'
Each mutant below changes ONE thing in a throw-away copy of the project. The fast suite
(tests/) must then fail. A mutant that survives means a requirement is protected by a test
that would not catch the bug, which is the failure Thuy warned about.

usage: python scripts/mutation_check.py [--json report/mutation_check.json]
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (id, requirement it guards, file, exact text to find, replacement)
MUTANTS = [
    # (id, requirement it guards, file, exact text to find, replacement). The text must match the
    # formatted source exactly; a mutant that cannot be applied makes the whole check fail.
    (
        "M01",
        "inventory-004",
        "eventhub/inventory.py",
        "AND available>=?",
        "AND (available>=? OR 1=1)",
    ),
    (
        "M02",
        "purchase-024",
        "eventhub/purchase.py",
        "        if token:\n            prior =",
        "        if False:\n            prior =",
    ),
    (
        "M03",
        "purchase-026",
        "eventhub/purchase.py",
        'prior["currency"]) != (',
        'prior["currency"]) == (',
    ),
    (
        "M04",
        "purchase-028",
        "eventhub/web.py",
        "require_token=True",
        "require_token=False",
    ),
    (
        "M05",
        "pricing-014",
        "eventhub/eligibility.py",
        '.partition("@")[2] == "usf.edu"',
        '.endswith("usf.edu")',
    ),
    (
        "M06",
        "pricing-012",
        "eventhub/eligibility.py",
        'return (email or "").strip().casefold()',
        'return (email or "").strip()',
    ),
    (
        "M07",
        "pricing-008",
        "eventhub/pricing.py",
        "rounding=ROUND_HALF_UP",
        "rounding='ROUND_DOWN'",
    ),
    (
        "M08",
        "pricing-014",
        "eventhub/purchase.py",
        'eligible_for_usf_discount(buyer["email"])',
        'buyer["email"].endswith("usf.edu")',
    ),
    (
        "M09",
        "pricing-015",
        "eventhub/purchase.py",
        'eligible_for_usf_discount(buyer["email"])',
        "__import__('builtins').__dict__.setdefault(('elig', conn.execute('PRAGMA database_list').fetchone()[2], account_id), eligible_for_usf_discount(buyer['email']))",
    ),
    (
        "M10",
        "purchase-032",
        "eventhub/web.py",
        "        if not allowed:\n            if first_block:",
        "        if False:\n            if first_block:",
    ),
    (
        "M11",
        "purchase-032",
        "eventhub/ratelimit.py",
        "len(hits) >= self.max_requests",
        "len(hits) > self.max_requests",
    ),
    (
        "M12",
        "audit-007",
        "eventhub/ratelimit.py",
        "first_block = key not in self._blocked",
        "first_block = True",
    ),
    (
        "M13",
        "purchase-008",
        "eventhub/purchase.py",
        "already + parsed_quantity > purchase_cap",
        "already + parsed_quantity >= purchase_cap",
    ),
    ("M14", "identity-014", "eventhub/web.py", '"\\\\" in target or ', ""),
    (
        "M15",
        "admin-003",
        "eventhub/web.py",
        'g.user["role"] != "administrator"',
        'g.user["role"] == "nobody"',
    ),
    (
        "M16",
        "system-002",
        "eventhub/web.py",
        'if not token or not secrets.compare_digest(\n                str(token), str(session.get("_csrf", ""))\n            ):',
        "if False:",
    ),
    (
        "M17",
        "identity-017",
        "eventhub/identity.py",
        "not EMAIL_SHAPE.fullmatch(email)",
        "'@' not in email",
    ),
    ("M18", "audit-008", "eventhub/purchase.py", 'outcome="success"', 'outcome="ok"'),
    (
        "M19",
        "purchase-019",
        "eventhub/purchase.py",
        "quote.total_minor,\n                code",
        "quote.total_minor + 1,\n                code",
    ),
    (
        "M20",
        "purchase-029",
        "templates/order.html",
        '{{ b.charged }}</strong><span id="charged-note">',
        "{{ order['total_minor'] }}</strong><span id=\"charged-note\">",
    ),
]


def run_suite(workdir):
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests",
            "-q",
            "-p",
            "no:cacheprovider",
            "--no-header",
            "--ignore=tests/test_oversell_stress.py",
            "--ignore=tests/test_requirement_gaps.py",
        ],
        cwd=workdir,
        capture_output=True,
        text=True,
        timeout=600,
    )
    failed = re.findall(r"^(?:FAILED|ERROR) (\S+)", proc.stdout, re.MULTILINE)
    return proc.returncode != 0, failed


def tags_of(workdir, nodeid):
    """Requirement IDs on the test a FAILED line names (read from the source, not imported)."""
    sys.path.insert(0, str(ROOT / "grading"))
    from check_test_traceability import tagged_tests

    wanted = nodeid.split("::")[-1].split("[")[0]
    return {
        req
        for req, tests in tagged_tests(workdir).items()
        if any(t.endswith("::" + wanted) for t in tests)
    }


def main(argv):
    work = Path(tempfile.mkdtemp(prefix="eventhub-mutants-"))
    shutil.copytree(
        ROOT,
        work / "p",
        ignore=shutil.ignore_patterns(
            "report", "instance", "__pycache__", ".git", "tests_system", ".pytest_cache"
        ),
    )
    proj = work / "p"
    broken, base = run_suite(proj)
    if broken:
        print("The unmodified project already fails; fix that first:", base)
        return 2
    results = []
    for mid, req, rel, old, new in MUTANTS:
        path = proj / rel
        original = path.read_text(encoding="utf-8")
        if original.count(old) != 1:
            results.append(
                {
                    "id": mid,
                    "req": req,
                    "file": rel,
                    "status": "NOT APPLIED",
                    "detail": f"expected 1 match, found {original.count(old)}",
                }
            )
            print(f"{mid} ⚪ not applied ({original.count(old)} matches)")
            continue
        path.write_text(original.replace(old, new), encoding="utf-8")
        try:
            killed, failed = run_suite(proj)
            wanted = (
                set(re.split(r"[/,]", req))
                if "/" in req and "-" not in req.split("/")[1]
                else {req}
            )
            named = [f for f in failed if tags_of(proj, f) & wanted]
        finally:
            path.write_text(original, encoding="utf-8")
        status = (
            "SURVIVED"
            if not killed
            else ("KILLED" if named else "KILLED, NOT BY ITS OWN REQUIREMENT'S TEST")
        )
        results.append(
            {
                "id": mid,
                "req": req,
                "file": rel,
                "change": f"{old.strip()[:60]!r} -> {new.strip()[:60]!r}",
                "status": status,
                "failing_tests": len(failed),
                "named_by": (named[0] if named else (failed[0] if failed else "")),
            }
        )
        mark = "🟢" if status == "KILLED" else ("🔴" if status == "SURVIVED" else "🟡")
        print(
            f"{mid} {mark} {status:12.12} {rel:26} {req:16} {len(failed):3} failing; {(named[0] if named else (failed[0] if failed else '-'))[:90]}"
        )
    shutil.rmtree(work, ignore_errors=True)
    unapplied = [r for r in results if r["status"] == "NOT APPLIED"]
    if unapplied:
        print(
            f"\n🔴 {len(unapplied)} mutant(s) could not be applied: "
            + ", ".join(r["id"] for r in unapplied)
        )
    applied = [r for r in results if r["status"] != "NOT APPLIED"]
    killed_n = sum(r["status"].startswith("KILLED") for r in applied)
    named_n = sum(r["status"] == "KILLED" for r in applied)
    print(
        f"\n{killed_n}/{len(applied)} mutants killed by the fast suite; {named_n}/{len(applied)} killed by a test that names the guarded requirement"
    )
    if "--json" in argv:
        Path(argv[argv.index("--json") + 1]).write_text(json.dumps(results, indent=1))
    return 0 if named_n == len(applied) == len(MUTANTS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

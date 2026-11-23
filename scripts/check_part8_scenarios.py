"""Eligibility audit: every feature folder has tagged Gherkin beside requirements.

Requirement-to-test coverage is separately enforced by the course's
grading/check_test_traceability.py. These scenarios are executable in pytest-bdd.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
feature_folders = sorted((ROOT / "features").glob("*/requirements.md"))
total = 0
for requirement_file in feature_folders:
    folder = requirement_file.parent
    requirement_ids = set(
        re.findall(r"\*\*([a-z]+-\d{3})\*\*", requirement_file.read_text())
    )
    scenarios = list((folder / "scenarios").glob("*.feature"))
    assert scenarios, f"No tagged scenario beside {folder.name}/requirements.md"
    tags = set()
    for feature in scenarios:
        content = feature.read_text(encoding="utf-8")
        assert "Scenario:" in content, f"No Gherkin Scenario in {feature}"
        tags.update(re.findall(r"@([a-z]+-\d{3})", content))
        total += content.count("  Scenario:")
    assert tags & requirement_ids, f"No valid requirement tags in {folder}"
    if folder.name == "localization":
        assert requirement_ids <= tags, (
            f"Part 8 requirements without scenarios: {sorted(requirement_ids - tags)}"
        )

assert (ROOT / "tests/test_part8_scenarios.py").is_file()
assert (ROOT / "tests/test_part8_legacy_scenarios.py").is_file()
print(
    f"Tagged Gherkin eligibility: {len(feature_folders)} feature folders, "
    f"{total} executable scenarios, localization has full requirement coverage"
)

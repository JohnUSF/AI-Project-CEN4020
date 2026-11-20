"""Static Part 5/Part 8 check: each localization scenario names a requirement."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
requirements_text = (ROOT / "features/localization/requirements.md").read_text()
reqs = set(re.findall(r"\*\*(localization-\d{3})\*\*", requirements_text))
feature = ROOT / "features/localization/scenarios/spanish_interface.feature"
scenario_text = feature.read_text()
tags = set(re.findall(r"@localization-\d{3}", scenario_text))
missing = reqs - {tag[1:] for tag in tags}
scenario_count = len(re.findall(r"^\s*Scenario:", scenario_text, flags=re.M))
assert scenario_count >= 5, "Missing tagged Gherkin examples"
assert not missing, f"Missing scenario requirement tags: {sorted(missing)}"
assert (ROOT / "tests/test_part8_scenarios.py").is_file(), (
    "Missing executable scenario steps"
)
print(
    f"Part 8 scenario eligibility: {len(reqs)} requirements, "
    f"{scenario_count} tagged scenarios, no gaps"
)

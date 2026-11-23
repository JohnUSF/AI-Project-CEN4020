"""Validate translation drafts before catalog import/release (Call 7 spreadsheet risk).

The external spreadsheet is never loaded at request time. This command checks the
version-controlled JSON reference catalogs and compiled gettext entries; a changed
key or format parameter fails the pre-release check rather than silently shipping.
"""

import json
import string
import sys
from pathlib import Path

from babel.support import Translations

ROOT = Path(__file__).resolve().parents[1]


def placeholders(value):
    return {field for _, field, _, _ in string.Formatter().parse(value) if field}


def validate_catalogs(root=ROOT):
    locales = root / "locales"
    english = json.loads((locales / "en.json").read_text(encoding="utf-8"))
    spanish = json.loads((locales / "es.json").read_text(encoding="utf-8"))
    errors = []
    if set(english) != set(spanish):
        errors.append("English/Spanish message keys differ")
    for key in sorted(set(english) & set(spanish)):
        if placeholders(english[key]) != placeholders(spanish[key]):
            errors.append(f"Placeholders differ for {key}")
    provenance_path = root / "docs" / "part8-translation-provenance.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if set(provenance["entries"]) != set(english):
        errors.append("Translation provenance does not cover all catalog entries")
    for language, locale, entries in (
        ("en", "en_US", english),
        ("es", "es_ES", spanish),
    ):
        gettext = Translations.load(
            str(root / "translations"), locales=[locale], domain="messages"
        )
        for key, phrase in entries.items():
            if gettext.gettext(key) != phrase:
                errors.append(f"Compiled gettext entry disagrees: {language}:{key}")
            source = provenance["entries"].get(key, {}).get(language, {})
            if not source.get("source") or not source.get("review_status"):
                errors.append(f"Missing translation source/status: {language}:{key}")
    return errors


if __name__ == "__main__":
    errors = validate_catalogs()
    if errors:
        print("Translation validation FAILED:", *errors, sep="\n - ")
        sys.exit(1)
    print(
        "Translation validation passed: two complete catalogs, placeholders, "
        "provenance and compiled gettext agree"
    )

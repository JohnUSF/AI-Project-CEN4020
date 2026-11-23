#!/usr/bin/env bash
# Install the exact skill version named in CEN 4020 Part 8 into the project workspace.
set -euo pipefail
PIN=301b02b12bff98e4688e6984af6556802322bbde
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# No auth tokens or passwords are required; cloning public read-only content.
git init -q "$TMP"
git -C "$TMP" remote add origin https://github.com/addyosmani/agent-skills.git
git -C "$TMP" fetch -q --depth 1 origin "$PIN"
git -C "$TMP" checkout -q --detach FETCH_HEAD
ACTUAL="$(git -C "$TMP" rev-parse HEAD)"
if [[ "$ACTUAL" != "$PIN" ]]; then echo "Incorrect pinned skill commit" >&2; exit 2; fi
SOURCE="$TMP/skills/code-review-and-quality"
if [[ ! -f "$SOURCE/SKILL.md" ]]; then echo "Pinned skill is missing" >&2; exit 3; fi
mkdir -p "$ROOT/.agents/skills/code-review-and-quality" "$ROOT/.claude/skills/code-review-and-quality"
cp -R "$SOURCE/". "$ROOT/.agents/skills/code-review-and-quality/"
cp -R "$SOURCE/". "$ROOT/.claude/skills/code-review-and-quality/"
cat > "$ROOT/.agents/skills/code-review-and-quality/PINNED_COMMIT.txt" <<< "$PIN"
cat > "$ROOT/.claude/skills/code-review-and-quality/PINNED_COMMIT.txt" <<< "$PIN"
echo "Pinned code-review-and-quality skill installed at $PIN"
echo "Review only; do not configure unattended changes or put credentials in agent settings."

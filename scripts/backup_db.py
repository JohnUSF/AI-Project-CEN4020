#!/usr/bin/env python3
"""One-command safe SQLite backup; configure scheduling/owner separately."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import os
from pathlib import Path

from eventhub.backups import create_backup

p = argparse.ArgumentParser()
p.add_argument(
    "--database", default=os.environ.get("EVENTHUB_DB", "instance/eventhub.sqlite3")
)
p.add_argument("--output", required=True)
a = p.parse_args()
manifest = create_backup(Path(a.database), Path(a.output))
print("Backup verified:", a.output, "sha256", manifest["sha256"])

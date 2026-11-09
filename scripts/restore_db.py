#!/usr/bin/env python3
"""Explicit offline restore; always stop the app first."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eventhub.backups import restore_backup

p = argparse.ArgumentParser()
p.add_argument("--backup", required=True)
p.add_argument("--destination", required=True)
p.add_argument("--confirm-restore", action="store_true")
a = p.parse_args()
restore_backup(a.backup, a.destination, confirmed=a.confirm_restore)
print("Restore verified:", a.destination)

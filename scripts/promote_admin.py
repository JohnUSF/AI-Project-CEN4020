"""Run after creating an account: python scripts/promote_admin.py email@domain"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eventhub.db import connect
from eventhub.identity import promote_from_cli

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/promote_admin.py account@example.com")
    repo = Path(__file__).resolve().parents[1]
    db_path = os.environ.get("EVENTHUB_DB", str(repo / "instance" / "eventhub.sqlite3"))
    with connect(db_path) as connection:
        promote_from_cli(connection, sys.argv[1])
    print("Administrator role granted using a server-only command.")

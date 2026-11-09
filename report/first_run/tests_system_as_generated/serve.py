"""Start the real EventHub app on a given port (used by the system-test fixtures).

Settings come from the same EVENTHUB_* environment variables the production entry
point reads, so the tests exercise the application exactly as it would be run.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eventhub.web import create_app

if __name__ == "__main__":
    create_app().run(
        host="127.0.0.1",
        port=int(sys.argv[1]),
        threaded=True,
        debug=False,
        use_reloader=False,
    )

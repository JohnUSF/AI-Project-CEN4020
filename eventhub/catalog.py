"""Events and search; no browser-specific code."""

from .errors import NotFound


def list_events(conn, term=""):
    term = (term or "").strip()
    if not term:
        return conn.execute(
            "SELECT * FROM events ORDER BY starts_at,id"
        ).fetchall(), False
    # Escape SQL wildcards: a student's search text is literal text.
    escaped = term.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    rows = conn.execute(
        """SELECT * FROM events
        WHERE LOWER(artist) LIKE ? ESCAPE '\\' OR LOWER(venue) LIKE ? ESCAPE '\\'
        ORDER BY starts_at,id""",
        (f"%{escaped}%", f"%{escaped}%"),
    ).fetchall()
    if rows:
        return rows, False
    return conn.execute("SELECT * FROM events ORDER BY starts_at,id").fetchall(), True


def get_event(conn, event_id):
    row = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if row is None:
        raise NotFound("Event not found")
    return row

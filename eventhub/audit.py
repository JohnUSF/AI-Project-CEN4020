"""Single owner of immutable audit trail writes and admin reads."""

def record(conn, *, kind, account_id, event_id, quantity, currency, outcome, detail=''):
    conn.execute('''INSERT INTO audit(kind, account_id, event_id, quantity, currency, outcome, detail)
                 VALUES (?,?,?,?,?,?,?)''', (kind, account_id, event_id, quantity, currency, outcome, detail[:250]))


def recent(conn, limit=100):
    return conn.execute('SELECT * FROM audit ORDER BY id DESC LIMIT ?', (min(limit, 250),)).fetchall()

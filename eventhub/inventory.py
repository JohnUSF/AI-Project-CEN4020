"""One atomic conditional decrement; called within the purchase transaction."""
from .errors import SoldOut


def take_tickets(conn, event_id, quantity):
    cursor = conn.execute('''UPDATE events SET available=available-?
        WHERE id=? AND available>=?''', (quantity, event_id, quantity))
    if cursor.rowcount != 1:
        raise SoldOut('Sold out: not enough tickets remain')

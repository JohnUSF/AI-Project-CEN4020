"""Thuy: 'I can generate load against the purchase path; I cannot tell you pass or fail without a number.'

No customer number exists (open item Q13). The budget below is a PLACEHOLDER chosen by the
team so the measurement has something to be judged against. It is not an approved requirement.
Change EVENTHUB_PERF_P95_MS (and EVENTHUB_PERF_BUYERS) when Marcus supplies the real sentence.
This test uses plain HTTP, not Selenium: a browser would measure Chrome, not the server.
"""
import http.cookiejar
import json
import os
import re
import statistics
import threading
import time
import urllib.parse
import urllib.request

import pytest

from .conftest import PASSWORD, REPORT_DIR

BUYERS = int(os.environ.get('EVENTHUB_PERF_BUYERS', '20'))
PURCHASES_EACH = int(os.environ.get('EVENTHUB_PERF_PURCHASES_EACH', '5'))
P95_BUDGET_MS = float(os.environ.get('EVENTHUB_PERF_P95_MS', '500'))      # PLACEHOLDER (Q13)


class Session:
    def __init__(self, base):
        self.base = base
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def get(self, path):
        with self.opener.open(self.base + path, timeout=30) as r:
            return r.read().decode()

    def post(self, path, fields):
        data = urllib.parse.urlencode(fields).encode()
        with self.opener.open(urllib.request.Request(self.base + path, data=data), timeout=30) as r:
            return r.geturl(), r.read().decode()


def field(html, name):
    return re.search(rf'name="{name}" value="([^"]+)"', html).group(1)


@pytest.mark.req("system-006")
@pytest.mark.perf
def test_purchase_latency_with_concurrent_buyers_against_the_placeholder_budget(server):
    event = server.new_event(available=BUYERS * PURCHASES_EACH + 10, price_minor=1500)
    users = [server.new_user() for _ in range(BUYERS)]
    sessions = []
    for u in users:                                                  # sign-in cost is not part of the measurement
        s = Session(server.url)
        page = s.get('/login')
        s.post('/login', {'csrf_token': field(page, 'csrf_token'), 'email': u['email'], 'password': PASSWORD, 'next': ''})
        sessions.append(s)

    latencies, failures = [], []
    gate = threading.Barrier(BUYERS)

    def buyer(s):
        gate.wait()
        for _ in range(PURCHASES_EACH):
            page = s.get(f'/checkout/{event}')
            fields = {'csrf_token': field(page, 'csrf_token'), 'purchase_token': field(page, 'purchase_token'),
                      'quantity': '1', 'currency': 'EUR'}
            started = time.perf_counter()
            try:
                url, body = s.post(f'/checkout/{event}', fields)
                elapsed = (time.perf_counter() - started) * 1000
                (latencies if '/orders/' in url else failures).append(elapsed if '/orders/' in url else body[:80])
            except Exception as exc:
                failures.append(repr(exc))

    started = time.perf_counter()
    threads = [threading.Thread(target=buyer, args=(s,)) for s in sessions]
    [t.start() for t in threads]
    [t.join() for t in threads]
    wall = time.perf_counter() - started

    latencies.sort()
    p95 = latencies[max(0, int(len(latencies) * 0.95) - 1)] if latencies else float('inf')
    summary = {'concurrent_buyers': BUYERS, 'purchases': len(latencies), 'failures': len(failures),
               'p50_ms': round(statistics.median(latencies), 1) if latencies else None, 'p95_ms': round(p95, 1),
               'max_ms': round(max(latencies), 1) if latencies else None,
               'wall_seconds': round(wall, 2), 'budget_p95_ms': P95_BUDGET_MS,
               'budget_status': 'PLACEHOLDER - not customer approved (Q13)'}
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / 'performance.json').write_text(json.dumps(summary, indent=1))
    print('\nPERFORMANCE', json.dumps(summary))

    assert failures == [], failures[:3]
    assert len(latencies) == BUYERS * PURCHASES_EACH
    assert server.scalar('SELECT available FROM events WHERE id=?', (event,)) == 10          # nothing oversold or lost
    assert server.scalar('SELECT COUNT(*) FROM orders WHERE event_id=?', (event,)) == BUYERS * PURCHASES_EACH
    assert p95 <= P95_BUDGET_MS, f'p95 {p95:.0f} ms is over the placeholder budget of {P95_BUDGET_MS:.0f} ms'

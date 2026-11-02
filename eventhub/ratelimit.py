"""Per-account sliding-window limiter for purchase requests (Call 5, Kenji's finding 2).

The numbers are provisional (open item Q19): the customer has not said how many
purchase requests per minute is too many. They live in application settings.
State is held in this process's memory, so it resets on restart and is not shared
between worker processes. See docs/decisions/ADR-007-purchase-rate-limit.md.
"""

import math
import threading
import time
from collections import defaultdict, deque

MAX_TRACKED_ACCOUNTS = 10000


class RateLimiter:
    def __init__(self, max_requests, window_seconds, clock=time.monotonic):
        self.max_requests = int(max_requests or 0)
        self.window = float(window_seconds or 0)
        self._clock = clock
        self._lock = threading.Lock()
        self._hits = defaultdict(deque)
        self._blocked = set()

    @property
    def enabled(self):
        return self.max_requests > 0 and self.window > 0

    def check(self, key):
        """Count one request for `key`.

        Returns (allowed, retry_after_seconds, first_block). `first_block` is True
        only for the first rejected request of a blocked period, so the caller can
        write one audit entry per period instead of one per rejected request.
        Rejected requests are not counted, so hammering does not extend the block.
        """
        if not self.enabled:
            return True, 0, False
        now = self._clock()
        with self._lock:
            hits = self._hits[key]
            while hits and hits[0] <= now - self.window:
                hits.popleft()
            if len(hits) >= self.max_requests:
                retry_after = max(1, math.ceil(hits[0] + self.window - now))
                first_block = key not in self._blocked
                self._blocked.add(key)
                return False, retry_after, first_block
            hits.append(now)
            self._blocked.discard(key)
            if len(self._hits) > MAX_TRACKED_ACCOUNTS:
                self._forget_idle(now)
            return True, 0, False

    def _forget_idle(self, now):
        idle = [k for k, d in self._hits.items() if not d or d[-1] <= now - self.window]
        for key in idle:
            del self._hits[key]
            self._blocked.discard(key)

    def reset(self):
        with self._lock:
            self._hits.clear()
            self._blocked.clear()

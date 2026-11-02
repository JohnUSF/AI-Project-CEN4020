"""Kenji's finding 2: nothing limited how fast purchase requests could arrive."""

import pytest

from eventhub.ratelimit import RateLimiter


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


@pytest.mark.req("purchase-032")
@pytest.mark.call5
def test_requests_up_to_the_limit_pass_and_the_next_is_refused():
    limiter = RateLimiter(3, 60, clock=FakeClock())
    assert [limiter.check("a")[0] for _ in range(3)] == [True, True, True]
    allowed, retry_after, _ = limiter.check("a")
    assert allowed is False and retry_after == 60


@pytest.mark.req("purchase-032")
@pytest.mark.call5
def test_retry_after_counts_down_and_the_window_slides():
    clock = FakeClock()
    limiter = RateLimiter(2, 60, clock=clock)
    limiter.check("a")
    clock.now += 20
    limiter.check("a")
    clock.now += 10
    allowed, retry_after, _ = limiter.check("a")
    assert not allowed and retry_after == 30  # first hit leaves the window in 30 s
    clock.now += 30
    assert limiter.check("a")[0] is True


@pytest.mark.req("purchase-032")
@pytest.mark.call5
def test_accounts_are_limited_independently():
    limiter = RateLimiter(1, 60, clock=FakeClock())
    assert limiter.check("a")[0] and not limiter.check("a")[0]
    assert limiter.check("b")[0]


@pytest.mark.req("audit-007")
@pytest.mark.call5
def test_only_the_first_rejection_of_a_blocked_period_is_flagged_for_the_audit_log():
    clock = FakeClock()
    limiter = RateLimiter(1, 60, clock=clock)
    limiter.check("a")
    flags = [limiter.check("a")[2] for _ in range(200)]
    assert flags[0] is True and not any(flags[1:])
    clock.now += 61
    assert limiter.check("a")[0]  # allowed again, period over
    assert limiter.check("a")[2] is True  # a new period flags once more


@pytest.mark.req("purchase-032")
@pytest.mark.call5
def test_hammering_does_not_extend_the_block():
    clock = FakeClock()
    limiter = RateLimiter(1, 60, clock=clock)
    limiter.check("a")
    for _ in range(500):
        clock.now += 0.05  # 25 seconds of hammering
        limiter.check("a")
    clock.now = 1000.0 + 60.01
    assert limiter.check("a")[0] is True


@pytest.mark.req("purchase-032")
@pytest.mark.whitebox
@pytest.mark.parametrize("limit,window", [(0, 60), (5, 0), (None, 60)])
def test_a_zero_setting_turns_the_limiter_off(limit, window):
    limiter = RateLimiter(limit, window, clock=FakeClock())
    assert limiter.enabled is False
    assert all(limiter.check("a")[0] for _ in range(1000))

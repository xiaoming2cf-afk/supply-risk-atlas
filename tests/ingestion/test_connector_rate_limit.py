from __future__ import annotations

from sra_core.ingestion.connectors.rate_limit import RateLimiter


def test_rate_limiter_reports_and_sleeps_bounded_wait() -> None:
    now = 100.0
    sleeps: list[float] = []

    def clock() -> float:
        return now

    limiter = RateLimiter(min_interval_seconds=2.0, sleep=sleeps.append, clock=clock)

    assert limiter.acquire() == 0.0
    assert limiter.acquire() == 2.0
    assert sleeps == [2.0]


from __future__ import annotations

import pytest

from sra_core.ingestion.connectors.errors import ConnectorRateLimitError
from sra_core.ingestion.connectors.rate_limit import InMemoryRateLimiter, RateLimitPolicy


def test_rate_limiter_enforces_windowed_request_limit() -> None:
    limiter = InMemoryRateLimiter(RateLimitPolicy(max_requests=2, per_seconds=10))

    limiter.check("sec_edgar_lite", now=100.0)
    limiter.check("sec_edgar_lite", now=101.0)

    with pytest.raises(ConnectorRateLimitError):
        limiter.check("sec_edgar_lite", now=102.0)


def test_rate_limiter_expires_old_events() -> None:
    limiter = InMemoryRateLimiter(RateLimitPolicy(max_requests=1, per_seconds=5))

    limiter.check("gdelt_semiconductor_lite", now=100.0)
    limiter.check("gdelt_semiconductor_lite", now=106.0)


def test_rate_limit_policy_validates_bounds() -> None:
    with pytest.raises(ValueError):
        RateLimitPolicy(max_requests=0).validate()
    with pytest.raises(ValueError):
        RateLimitPolicy(per_seconds=0).validate()


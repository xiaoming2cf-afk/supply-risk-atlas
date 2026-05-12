from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from time import monotonic

from sra_core.ingestion.connectors.errors import ConnectorRateLimitError


@dataclass(frozen=True)
class RateLimitPolicy:
    max_requests: int = 1
    per_seconds: float = 1.0

    def validate(self) -> None:
        if self.max_requests < 1:
            raise ValueError("max_requests must be positive")
        if self.per_seconds <= 0:
            raise ValueError("per_seconds must be positive")


class InMemoryRateLimiter:
    def __init__(self, policy: RateLimitPolicy | None = None) -> None:
        self.policy = policy or RateLimitPolicy()
        self.policy.validate()
        self._events: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, *, now: float | None = None) -> None:
        current = monotonic() if now is None else now
        window_start = current - self.policy.per_seconds
        events = self._events[key]
        while events and events[0] <= window_start:
            events.popleft()
        if len(events) >= self.policy.max_requests:
            raise ConnectorRateLimitError(f"rate limit exceeded for {key}")
        events.append(current)


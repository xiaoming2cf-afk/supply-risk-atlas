from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Callable


@dataclass
class RateLimiter:
    min_interval_seconds: float
    sleep: Callable[[float], None] = time.sleep
    clock: Callable[[], float] = time.monotonic
    _last_request_at: float | None = None

    def wait_time(self) -> float:
        if self._last_request_at is None:
            return 0.0
        elapsed = self.clock() - self._last_request_at
        return max(0.0, self.min_interval_seconds - elapsed)

    def acquire(self) -> float:
        wait = self.wait_time()
        if wait > 0:
            self.sleep(wait)
        self._last_request_at = self.clock()
        return wait


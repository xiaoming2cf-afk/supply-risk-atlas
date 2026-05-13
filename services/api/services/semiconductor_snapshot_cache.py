from __future__ import annotations

from functools import lru_cache
from typing import Any

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot


@lru_cache(maxsize=1)
def fixture_snapshot_for_services() -> Any:
    return build_semiconductor_fixture_snapshot()

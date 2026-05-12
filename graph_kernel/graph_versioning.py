from __future__ import annotations

from datetime import datetime
from typing import Any

from sra_core.contracts.semiconductor import canonical_json_bytes, payload_hash, parse_semirisk_time


def canonical_graph_hash(payload: Any) -> str:
    return payload_hash(payload)


def deterministic_graph_version(
    *,
    namespace: str,
    as_of_time: datetime | str,
    graph_payload: dict[str, Any],
) -> str:
    as_of = parse_semirisk_time(as_of_time)
    stamp = as_of.strftime("%Y%m%dT%H%M%SZ")
    digest = payload_hash(
        {
            "namespace": namespace,
            "as_of_time": as_of.isoformat(),
            "graph_payload": graph_payload,
        }
    )[:12]
    return f"{namespace}_{stamp}_{digest}"


def canonical_graph_bytes(payload: Any) -> bytes:
    return canonical_json_bytes(payload)

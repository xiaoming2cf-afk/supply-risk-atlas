from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sra_core.ingestion.connectors.result import ConnectorFetchResult, stable_payload_hash


@dataclass(frozen=True)
class ConnectorCachePolicy:
    enabled: bool = True
    store_records: bool = False


class ConnectorCache:
    def __init__(self, cache_dir: str | Path, policy: ConnectorCachePolicy | None = None) -> None:
        self.cache_dir = Path(cache_dir)
        self.policy = policy or ConnectorCachePolicy()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def key_for(self, *, source_id: str, params: dict[str, Any]) -> str:
        return stable_payload_hash({"source_id": source_id, "params": params})

    def path_for(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def write_metadata(self, *, key: str, result: ConnectorFetchResult) -> Path | None:
        if not self.policy.enabled:
            return None
        public_result = result.to_public_dict()
        if not self.policy.store_records:
            public_result["records"] = []
        path = self.path_for(key)
        path.write_text(json.dumps(public_result, sort_keys=True, indent=2), encoding="utf-8")
        return path

    def read_metadata(self, *, key: str) -> dict[str, Any] | None:
        path = self.path_for(key)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))


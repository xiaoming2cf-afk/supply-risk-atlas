from __future__ import annotations

import json
from pathlib import Path

from sra_core.ingestion.connectors.base import ConnectorFetchResult


class ConnectorMetadataCache:
    def __init__(self, cache_dir: str | Path) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def put(self, result: ConnectorFetchResult) -> Path:
        path = self.cache_dir / f"{result.source_id}_{result.payload_hash[:16]}.json"
        path.write_text(json.dumps(result.metadata(), sort_keys=True, indent=2), encoding="utf-8")
        return path

    def get(self, source_id: str, payload_hash_value: str) -> dict[str, object] | None:
        path = self.cache_dir / f"{source_id}_{payload_hash_value[:16]}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))


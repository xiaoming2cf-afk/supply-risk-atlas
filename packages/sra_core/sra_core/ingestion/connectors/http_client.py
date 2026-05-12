from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Any

from sra_core.ingestion.connectors.errors import ConnectorPayloadError


@dataclass(frozen=True)
class SafeHttpClient:
    timeout_seconds: float = 10.0
    max_response_bytes: int = 256_000
    user_agent: str = "SupplyRiskAtlas research connector; contact=not-configured"

    def get_json(self, url: str, *, headers: dict[str, str] | None = None) -> Any:
        request_headers = {"User-Agent": self.user_agent, **(headers or {})}
        request = urllib.request.Request(url, headers=request_headers, method="GET")
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > self.max_response_bytes:
                raise ConnectorPayloadError("connector response exceeds configured byte limit")
            payload = response.read(self.max_response_bytes + 1)
        if len(payload) > self.max_response_bytes:
            raise ConnectorPayloadError("connector response exceeds configured byte limit")
        return json.loads(payload.decode("utf-8"))


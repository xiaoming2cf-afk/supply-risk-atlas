from __future__ import annotations

from urllib.error import URLError
from urllib.request import Request, urlopen

from sra_core.ingestion.connectors.errors import ConnectorFetchError, ConnectorPolicyError


def bounded_http_get(
    url: str,
    *,
    timeout_seconds: float,
    max_bytes: int,
    user_agent: str,
) -> bytes:
    if not url.startswith("https://"):
        raise ConnectorPolicyError("connector fetch URL must be https")
    if max_bytes <= 0 or max_bytes > 8 * 1024 * 1024:
        raise ConnectorPolicyError("max_bytes must be bounded")
    request = Request(url, headers={"User-Agent": user_agent})
    chunks: list[bytes] = []
    total = 0
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            while True:
                chunk = response.read(min(64 * 1024, max_bytes - total + 1))
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise ConnectorPolicyError("connector response exceeded max_bytes")
                chunks.append(chunk)
    except URLError as exc:
        raise ConnectorFetchError("connector fetch failed") from exc
    return b"".join(chunks)


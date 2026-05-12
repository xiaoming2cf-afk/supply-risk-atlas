from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal

from sra_core.contracts.semiconductor import payload_hash
from sra_core.ingestion.connectors.errors import ConnectorPolicyError, ConnectorUnavailableError


ConnectorMode = Literal["fixture", "dry_run", "live", "unavailable"]


@dataclass(frozen=True)
class ConnectorRequest:
    source_id: str
    source_url: str
    provenance_url: str
    license_ref: str
    mode: ConnectorMode = "unavailable"
    timeout_seconds: float = 10.0
    max_bytes: int = 512_000
    allow_raw_storage: bool = False
    fixture_payload: dict[str, Any] | None = None


@dataclass(frozen=True)
class ConnectorFetchResult:
    source_id: str
    source_url: str
    retrieved_at: str
    payload_hash: str
    provenance_url: str
    license_ref: str
    status: str
    raw_payload_summary: str
    payload: dict[str, Any] | None = None

    def metadata(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_url": self.source_url,
            "retrieved_at": self.retrieved_at,
            "payload_hash": self.payload_hash,
            "provenance_url": self.provenance_url,
            "license_ref": self.license_ref,
            "status": self.status,
            "raw_payload_summary": self.raw_payload_summary,
            "raw_payload_stored": False,
        }


class PublicEvidenceConnector:
    source_id: str

    def __init__(self, source_id: str) -> None:
        self.source_id = source_id

    def fetch(self, request: ConnectorRequest) -> ConnectorFetchResult:
        if request.source_id != self.source_id:
            raise ConnectorPolicyError(f"connector source mismatch: {request.source_id}")
        if request.timeout_seconds <= 0 or request.timeout_seconds > 60:
            raise ConnectorPolicyError("timeout_seconds must be between 0 and 60")
        if request.max_bytes <= 0 or request.max_bytes > 8 * 1024 * 1024:
            raise ConnectorPolicyError("max_bytes must be bounded")
        if request.mode == "unavailable":
            return self._metadata_only_result(request, status="unavailable")
        if request.mode == "dry_run":
            return self._metadata_only_result(request, status="dry_run")
        if request.mode == "fixture":
            if request.fixture_payload is None:
                raise ConnectorPolicyError("fixture mode requires fixture_payload")
            return self._payload_result(request, request.fixture_payload, status="fixture")
        if request.mode == "live":
            return self.fetch_live(request)
        raise ConnectorPolicyError(f"unsupported connector mode: {request.mode}")

    def fetch_live(self, request: ConnectorRequest) -> ConnectorFetchResult:
        raise ConnectorUnavailableError("live connector is disabled unless explicitly implemented")

    def _metadata_only_result(self, request: ConnectorRequest, *, status: str) -> ConnectorFetchResult:
        return ConnectorFetchResult(
            source_id=request.source_id,
            source_url=request.source_url,
            retrieved_at=_utc_now(),
            payload_hash=payload_hash(
                {
                    "source_id": request.source_id,
                    "source_url": request.source_url,
                    "status": status,
                }
            ),
            provenance_url=request.provenance_url,
            license_ref=request.license_ref,
            status=status,
            raw_payload_summary=f"{status} connector metadata only; no raw payload fetched.",
            payload=None,
        )

    def _payload_result(
        self,
        request: ConnectorRequest,
        payload: dict[str, Any],
        *,
        status: str,
    ) -> ConnectorFetchResult:
        return ConnectorFetchResult(
            source_id=request.source_id,
            source_url=request.source_url,
            retrieved_at=_utc_now(),
            payload_hash=payload_hash(payload),
            provenance_url=request.provenance_url,
            license_ref=request.license_ref,
            status=status,
            raw_payload_summary=_summary_for_payload(payload),
            payload=payload,
        )


def _summary_for_payload(payload: dict[str, Any]) -> str:
    keys = sorted(str(key) for key in payload.keys())[:12]
    return f"Fixture payload with keys: {', '.join(keys)}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sra_core.geo.normalize import sanitize_api_visible_text


PROMPT_INJECTION_PATTERNS = (
    re.compile(r"</?\s*script\s*>?", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"system\s+prompt", re.IGNORECASE),
    re.compile(r"developer\s+message", re.IGNORECASE),
)


def stable_payload_hash(payload: Any) -> str:
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sanitize_external_text(value: Any, *, max_length: int = 512) -> str:
    text = "" if value is None else str(value)
    for pattern in PROMPT_INJECTION_PATTERNS:
        text = pattern.sub("[removed]", text)
    text = text.replace("<", "").replace(">", "")
    text = sanitize_api_visible_text(text)
    text = " ".join(text.split())
    if len(text) > max_length:
        return f"{text[: max_length - 3]}..."
    return text


@dataclass(frozen=True)
class ConnectorRecord:
    source_id: str
    source_record_id: str
    retrieved_at: str
    as_of_time: str
    payload_hash: str
    provenance_url: str
    license_or_terms_ref: str
    payload_summary: str
    payload_stored: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(
        cls,
        *,
        source_id: str,
        source_record_id: str,
        payload: Any,
        provenance_url: str,
        license_or_terms_ref: str,
        as_of_time: str | None = None,
        retrieved_at: str | None = None,
        payload_summary: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "ConnectorRecord":
        return cls(
            source_id=source_id,
            source_record_id=source_record_id,
            retrieved_at=retrieved_at or utc_now_iso(),
            as_of_time=as_of_time or retrieved_at or utc_now_iso(),
            payload_hash=stable_payload_hash(payload),
            provenance_url=provenance_url,
            license_or_terms_ref=license_or_terms_ref,
            payload_summary=sanitize_external_text(payload_summary or _summary_from_payload(payload)),
            payload_stored=False,
            metadata=sanitize_metadata(metadata or {}),
        )

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_record_id": self.source_record_id,
            "retrieved_at": self.retrieved_at,
            "as_of_time": self.as_of_time,
            "payload_hash": self.payload_hash,
            "provenance_url": self.provenance_url,
            "license_or_terms_ref": self.license_or_terms_ref,
            "payload_summary": self.payload_summary,
            "payload_stored": self.payload_stored,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ConnectorFetchResult:
    source_id: str
    mode: str
    status: str
    records: tuple[ConnectorRecord, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "mode": self.mode,
            "status": self.status,
            "record_count": len(self.records),
            "records": [record.to_public_dict() for record in self.records],
            "warnings": list(self.warnings),
            "metadata": self.metadata,
        }

    @classmethod
    def unavailable(
        cls,
        *,
        source_id: str,
        mode: str,
        reason: str,
        warnings: tuple[str, ...] = (),
    ) -> "ConnectorFetchResult":
        return cls(
            source_id=source_id,
            mode=mode,
            status="unavailable",
            warnings=(reason, *warnings),
        )


def _summary_from_payload(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("summary", "title", "name", "description"):
            if key in payload:
                return str(payload[key])
        return ", ".join(str(key) for key in sorted(payload)[:8])
    if isinstance(payload, list):
        return f"{len(payload)} records"
    return str(payload)


def sanitize_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            sanitize_external_text(key, max_length=80): sanitize_metadata(item)
            for key, item in value.items()
            if "body" not in str(key).lower() and "raw_payload" not in str(key).lower()
        }
    if isinstance(value, list):
        return [sanitize_metadata(item) for item in value[:100]]
    if isinstance(value, str):
        return sanitize_external_text(value)
    if isinstance(value, int | float | bool) or value is None:
        return value
    return sanitize_external_text(value)

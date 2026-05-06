from __future__ import annotations

from typing import Any
from uuid import uuid4

from sra_core.contracts.domain import ApiEnvelope, ApiError, ApiSourceMetadata, VersionMetadata


def _source_metadata(metadata: VersionMetadata) -> ApiSourceMetadata:
    if metadata.data_mode == "real":
        return ApiSourceMetadata(
            name="Public no-key real source manifest",
            lineage_ref=metadata.lineage_ref,
            license="Mixed public source licenses; see source_registry",
        )
    if metadata.data_mode == "synthetic":
        return ApiSourceMetadata(
            name="Synthetic test fixture",
            lineage_ref=metadata.lineage_ref,
            license="Test-only generated data; not production evidence",
        )
    return ApiSourceMetadata(
        name="Unavailable API source metadata",
        lineage_ref=metadata.lineage_ref,
        license="No business payload rendered until a real API envelope is accepted.",
    )


def make_envelope(
    data: Any,
    *,
    metadata: VersionMetadata,
    request_id: str | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    envelope = ApiEnvelope(
        request_id=request_id or f"req_{uuid4().hex[:12]}",
        status="success",
        data=data,
        metadata=metadata,
        warnings=warnings or [],
        errors=[],
        mode=metadata.data_mode,
        source_status=metadata.freshness_status,
        source=_source_metadata(metadata),
    )
    return envelope.model_dump(mode="json")


def make_error_envelope(
    code: str,
    message: str,
    *,
    metadata: VersionMetadata,
    request_id: str | None = None,
    field: str | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    envelope = ApiEnvelope(
        request_id=request_id or f"req_{uuid4().hex[:12]}",
        status="error",
        data=None,
        metadata=metadata,
        warnings=warnings or [],
        errors=[ApiError(code=code, message=message, field=field)],
        mode=metadata.data_mode,
        source_status=metadata.freshness_status,
        source=_source_metadata(metadata),
    )
    return envelope.model_dump(mode="json")

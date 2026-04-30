from __future__ import annotations

from typing import Any
from uuid import uuid4

from sra_core.contracts.domain import ApiEnvelope, ApiError, VersionMetadata


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
    )
    return envelope.model_dump(mode="json")

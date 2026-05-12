from __future__ import annotations

from typing import Any

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from sra_core.api.envelope import make_envelope, make_error_envelope
from sra_core.reports.investigation import REPORT_VERSION, generate_investigation_report
from services.api.runtime.errors import ControlledApiError
from services.api.security.validation import sanitized_payload, validate_report_payload
from services.api.services.common import semiconductor_metadata
from services.api.services.run_service import RUN_CACHE


def route_investigation_report(
    payload: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        payload = validate_report_payload(payload)
        snapshot = build_semiconductor_fixture_snapshot()
        result = sanitized_payload(generate_investigation_report(payload))
    except ControlledApiError as exc:
        return make_error_envelope(
            exc.code,
            str(exc),
            metadata=semiconductor_metadata(feature_version=REPORT_VERSION),
            request_id=request_id,
            field=exc.field,
            warnings=["fixture_graph:not_production_ready"],
        )
    except Exception as exc:
        return make_error_envelope(
            "investigation_report_unavailable",
            "Investigation report could not be generated from the SemiRisk fixture graph.",
            metadata=semiconductor_metadata(feature_version=REPORT_VERSION),
            request_id=request_id,
            warnings=[
                f"report_failed:{type(exc).__name__}",
                "fixture_graph:not_production_ready",
            ],
        )
    response = make_envelope(
        result,
        metadata=semiconductor_metadata(snapshot, feature_version=REPORT_VERSION),
        request_id=request_id,
        warnings=result.get("warnings", ["fixture_graph:not_production_ready"]),
    )
    RUN_CACHE.put_summary("investigation_report", response)
    return response


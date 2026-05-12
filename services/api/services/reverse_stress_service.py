from __future__ import annotations

from typing import Any

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.simulation.reverse_stress import run_reverse_stress
from ml.simulation.scenario_schema import REVERSE_SIMULATION_VERSION, ScenarioValidationError
from sra_core.api.envelope import make_envelope, make_error_envelope
from services.api.runtime.errors import ControlledApiError
from services.api.security.validation import validate_reverse_payload
from services.api.services.common import semiconductor_metadata
from services.api.services.run_service import RUN_CACHE


def route_reverse_scenario(
    payload: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        payload = validate_reverse_payload(payload)
        snapshot = build_semiconductor_fixture_snapshot()
        result = run_reverse_stress(payload, snapshot=snapshot)
    except ControlledApiError as exc:
        return make_error_envelope(
            exc.code,
            str(exc),
            metadata=semiconductor_metadata(feature_version=REVERSE_SIMULATION_VERSION),
            request_id=request_id,
            field=exc.field,
            warnings=["fixture_graph:not_production_ready"],
        )
    except ScenarioValidationError as exc:
        return make_error_envelope(
            "reverse_scenario_validation_error",
            str(exc),
            metadata=semiconductor_metadata(feature_version=REVERSE_SIMULATION_VERSION),
            request_id=request_id,
            field=exc.field,
            warnings=["fixture_graph:not_production_ready"],
        )
    except Exception as exc:
        return make_error_envelope(
            "reverse_scenario_unavailable",
            "Reverse stress search could not run against the SemiRisk fixture graph.",
            metadata=semiconductor_metadata(feature_version=REVERSE_SIMULATION_VERSION),
            request_id=request_id,
            warnings=[
                f"reverse_scenario_failed:{type(exc).__name__}",
                "fixture_graph:not_production_ready",
            ],
        )
    response = make_envelope(
        result,
        metadata=semiconductor_metadata(snapshot, feature_version=REVERSE_SIMULATION_VERSION),
        request_id=request_id,
        warnings=result.get("warnings", ["fixture_graph:not_production_ready"]),
    )
    RUN_CACHE.put_summary("reverse_stress", response)
    return response


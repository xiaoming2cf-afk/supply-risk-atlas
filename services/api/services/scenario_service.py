from __future__ import annotations

from typing import Any

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.simulation.monte_carlo import run_forward_monte_carlo
from ml.simulation.scenario_schema import FORWARD_SIMULATION_VERSION, ScenarioValidationError
from sra_core.api.envelope import make_envelope, make_error_envelope
from services.api.runtime.errors import ControlledApiError
from services.api.security.validation import validate_forward_payload
from services.api.services.common import semiconductor_metadata
from services.api.services.run_service import RUN_CACHE


def route_forward_scenario(
    payload: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        payload = validate_forward_payload(payload)
        snapshot = build_semiconductor_fixture_snapshot()
        result = run_forward_monte_carlo(payload, snapshot=snapshot)
    except ControlledApiError as exc:
        return make_error_envelope(
            exc.code,
            str(exc),
            metadata=semiconductor_metadata(feature_version=FORWARD_SIMULATION_VERSION),
            request_id=request_id,
            field=exc.field,
            warnings=["fixture_graph:not_production_ready"],
        )
    except ScenarioValidationError as exc:
        return make_error_envelope(
            "forward_scenario_validation_error",
            str(exc),
            metadata=semiconductor_metadata(feature_version=FORWARD_SIMULATION_VERSION),
            request_id=request_id,
            field=exc.field,
            warnings=["fixture_graph:not_production_ready"],
        )
    except Exception as exc:
        return make_error_envelope(
            "forward_scenario_unavailable",
            "Forward Monte Carlo scenario could not run against the SemiRisk fixture graph.",
            metadata=semiconductor_metadata(feature_version=FORWARD_SIMULATION_VERSION),
            request_id=request_id,
            warnings=[
                f"forward_scenario_failed:{type(exc).__name__}",
                "fixture_graph:not_production_ready",
            ],
        )
    response = make_envelope(
        result,
        metadata=semiconductor_metadata(snapshot, feature_version=FORWARD_SIMULATION_VERSION),
        request_id=request_id,
        warnings=result.get("warnings", ["fixture_graph:not_production_ready"]),
    )
    RUN_CACHE.put_summary("forward_scenario", response)
    return response


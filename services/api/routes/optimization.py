from __future__ import annotations

from typing import Any, Callable


def register(
    app: Any,
    *,
    Body: Any,
    Header: Any,
    route_intervention_optimization: Callable[..., dict[str, Any]],
) -> None:
    @app.post("/api/v1/optimization/interventions")
    def http_intervention_optimization(
        payload: dict[str, Any] | None = Body(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_intervention_optimization(payload=payload, request_id=x_request_id)


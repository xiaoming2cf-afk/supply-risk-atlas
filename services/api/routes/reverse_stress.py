from __future__ import annotations

from typing import Any, Callable


def register(
    app: Any,
    *,
    Body: Any,
    Header: Any,
    route_reverse_scenario: Callable[..., dict[str, Any]],
) -> None:
    @app.post("/api/v1/scenarios/reverse")
    def http_reverse_scenario(
        payload: dict[str, Any] | None = Body(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_reverse_scenario(payload=payload, request_id=x_request_id)


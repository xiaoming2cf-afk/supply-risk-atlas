from __future__ import annotations

from typing import Any, Callable


def register(
    app: Any,
    *,
    Header: Any,
    route_system_health_center: Callable[..., dict[str, Any]],
) -> None:
    @app.get("/api/v1/system-health")
    @app.get("/api/v1/system-health-center")
    @app.get("/api/v1/dashboard/system-health-center")
    def http_system_health_center(
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_system_health_center(request_id=x_request_id)


from __future__ import annotations

from typing import Any, Callable


def register(
    app: Any,
    *,
    Header: Any,
    route_version: Callable[..., dict[str, Any]],
) -> None:
    @app.get("/api/v1/version")
    def http_version(
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_version(request_id=x_request_id)


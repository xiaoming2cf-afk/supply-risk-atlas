from __future__ import annotations

from typing import Any, Callable


def register(
    app: Any,
    *,
    Header: Any,
    route_runs: Callable[..., dict[str, Any]],
    route_run_detail: Callable[..., dict[str, Any]],
) -> None:
    @app.get("/api/v1/runs")
    def http_runs(x_request_id: str | None = Header(default=None)) -> dict[str, Any]:
        return route_runs(request_id=x_request_id)

    @app.get("/api/v1/runs/{run_id}")
    def http_run_detail(
        run_id: str,
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_run_detail(run_id=run_id, request_id=x_request_id)

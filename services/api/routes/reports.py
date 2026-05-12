from __future__ import annotations

from typing import Any, Callable


def register(
    app: Any,
    *,
    Body: Any,
    Header: Any,
    route_investigation_report: Callable[..., dict[str, Any]],
    route_report_detail: Callable[..., dict[str, Any]],
) -> None:
    @app.post("/api/v1/reports/investigation")
    def http_investigation_report(
        payload: dict[str, Any] | None = Body(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_investigation_report(payload=payload, request_id=x_request_id)

    @app.get("/api/v1/reports/{report_id}")
    def http_report_detail(
        report_id: str,
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_report_detail(report_id=report_id, request_id=x_request_id)

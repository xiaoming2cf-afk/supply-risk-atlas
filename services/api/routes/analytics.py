from __future__ import annotations

from typing import Any, Callable


def register(
    app: Any,
    *,
    Header: Any,
    Query: Any,
    route_analytics_export: Callable[..., dict[str, Any]],
    route_analytics_table: Callable[..., dict[str, Any]],
) -> None:
    @app.get("/api/v1/analytics/tables/{table_id}")
    def http_analytics_table(
        table_id: str,
        limit: int = Query(default=50, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_analytics_table(
            table_id=table_id,
            limit=limit,
            offset=offset,
            request_id=x_request_id,
        )

    @app.get("/api/v1/analytics/export/{table_id}")
    def http_analytics_export(
        table_id: str,
        format: str = Query(default="json", pattern="^(json|csv|markdown)$"),
        limit: int = Query(default=50, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_analytics_export(
            table_id=table_id,
            export_format=format,
            limit=limit,
            offset=offset,
            request_id=x_request_id,
        )

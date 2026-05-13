from __future__ import annotations

from typing import Any, Callable


def register(
    app: Any,
    *,
    Header: Any,
    Query: Any,
    route_stage_graph: Callable[..., dict[str, Any]],
    route_stage_graph_focus: Callable[..., dict[str, Any]],
    route_stage_graph_source_coverage: Callable[..., dict[str, Any]],
    route_stage_graph_evidence: Callable[..., dict[str, Any]],
    route_stage_graph_tables: Callable[..., dict[str, Any]],
    route_stage_graph_charts: Callable[..., dict[str, Any]],
) -> None:
    @app.get("/api/v1/stage-graph/{stage_id}")
    def http_stage_graph(
        stage_id: str,
        limit: int = Query(default=18, ge=1, le=50),
        relationship_class: str | None = Query(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_stage_graph(
            stage_id=stage_id,
            limit=limit,
            relationship_class=relationship_class,
            request_id=x_request_id,
        )

    @app.get("/api/v1/stage-graph/{stage_id}/focus")
    def http_stage_graph_focus(
        stage_id: str,
        node_id: str | None = Query(default=None),
        limit: int = Query(default=25, ge=1, le=50),
        relationship_class: str | None = Query(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_stage_graph_focus(
            stage_id=stage_id,
            node_id=node_id,
            limit=limit,
            relationship_class=relationship_class,
            request_id=x_request_id,
        )

    @app.get("/api/v1/stage-graph/{stage_id}/source-coverage")
    def http_stage_graph_source_coverage(
        stage_id: str,
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_stage_graph_source_coverage(stage_id=stage_id, request_id=x_request_id)

    @app.get("/api/v1/stage-graph/{stage_id}/evidence")
    def http_stage_graph_evidence(
        stage_id: str,
        limit: int = Query(default=50, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_stage_graph_evidence(stage_id=stage_id, limit=limit, request_id=x_request_id)

    @app.get("/api/v1/stage-graph/{stage_id}/tables")
    def http_stage_graph_tables(
        stage_id: str,
        limit: int = Query(default=50, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_stage_graph_tables(stage_id=stage_id, limit=limit, request_id=x_request_id)

    @app.get("/api/v1/stage-graph/{stage_id}/charts")
    def http_stage_graph_charts(
        stage_id: str,
        limit: int = Query(default=50, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_stage_graph_charts(stage_id=stage_id, limit=limit, request_id=x_request_id)

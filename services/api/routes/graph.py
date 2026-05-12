from __future__ import annotations

from typing import Any, Callable


def register(
    app: Any,
    *,
    Header: Any,
    Query: Any,
    route_graph_snapshots: Callable[..., dict[str, Any]],
    route_graph_diff: Callable[..., dict[str, Any]],
    route_graph_view: Callable[..., dict[str, Any]],
    route_graph_focus: Callable[..., dict[str, Any]],
    route_graph_clusters: Callable[..., dict[str, Any]],
    route_graph_path_view: Callable[..., dict[str, Any]],
    route_graph_timeline: Callable[..., dict[str, Any]],
    route_graph_geo: Callable[..., dict[str, Any]],
    route_graph_matrix: Callable[..., dict[str, Any]],
    route_graph_layers: Callable[..., dict[str, Any]],
    route_graph_evidence: Callable[..., dict[str, Any]],
    route_graph_scenario_overlay: Callable[..., dict[str, Any]],
    route_analytics_charts: Callable[..., dict[str, Any]],
    route_analytics_tables: Callable[..., dict[str, Any]],
    route_semiconductor_graph_snapshot: Callable[..., dict[str, Any]],
    route_semiconductor_graph_neighborhood: Callable[..., dict[str, Any]],
) -> None:
    @app.get("/graph", include_in_schema=False)
    @app.get("/api/v1/graph")
    @app.get("/api/v1/graph/snapshots")
    def http_graph(x_request_id: str | None = Header(default=None)) -> dict[str, Any]:
        return route_graph_snapshots(request_id=x_request_id)

    @app.get("/api/v1/graph/diff")
    def http_graph_diff(x_request_id: str | None = Header(default=None)) -> dict[str, Any]:
        return route_graph_diff(request_id=x_request_id)

    @app.get("/api/v1/graph/view")
    def http_graph_view(
        mode: str = Query(default="overview"),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_graph_view(mode=mode, request_id=x_request_id)

    @app.get("/api/v1/graph/focus")
    def http_graph_focus(
        node_id: str = Query(default="company:tsmc"),
        depth: int = Query(default=1, ge=0, le=2),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_graph_focus(node_id=node_id, depth=depth, request_id=x_request_id)

    @app.get("/api/v1/graph/clusters")
    def http_graph_clusters(x_request_id: str | None = Header(default=None)) -> dict[str, Any]:
        return route_graph_clusters(request_id=x_request_id)

    @app.get("/api/v1/graph/path-view")
    def http_graph_path_view(
        source_node_id: str = Query(default="company:tsmc"),
        target_node_id: str = Query(default="product_grade:advanced_logic"),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_graph_path_view(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            request_id=x_request_id,
        )

    @app.get("/api/v1/graph/timeline")
    def http_graph_timeline(
        limit: int = Query(default=50, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_graph_timeline(limit=limit, request_id=x_request_id)

    @app.get("/api/v1/graph/geo")
    def http_graph_geo(
        limit: int = Query(default=50, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_graph_geo(limit=limit, request_id=x_request_id)

    @app.get("/api/v1/graph/matrix")
    def http_graph_matrix(
        limit: int = Query(default=50, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_graph_matrix(limit=limit, request_id=x_request_id)

    @app.get("/api/v1/graph/layers")
    def http_graph_layers(x_request_id: str | None = Header(default=None)) -> dict[str, Any]:
        return route_graph_layers(request_id=x_request_id)

    @app.get("/api/v1/graph/evidence")
    def http_graph_evidence(
        source_id: str | None = Query(default=None),
        limit: int = Query(default=50, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_graph_evidence(source_id=source_id, limit=limit, request_id=x_request_id)

    @app.get("/api/v1/graph/scenario-overlay")
    def http_graph_scenario_overlay(
        run_id: str | None = Query(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_graph_scenario_overlay(run_id=run_id, request_id=x_request_id)

    @app.get("/api/v1/analytics/charts")
    def http_analytics_charts(
        chart_id: str | None = Query(default=None),
        limit: int = Query(default=50, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_analytics_charts(chart_id=chart_id, limit=limit, request_id=x_request_id)

    @app.get("/api/v1/analytics/tables")
    def http_analytics_tables(
        table_id: str | None = Query(default=None),
        limit: int = Query(default=50, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_analytics_tables(
            table_id=table_id,
            limit=limit,
            offset=offset,
            request_id=x_request_id,
        )

    @app.get("/api/v1/graph/snapshot")
    def http_semiconductor_graph_snapshot(
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_semiconductor_graph_snapshot(request_id=x_request_id)

    @app.get("/api/v1/graph/neighborhood")
    def http_semiconductor_graph_neighborhood(
        node_id: str = Query(default="company:tsmc"),
        depth: int = Query(default=1, ge=0, le=3),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_semiconductor_graph_neighborhood(
            node_id=node_id,
            depth=depth,
            request_id=x_request_id,
        )

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

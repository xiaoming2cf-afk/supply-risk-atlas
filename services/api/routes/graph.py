from __future__ import annotations

from typing import Any, Callable


def register(
    app: Any,
    *,
    Header: Any,
    Query: Any,
    route_graph_snapshots: Callable[..., dict[str, Any]],
    route_graph_diff: Callable[..., dict[str, Any]],
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


from __future__ import annotations

from typing import Any, Callable


def register(
    app: Any,
    *,
    Header: Any,
    Query: Any,
    route_semirisk_entity_risk: Callable[..., dict[str, Any]],
    route_semirisk_risk_portfolio: Callable[..., dict[str, Any]],
) -> None:
    @app.get("/api/v1/risk/entities/{entity_id}")
    def http_semirisk_entity_risk(
        entity_id: str,
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_semirisk_entity_risk(entity_id=entity_id, request_id=x_request_id)

    @app.get("/api/v1/risk/portfolio")
    def http_semirisk_risk_portfolio(
        node_type: str | None = Query(default="company"),
        limit: int = Query(default=20, ge=1, le=100),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_semirisk_risk_portfolio(
            node_type=node_type,
            limit=limit,
            request_id=x_request_id,
        )


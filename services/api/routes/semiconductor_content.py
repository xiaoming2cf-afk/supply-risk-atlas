from __future__ import annotations

from typing import Any, Callable


def register(
    app: Any,
    *,
    Header: Any,
    Query: Any,
    route_semiconductor_coverage_overview: Callable[..., dict[str, Any]],
    route_semiconductor_value_chain_layers: Callable[..., dict[str, Any]],
    route_semiconductor_country_exposures: Callable[..., dict[str, Any]],
    route_semiconductor_entity_profiles: Callable[..., dict[str, Any]],
    route_semiconductor_chokepoints: Callable[..., dict[str, Any]],
    route_semiconductor_relationships: Callable[..., dict[str, Any]],
    route_semiconductor_source_coverage: Callable[..., dict[str, Any]],
) -> None:
    @app.get("/api/v1/semiconductor/coverage")
    def http_semiconductor_coverage_overview(
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_semiconductor_coverage_overview(request_id=x_request_id)

    @app.get("/api/v1/semiconductor/value-chain/layers")
    def http_semiconductor_value_chain_layers(
        stage: str | None = Query(default=None),
        layer_id: str | None = Query(default=None),
        limit: int = Query(default=100, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_semiconductor_value_chain_layers(
            stage=stage,
            layer_id=layer_id,
            limit=limit,
            request_id=x_request_id,
        )

    @app.get("/api/v1/semiconductor/country-exposures")
    def http_semiconductor_country_exposures(
        geo_id: str | None = Query(default=None),
        stage: str | None = Query(default=None),
        limit: int = Query(default=100, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_semiconductor_country_exposures(
            geo_id=geo_id,
            stage=stage,
            limit=limit,
            request_id=x_request_id,
        )

    @app.get("/api/v1/semiconductor/entities")
    def http_semiconductor_entity_profiles(
        entity_id: str | None = Query(default=None),
        stage: str | None = Query(default=None),
        layer_id: str | None = Query(default=None),
        geo_id: str | None = Query(default=None),
        source_id: str | None = Query(default=None),
        risk_tag: str | None = Query(default=None),
        limit: int = Query(default=100, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_semiconductor_entity_profiles(
            entity_id=entity_id,
            stage=stage,
            layer_id=layer_id,
            geo_id=geo_id,
            source_id=source_id,
            risk_tag=risk_tag,
            limit=limit,
            request_id=x_request_id,
        )

    @app.get("/api/v1/semiconductor/entities/{entity_id}")
    def http_semiconductor_entity_profile(
        entity_id: str,
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_semiconductor_entity_profiles(
            entity_id=entity_id,
            limit=1,
            request_id=x_request_id,
        )

    @app.get("/api/v1/semiconductor/chokepoints")
    def http_semiconductor_chokepoints(
        layer_id: str | None = Query(default=None),
        stage: str | None = Query(default=None),
        limit: int = Query(default=100, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_semiconductor_chokepoints(
            layer_id=layer_id,
            stage=stage,
            limit=limit,
            request_id=x_request_id,
        )

    @app.get("/api/v1/semiconductor/relationships")
    def http_semiconductor_relationships(
        relationship_class: str | None = Query(default=None),
        relationship_type: str | None = Query(default=None),
        edge_type: str | None = Query(default=None),
        source_id: str | None = Query(default=None),
        target_id: str | None = Query(default=None),
        layer_id: str | None = Query(default=None),
        stage: str | None = Query(default=None),
        source_family: str | None = Query(default=None),
        limit: int = Query(default=100, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_semiconductor_relationships(
            relationship_class=relationship_class,
            relationship_type=relationship_type,
            edge_type=edge_type,
            source_id=source_id,
            target_id=target_id,
            layer_id=layer_id,
            stage=stage,
            source_family=source_family,
            limit=limit,
            request_id=x_request_id,
        )

    @app.get("/api/v1/semiconductor/source-coverage")
    def http_semiconductor_source_coverage(
        stage: str | None = Query(default=None),
        source_family: str | None = Query(default=None),
        relationship_class: str | None = Query(default=None),
        limit: int = Query(default=100, ge=1, le=500),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_semiconductor_source_coverage(
            stage=stage,
            source_family=source_family,
            relationship_class=relationship_class,
            limit=limit,
            request_id=x_request_id,
        )

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any

from ml.risk_scoring.semirisk_score import (
    FEATURE_VERSION as SEMIRISK_RISK_FEATURE_VERSION,
    RISK_SCORE_WARNING_FIXTURE_GRAPH,
    RiskScoreUnavailable,
    rank_risk_portfolio,
    score_semirisk_entity,
)
from sra_core.api.envelope import make_envelope, make_error_envelope
from services.api.services.common import semiconductor_metadata
from services.api.services.semiconductor_content_service import profile_for_entity
from services.api.services.semiconductor_snapshot_cache import fixture_snapshot_for_services


@lru_cache(maxsize=128)
def _cached_entity_risk_payload(entity_id: str) -> dict[str, Any]:
    snapshot = fixture_snapshot_for_services()
    return score_semirisk_entity(entity_id, snapshot=snapshot)


@lru_cache(maxsize=64)
def _cached_risk_portfolio_payload(node_type_key: str, limit: int) -> dict[str, Any]:
    snapshot = fixture_snapshot_for_services()
    node_type = None if node_type_key == "__all__" else node_type_key
    return rank_risk_portfolio(snapshot=snapshot, node_type=node_type, limit=limit)


def route_semirisk_entity_risk(
    entity_id: str = "company:tsmc",
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
    except Exception as exc:
        return make_error_envelope(
            "semirisk_risk_graph_unavailable",
            "SemiRisk fixture graph could not be built for Risk Score v0.",
            metadata=semiconductor_metadata(feature_version=SEMIRISK_RISK_FEATURE_VERSION),
            request_id=request_id,
            warnings=[f"fixture_graph_build_failed:{type(exc).__name__}"],
        )
    try:
        payload = deepcopy(_cached_entity_risk_payload(entity_id))
    except RiskScoreUnavailable as exc:
        return make_error_envelope(
            "semirisk_risk_score_unavailable",
            str(exc),
            metadata=semiconductor_metadata(
                snapshot,
                feature_version=SEMIRISK_RISK_FEATURE_VERSION,
            ),
            request_id=request_id,
            field="entity_id",
            warnings=[RISK_SCORE_WARNING_FIXTURE_GRAPH],
        )
    profile = profile_for_entity(entity_id)
    if profile is not None:
        payload["semiconductor_profile"] = profile
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=SEMIRISK_RISK_FEATURE_VERSION),
        request_id=request_id,
        warnings=payload.get("warnings", [RISK_SCORE_WARNING_FIXTURE_GRAPH]),
    )


def route_semirisk_risk_portfolio(
    node_type: str | None = "company",
    limit: int = 20,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
        node_type_key = node_type or "__all__"
        payload = deepcopy(_cached_risk_portfolio_payload(node_type_key, limit))
    except Exception as exc:
        return make_error_envelope(
            "semirisk_risk_portfolio_unavailable",
            "SemiRisk fixture graph portfolio scores could not be built.",
            metadata=semiconductor_metadata(feature_version=SEMIRISK_RISK_FEATURE_VERSION),
            request_id=request_id,
            warnings=[
                f"risk_portfolio_failed:{type(exc).__name__}",
                RISK_SCORE_WARNING_FIXTURE_GRAPH,
            ],
        )
    return make_envelope(
        payload,
        metadata=semiconductor_metadata(snapshot, feature_version=SEMIRISK_RISK_FEATURE_VERSION),
        request_id=request_id,
        warnings=payload.get("warnings", [RISK_SCORE_WARNING_FIXTURE_GRAPH]),
    )

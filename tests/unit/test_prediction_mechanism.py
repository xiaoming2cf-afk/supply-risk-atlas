from __future__ import annotations

from datetime import datetime, timezone

import pytest

from ml.datasets.builder import DatasetSample
from ml.models.baseline import BaselineRiskModel
from sra_core.contracts.domain import CanonicalEntity, EdgeState, GraphSnapshot
from sra_core.feature_factory import compute_features


AS_OF_TIME = datetime(2026, 2, 1, tzinfo=timezone.utc)


def _sample(
    target_id: str,
    node_features: dict[str, float],
    *,
    incoming_risk: float = 0.0,
    path_tokens: list[str] | None = None,
) -> DatasetSample:
    return DatasetSample(
        target_id=target_id,
        target_type="firm",
        prediction_time=AS_OF_TIME,
        horizon=30,
        graph_version="g_test",
        feature_version="f_test",
        label_version="l_test",
        node_features=node_features,
        edge_features={"incoming_risk_max": incoming_risk},
        path_tokens=path_tokens or [],
        label=None,
    )


def _edge(
    edge_id: str,
    source_id: str,
    target_id: str,
    *,
    confidence: float,
    risk_score: float,
    source: str,
    weight: float = 1.0,
    reliability: float | None = None,
) -> EdgeState:
    attributes = {} if reliability is None else {"reliability": reliability}
    return EdgeState(
        edge_id=edge_id,
        source_id=source_id,
        target_id=target_id,
        edge_type="supplies_to",
        valid_from=AS_OF_TIME,
        valid_to=None,
        weight=weight,
        confidence=confidence,
        risk_score=risk_score,
        attributes=attributes,
        graph_version="g_test",
        source=source,
    )


def test_baseline_normalizes_large_counts_without_score_saturation() -> None:
    model = BaselineRiskModel()
    count_heavy = _sample(
        "firm_count_heavy",
        {
            "inbound_edge_count": 1_000_000.0,
            "outbound_edge_count": 900_000.0,
            "path_count": 500_000.0,
            "path_count_norm": 1.0,
            "incoming_risk_mean": 0.0,
            "path_risk_max": 0.0,
        },
    )

    components = model.score_components(count_heavy)
    prediction = model.predict(count_heavy)

    assert components == model.score_components(count_heavy)
    assert 0.0 <= components["structure"] <= 1.0
    assert prediction.risk_score == components["score"]
    assert prediction.risk_score < 0.2


def test_baseline_score_distribution_does_not_flatline_at_one() -> None:
    model = BaselineRiskModel()
    scores = []
    for index in range(30):
        path_risk = 0.05 + (index * 0.02)
        sample = _sample(
            f"firm_{index}",
            {
                "inbound_edge_count": 10_000.0 + index,
                "outbound_edge_count": 8_000.0 + index,
                "path_count": 2_000.0 + index,
                "incoming_risk_mean": min(0.95, path_risk + 0.1),
                "path_risk_max": min(0.95, path_risk),
                "path_score_mean": min(0.95, path_risk * 0.8),
                "path_confidence_mean": 0.78,
                "evidence_quality_mean": 0.82,
            },
            incoming_risk=min(0.95, path_risk + 0.05),
            path_tokens=[f"path_{index}_{hop}" for hop in range(8)],
        )
        scores.append(model.predict(sample).risk_score)

    assert max(scores) < 0.95
    assert sum(score >= 0.85 for score in scores) <= 1
    assert len({round(score, 4) for score in scores}) > 20


def test_baseline_component_outputs_do_not_change_prediction_result_contract() -> None:
    model = BaselineRiskModel()
    sample = _sample(
        "firm_contract",
        {
            "incoming_risk_mean": 0.55,
            "path_risk_max": 0.45,
            "path_confidence_mean": 0.8,
            "evidence_quality_mean": 0.9,
        },
        incoming_risk=0.5,
        path_tokens=["path_a"],
    )

    components = model.score_components(sample)
    payload = model.predict(sample).model_dump(mode="json")

    assert {"risk", "edge", "path", "structure", "evidence", "residual", "score"} <= set(
        components
    )
    assert "components" not in payload
    assert set(payload) >= {"risk_score", "top_drivers", "top_paths", "model_version"}


def test_feature_factory_emits_normalized_path_and_evidence_features() -> None:
    entities = [
        CanonicalEntity(
            canonical_id="supplier_a",
            entity_type="firm",
            display_name="Supplier A",
            confidence=0.9,
        ),
        CanonicalEntity(
            canonical_id="supplier_b",
            entity_type="firm",
            display_name="Supplier B",
            confidence=0.9,
        ),
        CanonicalEntity(
            canonical_id="firm_target",
            entity_type="firm",
            display_name="Target",
            confidence=0.95,
        ),
        CanonicalEntity(
            canonical_id="product_x",
            entity_type="product",
            display_name="Product X",
            confidence=0.95,
        ),
    ]
    edge_states = [
        _edge(
            "edge_a",
            "supplier_a",
            "firm_target",
            confidence=0.9,
            risk_score=0.6,
            source="source_a",
            weight=0.8,
            reliability=0.8,
        ),
        _edge(
            "edge_b",
            "supplier_b",
            "firm_target",
            confidence=0.5,
            risk_score=0.3,
            source="source_b",
            weight=0.7,
            reliability=0.6,
        ),
        _edge(
            "edge_c",
            "firm_target",
            "product_x",
            confidence=0.75,
            risk_score=0.2,
            source="source_a",
            weight=0.9,
        ),
    ]
    snapshot = GraphSnapshot(
        snapshot_id="snapshot_test",
        graph_version="g_test",
        as_of_time=AS_OF_TIME,
        window_start=AS_OF_TIME,
        window_end=AS_OF_TIME,
        node_count=len(entities),
        edge_count=len(edge_states),
        checksum="checksum",
    )

    features = compute_features(entities, edge_states, snapshot)
    by_entity = {
        feature.feature_name: feature.feature_value
        for feature in features
        if feature.entity_id == "firm_target"
    }

    expected = {
        "inbound_degree_norm",
        "outbound_degree_norm",
        "total_degree_norm",
        "path_count_norm",
        "path_score_max",
        "path_score_mean",
        "path_confidence_mean",
        "evidence_quality_mean",
        "source_diversity_norm",
    }
    assert expected <= set(by_entity)
    assert all(0.0 <= by_entity[name] <= 1.0 for name in expected)
    assert by_entity["inbound_degree_norm"] == 1.0
    assert by_entity["source_diversity_norm"] == 1.0
    assert by_entity["evidence_quality_mean"] == pytest.approx(
        ((0.9 * 0.8) + (0.5 * 0.6)) / 2
    )

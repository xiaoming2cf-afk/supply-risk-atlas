from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from graph_kernel.path_index import build_path_index
from graph_kernel.snapshot_builder import build_graph_snapshot
from ml.datasets.builder import DatasetSample, build_dataset
from ml.models.baseline import BaselineRiskModel
from sra_core.contracts.domain import (
    ApiEnvelope,
    CanonicalEntity,
    EdgeState,
    ExplanationPath,
    FeatureValue,
    GraphSnapshot,
    LabelValue,
    PredictionResult,
    VersionMetadata,
)
from sra_core.feature_factory import compute_features
from sra_core.label_factory import generate_labels, label_quality_report
from sra_core.synthetic.generator import SyntheticDataset, generate_synthetic_dataset


DEFAULT_AS_OF_TIME = datetime(2026, 2, 1, tzinfo=timezone.utc)
DEFAULT_WINDOW_START = datetime(2026, 1, 1, tzinfo=timezone.utc)


@dataclass(frozen=True)
class PipelineResult:
    synthetic: SyntheticDataset
    snapshot: GraphSnapshot
    edge_states: list[EdgeState]
    features: list[FeatureValue]
    labels: list[LabelValue]
    samples: list[DatasetSample]
    predictions: list[PredictionResult]
    explanations: list[ExplanationPath]
    label_quality: dict[str, float | int]


def run_synthetic_pipeline(seed: int = 42, as_of_time: datetime = DEFAULT_AS_OF_TIME) -> PipelineResult:
    synthetic = generate_synthetic_dataset(seed=seed)
    snapshot, edge_states = build_graph_snapshot(
        synthetic.entities,
        synthetic.edge_events,
        as_of_time=as_of_time,
        window_start=DEFAULT_WINDOW_START,
    )
    features = compute_features(synthetic.entities, edge_states, snapshot)
    labels = generate_labels(synthetic.edge_events, prediction_time=as_of_time)
    paths = build_path_index(edge_states)
    samples = build_dataset(
        prediction_time=as_of_time,
        graph_version=snapshot.graph_version,
        feature_values=features,
        labels=labels,
        edge_states=edge_states,
        paths=paths,
    )
    model = BaselineRiskModel()
    predictions = [model.predict(sample, created_at=as_of_time + timedelta(minutes=1)) for sample in samples]
    explanations = [
        ExplanationPath(
            explanation_id=f"explain_{prediction.prediction_id.removeprefix('pred_')}",
            prediction_id=prediction.prediction_id,
            path_id=prediction.top_paths[0] if prediction.top_paths else "path_none",
            node_sequence=[],
            edge_sequence=[],
            contribution_score=prediction.risk_score,
            causal_score=min(1.0, prediction.risk_score + 0.1),
            confidence=0.72,
            evidence=["synthetic_edge_events", "synthetic_feature_factory"],
        )
        for prediction in predictions
    ]
    return PipelineResult(
        synthetic=synthetic,
        snapshot=snapshot,
        edge_states=edge_states,
        features=features,
        labels=labels,
        samples=samples,
        predictions=predictions,
        explanations=explanations,
        label_quality=label_quality_report(labels),
    )


def default_metadata(result: PipelineResult) -> VersionMetadata:
    first_feature_version = result.features[0].feature_version if result.features else "f_none"
    first_label_version = result.labels[0].label_version if result.labels else "l_none"
    first_model_version = result.predictions[0].model_version if result.predictions else "model_none"
    return VersionMetadata(
        graph_version=result.snapshot.graph_version,
        feature_version=first_feature_version,
        label_version=first_label_version,
        model_version=first_model_version,
        as_of_time=result.snapshot.as_of_time,
        audit_ref="audit_synthetic_demo",
        lineage_ref="lineage_synthetic_seed_42",
        data_mode="synthetic",
        freshness_status="fresh",
        source_count=1,
        source_manifest_ref="manifest_synthetic_seed_42",
    )


def envelope(data: object, request_id: str = "req_synthetic_demo") -> ApiEnvelope:
    result = run_synthetic_pipeline()
    return ApiEnvelope(
        request_id=request_id,
        status="success",
        data=data,
        metadata=default_metadata(result),
        warnings=[],
        errors=[],
    )


def serializable_entities(entities: list[CanonicalEntity]) -> list[dict[str, object]]:
    return [entity.model_dump(mode="json") for entity in entities]

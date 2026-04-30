from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256

from ml.datasets.builder import DatasetSample
from sra_core.contracts.domain import PredictionResult


def risk_level(score: float) -> str:
    if score >= 0.85:
        return "critical"
    if score >= 0.65:
        return "high"
    if score >= 0.35:
        return "medium"
    return "low"


@dataclass(frozen=True)
class BaselineRiskModel:
    model_version: str = "baseline_v0.1.0"

    def predict(self, sample: DatasetSample, created_at: datetime | None = None) -> PredictionResult:
        feature_signal = sum(sample.node_features.values()) / max(1, len(sample.node_features))
        edge_signal = sample.edge_features.get("incoming_risk_max", 0.0)
        path_signal = min(1.0, len(sample.path_tokens) / 8)
        score = max(0.0, min(1.0, 0.45 * feature_signal + 0.40 * edge_signal + 0.15 * path_signal))
        digest = sha256(f"{sample.target_id}|{sample.prediction_time.isoformat()}|{self.model_version}".encode()).hexdigest()[:12]
        return PredictionResult(
            prediction_id=f"pred_{digest}",
            target_id=sample.target_id,
            target_type=sample.target_type,
            prediction_time=sample.prediction_time,
            horizon=sample.horizon,
            risk_score=score,
            risk_level=risk_level(score),  # type: ignore[arg-type]
            confidence_low=max(0.0, score - 0.12),
            confidence_high=min(1.0, score + 0.12),
            model_version=self.model_version,
            graph_version=sample.graph_version,
            feature_version=sample.feature_version,
            label_version=sample.label_version,
            created_at=created_at or sample.prediction_time,
            top_drivers=sorted(sample.node_features, key=sample.node_features.get, reverse=True)[:3],
            top_paths=sample.path_tokens[:3],
        )

from __future__ import annotations

from datetime import datetime, timedelta
from hashlib import sha256

from sra_core.contracts.domain import EdgeEvent, LabelValue


def _label_id(target_id: str, label_name: str, prediction_time: datetime) -> str:
    digest = sha256(f"{target_id}|{label_name}|{prediction_time.isoformat()}".encode()).hexdigest()[:12]
    return f"label_{digest}"


def generate_labels(edge_events: list[EdgeEvent], prediction_time: datetime) -> list[LabelValue]:
    version = f"l_{prediction_time.strftime('%Y%m%dT%H%M%SZ')}"
    labels: list[LabelValue] = []
    firm_targets = sorted({event.target_id for event in edge_events if event.target_id.startswith("firm_")})
    for target_id in firm_targets:
        future_events = [
            event
            for event in edge_events
            if event.target_id == target_id
            and prediction_time <= event.event_time <= prediction_time + timedelta(days=30)
        ]
        value = 1.0 if any(event.event_type == "remove" or event.attributes.get("risk_score", 0) >= 0.6 for event in future_events) else 0.0
        labels.append(
            LabelValue(
                label_id=_label_id(target_id, "firm_risk_30d", prediction_time),
                target_id=target_id,
                target_type="firm",
                label_name="firm_risk_30d",
                prediction_time=prediction_time,
                horizon=30,
                label_time=prediction_time + timedelta(days=30),
                label_value=value,
                confidence=0.78 if value else 0.65,
                label_version=version,
                label_source="synthetic_future_window",
            )
        )
    edge_targets = sorted({f"{event.source_id}->{event.target_id}:{event.edge_type}" for event in edge_events})
    for target in edge_targets[:6]:
        labels.append(
            LabelValue(
                label_id=_label_id(target, "edge_disruption_30d", prediction_time),
                target_id=target,
                target_type="edge",
                label_name="edge_disruption_30d",
                prediction_time=prediction_time,
                horizon=30,
                label_time=prediction_time + timedelta(days=30),
                label_value=1.0 if "firm_sensor->firm_anchor" in target else 0.0,
                confidence=0.7,
                label_version=version,
                label_source="synthetic_edge_remove_future_window",
            )
        )
    return labels


def label_quality_report(labels: list[LabelValue]) -> dict[str, float | int]:
    positives = sum(1 for label in labels if label.label_value > 0)
    return {
        "label_count": len(labels),
        "positive_count": positives,
        "positive_rate": positives / len(labels) if labels else 0.0,
        "mean_confidence": sum(label.confidence for label in labels) / len(labels) if labels else 0.0,
    }

from pathlib import Path

from graph_kernel.events import EdgeKey, materialize_edge_state
from graph_kernel.snapshots import snapshot_from_edge_states
from graph_kernel.synthetic import SyntheticGraphSpec, generate_synthetic_edge_events
from ml.baseline import FeatureThresholdClassifier, MajorityClassClassifier
from ml.causal import estimate_ate, simulate_disruption
from ml.dataset import DatasetBuilder, DatasetRecord, temporal_train_test_split
from ml.features import FeatureFactory, load_feature_spec
from ml.labels import LabelFactory, load_label_spec


ROOT = Path(__file__).resolve().parents[2]


def test_dataset_builder_baseline_and_config_flow() -> None:
    events = generate_synthetic_edge_events(
        SyntheticGraphSpec(seed=7, supplier_count=5, component_count=3, facility_count=2, days=12)
    )
    feature_factory = FeatureFactory(load_feature_spec(ROOT / "configs" / "features" / "default.json"))
    label_factory = LabelFactory(load_label_spec(ROOT / "configs" / "labels" / "default.json"))

    records = DatasetBuilder(feature_factory, label_factory).build(events, cutoffs=[0, 4, 8])
    train, test = temporal_train_test_split(records, test_cutoff_start=8)

    assert records
    assert train
    assert test
    assert set(feature_factory.feature_names).issubset(records[0].features)

    majority = MajorityClassClassifier().fit(train)
    threshold = FeatureThresholdClassifier("active_out_degree").fit(train)
    test_rows = [record.features for record in test]

    assert len(majority.predict(test_rows)) == len(test)
    assert len(threshold.predict_proba(test_rows)) == len(test)


def test_simulation_removes_disrupted_node_edges() -> None:
    events = generate_synthetic_edge_events(SyntheticGraphSpec(seed=3, days=8))
    snapshot = snapshot_from_edge_states(materialize_edge_state(events, 0), 0)
    supplier = next(node for node in snapshot.nodes if node.startswith("supplier:"))

    disrupted = simulate_disruption(snapshot, disrupted_nodes=(supplier,))

    assert len(disrupted.edges) < len(snapshot.edges)
    assert all(edge.source != supplier and edge.target != supplier for edge in disrupted.edges)


def test_simulation_can_remove_low_reliability_edges() -> None:
    events = generate_synthetic_edge_events(SyntheticGraphSpec(seed=3, days=8))
    snapshot = snapshot_from_edge_states(materialize_edge_state(events, 0), 0)
    low_reliability = [
        edge.key
        for edge in snapshot.edges
        if "reliability" in edge.attrs and float(edge.attrs["reliability"]) < 0.95
    ]

    disrupted = simulate_disruption(snapshot, reliability_threshold=0.95)

    assert low_reliability
    assert not set(low_reliability).intersection(edge.key for edge in disrupted.edges)
    assert EdgeKey("missing", "missing", "missing") not in {edge.key for edge in disrupted.edges}


def test_estimate_ate_uses_threshold_groups() -> None:
    records = (
        DatasetRecord("a", 0, {"exposure": 0.0}, 0),
        DatasetRecord("b", 0, {"exposure": 1.0}, 1),
        DatasetRecord("c", 0, {"exposure": 2.0}, 1),
        DatasetRecord("d", 0, {"exposure": 0.2}, 0),
    )

    assert estimate_ate(records, treatment_feature="exposure", threshold=1.0) == 1.0

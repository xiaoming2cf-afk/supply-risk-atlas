from sra_core.pipeline import run_synthetic_pipeline
from ml.models.dchgt_sc import DCHGTSCSkeleton
from ml.simulation.counterfactual import build_counterfactual_edges


def test_baseline_predictions_are_serializable_and_versioned() -> None:
    result = run_synthetic_pipeline()
    assert result.predictions
    prediction = result.predictions[0]
    payload = prediction.model_dump(mode="json")
    assert payload["graph_version"].startswith("g_")
    assert payload["feature_version"].startswith("f_")
    assert payload["label_version"].startswith("l_")
    assert payload["model_version"] == "baseline_v0.1.0"


def test_counterfactual_does_not_mutate_base_graph() -> None:
    result = run_synthetic_pipeline()
    base_versions = [edge.graph_version for edge in result.edge_states]
    counterfactual = build_counterfactual_edges(
        result.snapshot.graph_version,
        result.edge_states,
        "close_port",
        "port_kaohsiung",
    )
    assert [edge.graph_version for edge in result.edge_states] == base_versions
    assert counterfactual.counterfactual_graph_version != result.snapshot.graph_version


def test_dchgt_sc_skeleton_lists_required_modules() -> None:
    description = DCHGTSCSkeleton().describe()
    assert "CausalGate" in description["modules"]
    assert "PathTransformer" in description["modules"]
    assert "CounterfactualHead" in description["modules"]

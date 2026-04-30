from sra_core.pipeline import run_synthetic_pipeline


def test_synthetic_pipeline_end_to_end() -> None:
    result = run_synthetic_pipeline(seed=42)
    assert result.synthetic.entities
    assert result.edge_states
    assert result.snapshot.graph_version.startswith("g_")
    assert result.features
    assert result.labels
    assert result.samples
    assert result.predictions
    assert result.explanations
    assert result.label_quality["label_count"] == len(result.labels)

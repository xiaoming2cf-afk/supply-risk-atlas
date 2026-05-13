from sra_core.pipeline import run_synthetic_pipeline
from ml.models.dchgt_sc import DCHGTSCSkeleton
from ml.simulation.counterfactual import build_counterfactual_edges
from ml.simulation.scenario import ScenarioShock, build_scenario_simulation, normalize_scenario_shock, _terms


def test_baseline_predictions_are_serializable_and_versioned() -> None:
    result = run_synthetic_pipeline()
    assert result.predictions
    prediction = result.predictions[0]
    payload = prediction.model_dump(mode="json")
    assert payload["graph_version"].startswith("g_")
    assert payload["feature_version"].startswith("f_")
    assert payload["label_version"].startswith("l_")
    assert payload["model_version"] == "baseline_v0.2.0"


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


def test_scenario_engine_returns_deterministic_offset_without_mutating_base_graph() -> None:
    result = run_synthetic_pipeline()
    base_risks = [edge.risk_score for edge in result.edge_states]
    simulation = build_scenario_simulation(
        base_graph_version=result.snapshot.graph_version,
        edge_states=result.edge_states,
        entities=result.real.entities if hasattr(result, "real") else result.synthetic.entities,
        predictions=result.predictions,
        shock=ScenarioShock(region="中国台湾 semiconductor corridor", commodity="semiconductor", severity=90),
    )

    assert [edge.risk_score for edge in result.edge_states] == base_risks
    assert simulation["diagnostics"]["calculationMode"] == "deterministic_public_evidence_mitigation_offset_v1"
    assert simulation["netImpactScore"] <= simulation["grossImpactScore"]
    assert 0 <= simulation["offsetAmountPct"] <= 0.45
    assert simulation["ebitdaAtRiskUsd"] == 0 if "ebitdaAtRiskUsd" in simulation else True
    assert {item["key"] for item in simulation["offsetBreakdown"]} == {
        "supplierDiversification",
        "routeRedundancy",
        "inventoryRecovery",
        "substitutionReadiness",
        "countryResilience",
        "evidenceCoverage",
    }
    assert all(item["evidenceRef"] and item["dataSource"] and item["confidence"] > 0 for item in simulation["offsetBreakdown"])
    assert "scenario_delta" in simulation
    assert "top_changed_paths" in simulation
    assert "changedPathDetails" in simulation
    assert simulation["scenarioGraphOverlay"]["nodes"]
    assert simulation["scenarioGraphOverlay"]["links"]


def test_scenario_shock_text_inputs_are_bounded() -> None:
    long_text = " ".join(["semiconductor"] * 200)
    shock = normalize_scenario_shock(
        {
            "region": long_text,
            "commodity": long_text,
            "supplier": long_text,
            "route": long_text,
        }
    )

    assert len(shock.region) <= 160
    assert len(shock.commodity) <= 160
    assert shock.supplier is not None and len(shock.supplier) <= 160
    assert shock.route is not None and len(shock.route) <= 160
    assert len(_terms(long_text)) <= 25


def test_dchgt_sc_skeleton_lists_required_modules() -> None:
    description = DCHGTSCSkeleton().describe()
    assert "CausalGate" in description["modules"]
    assert "PathTransformer" in description["modules"]
    assert "CounterfactualHead" in description["modules"]

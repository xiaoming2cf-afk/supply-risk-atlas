from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CHAIN_PATH = ROOT / "configs" / "ontology" / "semiconductor_chain_layers.yaml"

EXPECTED_LAYERS = {
    "L0_policy_macro": {"country", "region", "policy_regime", "macro_indicator", "industrial_policy", "export_control_regime"},
    "L1_raw_minerals": {"critical_mineral", "raw_material", "mining_country", "refining_country"},
    "L2_materials_chemicals": {"wafer_material", "electronic_chemical", "photoresist", "specialty_gas", "mask_reticle", "substrate_material", "cmp_material"},
    "L3_design_eda_ip": {"design_company", "eda_tool", "ip_core", "fabless_company", "idm", "architecture"},
    "L4_equipment": {"equipment", "equipment_supplier", "equipment_category", "equipment_component"},
    "L5_fabrication": {"foundry", "fab", "process_stage", "technology_node", "capacity_node", "wafer_process"},
    "L6_products": {"product_grade", "chip_type", "downstream_product"},
    "L7_packaging_testing": {"osat_company", "packaging_stage", "advanced_packaging", "substrate", "testing_stage"},
    "L8_logistics": {"port", "airport", "logistics_route", "shipping_lane", "customs_region"},
    "L9_downstream_demand": {"downstream_sector", "customer_industry", "demand_indicator"},
    "L10_risk_events": {"risk_event", "hazard_event", "market_event", "factory_event", "cyber_event", "labor_event"},
    "L11_compliance": {"policy_event", "sanction_event", "restricted_item", "restricted_entity", "compliance_risk"},
}


def load_chain_layers() -> dict:
    return yaml.safe_load(CHAIN_PATH.read_text(encoding="utf-8"))


def test_chain_layers_define_all_l0_to_l11_layers() -> None:
    data = load_chain_layers()
    layers = {layer["layer_id"]: layer for layer in data["layers"]}

    assert set(layers) == set(EXPECTED_LAYERS)
    assert [layer["order"] for layer in data["layers"]] == list(range(12))


def test_chain_layers_have_expected_node_types_and_status_labels() -> None:
    data = load_chain_layers()
    layers = {layer["layer_id"]: layer for layer in data["layers"]}

    assert data["production_status"] == "research_fixture"
    assert data["calibration_status"] == "fixture_proxy_not_calibrated"
    for layer_id, expected_node_types in EXPECTED_LAYERS.items():
        layer = layers[layer_id]
        assert layer["description"]
        assert set(layer["node_types"]) == expected_node_types

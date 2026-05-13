from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CHAIN_PATH = ROOT / "configs" / "ontology" / "semiconductor_chain_layers.yaml"
NODE_PATH = ROOT / "configs" / "ontology" / "semiconductor_node_catalog.yaml"

REQUIRED_NODE_IDS = {
    "country:US", "country:CN", "region:china_taiwan", "country:KR", "country:JP", "country:NL",
    "country:DE", "country:SG", "country:MY", "country:VN", "region:East_Asia", "region:EU",
    "region:North_America", "critical_mineral:silicon", "critical_mineral:gallium",
    "critical_mineral:germanium", "critical_mineral:rare_earths", "critical_mineral:tungsten",
    "critical_mineral:tantalum", "raw_material:quartz", "raw_material:graphite",
    "raw_material:fluorspar", "raw_material:helium", "raw_material:neon",
    "material:silicon_wafer_300mm", "material:soi_wafer", "material:photomask",
    "material:reticle", "chemical:photoresist_ArF", "chemical:photoresist_EUV",
    "chemical:hydrogen_peroxide", "chemical:sulfuric_acid", "chemical:hydrofluoric_acid",
    "gas:neon", "gas:argon", "gas:helium", "gas:nitrogen_trifluoride", "material:cmp_slurry",
    "material:abf_substrate", "company:NVIDIA", "company:AMD", "company:Qualcomm",
    "company:Broadcom", "company:Apple", "company:MediaTek", "company:Cadence",
    "company:Synopsys", "company:Siemens_EDA", "eda:logic_synthesis", "eda:place_and_route",
    "eda:verification", "ip:ARM_core", "ip:SerDes", "ip:DDR_controller", "architecture:x86",
    "architecture:ARM", "architecture:RISC-V", "equipment:EUV_scanner", "equipment:DUV_scanner",
    "equipment:etch_tool", "equipment:deposition_CVD", "equipment:deposition_PVD",
    "equipment:deposition_ALD", "equipment:ion_implanter", "equipment:CMP_tool",
    "equipment:metrology_tool", "equipment:inspection_tool", "equipment:wafer_cleaning_tool",
    "equipment:test_equipment", "company:ASML", "company:Applied_Materials",
    "company:Lam_Research", "company:Tokyo_Electron", "company:KLA", "company:Nikon",
    "company:Canon", "company:Advantest", "company:Teradyne", "company:TSMC",
    "company:Samsung_Foundry", "company:Intel_Foundry", "company:SMIC", "company:UMC",
    "company:GlobalFoundries", "company:Hua_Hong", "fab:TSMC_Fab_18",
    "fab:Samsung_Pyeongtaek", "process:lithography", "process:etching", "process:deposition",
    "process:ion_implantation", "process:cleaning", "process:CMP", "process:metrology",
    "technology_node:3nm", "technology_node:5nm", "technology_node:7nm",
    "technology_node:14nm", "technology_node:28nm", "technology_node:55nm",
    "product:advanced_logic", "product:mature_logic", "product:DRAM", "product:NAND",
    "product:HBM", "product:GPU", "product:AI_accelerator", "product:MCU",
    "product:power_semiconductor", "product:analog_chip", "product:RF_chip", "product:CIS",
    "product:automotive_chip", "product:server_cpu", "company:ASE", "company:Amkor",
    "company:JCET", "company:Powertech", "company:SPIL", "packaging:wire_bonding",
    "packaging:flip_chip", "packaging:fan_out", "packaging:2_5D", "packaging:3D",
    "packaging:CoWoS", "packaging:chiplet", "material:ABF_substrate", "material:interposer",
    "testing:wafer_sort", "testing:final_test", "port:Kaohsiung", "port:Keelung",
    "port:Shanghai", "port:Shenzhen", "port:Busan", "port:Yokohama", "port:Rotterdam",
    "port:Los_Angeles", "airport:Taoyuan", "airport:Incheon", "airport:Narita",
    "airport:Changi", "sector:AI_datacenter", "sector:cloud_computing",
    "sector:consumer_electronics", "sector:automotive", "sector:industrial_control",
    "sector:telecom", "sector:defense", "sector:medical_devices", "sector:robotics",
    "sector:renewable_energy", "event:earthquake", "event:power_outage",
    "event:water_shortage", "event:factory_fire", "event:port_disruption",
    "event:cyber_attack", "event:demand_spike", "event:price_spike",
    "policy:US_advanced_computing_controls", "policy:semiconductor_manufacturing_equipment_controls",
    "policy:entity_list_update", "list:OFAC_SDN", "list:Consolidated_Screening_List",
}


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_node_type_catalog_covers_every_chain_layer_node_type() -> None:
    chain = load_yaml(CHAIN_PATH)
    catalog = load_yaml(NODE_PATH)
    layer_node_types = {
        node_type
        for layer in chain["layers"]
        for node_type in layer["node_types"]
    }
    catalog_node_types = {entry["node_type"] for entry in catalog["node_types"]}

    assert catalog_node_types == layer_node_types
    for entry in catalog["node_types"]:
        assert entry["description"]
        assert entry["required_attributes"]
        assert entry["example_ids"]
        assert entry["source_candidates"]
        assert entry["layer"] in {layer["layer_id"] for layer in chain["layers"]}


def test_concrete_semiconductor_nodes_are_present_and_typed() -> None:
    chain = load_yaml(CHAIN_PATH)
    catalog = load_yaml(NODE_PATH)
    valid_layers = {layer["layer_id"]: set(layer["node_types"]) for layer in chain["layers"]}
    nodes = {entry["node_id"]: entry for entry in catalog["nodes"]}

    assert len(nodes) >= 120
    assert REQUIRED_NODE_IDS <= set(nodes)
    for node_id in REQUIRED_NODE_IDS:
        node = nodes[node_id]
        assert node["label"]
        assert node["source_candidates"]
        assert node["node_type"] in valid_layers[node["layer"]]
        assert node["canonical_name"]
        assert node["display_name"]
        assert node["chain_layer"] == node["layer"]
        assert node["description"]
        assert node["example_source_ids"]
        assert node["allowed_relationship_classes"]
        assert "production" not in str(node.get("production_status", "")).lower()


def test_node_type_catalog_has_concept_model_fields() -> None:
    catalog = load_yaml(NODE_PATH)

    for entry in catalog["node_types"]:
        assert "optional_attributes" in entry
        assert entry["allowed_outgoing_edges"]
        assert entry["allowed_incoming_edges"]
        assert entry["geography_terminology_policy"]


def test_china_taiwan_region_uses_canonical_parent_country_context() -> None:
    catalog = load_yaml(NODE_PATH)
    node = {entry["node_id"]: entry for entry in catalog["nodes"]}["region:china_taiwan"]

    assert node["node_type"] == "region"
    assert node["display_name"] == "中国台湾"
    assert node["attributes"]["country_id"] == "country:CN"
    assert node["attributes"]["country_display"] == "中国"
    assert node["geography_policy_passed"] is True


def test_node_catalog_keeps_fixture_status_and_no_production_claim() -> None:
    catalog = load_yaml(NODE_PATH)

    assert catalog["production_status"] == "research_fixture"
    assert catalog["data_mode"] == "fixture"
    assert catalog["calibration_status"] == "fixture_proxy_not_calibrated"
    assert "production-verified" not in str(catalog).lower()

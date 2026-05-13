# Semiconductor Supply-Chain Map

This map defines the canonical node and edge vocabulary used by the research platform. It is a fixture/proxy ontology foundation, not a production supply-chain database.

## Scope

The chain map is organized into twelve layers:

- `L0_policy_macro`: countries, regions, policy regimes, macro indicators, industrial policy, and export-control regimes.
- `L1_raw_minerals`: critical minerals, raw materials, mining countries, and refining countries.
- `L2_materials_chemicals`: wafer materials, electronic chemicals, photoresists, specialty gases, masks/reticles, substrates, and CMP materials.
- `L3_design_eda_ip`: design firms, EDA tools, IP cores, fabless firms, IDMs, and architectures.
- `L4_equipment`: semiconductor equipment, suppliers, categories, and components.
- `L5_fabrication`: foundries, fabs, process stages, technology nodes, capacity nodes, and wafer processes.
- `L6_products`: product grades, chip types, and downstream semiconductor products.
- `L7_packaging_testing`: OSAT firms, packaging stages, advanced packaging, substrates, and testing stages.
- `L8_logistics`: ports, airports, logistics routes, shipping lanes, and customs regions.
- `L9_downstream_demand`: downstream sectors, customer industries, and demand indicators.
- `L10_risk_events`: hazard, market, factory, cyber, labor, and general risk events.
- `L11_compliance`: policy events, sanctions events, restricted items, restricted entities, and compliance-risk context.

## Catalog Files

- `configs/ontology/semiconductor_chain_layers.yaml` defines the layer ordering and node types.
- `configs/ontology/semiconductor_node_catalog.yaml` provides concrete semiconductor node examples and source candidates.
- `configs/ontology/semiconductor_edge_catalog.yaml` defines allowable edge semantics and required provenance.

## Evidence Boundary

Every source-backed graph claim must carry source references, provenance URLs, evidence summaries, warnings, and graph/source metadata. Evidence-context links are explicitly marked as derived context and must not be displayed or counted as supply-chain dependency edges.

## Limitations

The catalog is intentionally bounded and source-bound. It does not claim complete company coverage, complete facility coverage, calibrated financial losses, or production readiness.

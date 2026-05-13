# Semiconductor Supply-Chain Concept Model

This concept model defines the research graph vocabulary used by Supply Risk Atlas. It is a fixture/proxy and promoted-public-evidence model, not a production data product.

The chain map is organized into twelve layers, `L0_policy_macro` through `L11_compliance`. Each layer has explicit node types in `configs/ontology/semiconductor_chain_layers.yaml`, concrete catalog seeds in `configs/ontology/semiconductor_node_catalog.yaml`, and allowed graph edge semantics in `configs/ontology/semiconductor_edge_catalog.yaml`.

Geography terminology is normalized before API visibility. The relevant China region is represented as `region:china_taiwan`, displayed as 中国台湾, and associated with `country:CN` / 中国. It is not represented as an independent country node.

The node catalog records:

- source candidates for every node type and concrete node;
- required and optional attributes for node types;
- allowed incoming and outgoing edge families;
- allowed relationship classes for concrete nodes;
- fixture-only status and calibration warnings.

The edge catalog keeps evidence-context links separate from supply-chain relationships. An `evidence_context_link` is inspection context only and carries `not_supply_chain_dependency: true`.

Known limits:

- concrete nodes are canonical seeds, not exhaustive coverage;
- source candidates do not imply complete source coverage;
- fixture/proxy metrics are not calibrated financial loss estimates;
- no live connector fetch occurs at import, startup, tests, CI, or Render startup.

# Supply-Demand Relationship Rebuild Log

## Gate 0 - Baseline, Readability, And Geography Terminology Normalization

- Timestamp: 2026-05-13T02:42:16.5491466-05:00
- Starting HEAD: 96d0bf6
- Gate status: PASS
- Changed files: shared geo terminology normalizer, API envelope sanitizer, connector text sanitizer, semiconductor fixture/public-real normalization paths, geography policy docs, repository-wide geography guard tests, Graph Explorer source/node coverage files already present in local WIP, and normalized tracked fixtures/docs/artifacts.
- Commands run:
  - python -m pytest tests/geo tests/quality -q -> PASS (16 passed)
  - python -m pytest tests/api -q -> PASS
  - python -m pytest -q -> PASS
  - 
pm.cmd --workspace apps/web run typecheck -> PASS
  - 
pm.cmd --workspace apps/web run build -> PASS
  - 
pm.cmd run smoke:web -> PASS (Browser smoke passed: 39 checks)
- Terminology normalization evidence:
  - Canonical region id is egion:china_taiwan.
  - Canonical display label is 中国台湾.
  - Parent country context is country:CN / 中国.
  - API envelopes sanitize chart/table/report/source/graph payloads before rendering.
  - Repository-wide guard scans tracked user-visible text files and core API/report outputs for forbidden old geography labels and identifiers.
  - Graph snapshot and graph view APIs expose the canonical region node and do not expose it as an independent country node.
- Source/legal notes: no live fetch was added or executed; fixture/promoted-public-evidence data remains bounded and source-referenced.
- Limitations:
  - The platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.
  - Internal alias modules keep legacy external-source aliases only for normalization and entity resolution.
  - Render deployment was not redeployed or claimed verified in this gate.
- Next gate decision: proceed to Gate 1 once this commit is created.

## Gate 1 - Canonical Semiconductor Supply-Chain Concept Model

- Gate status: PASS
- Changed files: `configs/ontology/semiconductor_node_catalog.yaml`, `docs/domain/semiconductor-supply-chain-concept-model.md`, `tests/contract/test_semiconductor_node_catalog.py`.
- Commands run:
  - `python -m pytest tests/contract/test_semiconductor_chain_layers.py tests/contract/test_semiconductor_node_catalog.py tests/contract/test_semiconductor_edge_catalog.py tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`14 passed`)
- Terminology normalization evidence: node catalog uses `region:china_taiwan`, display label `中国台湾`, and parent country context `country:CN` / `中国`.
- Limitations: catalog nodes remain canonical fixture seeds and do not assert production relationships.
- Next gate decision: proceed to relationship semantics.
## Gate 2 - Supply, Demand, Dependency, And Evidence Relationship Semantics

- Gate status: PASS
- Changed files: `configs/ontology/semiconductor_relationship_semantics.yaml`, `docs/domain/semiconductor-supply-demand-relationship-model.md`, `tests/contract/test_semiconductor_relationship_semantics.py`.
- Commands run:
  - `python -m pytest tests/contract/test_semiconductor_relationship_semantics.py tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`8 passed`)
- Terminology normalization evidence: relationship semantics carry `region:china_taiwan` / `中国台湾` and parent `country:CN` / `中国` policy.
- Limitations: relationship classes are semantics contracts; graph construction integration follows in later gates.
- Next gate decision: proceed to concrete node/source mapping validation and registry/contracts gates.
## Gate 3 - Concrete Semiconductor Node Catalog

- Gate status: PASS
- Changed files: `tests/contract/test_semiconductor_node_catalog.py`.
- Commands run:
  - `python -m pytest tests/contract/test_semiconductor_node_catalog.py tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`10 passed`)
- Evidence: node catalog has at least 120 concrete nodes and every concrete node has canonical/display names, chain layer, source candidates, allowed relationship classes, fixture-only status, and no production status.
- Terminology normalization evidence: `region:china_taiwan` is the canonical region node with display `中国台湾` and parent `country:CN` / `中国`.
- Limitations: node catalog remains a canonical seed catalog, not complete operational source coverage.
- Next gate decision: proceed to node-source map and data requirements.
## Gate 4 - Node-Source Map And Data Requirements

- Gate status: PASS
- Changed files: `configs/sources/semiconductor_node_source_map.yaml`, `docs/data/semiconductor-node-source-map.md`, `tests/sources/test_node_source_map.py`.
- Commands run:
  - `python -m pytest tests/sources/test_node_source_map.py tests/contract/test_semiconductor_node_source_map.py tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`14 passed`)
- Evidence: every L0-L11 layer has at least two candidate sources, every node type has a source candidate, and supply/demand/production-dependency/evidence classes each have source coverage.
- Terminology normalization evidence: geography-bearing source entries require normalization and the quality guard passed.
- Limitations: mapping identifies candidate evidence coverage only; it does not authorize live fetch or assert complete coverage.
- Next gate decision: proceed to expanded public source registry checks.
## Gate 5 - Expanded Public Source Registry

- Gate status: PASS
- Changed files: `configs/sources/semiconductor.yaml`, `packages/sra_core/sra_core/sources/models.py`, `tests/sources/test_source_registry_runtime.py`, `docs/data/public-source-catalog.md`.
- Commands run:
  - `python -m pytest tests/sources/test_source_registry_runtime.py tests/sources/test_source_license_policy.py tests/sources/test_source_status.py tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`14 passed`)
- Evidence: required public, review-required, and deferred sources are registry-visible; live fetch defaults remain disabled; geography normalization policy is present on API-visible registry rows.
- Limitations: registry entries are source governance metadata, not executed live ingestion.
- Next gate decision: proceed to data contract verification.
## Gate 6 - Data Contracts For Supply/Demand Source Types

- Gate status: PASS
- Changed files: supply, demand, and production dependency graph schemas plus expanded contract tests.
- Commands run:
  - `python -m pytest tests/contract/test_expanded_source_contracts.py tests/contract/test_graph_evidence_context_contract.py tests/contract/test_semiconductor_node_source_map.py tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`13 passed`)
- Evidence: raw contracts remain summary/hash/provenance only; graph contracts require provenance refs and relationship semantics; evidence-context remains separate.
- Limitations: schemas define contracts only; connector and graph construction integration follows.
- Next gate decision: proceed to connector framework and fixture connector verification.
## Gate 7 - Connector Framework And Fixture Connectors

- Gate status: PASS
- Changed files: log only; required connector framework and fixture connectors already existed and were verified.
- Commands run:
  - `python -m pytest tests/ingestion tests/sources tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`75 passed`)
- Evidence: connector framework, fixture connectors, source registry runtime, and no-startup-network tests passed; live fetch remains disabled by default.
- Terminology normalization evidence: connector fixtures and source outputs passed the repository-wide geography guard.
- Limitations: connector live paths remain architecture-only unless separately enabled by reviewed source policy and explicit admin/CLI trigger.
- Next gate decision: proceed to entity resolution and crosswalk policy checks.
## Gate 8 - Entity Resolution And Crosswalks

- Gate status: PASS
- Changed files: `tests/entity_resolution/test_geography_resolution_policy.py`.
- Commands run:
  - `python -m pytest tests/entity_resolution tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`20 passed`)
- Evidence: company, country/region, commodity, and policy crosswalk tests pass; legacy geography aliases resolve to `region:china_taiwan` with parent `country:CN` context.
- Limitations: low-confidence entity mentions remain unresolved instead of fabricating relationships.
- Next gate decision: proceed to relationship-aware graph construction.
## Gate 9 - Relationship-Aware Graph Construction

- Gate status: PASS
- Changed files: `graph_kernel/relationship_builder.py`, `graph_kernel/supply_demand_builder.py`, `graph_kernel/promoted_pipeline.py`, `services/api/routes/graph.py`, `services/api/services/graph_service.py`, `data/promoted/latest/*.json`, `tests/graph_invariants/test_supply_demand_relationships.py`, `tests/graph_invariants/test_relationship_class_separation.py`, `tests/graph_invariants/test_geography_normalized_graph.py`.
- Commands run:
  - `python -m pytest tests/graph_invariants/test_supply_demand_relationships.py tests/graph_invariants/test_relationship_class_separation.py tests/graph_invariants/test_geography_normalized_graph.py -q` -> PASS (`10 passed`)
  - `python -m pytest tests/graph_invariants tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`35 passed`)
  - `python -m pytest tests/api/test_graph_view_endpoints.py tests/api/test_graph_chart_table_endpoints.py -q` -> PASS (`17 passed`)
  - `python scripts/build_promoted_graph.py` -> PASS; regenerated sanitized promoted graph artifacts with relationship edge groups.
  - `python -m pytest tests/api -q` -> PASS (`108 passed`)
  - `python -m pytest tests/quality -q` -> PASS (`12 passed`)
- Evidence: promoted graph snapshots now expose separate `supply_edges`, `demand_edges`, `production_dependency_edges`, and `evidence_context_links`; supply edges carry supplied-item metadata, demand edges carry demand-proxy metadata, production dependencies carry criticality/substitutability metadata, and evidence-context links remain excluded from physical propagation.
- Terminology normalization evidence: promoted graph and graph invariant tests pass with `region:china_taiwan` / `中国台湾`; generated artifacts contain no old geography country node.
- Limitations: demand relationships remain fixture/proxy public-evidence signals, not production demand data; live connector fetch remains disabled.
- Next gate decision: proceed to supply-demand relationship API/view expansion.

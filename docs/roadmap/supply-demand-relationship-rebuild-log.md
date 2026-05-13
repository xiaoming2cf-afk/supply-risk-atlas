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
## Gate 10 - Supply-Demand Relationship Views

- Gate status: PASS
- Changed files: `services/api/services/graph_service.py`, `services/api/routes/graph.py`, `services/api/main.py`, `tests/api/test_supply_demand_graph_endpoints.py`, `packages/shared-types/src/graph.ts`, `packages/api-client/src/dashboard.ts`, `apps/web/src/features/graph-explorer/*RelationshipView.tsx`, `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx`, `apps/web/src/features/graph-explorer/GraphExplorer.tsx`, `apps/web/src/features/graph-explorer/GraphControls.tsx`, `apps/web/src/features/graph-explorer/graphViewModel.ts`, `scripts/browser-smoke.mjs`.
- Commands run:
  - `python -m pytest tests/api/test_supply_demand_graph_endpoints.py tests/api/test_graph_view_endpoints.py -q` -> PASS (`10 passed`)
  - `python -m pytest tests/api/test_supply_demand_graph_endpoints.py tests/api/test_graph_view_endpoints.py tests/api/test_graph_chart_table_endpoints.py tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`27 passed`)
  - `npm.cmd --workspace apps/web run typecheck` -> PASS
  - `npm.cmd --workspace apps/web run build` -> PASS
  - `npm.cmd run smoke:web` -> PASS (`43 checks`)
- Evidence: added `/api/v1/graph/supply-relationships`, `/api/v1/graph/demand-relationships`, `/api/v1/graph/production-dependencies`, and `/api/v1/graph/supply-demand-balance`; Graph Explorer exposes Supply, Demand, Production, and Balance table-first modes and smoke verifies all four.
- Terminology normalization evidence: geography quality guard passed; relationship views use backend-sanitized rows and do not expose raw payloads.
- Limitations: demand and balance values remain fixture/promoted public-evidence proxy counts, not calibrated production demand or supply capacity.
- Next gate decision: proceed to analytics relationship tables.
## Gate 11 - Analytics Tables For Supply/Demand/Supplier Relationships

- Gate status: PASS
- Changed files: `services/api/services/analytics_service.py`, `tests/api/test_supply_demand_analytics_tables.py`, `apps/web/src/features/common/tables/SupplyRelationshipTable.tsx`, `apps/web/src/features/common/tables/DemandRelationshipTable.tsx`, `apps/web/src/features/common/tables/ProductionDependencyTable.tsx`, `apps/web/src/features/common/tables/SupplierConcentrationTable.tsx`, `apps/web/src/features/common/tables/ProductDemandTable.tsx`, `apps/web/src/features/common/tables/CriticalInputTable.tsx`, `apps/web/src/features/common/tables/SupplyDemandBalanceTable.tsx`, `apps/web/src/features/common/tables/index.ts`.
- Commands run:
  - `python -m pytest tests/api/test_supply_demand_analytics_tables.py tests/security/test_export_sanitization.py tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`14 passed`)
  - `npm.cmd --workspace apps/web run typecheck` -> PASS
  - `npm.cmd --workspace apps/web run build` -> PASS
- Evidence: added bounded analytics table/export support for supply relationships, demand relationships, production dependencies, supplier concentration, product demand, critical inputs, and supply-demand balance; new frontend table wrappers use shared empty/loading/degraded states through `DataTable`.
- Terminology normalization evidence: export sanitization and geography quality guards passed; no raw payload keys are exposed.
- Limitations: table rows are fixture/promoted public-evidence summaries and proxy counts, not audited production supply-demand records.
- Next gate decision: proceed to supply-demand-specific charts and page integration.
## Gate 12 - Supply-Demand And Supplier Relationship Charts

- Gate status: PASS
- Changed files: supply-demand chart wrappers under `apps/web/src/features/common/charts/`, `apps/web/src/features/common/charts/index.ts`, `apps/web/src/features/graph-explorer/*RelationshipView.tsx`, `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx`, `apps/web/src/features/common/legacyDashboard.tsx`, `scripts/browser-smoke.mjs`.
- Commands run:
  - `npm.cmd --workspace apps/web run typecheck` -> PASS
  - `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`4 passed`)
  - `npm.cmd --workspace apps/web run build` -> PASS
  - `python -m pytest tests/api/test_supply_demand_analytics_tables.py tests/api/test_supply_demand_graph_endpoints.py tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`18 passed`)
  - `npm.cmd run smoke:web` -> PASS (`43 checks`)
- Evidence: added `SupplyDemandBalanceChart`, `SupplierConcentrationHHIChart`, `CriticalInputBottleneckChart`, `DownstreamDemandPressureChart`, `ProductToProcessDependencyChart`, `PolicyRestrictionImpactChart`, `HazardExposureByLayerChart`, and `SupplierCountryConcentrationChart`; smoke checks supply-demand chart cards on System Health, Entity Risk, Shock Simulator, Reverse Stress, Optimizer, and Graph Explorer relationship modes.
- Terminology normalization evidence: geography quality guard and browser smoke passed; charts use existing sanitized metadata and controlled empty states.
- Limitations: charts are evidence-bound summaries/proxy metrics; no production supply capacity, demand forecast, or financial loss claims are introduced.
- Next gate decision: proceed to documentation and glossary.
## Gate 13 - Documentation And Glossary

- Gate status: PASS
- Changed files: `docs/domain/semiconductor-supply-chain-glossary.md`, `docs/domain/supply-demand-supplier-relationship-guide.md`, `docs/data/supply-demand-data-requirements.md`, `docs/model/supply-demand-risk-usage.md`.
- Commands run:
  - `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`4 passed`)
  - `python -m pytest tests/contract/test_semiconductor_relationship_semantics.py tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`8 passed`)
- Evidence: docs define supply relationships, demand relationships, production dependencies, evidence context links, supplier/buyer/supplied-item terms, critical inputs, bottlenecks, substitutability, HHI, demand pressure, supply capacity proxy, and shortage proxy.
- Terminology normalization evidence: docs use `region:china_taiwan` / `中国台湾` and parent `country:CN` / `中国`; repository geography guard passed.
- Limitations: documentation describes fixture/proxy/promoted-public-evidence usage only and adds no production-readiness claim or live ingestion.
- Next gate decision: proceed to final acceptance tests.

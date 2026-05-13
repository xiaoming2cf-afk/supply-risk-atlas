# Semiconductor Node Data Visualization Build Log

## Gate 0 - Baseline And Quality Guard

- Current HEAD: `9cbb0e9`
- Gate name: baseline and readability guard
- Files changed:
  - `docs/roadmap/semiconductor-node-data-visualization-build-log.md`
- Commands run:
  - `python -m pytest tests/quality -q`
  - `python -m pytest tests/api -q`
  - `python -m pytest -q`
  - `npm.cmd --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run build`
  - `npm.cmd run smoke:web`
- Pass/fail: pass
- Evidence:
  - Quality tests passed: 8 tests.
  - API tests passed.
  - Full repository pytest passed.
  - Web typecheck passed.
  - Web production build passed.
  - Browser smoke passed 37 checks.
  - Readability tests cover `services/api`, `graph_kernel`, `ml`, `packages/sra_core/sra_core`, and `scripts`.
  - `tests/quality/test_service_layer_readability.py` exists and checks service/route modules for readable physical lines.
- Source/legal notes:
  - No live ingestion was run.
  - No raw payloads, bulk source data, private diagnostics, secrets, internal paths, cookies, authorization headers, API keys, PII, or evasion guidance were introduced.
- Limitations:
  - Current platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.
  - Generated local SQLite runtime files are local state and must not be committed.
- Next gate:
  - Proceed to Gate 1 canonical semiconductor supply-chain chain map.

## Gate 1 - Canonical Semiconductor Supply-Chain Chain Map

- Current HEAD: `3838327`
- Gate name: canonical chain layers, node catalog, and edge catalog
- Files changed:
  - `configs/ontology/semiconductor_chain_layers.yaml`
  - `configs/ontology/semiconductor_node_catalog.yaml`
  - `configs/ontology/semiconductor_edge_catalog.yaml`
  - `docs/domain/semiconductor-supply-chain-map.md`
  - `tests/contract/test_semiconductor_chain_layers.py`
  - `tests/contract/test_semiconductor_node_catalog.py`
  - `tests/contract/test_semiconductor_edge_catalog.py`
- Commands run:
  - `python -m pytest tests/contract/test_semiconductor_chain_layers.py tests/contract/test_semiconductor_node_catalog.py tests/contract/test_semiconductor_edge_catalog.py tests/sources/test_node_source_map.py -q`
  - `python -m pytest tests/quality -q`
- Pass/fail: pass
- Evidence:
  - New chain/node/edge catalog tests passed as part of the 12-test targeted contract/source-map run.
  - Quality tests passed: 8 tests.
  - The catalog defines all `L0` to `L11` layers, all requested node types, all requested concrete semiconductor node examples, and all requested edge semantics.
  - `evidence_context_link` carries `derived_context: true`, `not_supply_chain_dependency: true`, and user-facing label `evidence-context link`.
- Source/legal notes:
  - Catalog entries are source-candidate mappings and ontology seeds only.
  - No live ingestion was run and no raw source payload was added.
  - Compliance-related edges are documented as compliance-risk context only, with no evasion or bypass guidance.
- Limitations:
  - The node catalog is not a complete semiconductor supplier database.
  - Catalog nodes are not production-verified operational dependencies.
- Next gate:
  - Proceed to Gate 2 node-to-data-source mapping.

## Gate 2 - Node-To-Data-Source Mapping

- Current HEAD: `3838327`
- Gate name: semiconductor node source map
- Files changed:
  - `configs/sources/semiconductor_node_source_map.yaml`
  - `docs/data/semiconductor-node-source-map.md`
  - `tests/sources/test_node_source_map.py`
- Commands run:
  - `python -m pytest tests/contract/test_semiconductor_chain_layers.py tests/contract/test_semiconductor_node_catalog.py tests/contract/test_semiconductor_edge_catalog.py tests/sources/test_node_source_map.py -q`
  - `python -m pytest tests/quality -q`
- Pass/fail: pass
- Evidence:
  - Targeted contract/source-map run passed: 12 tests.
  - Every `L0` to `L11` layer has at least two source candidates.
  - Every canonical node type has at least one source candidate.
  - Every mapped source has graph outputs, `live_fetch_default: disabled`, and `fixture_required: true`.
- Source/legal notes:
  - Source map separates public evidence candidates from production claims.
  - Terms-review and manual-review sources remain non-live by default.
  - No connector fetch or network ingestion was executed.
- Limitations:
  - HS-code and public-source mappings remain proxy evidence and require explicit warnings in downstream views.
  - Source coverage is candidate coverage, not actual completeness.
- Next gate:
  - Proceed to Gate 3 expanded source registry and public source catalog.

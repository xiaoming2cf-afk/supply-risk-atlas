# Stage-Centered Visualization And Source Expansion Log

## Current HEAD

- Baseline HEAD before this continuation: `9d119739989b694fbf695d886879d2380dedfeef`
- Branch: `main`
- Preserved untracked paths: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`, `data/runtime/`

## Gate 0 - Audit And Readability

### Inventory

- Public evidence connectors exist under `packages/sra_core/sra_core/ingestion/connectors/`, including SEC EDGAR Lite, GDELT semiconductor Lite, UN Comtrade semiconductor trade Lite, WITS trade tariff Lite, USGS minerals Lite, USGS earthquake Lite, NGA World Port Index Lite, OFAC sanctions Lite, Consolidated Screening List Lite, BIS export controls Lite, Federal Register export controls Lite, ETO/CSET fixtures, and WSTS billings fixtures.
- Graph Explorer relationship views already existed for supply relationships, demand relationships, production dependencies, and supply-demand balance.
- Existing chart/table systems existed under `apps/web/src/features/common/charts/` and `apps/web/src/features/common/tables/`.
- Existing semantic files existed for chain layers, node catalog, edge catalog, relationship semantics, node-source map, relationship builder, supply-demand builder, and page relevance policy.
- Low-readability one-line target files were not present; readability guards were strengthened with `tests/quality/test_frontend_source_readability.py`.

### Commands

- `python -m pytest tests/quality -q` - pass
- `python -m pytest tests/api -q` - pass
- `python -m pytest -q` - pass
- `npm.cmd --workspace apps/web run typecheck` - pass
- `npm.cmd --workspace apps/web run build` - pass
- `npm.cmd run smoke:web` - pass, 51 baseline checks

## Gate 1 - Stage-Centered Source Coverage Matrix

### Files Changed

- Created `configs/sources/stage_source_coverage_matrix.yaml`
- Created `docs/data/stage-source-coverage-matrix.md`
- Created `tests/sources/test_stage_source_coverage_matrix.py`

### Result

- All L0-L11 stages now map to source candidates, node types, edge types, relationship classes, graph views, charts, tables, risk-model usage, simulation usage, source gaps, and coverage status.
- Each stage has at least two source candidates and at least one graph view, chart, and table.
- Live fetch remains disabled by default through the referenced connector policy.

## Gate 2 - Stage-Specific Graph Views

### Files Changed

- Created `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- Created 12 stage view wrappers:
  - `PolicyMacroGraphView.tsx`
  - `MineralDependencyGraphView.tsx`
  - `MaterialChemicalDependencyGraphView.tsx`
  - `DesignIPDependencyGraphView.tsx`
  - `EquipmentProcessDependencyGraphView.tsx`
  - `FabProcessGraphView.tsx`
  - `ProductDemandGraphView.tsx`
  - `PackagingTestingGraphView.tsx`
  - `LogisticsRouteGraphView.tsx`
  - `DownstreamDemandGraphView.tsx`
  - `EventTimelineGraphView.tsx`
  - `ComplianceRiskGraphView.tsx`
- Updated `apps/web/src/features/graph-explorer/GraphExplorer.tsx`
- Updated `apps/web/src/features/graph-explorer/GraphControls.tsx`

### Result

- Graph Explorer now includes a supply-chain stage selector and relationship-class selector.
- Stage views show graph version, source manifest, data mode, graph mode, source coverage, evidence refs, fixture/promoted warning, and declutter cap.
- Evidence-context links remain explicitly marked as non-dependency inspection links.

## Gate 3 - Backend Stage Graph Endpoints

### Files Changed

- Created `services/api/services/stage_graph_service.py`
- Created `services/api/routes/stage_graph.py`
- Updated `services/api/main.py`
- Created `tests/api/test_stage_graph_endpoints.py`

### Endpoints Added

- `GET /api/v1/stage-graph/{stage_id}`
- `GET /api/v1/stage-graph/{stage_id}/focus`
- `GET /api/v1/stage-graph/{stage_id}/source-coverage`
- `GET /api/v1/stage-graph/{stage_id}/evidence`
- `GET /api/v1/stage-graph/{stage_id}/tables`
- `GET /api/v1/stage-graph/{stage_id}/charts`

### Result

- Stage graph responses are bounded, sanitized, metadata-complete, and source-coverage aware.
- Stage graph tests verify all L0-L11 endpoints, focus caps, relationship-class filters, and no old region/country node IDs.

## Gate 4 - Stage Charts And Tables

### Files Changed

- Added stage chart components for source coverage, risk contribution, node coverage, evidence quality, mineral HHI, material supplier concentration, equipment restriction timeline, fab hazard exposure, product demand pressure, packaging capacity proxy, logistics route exposure, downstream demand mix, and compliance restriction matrix.
- Added stage table components for stage node catalog, stage source coverage, stage evidence refs, mineral inputs, material/chemical inputs, equipment suppliers, fab process dependencies, packaging/testing, logistics routes, and compliance restrictions.
- Updated chart/table indexes.
- Updated `services/api/services/graph_service.py` with first-class supply-demand and stage chart/table payloads.

### Result

- Stage-specific chart/table files exist and use controlled empty/degraded/loading-capable primitives.
- Analytics table payloads now include supply relationships, demand relationships, production dependencies, supplier concentration, product demand, critical inputs, and supply-demand balance.

## Gate 5 - Page Relevance Rebuild

### Files Changed

- Created `apps/web/src/features/common/PageSectionGuard.tsx`
- Updated `apps/web/src/features/common/pageRelevance.ts`
- Updated `scripts/browser-smoke.mjs`

### Result

- Page relevance policy now recognizes Graph Explorer stage selector and stage source coverage as relevant sections.
- Browser smoke verifies the Graph Explorer stage selector, relationship-class selector, and at least six stage view transitions.
- Dense graph remains constrained to graph-specific pages by existing page relevance smoke checks.

## Gate 6 - Connector Stage Coverage Audit

### Files Changed

- Created `docs/data/connector-stage-coverage-audit.md`
- Created `tests/sources/test_connector_stage_coverage.py`

### Result

- Each required public evidence connector is mapped to at least one L0-L11 stage.
- Every stage has at least two source candidates.
- Gaps are documented for mineral proxies, packaging capacity, logistics volume, and non-US disclosure coverage.

## Gate 7 - Supply-Demand Analytics Consolidation

### Files Changed

- Updated `services/api/services/graph_service.py`
- Existing analytics endpoints remain compatible.

### Result

- Existing supply/demand/dependency analytics endpoints remain bounded and metadata-complete.
- Chart payloads now include datasets for supply-demand balance, supplier concentration HHI, critical input bottlenecks, downstream demand pressure, product-to-process dependency, policy restriction impact, hazard exposure by layer, and supplier concentration.

## Gate 8 - Productized Graph Explorer Flow

### Files Changed

- Updated `GraphExplorer.tsx`, `GraphControls.tsx`, and stage view files.
- Updated `packages/api-client/src/dashboard.ts`.

### Result

- Graph Explorer flow now starts from stage, relationship class, and mode selection.
- The stage panel explains what the selected relationship class means and whether it can propagate risk.
- Evidence context remains explicitly non-propagating.

## Commands Run After Changes

- `python -m pytest tests/sources/test_stage_source_coverage_matrix.py tests/api/test_stage_graph_endpoints.py tests/quality/test_frontend_source_readability.py -q` - pass
- `python -m pytest tests/quality/test_python_source_readability.py tests/quality/test_service_layer_readability.py -q` - pass
- `python -m pytest tests/quality/test_frontend_source_readability.py tests/quality/test_stage_frontend_artifacts.py tests/sources/test_stage_source_coverage_matrix.py tests/sources/test_connector_stage_coverage.py tests/api/test_stage_graph_endpoints.py -q` - pass
- `python -m pytest tests/api/test_supply_demand_graph_endpoints.py tests/api/test_supply_demand_analytics_tables.py -q` - pass
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py tests/geo -q` - pass
- `python -m pytest tests/contract tests/sources tests/graph_invariants tests/api/test_stage_graph_endpoints.py tests/api/test_supply_demand_graph_endpoints.py tests/api/test_supply_demand_analytics_tables.py -q` - pass
- `npm.cmd --workspace apps/web run typecheck` - pass
- `npm.cmd --workspace apps/web run build` - pass
- `npm.cmd run smoke:web` - pass, 57 checks

## Failures And Fixes

- Initial new stage endpoint test incorrectly treated the canonical machine ID `region:china_taiwan` as a forbidden string. Fixed the test to forbid old region/country node IDs while allowing the required canonical ID.
- Initial frontend typecheck failed on a JSX `->` text node in the stage graph view. Escaped the text and normalized fallback row typing.

## Terminology Evidence

- Canonical region ID remains `region:china_taiwan`.
- Canonical display remains `中国台湾`.
- Parent country context remains `country:CN` / `中国`.
- New stage endpoint tests forbid old region/country node IDs.
- Geography tests passed after changes.

## Known Limitations

- Promoted graph node catalog coverage remains partial and is documented by existing quality reports.
- Stage graph endpoints use the existing fixture/promoted graph and coverage matrix; they do not perform live ingestion.
- Supplier shares, capacity values, qualification times, route volumes, and product demand values remain proxy summaries unless explicitly sourced.
- Some broader graph-kernel hardening items remain for a later task: full ontology validation inside promoted graph readiness, artifact/runtime path unification, and path traversal filtering through propagation-eligible relationship classes only.

## Computer Use And Deployment Status

- Computer Use was used only for project-scoped Render verification/redeploy.
- GitHub Actions for commit `b2980ed1b2454cb457a68cbd4a340cfd78b6437e` completed successfully for `ci` and `Quality Gates`.
- Render API service `supply-risk-atlas-api` was redeployed from commit `b2980ed1b2454cb457a68cbd4a340cfd78b6437e`; deploy evidence observed as live.
- Render Web service `supply-risk-atlas-web` was redeployed from commit `b2980ed1b2454cb457a68cbd4a340cfd78b6437e`; deploy evidence observed as live.
- Deployed API `/api/v1/version` reported git commit `b2980ed1b2454cb457a68cbd4a340cfd78b6437e`.
- Deployed smoke was run in best-effort mode and exposed an intermittent browser-side `Failed to fetch` on Entity Risk 360 despite direct deployed API and CORS checks returning success. The API client was updated to avoid unnecessary CORS preflight on GET/HEAD requests.
- A second deployed smoke run showed the same failure pattern on API-driven page requests. The deployed bundle confirmed pages could mount once with the initial `/api/v1` proxy client before runtime hostname resolution selected the direct API. The app shell was updated to hold API-driven pages until the runtime hostname is resolved.
- A follow-up deployment still showed browser-side fetch failures on Shock Simulator even though direct deployed API checks succeeded. The web proxy route was updated so Render web uses the public API origin instead of a potentially unavailable internal `SUPPLY_RISK_API_HOSTPORT`, allowing the frontend to use same-origin `/api/v1` on deployed web.
- Subsequent deployed smoke runs showed intermittent first-request HTTP 502 responses during Render warm-up. The API client now retries transient 5xx HTTP responses while still preserving controlled unavailable envelopes for persistent failures and non-retryable 4xx responses.
- Deployed web GET proxying stabilized, but Render's web route still returned 502 for POST proxying. The frontend client now supports a separate write API base URL so deployed POST actions call the API service directly while read requests continue using the same-origin web proxy.
- No secrets, cookies, tokens, account details, or private diagnostics were recorded.

## Post-Deployment Transport Fix

### Files Changed

- Updated `packages/api-client/src/dashboard.ts`
- Updated `apps/web/src/app/App.tsx`
- Updated `apps/web/src/app/api/v1/[...path]/route.ts`

### Result

- GET/HEAD dashboard API requests no longer add `content-type: application/json`.
- POST requests with JSON bodies still send `content-type: application/json`.
- This reduces deployed-browser CORS preflight surface for read-only dashboard and risk endpoint calls without changing API payload semantics.
- API-driven page components no longer mount with the initial unresolved same-origin proxy base URL on deployed web.
- Deployed web now resolves `/api/v1` proxy requests to the public API origin when the request host is the Render web host.
- Dashboard API calls now retry transient 5xx HTTP responses, reducing deployed smoke sensitivity to Render warm-up races.
- Deployed write actions can use `NEXT_PUBLIC_SUPPLY_RISK_API_WRITE_URL` or the default Render API origin, avoiding the web-service POST proxy path.

### Commands Run

- `npm.cmd --workspace apps/web run typecheck` - pass
- `python -m pytest tests/quality -q` - pass
- `npm.cmd --workspace apps/web run build` - pass
- `python -m pytest tests/api -q` - first run hit command timeout, rerun with longer timeout passed
- `npm.cmd run smoke:web` - pass, 57 checks

## Deployed Proxy Stabilization Follow-Up

### Files Changed

- Updated `apps/web/src/app/api/v1/[...path]/route.ts`
- Updated `scripts/browser-smoke.mjs`

### Result

- GitHub `ci` and `Quality Gates` passed for commit `ea9fd54d78c0901cc5155f6a92de794d3992cf8e`.
- Render API service `supply-risk-atlas-api` was redeployed to commit `ea9fd54d78c0901cc5155f6a92de794d3992cf8e` and observed live.
- Render Web service `supply-risk-atlas-web` was redeployed to commit `ea9fd54d78c0901cc5155f6a92de794d3992cf8e` and observed live.
- Deployed API `/api/v1/version` reported `ea9fd54d78c0901cc5155f6a92de794d3992cf8e`.
- Direct API and web proxy GET checks for Graph Explorer and risk portfolio returned HTTP 200 after Render warm-up.
- Deployed smoke still did not complete consistently because first page fetches can receive transient 502 responses from the deployed web proxy before the API service is fully warm.
- The web proxy now retries transient 502/503/504 responses for GET/HEAD requests only, with per-attempt timeouts so Render cold-start handling remains bounded. POST requests remain non-retried by the proxy, and deployed write calls continue to use the direct API write base.
- Deployed smoke and CI real-API smoke now use a longer wait budget for slow service warm-up; default local proxy smoke keeps the existing stricter wait budget.
- No secrets, cookies, tokens, account details, private URLs, or raw payloads were recorded.

### Commands Run

- `npm.cmd --workspace apps/web run typecheck` - pass
- `python -m pytest tests/quality -q` - pass
- `npm.cmd --workspace apps/web run build` - pass
- `npm.cmd run smoke:web` - pass, 57 checks
- `npm.cmd run smoke:web -- --mode=deployed` - best-effort incomplete before proxy retry deployment; Graph Explorer and Entity Risk pages saw transient 502 responses from the deployed web proxy

## Final Local Acceptance Evidence

- `python -m pytest tests/quality -q` - pass
- `python -m pytest tests/geo tests/contract tests/sources tests/graph_invariants tests/api tests/security tests/model tests/simulation tests/optimization tests/reports -q` - pass
- `python -m pytest -q` - pass
- `npm.cmd --workspace apps/web run typecheck` - pass
- `npm.cmd --workspace apps/web run build` - pass
- `npm.cmd run smoke:web` - pass, 57 checks

## Final Local Acceptance Status

- Stage-centered source coverage matrix exists.
- All L0-L11 stages have at least two source candidates and at least one graph view, chart, and table.
- Stage-specific graph view files exist.
- Backend stage graph endpoints exist and are bounded.
- Graph Explorer includes stage selector, relationship-class selector, and graph mode selector.
- Supply/demand/production dependency/evidence context remain visually and semantically separated.
- Connector-stage coverage audit exists.
- Supply-demand analytics endpoints remain bounded and metadata-complete.
- No raw payload exposure was introduced.
- No production-use claim was introduced.
- Deployment and ChatGPT handoff remain pending post-commit Computer Use.

## 2026-05-16 Data API And Relationship Evidence Hardening

### Current HEAD And Worktree Guard

- Starting HEAD: `13b3ece` (`Bound deployed proxy retry attempts`).
- Preserved local/untracked files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`, `data/runtime/`, and existing `docs/roadmap/codex-continuation-request.md`.
- Deployment before edits: deployed API `/api/v1/version` reported commit `13b3ece3e2f41918578a13c573905f1b16b73fab`.
- Known deployed limitation before edits: deployed smoke could still hit transient web-proxy/API warm-up failures even though warmed direct API and proxy endpoint probes returned HTTP 200.

### Gates Completed

- Gate 0 baseline and worktree guard: completed with local API/web stack. Initial local smoke without API returned controlled public-data-unavailable state; rerun with `python -m services.api.dev_server` and documented local API env passed.
- Gate 1 deployed data API access: browser API client now treats 5xx envelopes from idempotent reads as retryable, retries timeout/network failures only for idempotent reads, avoids retrying non-idempotent writes, and emits sanitized unavailable diagnostics (`failed_endpoint`, `retry_hint`, `transport_attempts`, `source_status`).
- Gate 2 relationship fallback masking: Supply, Demand, Production Dependency, and Supply-Demand Balance views no longer derive authoritative rows from local visible graph links/nodes when backend endpoints are unavailable. Degraded states are explicit and marked `unavailable-preview`.
- Gate 3 relationship evidence binding: supply/demand/production relationship rows now include `edge_type`, source/target IDs, source/evidence refs, validity windows, warnings, and calibration status. Relationship endpoints include top-level evidence refs, source status, and calibration status.

### Files Changed

- `packages/shared-types/src/common.ts`
- `packages/api-client/src/dashboard.ts`
- `apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/DemandRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/ProductionDependencyView.tsx`
- `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx`
- `graph_kernel/supply_demand_builder.py`
- `services/api/services/graph_service.py`
- `tests/api/test_supply_demand_graph_endpoints.py`
- `tests/quality/test_relationship_view_no_authoritative_fallbacks.py`

### Commands Run

- `python -m pytest tests/quality -q` - pass, 17 tests before edits; pass, 18 tests after edits
- `python -m pytest tests/api tests/graph_invariants tests/security -q` - pass before edits
- `npm.cmd --workspace apps/web run typecheck` - pass
- `npm.cmd --workspace apps/web run build` - pass
- `npm.cmd run smoke:web` - initial local run failed because no local API server was running; rerun with local API and web env passed, 61 checks
- `python -m pytest tests/quality/test_relationship_view_no_authoritative_fallbacks.py tests/api/test_supply_demand_graph_endpoints.py tests/graph_invariants/test_supply_demand_relationships.py tests/graph_invariants/test_relationship_class_separation.py -q` - pass, 14 tests

### Terminology And Safety Evidence

- No raw payload, authorization, API key, or forbidden geography output was introduced in touched endpoint tests.
- Evidence-context links remain excluded from supply, demand, and production dependency endpoints.
- Non-idempotent writes remain direct API writes and are not retried through the deployed web proxy path.

### Computer Use And Deployment Status

- Computer Use not yet used for this commit slice.
- GitHub push, CI verification, Render redeploy, deployed smoke, screenshots, and GPT Pro review are pending after commit.

## 2026-05-16 GPT Pro Review And Release Observability Slice

### GPT Pro Review Result

- Sent a sanitized status report for commit `c4609dc29e340dd66944aa6147f3b13181da907f` to the project ChatGPT conversation.
- GPT Pro returned a staged PASS for local/code/CI evidence, with deployment reservation because Render still served `13b3ece`.
- Next instruction from GPT Pro: harden version/deployment evidence, controlled degraded-state diagnostics, relationship evidence propagation consistency, stage-centered source coverage auditability, and deployed-smoke evidence without adding fake production data or claiming deployment success.

### Gates Completed

- Gate A baseline guard: current work started from `c4609dc`; preserved existing local/untracked files and did not stage `docs/roadmap/codex-continuation-request.md`, `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`, or `data/runtime/`.
- Gate B version evidence: API version now exposes sanitized `api_commit`, `web_commit`, `runtime_env`, `source_status`, and `commit_mismatch` while preserving legacy `git_commit`. System Health surfaces commit mismatch without exposing raw env values.
- Gate C controlled degraded diagnostics: app-level unavailable banners and Graph Explorer endpoint status now render sanitized diagnostics (`failed_endpoint`, `source_status`, `retry_hint`, `transport_attempts`, and app-level `last_checked_at`) without raw upstream URLs. Proxy error envelopes include bounded retry diagnostics.
- Gate D relationship consistency: relationship endpoint tests now require list-typed `source_refs`/`evidence_refs`, row warnings, calibration status, explicit validity fields, and continued exclusion of `evidence_context_link` rows.
- Gate E stage-centered source coverage: every L0-L11 stage now records `source_status`, `evidence_ref_count`, `calibration_status`, `failure_reason`, and `required_narrow_patch_if_failed`; partial stages explicitly state source gaps and next narrow fixes.
- Gate F CI future-proofing: workflow files use `actions/checkout@v5`, `actions/setup-node@v5`, Node 22, and `actions/setup-python@v5`; `quality-gates.yml` still uses `windows-latest`, so the runner migration warning remains a recorded TODO rather than a behavior change in this release slice.

### Files Changed

- `apps/web/src/app/App.tsx`
- `apps/web/src/app/api/v1/[...path]/route.ts`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `apps/web/src/features/graph-explorer/GraphExplorer.tsx`
- `configs/sources/stage_source_coverage_matrix.yaml`
- `packages/shared-types/src/health.ts`
- `services/api/services/stage_graph_service.py`
- `services/api/services/system_health_service.py`
- `services/api/services/version_service.py`
- `tests/api/test_stage_graph_endpoints.py`
- `tests/api/test_supply_demand_graph_endpoints.py`
- `tests/api/test_version_endpoint.py`
- `tests/quality/test_relationship_view_no_authoritative_fallbacks.py`
- `tests/sources/test_stage_source_coverage_matrix.py`

### Commands Run

- `python -m pytest tests/api/test_version_endpoint.py tests/sources/test_stage_source_coverage_matrix.py tests/api/test_stage_graph_endpoints.py tests/api/test_supply_demand_graph_endpoints.py tests/quality/test_relationship_view_no_authoritative_fallbacks.py -q` - pass, 34 tests
- `npm.cmd --workspace apps/web run typecheck` - pass
- `python -m pytest tests/quality -q` - pass, 19 tests
- `python -m pytest tests/api tests/graph_invariants tests/security -q` - pass
- `npm.cmd --workspace apps/web run build` - pass
- `npm.cmd run smoke:web` with local API/Web - pass, 61 checks
- `python -m pytest -q` - pass

### Deployment Status

- Deployment status remains `deployed_stale_or_unverified` until Render API/Web report the new commit and deployed smoke passes or reaches only a controlled unavailable state with matching version evidence.
- Previous deployed check showed API `/api/v1/version` still at `13b3ece3e2f41918578a13c573905f1b16b73fab`; no deployment success is claimed here.

### Safety Evidence

- No live fetch behavior was enabled.
- No raw payload, authorization header, cookie, token, private path, or secret-bearing diagnostics were introduced.
- Relationship views keep authoritative rows empty when relationship endpoints are unavailable.
- Evidence-context links remain non-propagating and excluded from supply/demand/production relationship rows.

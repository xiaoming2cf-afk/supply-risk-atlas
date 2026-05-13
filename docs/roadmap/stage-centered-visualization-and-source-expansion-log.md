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
- The web proxy now retries transient 502/503/504 responses for GET/HEAD requests only. POST requests remain non-retried by the proxy, and deployed write calls continue to use the direct API write base.
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

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

### Post-Push CI And Deployed Evidence

- Commit `8942950` pushed to `origin/main`.
- GitHub Actions `ci` passed for `8942950`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25963294094`.
- GitHub Actions `Quality Gates` passed for `8942950`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25963294096`.
- `python scripts/check-deployed-version.py --expected-commit 8942950` returned `stale_or_unverified`; the direct version probe still reported deployed API commit `13b3ece3e2f41918578a13c573905f1b16b73fab`.
- `npm.cmd run smoke:web -- --mode=deployed` ran in best-effort mode and exited without failing the shell, but the smoke did not complete. It reached Entity Risk 360 and reported a controlled unavailable state with redacted endpoint diagnostics, `source_status=unavailable`, and HTTP 502 diagnostic messages.
- Deployment status remains `deployed_stale_or_unverified`; do not claim deployed completion until Render API/Web expose the latest HEAD and deployed smoke passes or reports only expected controlled degradation with matching version evidence.

### Safety Evidence

- No live fetch behavior was enabled.
- No raw payload, authorization header, cookie, token, private path, or secret-bearing diagnostics were introduced.
- Relationship views keep authoritative rows empty when relationship endpoints are unavailable.
- Evidence-context links remain non-propagating and excluded from supply/demand/production relationship rows.

## 2026-05-16 GPT Pro R1-R4 Review And Deployed Checker Patch

### GPT Pro Review Result

- Sent a sanitized second-round status report for commits `c4609dc`, `8942950`, and `9674e60` to the project ChatGPT conversation.
- GPT Pro returned `judgment: PASS`, `blocking_issue: NONE`, and `narrow_patch_required: NONE` for the M1-4 stage-start narrow patch review.
- GPT Pro authorized the next action only after R1/R2/R3/R4 review: forward the judgment to four reviewers and begin the M1-4 W6 candidate inventory only if all reviewers pass without reservation.

### R1-R4 Review Status

- R1 implementation reliability review: PASS. It verified API read retry behavior, sanitized diagnostics, version metadata, proxy error envelopes, app/Graph Explorer diagnostics, and no authoritative fallback rows.
- R2 deployment evidence review: FAIL on one narrow issue. `scripts/check-deployed-version.py` treated short SHA `8942950` and the matching full SHA as different commits, which could leave deployment evidence incorrectly `stale_or_unverified`.
- R3 relationship semantics review: PASS. It verified relationship class separation, evidence-context exclusion from propagation, relationship endpoint metadata, and no backend-unavailable authoritative fallback rows.
- R4 safety/governance review: initial FAIL on two narrow issues. Runtime artifacts under `data/runtime/` were untracked but not ignored, and raw scan coverage did not block tracked `.db`/`.raw` runtime artifacts. The first deployed checker patch also accepted any alphanumeric prefix instead of Git SHA hex only.
- R4 final re-review: PASS after the continuation request, deployed checker, raw scan, runtime ignore, and new quality tests were patched.

### Narrow Patch

- `.gitignore` now excludes `data/runtime/` so local SQLite/debug runtime files are preserved but not accidentally staged.
- `scripts/check-deployed-version.py` now treats sanitized Git SHA hex values as matching when either value is a prefix of the other, while rejecting unknown, too-short, non-hex, or unrelated values.
- `scripts/check-no-raw-payloads.py` now fails if raw/runtime artifacts such as `data/runtime/*`, `data/raw/*`, `.db`, `.raw`, `.parquet`, or pickle files are tracked.
- `tests/quality/test_deployed_version_checker.py` covers short-vs-full SHA matching in both directions and rejection of unknown/unrelated commit values.
- `tests/quality/test_no_tracked_runtime_artifacts.py` covers tracked runtime database/raw files and raw artifact suffixes outside runtime.
- R4 re-review then identified three more governance issues:
  - `docs/roadmap/codex-continuation-request.md` contained stale deployment-success claims for an older commit.
  - The same continuation file recorded a private ChatGPT conversation URL.
  - Web commit detection could mark a 7-character SHA that appeared anywhere in HTML as verified.
- `docs/roadmap/codex-continuation-request.md` was rewritten as a sanitized, conservative continuation request: deployment remains `deployed_stale_or_unverified`, private operational URLs are not recorded, and GPT Pro/R1-R4 status is summarized without secrets.
- `scripts/check-deployed-version.py` now requires at least a 12-character bounded SHA token for Web HTML commit visibility; 7-character generic HTML matches no longer verify Web deployment.

### Commands Run

- `python -m pytest tests/quality/test_deployed_version_checker.py -q` - pass, 3 tests
- `python -m py_compile scripts/check-deployed-version.py` - pass
- `python -m pytest tests/quality/test_deployed_version_checker.py tests/api/test_version_endpoint.py tests/sources/test_stage_source_coverage_matrix.py tests/quality/test_no_forbidden_geography_labels.py -q` - pass, 15 tests
- `python scripts/check-deployed-version.py --expected-commit 9674e60 --api-url http://127.0.0.1:1/api/v1 --web-url http://127.0.0.1:1` - expected conservative failure with sanitized `stale_or_unverified`, `api_commit_unknown`, and no raw response body
- `python -m pytest tests/quality/test_deployed_version_checker.py tests/quality/test_no_tracked_runtime_artifacts.py tests/api/test_version_endpoint.py tests/sources/test_stage_source_coverage_matrix.py tests/quality/test_no_forbidden_geography_labels.py -q` - pass, 17 tests
- `python scripts/check-no-raw-payloads.py` - pass
- `python -m py_compile scripts/check-deployed-version.py scripts/check-no-raw-payloads.py` - pass
- `git status --short --ignored data/runtime` - shows `!! data/runtime/`, confirming runtime files are ignored
- `python -m pytest tests/quality/test_deployed_version_checker.py tests/quality/test_no_tracked_runtime_artifacts.py tests/sources/test_stage_source_coverage_matrix.py tests/quality/test_no_forbidden_geography_labels.py -q` - pass, 17 tests
- `rg -n "chatgpt\\.com/g/|live at commit|deployed smoke passed|reports the expected commit|9d119739" docs\\roadmap scripts tests -g "*.md" -g "*.py" -g "*.mjs"` - no current continuation private URL or stale deployment-success claim; remaining hits are historical deployment log context or baseline commit references
- R4 final re-review ran `python -m pytest tests/quality/test_deployed_version_checker.py tests/quality/test_no_tracked_runtime_artifacts.py tests/sources/test_stage_source_coverage_matrix.py tests/quality/test_no_forbidden_geography_labels.py -q -p no:cacheprovider` - pass, 17 tests

### Computer Use And Deployment Status

- Computer Use used Chrome only for the project ChatGPT conversation and sanitized GPT Pro review handoff.
- A stale Render login page was identified; closing it through browser automation timed out, so no further Render UI action was attempted in that failed page.
- No credentials, cookies, tokens, private diagnostics, raw payloads, screenshots with secrets, or unrelated personal content were copied into the log or GPT Pro handoff.
- Deployment remains `deployed_stale_or_unverified`; no deployed-complete claim is made.

### Post-Push Evidence

- Commit `8c04c14` pushed to `origin/main`.
- GitHub Actions `ci` passed for `8c04c14`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25965269537`.
- GitHub Actions `Quality Gates` passed for `8c04c14`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25965269558`.
- `python scripts/check-deployed-version.py --expected-commit 8c04c14 --timeout 20` returned sanitized `stale_or_unverified` with `api_commit_unknown` and Web `HTTPError`; deployment is still not verified.

## 2026-05-16 CI Browser Smoke Launch Stabilization

### Current HEAD

- Local HEAD before this narrow patch: `cdc242993b4bd358100683db775989615830aa56`.
- Preserved untracked local files: `apps/web/AGENTS.md` and `apps/web/CLAUDE.md`.
- `data/runtime/` remains ignored and untracked.

### Failure Evidence

- Commit `cdc2429` pushed to `origin/main`.
- GitHub Actions `Quality Gates` passed for `cdc2429`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25965525247`.
- GitHub Actions `ci` failed for `cdc2429`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25965525265`.
- The failing job was the browser-smoke job. The sanitized failure was `Chrome DevTools did not become ready: fetch failed` before page assertions ran.
- Local real-API browser smoke continued to pass, so this was treated as CI Chrome launch instability rather than a page relevance or API regression.

### Narrow Patch

- `scripts/browser-smoke.mjs` now uses CI-safe Chrome launch flags:
  - `--no-sandbox`
  - `--disable-setuid-sandbox`
  - `--disable-background-networking`
  - `--disable-extensions`
  - `--remote-debugging-address=127.0.0.1`
- Chrome DevTools startup wait is now configurable through `SUPPLY_RISK_CHROME_READY_MS` and defaults to 30 seconds.
- The smoke script now reports a bounded `chrome_exited` diagnostic if Chrome exits before DevTools is available.
- `tests/quality/test_frontend_source_readability.py` now guards the CI-hardened Chrome launch requirements.

### Commands Run

- `python -m pytest tests/quality/test_frontend_source_readability.py tests/quality/test_deployed_version_checker.py tests/quality/test_no_tracked_runtime_artifacts.py -q` - pass, 12 tests
- `npm.cmd --workspace apps/web run typecheck` - pass
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_EXPECT_MODE=real npm.cmd run smoke:web` - pass, 61 checks

### Deployment Status

- Deployment remains `deployed_stale_or_unverified`.
- No Render deployment success is claimed until the deployed API/Web version endpoint reports the latest commit and deployed smoke passes or returns only controlled, actionable unavailable diagnostics.

### Post-Push Evidence

- Commit `99132bd3803073f42a28cbb24cdfbf7dd23345ad` pushed to `origin/main`.
- GitHub Actions `ci` passed for `99132bd`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25966115107`.
- GitHub Actions `Quality Gates` passed for `99132bd`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25966115177`.
- `python scripts/check-deployed-version.py --expected-commit 99132bd --timeout 20` returned sanitized `stale_or_unverified` with `api_commit_unknown` and Web `HTTPError`; deployment is still not verified.

## 2026-05-16 Crash Recovery And Deployment Handoff

### Current HEAD

- Local HEAD at recovery: `5147d4f0e972428ccef1010ec3d8b7d7a1d31031`.
- Recent pushed commits:
  - `99132bd3803073f42a28cbb24cdfbf7dd23345ad` - CI browser smoke launch stabilization.
  - `5147d4f0e972428ccef1010ec3d8b7d7a1d31031` - browser smoke CI recovery evidence.
- Preserved untracked local files:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`
- `data/runtime/` remains ignored and untracked.

### GitHub Evidence

- GitHub Actions `ci` passed for `5147d4f`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25966256323`.
- GitHub Actions `Quality Gates` passed for `5147d4f`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25966256330`.

### Recovery Commands

- `python -m pytest tests/quality -q` - pass, 28 tests.
- `python scripts/check-deployed-version.py --expected-commit 5147d4f --timeout 20` - expected failure with sanitized `stale_or_unverified`.

### Deployment Probe Evidence

- Expected commit: `5147d4f`.
- Deployed API status: `ok`, but reported old commit `13b3ece3e2f41918578a13c573905f1b16b73fab`.
- Deployed Web status: `commit_not_visible`; commit marker for `5147d4f` was not visible.
- Deployment status remains `deployed_stale_or_unverified`.
- No deployed-complete claim is made.

### GPT Pro Review

- A sanitized GPT Pro review packet was submitted after commit `5147d4f`.
- GPT Pro accepted the CI/browser-smoke stabilization step.
- GPT Pro identified deployment consistency as the next priority before further stage-centered data/API enrichment.

### Computer Use Actions

- Computer Use was used only for project-scoped Chrome/GitHub/GPT Pro/Render inspection.
- Render redeploy could not be completed because automation reached an interactive Render sign-in page.
- No credentials were typed or submitted.
- No cookies, tokens, screenshots with secrets, raw payloads, private diagnostics, account details, private operational URLs, or unrelated personal content were copied into repository files or GPT Pro handoff.

### Known Limitations And Next Step

- Render deployment remains blocked until the user manually completes Render sign-in or provides a safe local Render automation path outside chat.
- After Render access is available, redeploy API/Web from latest `main`, verify `/api/v1/version`, run deployed endpoint probes, run deployed smoke, and record sanitized evidence.
- If deployment is deferred, continue with local-only data/API hardening only after recording that decision.

## 2026-05-16 Worker D QA/Security/Product Hardening Audit

### Findings

- Low-readability critical file guards, forbidden geography output guards, raw/private payload scans, unsafe compliance-language tests, and targeted graph/page quality checks passed locally.
- Current local WIP includes app/API-client read-fallback work and supply-demand aggregate row hardening owned by other workers; this audit did not modify those files.
- Smallest remaining product-hardening patch: extend `scripts/browser-smoke.mjs` page-relevance expectations to cover every public nav page it already visits, especially Global Risk Cockpit, Prediction Center, Path Analysis, and Country Lens, so dense-graph allowance is smoke-checked outside Graph Explorer as well.

### Commands Run

- `python scripts/check-no-one-line-python.py` - pass
- `python scripts/check-no-raw-payloads.py` - pass
- `python -m pytest tests/quality/test_python_source_readability.py tests/quality/test_frontend_source_readability.py tests/quality/test_no_forbidden_geography_labels.py tests/security/test_no_raw_payload_exposure.py tests/security/test_unsafe_compliance_language.py tests/quality/test_graph_context_safety.py tests/quality/test_stage_frontend_artifacts.py tests/quality/test_relationship_view_no_authoritative_fallbacks.py tests/quality/test_deployed_api_transport_fallback.py tests/api/test_supply_demand_graph_endpoints.py tests/api/test_graph_chart_table_endpoints.py -q` - pass, 40 tests
- `npm.cmd --workspace apps/web run typecheck` - pass

## 2026-05-16 Stage-Centered Data/API Hardening Gate

### Current HEAD

- Local HEAD before this implementation gate: `17b5b92f900d563ef8fec1b7cc74f1238c19caac`.
- Preserved untracked local files: `apps/web/AGENTS.md` and `apps/web/CLAUDE.md`.
- `data/runtime/` remains ignored and untracked.

### Gate Result

- Deployed data API access hardening: pass locally. The deployed web client now wires direct public API reads with same-origin proxy fallback while keeping write calls on the configured write API origin.
- Relationship view failure masking hardening: pass locally. Supply, demand, production dependency, and supply-demand balance views accept only active backend endpoint data for the selected mode and render `unavailable_preview` states otherwise.
- Relationship evidence binding: pass locally. Supply/demand/production endpoint rows include row-level graph/source/data-mode metadata, refs, warnings, calibration/source status, and evidence-context exclusion. Supply-demand balance rows are explicitly aggregate rows and not dependency edges.
- Stage source coverage enrichment: pass locally. L0-L11 stages now record source families, fixture/live-disabled defaults, no-raw-source-records policy, and proxy limitations for national/policy/macro, enterprise disclosure, and industry fixture sources.
- Page relevance smoke hardening: pass locally. Browser smoke now checks relevance policy for Global Risk Cockpit, Prediction Center, Path Analysis, and Country Lens in addition to the existing analytical pages.

### Changed Files

- `apps/web/src/app/App.tsx`
- `packages/api-client/src/dashboard.ts`
- `packages/shared-types/src/graph.ts`
- `apps/web/src/features/graph-explorer/GraphExplorer.tsx`
- `apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/DemandRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/ProductionDependencyView.tsx`
- `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx`
- `services/api/services/graph_service.py`
- `graph_kernel/supply_demand_builder.py`
- `configs/sources/stage_source_coverage_matrix.yaml`
- `docs/data/stage-source-coverage-matrix.md`
- `docs/data/connector-stage-coverage-audit.md`
- `scripts/browser-smoke.mjs`
- `tests/api/test_supply_demand_graph_endpoints.py`
- `tests/quality/test_deployed_api_transport_fallback.py`
- `tests/quality/test_relationship_view_no_authoritative_fallbacks.py`
- `tests/sources/test_stage_source_coverage_matrix.py`
- `tests/sources/test_connector_stage_coverage.py`

### Commands Run

- `python -m pytest tests/quality/test_deployed_api_transport_fallback.py -q` - pass, 2 tests.
- `npm.cmd --workspace apps/web run typecheck` - pass.
- `python -m pytest tests/api/test_supply_demand_graph_endpoints.py tests/graph_invariants/test_supply_demand_relationships.py tests/graph_invariants/test_relationship_class_separation.py -q` - pass, 13 tests.
- `python -m pytest tests/quality/test_deployed_api_transport_fallback.py tests/quality/test_relationship_view_no_authoritative_fallbacks.py -q` - pass, 4 tests.
- `python -m pytest tests/sources/test_stage_source_coverage_matrix.py tests/sources/test_connector_stage_coverage.py tests/quality/test_no_forbidden_geography_labels.py -q` - pass, 15 tests.
- `python -m pytest tests/quality/test_relationship_view_no_authoritative_fallbacks.py tests/quality/test_frontend_source_readability.py tests/quality/test_deployed_api_transport_fallback.py tests/sources/test_stage_source_coverage_matrix.py tests/sources/test_connector_stage_coverage.py tests/api/test_supply_demand_graph_endpoints.py tests/graph_invariants/test_supply_demand_relationships.py tests/graph_invariants/test_relationship_class_separation.py tests/quality/test_no_forbidden_geography_labels.py -q` - pass, 37 tests.
- `npm.cmd --workspace apps/web run typecheck` - pass.
- `npm.cmd --workspace apps/web run typecheck:packages` - pass.
- `npm.cmd --workspace apps/web run build` - pass.
- `python -m pytest tests/quality -q` - pass, 30 tests.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_EXPECT_MODE=real npm.cmd run smoke:web` - pass, 65 checks.

### Failures And Limitations

- Deployment remains `deployed_stale_or_unverified`; the latest deployed probe before this gate still reported old API commit `13b3ece3e2f41918578a13c573905f1b16b73fab` and no visible Web commit marker.
- Render redeploy remains blocked by interactive Render sign-in until the user completes sign-in or configures a safe local Render automation path.
- Data-source coverage is richer and more explicit, but still fixture/promoted-public-evidence only. Live fetch remains disabled by default.

### Computer Use Status

- No new Computer Use action was performed during this local implementation gate.
- Prior GPT Pro review accepted the CI/browser-smoke stabilization step and made deployment consistency the next priority before further deployed claims.

### Post-Push Evidence

- Commit `623adacf823a417a4b0558010e444430d978f08b` pushed to `origin/main` through SSH after repeated HTTPS connection resets.
- GitHub Actions `ci` passed for `623adac`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25968271852`.
- GitHub Actions `Quality Gates` passed for `623adac`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25968271843`.
- `python scripts/check-deployed-version.py --expected-commit 623adac --timeout 20` returned sanitized `stale_or_unverified`; API and Web probes failed in that run, so deployed success is not claimed.
- Render redeploy remains blocked by interactive login or missing safe local Render automation credentials.

## 2026-05-16 Deployment Version And Relationship Authority Regression Closure

### Current HEAD

- Local HEAD before this gate: `18cdd05db779337b1dcfb8550a97f270018960be`.
- Preserved untracked local files:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`
- `data/runtime/` remains ignored runtime state and was not staged.

### Gate Result

- Deployment version semantics hardened locally. Version payloads now expose explicit `deployment_readiness_state`, `deployment_stale_or_unverified`, `deployment_unavailable`, and sanitized `last_checked_at` fields.
- Deployed version checker hardened locally. Status values are limited to `deployed_verified`, `deployed_stale_or_unverified`, `deployed_unavailable`, and `probe_error`; exact deployed success requires API/Web commit verification.
- Relationship authority regression fixed locally. Browser smoke now probes backend relationship endpoints before deciding whether a relationship view must show authoritative backend rows or only a controlled `unavailable_preview`.
- Local data API access regression fixed. `services/api/dev_server.py` now exposes the same graph view and relationship endpoints needed by local web proxy and direct API smoke.
- Relationship exports remain backend-authoritative. Graph Explorer relationship exports use backend endpoint data only; unavailable previews are labeled and excluded from relationship rows.
- Source coverage policy clarified. `unavailable_preview` and unavailable relationship endpoints do not count as source/stage coverage.
- Page relevance smoke now checks visible shared metadata, disallowed major sections, deployment-success claims, dense graph allowance, Path Analysis, and Country Lens.

### Files Changed

- `apps/web/src/app/App.tsx`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `apps/web/src/features/graph-explorer/GraphExplorer.tsx`
- `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx`
- `configs/sources/stage_source_coverage_matrix.yaml`
- `docs/data/stage-source-coverage-matrix.md`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`
- `packages/shared-types/src/health.ts`
- `scripts/browser-smoke.mjs`
- `scripts/check-deployed-version.py`
- `services/api/dev_server.py`
- `services/api/services/graph_service.py`
- `services/api/services/system_health_service.py`
- `services/api/services/version_service.py`
- `tests/api/test_dev_server_graph_routes.py`
- `tests/api/test_supply_demand_graph_endpoints.py`
- `tests/api/test_system_health_semiconductor_graph.py`
- `tests/api/test_system_health_storage_sources.py`
- `tests/api/test_version_endpoint.py`
- `tests/quality/test_deployed_version_checker.py`
- `tests/quality/test_relationship_view_no_authoritative_fallbacks.py`
- `tests/sources/test_connector_stage_coverage.py`
- `tests/sources/test_stage_source_coverage_matrix.py`

### Commands Run

- `python -m pytest tests/api/test_dev_server_graph_routes.py tests/api/test_supply_demand_graph_endpoints.py -q` - pass, 9 tests.
- `python -m pytest tests/quality -q` - pass, 35 tests.
- `python -m pytest tests/geo tests/contract tests/sources tests/graph_invariants tests/api tests/security tests/model tests/simulation tests/optimization tests/reports -q` - pass.
- `python -m pytest -q` - pass.
- `npm.cmd --workspace apps/web run typecheck` - pass.
- `npm.cmd --workspace apps/web run typecheck:packages` - pass.
- `npm.cmd --workspace apps/web run build` - pass.
- `npm.cmd run smoke:web` - pass, 63 checks.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_EXPECT_MODE=real npm.cmd run smoke:web` - pass, 67 checks.
- `python scripts/check-no-raw-payloads.py` - pass.
- `python scripts/check-deployed-version.py --expected-commit 18cdd05 --timeout 20` - controlled failure with `deployed_unavailable`; deployed success is not claimed.

### Deployment Probe Evidence

- Expected commit during local probe: `18cdd05`.
- Deployment status: `deployed_unavailable`.
- Sanitized warnings: `api_unavailable`, `web_unavailable`, `web_proxy_unavailable`.
- No Render credentials were submitted.
- No tokens, cookies, raw payloads, local filesystem diagnostics, private account details, or PII were recorded.

### Known Limitations

- Render deployment remains unverified and unavailable from automation until project-scoped Render access is restored safely.
- The latest local implementation still needs to be committed, pushed, and verified in GitHub Actions before any new GPT Pro review packet is sent.
- The platform remains fixture/proxy/promoted-public-evidence research infrastructure; no deployment success or operational readiness claim is made.

### Post-Push Evidence

- Commit `9217e128db7b7359ee53388d2e2f6fce8abf6380` pushed to `origin/main`.
- GitHub Actions `ci` passed for `9217e12`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25969818506`.
- GitHub Actions `Quality Gates` passed for `9217e12`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25969818499`.
- `python scripts/check-deployed-version.py --expected-commit 9217e12 --timeout 20` returned `deployed_stale_or_unverified`.
- Deployed API reported old commit `13b3ece3e2f41918578a13c573905f1b16b73fab`.
- Deployed Web HTML did not expose the `9217e12` commit marker.
- Deployed Web proxy reported old commit `13b3ece3e2f41918578a13c573905f1b16b73fab`.
- Browser/Computer Use attempt for Render/GPT Pro handoff was blocked because the Browser runtime reported no active Codex browser pane.
- Render API credentials were not present in the local environment.
- No Render login credentials were typed, no redeploy was triggered, and no GPT Pro message was sent after `9217e12`.
- A later probe against latest local HEAD `377d83d` still returned `deployed_stale_or_unverified`; deployed API and Web proxy continued to report old commit `13b3ece3e2f41918578a13c573905f1b16b73fab`.
- `npm.cmd run smoke:web -- --mode=deployed` did not complete in deployed best-effort mode because the stale deployed Entity Risk 360 page still received 502 responses for entity risk and portfolio endpoints.
- The deployed smoke failure is attributed to stale/unverified deployment state, not to local test failures.

### Next-Step Request

- Restore safe project-scoped Browser/Chrome access or provide a safe local Render automation path outside chat.
- Redeploy Render API and Web from latest `main`.
- Verify `/api/v1/version` reports `9217e12` or a newer commit.
- Run deployed endpoint probes and `npm run smoke:web -- --mode=deployed`.
- Send GPT Pro a concise sanitized review packet after deployed verification is available.

## 2026-05-16 Web Commit Marker And Stage Source Visibility Gate

### Current HEAD

- Local HEAD before this gate: `bad60410999b4217bba26c5769b1fe0188bd3b9b`.
- Preserved untracked local files:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`
- `data/runtime/` remains ignored runtime state and was not staged.

### Gate Result

- Deployment probe now shows API and Web proxy reporting `bad60410999b4217bba26c5769b1fe0188bd3b9b`, but Web HTML still lacks a commit marker, so deployment remains `deployed_stale_or_unverified`.
- Render UI access remains blocked at the Render sign-in page; no credentials were entered. The failed page was closed before continuing to avoid page buildup.
- Browser/Computer Use could not open the GPT Pro project after the Render login attempt because the Browser runtime reported no active Codex browser pane.
- Web build commit marker root cause addressed locally: the Next config now derives `NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT` from Render/git at build time without requiring a manual Render env var.
- `render.yaml` deployment trigger comment was updated so both API and Web build filters can observe a deployment-relevant tracked file change.
- Stage graph API now returns `source_families`, `source_family_coverage`, `source_gaps`, `proxy_limitations`, `primary_sources`, `secondary_sources`, and `required_data_fields` so national, enterprise, and industry evidence coverage is visible at page/API level.
- Graph Explorer stage views now render source-family coverage, source gaps, and proxy limitations instead of hiding them behind config/docs.
- Dev server route parity improved for stage graph endpoints, named analytics table endpoints, and analytics export endpoints.
- Supply-demand balance aggregate rows now include row-level graph/source/data-mode metadata, source status, validity fields, source refs, evidence refs, warnings, and calibration status.
- Deployed version checker now honors API-reported deployment stale/unavailable readiness fields instead of relying only on external commit probes.

### Files Changed

- `apps/web/next.config.mjs`
- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`
- `render.yaml`
- `scripts/check-deployed-version.py`
- `services/api/dev_server.py`
- `services/api/services/graph_service.py`
- `services/api/services/stage_graph_service.py`
- `tests/api/test_dev_server_graph_routes.py`
- `tests/api/test_stage_graph_endpoints.py`
- `tests/api/test_supply_demand_graph_endpoints.py`
- `tests/quality/test_deployed_version_checker.py`

### Commands Run

- `python scripts/check-deployed-version.py --expected-commit bad60410999b4217bba26c5769b1fe0188bd3b9b --timeout 20` - controlled failure with `deployed_stale_or_unverified`; only blocker was Web HTML commit visibility.
- `python -m pytest tests/api/test_dev_server_graph_routes.py tests/api/test_stage_graph_endpoints.py tests/api/test_supply_demand_graph_endpoints.py tests/api/test_supply_demand_analytics_tables.py tests/quality/test_deployed_version_checker.py -q` - pass, 48 tests.
- `npm.cmd --workspace apps/web run typecheck` - pass.
- `npm.cmd --workspace apps/web run typecheck:packages` - pass.

### Computer Use Status

- Render Dashboard was opened with Browser/Computer Use and reached the Render sign-in page.
- A GitHub login attempt did not enter an authenticated Render dashboard and returned to the Render sign-in page.
- No credentials, cookies, tokens, OTPs, private account details, screenshots with secrets, raw payloads, private diagnostics, local filesystem paths, or PII were entered or copied.
- The failed Render login page was closed before continuing.
- GPT Pro project handoff was attempted next but blocked because the Browser runtime reported no active Codex browser pane.

### Known Limitations

- Deployment cannot be claimed verified until Web HTML exposes the latest commit marker and `scripts/check-deployed-version.py` returns `deployed_verified`.
- GPT Pro has not reviewed this local gate yet because Browser access to the project conversation failed after the Render login attempt.
- Live connectors remain disabled by default; stage coverage remains fixture/promoted-public-evidence with explicit proxy limitations.

## 2026-05-16 Deployment Version Readiness Patch

### Current HEAD

- Local HEAD before this patch: `fa26bb0b468ae058a3ce3e346a56536303463e36`.
- Preserved untracked local files:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`
- `data/runtime/` remains ignored runtime state and was not staged.

### Gate Result

- Render API and Web were manually redeployed from latest `main` using project-scoped Chrome Browser control.
- API service `supply-risk-atlas-api` started a Render build for `fa26bb0b468ae058a3ce3e346a56536303463e36`.
- Web service `supply-risk-atlas-web` started a Render build for `fa26bb0b468ae058a3ce3e346a56536303463e36`; build logs showed Next.js build success and health-check deployment in progress.
- Post-redeploy probes showed API, Web proxy, and Web HTML all reporting or exposing `fa26bb0b468ae058a3ce3e346a56536303463e36`.
- Remaining deployed warning was traced to `/api/v1/version` self-reporting `deployment_stale_or_unverified=true` solely because API runtime does not receive a Web build commit environment variable.
- Version readiness semantics were patched so API reports `api_commit_reported` when API commit is known and Web commit is not available to the API process; the external deployed checker still verifies API/Web/HTML cross-service commit consistency.

### Files Changed

- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`
- `services/api/services/version_service.py`
- `tests/api/test_version_endpoint.py`

### Commands Run

- `python -m pytest tests/api/test_version_endpoint.py tests/quality/test_deployed_version_checker.py -q` - pass, 18 tests.
- `python scripts/check-deployed-version.py --expected-commit fa26bb0b468ae058a3ce3e346a56536303463e36 --timeout 25` - controlled failure before this patch because API self-reported `deployment_stale_or_unverified`; external probes already matched latest API/Web commit.

### Computer Use Actions

- Used Chrome Browser extension only for project-scoped Render Dashboard actions.
- Triggered `Deploy latest commit` for `supply-risk-atlas-api`.
- Triggered `Deploy latest commit` for `supply-risk-atlas-web`.
- Captured public deployed-page screenshots for GPT Pro review packet:
  - `artifacts/gpt-pro-review/system-health.png`
  - `artifacts/gpt-pro-review/graph-explorer.png`
- Entity Risk screenshot capture timed out twice; failed project pages were closed before continuing to avoid tab buildup.
- No secrets, cookies, tokens, credentials, OTPs, private diagnostics, local filesystem paths, raw payloads, or PII were copied into logs.

### Known Limitations

- A new API redeploy is required after this patch is committed and pushed so `/api/v1/version` reports the updated readiness semantics.
- GPT Pro review packet is still pending after this patch commit and deployment verification.
- The platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.

## 2026-05-16 GPT Pro Review And Deployed Retry Hardening

### Current HEAD

- Local HEAD before this patch: `0d440fefa0872d55ecbe3619ef8e4e3754ce2ccb`.
- Preserved untracked local files:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`

### GPT Pro Review Result

- GPT Pro received the sanitized status packet in the project-scoped conversation.
- Review priority for the next gate:
  - do not claim deployment completion unless `/api/v1/version`, Web proxy, and Web HTML match the latest HEAD;
  - relationship views must keep authoritative rows at zero when backend endpoints are unavailable;
  - source coverage must keep fixture/promoted/unavailable/official support distinct;
  - exports and reports must not bypass frontend relationship safety by using local graph-derived fallback rows.

### Gate Result

- Deployed API/Web had been manually aligned to `fa26bb0b468ae058a3ce3e346a56536303463e36`.
- Latest pushed HEAD `0d440fefa0872d55ecbe3619ef8e4e3754ce2ccb` passed GitHub `ci` and `Quality Gates`, but Render UI automation repeatedly timed out before a latest-commit redeploy could be confirmed.
- Public deployed probes therefore remained `deployed_stale_or_unverified`.
- Direct endpoint probes later showed `/graph/supply-relationships` and `/stage-graph/L5_fabrication` returning HTTP 200 again, indicating the deployed 502s were transient Render cold-start/restart windows rather than permanent endpoint absence.
- Deployed smoke remained best-effort and continued to capture a controlled `unavailable_preview` state when relationship and stage endpoints returned transient 502 during page load.
- The API client and same-origin proxy read retry budgets were increased for idempotent GET/HEAD requests only. POST/write calls remain single-attempt and direct to avoid retrying non-idempotent actions.

### Files Changed

- `apps/web/src/app/api/v1/[...path]/route.ts`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`
- `packages/api-client/src/dashboard.ts`

### Commands Run

- `python scripts/check-deployed-version.py --expected-commit 0d440fefa0872d55ecbe3619ef8e4e3754ce2ccb --timeout 30` - controlled failure with `deployed_stale_or_unverified`; deployed API/Web still reported `fa26bb0b468ae058a3ce3e346a56536303463e36`.
- `npm.cmd run smoke:web -- --mode=deployed` - best-effort exit 0; captured transient 502 relationship/stage endpoint unavailable state with no authoritative relationship rows rendered.
- Direct deployed probes for `/api/v1/version`, `/api/v1/graph/supply-relationships?limit=5`, and `/api/v1/stage-graph/L5_fabrication?limit=18` later returned HTTP 200 against deployed `fa26bb0`.

### Known Limitations

- Latest HEAD after this patch must still be deployed and verified; no deployed success claim is made.
- Render UI automation remains unstable in Chrome for repeated latest-commit deployment actions.
- Entity Risk screenshot capture remains unavailable due browser timeout; public System Health and Graph Explorer screenshots were captured.

## 2026-05-17 Version Probe And API Warm-Up Hardening

### Current HEAD

- Local HEAD before this patch: `6bc50eed20050cdb920583a87a4471d8af221ec1`.
- Preserved untracked local files:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`

### Gate Result

- Current deployed state remains `deployed_stale_or_unverified`: API and Web still report `fa26bb0b468ae058a3ce3e346a56536303463e36` while local HEAD is newer.
- Direct public probes showed relationship and stage graph endpoints returning HTTP 200 after Render recovered:
  - `/api/v1/graph/supply-relationships?limit=5`
  - `/api/v1/graph/demand-relationships?limit=5`
  - `/api/v1/graph/production-dependencies?limit=5`
  - `/api/v1/graph/supply-demand-balance?limit=5`
  - `/api/v1/stage-graph/L5_fabrication?limit=18`
- `/api/v1/version` remained the slowest public endpoint during cold-start windows.
- `version_service` and System Health now reuse the service-level fixture snapshot cache instead of rebuilding the fixture graph directly.
- `scripts/check-deployed-version.py` now uses bounded per-probe retries and records attempt counts so transient Render timeouts do not become false `deployed_unavailable` claims.

### Files Changed

- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`
- `scripts/check-deployed-version.py`
- `services/api/services/system_health_service.py`
- `services/api/services/version_service.py`
- `tests/quality/test_deployed_version_checker.py`

### Commands Run

- `python -m pytest tests/api/test_version_endpoint.py tests/api/test_system_health_semiconductor_graph.py tests/api/test_system_health_storage_sources.py tests/quality/test_deployed_version_checker.py -q` - pass, 27 tests.
- `npm.cmd --workspace apps/web run typecheck` - pass.
- `python scripts/check-deployed-version.py --expected-commit 6bc50eed20050cdb920583a87a4471d8af221ec1 --timeout 20 --attempts 2` - controlled failure with `deployed_stale_or_unverified`; deployed API/Web still reported `fa26bb0b468ae058a3ce3e346a56536303463e36`.

### Known Limitations

- Latest local patch is not deployed yet.
- Deployment verification remains blocked on Render redeploy consistency, not on local tests.
- No production readiness, live authoritative data, or source usability claim is made.

## 2026-05-17 Deployment Stale Recovery Check

### Current HEAD

- Current HEAD: `2cac0b9742709b1a26d5263b66214c4b3e274e6e`.
- Preserved untracked local files:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`

### Gate Result

- GitHub `ci` passed for `2cac0b9`.
- GitHub `Quality Gates` passed for `2cac0b9`.
- Five bounded public deployment probes still reported `deployed_stale_or_unverified`.
- The public API and Web proxy continued reporting deployed commit `fa26bb0b468ae058a3ce3e346a56536303463e36`.
- The Web HTML did not expose the `2cac0b9` commit marker.
- Relationship and stage graph endpoints were reachable with HTTP 200 during direct checks, but they were still served by the stale deployed commit.
- `codex-continuation-request.md` was refreshed so the next handoff no longer points to `0d440fe` as latest.
- The deployed version checker now catches unexpected per-probe exceptions and returns a sanitized failed attempt record.

### Files Changed

- `docs/roadmap/codex-continuation-request.md`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`
- `scripts/check-deployed-version.py`
- `tests/quality/test_deployed_version_checker.py`

### Commands Run

- `python scripts/check-deployed-version.py --expected-commit 2cac0b9742709b1a26d5263b66214c4b3e274e6e --timeout 30 --attempts 3` - controlled failure with `deployed_stale_or_unverified`.
- Five repeated deployment probes over roughly four minutes - controlled failures with stale deployed commit `fa26bb0`.
- Direct public probes for supply, demand, production-dependency, balance, and L5 stage endpoints - HTTP 200 on stale deployed commit.

### Computer Use Actions

- Browser/Computer Use deployment actions were not repeated in this gate because prior Render Dashboard automation remained unstable and public probes confirmed the deployed services were stale.
- No credentials, cookies, tokens, OTPs, private diagnostics, raw payloads, private operational URLs, or PII were copied into repository files.

### Known Limitations

- Render API and Web still need a confirmed redeploy from latest `main`.
- Deployment verification cannot be marked complete until API version, Web proxy, and Web HTML all match the latest commit.
- The platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.

## 2026-05-17 Web HTML Commit Marker Fix

### Current HEAD

- Current HEAD before this patch: `f2854eaa3bb58d91550bff6748e1393cae67dbf8`.
- Preserved untracked local files:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`

### Gate Result

- Render API and Web runtime proxy were manually redeployed from latest `main`.
- Public deployed probes showed API and Web proxy both reporting `f2854eaa3bb58d91550bff6748e1393cae67dbf8`.
- Deployment verification still returned `deployed_stale_or_unverified` because Web static HTML did not expose a 12-character or full-length commit marker.
- Root cause: `data-web-build-commit` was emitted by the client `App` component after hydration, but `scripts/check-deployed-version.py` verifies static HTML before client hydration.
- The Web layout metadata now emits `supply-risk-web-commit` and `supply-risk-web-build-time` meta tags at build time so deployed static HTML can be verified externally.

### Files Changed

- `apps/web/src/app/layout.tsx`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`
- `tests/quality/test_web_commit_marker.py`

### Commands Run

- `python scripts/check-deployed-version.py --expected-commit f2854eaa3bb58d91550bff6748e1393cae67dbf8 --timeout 35 --attempts 3` - controlled failure with only `web_html_commit_not_visible`.
- Public HTML spot check - no `f2854ea`, 12-character commit prefix, or `supply-risk-web-commit` marker was present before this patch.

### Computer Use Actions

- Used authorized Chrome Browser control only for project-scoped Render Dashboard.
- Triggered `Deploy latest commit` for `supply-risk-atlas-api`.
- Navigated to `supply-risk-atlas-web`; the browser control session timed out while checking whether the Web deploy click completed, so deployment verification was determined by public probes instead of raw dashboard logs.
- No credentials, cookies, tokens, OTPs, private diagnostics, raw payloads, private operational URLs, or PII were copied into repository files.

### Known Limitations

- This patch must be committed, pushed, rebuilt by Render Web, and rechecked before deployment can be marked verified.
- API and Web runtime proxy were aligned at `f2854ea`, but Web static HTML verification remains pending until this patch is deployed.

## 2026-05-17 Render Web Commit Env Priority Fix

### Current HEAD

- Current HEAD before this patch: `c3f245d47f678053fc4aca44024a31498ea58d86`.

### Gate Result

- Render API reported latest commit `c3f245d47f678053fc4aca44024a31498ea58d86`.
- Web same-origin version proxy reported latest API commit `c3f245d47f678053fc4aca44024a31498ea58d86`.
- Web static HTML still rendered `data-web-build-commit="fa26bb0..."`.
- Root cause: `next.config.mjs` preferred `NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT` over `RENDER_GIT_COMMIT`, so a stale manually configured public env value could override Render's actual Git commit at build time.
- Fix: `next.config.mjs` now prioritizes `RENDER_GIT_COMMIT`, then `SUPPLY_RISK_GIT_COMMIT`, then the public override, then local `git rev-parse HEAD`.

### Files Changed

- `apps/web/next.config.mjs`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`
- `tests/quality/test_web_commit_marker.py`

### Commands Run

- Public deployed root HTML spot checks showed `fa26bb0` in `data-web-build-commit` despite API/Web proxy commit alignment at `c3f245d`.
- `python scripts/check-deployed-version.py --expected-commit c3f245d47f678053fc4aca44024a31498ea58d86 --timeout 35 --attempts 3` - controlled failure with only `web_html_commit_not_visible`.

### Known Limitations

- This env-priority patch still needs commit, push, GitHub Actions, Render rebuild, and deployed verification.
- No production readiness claim is made.

## 2026-05-17 Render Auto-Deploy Trigger For Web Marker

### Gate Result

- Browser control against Render Dashboard repeatedly timed out while trying to confirm a Web `Clear build cache & deploy` click.
- Public probes continued to show API at `c3f245d` while Web root HTML still rendered the old `fa26bb0` client build marker.
- `render.yaml` was updated with a comment-only deployment trigger because both Render services have `autoDeploy: true` and include `render.yaml` in their build filters.
- Expected effect: Render Git integration should rebuild both API and Web from latest `main` without changing runtime behavior or enabling live connector fetch.

### Files Changed

- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`
- `render.yaml`

### Known Limitations

- Deployment verification remains pending until public probes show API, Web proxy, and Web HTML all aligned to the trigger commit.
- No production readiness claim is made.

## 2026-05-17 Render Deployment Closure专项

### Current HEAD

- Current HEAD before this patch: `ed41ab3af0f6d578277f2bcaac7f24f0111abd0c`.
- GPT Pro review result: prioritize Render Web static HTML, deployment control, and version-consistency closure before further content/API/data-source expansion.
- Preserved untracked local files:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`

### Gate Result

- Public deployment probe still reported `deployed_stale_or_unverified` before this patch.
- API and Web same-origin proxy reported `c3f245d47f678053fc4aca44024a31498ea58d86`, not current `ed41ab3`.
- Web static HTML did not expose the current commit marker.
- Added a dynamic Web build metadata endpoint so deployed Web identity can be checked without relying only on root HTML.
- Added a manual-only GitHub Actions workflow for Render API/Web deploys using GitHub secrets and bounded public convergence checks.
- Added actionable Render secret requirements documentation for the blocked case.

### Files Changed

- `.github/workflows/render-manual-deploy.yml`
- `apps/web/src/app/api/build-info/route.ts`
- `docs/roadmap/render-deploy-secret-requirements.md`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`
- `scripts/check-deployed-version.py`
- `tests/quality/test_deployed_version_checker.py`
- `tests/quality/test_render_manual_deploy_workflow.py`
- `tests/quality/test_web_commit_marker.py`

### Commands Run

- `git status --short; git rev-parse HEAD` - only preserved untracked Web notes were present.
- `python scripts/check-deployed-version.py --expected-commit ed41ab3af0f6d578277f2bcaac7f24f0111abd0c --timeout 25 --attempts 2` - controlled failure with `deployed_stale_or_unverified`.
- `python -m pytest tests/quality/test_deployed_version_checker.py tests/quality/test_web_commit_marker.py tests/quality/test_render_manual_deploy_workflow.py -q` - passed after narrowing the raw-payload guard to allow the safety warning `no_raw_payload`.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.

### Computer Use Actions

- Used authorized Chrome Browser control only for the project-scoped ChatGPT project conversation.
- Sent a sanitized status report with commit SHAs, tests, deployment state, and limitations.
- GPT Pro replied that the next round must prioritize Render Web static HTML / deployment control / version consistency closure.
- No secrets, cookies, tokens, OTPs, private diagnostics, raw payloads, private operational URLs, screenshots with sensitive account data, or PII were copied into repository files or the GPT Pro message.

### Known Limitations

- Deployment cannot be marked aligned until the manual Render workflow runs successfully or Render Dashboard/API access safely triggers API and Web redeploys.
- If the required GitHub Actions secrets are absent, the actionable status is `render_deploy_blocked_missing_safe_deploy_path`.
- No content/API/data-source expansion was attempted in this gate by GPT Pro direction.
- No production readiness claim is made.

## 2026-05-17 Display Declutter And Audit Details Gate

### Current HEAD

- Work started from local HEAD `06c50120449525fac149be9a4de6536b7371cc16`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Reworked the global data lineage banner so the primary display shows only public coverage, update time, source summary, and a user-facing public evidence / research fixture status.
- Moved `data_mode`, `graph_mode`, `graph_version`, `source_manifest_id`, calibration metadata, warning details, and endpoint diagnostics into collapsed audit/detail sections.
- Reworked common chart/table metadata rendering to use compact status badges plus collapsed audit details instead of raw metadata rows.
- Reworked Graph Explorer relationship views and endpoint diagnostics so unavailable relationship data is described as non-authoritative, with technical diagnostics folded away.
- Cleaned Entity Risk, Shock Simulator, Reverse Stress, Optimizer, Investigation Report, Evidence Board, and System Health surfaces so primary panels emphasize business conclusions, evidence, and controlled status summaries.
- API response fields, exports, and report metadata requirements were not changed.

### Files Changed

- `apps/web/src/app/App.tsx`
- `apps/web/src/app/globals.css`
- `apps/web/src/app/pages.tsx`
- `apps/web/src/features/common/AuditDetails.tsx`
- `apps/web/src/features/common/charts/ChartPrimitives.tsx`
- `apps/web/src/features/common/data-cards/GraphVersionBadge.tsx`
- `apps/web/src/features/common/data-cards/NotProductionReadyBanner.tsx`
- `apps/web/src/features/common/data-cards/SourceManifestBadge.tsx`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `apps/web/src/features/common/pageRelevance.ts`
- `apps/web/src/features/common/tables/DataTable.tsx`
- `apps/web/src/features/graph-explorer/DemandRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/GraphExplorer.tsx`
- `apps/web/src/features/graph-explorer/GraphLegend.tsx`
- `apps/web/src/features/graph-explorer/GraphOverviewView.tsx`
- `apps/web/src/features/graph-explorer/ProductionDependencyView.tsx`
- `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx`
- `apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`

### Commands Run

- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `npm.cmd run smoke:web` - passed with 63 checks.

### Display And Terminology Evidence

- Primary display no longer renders raw `data_mode:`, `graph_version:`, `source_manifest_id:`, `transport_attempts:`, `failed_endpoint:`, or `not_production_ready: true` chips.
- Main pages now show user-facing labels such as `Public evidence mode` and `Research fixture mode`.
- Audit metadata remains available in collapsed `Data audit details` / `Technical diagnostics` sections.
- Geography normalization remains unchanged; user-facing regional labels continue to use `region:china_taiwan` / `中国台湾`.

### Deployment Status

- No deployment action was attempted in this display-only gate.
- Render deployment consistency remains blocked by the previously recorded safe-deploy access issue.
- No production readiness claim is made.

## 2026-05-17 Render Manual Workflow Validation Fix

### Current HEAD

- Latest pushed commit after workflow syntax fix: `9841a37f228015c808f8fada715fad698b95de55`.

### Gate Result

- Initial manual Render workflow commits produced GitHub workflow validation failures because a bash heredoc inside YAML was not indented as valid YAML.
- The workflow now uses a validated one-line JSON payload for the Render API request.
- GitHub `ci` passed for `9841a37f228015c808f8fada715fad698b95de55`.
- GitHub `Quality Gates` passed for `9841a37f228015c808f8fada715fad698b95de55`.
- The Render workflow is active and no longer produces a new invalid-workflow push failure on latest HEAD.

### Files Changed

- `.github/workflows/render-manual-deploy.yml`
- `docs/roadmap/codex-continuation-request.md`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`
- `tests/quality/test_render_manual_deploy_workflow.py`

### Commands Run

- Local YAML parse check for `.github/workflows/render-manual-deploy.yml` - passed.
- `python -m pytest tests/quality/test_render_manual_deploy_workflow.py -q` - passed.
- `python -m pytest tests/quality/test_render_manual_deploy_workflow.py tests/quality/test_deployed_version_checker.py tests/quality/test_web_commit_marker.py -q` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python scripts/check-deployed-version.py --expected-commit 9841a37f228015c808f8fada715fad698b95de55 --timeout 10 --attempts 1` - controlled failure with `deployed_stale_or_unverified`.

### Deployment Status

- Public API and Web same-origin proxy still report `c3f245d47f678053fc4aca44024a31498ea58d86`.
- Web root HTML still does not expose the latest commit marker.
- Web `/api/build-info` is unavailable on the deployed site because the currently deployed Web build predates that route.
- Local shell has no Render or GitHub token environment variables available.
- GitHub UI displayed the manual workflow as active, but the `Run workflow` panel returned a page loading error in Browser automation. The failed page was closed before continuing.
- Current actionable status: `render_deploy_blocked_missing_safe_deploy_path_or_reliable_dispatch`.

### Computer Use Actions

- Used authorized Chrome Browser control only for project-scoped GitHub Actions.
- Closed the failed GitHub workflow page after the loading error, per the user's browser-stability instruction.
- Attempted to send a sanitized status packet to the project-scoped GPT Pro conversation after this gate.
- ChatGPT browser control timed out while filling/sending and again while checking send status, so this handoff is recorded as attempted but unconfirmed.
- No credentials, cookies, tokens, OTPs, private diagnostics, raw payloads, private operational URLs, screenshots with sensitive account data, or PII were copied into repository files.

### Known Limitations

- Deployment remains unverified until the manual workflow is dispatched with configured secrets or Render Dashboard/API deploy succeeds.
- GPT Pro review for the final `57832e6` status is not confirmed because ChatGPT browser automation timed out.
- No content/API/data-source expansion was attempted in this gate by GPT Pro direction.
- No production readiness claim is made.

## 2026-05-29 Display Declutter Push, CI, And Deploy Preflight

### Current HEAD

- Latest pushed commit: `c78f32c62c85f965d71e35d6e72dfc8daec72cc0`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Pushed the display-declutter commit to `origin/main` after the first ordinary push failed due to GitHub network timeout.
- GitHub `ci` passed for `c78f32c62c85f965d71e35d6e72dfc8daec72cc0`.
- GitHub `Quality Gates` passed for `c78f32c62c85f965d71e35d6e72dfc8daec72cc0`.
- Deployed public version probe still reports stale services at `06c50120449525fac149be9a4de6536b7371cc16`.
- Triggered GitHub Actions run `26643255838` for `Render Manual Deploy` with `commit_sha=c78f32c62c85f965d71e35d6e72dfc8daec72cc0` and `clear_cache=clear`.
- Render deploy was not triggered because the workflow failed preflight on missing GitHub Actions secrets: `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID`.

### Commands Run

- `git push origin main` - first attempt failed with GitHub 443 network timeout.
- Elevated `git push origin main` - passed; `c78f32c` pushed to `origin/main`.
- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_deployed_api_transport_fallback.py tests/quality/test_relationship_view_no_authoritative_fallbacks.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `gh run list --repo xiaoming2cf-afk/supply-risk-atlas --limit 10 --json ...` - latest `ci` and `Quality Gates` discovered.
- `python scripts/check-deployed-version.py --expected-commit c78f32c62c85f965d71e35d6e72dfc8daec72cc0 --timeout 25 --attempts 2` - controlled failure with `deployed_stale_or_unverified`.
- `gh workflow run render-manual-deploy.yml --repo xiaoming2cf-afk/supply-risk-atlas --ref main -f commit_sha=c78f32c62c85f965d71e35d6e72dfc8daec72cc0 -f clear_cache=clear` - dispatched run `26643255838`.
- `gh run view 26643255838 --repo xiaoming2cf-afk/supply-risk-atlas --json status,conclusion,headSha,url,jobs` - failed in preflight.
- `gh run view 26643255838 --repo xiaoming2cf-afk/supply-risk-atlas --log-failed` - confirmed missing-secret names only.

### Deployment Status

- Public API commit: `06c50120449525fac149be9a4de6536b7371cc16`.
- Web `/api/build-info` commit: `06c50120449525fac149be9a4de6536b7371cc16`.
- Web proxy commit: `06c50120449525fac149be9a4de6536b7371cc16`.
- Web root HTML latest commit marker: not visible.
- Current actionable status: `render_deploy_blocked_missing_github_actions_secrets`.

### Computer Use Actions

- No browser/Chrome Computer Use was used in this gate.
- GitHub Actions inspection and workflow dispatch were done through `gh` CLI with sanitized output.
- No secrets, cookies, tokens, OTPs, raw payloads, private diagnostics, account screenshots, or PII were exposed.

### Known Limitations

- Render deployment cannot proceed until `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are configured as GitHub Actions secrets.
- GPT Pro handoff was not retried in this gate because deployment remains safely blocked before Render can deploy latest `main`.
- No production readiness claim is made.

## 2026-05-29 Deployment Handoff Commit And Chrome Retry

### Current HEAD

- Latest pushed commit: `fa4ba1ed05ea9d0ac33fc98eccc30268c97bdbf1`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Committed and pushed the docs-only recovery handoff as `fa4ba1ed05ea9d0ac33fc98eccc30268c97bdbf1`.
- GitHub `ci` passed for `fa4ba1ed05ea9d0ac33fc98eccc30268c97bdbf1`.
- GitHub `Quality Gates` passed for `fa4ba1ed05ea9d0ac33fc98eccc30268c97bdbf1`.
- Public deployed version probe for `fa4ba1ed05ea9d0ac33fc98eccc30268c97bdbf1` still reports stale API/Web commit `06c50120449525fac149be9a4de6536b7371cc16`.
- Render Manual Deploy remains blocked because GitHub Actions secrets `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured.

### Commands Run

- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py tests/quality/test_frontend_display_declutter.py -q` - passed.
- `git diff --check` - passed.
- `git commit -m "Record Render deploy preflight blocker"` - created `fa4ba1ed05ea9d0ac33fc98eccc30268c97bdbf1`.
- `git push origin main` - passed.
- `gh run list --repo xiaoming2cf-afk/supply-risk-atlas --limit 6 --json ...` - confirmed `ci` and `Quality Gates` success for `fa4ba1ed05ea9d0ac33fc98eccc30268c97bdbf1`.
- `python scripts/check-deployed-version.py --expected-commit fa4ba1ed05ea9d0ac33fc98eccc30268c97bdbf1 --timeout 25 --attempts 2` - controlled stale deployment result.

### Computer Use Actions

- Connected to the authenticated Chrome profile through the Codex Chrome Extension.
- Opened Render Dashboard for project-scoped deployment verification.
- Browser control timed out while inspecting the Render Dashboard page.
- Opened a fresh Chrome window with user authorization and retried the Render Dashboard.
- The fresh Render Dashboard page also timed out through the extension.
- Attempted to close the stale Render tab after the first failure, but claiming that tab also timed out. To avoid an unbounded loop or browser overload, no further Render UI retries were attempted.
- No credentials, cookies, tokens, OTPs, account screenshots, private diagnostics, raw payloads, or PII were copied or stored.

### Deployment Status

- Current actionable status: `render_deploy_blocked_missing_github_actions_secrets_and_chrome_extension_timeout`.
- Required safe path: configure Render deployment GitHub Actions secrets or complete Render redeploy manually in the browser, then rerun deployed version and smoke checks.

### Known Limitations

- Deployed API/Web remain stale at commit `06c50120449525fac149be9a4de6536b7371cc16`.
- GPT Pro handoff was not retried because deployment is still blocked and no sanitized deployed screenshots can be produced from the timed-out Chrome session.
- No production readiness claim is made.

## 2026-05-29 Audit Metadata DOM Hiding And CI Recovery

### Current HEAD

- Latest implementation commit: `1e506a8da2e110d214d5b37ead43988d34de9481`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Fixed the CI browser-smoke regression introduced by display decluttering.
- `AuditDetails` now renders audit rows only after the user expands the details section, so ordinary page text no longer includes raw technical metadata such as `data_mode`, `graph_version`, `source_manifest_id`, `transport_attempts`, or warning bodies.
- Marked `AuditDetails` as a client component because it now uses state for controlled expansion.
- Added `allowedDevOrigins` for local Next dev smoke origins `127.0.0.1` and `localhost`; this preserves local/CI browser-smoke while not changing production API behavior.
- GitHub `ci` passed for `1e506a8da2e110d214d5b37ead43988d34de9481`.
- GitHub `Quality Gates` passed for `1e506a8da2e110d214d5b37ead43988d34de9481`.

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_no_forbidden_geography_labels.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api -q` - passed.
- `python -m pytest tests/security tests/graph_invariants -q` - passed.
- `npm.cmd run smoke:web` - passed with 63 checks after restarting the local dev server.
- `gh run list --repo xiaoming2cf-afk/supply-risk-atlas --limit 6 --json ...` - confirmed `ci` and `Quality Gates` success for `1e506a8da2e110d214d5b37ead43988d34de9481`.
- `python scripts/check-deployed-version.py --expected-commit 1e506a8da2e110d214d5b37ead43988d34de9481 --timeout 25 --attempts 2` - controlled stale deployment result.
- `gh workflow run render-manual-deploy.yml --repo xiaoming2cf-afk/supply-risk-atlas --ref main -f commit_sha=1e506a8da2e110d214d5b37ead43988d34de9481 -f clear_cache=clear` - dispatched run `26646684760`.
- `gh run view 26646684760 --repo xiaoming2cf-afk/supply-risk-atlas --json status,conclusion,headSha,url,jobs` - failed at preflight before triggering Render.
- `gh run view 26646684760 --repo xiaoming2cf-afk/supply-risk-atlas --log-failed` - confirmed missing secret names only.

### Deployment Status

- Public API commit: `06c50120449525fac149be9a4de6536b7371cc16`.
- Web `/api/build-info` commit: `06c50120449525fac149be9a4de6536b7371cc16`.
- Web proxy commit: `06c50120449525fac149be9a4de6536b7371cc16`.
- Render Manual Deploy run `26646684760` failed preflight because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured as GitHub Actions secrets.
- Render deploy was not triggered.

### Computer Use Actions

- No additional Render Chrome actions were attempted in this gate because the prior authenticated Render Dashboard tab and fresh retry both timed out through the Chrome extension.
- No credentials, cookies, tokens, OTPs, account screenshots, private diagnostics, raw payloads, or PII were copied or stored.

### Known Limitations

- Deployed API/Web remain stale at commit `06c50120449525fac149be9a4de6536b7371cc16`.
- GPT Pro handoff is still pending a stable browser path or a user-provided review message path; no production readiness claim is made.

## 2026-05-29 GPT Pro Handoff Attempt After CI Recovery

### Current HEAD

- Latest pushed commit before this handoff attempt: `8124f03a38ae68851e873d82b44bb81bdaf69439`.
- GitHub `ci` passed for `8124f03a38ae68851e873d82b44bb81bdaf69439`.
- GitHub `Quality Gates` passed for `8124f03a38ae68851e873d82b44bb81bdaf69439`.

### Computer Use Actions

- Attempted to open the project-scoped GPT Pro project URL provided by the user.
- The ChatGPT project page timed out through the Codex Chrome Extension before a status message could be pasted.
- Attempted to close the failed project tab according to the user's failed-page cleanup rule.
- Closing the failed tab also timed out through the extension, so no further browser loop was attempted.
- No unrelated tabs were inspected beyond the project-scoped tab list needed for cleanup.
- No secrets, cookies, tokens, OTPs, private diagnostics, account screenshots, raw payloads, or PII were copied or stored.

### Sanitized Handoff Summary That Could Not Be Sent

- Latest implementation commit: `1e506a8da2e110d214d5b37ead43988d34de9481`.
- Latest pushed log commit: `8124f03a38ae68851e873d82b44bb81bdaf69439`.
- Page display declutter is implemented: audit metadata stays behind closed details until expanded.
- CI and Quality Gates passed after the fix.
- Local validation passed: quality, API, security, graph invariant, typecheck, build, and browser smoke.
- Render deployment is still blocked because Render GitHub Actions secrets are missing and Render Dashboard automation times out through Chrome extension.
- Request for GPT Pro: `请审查当前 Codex 完成结果，并给出下一轮 prompt。`

### Known Limitations

- GPT Pro review was not completed because the browser control path timed out.
- Render deployed API/Web remain stale at commit `06c50120449525fac149be9a4de6536b7371cc16`.

## 2026-05-29 Run Page Unavailable-State Declutter

### Current HEAD

- Starting HEAD: `a949a1312269c66b96284742e0a74140a3eb4de7`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Tightened the display declutter policy for unavailable run pages.
- Shock Simulator, Reverse Stress Lab, Intervention Optimizer, and Investigation Report no longer show `failed_endpoint` or `source_status` as primary page fields.
- Each unavailable panel now shows a user-facing status summary and keeps endpoint/source diagnostics in collapsed `View diagnostics` audit details.
- Added a quality test to prevent those endpoint diagnostics from returning to primary page `Field` rows.

### Commands Run

- `git status --short --branch` - confirmed only preserved untracked user files before edits.
- `gh run list --repo xiaoming2cf-afk/supply-risk-atlas --limit 8 --json ...` - confirmed `ci` and `Quality Gates` success for `a949a1312269c66b96284742e0a74140a3eb4de7`.
- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` - passed.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd run smoke:web` - first run failed with `ECONNREFUSED 127.0.0.1:3000` because local Web/API servers were not running.
- Started local API and Web dev servers on `127.0.0.1:8000` and `127.0.0.1:3000`.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000 npm.cmd run smoke:web` - passed with 63 checks.
- Stopped the local API and Web dev servers after smoke validation.
- `python scripts/check-deployed-version.py --expected-commit a949a1312269c66b96284742e0a74140a3eb4de7 --timeout 10 --attempts 1` - controlled deployed-unavailable result in this environment.

### Computer Use Actions

- Reconnected to Chrome through the Codex Chrome Extension after one retry.
- Listed open tabs and identified the project-scoped Render Dashboard tab without inspecting unrelated tab contents.
- Attempted to claim and read the Render Dashboard tab for deployment verification.
- The Render tab timed out through the Chrome Extension.
- Attempted to close the failed Render tab according to the failed-page cleanup rule.
- Closing the failed tab also timed out, so no additional Render UI loop was attempted.
- No credentials, cookies, tokens, OTPs, account screenshots, private diagnostics, raw payloads, or PII were copied or stored.

### Deployment Status

- GitHub `ci` and `Quality Gates` are green for the latest pushed commit before this gate.
- Render deployment remains blocked by unavailable non-interactive credentials and Chrome Extension timeouts.
- Local environment has no `RENDER_API_KEY`, no Render CLI, and no visible repository Render secrets from `gh secret list`.
- Deployed version probe currently reports `deployed_unavailable` in this environment.

### Known Limitations

- This gate improves local UI behavior only; it does not claim the deployed Render services were updated.
- GPT Pro handoff was not retried after the Render timeout because Chrome control remained unstable.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Post-Push Evidence

- Implementation commit: `4b6150f8b2c8425aa56861890707b20c61e2fb05`.
- GitHub `ci` run `26649529530`: passed.
- GitHub `Quality Gates` run `26649529014`: passed.
- Render Manual Deploy run `26649777624`: failed preflight before contacting Render because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured.
- Updated `docs/roadmap/codex-continuation-request.md` with the latest safe deployment handoff state and required next action.

## 2026-05-29 Primary Display Label Hardening

### Current HEAD

- Starting HEAD: `e50db696f5d9503951a8af45fbfeb99777405dd3`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Added a shared frontend display-label layer so table headers, metric labels, report fields, chart labels, and run labels use user-facing terminology instead of raw snake_case or internal enum strings.
- Kept graph/source/data-mode metadata available through props, exports, and collapsed audit details; it is not removed from API/report structures.
- Collapsed the Investigation Report JSON export payload behind audit disclosure so the report page no longer defaults to a large technical payload block.
- Updated smoke expectations to validate user-facing labels while still checking that raw payloads, private diagnostics, and developer diagnostics are not shown in primary page text.
- Fixed the browser smoke hash-navigation helper and successful-exit path after a run produced a passing report but left the Node process open.

### Files Changed

- `apps/web/src/features/common/displayLabels.ts`
- `apps/web/src/app/components.tsx`
- `apps/web/src/features/common/tables/DataTable.tsx`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_no_forbidden_geography_labels.py -q` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://localhost:3000/ npm.cmd run smoke:web` - passed with 63 checks; report written to `artifacts/browser-smoke/report.json`.
- `npm.cmd --workspace apps/web run build` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `python -m pytest -q` - passed.

### Deployment Status

- No Render deployment is claimed for this gate.
- Render redeploy remains blocked by the previously recorded missing GitHub Actions secrets / unavailable safe Render credential path.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Known Limitations

- This gate improves local presentation quality and smoke reliability; it does not update the stale deployed Render services.
- GPT Pro handoff still requires a stable project-scoped browser/Chrome path.

### Post-Push Evidence

- Implementation commit: `4a10e48766c3aa30eaa3155b7ec0de125ba2c5a6`.
- GitHub `ci` run `26652907513`: passed.
- GitHub `Quality Gates` run `26652907468`: passed.
- Deployed version probe for expected commit `4a10e48766c3aa30eaa3155b7ec0de125ba2c5a6`: `deployed_unavailable`.
- Render Manual Deploy run `26653298557`: failed preflight before contacting Render because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured as GitHub Actions secrets.

## 2026-05-29 System Health Detail Folding And Local API Stability

### Current HEAD

- Starting HEAD: `9ff222c8ba633f9cf016fcbc83f6556804265921`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Continued the demo-first display cleanup on System Health.
- Kept readiness, source coverage, graph quality, connector/source status, and fixture/public-evidence badges visible.
- Moved heavy source registry rows, graph node/edge type counts, data catalog inventories, entity-resolution breakdowns, evidence-lineage records, and runtime log lines behind explicit audit/detail disclosures.
- Renamed default source/connector table titles from implementation-style `SourceCatalog` / `ConnectorStatus` to user-facing `Source catalog` / `Connector status`.
- Local browser reads now prefer the same-origin `/api/v1` proxy on `localhost` / `127.0.0.1`, avoiding direct-origin CORS retry delays during local smoke.
- Increased the bounded Next proxy upstream timeout from 15 seconds to 30 seconds; POST/write requests still use one upstream attempt and are not retried through the proxy.
- Fixed the smoke hash navigation helper so same-document hash routes are explicitly verified without blocking on `Page.navigate` hash behavior.

### Files Changed

- `apps/web/src/app/App.tsx`
- `apps/web/src/app/api/v1/[...path]/route.ts`
- `apps/web/src/app/components.tsx`
- `apps/web/src/features/common/displayLabels.ts`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `apps/web/src/features/common/tables/ConnectorStatusTable.tsx`
- `apps/web/src/features/common/tables/SourceCatalogTable.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`

### Commands Run

- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_no_forbidden_geography_labels.py -q` - passed.
- Started local API on `127.0.0.1:8000` and local Web on `localhost:3000`.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://localhost:3000/ npm.cmd run smoke:web` - passed with 63 checks.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest -q` - passed.
- Stopped local API/Web dev servers after validation.

### Deployment Status

- No Render deployment is claimed for this gate.
- Render remains blocked by the previously recorded missing GitHub Actions secrets / unavailable safe Render credential path.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Known Limitations

- This gate improves local page clarity and local API/proxy stability; deployed Render services still require the safe deployment path to be restored.
- GPT Pro handoff still requires a stable project-scoped browser/Chrome path.

### Post-Push Evidence

- Implementation commit: `e6318430700d14f57dbcf7b7c8073922c834eb48`.
- GitHub `ci` run `26670601896`: passed.
- GitHub `Quality Gates` run `26670601897`: passed.
- Deployed version probe for expected commit `e631843`: `deployed_unavailable`.
- Render Manual Deploy run `26670744158`: failed preflight before contacting Render because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured as GitHub Actions secrets.

## 2026-05-29 System Health Folding Evidence And Deployment Handoff

### Current HEAD

- Starting HEAD: `e6318430700d14f57dbcf7b7c8073922c834eb48`.
- Evidence/docs commit: `63c931d79a8a21baed33e95d8c234d97a3557aa2`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Recorded the local System Health folding work, local validation evidence, GitHub CI evidence, and the deployment blocker state in the continuation handoff.
- Rechecked the public deployed version after the docs commit. Public API/Web still report stale commit `06c50120449525fac149be9a4de6536b7371cc16`, not latest `main`.
- Retried project-scoped Render Dashboard verification through the authorized Chrome path. The Render Dashboard page timed out and the failed page was closed.
- Retried the project-scoped GPT Pro handoff through Chrome. The project page timed out through the extension; a cleanup attempt to close the failed tab also timed out, so no further browser loop was attempted to avoid accumulating pages.

### Commands Run

- `git rev-parse HEAD` - confirmed `63c931d79a8a21baed33e95d8c234d97a3557aa2`.
- `git status --short` - only user-owned untracked files were present.
- `gh run list --repo xiaoming2cf-afk/supply-risk-atlas --branch main --limit 10 --json ...` - confirmed latest CI/Quality Gates status.
- `python scripts/check-deployed-version.py --expected-commit 63c931d --timeout 20` - failed with `deployed_stale_or_unverified`; deployed API/Web still reported stale commit `06c50120449525fac149be9a4de6536b7371cc16`.

### Post-Push Evidence

- Docs/evidence commit: `63c931d79a8a21baed33e95d8c234d97a3557aa2`.
- GitHub `ci` run `26670773172`: passed.
- GitHub `Quality Gates` run `26670773161`: passed.
- Render Manual Deploy run `26670744158`: failed before contacting Render because required GitHub Actions secrets are absent.

### Computer Use Actions

- Used only project-scoped Chrome pages for Render and GPT Pro handoff attempts.
- Render Dashboard attempt result: `render_tab_failed_closed`.
- GPT Pro project attempt result: extension timeout; cleanup attempt also timed out.
- No Render credentials, tokens, cookies, private diagnostics, local filesystem paths, raw payloads, or PII were copied into logs or external prompts.

### Deployment Status

- Current status: `render_deploy_blocked_missing_github_actions_secrets_and_chrome_extension_timeout`.
- No Render deployment is claimed for this gate.
- Latest local/GitHub commit is verified, but deployed API/Web are stale or unverified.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Known Limitations

- Render redeploy still requires either the documented GitHub Actions secrets or a reliable authenticated Render Dashboard session.
- GPT Pro handoff remains pending because the project page timed out through Chrome automation.

## 2026-05-29 User-Facing Table Title Declutter

### Current HEAD

- Starting HEAD: `e28fe20feb94642bddc1011ea0cddde0d2355dc1`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Continued the demo-first display cleanup after a page audit found table titles such as `SupplyRelationship`, `ProductDemand`, `GraphNode`, and `ScenarioRun` still visible through default table component titles.
- Updated table defaults to user-facing labels such as `Supply relationships`, `Product demand`, `Graph nodes`, `Scenario runs`, `Recommended actions`, and `Validation artifacts`.
- Updated the shared display-label formatter to split PascalCase/camelCase fallback labels, while preserving existing acronym and explicit label overrides.
- Updated `DataTable` to format titles through the display-label layer and avoid rendering nested object values as raw JSON in table cells. Nested structured values now render as `Structured metadata`.
- Updated browser smoke expectations to use the new user-facing table titles.

### Files Changed

- `apps/web/src/features/common/displayLabels.ts`
- `apps/web/src/features/common/tables/DataTable.tsx`
- `apps/web/src/features/common/tables/*Table.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- Started local API on `127.0.0.1:8000` and local Web on `localhost:3000`.
- First `npm.cmd run smoke:web` attempt failed because the smoke script still expected the old implementation label `ScenarioRun`.
- Updated smoke expectations to `Scenario runs` and `Recommended actions`.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://localhost:3000/ npm.cmd run smoke:web` - passed.

### Deployment Status

- No Render deployment is claimed for this gate.
- Public deployed API/Web remain stale or unverified until the documented Render deployment path is restored.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Post-Push Evidence

- Implementation commit: `cce30c21749101f439ae51c59fa9050ddf81a0f1`.
- GitHub `ci` run `26671602820`: passed.
- GitHub `Quality Gates` run `26671602832`: passed.
- Deployed version probe for expected commit `cce30c2`: `deployed_stale_or_unverified`.
- Public Web build metadata and Web proxy still reported stale commit `06c50120449525fac149be9a4de6536b7371cc16`; API probe was unavailable during this check.

### Known Limitations

- This gate improves local UI clarity only; it does not resolve the Render credential/Chrome extension deployment blocker.
- GPT Pro handoff remains pending a stable project-scoped Chrome path.

## 2026-05-29 Stage Graph Metadata Folding And Evidence Cell Cleanup

### Current HEAD

- Starting HEAD: `11285efb01871f92f5d8557c1aca153729673f88`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Removed primary-page `graph_version`, `source_manifest_id`, `data_mode`, and `graph_mode` metric rows from stage-specific Graph Explorer views.
- Stage graph views now show user-facing stage labels such as `L0 Policy / macro`, with implementation component names retained only inside collapsed audit details.
- Relationship class labels now render as user-facing strings such as `Supply relationships` and `Production dependencies`.
- Source-family status labels are formatted for display, including `fixture_promoted_public_evidence` -> `Fixture/promoted public evidence`.
- `DataTable` now renders arrays of evidence/source objects as bounded evidence summaries instead of `[object Object]`.
- Browser smoke stage-view checks now assert user-facing stage labels instead of implementation component names.

### Files Changed

- `apps/web/src/features/common/displayLabels.ts`
- `apps/web/src/features/common/tables/DataTable.tsx`
- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://localhost:3000/ npm.cmd run smoke:web` - passed with 63 checks.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run build` - passed.

### Deployment Status

- No Render deployment is claimed for this gate.
- Public deployed API/Web remain stale or unverified until the documented Render deployment path is restored.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Known Limitations

- This gate improves local Graph Explorer and table display quality only; it does not resolve the Render credential/Chrome extension deployment blocker.
- GPT Pro handoff remains pending a stable project-scoped Chrome path.

## 2026-05-29 Graph Legend Warning Declutter

### Current HEAD

- Starting HEAD: `d3e10d6fba82a494ccfd43a99f4cb1bdd71b0cea`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Graph Explorer legend no longer renders raw metadata warnings such as `semirisk_fixture_metadata: graphVersion=...; sourceManifestId=...` in the primary visible warning list.
- Detailed warning strings remain available through collapsed `Data audit details`.
- Primary warning rows are now deduplicated user-facing labels: `Research fixture mode`, `Fixture graph metadata available`, `Some fixture source freshness is limited`, or a generic public evidence warning.
- Added a quality guard to prevent `GraphLegend` from directly mapping raw metadata warnings back into primary page text.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphLegend.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://localhost:3000/ npm.cmd run smoke:web` - passed with 63 checks.
- `Select-String -Path artifacts/browser-smoke/report.json -Pattern 'semirisk_fixture_metadata|graphVersion=|sourceManifestId=|\[object Object\]'` - no matches.

### Deployment Status

- No Render deployment is claimed for this gate.
- Public deployed API/Web remain stale or unverified until the documented Render deployment path is restored.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Known Limitations

- This gate improves local Graph Explorer warning readability only; it does not resolve the Render credential/Chrome extension deployment blocker.
- GPT Pro handoff remains pending a stable project-scoped Chrome path.

## 2026-05-29 Scenario Option Label Declutter

### Current HEAD

- Starting HEAD: `91428abcfdc4dde2f4c8a9abfbfe4387ba8b561b`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Shock Simulator no longer exposes legacy implementation wording in the visible loss/propagation option labels.
- `Affected mean legacy` now renders as `Affected mean`.
- `Max legacy` now renders as `Maximum propagation`.
- Added a frontend display quality guard so the legacy labels cannot return to primary user-facing page copy.
- Browser smoke report was checked for old legacy labels and previously cleaned raw metadata/diagnostic strings.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed after rerun with a longer timeout; the first run reached 100% output but was cut off by the command timeout.
- `npm.cmd --workspace apps/web run build` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://localhost:3000/ npm.cmd run smoke:web` - passed with 63 checks.
- `Select-String -Path artifacts/browser-smoke/report.json -Pattern 'Affected mean legacy|Max legacy|semirisk_fixture_metadata|graphVersion=|sourceManifestId=|\[object Object\]|transport_attempts:|failed_endpoint:'` - no matches.

### Deployment Status

- No Render deployment is claimed for this gate.
- Public deployed API/Web remain stale or unverified until the documented Render deployment path is restored.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Known Limitations

- This gate only removes two remaining user-visible legacy labels from the local Shock Simulator UI.
- Local Next dev startup still emitted a non-blocking cache persistence permission warning; smoke passed and no product behavior regression was observed.
- GPT Pro handoff and Render redeploy remain pending a stable project-scoped Chrome/Render path.

## 2026-05-29 Deployment Attempt After Scenario Label Declutter

### Current HEAD

- Latest pushed HEAD: `313c9ba627e77d0ebf739affa55b4894770be227`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- GitHub `ci` passed for `313c9ba627e77d0ebf739affa55b4894770be227` in run `26673063065`.
- GitHub `Quality Gates` passed for `313c9ba627e77d0ebf739affa55b4894770be227` in run `26673063056`.
- Deployed version probe still reports stale or unverified public deployment state.
- GitHub Render Manual Deploy was triggered for the latest commit with cache clear in run `26673268538`.
- Render Manual Deploy failed before contacting Render because repository secrets are not configured.
- Chrome/Computer Use handoff remains blocked by extension timeouts on project-scoped Render Dashboard pages.

### Commands Run

- `gh run list --repo xiaoming2cf-afk/supply-risk-atlas --branch main --limit 4` - latest `ci` and `Quality Gates` passed.
- `python scripts/check-deployed-version.py --expected-commit 313c9ba --timeout 30` - returned `deployed_stale_or_unverified`.
- `gh workflow run render-manual-deploy.yml --repo xiaoming2cf-afk/supply-risk-atlas --ref main -f commit_sha=313c9ba627e77d0ebf739affa55b4894770be227 -f clear_cache=clear` - dispatched run `26673268538`.
- `gh run view 26673268538 --repo xiaoming2cf-afk/supply-risk-atlas --log-failed` - preflight reported missing Render deployment secrets.

### Deployment Status

- Current status: `blocked_missing_render_github_actions_secrets_and_chrome_extension_timeout`.
- Public API/Web still report old commit `06c50120449525fac149be9a4de6536b7371cc16` through version probes.
- Required GitHub Actions secrets are missing: `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, `RENDER_WEB_SERVICE_ID`.
- No Render credentials, token values, cookies, private diagnostics, or raw payloads were exposed or stored.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Computer Use Actions

- Chrome extension connection succeeded once for project-scoped tab discovery.
- Opening Render Dashboard in Chrome timed out.
- Attempting to close project-scoped Render Dashboard tabs through the extension also timed out.
- No unrelated tabs were inspected.
- GPT Pro handoff was not completed because Chrome control was unstable.

### Next-Step Request

- Configure the missing Render GitHub Actions secrets or complete Render redeploy manually in the Dashboard.
- Then verify `313c9ba627e77d0ebf739affa55b4894770be227` with `python scripts/check-deployed-version.py --expected-commit 313c9ba627e77d0ebf739affa55b4894770be227 --timeout 25 --attempts 3` and `npm.cmd run smoke:web -- --mode=deployed`.
- After deployment aligns, send GPT Pro only a sanitized project status and screenshots from project pages.

## 2026-05-30 Propagation Option Label Declutter

### Current HEAD

- Starting HEAD: `458f0070393e17f3e1dbbb2920195789b40c0aa3`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Shock Simulator and Reverse Stress Lab no longer expose model-internal propagation names as the visible option text.
- `Noisy OR` now renders as `Independent exposure spread`.
- `Leontief bottleneck` now renders as `Bottleneck-limited spread`.
- `Additive cap` now renders as `Capped cumulative spread`.
- Underlying API/model enum values remain unchanged, preserving backwards compatibility and report metadata.
- Added a frontend display quality guard to prevent the model-internal option labels from returning to primary page copy.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.
- `Select-String -Path artifacts/browser-smoke/report.json -Pattern 'Noisy OR|Leontief bottleneck|Additive cap|Affected mean legacy|Max legacy|semirisk_fixture_metadata|graphVersion=|sourceManifestId=|\[object Object\]'` - no matches.

### Deployment Status

- No Render deployment is claimed for this gate.
- Public deployed API/Web remain stale or unverified until the missing Render secrets or manual Render redeploy path is restored.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Known Limitations

- This gate improves local form copy only; it does not change the underlying simulation algorithms or deployed Render state.
- Local Next dev startup still emitted a non-blocking cache persistence permission warning; smoke passed and no product behavior regression was observed.

## 2026-05-30 Run Result ID Declutter

### Current HEAD

- Starting HEAD: `c0aeac7d8d00fb98095252eb73ac0cd26bbbf533`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Forward stress transmission lists no longer show raw `path:edge:...` identifiers as primary row titles.
- Reverse stress charts and tables no longer use raw `shock_set_id` values as chart labels or primary table labels.
- Optimizer charts and tables no longer use raw `action_id`, `target_id`, or run IDs as default display labels.
- Result subtitles no longer expose run IDs or model version strings; these remain in collapsed audit details.
- Inline scenario explanations now translate internal tokens such as `loss_mode=resilience_integral_loss`, `propagation_mode=auto_semiconductor`, `additive_cap`, and `leontief_bottleneck` into user-facing language.
- Simple table headers now capitalize through `formatDisplayLabel`, so generic columns such as `path`, `method`, and `cvar95` render as display labels.

### Files Changed

- `apps/web/src/features/common/displayLabels.ts`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks after updating smoke expectations for collapsed model version details.
- `Select-String -Path artifacts/browser-smoke/report.json -Pattern 'Noisy OR|Leontief bottleneck|Additive cap|Affected mean legacy|Max legacy|semirisk_fixture_metadata|graphVersion=|sourceManifestId=|\[object Object\]|path:edge:|action:increase_inventory_buffer|semirisk_reverse_stress_v0.1|semirisk_intervention_optimizer_v0.1'` - no matches.

### Deployment Status

- No Render deployment is claimed for this gate.
- Public deployed API/Web remain stale or unverified until the missing Render secrets or manual Render redeploy path is restored.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Known Limitations

- Raw IDs are still preserved in API payloads, audit details, and export data for traceability; this gate changes only default page presentation.
- Local Next dev startup may still emit a non-blocking cache persistence permission warning; smoke passed and no product behavior regression was observed.

## 2026-05-30 Primary Page Identifier Declutter

### Current HEAD

- Starting HEAD: `dcad2287c2074bffa1a3e38fe8870d0df8932bb5`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Entity Risk 360 now shows entity names and node types instead of raw `company:*` node IDs in the primary watchlist, score panel, and ranking table.
- Prediction Center now shows formatted target names in the queue/workbench; prediction IDs, target IDs, and model version remain in collapsed audit details.
- Forward Shock Simulator no longer displays run IDs in run history, run tables, affected-node chips, or compare panels.
- Reverse Stress Lab and Intervention Optimizer no longer display context run IDs as primary fields; selected context is summarized in user-facing language.
- Investigation Report no longer shows report IDs, report version strings, or selected run refs in the primary summary; they remain available in audit details and exports.
- Graph scenario overlay now says whether a selected run is available instead of rendering `run_id:` in the panel.
- Audit detail labels are formatted for readability while preserving the underlying metadata values.

### Files Changed

- `apps/web/src/features/common/AuditDetails.tsx`
- `apps/web/src/features/common/displayLabels.ts`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `apps/web/src/features/graph-explorer/GraphScenarioOverlay.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed after updating the Entity Risk smoke expectation from raw `company:tsmc` to `TSMC`.
- `Select-String -Path artifacts/browser-smoke/report.json -Pattern 'run_id:|company:tsmc|graphVersion=|sourceManifestId=|semirisk_investigation_report_v0.1|semirisk_reverse_stress_v0.1|semirisk_intervention_optimizer_v0.1|\[object Object\]|path:edge:|action:increase_inventory_buffer|data_mode:|graph_version:|source_manifest_id:|transport_attempts:|failed_endpoint:|not_production_ready: true'` - no matches.

### Deployment Status

- No Render deployment is claimed for this gate.
- Public deployed API/Web remain stale or unverified until the missing Render secrets or a stable manual Render redeploy path is restored.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Known Limitations

- IDs and version fields remain intentionally present in API responses, exported reports, and collapsed audit details for traceability.
- Browser smoke does not assert every possible table cell value; it now guards the main page text against the highest-noise raw identifiers and diagnostics.
- Local Next dev startup still emitted a non-blocking cache persistence permission warning; smoke passed.

## 2026-05-30 Stage View Source Family Declutter

### Current HEAD

- Starting HEAD: `f0111aac45db851ffef4b1b0d1e56a0e7362206b`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Graph Explorer stage views no longer show source-family identifiers such as `national_policy_macro_public` as primary labels.
- Source families now render as business-readable labels:
  - National, policy, macro public sources
  - Enterprise public disclosures
  - Industry public fixture sources
- Stage edge endpoint labels now format node refs instead of showing raw `source -> target` IDs in the stage list.
- Long source-gap and proxy-limitation text moved out of the main graph summary and into audit details with a short user-facing caveat.
- Stage view still preserves graph/source/data-mode metadata, relationship class, and evidence-context non-dependency warnings.

### Files Changed

- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `tests/quality/test_stage_frontend_artifacts.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_stage_frontend_artifacts.py tests/quality/test_frontend_display_declutter.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.

### Deployment Status

- No Render deployment is claimed for this gate.
- Public deployed API/Web remain stale or unverified until the missing Render secrets or a stable manual Render redeploy path is restored.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Known Limitations

- Stage source coverage remains fixture/promoted-public-evidence with documented proxy limitations.
- Full source IDs are still present in API responses, source coverage tables, and audit/export paths for traceability.

## 2026-05-30 Primary Table And Graph Label Declutter

### Current HEAD

- Starting HEAD: `197ba5432c9f953b61ee4fc7bdf67a5f599ea6f0`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Added shared UI display helpers for node refs, source refs, stage IDs, relationship classes, and edge types.
- Metadata summary badges now format labels before rendering and no longer collapse to empty text when the label contains a colon.
- Common chart and table primitives format raw node/source identifiers into user-facing labels while preserving API/export/audit values.
- Graph Explorer relationship views now display suppliers, products, dependencies, regions, and source refs with user-facing labels rather than raw IDs.
- Graph Explorer node catalog, evidence, and source coverage views now format source candidates and evidence refs in primary UI.
- Audit details still contain graph/source/data-mode metadata and warnings; raw IDs remain available in API payloads and exports.

### Files Changed

- `apps/web/src/features/common/AuditDetails.tsx`
- `apps/web/src/features/common/charts/ChartPrimitives.tsx`
- `apps/web/src/features/common/displayLabels.ts`
- `apps/web/src/features/common/tables/DataTable.tsx`
- `apps/web/src/features/graph-explorer/DemandRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/GraphEvidenceView.tsx`
- `apps/web/src/features/graph-explorer/GraphNodeCatalogView.tsx`
- `apps/web/src/features/graph-explorer/GraphSourceCoverageView.tsx`
- `apps/web/src/features/graph-explorer/ProductionDependencyView.tsx`
- `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx`
- `apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx`
- `tests/quality/test_frontend_display_declutter.py`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed after rerunning with a longer timeout; the first combined run timed out without failure output.
- `npm.cmd --workspace apps/web run build` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks after fixing empty metadata summary badges.
- `Select-String -Path artifacts/browser-smoke/report.json -Pattern 'data_mode:|graph_version:|source_manifest_id:|transport_attempts:|failed_endpoint:|not_production_ready: true|company:tsmc|national_policy_macro_public|enterprise_public_disclosure|industry_public_fixture|sec_edgar_lite|gdelt_semiconductor_lite|un_comtrade_semiconductor_trade_lite|evidence_context_link|SUPPLY_RELATIONSHIP|DEMAND_RELATIONSHIP|PRODUCTION_DEPENDENCY'` - no matches.

### Deployment Status

- No Render deployment is claimed for this local gate.
- Public deployed API/Web remain stale or unverified until Render redeploy access is restored.
- The platform remains fixture/promoted-public-evidence research infrastructure, not production-ready.

### Known Limitations

- Primary UI is cleaner, but source IDs and node IDs are intentionally still present in API responses, collapsed audit details, and exported evidence for traceability.
- Browser smoke validates representative pages and high-noise identifiers; it does not inspect every possible table row from every endpoint.

## 2026-05-30 Inspector And System Health Label Declutter

### Current HEAD

- Starting HEAD: `bd065cffed2fb048bd305cfd9c46790120a957c9`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Graph Explorer inspector now formats node refs, source refs, edge types, country refs, path evidence, and metadata values through the shared display-label layer before rendering primary UI text.
- Stage graph views now use the shared node/source display helpers instead of local raw ID handling for node labels and source-family labels.
- System Health data catalog and entity-resolution audit tables now render user-facing source labels rather than raw source IDs.
- Existing API payloads, audit details, exports, source refs, graph/source/data-mode metadata, and evidence traceability are preserved.
- Browser smoke evidence confirmed no primary-page matches for raw metadata/source/relationship patterns including `data_mode:`, `graph_version:`, `source_manifest_id:`, `failed_endpoint:`, `company:tsmc`, raw source IDs, or raw relationship class constants.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `apps/web/src/features/graph-explorer/GraphInspector.tsx`
- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` - passed, 12 tests.
- `npm.cmd --workspace apps/web run typecheck` - passed after adding an explicit return type to the inspector formatter.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.
- `Select-String -Path artifacts/browser-smoke/report.json -Pattern 'data_mode:|graph_version:|source_manifest_id:|transport_attempts:|failed_endpoint:|not_production_ready: true|company:tsmc|national_policy_macro_public|enterprise_public_disclosure|industry_public_fixture|sec_edgar_lite|gdelt_semiconductor_lite|un_comtrade_semiconductor_trade_lite|evidence_context_link|SUPPLY_RELATIONSHIP|DEMAND_RELATIONSHIP|PRODUCTION_DEPENDENCY'` - no matches.

### Deployment Status

- No Render deployment is claimed for this local UI-label gate.
- The latest deployed API/Web remain stale or unverified until Render access is restored.
- Previous Computer Use attempts reached ChatGPT login or Render browser timeout states; no credentials, cookies, tokens, secrets, raw payloads, or private account data were entered or recorded.

### Known Limitations

- Some raw IDs remain intentionally available in collapsed audit details, API responses, reports, and exports for traceability.
- This gate improves default presentation quality; it does not change the deployed Render blocker or claim production readiness.

## 2026-05-30 Stage Table And Source Coverage API Hardening

### Current HEAD

- Starting HEAD: `bf729d4c0a7c2a2fca7efc8f6fb0af17a912f96c`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Stage graph source coverage rows now include source family, source scope, supported node types, supported edge types, supported relationship classes, coverage summary, fixture policy, and API visibility policy.
- Stage table endpoints no longer fall back to generic graph node rows for stage-specific tables such as mineral inputs, material/chemical inputs, equipment suppliers, fab process dependencies, packaging/testing, logistics routes, compliance restrictions, stage node catalog, stage source coverage, and stage evidence refs.
- L3 Design/EDA/IP source family coverage was corrected to include national/multilateral public evidence because OECD reports are a primary source for that stage.
- Existing bounded metadata, fixture/public-evidence labels, no-live-fetch posture, no raw payload exposure, and geography normalization requirements are preserved.

### Files Changed

- `configs/sources/stage_source_coverage_matrix.yaml`
- `docs/data/stage-source-coverage-matrix.md`
- `services/api/services/graph_service.py`
- `services/api/services/stage_graph_service.py`
- `tests/api/test_stage_graph_endpoints.py`

### Commands Run

- `python -m pytest tests/api/test_stage_graph_endpoints.py tests/sources/test_stage_source_coverage_matrix.py -q` - passed, 29 tests.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.

### Deployment Status

- No Render deployment is claimed for this local API hardening gate.
- Deployed API/Web were already recorded as unavailable for the latest implementation path; redeploy remains blocked until a safe Render access path is restored.

### Known Limitations

- Stage coverage still uses fixture/promoted public evidence and documented proxies; it does not claim calibrated production telemetry.
- Stage-specific tables improve API semantics but remain bounded summaries; detailed raw source records remain unavailable by design.

## 2026-05-30 Display Noise Reduction Follow-Up

### Current HEAD

- Starting HEAD: `908ede3aee6d9835623464da20589c8f13ab4a6a`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Common audit details now format internal warning tokens before rendering them in expandable audit sections.
- `not_production_ready=true` and fixture calibration audit values are converted to user-facing research/fixture language when shown.
- Common chart/table frames still keep metadata props and export/API compatibility, but default pages only show the audit disclosure for degraded or warning states instead of repeating technical audit controls under every normal chart/table.
- Graph Explorer legend now uses the shared public-warning formatter so evidence-context and fixture warnings remain consistent with the rest of the product.
- Browser smoke confirmed primary page text does not expose raw `data_mode:`, `graph_version:`, `source_manifest_id:`, `transport_attempts:`, `failed_endpoint:`, `not_production_ready: true`, `relationship_endpoint_unavailable`, or fixture calibration tokens.

### Files Changed

- `apps/web/src/features/common/AuditDetails.tsx`
- `apps/web/src/features/common/charts/ChartPrimitives.tsx`
- `apps/web/src/features/common/tables/DataTable.tsx`
- `apps/web/src/features/graph-explorer/GraphLegend.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` - passed, 13 tests.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - initial 184-second runner timeout with no assertion output, rerun with longer timeout passed.
- `npm.cmd --workspace apps/web run build` - passed.
- Started local API/Web on `127.0.0.1:8000` and `127.0.0.1:3000`.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.
- `Select-String -Path artifacts/browser-smoke/report.json -Pattern 'data_mode:|graph_version:|source_manifest_id:|transport_attempts:|failed_endpoint:|not_production_ready: true|fixture_proxy_not_calibrated; not_financial_loss|relationship_endpoint_unavailable|semirisk_fixture_metadata'` - no matches.

### Deployment Status

- No Render deployment is claimed for this local UI declutter follow-up.
- Latest deployed API/Web remain unavailable or unverified until Render access is restored through a safe project-scoped path.
- Computer Use actions for this gate: none.

### Known Limitations

- Audit metadata remains available in APIs, exports, reports, and expandable audit details where needed for traceability.
- This gate improves default display quality; it does not add new source telemetry or claim production readiness.

## 2026-05-30 Stage Source Family Coverage Enrichment

### Current HEAD

- Starting HEAD: `0af333d69881e5c396c248c82160e45622d62627`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Stage source coverage now requires every L0-L11 stage to carry all three public source families: national/policy/macro, enterprise public disclosure, and industry public fixture evidence.
- Coverage matrix gaps were patched for L0 policy/macro, L1 raw minerals, L6 products, L8 logistics, L9 downstream demand, and L11 compliance by adding appropriate public source candidates without enabling live fetch.
- Stage graph API family coverage now reports true per-family source counts, primary/secondary counts, and source IDs instead of repeating the same total for every family.
- Stage Graph Explorer views now show a compact "Evidence support by source" section with formatted source names, tier, source scope, and normalized coverage text.
- Existing fixture/promoted public-evidence posture, bounded responses, no raw payload exposure, and `region:china_taiwan` / `中国台湾` terminology remain unchanged.

### Files Changed

- `configs/sources/stage_source_coverage_matrix.yaml`
- `docs/data/stage-source-coverage-matrix.md`
- `services/api/services/stage_graph_service.py`
- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `tests/sources/test_stage_source_coverage_matrix.py`
- `tests/api/test_stage_graph_endpoints.py`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/sources/test_stage_source_coverage_matrix.py tests/api/test_stage_graph_endpoints.py tests/quality/test_frontend_display_declutter.py -q` - passed, 42 tests.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - initial 120-second runner timeout with no assertion output, rerun with longer timeout passed.
- `npm.cmd --workspace apps/web run build` - passed.
- Started local API/Web on `127.0.0.1:8000` and `127.0.0.1:3000`.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.

### Deployment Status

- No Render deployment is claimed for this local source-coverage enrichment gate.
- Deployed API/Web remain stale or unverified until a safe Render access path is available.
- Computer Use actions for this gate: none.

### Known Limitations

- Added sources are registry/fixture/promoted public-evidence candidates; live connectors remain disabled by default.
- Stage source coverage is broader and clearer, but still identifies proxy limitations and does not claim production telemetry.

## 2026-05-30 Deployed API Fallback Tightening

### Current HEAD

- Starting HEAD: `3b62c52db40129e82183d26fd15a31fed3482586`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Browser reads now spend fewer attempts on the direct API origin when a same-origin read fallback is configured, so Render cold-start 5xx/timeouts can move to the Web proxy path faster.
- Deployed Web runtime now uses a shorter request timeout for browser data reads while keeping POST/write calls on the direct API write base; non-idempotent writes are still not retried through the proxy.
- Unavailable envelopes still carry `failed_endpoint`, `retry_hint`, `transport_attempts`, source status, and graph/source/data-mode metadata.
- This keeps direct public API as the preferred deployed read origin when it is healthy, while reducing the chance that Entity Risk remains in a stale pending/degraded UI after a transient API restart.

### Files Changed

- `apps/web/src/app/App.tsx`
- `packages/api-client/src/dashboard.ts`
- `tests/quality/test_deployed_api_transport_fallback.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_deployed_api_transport_fallback.py tests/quality/test_frontend_display_declutter.py -q` - passed, 15 tests.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- Started local API/Web on `127.0.0.1:8000` and `127.0.0.1:3000`.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.

### Deployment Status

- Render API deploy `dep-d8ddkiurnols73983hng` for `supply-risk-atlas-api` reached live at commit `3b62c52db40129e82183d26fd15a31fed3482586`.
- Render Web deploy `dep-d8ddkrcp3tds73fg3060` for `supply-risk-atlas-web` reached live at commit `3b62c52db40129e82183d26fd15a31fed3482586`.
- Public version probe showed API, Web build-info, and Web proxy at `3b62c52`; conservative script status remained `deployed_stale_or_unverified` only because the static HTML shell does not expose the commit string.
- Deployed endpoint probes returned 200 for `/api/v1/version`, `/api/v1/health`, `/api/v1/risk/entities/company%3Atsmc`, and `/api/v1/stage-graph/L5_fabrication` after Render warm-up.
- `npm.cmd run smoke:web -- --mode=deployed` exited 0 in best-effort mode but initially observed Entity Risk in pending/degraded state during API warm-up; after waiting, Chrome page state showed the TSMC risk score and evidence tables rendered.

### Computer Use Actions

- Used Chrome extension browser only for project-scoped Render dashboard verification.
- Triggered `Deploy latest commit` for `supply-risk-atlas-api` and `supply-risk-atlas-web`.
- Recorded only sanitized service names, deploy IDs, commit SHA, and live/build state.
- No credentials, cookies, tokens, private URLs, raw logs, or account secrets were copied into docs or chat.

### Known Limitations

- The transport tightening is local until this follow-up commit is pushed and Render redeploys again.
- The static HTML shell still does not carry the commit marker used by `scripts/check-deployed-version.py`, so that script can remain conservative even when API/build-info/proxy commit values match.

## 2026-05-30 Deployed API Cold-Start Timeout Tuning

### Current HEAD

- Starting HEAD: `cbf74dbf35600a5a9ebe2a87c1055399dcf841e3`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Follow-up deployed smoke showed the 12-second deployed browser timeout was too aggressive after a Render restart: Entity Risk could abort otherwise valid Risk Score v0 reads during warm-up.
- Updated browser read strategy so a configured fallback path causes the direct public API origin to be tried once, not repeatedly, before moving to fallback.
- Increased deployed browser request timeout to 25 seconds to avoid premature aborts while still bounding slow Render cold-start reads.
- POST/write calls still use the direct API write base and are not retried through the same-origin proxy.

### Files Changed

- `apps/web/src/app/App.tsx`
- `packages/api-client/src/dashboard.ts`
- `tests/quality/test_deployed_api_transport_fallback.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_deployed_api_transport_fallback.py tests/quality/test_frontend_display_declutter.py -q` - passed, 15 tests.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- Started local API/Web on `127.0.0.1:8000` and `127.0.0.1:3000`.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.

### Deployment Status

- This tuning is local until committed, pushed, and redeployed after this section.
- Previous deployed probe for `cbf74db` confirmed API, Web build-info, and Web proxy commit values matched, but best-effort deployed smoke still showed Entity Risk timing out at 12 seconds during warm-up.

### Known Limitations

- Render cold-start behavior can still be variable; the UI remains bounded and diagnostic-bearing instead of fabricating scores.
- The platform remains fixture/promoted public-evidence research infrastructure, not production-ready telemetry.

## 2026-05-30 Deployed Same-Origin Read Path Stabilization

### Current HEAD

- Starting HEAD: `69f1381cb1de4c09df9aae350437f4c650fc4954`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Deployed browser reads now use the same-origin Web `/api/v1` proxy as the primary read path, avoiding headless/deployed-browser direct API stalls that left Entity Risk in a pending state.
- Deployed write calls remain direct to `https://supply-risk-atlas-api.onrender.com/api/v1` and still do not retry non-idempotent writes through the proxy.
- Deployed browser request timeout is now 45 seconds so the Web proxy can complete its bounded upstream warm-up retries before the browser aborts the read.
- The API client still keeps bounded retries, sanitized diagnostics, and no raw payload exposure.

### Files Changed

- `apps/web/src/app/App.tsx`
- `tests/quality/test_deployed_api_transport_fallback.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_deployed_api_transport_fallback.py tests/quality/test_frontend_display_declutter.py -q` - passed, 15 tests.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- Started local API/Web on `127.0.0.1:8000` and `127.0.0.1:3000`.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.

### Deployment Status

- This stabilization is local until committed, pushed, and redeployed after this section.
- Previous deployed smoke for `69f1381` still showed Entity Risk timing out on direct API reads after 25 seconds, which motivated the same-origin primary read path.

### Known Limitations

- The same-origin proxy still depends on the Render API service; cold starts can degrade temporarily, but they now go through a single bounded retry policy with user-facing diagnostics.
- The platform remains fixture/promoted public-evidence research infrastructure, not production-ready telemetry.

## 2026-05-30 Web Build Info Commit Stabilization

### Current HEAD

- Starting HEAD: `1783e72f224af46585db9ae3a89502a6b180cd5c`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Render Web showed the latest deploy live, but `/api/build-info` could still report an older `NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT` value when that public environment value was stale.
- Updated Web build metadata priority so Render/Git/current checkout commit beats stale public override values.
- Updated `/api/build-info` to resolve runtime commit from `RENDER_GIT_COMMIT`, then `SUPPLY_RISK_GIT_COMMIT`, then the sanitized public fallback.
- Kept cache control as `no-store` and did not expose raw payloads, secrets, local paths, cookies, or private diagnostics.

### Files Changed

- `apps/web/next.config.mjs`
- `apps/web/src/app/api/build-info/route.ts`
- `tests/quality/test_web_commit_marker.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_web_commit_marker.py tests/quality/test_deployed_version_checker.py tests/quality/test_deployed_api_transport_fallback.py -q` - passed, 23 tests.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed after rerun with a longer timeout; the first 3-minute run timed out without an assertion failure.
- Started local API/Web on `127.0.0.1:8000` and `127.0.0.1:3000`.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.

### Deployment Status

- This stabilization is local until committed, pushed, and redeployed.
- Previous deployed state after commit `1783e72` had API and Web proxy at the expected commit; Web build-info still reported `69f1381`, which this patch addresses.

### Known Limitations

- Static HTML commit visibility depends on the value embedded at Web build time; this patch ensures stale public overrides no longer take priority over Render/Git/current checkout commit sources.
- The platform remains fixture/promoted public-evidence research infrastructure, not production-ready telemetry.

## 2026-05-30 Deployed Write Path Stabilization

### Current HEAD

- Starting HEAD: `1136535be7f3f825e63868a8727b9997a947fac1`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Render deploy for `1136535` reached live on API and Web, and `scripts/check-deployed-version.py` reported `deployed_verified` with no warnings.
- Deployed smoke then exposed an intermittent browser write-path failure: Entity Risk reads could pass, but Shock Simulator POST could still show `Failed to fetch` in headless Chrome.
- Direct deployed API POST probes succeeded, and manual Chrome verification on the deployed Shock Simulator page produced Expected/P50/CVaR results, so the remaining failure was isolated to deployed browser write transport stability under smoke load.
- Updated deployed Web write base to use the same-origin `/api/v1` proxy. The proxy forwards POST with a single upstream attempt, so non-idempotent writes are still not retried through fallback paths.
- Reduced deployed browser startup pressure by changing dashboard hydration from all-at-once full-dashboard loading to page-scoped sequential requests. Entity Risk now loads only its entity overview plus its risk endpoints, graph pages load graph/path data, and simulation/report pages load only the global metadata they need.
- Merged page-scoped dashboard results instead of replacing the full result map, preventing late responses from a previous page from clearing the current page's active metadata state during smoke navigation.
- Kept all API envelopes, report metadata, source refs, graph/source/data-mode metadata, and no-raw-payload guarantees unchanged.

### Files Changed

- `apps/web/src/app/App.tsx`
- `tests/quality/test_deployed_api_transport_fallback.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_deployed_api_transport_fallback.py tests/quality/test_frontend_display_declutter.py -q` - passed, 15 tests.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- Started local API/Web on `127.0.0.1:8000` and `127.0.0.1:3000`.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.

### Deployment Status

- Previous deployed commit `1136535` is verified live.
- This write-path stabilization is local until committed, pushed, and redeployed.

### Known Limitations

- Render free-tier cold starts and short-lived 429s on auxiliary run-history reads can still occur under repeated smoke loops; user-facing pages must show controlled diagnostics instead of fabricated data.
- The platform remains fixture/promoted public-evidence research infrastructure, not production-ready telemetry.

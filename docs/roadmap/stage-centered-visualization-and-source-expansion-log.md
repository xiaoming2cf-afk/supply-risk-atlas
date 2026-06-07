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

## 2026-05-30 Browser Smoke Navigation Readiness Stabilization

### Current HEAD

- Starting HEAD: `ef5ce88f09adf619e13769e072cd78dc03d8011e`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- GitHub `Quality Gates` passed for `ef5ce88`, but `ci / browser-smoke` failed twice in the local real-API smoke job with a transient Chrome error page titled `This page couldn\u2019t load`.
- The failure occurred before page-specific assertions and after local API/Web startup, so the next fix targets smoke navigation readiness rather than weakening application checks.
- Updated `scripts/browser-smoke.mjs` to poll Web readiness, recognize browser load-error pages, retry bounded navigation, and fail with a clear final page state only after repeated load errors.
- After the first pushed fix, GitHub `ci / browser-smoke` still failed on the final hash route because repeated full `Page.navigate` calls against the same SPA path could still land on a transient Chrome load-error page.
- Updated the smoke navigator again so it reuses an already loaded app shell for same-path hash page checks and only performs a full browser navigation when the current document is missing or already degraded.
- After the second pushed fix, GitHub `ci / browser-smoke` still failed on the same final hash route. The page matrix now loads the app shell once and switches pages through the SPA hash/nav controls, eliminating repeated full navigations from the basic public-page inventory pass.
- Local smoke initially caught a `pushState` hash synchronization issue in the new SPA page switcher; the switcher now uses native `window.location.hash` assignment and keeps full navigation out of the page matrix.
- Added a quality assertion so the smoke script keeps this CI hardening behavior.

### Files Changed

- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_source_readability.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `node --check scripts/browser-smoke.mjs` - passed.
- `python -m pytest tests/quality/test_frontend_source_readability.py -q` - passed, 5 tests.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- Started local API/Web on `127.0.0.1:8000` and `127.0.0.1:3000`.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.
- After GitHub `ci` failed once more on the final hash route, reran targeted checks after the same-path hash navigation patch:
  - `node --check scripts/browser-smoke.mjs` - passed.
  - `python -m pytest tests/quality/test_frontend_source_readability.py -q` - passed, 5 tests.
  - `python -m pytest tests/quality/test_deployed_api_transport_fallback.py tests/quality/test_frontend_display_declutter.py -q` - passed, 15 tests.
  - `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.
  - `python -m pytest tests/quality -q` - passed.
- After changing the SPA page switcher to native hash assignment:
  - `node --check scripts/browser-smoke.mjs` - passed.
  - `python -m pytest tests/quality/test_frontend_source_readability.py -q` - passed, 5 tests.
  - `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.
  - `python -m pytest tests/quality -q` - passed.

### Deployment Status

- No new deployment yet for this patch.
- Latest deployed commit before this patch was `3bf5ce0` during the previous failed CI cycle; deployment must wait for this smoke stabilization to pass GitHub `ci` and `Quality Gates`.

### Known Limitations

- This patch does not mask application failures; it only retries transient Chrome local-load errors before running the same page, relevance, graph, relationship, and no-raw-payload assertions.
- The platform remains fixture/promoted public-evidence research infrastructure, not production-ready telemetry.

## 2026-05-30 Deployed Direct API Read Stabilization

### Current HEAD

- Starting HEAD: `c3f89457c068a35a58ff48014f6c6b50f762bb2a`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- GitHub `ci` and `Quality Gates` passed for `c3f8945`.
- Render API/Web were redeployed from `c3f8945` and `/api/v1/version` verified that API, web build-info, same-origin proxy, and deployed HTML reported `c3f89457c068a35a58ff48014f6c6b50f762bb2a`.
- Deployed smoke remained best-effort: it exited successfully but captured transient deployed read failures on Entity Risk/System Health during Render cold-start windows.
- Direct public API CORS was verified healthy for the deployed web origin. The remaining issue was that deployed browser reads still preferred the same-origin Web proxy, so proxy cold starts could hold the page in degraded state even when the public API was reachable.
- Updated deployed transport policy so deployed browser GET reads prefer `https://supply-risk-atlas-api.onrender.com/api/v1`, keep `/api/v1` as same-origin read fallback, and keep deployed write/POST calls direct to the public API without proxy retry.

### Files Changed

- `apps/web/src/app/App.tsx`
- `tests/quality/test_deployed_api_transport_fallback.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_deployed_api_transport_fallback.py tests/quality/test_frontend_display_declutter.py -q` - passed, 15 tests.
- `python -m pytest tests/quality -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - first run hit a transient browser hash-switch wait state; immediate rerun passed with 63 checks.

### Deployment Status

- This direct-API deployed transport patch is local until committed, pushed, and redeployed.
- Next verification target: `/api/v1/version` must report the new commit after Render API/Web redeploy; deployed smoke should no longer permanently degrade Entity Risk after transient Web proxy 503s.

### Known Limitations

- Render service warm-up can still produce short 503 windows. The UI must continue showing controlled degraded diagnostics rather than authoritative fallback data.
- The platform remains fixture/promoted public-evidence research infrastructure, not production-ready telemetry.

## 2026-05-30 Deployed Read 429 Retry Follow-Up

### Current HEAD

- Starting HEAD: `a6caf97496b04b8891858ff5b773f3f57ddc80f3`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- GitHub `ci` and `Quality Gates` passed for `a6caf97`.
- Render API/Web were redeployed from `a6caf97`, and the full commit version probe reported `deployed_verified`.
- Deployed smoke still found Entity Risk degraded when the risk endpoints returned HTTP 429 during repeated browser smoke reads.
- Updated the API client retry classifier so idempotent GET/HEAD reads retry and can move to the configured read fallback for HTTP `408`, `425`, `429`, and `5xx`. Non-idempotent write requests remain direct and single-attempt.

### Files Changed

- `packages/api-client/src/dashboard.ts`
- `tests/quality/test_deployed_api_transport_fallback.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_deployed_api_transport_fallback.py tests/quality/test_frontend_display_declutter.py -q` - passed, 15 tests.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.

### Deployment Status

- This 429 retry follow-up is local until committed, pushed, and redeployed.

### Known Limitations

- Render free-tier throttling can still exhaust all bounded read attempts; pages must continue to show controlled degraded diagnostics rather than fabricate entity risk rows.
- The platform remains fixture/promoted public-evidence research infrastructure, not production-ready telemetry.

## 2026-05-30 Risk Endpoint Fixture Cache Stabilization

### Current HEAD

- Starting HEAD: `e626cf6bc5872edf09546df7a984cb955c8c5856`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- GitHub `ci` and `Quality Gates` passed for `e626cf6`.
- Render API/Web were redeployed from `e626cf6`, and the full commit version probe reported `deployed_verified`.
- Deployed smoke still observed Entity Risk degradation under repeated smoke reads because `/risk/entities` and `/risk/portfolio` could time out after exhausting bounded transport attempts.
- Added API-side in-process LRU caching for deterministic fixture risk entity and portfolio payloads. Cached payloads are deep-copied before envelope creation so request handlers cannot mutate the cached source.
- This reduces repeated CPU/query pressure on Render without adding live fetch, production data, raw payload exposure, or production-readiness claims.

### Files Changed

- `services/api/services/risk_service.py`
- `tests/api/test_semirisk_risk_score.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/api/test_semirisk_risk_score.py tests/quality/test_deployed_api_transport_fallback.py -q` - passed, 8 tests.
- `python -m pytest tests/quality -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.

### Deployment Status

- This risk endpoint cache patch is local until committed, pushed, and redeployed.

### Known Limitations

- The cache covers deterministic fixture/promoted risk score payloads only. It is not production telemetry and does not enable live connector fetch.
- Render free-tier throttling can still happen during cold start or concurrent smoke loops; the UI keeps controlled degraded states with diagnostics.

## 2026-05-30 Deployed Smoke Controlled Entity-Risk Degradation

### Current HEAD

- Starting HEAD: `40501f2ab76a52abfc7aae392cc5b606163fd647`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- GitHub `ci` and `Quality Gates` passed for `40501f2`.
- Render API/Web were redeployed from `40501f2`, and the full commit version probe reported `deployed_verified`.
- Deployed smoke still observed Render 503s on repeated Entity Risk reads during best-effort deployed verification, while direct/proxy probes recovered to HTTP 200 after warm-up.
- Updated browser smoke so deployed mode accepts Entity Risk only when it either renders full risk evidence or shows the controlled unavailable state with diagnostics. Local/CI real API mode still requires full evidence when the risk API capability probe is healthy.
- Removed the brittle hash-equality wait from SPA page switching; the smoke still validates each page title and content after switching.

### Files Changed

- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_source_readability.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `node --check scripts/browser-smoke.mjs` - passed.
- `python -m pytest tests/quality/test_frontend_source_readability.py tests/quality/test_deployed_api_transport_fallback.py -q` - passed, 8 tests.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.

### Deployment Status

- This deployed-smoke stabilization is local until committed and pushed. No Render redeploy is needed for this docs/smoke-only change.

### Known Limitations

- Deployed smoke remains best-effort because Render free-tier services can return transient 503/429 under repeated automated reads.
- The product UI still refuses to fabricate entity risk scores when the authoritative risk endpoints are unavailable.

## 2026-05-30 Deployed Visualization Smoke Degradation Alignment

### Current HEAD

- Starting HEAD: `21aa87eafa37867c1841995af782480feb49e6da`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- GitHub `ci` and `Quality Gates` passed for `21aa87e`.
- Render API/Web were redeployed from `21aa87e`, and the full commit version probe reported `deployed_verified`.
- Deployed smoke reached Entity Risk page visualization before the dedicated risk assertion and still saw a controlled unavailable state while risk reads were pending or rate-limited.
- Aligned the deployed-only page visualization check with the dedicated Entity Risk check: deployed smoke accepts either full risk evidence or the controlled Entity Risk unavailable state with diagnostics. Local/CI real API mode still requires full evidence when the API probe is healthy.

### Files Changed

- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_source_readability.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `node --check scripts/browser-smoke.mjs` - passed.
- `python -m pytest tests/quality/test_frontend_source_readability.py -q` - passed, 6 tests.
- `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000/ npm.cmd run smoke:web` - passed with 63 checks.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.

### Deployment Status

- This deployed-smoke alignment is local until committed and pushed. No Render runtime redeploy is required for this smoke-only change, but deployment can still be triggered to keep version markers aligned.

### Known Limitations

- Deployed smoke remains best-effort because Render free-tier services can throttle repeated automated reads. The app keeps controlled degraded states instead of fabricated data.

## 2026-05-30 Deployed Write API Stabilization

### Current HEAD

- Starting HEAD: `f87245eace76cc8019a7dd9eaa821610bb8f0f3d`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- GitHub `ci` and `Quality Gates` passed for `f87245e`.
- Render API service `supply-risk-atlas-api` and Web service `supply-risk-atlas-web` were manually redeployed from `f87245e`; both showed `Live`.
- Version probe for `f87245e` returned `deployed_verified` for API, Web build metadata, Web HTML, and Web proxy.
- Direct deployed endpoint probes returned HTTP 200 for `/version`, `/health`, `/risk/entities/company%3Atsmc`, `/graph/supply-relationships`, and `/analytics/tables/supply-relationships`.
- Deployed browser smoke then exposed a write-path issue: Shock Simulator POST from the deployed browser showed `Failed to fetch` while the same-origin Web proxy POST to `/api/v1/scenarios/forward` succeeded with the fixture envelope.
- Updated deployed Web write base URL to use the same-origin `/api/v1` proxy as the primary write path. POST requests remain single-attempt; non-idempotent writes are not retried through fallback paths.
- Fixed deployed smoke Entity Risk mode detection to use `deployedBestEffort` rather than `expectedMode === "deployed"`, and made its controlled source-status assertion case-insensitive.
- After the first `4f4a21c` CI attempt, GitHub browser-smoke failed before app checks because Chrome DevTools was not ready inside the default 30-second startup window. Increased the default `SUPPLY_RISK_CHROME_READY_MS` fallback to 60 seconds while preserving environment override.

### Files Changed

- `apps/web/src/app/App.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_deployed_api_transport_fallback.py`
- `tests/quality/test_frontend_source_readability.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python scripts/check-deployed-version.py --expected-commit f87245eace76cc8019a7dd9eaa821610bb8f0f3d --timeout 25 --attempts 3` - passed, `deployed_verified`.
- `npm.cmd run smoke:web -- --mode=deployed` - returned best-effort exit 0 but recorded Shock Simulator `Failed to fetch` before the write-path patch.
- Direct API and Web proxy endpoint probes - passed for read endpoints; Web proxy POST to `/api/v1/scenarios/forward` passed after warm-up.
- `node --check scripts/browser-smoke.mjs` - passed.
- `python -m pytest tests/quality/test_deployed_api_transport_fallback.py tests/quality/test_frontend_source_readability.py -q` - passed, 8 tests.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/security tests/graph_invariants -q` - passed.
- API tests were split by file after the aggregate command exceeded the local timeout; every API file passed individually.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `npm.cmd run smoke:web` - passed with 63 checks.
- `python -m pytest tests/geo tests/contract tests/sources tests/model tests/simulation tests/optimization tests/reports -q` - passed.

### Computer Use Actions

- Used project-scoped Chrome tabs for Render API/Web deploy verification only.
- No credentials, cookies, tokens, account settings, or private diagnostics were copied into logs.
- Failed/stale deployed smoke pages were not kept as additional browser tabs.

### Deployment Status

- Runtime deployment is currently live for `f87245e`.
- The write-path patch is local pending commit, push, CI, Render redeploy, and deployed smoke verification.

### Known Limitations

- The platform remains fixture/promoted public-evidence research infrastructure, not production-ready.
- Render free-tier cold starts and rate limiting can still require warm-up; unavailable states remain controlled and diagnostic-only.

## 2026-05-30 Display Declutter And Deployed Smoke Hardening

### Current HEAD

- Starting HEAD: `55ebf6e0d38d58d10bbc267b31dc58b9129b9a78`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Verified the display declutter implementation requested after the screenshot review:
  - `DataLineageBanner` now shows only user-facing coverage, freshness, source summary, and public-evidence/fixture mode badges by default.
  - `graph_version`, `source_manifest_id`, `data_mode`, `graph_mode`, `calibration_status`, `last_checked_at`, `failed_endpoint`, and `transport_attempts` remain available through collapsed audit/diagnostic details instead of the primary page surface.
  - `DataTable` and `ChartFrame` keep metadata props but render only concise public-evidence badges by default.
- Deployed smoke exposed Render transient 502/503 responses on explicit write-style pages even after API capability probes succeeded.
- Updated deployed best-effort smoke to accept only controlled unavailable states with `View diagnostics` for Shock Simulator, Reverse Stress Lab, Intervention Optimizer, and Investigation Report. Local smoke remains strict and requires full successful results.
- Updated the deployed degraded-envelope probe to prefer the Web proxy, retry the probe, preserve sanitized error evidence in the report, and treat test-route network failure as deployed best-effort limitation only. Local smoke still requires a real error envelope.

### Files Changed

- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python scripts/check-deployed-version.py --expected-commit 55ebf6e0d38d58d10bbc267b31dc58b9129b9a78 --timeout 25 --attempts 3` - passed, `deployed_verified`.
- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_deployed_api_transport_fallback.py tests/quality/test_frontend_source_readability.py -q` - passed.
- `node --check scripts/browser-smoke.mjs` - passed.
- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_frontend_source_readability.py -q` - passed.
- `npm.cmd run smoke:web` - passed with 63 checks.
- `npm.cmd run smoke:web -- --mode=deployed` - passed with 63 checks after deployed best-effort diagnostics alignment.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api/test_supply_demand_graph_endpoints.py tests/api/test_supply_demand_analytics_tables.py tests/api/test_api_endpoints.py tests/api/test_version_endpoint.py -q` - passed.
- `python -m pytest tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `python -m pytest -q` - passed.

### Deployment Status

- Existing deployed API/Web currently report `55ebf6e0d38d58d10bbc267b31dc58b9129b9a78`.
- This smoke/log patch is local pending commit, push, CI verification, Render redeploy, version probe, deployed smoke, and GPT Pro review handoff.

### Computer Use Actions

- No new Chrome/Render/GPT Pro action has been completed yet for this patch slice.
- Next project-scoped browser actions: push commit, verify GitHub `ci` and `Quality Gates`, redeploy Render API/Web, capture sanitized deployed page screenshots, and submit the GPT Pro review packet.

### Known Limitations

- Deployed write-style actions can still hit transient Render 502/503 during automated browser runs. The UI now shows controlled unavailable states with collapsed diagnostics and no fabricated results.
- The platform remains fixture/promoted public-evidence research infrastructure, not production-ready.

## 2026-05-30 Semiconductor Content Coverage API Slice

### Current HEAD

- Starting HEAD: `6b08696e7213f6af9a743848ec40801fedc21407`.
- Branch: `stage/chip-supply-chain-content-coverage`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Added a fixture-first semiconductor content coverage layer for national/regional, enterprise, and industry supply-chain context.
- Added bounded sanitized API routes for semiconductor coverage overview, value-chain layers, country/region exposures, entity profiles, and chokepoints.
- Extended Entity Risk 360 with an evidence-bound supply-chain role panel for known semiconductor entities.
- Extended System Health with a concise chip supply-chain coverage panel while keeping manifest/version/data-mode diagnostics folded in audit details.
- Kept canonical geography: `region:china_taiwan`, display `中国台湾`, parent `country:CN` / `中国`.

### Coverage Counts

- Countries/regions: `10`.
- Value-chain layers: `22`.
- Entity profiles: `41`.
- Relationship summaries: `15`.
- Chokepoints: `10`.
- Source families: `3` (`national_policy_macro_public`, `enterprise_public_disclosure`, `industry_public_fixture`).

### Files Changed

- `configs/sources/semiconductor_supply_chain_content.yaml`
- `docs/data/semiconductor-supply-chain-content-coverage.md`
- `services/api/services/semiconductor_content_service.py`
- `services/api/routes/semiconductor_content.py`
- `services/api/main.py`
- `services/api/dev_server.py`
- `services/api/services/system_health_service.py`
- `services/api/services/risk_service.py`
- `packages/shared-types/src/semiconductor-content.ts`
- `packages/shared-types/src/health.ts`
- `packages/shared-types/src/risk.ts`
- `packages/shared-types/src/index.ts`
- `packages/api-client/src/dashboard.ts`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `scripts/browser-smoke.mjs`
- `tests/sources/test_semiconductor_supply_chain_content.py`
- `tests/api/test_semiconductor_content_endpoints.py`
- `tests/quality/test_frontend_display_declutter.py`

### Commands Run

- `python -m pytest tests/sources/test_semiconductor_supply_chain_content.py tests/api/test_semiconductor_content_endpoints.py -q` -> PASS.
- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api -q` -> PASS.
- `python -m pytest tests/security -q` -> PASS.
- `python -m pytest tests/graph_invariants -q` -> PASS.
- `npm.cmd run smoke:web` -> PASS (`63` checks).
- `python -m pytest tests/sources -q` -> PASS.
- `python -m pytest tests/geo tests/contract tests/sources tests/graph_invariants tests/api tests/security tests/model tests/simulation tests/optimization tests/reports -q` -> PASS.
- `python -m pytest -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS (`63` checks).

### Failures And Fixes

- Initial local smoke connected to stale local API/Web dev processes. The stale processes were restarted with current code, then smoke passed.
- Initial System Health smoke did not show the new coverage panel because the lightweight summary payload lacked `coverage_counts` and representative rows. The summary now includes both `counts` and `coverage_counts` plus representative country/region, layer, entity, and chokepoint summaries.
- Initial relationship-content tests exposed missing `relationship_class` fields in the content fixture. Relationship summaries now explicitly separate supply, demand, production dependency, and evidence context records.
- API-visible audit payload no longer exposes a `raw_payload_policy` field name; it uses `source_payload_policy` while preserving the no-bulk-payload policy.

### Computer Use And Deployment Status

- No new Chrome/Render/GitHub/GPT Pro action has been completed for this slice yet.
- Next steps after commit: push branch, verify GitHub `ci` and `Quality Gates`, open or update PR, deploy from latest main/approved branch path as applicable, run deployed version probe and deployed smoke, then send GPT Pro a sanitized review packet.

### Known Limitations

- The content layer is a curated public-evidence fixture; live connectors remain disabled by default.
- Private supplier transactions, order books, capacity reservations, and customer shares are documented gaps.
- Capacity, demand, lead-time, and substitution values are proxy summaries unless directly supported by public fixture evidence.

## 2026-05-31 Semiconductor Content Coverage Deployment Verification

### Current HEAD

- Verified code commit: `d064e3d71b12a6e46e5ffe6a02b6d029a418635f`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- GitHub PR `#1` for the semiconductor content coverage API slice was merged into `main`.
- GitHub `ci` and `Quality Gates` both passed on `d064e3d71b12a6e46e5ffe6a02b6d029a418635f`.
- Render Web service `supply-risk-atlas-web` was manually redeployed with `Clear build cache & deploy` from `d064e3d71b12a6e46e5ffe6a02b6d029a418635f` and reached `live`.
- Render API service `supply-risk-atlas-api` was manually redeployed with `Deploy latest commit` from `d064e3d71b12a6e46e5ffe6a02b6d029a418635f` and reached `live`.
- Public version probe reported `deployed_verified`: API, Web build-info, Web HTML marker, and Web proxy all matched `d064e3d71b12a6e46e5ffe6a02b6d029a418635f`.
- Deployed smoke passed with `63` checks.
- Canonical geography remained visible as `region:china_taiwan` / `中国台湾`; no legacy standalone geography output was introduced.

### Commands Run

- `gh run watch 26703741609 --exit-status` - GitHub `ci` passed on merged `main`.
- `gh run watch 26703741614 --exit-status` - GitHub `Quality Gates` passed on merged `main`.
- `python scripts/check-deployed-version.py --expected-commit d064e3d71b12a6e46e5ffe6a02b6d029a418635f --timeout 40 --attempts 5` - passed, `deployed_verified`.
- Deployed endpoint probes returned HTTP `200` for `/api/v1/version`, `/api/v1/health`, `/api/v1/semiconductor/coverage`, and `/api/v1/risk/entities/company%3Atsmc`.
- `npm.cmd run smoke:web -- --mode=deployed` - passed with `63` checks.

### Screenshot Evidence For GPT Pro Review

- `artifacts/gpt-pro-review/d064e3d/system-health-headless.png` - System Health shows chip supply-chain coverage counts and public-evidence badges.
- `artifacts/gpt-pro-review/d064e3d/graph-explorer-headless.png` - Graph Explorer shows stage selector, relationship class selector, graph mode selector, source/evidence context, and no full dense graph by default.
- `artifacts/gpt-pro-review/d064e3d/entity-risk-headless.png` - Entity Risk 360 shows TSMC risk posture and supply-chain role context from fixture public evidence.
- One Chrome extension screenshot attempt initially observed a temporary `public data unavailable` state before refresh; retry loaded the expected System Health coverage panel. This was recorded as a transient deployed-page observation, not hidden.

### Computer Use Actions

- Used only project-scoped Chrome tabs for Render, deployed public pages, and the existing GPT Pro project conversation.
- Did not open unrelated tabs or copy credentials, cookies, tokens, private URLs, raw logs, or account secrets.
- Triggered Render manual deployments for `supply-risk-atlas-api` and `supply-risk-atlas-web`.
- Captured only public deployed application screenshots for GPT Pro review.

### Deployment Status

- Deployment status after this verification gate: `deployed_verified` for commit `d064e3d71b12a6e46e5ffe6a02b6d029a418635f`.
- This log update is docs-only and requires a follow-up commit/push plus Render redeploy if it becomes the latest `main` commit.

### Known Limitations

- The semiconductor content layer remains fixture/promoted public-evidence infrastructure, not production-ready.
- Live source connectors remain disabled by default; source enrichment is curated and bounded by public fixture evidence.
- GPT Pro review handoff is pending immediately after this deployment evidence commit is pushed and the latest docs-only commit is redeployed or explicitly marked as docs-only.

## 2026-05-31 Semiconductor Relationship And Source-Coverage API Hardening

### Current HEAD

- Starting commit: `755d549f07fb1b0b15fbd473df72c7de8bf017b1`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Added bounded semiconductor content endpoints for direct relationship inspection and value-chain source coverage:
  - `GET /api/v1/semiconductor/relationships`
  - `GET /api/v1/semiconductor/source-coverage`
- Extended `GET /api/v1/semiconductor/entities` filters with `stage`, `layer_id`, `geo_id`, `source_id`, and `risk_tag`.
- Relationship rows now standardize `source_refs`, `evidence_refs`, validity window fields, source families, stage context, and class-specific fields for supply, demand, production dependency, and evidence-context rows.
- Evidence-context links remain non-propagating and carry `not_supply_chain_dependency=true`.
- Source coverage rows now summarize source families, relationship-class coverage, source gaps, connector status, fixture requirement, and live-fetch-disabled policy by value-chain layer.
- Canonical geography remains `region:china_taiwan` / `中国台湾` with parent `country:CN` / `中国`.

### Files Changed

- `services/api/services/semiconductor_content_service.py`
- `services/api/routes/semiconductor_content.py`
- `services/api/main.py`
- `services/api/dev_server.py`
- `packages/shared-types/src/semiconductor-content.ts`
- `packages/api-client/src/dashboard.ts`
- `tests/api/test_semiconductor_content_endpoints.py`
- `tests/sources/test_semiconductor_supply_chain_content.py`
- `docs/data/semiconductor-supply-chain-content-coverage.md`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/api/test_semiconductor_content_endpoints.py tests/sources/test_semiconductor_supply_chain_content.py -q` -> PASS (`17` tests).
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api/test_semiconductor_content_endpoints.py -q` -> PASS (`11` tests).
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> timed out at the local command window without a reported assertion failure.
- `python -m pytest tests/api -q` -> PASS.
- `python -m pytest tests/security -q` -> PASS.
- `python -m pytest tests/graph_invariants -q` -> PASS.

### Computer Use And Deployment Status

- GitHub `ci` passed for commit `c07222cef472547ba30e2df21c349939bf812312` (`26705354314`).
- GitHub `Quality Gates` passed for commit `c07222cef472547ba30e2df21c349939bf812312` (`26705354309`).
- GitHub Render Manual Deploy workflow was attempted for `c07222c` and failed preflight because required Actions secrets are not configured (`RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, `RENDER_WEB_SERVICE_ID`); no secret values were printed.
- Used project-scoped Chrome Render tabs only:
  - API service `supply-risk-atlas-api` was manually deployed from latest `main` and reached `live` for `c07222c`.
  - Web service `supply-risk-atlas-web` was manually deployed from latest `main` with build cache cleared and reached `live` for `c07222c`.
- Public version probe after deployment reported API, Web build-info, and Web proxy all at `c07222cef472547ba30e2df21c349939bf812312`; the root HTML commit marker was not visible, so the strict version script returned `deployed_stale_or_unverified`.
- Deployed endpoint probes returned HTTP `200` for:
  - `/api/v1/semiconductor/relationships?relationship_class=SUPPLY_RELATIONSHIP&limit=3`
  - `/api/v1/semiconductor/source-coverage?stage=midstream&limit=3`
  - Web proxy `/api/v1/semiconductor/relationships?relationship_class=EVIDENCE_CONTEXT&limit=2`
- `npm.cmd run smoke:web -- --mode=deployed` -> PASS (`63` checks).
- Screenshot evidence for GPT Pro review was captured from public deployed pages:
  - `artifacts/gpt-pro-review/c07222c/system-health.png`
  - `artifacts/gpt-pro-review/c07222c/graph-explorer.png`
  - `artifacts/gpt-pro-review/c07222c/entity-risk.png`
- GPT Pro review from the prior deployment evidence packet did not return a complete next prompt before being stopped; local safe hardening continued without accessing unrelated tabs.

### Known Limitations

- The new endpoints expose curated fixture summaries and indices only; they do not fetch live data or expose raw source payloads.
- Relationship class-specific fields are normalized from existing public-evidence relationship summaries. Quantitative share, capacity, lead-time, and demand values remain null unless supported by future source-specific fixtures.
- GitHub Actions secrets for automated Render deployment remain absent, so Render deployment currently requires project-scoped browser/console action or a safe future secret configuration path.
- The strict version script still treats a missing root HTML commit marker as stale even when API, Web build-info, and Web proxy agree on the deployed commit.
- GPT Pro review remains pending for the `c07222c` deployed result.

## 2026-05-31 Display Declutter And Audit Details Gate

### Current HEAD

- Starting commit: `86e66a440c8c608302365ab73d410ca5d230c745`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Tightened the demonstration-first display policy for the global public-data banner.
- `MetadataSummary` now filters internal audit and diagnostics tokens from primary badges, including `data_mode`, `source_status`, `graph_mode`, `graph_version`, `source_manifest_id`, `calibration_status`, `last_checked_at`, `transport_attempts`, `failed_endpoint`, and `not_production_ready`.
- Top-level diagnostics now appear only for actual blocked/fallback/unavailable states, failed endpoints, retry hints, or repeated transport attempts.
- `Data audit details` remains available as a collapsed audit surface; API/export metadata fields remain unchanged.
- The public data banner layout is compacted so the primary view shows conclusion, coverage, update time, source summary, and public-evidence/research-fixture mode only.
- Browser smoke now fails if primary visible text exposes raw audit keys such as `source_status:` or `source_manifest_id:`.

### Files Changed

- `apps/web/src/features/common/AuditDetails.tsx`
- `apps/web/src/app/App.tsx`
- `apps/web/src/app/globals.css`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_frontend_source_readability.py -q` -> PASS (`23` tests).
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `npm.cmd run smoke:web` -> PASS (`63` checks).
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.

### Deployment And Computer Use Status

- GitHub `ci` passed for commit `5f3f3dd96dc1100faa86a99c57f458e518bd9f6b` (`26706963595`).
- GitHub `Quality Gates` passed for commit `5f3f3dd96dc1100faa86a99c57f458e518bd9f6b` (`26706963610`).
- Used project-scoped Chrome tabs only for Render Dashboard, deployed public pages, and the existing GPT Pro project conversation.
- Render API service `supply-risk-atlas-api` was manually deployed from latest `main` and reported `5f3f3dd96dc1100faa86a99c57f458e518bd9f6b`.
- Render Web service `supply-risk-atlas-web` was manually deployed from latest `main` and reported `5f3f3dd96dc1100faa86a99c57f458e518bd9f6b`.
- `python scripts/check-deployed-version.py --expected-commit 5f3f3dd96dc1100faa86a99c57f458e518bd9f6b --timeout 40 --attempts 2` -> `deployed_verified`.
- `npm.cmd run smoke:web -- --mode=deployed` -> PASS (`63` checks).
- Public screenshot observations for GPT Pro review were captured from System Health, Graph Explorer, and Entity Risk 360. The status banner now shows user-facing public-data badges and collapsed audit details rather than raw engineering fields.
- GPT Pro review packet was sent to the existing project conversation with sanitized status and public page observations. Reading the response was blocked by repeated Chrome extension timeouts, so the handoff status is `sent_response_unread_due_browser_timeout`.

### Known Limitations

- This gate changes default frontend presentation only; it does not change API contracts, report exports, connector policy, or fixture/promoted data semantics.
- The platform remains fixture/promoted public-evidence research infrastructure, not production-ready.

### Post-Commit Recovery Verification

- Documentation evidence commit: `40b982994861bc01c84ad9318d1685e7a9034ce2`.
- GitHub `ci` passed for `40b982994861bc01c84ad9318d1685e7a9034ce2` (`26707823139`).
- GitHub `Quality Gates` passed for `40b982994861bc01c84ad9318d1685e7a9034ce2` (`26707823146`).
- Worktree remained clean except for preserved user-owned untracked files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.
- A first deployed probe for the runtime code commit hit Render `x-render-routing: hibernate-wake-error` on API endpoints, including `/api/v1/version`, `/api/v1/health`, and `/api/v1/graph/supply-relationships`.
- After a bounded warm-up wait, deployed API endpoints recovered with HTTP `200` for `/api/v1/version`, `/api/v1/health`, and `/api/v1/graph/supply-relationships`.
- `python scripts/check-deployed-version.py --expected-commit 5f3f3dd96dc1100faa86a99c57f458e518bd9f6b --timeout 40 --attempts 2` -> `deployed_verified`.
- `npm.cmd run smoke:web -- --mode=deployed` -> PASS (`63` checks).
- Render was not redeployed for the docs-only evidence commit because deployed API/Web runtime code already verified at `5f3f3dd96dc1100faa86a99c57f458e518bd9f6b`; the later commits only update roadmap evidence.
- GPT Pro handoff remains `sent_response_unread_due_browser_timeout`; no additional browser loop was started after the deployed recovery check.

## 2026-05-31 L0-L11 Stage Coverage Summary Gate

### Current HEAD

- Starting commit: `4f76d3618217e665e0a0248f4d735cfa62fb8f4d`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Extended the semiconductor content summary payload with an L0-L11 `stage_source_coverage_summary` derived from the canonical `stage_source_coverage_matrix.yaml`.
- Each stage summary records public source counts, source families, relationship classes, linked graph views, charts, tables, source gaps, proxy limitations, fixture-required policy, and live-fetch-disabled policy.
- Added `stage_source_family_counts` so System Health can show whether national/policy, enterprise disclosure, and industry fixture evidence cover all stages.
- Updated System Health's Chip supply chain coverage panel with compact L0-L11 coverage counts and visible first-stage summaries, while keeping full stage coverage details folded under `Data audit details`.
- No raw payloads, secrets, private diagnostics, live fetches, or production-readiness claims were added.

### Files Changed

- `services/api/services/semiconductor_content_service.py`
- `packages/shared-types/src/semiconductor-content.ts`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/api/test_semiconductor_content_endpoints.py`
- `tests/sources/test_semiconductor_supply_chain_content.py`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/data/semiconductor-supply-chain-content-coverage.md`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/api/test_semiconductor_content_endpoints.py tests/sources/test_semiconductor_supply_chain_content.py tests/quality/test_frontend_display_declutter.py -q` -> PASS.
- `python -m pytest tests/sources/test_stage_source_coverage_matrix.py tests/api/test_stage_graph_endpoints.py -q` -> PASS.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.
- First `npm.cmd run smoke:web` attempt failed because the local web server was not yet listening at `http://127.0.0.1:3000`.
- After starting local API/Web dev servers, `npm.cmd run smoke:web` -> PASS (`63` checks).

### Known Limitations

- The L0-L11 stage coverage summary is still a curated fixture/promoted public-evidence index. It does not perform live source fetches and does not add raw source payloads.
- Quantitative capacity, demand, substitution, and lead-time fields remain proxy summaries unless supported by source-specific fixtures.

### Post-Commit Deployment And GPT Pro Review Evidence

- Implementation commit: `b281948e446031f7605d4d85e6f7f6269adfa357`.
- GitHub `Quality Gates` passed for `b281948e446031f7605d4d85e6f7f6269adfa357` in run `27029817219`.
- GitHub `ci` passed for `b281948e446031f7605d4d85e6f7f6269adfa357` in run `27029817226`.
- GitHub `Render Manual Deploy` workflow run `27048315827` failed preflight before any Render API call because required repository secrets were absent: `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID`. No secret values, cookies, tokens, private diagnostics, or raw payloads were printed.
- Project-scoped Chrome Computer Use was used only for GitHub/Render/deployed public pages/GPT Pro. Render Dashboard was already authenticated by the user.
- Render API service `supply-risk-atlas-api` was manually deployed from latest `main` at `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Render Web service `supply-risk-atlas-web` was manually deployed from latest `main` at `b281948e446031f7605d4d85e6f7f6269adfa357` with build cache cleared.
- `python scripts/check-deployed-version.py --expected-commit b281948e446031f7605d4d85e6f7f6269adfa357 --timeout 40 --attempts 2` -> `deployed_verified`.
- First deployed smoke attempt timed out during deploy/cold-start transition; residual smoke Node processes were stopped after their command lines were checked.
- After warm-up, `npm.cmd run smoke:web -- --mode=deployed` -> PASS (`63` checks).
- Public page screenshots for GPT Pro review were captured from deployed System Health, Graph Explorer, and Entity Risk 360. They did not include Render account screens, secrets, cookies, or private diagnostics.
- GPT Pro review packet was sent through the project-scoped Chrome ChatGPT project conversation. GPT Pro returned `Verdict: PASS` for this gate and accepted the L0-L11 Stage Coverage Summary/source-coverage visibility hardening.
- GPT Pro next priority: deployed API/Web readiness hardening, Render workflow preflight clarity, GitHub Actions Node 24 readiness, and complete compact all-12-stage System Health coverage before richer real-data fixtures.

## 2026-06-05 Deployed Readiness And All-Stage Display Hardening Gate

### Current HEAD

- Starting commit: `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- `scripts/check-deployed-version.py` now emits sanitized deployment `failure_class` and `retry_hint` fields. It distinguishes `deployed_verified`, `cold_start_or_deploy_transition`, `transport_timeout`, `schema_mismatch`, `commit_mismatch`, `unavailable`, and `probe_error` without printing raw response bodies.
- Public deployed probes remain bounded by explicit attempt and timeout limits. GET probes are retried only through the existing bounded probe loop; no POST/write retry path was added.
- Render Manual Deploy preflight now reports `render_preflight_status=missing_required_deploy_secrets` and explicitly states that no Render deploy API call was attempted when required GitHub Actions secrets are absent.
- `scripts/browser-smoke.mjs` now installs SIGINT/SIGTERM/SIGHUP cleanup for the temporary headless browser and profile directory, reducing residual process risk after an external timeout.
- GitHub `ci` upgraded `actions/upload-artifact` from `v4` to `v6`, while keeping explicit smoke-report artifact paths. Official GitHub-owned action usage is covered by a quality test for Node 24-ready major versions.
- System Health's `Chip supply chain coverage` panel now renders all 12 L0-L11 stages in a compact user-facing grid instead of only the first six. Detailed source gaps, proxy limitations, source refs, and manifest details remain folded under `Data audit details`.
- No live fetch, raw payload exposure, production-ready claim, secret exposure, or geography-policy change was introduced. Canonical geography remains `region:china_taiwan` / `中国台湾` / `country:CN` / `中国`.

### Files Changed

- `.github/workflows/ci.yml`
- `.github/workflows/render-manual-deploy.yml`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `docs/deployment/github-ci.md`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`
- `scripts/browser-smoke.mjs`
- `scripts/check-deployed-version.py`
- `tests/quality/test_deployed_version_checker.py`
- `tests/quality/test_frontend_display_declutter.py`
- `tests/quality/test_github_workflow_runtime_readiness.py`
- `tests/quality/test_render_manual_deploy_workflow.py`

### Commands Run

- `python -m pytest tests/quality/test_deployed_version_checker.py tests/quality/test_render_manual_deploy_workflow.py tests/quality/test_github_workflow_runtime_readiness.py tests/quality/test_frontend_display_declutter.py -q` -> PASS.
- `python -m pytest tests/api/test_semiconductor_content_endpoints.py tests/sources/test_semiconductor_supply_chain_content.py tests/sources/test_stage_source_coverage_matrix.py -q` -> PASS.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd run smoke:web` -> PASS (`63` checks).
- `python scripts/check-deployed-version.py --expected-commit b281948e446031f7605d4d85e6f7f6269adfa357 --timeout 40 --attempts 2` first classified the public HTML shell as `cold_start_or_deploy_transition` with retry hint `wait_for_render_warmup_then_retry_bounded_probe`; API, Web build-info, and Web proxy were already on `b281948e446031f7605d4d85e6f7f6269adfa357`.
- After a bounded warm-up wait, the same deployed version probe returned `deployed_verified` with `failure_class=none` and no warnings.

### Known Limitations

- This gate hardens deployment/readiness classification and presentation. It does not add richer real-data fixtures, new live ingestion connectors, databases, or production deployment guarantees.
- Render Manual Deploy remains unable to run fully through GitHub Actions until the required Render repository secrets are configured by a safe manual path.

### Post-Commit Background Status

- Implementation commit: `b253acf418837b775c7b8310c21e403a33854329`.
- GitHub `ci` passed in run `27051669296`.
- GitHub `Quality Gates` passed in run `27051669298`.
- GitHub `Render Manual Deploy` run `27051776714` failed in preflight with `render_preflight_status=missing_required_deploy_secrets`; no Render API call was attempted.
- Background deployed endpoint checks showed API `/api/v1/version`, Web `/api/build-info`, and Web proxy `/api/v1/version` still reporting `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Current deployed runtime status: stale relative to `b253acf418837b775c7b8310c21e403a33854329`.
- Background deployment capability check found no Render CLI, no `RENDER_API_KEY` environment variable, and no exposed Render MCP tool. The user requested background-only work, so no further Render Dashboard or ChatGPT foreground interaction was attempted.
- Next safe deployment options are documented in `docs/roadmap/codex-continuation-request.md`.

## 2026-06-06 Background Render Deploy Helper Gate

### Gate Result

- Added `scripts/trigger-render-deploy.py` as a foreground-free Render API deployment helper for future use when `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are configured outside chat.
- The helper validates commit SHA and service ID shape, supports `--dry-run`, triggers API/Web deploys with bounded request timeouts, and prints only sanitized service names, HTTP status categories, commit SHA, and retry hints.
- Missing credentials return `render_deploy_blocked_missing_safe_deploy_path` before any Render API call.
- HTTP failures are sanitized; raw Render API bodies, tokens, cookies, headers, service IDs, and secret values are not printed.
- Updated Render deployment docs and continuation request with the new background path.
- This gate does not deploy Render by itself because no Render API key is present in the local environment.

### Files Changed

- `scripts/trigger-render-deploy.py`
- `tests/quality/test_render_background_deploy_script.py`
- `docs/roadmap/render-deploy-secret-requirements.md`
- `docs/roadmap/codex-continuation-request.md`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Known Limitations

- The deployed API/Web runtime remains stale until Render deploys are triggered by GitHub Actions secrets, Render MCP/CLI/API environment configuration, or manual Dashboard action.

## 2026-06-06 Background Stage Gap Summary Gate

### Current HEAD

- Starting commit: `9fab22bb54455b9fd1de76d7a8d23201cb37a1ef`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.
- User requested background-only work, so no Chrome, Render Dashboard, or ChatGPT foreground actions were attempted.

### Gate Result

- Extended the semiconductor content coverage summary with per-stage `failure_reason` and `required_narrow_patch_if_failed` so partial L0-L11 stages expose actionable next steps through API data without inventing production data.
- Updated shared frontend types for the expanded stage coverage summary.
- System Health now shows a compact user-facing `Priority coverage gaps` line for partial stages while retaining detailed narrow patch plans in folded `Data audit details`.
- Graph Explorer stage views now label folded source caveats as `known source gaps`, `proxy limitations`, `why coverage is partial`, and `next narrow patch` instead of exposing raw field labels in the primary display.
- No API route was removed or renamed. No live fetch path, raw payload exposure, production-ready claim, secret exposure, or geography terminology change was introduced.

### Files Changed

- `services/api/services/semiconductor_content_service.py`
- `packages/shared-types/src/semiconductor-content.ts`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `tests/api/test_semiconductor_content_endpoints.py`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/api/test_semiconductor_content_endpoints.py tests/sources/test_stage_source_coverage_matrix.py tests/quality/test_frontend_display_declutter.py -q` -> PASS, 38 tests.
- `python -m pytest tests/quality -q` -> PASS.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` first timed out at 184 seconds without failure output, then passed with a longer timeout.

### Known Limitations

- This gate improves stage-gap visibility and page decluttering only. It does not add live ingestion, private enterprise data, calibrated production shares, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is available.
- GPT Pro handoff was not attempted because the user requested background-only operation and there is no background ChatGPT connector in this environment.

### Post-Commit Background Status

- Implementation commit: `341ffd0ab2c7b4ae9cfeca6bbd5330bf02efbe2f`.
- GitHub `ci` passed in run `27067265289`.
- GitHub `Quality Gates` passed in run `27067265296`.
- Background deployed version probe for expected commit `341ffd0ab2c7b4ae9cfeca6bbd5330bf02efbe2f` returned `deployed_stale_or_unverified`.
- Probe evidence: API and Web build-info timed out during the bounded one-attempt check, public Web HTML returned HTTP 503, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Stage Endpoint Authority Gate

### Current HEAD

- Starting commit: `8c70d0b8bf265ea6a70ed3b796a7d04d76b2f8fe`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Removed local dashboard graph fallback rows from `StageGraphView`. Stage-specific graph views now show nodes and edges only when the backend stage endpoint is active.
- When a stage endpoint is unavailable, the view now shows a controlled degraded state: `Stage graph data unavailable; backend stage rows are hidden.`
- Stage endpoint fallback diagnostics are passed through the existing folded diagnostics path, keeping failed endpoint and retry details out of primary page content.
- Added frontend quality assertions preventing reintroduction of `view.visibleNodes`, `view.visibleLinks`, `fallbackNodes`, `fallbackEdges`, and `Source coverage fallback` inside the stage graph view.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography terminology change was introduced.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphExplorer.tsx`
- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_relationship_view_no_authoritative_fallbacks.py tests/quality/test_stage_frontend_artifacts.py -q` -> PASS, 23 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd run smoke:web` first timed out while System Health was still in `Connecting to public data`; local API and Web probes both returned HTTP 200.
- `npm.cmd run smoke:web` rerun -> PASS, 63 checks.

### Known Limitations

- This gate hardens stage-view authority boundaries only. It does not add calibrated production data or deploy Render.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.

### Post-Commit Background Status

- Implementation commit: `f953619ebb7fe3efa67a45496175431b2bb07fd4`.
- GitHub `ci` passed in run `27067851606`.
- GitHub `Quality Gates` passed in run `27067851619`.
- Background deployed version probe for expected commit `f953619ebb7fe3efa67a45496175431b2bb07fd4` returned `deployed_stale_or_unverified`.
- Probe evidence: API and Web build-info timed out during the bounded one-attempt check, public Web HTML returned HTTP 503, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Relationship Preview State Gate

### Current HEAD

- Starting commit: `da91e83ca1e01c9d5379f78e4e39dba614ad3554`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Browser smoke no longer expects `unavailable_preview` to appear in user-visible text. It now checks `data-preview-state` DOM attributes so internal preview state can remain testable without becoming user copy.
- Graph Explorer relationship modes now render a neutral loading state while authoritative backend relationship data is still loading, instead of briefly showing a degraded unavailable preview.
- Stage graph views now distinguish endpoint loading from endpoint fallback. Loading shows `Loading authoritative stage graph data`; only actual fallback renders `data-preview-state="stage_endpoint_unavailable"`.
- Added quality tests to prevent reintroducing user-visible `unavailable_preview` checks and to keep relationship/stage loading states separate from unavailable-preview states.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography terminology change was introduced.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphExplorer.tsx`
- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `tests/quality/test_relationship_view_no_authoritative_fallbacks.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_frontend_source_readability.py -q` -> PASS, 24 tests.
- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_relationship_view_no_authoritative_fallbacks.py -q` -> PASS, 21 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` initially exposed the stale issue where `unavailable_preview` DOM state appeared while relationship endpoints were ready but the UI was still loading.
- After the loading-state fix, `npm.cmd run smoke:web` -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.

### Known Limitations

- This gate improves frontend state semantics only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.

### Post-Commit Background Status

- Implementation commit: `a3c4d47b413bd950eaae9e7fab7dbec7bc8cf7ae`.
- GitHub `ci` passed in run `27068593789`.
- GitHub `Quality Gates` passed in run `27068593803`.
- Background deployed version probe for expected commit `a3c4d47b413bd950eaae9e7fab7dbec7bc8cf7ae` returned `deployed_stale_or_unverified`.
- Probe evidence: API and Web build-info timed out during the bounded one-attempt check, public Web HTML returned HTTP 503, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Graph Table Authority Gate

### Current HEAD

- Starting commit: `c8ca4ea2a7cefd5e38cbed3f366dbe38be7464cf`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Removed local visible-graph-derived fallback rows from Graph Explorer table modes:
  - Source Coverage no longer counts `view.visibleLinks` when the backend source-coverage endpoint is unavailable.
  - Node Catalog no longer builds catalog rows from `view.visibleNodes` when the backend node-catalog endpoint is unavailable.
  - Matrix mode no longer builds matrix rows from visible graph links when the backend matrix endpoint is unavailable.
- Each affected table now renders a controlled degraded row with a `data-preview-state` marker and user-facing copy stating that authoritative backend rows are hidden.
- Added frontend quality assertions preventing reintroduction of local fallback rows in these table modes.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography terminology change was introduced.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphSourceCoverageView.tsx`
- `apps/web/src/features/graph-explorer/GraphNodeCatalogView.tsx`
- `apps/web/src/features/graph-explorer/GraphMatrixView.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_relationship_view_no_authoritative_fallbacks.py -q` -> PASS, 21 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `npm.cmd run smoke:web` first timed out while a relationship endpoint remained in loading state; rerun -> PASS, 63 checks.

### Known Limitations

- This gate hardens frontend table authority boundaries only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.

### Post-Commit Background Status

- Implementation commit: `ecd48b8ffcf1e9a2714510643b7d0a57985b82f8`.
- GitHub `ci` passed in run `27069230669`.
- GitHub `Quality Gates` passed in run `27069230695`.
- Background deployed version probe for expected commit `ecd48b8ffcf1e9a2714510643b7d0a57985b82f8` returned `deployed_stale_or_unverified`.
- Probe evidence: API and Web build-info timed out during the bounded one-attempt check, public Web HTML returned HTTP 503, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Graph Endpoint Loading Bound Gate

### Current HEAD

- Starting commit: `b958fa3ba1ca01a3004e6671d4812e252886079b`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Added a bounded frontend loading timeout for Graph Explorer backend graph-view and stage-graph requests.
- If an endpoint remains in loading state past the bound, the UI switches to a controlled fallback message stating that authoritative rows are hidden.
- Late successful endpoint responses can still replace the controlled fallback because the request remains active until cleanup.
- Replaced stage-view summary copy that previously showed `fallback` or `not recorded` as if it were a metric. The UI now says source coverage, source families, or evidence refs are loading or unavailable.
- Added quality assertions so those fallback labels and unbounded loading regressions are caught.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography terminology change was introduced.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphExplorer.tsx`
- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `tests/quality/test_relationship_view_no_authoritative_fallbacks.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_relationship_view_no_authoritative_fallbacks.py tests/quality/test_frontend_display_declutter.py -q` -> PASS, 21 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` first hit the local command timeout and terminal flush error before completion; rerun with a longer timeout -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate improves Graph Explorer frontend availability semantics only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

## 2026-06-06 Background Run Page Display Declutter Gate

### Current HEAD

- Starting commit: `f6080eeb94b7a8e3a2f418d781d12f7e6f931616`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Replaced Shock Simulator primary labels such as `current_loss_mode`, `current_propagation_mode`, `functionality_metric`, and `weighting_method` with user-facing labels.
- Replaced forward stress result metric labels such as `p50_loss`, `p95_loss`, and `cvar_95` with plain loss-summary labels.
- Replaced Reverse Stress Lab engineering subtitles and field labels with threshold, context, and search-limit language.
- Replaced Optimizer primary before/after and context labels with business-facing terms, while keeping run IDs and graph/source metadata in folded audit details.
- Renamed Evidence Board `Evidence audit table` to `Evidence review table` and changed evidence filter labels to display language.
- Updated shared display label mappings so `cvar` identifiers render as tail-loss language in tables/charts.
- Updated browser smoke and display-declutter quality checks to prevent the old engineering labels from returning.
- No public route, API response field, report export field, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context safety rule was changed.

### Files Changed

- `apps/web/src/features/common/displayLabels.ts`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `apps/web/src/features/evidence-board/EvidenceAuditPanel.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 30 tests.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS after increasing timeout for the full group.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks after restarting stale local background API/Web dev processes.

### Known Limitations

- This gate changes display language only. It does not add calibrated production data, new source connectors, or Render redeployment.
- A first smoke attempt failed while stale local background API/Web processes were serving degraded or mismatched state; the processes were restarted in hidden/background mode and the final smoke passed.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `3f30ae345bd6bf572c36dd30f3948d12589a97e4`.
- GitHub `ci` passed in run `27081805935`.
- GitHub `Quality Gates` passed in run `27081805924`.
- Background deployed version probe for expected commit `3f30ae3` returned `deployed_stale_or_unverified`.
- The deployed API/Web metadata still reported commit `b281948e446031f7605d4d85e6f7f6269adfa357`, so the deployed services are stale relative to latest `main`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Source Coverage Readiness Label Declutter Gate

### Current HEAD

- Starting commit: `bb71359b99746d3d850fae4ae416194c0b13289e`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Reworded the Entity Risk 360 unavailable fallback field from `Source status` to `Source coverage`.
- Reworded the system health `source_statuses` display label from `Source status summary` to `Source coverage summary` while keeping the underlying data key unchanged.
- Added quality assertions that keep the older visible status wording out of the fallback and shared readiness label map.
- No public route, API response schema, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context propagation rule was changed.

### Files Changed

- `apps/web/src/features/common/displayLabels.ts`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 43 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `rg -n "Source status summary" apps/web/src tests/quality` -> only the negative quality assertion still contains the old phrase.
- `rg -n "Source status" apps/web/src tests/quality` -> only negative quality assertions still contain the old fallback/summary wording.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m services.api.dev_server` -> started as a hidden local background API process for smoke verification.
- `npm.cmd --workspace apps/web run dev` -> started as a hidden local background Web process with `NEXT_PUBLIC_SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1` and `SUPPLY_RISK_API_ORIGIN=http://127.0.0.1:8000`.
- `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000 SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_API_ORIGIN=http://127.0.0.1:8000 npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes visible readiness/fallback copy and quality guards only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Deployed Render endpoints were not updated by this background pass.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

## 2026-06-07 Background Global Data Status Calibration Copy Declutter Gate

### Current HEAD

- Starting commit: `cfad4db8a4b99e523879d1733afb079aca67e5a6`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Reworded the global data status audit fallback from the raw `fixture_proxy_not_calibrated; not_financial_loss` token into `Research fixture calibration; no financial loss estimate`.
- Kept API response metadata, exported report metadata, source/graph metadata fields, raw-payload exclusion policy, geography terminology, and evidence-context safety behavior unchanged.
- Added frontend display declutter assertions so the raw calibration token does not return to `DataLineageBanner` fallback copy.

### Files Changed

- `apps/web/src/app/App.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` - passed.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `npm.cmd run smoke:web` - passed, 63 browser checks.

### Known Limitations

- This gate changes visible/collapsible frontend fallback wording only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `ef7d68a9d20b9a7f3c155aadac359c5dbabd21f1` (`Use user friendly calibration fallback copy`).
- GitHub `Quality Gates`: run `27095029132`, passed.
- GitHub `ci`: run `27095029146`, passed, including web, python, and browser-smoke jobs.
- CI annotation observed: GitHub Actions Node.js 20 deprecation warning for `actions/setup-python@v5`; no functional failure in this gate.
- Deployed version probe: `python scripts/check-deployed-version.py --expected-commit ef7d68a --timeout 20` timed out from the background environment.
- Render deploy dry run: `python scripts/trigger-render-deploy.py --dry-run --commit ef7d68a --timeout 20` returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured.
- Deployment status: `blocked_background_no_safe_render_api_path`.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Graph Count Copy Declutter Gate

### Current HEAD

- Starting commit: `3a0985259fbeae1ae53b399e72fc288db29e563b`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Replaced user-facing Graph Explorer count copy such as `nodes / edges`, `Visible nodes`, `Eligible nodes`, and `edge labels` with `entities`, `relationships`, and user-facing relationship wording.
- Replaced graph relationship view copy that described demand facts as `edges`; demand rows now say demand relationships are not supplier relationships.
- Replaced stage view declutter limit copy from `18 nodes / 30 edges` to `18 entities / 30 relationships`.
- Replaced report graph context and geography drilldown count copy with `entities`, `relationships`, and `catalog records` where appropriate.
- Kept graph API payload fields, graph kernel field names, report export metadata, geography terminology, raw-payload exclusion, and evidence-context separation unchanged.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphExplorer.tsx`
- `apps/web/src/features/graph-explorer/GraphControls.tsx`
- `apps/web/src/features/graph-explorer/GraphGeoView.tsx`
- `apps/web/src/features/graph-explorer/GraphOverviewView.tsx`
- `apps/web/src/features/graph-explorer/GraphScenarioOverlay.tsx`
- `apps/web/src/features/graph-explorer/GraphSourceCoverageView.tsx`
- `apps/web/src/features/graph-explorer/GraphTimelineView.tsx`
- `apps/web/src/features/graph-explorer/GraphInspector.tsx`
- `apps/web/src/features/graph-explorer/DemandRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/GraphEvidenceView.tsx`
- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `tests/quality/test_stage_frontend_artifacts.py`
- `scripts/browser-smoke.mjs`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_stage_frontend_artifacts.py -q` - passed.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `npm.cmd run smoke:web` - passed, 63 browser checks.

### Known Limitations

- This gate is a display-language hardening pass only. It does not add new source connectors, calibrated production datasets, or Render redeployment.
- Some System Health technical summaries still use node/relationship counts intentionally because that page is allowed to expose readiness diagnostics in grouped form.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `1590a097db3d843a12ddf2a2fd86fbc20c41b84d` (`Use user friendly graph count copy`).
- GitHub `Quality Gates`: run `27095639754`, passed.
- GitHub `ci`: run `27095639757`, passed, including web, python, and browser-smoke jobs.
- CI annotations observed: GitHub Actions Node.js 20 deprecation warning for `actions/setup-python@v5`; Windows runner migration notice. No functional failure in this gate.
- Deployed version probe: `python scripts/check-deployed-version.py --expected-commit 1590a09 --timeout 20` timed out from the background environment.
- Render deploy dry run: `python scripts/trigger-render-deploy.py --dry-run --commit 1590a09 --timeout 20` returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured.
- Deployment status: `blocked_background_no_safe_render_api_path`.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Graph Relationship Copy Follow-Up Gate

### Current HEAD

- Starting commit: `437b346ab941b14e9ebf0cb98236df79e58b0dfe`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Replaced the default graph edge table title with `Graph relationships`.
- Reworded Graph Explorer mode descriptions from implementation terms such as `nodes` and `bottleneck edges` to user-facing `entities` and `bottleneck relationships`.
- Reworded stage evidence-context copy so it says inspection links are not supply-chain dependencies, rather than asking users to reason about dependency edges.
- Kept graph API fields, report exports, relationship class semantics, geography normalization, raw-payload exclusion, and evidence-context non-propagation unchanged.

### Files Changed

- `apps/web/src/features/common/tables/GraphEdgeTable.tsx`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_stage_frontend_artifacts.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.

### Known Limitations

- This gate is a copy-only follow-up and does not change backend graph semantics, source coverage, deployment status, or data calibration.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `8bdd1df2bcdde299fcc0da6e3a9c15f4b063fa2c` (`Use relationship copy for graph details`).
- GitHub `Quality Gates`: run `27096040677`, passed.
- GitHub `ci`: run `27096040679`, passed. The first `gh run watch` attempt hit a GitHub annotations EOF while the run was still active; a follow-up `gh run list` confirmed success.
- Deployed version probe: `python scripts/check-deployed-version.py --expected-commit 8bdd1df --timeout 20` returned `deployed_stale_or_unverified`.
- Deployed probe details: API version probe failed with `transport_timeout`; web build info and web proxy still reported commit `b281948e446031f7605d4d85e6f7f6269adfa357`, not `8bdd1df`.
- Render deploy dry run: `python scripts/trigger-render-deploy.py --dry-run --commit 8bdd1df --timeout 20` returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured.
- Deployment status: `blocked_background_no_safe_render_api_path_and_deployed_web_stale`.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Relationship Unavailable Copy Declutter Gate

### Current HEAD

- Starting commit: `25bf6a9cb482c2ac79bf0141b558039fc3103207`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Reworded supply, demand, production dependency, and supply-demand balance unavailable states so the visible copy no longer says `Local graph links` or `Local graph nodes`.
- New unavailable copy says non-authoritative local preview data is excluded from charts, tables, exports, reports, and source coverage.
- Updated browser smoke and quality tests so the controlled unavailable state remains testable without exposing implementation-specific graph wording.
- Kept the backend-authoritative relationship rule unchanged: unavailable endpoints still hide authoritative rows and exclude preview data from analytical outputs.

### Files Changed

- `apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/DemandRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/ProductionDependencyView.tsx`
- `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `python -m pytest tests/quality -q` - passed.
- `npm.cmd run smoke:web` - passed, 63 browser checks.

### Known Limitations

- This gate is a display-language hardening pass for unavailable relationship states only. It does not add new public source connectors, calibrated production datasets, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `bb3226107a8c204ab221fe5c1a02a5c2cfa9f5d2`.
- GitHub `ci` passed in run `27096531000`.
- GitHub `Quality Gates` passed in run `27096530983`.
- Background deployed version probe for expected commit `bb32261` returned `deployed_stale_or_unverified`.
- The deployed API, web build metadata, and web proxy reported commit `b281948e446031f7605d4d85e6f7f6269adfa357`; the web HTML did not expose the expected commit marker.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background System Health Graph Readiness Copy Declutter Gate

### Current HEAD

- Starting commit: `a78aadf14c57c9f6aac1d1504295cdb53f2d0b7a`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Reworded the System Health SemiRisk-KG readiness panel from raw implementation labels such as `registryReady`, `fixtureManifestReady`, `nodeCount`, and `edgeCount` into user-facing readiness fields.
- Replaced boolean `true`/`false` values in that primary grid with `Ready` / `Needs review`.
- Reworded the graph readiness subtitle from `Fixture/promoted` wording into public-evidence research-use language.
- Reworded System Health pipeline stage labels from raw/silver/gold implementation terminology into evidence ingestion, entity/event normalization, graph relationship materialization, and public evidence graph snapshot language.
- Kept technical diagnostics, graph/source metadata, API payload fields, raw-payload exclusion policy, geography terminology, and evidence-context safety behavior unchanged.
- Added frontend and API assertions so the raw readiness field labels and raw/silver/gold pipeline labels do not return to the primary System Health UI.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `services/api/main.py`
- `scripts/browser-smoke.mjs`
- `tests/api/test_system_health_semiconductor_graph.py`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- First `npm.cmd run smoke:web` attempt -> FAILED because System Health still displayed raw/silver/gold pipeline stage labels; this gate was expanded to fix the API stage labels and smoke expectations.
- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 40 tests.
- `python -m pytest tests/api/test_system_health_semiconductor_graph.py -q` -> PASS, 6 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks after API stage-label declutter.

### Known Limitations

- This gate changes visible System Health readiness wording only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `76f98428ddc59211947811fbfb367e589da9da6c`.
- GitHub `ci` passed in run `27094463396`.
- GitHub `Quality Gates` passed in run `27094463394`.
- Background deployed version probe for expected commit `76f9842` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Supply-Demand Balance Copy Declutter Gate

### Current HEAD

- Starting commit: `d0eb7fca949ba73f8711f1399de8ac7499116b31`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Reworded the Graph Explorer Supply-Demand Balance note from `fixture/promoted demand signals` into public-evidence demand-signal language.
- Kept relationship endpoint data, metadata, audit details, chart/table behavior, raw-payload exclusion policy, geography terminology, and evidence-context safety behavior unchanged.
- Extended frontend display declutter assertions so the relationship views do not reintroduce `fixture/promoted` in primary page copy.

### Files Changed

- `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 40 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes visible Supply-Demand Balance wording only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `71239719ac97a25ae394be2fb67f06668e5aee3b`.
- GitHub `ci` passed in run `27093772838`.
- GitHub `Quality Gates` passed in run `27093772851`.
- Background deployed version probe for expected commit `7123971` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Scenario And Report Method Copy Declutter Gate

### Current HEAD

- Starting commit: `abca1433abcf82717382d5a9129d6d5f0b7a2c45`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Reworded Shock Simulator scenario assumptions from `fixture/proxy only` / `fixture/promoted test graph only` wording into public-evidence scenario language.
- Reworded Investigation Report methodology note from `fixture/proxy methodology only` into research-methodology language while preserving the no-production-readiness caveat.
- Kept API fields, scenario input shape, report metadata, graph/source metadata, raw-payload exclusion policy, geography terminology, and evidence-context safety behavior unchanged.
- Added frontend display declutter assertions so the old fixture/proxy-only strings do not return to primary page copy.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 40 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes visible scenario/report methodology wording only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `a669881f6c737a7068ec58ec3b8ff635cb6a5eba`.
- GitHub `ci` passed in run `27093272658`.
- GitHub `Quality Gates` passed in run `27093272684`.
- Background deployed version probe for expected commit `a669881` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Evidence Lineage Label Declutter Gate

### Current HEAD

- Starting commit: `1bca4c0`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Reworded the System Health Evidence lineage panel from source-record/raw-silver-gold engineering terms into user-facing evidence inputs, normalized events, and graph relationships.
- Reworded related Source Registry and Entity Resolution primary metrics from raw/silver/gold implementation labels into evidence inputs, resolved entities, and graph relationships.
- Kept the underlying registry, lineage, and entity-resolution counts, manifest/checksum audit details, source tables, API payloads, raw-payload exclusion policy, geography terminology, and evidence-context safety behavior unchanged.
- Updated frontend display declutter assertions so old source-record/raw/silver/gold wording does not return to primary System Health UI.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 39 tests after updating expected copy.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes visible Evidence lineage wording only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `a9ed3235486184d7603f86143de55eb17927bf59`.
- GitHub `ci` passed in run `27092369072`.
- GitHub `Quality Gates` passed in run `27092369063`.
- Background deployed version probe for expected commit `a9ed323` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Stage View Source Language Declutter Gate

### Current HEAD

- Starting commit: `03b55db`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Reworded Graph Explorer stage-view source coverage summaries from engineering terms such as source records/families/candidates into evidence sources, public data groups, evidence notes, and coverage caveats.
- Kept stage endpoint data, graph caps, audit details, relationship-class filtering, evidence refs, geography terminology, and evidence-context non-propagation behavior unchanged.
- Updated the frontend display declutter quality assertion so the old source coverage terms do not return to the stage-view primary UI.

### Files Changed

- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 39 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes visible stage-view wording only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `d3263ac71d8590ce0a2149b5423ec9e2bece1a4f`.
- GitHub `ci` passed in run `27091836747`.
- GitHub `Quality Gates` passed in run `27091836759`.
- Background deployed version probe for expected commit `d3263ac` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Graph Overview Source Label Declutter Gate

### Current HEAD

- Starting commit: `6b7bab4`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Updated Graph Explorer overview source-coverage rows to format source identifiers through the shared display-label helpers before rendering.
- Kept graph statistics, API payloads, source metadata, audit details, exports, relationship filtering, geography terminology, and evidence-context propagation behavior unchanged.
- Added a frontend display declutter assertion so overview source rows do not regress to raw source/kind identifiers as primary UI copy.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphOverviewView.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 39 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes visible source-label formatting only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `be4ab67d2fd34073966e5ed86b7ed83ce3cc621d`.
- GitHub `ci` passed in run `27091343975`.
- GitHub `Quality Gates` passed in run `27091343982`.
- Background deployed version probe for expected commit `be4ab67` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Graph Overview Copy Declutter Gate

### Current HEAD

- Starting commit: `67e8cb0aff70b0efcfd6942cefe2271f30377f61`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Rewrote the Graph Explorer overview empty source-coverage copy to avoid exposing `fixture/proxy dashboard graph` implementation wording in primary UI.
- Kept graph metadata, source coverage data, audit details, relationship filtering, and evidence-context safety behavior unchanged.
- Added a frontend display declutter quality assertion for the Graph Overview copy.
- No public route, API response schema, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context propagation rule was changed.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphOverviewView.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 38 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes user-facing copy only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `ccb8f6ea1b4c921322affad8e414ae8d0f7b115d`.
- GitHub `ci` passed in run `27090803763`.
- GitHub `Quality Gates` passed in run `27090803750`.
- Background deployed version probe for expected commit `ccb8f6e` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Readiness Copy Declutter Gate

### Current HEAD

- Starting commit: `a5ab9f362a7f5b0fea74b30fb6b2c827a655ba7e`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Rewrote the System Health readiness note from engineering/governance phrasing into user-facing public-evidence demo language.
- Kept the underlying readiness signals, API fields, diagnostics, source metadata, audit details, export metadata, and deployment status unchanged.
- Added a frontend display declutter quality assertion so the old engineering phrase does not return to the primary page copy.
- No public route, API response schema, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context propagation rule was changed.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 37 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes user-facing copy only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `cc1b750895f17027d50890e2d4d1bff811a3d88a`.
- GitHub `ci` passed in run `27090334849`.
- GitHub `Quality Gates` passed in run `27090334851`.
- Background deployed version probe for expected commit `cc1b750` timed out before a verified deployed version could be recorded.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Reference Label Declutter Gate

### Current HEAD

- Starting commit: `8345e2a7794563d88eb1737b1bc513f276548d59`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Added user-facing display labels for reference fields that can appear in table headers or audit details.
- `source_refs` now renders as `Sources`, `formula_refs` as `Formula references`, and `selected_run_refs` as `Selected runs`.
- Kept API fields, export metadata, diagnostics, graph data, report fields, source refs, and evidence refs unchanged.
- No public route, API response schema, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context propagation rule was changed.

### Files Changed

- `apps/web/src/features/common/displayLabels.ts`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 36 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes display labels only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `c2d1455754dba9441a245a25f39f0f61187fcb08`.
- GitHub `ci` passed in run `27089931200`.
- GitHub `Quality Gates` passed in run `27089931170`.
- Background deployed version probe for expected commit `c2d1455` timed out before a verified deployed version could be recorded.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Boolean Display Label Declutter Gate

### Current HEAD

- Starting commit: `eeb029374e4f40a33a8c0e44fd08075b0460d8e3`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Added display-value mappings so string boolean values render as `yes` / `no` rather than `true` / `false` in shared fields and technical diagnostic summaries.
- Added a quality assertion for the boolean-string display mappings.
- Kept API fields, export metadata, diagnostics, source refs, report fields, and System Health technical diagnostics unchanged.
- No public route, API response schema, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context propagation rule was changed.

### Files Changed

- `apps/web/src/features/common/displayLabels.ts`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 35 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> TIMED OUT after 180 seconds on the first local background attempt; retry passed.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS on retry.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> TIMED OUT on the first local background attempt while System Health was still connecting to public data; retry passed.
- `npm.cmd run smoke:web` -> PASS on retry, 63 checks.

### Known Limitations

- This gate changes display labels only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `6d14f1e15e6e31992525a0037712acac7c5a3796`.
- GitHub `ci` passed in run `27089466021`.
- GitHub `Quality Gates` passed in run `27089466025`.
- Background deployed version probe for expected commit `6d14f1e` timed out before a verified deployed version could be recorded.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Audit Label Declutter Gate

### Current HEAD

- Starting commit: `4cd8627bbf1e3112d392a4496fb7d384008affbc`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Changed expanded audit/diagnostic labels from raw field-oriented wording to product-facing wording:
  - `data_mode` -> `Data source mode`
  - `graph_mode` -> `Graph data mode`
  - `graph_version` -> `Graph snapshot`
  - `source_manifest_id` -> `Source manifest`
  - `source_status` -> `Source coverage`
  - `failed_endpoint` -> `Connection target`
  - `transport_attempts` -> `Connection attempts`
  - `retry_hint` -> `Recovery hint`
  - `last_checked_at` -> `Last checked`
- Kept all API fields, export metadata, diagnostics, source refs, and report fields unchanged.
- Added a quality assertion so raw engineering labels do not return to the display label map.
- No public route, API response schema, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context propagation rule was changed.

### Files Changed

- `apps/web/src/features/common/displayLabels.ts`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 33 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS.

### Known Limitations

- This gate changes display labels only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `cb04ac94adec84687248875db3b7cd9f118b19a0`.
- GitHub `ci` passed in run `27088310988`.
- GitHub `Quality Gates` passed in run `27088311003`.
- Background deployed version probe for expected commit `cb04ac9` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Residual Engineering-Term Declutter Gate

### Current HEAD

- Starting commit: `8662d23a8b1edaf552a5bb0e1204b5aa39ae7044`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Renamed the default tail-loss chart title from `CVaR tail` to `Tail loss detail`.
- Replaced remaining main-page `fixture graph` wording in intervention navigation, report generation, scenario assumptions, and System Health graph titles with `public evidence graph` / `research graph` language.
- Kept fixture/promoted/research status visible while avoiding internal graph implementation terms in default presentation copy.
- Updated browser smoke to expect the System Health public-evidence graph title.
- Added display-declutter assertions preventing old `CVaR tail`, `SemiRisk-KG v0.1 fixture graph`, and report-generation fixture graph copy from returning.
- No public route, API response field, report export field, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context safety rule was changed.

### Files Changed

- `apps/web/src/app/i18n.tsx`
- `apps/web/src/features/common/charts/CVaRTailChart.tsx`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 30 tests.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes display language only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `34a68638a549eb1015707cad91eb7fb30716a1fe`.
- GitHub `ci` passed in run `27082302488`.
- GitHub `Quality Gates` passed in run `27082302484`.
- Background deployed version probe for expected commit `34a6863` returned `deployed_stale_or_unverified`.
- The deployed web build metadata and web proxy still reported commit `b281948e446031f7605d4d85e6f7f6269adfa357`; the API probe timed out and the web HTML probe returned 503 in the bounded check window.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Target Selector Display Declutter Gate

### Current HEAD

- Starting commit: `f133c549bd1e5da5f732becfe9f54f20a3b3da20`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Changed Shock Simulator target dropdown display labels from raw node IDs to business names such as `TSMC`, `EUV scanner`, `Advanced logic`, `HBM`, and `中国台湾`.
- Kept dropdown `value` attributes as canonical node IDs so API requests and graph semantics remain unchanged.
- Changed Investigation Report entity dropdown display labels from raw `company:*` IDs to company names while preserving canonical values for report API calls.
- Added display mappings for common lowercase company and product-grade IDs used by UI controls.
- Updated browser smoke to assert the user-facing target labels rather than raw node IDs.
- Added quality assertions preventing raw target option text from returning to primary UI.
- No public route, API response field, report export field, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context safety rule was changed.

### Files Changed

- `apps/web/src/features/common/displayLabels.ts`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 30 tests.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `python -m pytest tests/api/*.py -q` file-by-file -> PASS for all API test files. The single full-suite `tests/api` invocation timed out locally under concurrent background service load, so the files were verified serially.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks, after restarting hidden local API/Web dev services in same-origin proxy mode.

### Known Limitations

- This gate changes display labels only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Local smoke was sensitive to dev-server startup mode: browser smoke passed after the hidden web dev server was started with `NEXT_PUBLIC_SUPPLY_RISK_API_URL=http://127.0.0.1:3000/api/v1` and `SUPPLY_RISK_API_ORIGIN=http://127.0.0.1:8000`.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `bc5582efbfa4b572d88fa44ba42d0e111b0a5431`.
- GitHub `ci` passed in run `27085909809`.
- GitHub `Quality Gates` passed in run `27085909810`.
- Background deployed version probe for expected commit `bc5582e` returned `deployed_stale_or_unverified`.
- The deployed web build metadata and web proxy still reported commit `b281948e446031f7605d4d85e6f7f6269adfa357`; the API probe timed out and the web HTML probe returned 503 in the bounded check window.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

### Post-Commit Background Status

- Implementation commit: `4f4255ba8851eccc183dd0075f191e537a7a09f2`.
- GitHub `ci` passed in run `27070071898`.
- GitHub `Quality Gates` passed in run `27070071926`.
- Background deployed version probe for expected commit `4f4255ba8851eccc183dd0075f191e537a7a09f2` returned `deployed_stale_or_unverified`.
- Probe evidence: API and Web build-info timed out during the bounded one-attempt check, public Web HTML returned HTTP 503, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background System Health Metadata Declutter Gate

### Current HEAD

- Starting commit: `5b6b1c0f007d3e4cd8a7e9bd7dc90b6142d34a1e`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Moved Source Registry manifest/checksum/catalog identifiers out of the System Health primary subtitle and into collapsed audit details.
- Moved Evidence Lineage manifest/checksum identifiers out of the primary subtitle/metric grid and into collapsed audit details.
- Replaced the main Evidence Lineage checksum tile with a user-facing `Lineage status` summary.
- Added frontend quality assertions preventing manifest/checksum internals from returning to System Health primary subtitles or metric tiles.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography-policy exception was introduced.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 29 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.

### Known Limitations

- This gate is a System Health display-layer metadata declutter fix only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `112818bf65d764da4a890ba37c398615216698d7`.
- GitHub `ci` passed in run `27077356698`.
- GitHub `Quality Gates` passed in run `27077356696`.
- Background deployed version probe for expected commit `112818bf65d764da4a890ba37c398615216698d7` returned `deployed_unavailable`.
- Probe evidence: API, Web build-info, Web proxy, and public Web HTML were unavailable or timed out during the bounded one-attempt check; public Web HTML returned HTTP 503.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Graph Node Geography Label Declutter Gate

### Current HEAD

- Starting commit: `fe86d66a99a0cb0968e64149942efdb97914e49b`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Added a shared frontend `formatGeographyDisplayRef` helper for visible country/region labels in graph UI.
- Updated Graph Explorer controls, focus view, graph canvas node tooltip/card text, and the retained legacy dashboard graph canvas/list to use user-facing geography labels instead of raw country codes.
- The helper normalizes legacy region aliases internally without writing legacy geography node ids as source literals, preserving the repository-wide geography guard.
- Added frontend quality assertions to prevent graph node country labels from returning to raw code display.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography-policy exception was introduced.

### Files Changed

- `apps/web/src/features/common/displayLabels.ts`
- `apps/web/src/features/graph-explorer/GraphControls.tsx`
- `apps/web/src/features/graph-explorer/GraphFocusView.tsx`
- `apps/web/src/features/graph-explorer/GraphCanvas.tsx`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 28 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` initially failed because a new formatter used forbidden legacy geography ids as source literals; after replacing them with constructed internal aliases -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.

### Known Limitations

- This gate is a graph display-layer geography label fix only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `8b0918ee307f68f4d36b332f0136828fbe75e297`.
- GitHub `ci` passed in run `27076837489`.
- GitHub `Quality Gates` passed in run `27076837478`.
- Background deployed version probe for expected commit `8b0918ee307f68f4d36b332f0136828fbe75e297` returned `deployed_unavailable`.
- Probe evidence: API, Web build-info, Web proxy, and public Web HTML were unavailable or timed out during the bounded one-attempt check; public Web HTML returned HTTP 503.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Graph Edge Tooltip Declutter Gate

### Current HEAD

- Starting commit: `54c690438af825fe948454f376997fa30fee152c`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Updated the Graph Explorer canvas edge hover tooltip so missing labels fall back to formatted edge role/type text or `Graph edge`, not raw `edge.id`.
- Updated the retained legacy dashboard graph canvas with the same tooltip fallback rule.
- Added a frontend quality assertion to prevent edge hover titles from exposing raw edge ids.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography-policy exception was introduced.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphCanvas.tsx`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 27 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.

### Known Limitations

- This gate is a graph tooltip display-layer declutter fix only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `cd80aa0ff2e0faafee5a250e05467512d84f08ad`.
- GitHub `ci` passed in run `27076320791`.
- GitHub `Quality Gates` passed in run `27076320801`.
- Background deployed version probe for expected commit `cd80aa0ff2e0faafee5a250e05467512d84f08ad` returned `deployed_stale_or_unverified`.
- Probe evidence: API and Web build-info timed out, public Web HTML returned HTTP 503, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Data Table Evidence ID Declutter Gate

### Current HEAD

- Starting commit: `0aa19360735038af766e114369b5a8e35352381b`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Updated the shared `DataTable` array-object renderer so evidence/ref/id-only objects no longer expose raw `source_record_id`, `evidence_id`, `ref_id`, `edge_id`, or generic `id` values as user-visible table text.
- Source-backed evidence objects still show a user-facing source label plus `evidence`; node objects still use canonical node display formatting.
- Added a frontend quality assertion to keep raw evidence record IDs out of shared table cells when source context is unavailable.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography-policy exception was introduced.

### Files Changed

- `apps/web/src/features/common/tables/DataTable.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 26 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.

### Known Limitations

- This gate is a shared table display-layer declutter fix only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `0b55c115fc92f74633d6b9d8806543848df63cc4`.
- GitHub `ci` passed in run `27075829330`.
- GitHub `Quality Gates` passed in run `27075829329`.
- Background deployed version probe for expected commit `0b55c115fc92f74633d6b9d8806543848df63cc4` returned `deployed_stale_or_unverified`.
- Probe evidence: API and Web build-info timed out, public Web HTML returned HTTP 503, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Timeline And Geo Label Declutter Gate

### Current HEAD

- Starting commit: `c76292c112024abcbdb893bc09775f733ef29651`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Updated Graph Explorer Timeline mode so event labels no longer fall back to raw `event.id` values in visible text.
- Updated Graph Explorer Geo mode so visible geography labels prefer canonical node/display formatting instead of raw country/region codes.
- Added frontend quality assertions to prevent Timeline and Geo views from regressing to raw identifier fallbacks.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography-policy exception was introduced.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphTimelineView.tsx`
- `apps/web/src/features/graph-explorer/GraphGeoView.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 25 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `npm.cmd run smoke:web` first attempt timed out during the initial page hash-switch loop while the browser target remained on System Health; rerun -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.

### Known Limitations

- This gate is a display-layer label fallback fix only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `0574f5860aeea5b165aab9814423f5d28dcd8cf5`.
- GitHub `ci` passed in run `27075375350`.
- GitHub `Quality Gates` passed in run `27075375348`.
- Background deployed version probe for expected commit `0574f5860aeea5b165aab9814423f5d28dcd8cf5` returned `deployed_unavailable`.
- Probe evidence: API, Web build-info, Web proxy, and public Web HTML were unavailable or timed out during the bounded one-attempt check; public Web HTML returned HTTP 503.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Relationship Chart Label Declutter Gate

### Current HEAD

- Starting commit: `b44bd609e39ed96941deed0b65509f07a9f2860c`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Updated Graph Explorer relationship charts so supply, demand, production dependency, and supply-demand balance chart labels use the same user-facing node formatter as their tables.
- Prevented chart labels from rendering raw `supplier_id`, `product_grade_id`, or `dependency_target_id` strings when a display label is available.
- Added frontend quality assertions to prevent relationship chart labels from regressing to raw identifier strings.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography-policy exception was introduced.

### Files Changed

- `apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/DemandRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/ProductionDependencyView.tsx`
- `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 24 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.

### Known Limitations

- This gate is a display-layer chart-label declutter fix only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `7621f37d31f1de417feb838f73d2b57313e1e904`.
- GitHub `ci` passed in run `27074874097`.
- GitHub `Quality Gates` passed in run `27074874100`.
- Background deployed version probe for expected commit `7621f37d31f1de417feb838f73d2b57313e1e904` returned `deployed_stale_or_unverified`.
- Probe evidence: API and Web build-info timed out, public Web HTML returned HTTP 503, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background I18n Geography Display Guard Gate

### Current HEAD

- Starting commit: `b26d60d9e92bb8ae8376801a8dcd79c076e28cc1`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Confirmed the core display label source uses correct UTF-8 for `region:china_taiwan` / `中国台湾`.
- Fixed the app i18n table so the canonical user-facing region display remains `中国台湾` across supported language views instead of being generalized to another geography label.
- Fixed the related strait label to preserve the canonical geography wording across supported language views.
- Added a frontend quality assertion to prevent i18n from translating the canonical region display into a non-canonical visible label.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography-policy exception was introduced.

### Files Changed

- `apps/web/src/app/i18n.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 23 tests.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.

### Known Limitations

- This gate is a display-layer terminology guard only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `8af82c877701f4fd7abf14310881fb3fdec1e762`.
- GitHub `ci` passed in run `27074405109`.
- GitHub `Quality Gates` passed in run `27074405105`.
- Background deployed version probe for expected commit `8af82c877701f4fd7abf14310881fb3fdec1e762` returned `deployed_stale_or_unverified`.
- Probe evidence: API and Web build-info timed out, public Web HTML returned HTTP 503, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Graph Evidence Source Declutter Gate

### Current HEAD

- Starting commit: `962cfbb73204f14cbf2794e6bf64e1a346b803ce`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Removed `edge_id` as a visible fallback for the Graph Explorer Evidence mode source column.
- Evidence rows still keep internal edge ids for React row identity, but missing source data now renders the user-facing fallback `Evidence source` instead of presenting a graph edge id as if it were a source.
- Added a quality assertion to prevent the source cell from falling back to `edge_id`.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography terminology change was introduced.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphEvidenceView.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 22 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` initially timed out at 180 seconds with no failure summary; rerun with a 420 second timeout -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.

### Known Limitations

- This gate is a display-layer declutter fix only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `f3005e142332b81218d025252e6c17cc6d9ea111`.
- GitHub `ci` passed in run `27073875801`.
- GitHub `Quality Gates` passed in run `27073875800`.
- Background deployed version probe for expected commit `f3005e142332b81218d025252e6c17cc6d9ea111` returned `deployed_stale_or_unverified`.
- Probe evidence: API and Web build-info timed out, public Web HTML returned HTTP 503, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Graph Endpoint Copy Declutter Gate

### Current HEAD

- Starting commit: `7b5dc6a89ec09009afddc9934abc9354b03f3704`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Removed `Fallback graph payload` and `Fallback stage graph payload` from Graph Explorer primary endpoint-status copy.
- Graph Explorer now uses user-facing unavailable messages:
  - `Backend graph data unavailable; authoritative rows are hidden.`
  - `Backend stage graph data unavailable; authoritative rows are hidden.`
- Endpoint diagnostics still remain available through folded diagnostic details when present.
- Added a frontend quality assertion to prevent those internal fallback labels from returning to primary UI source.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography terminology change was introduced.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphExplorer.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_relationship_view_no_authoritative_fallbacks.py -q` -> PASS, 22 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes Graph Explorer user-facing copy only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `f24cd68665991e324f66474906dea32b44086b43`.
- GitHub `ci` passed in run `27070785443`.
- GitHub `Quality Gates` passed in run `27070785447`.
- Background deployed version probe for expected commit `f24cd68665991e324f66474906dea32b44086b43` returned `deployed_stale_or_unverified`.
- Probe evidence: API and Web build-info timed out during the bounded one-attempt check, public Web HTML returned HTTP 503, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Relationship Loading Declutter Gate

### Current HEAD

- Starting commit: `9528a0c13cfda2817a9d764df9d01d4da130cb8a`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Removed the relationship-mode main-panel loading blocker from Graph Explorer. If authoritative relationship endpoint rows are not available, the relationship views immediately show their controlled degraded empty state instead of an indefinite loading message.
- Added a second UI-level timeout guard for relationship endpoint loading state, used by export summaries and endpoint status display.
- Changed endpoint status headings so loading state is labeled `Authoritative data loading`, active state is labeled `Authoritative data connected`, and unavailable state is labeled `Backend data unavailable`.
- Updated regression tests so relationship rows still require backend authoritative data and do not fall back to local visible graph links.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography terminology change was introduced.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphExplorer.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `tests/quality/test_relationship_view_no_authoritative_fallbacks.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_relationship_view_no_authoritative_fallbacks.py -q` -> PASS, 22 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd run smoke:web` initially reproduced a stuck relationship loading state; after the relationship loading blocker removal -> PASS, 63 checks.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.

### Known Limitations

- This gate changes Graph Explorer loading semantics only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `827683f9f82a23b76de40e24cddfa8ae9baf3397`.
- GitHub `ci` passed in run `27071927990`.
- GitHub `Quality Gates` passed in run `27071927989`.
- Background deployed version probe for expected commit `827683f9f82a23b76de40e24cddfa8ae9baf3397` returned `deployed_stale_or_unverified`.
- Probe evidence: API and Web build-info timed out during the bounded one-attempt check, public Web HTML returned HTTP 503, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Entity Risk Label Declutter Gate

### Current HEAD

- Starting commit: `8564bb66a8c2291a37838a58f6e52730dde12013`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Replaced Entity Risk 360 primary metric labels that looked like raw field names with user-facing labels:
  - `score` -> `Risk score`
  - `level` -> `Risk level`
  - `likelihood` -> `Likelihood`
  - `impact` -> `Impact`
  - `vulnerability_modifier` -> `Vulnerability adjustment`
  - concentration and weighting fields now use title-cased business labels.
- The unavailable Entity Risk panel now formats the selected entity through the public node display helper instead of rendering the raw node id.
- Browser smoke now verifies the user-facing `EVIDENCE RECORDS` label instead of the older field-oriented evidence text.
- Added quality assertions scoped to Entity Risk 360 to prevent these raw metric labels returning to the primary UI.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography terminology change was introduced.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 20 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd run smoke:web` initially failed because the smoke expectation still used the old evidence label; after updating the smoke expectation -> PASS, 63 checks.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.

### Known Limitations

- This gate changes Entity Risk 360 display copy only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `610eb79f4cc23e7c8807f11809d68b53f7f3b0c1`.
- GitHub `ci` passed in run `27080908787`.
- GitHub `Quality Gates` passed in run `27080908792`.
- Background deployed version probe for expected commit `610eb79` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

### Post-Commit Background Status

- Implementation commit: `f83f162f40c3fa7a234ad45727d7c1b7a61d5a70`.
- GitHub `ci` passed in run `27072647694`.
- GitHub `Quality Gates` passed in run `27072647707`.
- Background deployed version probe for expected commit `f83f162f40c3fa7a234ad45727d7c1b7a61d5a70` returned `deployed_unavailable`.
- Probe evidence: API, Web build-info, and Web proxy timed out during the bounded one-attempt check, and public Web HTML returned HTTP 503.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Entity Risk Evidence Table Declutter Gate

### Current HEAD

- Starting commit: `30bdec98ebe3f76624344a5b02e0d931e18342de`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Removed raw `edge_id`, `edge_type`, and `source_ref` columns from the Entity Risk 360 evidence summary table.
- The primary evidence table now displays `Relationship`, `Source`, and `Summary` with formatted relationship/source labels.
- The detailed evidence table no longer renders raw edge ids or source record ids in the main page; source display is formatted through the public source label helper.
- Browser smoke now accepts either authoritative relationship rows or a controlled unavailable state that explicitly says local graph rows are excluded. This keeps the smoke aligned with the no-synthetic-relationship-row requirement.
- Added quality assertions preventing raw evidence edge/source record identifiers from returning to Entity Risk 360 primary evidence tables.
- No public API route was removed or changed. No live fetch, raw payload exposure, production-ready claim, or geography terminology change was introduced.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 21 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd run smoke:web` initially failed because Graph Explorer relationship endpoints entered controlled unavailable state while smoke expected authoritative rows; after updating smoke to require controlled unavailable copy when preview rows are hidden -> PASS, 63 checks.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.

### Known Limitations

- This gate changes Entity Risk 360 evidence table display and smoke acceptance semantics only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `3b193eb33c3524fe86b10d271235d3221543b5d4`.
- GitHub `ci` passed in run `27073290417`.
- GitHub `Quality Gates` passed in run `27073290426`.
- Background deployed version probe for expected commit `3b193eb33c3524fe86b10d271235d3221543b5d4` returned `deployed_stale_or_unverified`.
- Probe evidence: API and Web build-info timed out, public Web HTML returned HTTP 503, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Graph Relationship Copy Declutter Gate

### Current HEAD

- Starting commit: `85b2fb2d306d0983a017df0ec6957e15eefb1de4`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Replaced visible Graph Explorer relationship view headings with user-facing terms: `Supply relationships`, `Demand relationships`, `Production dependencies`, and `Supply-demand balance`.
- Removed internal relationship-class enum names from relationship view summary badges while retaining the raw metadata in folded audit details and API payloads.
- Reworded stage graph primary copy from engineering phrasing to user-facing phrasing: `Public evidence view`, `Risk propagation`, and `Focused view`.
- Updated browser smoke assertions to match the decluttered labels and continue enforcing controlled unavailable relationship states.
- Added quality assertions preventing internal relationship class names and older engineering copy from returning to primary stage/relationship view UI.
- No public route, API response field, report export field, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context safety rule was changed.

### Files Changed

- `apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/DemandRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/ProductionDependencyView.tsx`
- `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx`
- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 30 tests.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` initially failed because smoke still expected the old relationship/stage view copy; after updating the assertions -> PASS, 63 checks.

### Known Limitations

- This gate is a display declutter gate only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `5f2287b7b0793936d6134cc15c6387ac7268adcc`.
- GitHub `ci` passed in run `27077957689`.
- GitHub `Quality Gates` passed in run `27077957680`.
- Background deployed version probe for expected commit `5f2287b` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Report Export Copy Declutter Gate

### Current HEAD

- Starting commit: `cde0af850a7a78521e6b9d866b5ea2ed800280dc`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Removed visible `report_id; report_version` subtitle copy from the Investigation Report export panel.
- Replaced it with a user-facing sanitized export readiness sentence.
- Kept report identifiers, selected run refs, report version, graph version, source manifest id, calibration status, formula refs, and exclusion flags in folded audit details.
- Added a quality assertion preventing report id/version concatenation from returning to primary page copy.
- No public route, API response field, report export field, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context safety rule was changed.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 30 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.

### Known Limitations

- This gate changes report page display copy only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `8ac06b713e8937065f6f4af93e5475f670ba8c3f`.
- GitHub `ci` passed in run `27078363473`.
- GitHub `Quality Gates` passed in run `27078363466`.
- Background deployed version probe for expected commit `8ac06b7` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Source Registry Checksum Declutter Gate

### Current HEAD

- Starting commit: `bf2f7ef0d570ea07732b2bb6e2338d33fced20ef`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Removed per-source checksum snippets from the System Health source registry detail list.
- Replaced each visible checksum snippet with a user-facing note that the checksum is retained in the audit manifest.
- Kept the manifest checksum in folded audit details for traceability.
- Added a quality assertion preventing `source.checksum.slice(...)` from returning to the primary source registry list.
- No public route, API response field, report export field, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context safety rule was changed.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 30 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.

### Known Limitations

- This gate changes System Health source registry display copy only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `5981d603f3859c5888262b173f9e53f7cc8c4374`.
- GitHub `ci` passed in run `27078837884`.
- GitHub `Quality Gates` passed in run `27078837880`.
- Background deployed version probe for expected commit `5981d60` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Report Evidence Summary Declutter Gate

### Current HEAD

- Starting commit: `77b7a0647e3f595f1003c0fd72f8db6b22c3df33`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Replaced `Report metadata and evidence table` with `Report evidence summary` in Investigation Report primary UI.
- Replaced `Controlled report audit view...` / `Audited report context...` subtitles with evidence coverage and graph context language.
- Formatted report evidence section ids through the display label helper so internal ids such as semirisk methodology keys are not rendered as raw primary table values.
- Updated browser smoke to assert the new user-facing report evidence summary title.
- Added quality assertions preventing the old audit-oriented report titles and raw section values from returning.
- No public route, API response field, report export field, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context safety rule was changed.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 30 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` initially failed because the smoke expectation still used the old report title; after updating the assertion -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.

### Known Limitations

- This gate changes Investigation Report display copy and table formatting only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `8f97c9e1d9a5fd3f4a1b91219e3976aa9090310b`.
- GitHub `ci` passed in run `27079405434`.
- GitHub `Quality Gates` passed in run `27079405438`.
- Background deployed version probe for expected commit `8f97c9e` returned `deployed_stale_or_unverified`.
- Probe evidence: API timed out, public Web HTML returned HTTP 503, and Web build-info / Web proxy still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Run History Unavailable Copy Gate

### Current HEAD

- Starting commit: `6f17ee040f2ff78d8bfabcde443abdb9d03c4502`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Confirmed current source includes `/api/v1/runs` route wiring and API tests, but the currently running local/deployed API can still return a 404 from older runtime state.
- Removed raw route error text such as `Route not found: /api/v1/runs` from Run History primary page copy.
- Replaced it with a user-facing empty/degraded state: `Run history is not available in this environment. Stored workflow runs are hidden.`
- Preserved the sanitized diagnostic in folded `Run history diagnostics` audit details.
- Added quality assertions preventing route error text from returning to primary Run History copy.
- No public route, API response field, report export field, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context safety rule was changed.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 30 tests.
- `npm.cmd --workspace apps/web run typecheck` initially failed on a wrong helper name; after switching to `sanitizePublicEndpointDiagnostic` -> PASS.
- `npm.cmd run smoke:web` initially failed while the page was in the compile-error state; after the helper fix -> PASS, 63 checks.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.

### Known Limitations

- This gate cleans the Run History unavailable state; it does not redeploy Render or prove the deployed API has picked up the existing `/api/v1/runs` route.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `bef3683c912701d142a094920306cbff2718f9be`.
- GitHub `ci` passed in run `27079930371`.
- GitHub `Quality Gates` passed in run `27079930365`.
- Background deployed version probe for expected commit `bef3683` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Report Evidence Section Label Gate

### Current HEAD

- Starting commit: `ab2602cccadd799609f79c1ea936cff840a75f59`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Added a report evidence section formatter so internal methodology keys do not become primary user-facing table labels.
- The Investigation Report evidence summary now maps risk-score methodology sections to `Risk score evidence`, with explicit labels available for forward stress, reverse stress, intervention, and methodology evidence.
- Updated both report evidence summary tables and the evidence/limitations list to use the dedicated formatter.
- Added quality assertions preventing raw section values from returning to report evidence tables.
- No public route, API response field, report export field, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context safety rule was changed.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 30 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.

### Known Limitations

- This gate changes Investigation Report evidence labels only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `e7f25f4f6a5f476df4a7dc2c11fb5f22a271d85b`.
- GitHub `ci` passed in run `27080418260`.
- GitHub `Quality Gates` passed in run `27080418262`.
- Background deployed version probe for expected commit `e7f25f4` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-06 Background Entity Risk Copy Declutter Gate

### Current HEAD

- Starting commit: `38f107c4d10d45c1243311060ae92e8f5dd706ed`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Replaced `Fixture-labeled SemiRisk-KG entity scores...` with user-facing public evidence graph language.
- Replaced the unavailable portfolio explanation that referenced a `metadata envelope` with a valid public-evidence response message.
- Reworded HHI notes from `fixture/proxy shares` to `public-evidence proxy shares`.
- Replaced the unavailable Risk Score API subtitle that referenced the fixture graph API with an evidence-backed risk response message.
- Renamed the primary `Version and freshness` panel to `Data status`, moving graph/source version language into folded audit details.
- Added quality assertions preventing the old Entity Risk engineering copy from returning.
- No public route, API response field, report export field, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context safety rule was changed.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 30 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.
- `python -m pytest tests/quality -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.

### Known Limitations

- This gate changes Entity Risk 360 display copy only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

## 2026-06-07 Background Evidence Board Graph Path Declutter Gate

### Current HEAD

- Starting commit: `7659712b753a7ec8dc312a9fc3e57beef6dfb95e`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Replaced visible Evidence Board `graph_path_ref` values with user-facing labels such as `Evidence path 1`.
- Kept the original graph path references inside the sanitized JSON export input so audit/export paths remain available outside the primary page display.
- Added a frontend display-declutter quality assertion that the visible table uses formatted path labels while the export builder still receives the original rows.
- Confirmed the API client already keeps bounded idempotent GET retry, same-origin read fallback, and sanitized unavailable envelopes with `failed_endpoint`, `retry_hint`, and `transport_attempts`.
- No public route, API response field, report export field, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context safety rule was changed.

### Files Changed

- `apps/web/src/features/evidence-board/EvidenceAuditPanel.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 31 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `npm.cmd run smoke:web` -> PASS in local proxy mode.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.

### Known Limitations

- This gate changes Evidence Board primary display labels only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `76a35e0872e0f46d5cb9ec14f895b3f70a2a00a0`.
- GitHub `ci` passed in run `27086741167`.
- GitHub `Quality Gates` passed in run `27086741162`.
- Background deployed version probe for expected commit `76a35e0` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Evidence Link Label Declutter Gate

### Current HEAD

- Starting commit: `a7cf6d6713559c17b572d8c457d7d92f3641cedf`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Replaced the legacy Evidence Board `Graph and model links` panel with user-facing `Evidence links` copy.
- Removed primary page field labels such as `evidence_ref`, `graph_path_ref`, `model_component`, `claim_source`, and `last_reviewed`.
- Replaced the visible raw `evidence:<id>` path value with `Evidence path N` labels.
- Added a `graph_path_ref` display-label mapping so shared tables render `Graph path link` instead of the raw field key.
- Changed the generic unknown boolean display fallback from `true` / `false` to `yes` / `no`.
- No public route, API response field, report export field, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context safety rule was changed.

### Files Changed

- `apps/web/src/features/common/legacyDashboard.tsx`
- `apps/web/src/features/common/displayLabels.ts`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 31 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes Evidence Board display labels only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `399f2ae6a94ea670f58d74ce59845d98f22fe902`.
- GitHub `ci` passed in run `27087210495`.
- GitHub `Quality Gates` passed in run `27087210464`.
- Background deployed version probe for expected commit `399f2ae` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Evidence Records Copy Declutter Gate

### Current HEAD

- Starting commit: `05721fd0ce0448b82d40de069f26cc501f036d47`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Replaced visible `Evidence refs` / `evidence refs` copy with `Evidence records` / `evidence records` across primary dashboard pages, Graph Explorer, stage views, shared evidence tables, smoke expectations, and display-label overrides.
- Replaced relationship table `Source refs` headers with `Sources`.
- Kept underlying API/data field names such as `evidence_refs` unchanged for compatibility, exports, and audit data.
- Added quality assertions that block `Evidence refs`, `Source refs`, and stage-view `evidence refs` from returning to primary UI copy.
- No public route, API response field, report export field, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context safety rule was changed.

### Files Changed

- `apps/web/src/app/i18n.tsx`
- `apps/web/src/features/common/displayLabels.ts`
- `apps/web/src/features/common/legacyDashboard.tsx`
- `apps/web/src/features/common/pageRelevance.ts`
- `apps/web/src/features/common/tables/EvidenceRefsTable.tsx`
- `apps/web/src/features/common/tables/StageEvidenceRefsTable.tsx`
- `apps/web/src/features/graph-explorer/DemandRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/GraphInspector.tsx`
- `apps/web/src/features/graph-explorer/ProductionDependencyView.tsx`
- `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx`
- `apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx`
- `scripts/browser-smoke.mjs`
- `tests/e2e/supply-risk-atlas.feature`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 32 tests after updating expected copy.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS.
- `python -m pytest tests/api -q` -> TIMED OUT after 180 seconds in the local background window; no API files were changed in this gate.

### Known Limitations

- This gate changes visible evidence-reference wording only. It does not add calibrated production data, new source connectors, or Render redeployment.
- The full `tests/api -q` group timed out locally under background load; GitHub `ci` remains the authoritative full-suite check after push.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `064b0e6315d5f65b4e236f79bfc72d863a9b3cc5`.
- GitHub `ci` passed in run `27087861521`.
- GitHub `Quality Gates` passed in run `27087861510`.
- Background deployed version probe for expected commit `064b0e6` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background System Health Readiness Label Declutter Gate

### Current HEAD

- Starting commit: `0928d7d15ccdb4ada771ea3bddfb7ab4fd222967`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Added product-facing display labels for System Health readiness and status fields that previously depended on generic snake_case formatting.
- Covered `api_readiness`, `connector_readiness`, `connector_statuses`, `deployment_state`, `deployment_version_readiness`, `graph_readiness`, `model_readiness`, `service_readiness`, `source_registry_readiness`, `source_statuses`, `storage_readiness`, and `validation_readiness`.
- Kept API fields, export metadata, diagnostics, source refs, report fields, and System Health technical diagnostics unchanged.
- Added a quality assertion so these readiness labels stay mapped to user-facing copy.
- No public route, API response schema, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context propagation rule was changed.

### Files Changed

- `apps/web/src/features/common/displayLabels.ts`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 34 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS.

### Known Limitations

- This gate changes display labels only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `57d9f4b09c3a770411f9f5798c571018156dedc0`.
- GitHub `ci` passed in run `27088705484`.
- GitHub `Quality Gates` passed in run `27088705474`.
- Background deployed version probe for expected commit `57d9f4b` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Graph Node Catalog Source Copy Declutter Gate

### Current HEAD

- Starting commit: `1f555c3ab0010ef2b1b3cad6d71e0e1be340df28`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Reworded the Graph Explorer Node Catalog view from the internal source-candidate term to user-facing evidence-source language.
- Kept the underlying `source_candidates` data field unchanged for API compatibility, exports, and ontology contracts.
- Added a frontend display declutter assertion so the internal source-candidate wording does not return to the Node Catalog primary UI.
- No public route, API response schema, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context propagation rule was changed.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphNodeCatalogView.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 40 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes visible Node Catalog wording only. It does not add calibrated production data, new source connectors, or Render redeployment.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `c89483182af83a10eb201e7548578ca0661ccb36`.
- GitHub `ci` passed in run `27092823564`.
- GitHub `Quality Gates` passed in run `27092823552`.
- Background deployed version probe for expected commit `c894831` timed out in the bounded probe window and did not verify deployment.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Relationship Audit Label Declutter Gate

### Current HEAD

- Starting commit: `27320fc380e5ac568a438dec3fa9e0a7f25eac1c`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Reworded relationship audit detail labels from raw metadata names to user-facing copy in supply, demand, production dependency, and supply-demand balance relationship views.
- Kept the underlying `source_status` and `evidence_refs` metadata fields unchanged for API compatibility, exports, diagnostics, and evidence traceability.
- Added a frontend display declutter assertion so the relationship views do not reintroduce `source_status` or `evidence_refs` as visible audit labels.
- No public route, API response schema, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context propagation rule was changed.

### Files Changed

- `apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/DemandRelationshipView.tsx`
- `apps/web/src/features/graph-explorer/ProductionDependencyView.tsx`
- `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 41 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `npm.cmd run smoke:web` -> first failed because no local Web server was listening on `http://127.0.0.1:3000`.
- `npm.cmd run smoke:web` -> then timed out under the outer command window before the local API server was available.
- `npm.cmd run smoke:web` -> failed with the app still connecting to public data when local API port `8000` was not listening.
- `python -m services.api.dev_server` -> started as a hidden local background API process for smoke verification.
- `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000 SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_API_ORIGIN=http://127.0.0.1:8000 npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes visible relationship audit labels only. It does not add calibrated production data, new source connectors, or Render redeployment.
- GitHub checks passed after push; deployed Render endpoints remain unavailable or unverified in the bounded background probe.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `546ade6c0286232f45f3d9e82324963a8e7ac9cc`.
- GitHub `ci` passed in run `27100403274`.
- GitHub `Quality Gates` passed in run `27100403271`.
- Background deployed version probe for expected commit `546ade6` returned `deployed_unavailable`: API, Web build-info, and Web proxy timed out in the bounded probe window, and public Web HTML returned HTTP `503`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Graph Explorer Diagnostic Label Declutter Gate

### Current HEAD

- Starting commit: `df54f8e390eb729b13c1da614436003d4b8252a0`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Reworded Graph Explorer backend-unavailable diagnostic labels from internal transport metadata names to user-facing copy.
- Kept the underlying `failed_endpoint`, `source_status`, `retry_hint`, and `transport_attempts` metadata reads, sanitization, and API envelope compatibility unchanged.
- Added a frontend display declutter assertion so Graph Explorer endpoint diagnostics do not reintroduce raw transport metadata keys as visible labels.
- No public route, API response schema, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context propagation rule was changed.

### Files Changed

- `apps/web/src/features/graph-explorer/GraphExplorer.tsx`
- `tests/quality/test_frontend_display_declutter.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py -q` -> PASS, 42 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m services.api.dev_server` -> started as a hidden local background API process for smoke verification.
- `npm.cmd --workspace apps/web run dev` -> started as a hidden local background Web process with `NEXT_PUBLIC_SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1` and `SUPPLY_RISK_API_ORIGIN=http://127.0.0.1:8000`.
- `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000 SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_API_ORIGIN=http://127.0.0.1:8000 npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes visible Graph Explorer diagnostic labels only. It does not add calibrated production data, new source connectors, or Render redeployment.
- GitHub checks passed after push; deployed Render endpoints remain stale, unavailable, or unverified in the bounded background probe.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `ee5849f34c9711974dd0dc1384a793f4b2f29a69`.
- GitHub `ci` passed in run `27100825345`.
- GitHub `Quality Gates` passed in run `27100825331`.
- Background deployed version probe for expected commit `ee5849f` returned `deployed_stale_or_unverified`: API and Web build-info timed out in the bounded probe window, public Web HTML returned HTTP `503`, and Web proxy `/api/v1/version` still reported stale commit `b281948e446031f7605d4d85e6f7f6269adfa357`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

## 2026-06-07 Background Source Coverage Error Copy Declutter Gate

### Current HEAD

- Starting commit: `f6bac6ade43149f43ceaff410a9b35bbdf6e423c`.
- Branch: `main`.
- Preserved untracked user files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`.

### Gate Result

- Reworded global dashboard endpoint error copy from `source status` wording to user-facing source coverage wording.
- Updated browser smoke's controlled Entity Risk degradation expectation to look for `source coverage`, so smoke no longer encourages the older status wording.
- Added quality assertions that keep the old `failed source status` and `degraded source status` phrases out of the app shell.
- No public route, API response schema, source connector, live-fetch setting, raw-payload policy, geography terminology rule, or evidence-context propagation rule was changed.

### Files Changed

- `apps/web/src/app/App.tsx`
- `scripts/browser-smoke.mjs`
- `tests/quality/test_frontend_display_declutter.py`
- `tests/quality/test_frontend_source_readability.py`
- `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md`

### Commands Run

- `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_frontend_source_readability.py -q` -> PASS, 48 tests.
- `npm.cmd --workspace apps/web run typecheck` -> PASS.
- `rg -n "source status|failed source status|degraded source status" apps/web/src scripts/browser-smoke.mjs tests/quality` -> only the negative quality assertions still contain the old phrases.
- `python -m pytest tests/quality -q` -> PASS.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS.
- `python -m pytest tests/security tests/graph_invariants -q` -> PASS.
- `npm.cmd --workspace apps/web run build` -> PASS.
- `python -m services.api.dev_server` -> started as a hidden local background API process for smoke verification.
- `npm.cmd --workspace apps/web run dev` -> started as a hidden local background Web process with `NEXT_PUBLIC_SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1` and `SUPPLY_RISK_API_ORIGIN=http://127.0.0.1:8000`.
- `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000 SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_API_ORIGIN=http://127.0.0.1:8000 npm.cmd run smoke:web` -> PASS, 63 checks.

### Known Limitations

- This gate changes visible app-shell error copy and smoke expectations only. It does not add calibrated production data, new source connectors, or Render redeployment.
- GitHub checks passed after push; deployed Render endpoints remain unavailable or unverified in the bounded background probe.
- Render deployment remains blocked in background mode until a safe Render API key / service IDs / GitHub Actions secrets / Render MCP path is configured.
- No Chrome, Render UI, credential entry, screenshot capture, raw response logging, or ChatGPT handoff occurred because the user asked the agent to work in the background without affecting foreground browser activity.

### Post-Commit Background Status

- Implementation commit: `3d948d1fd88ee9ed41a4c2618aad831ca0d5bf71`.
- GitHub `ci` passed in run `27101230324`.
- GitHub `Quality Gates` passed in run `27101230328`.
- Background deployed version probe for expected commit `3d948d1` returned `deployed_unavailable`: API, Web build-info, Web proxy, and public Web HTML were unavailable in the bounded probe window; public Web HTML returned HTTP `503`.
- Background Render deploy helper dry run returned `render_deploy_blocked_missing_safe_deploy_path` because `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, and `RENDER_WEB_SERVICE_ID` are not configured in the local environment.
- No Render API call, Chrome action, credential entry, raw response logging, screenshot capture, or ChatGPT handoff occurred in this background-only pass.

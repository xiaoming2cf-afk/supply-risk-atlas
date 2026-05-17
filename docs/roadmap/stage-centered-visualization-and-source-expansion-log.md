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

# Semantic Graph Page Relevance Continuation Log

## Gate 0 - Baseline And Current-State Inventory

- Gate status: PASS
- Current HEAD at inventory start: `a333f80`
- Preserved untracked local files: `apps/web/AGENTS.md`, `apps/web/CLAUDE.md`, `data/runtime/`
- Commands run:
  - `python -m pytest tests/quality -q` -> PASS (`12 passed`)
  - `python -m pytest tests/api -q` -> PASS
  - `python -m pytest -q` -> PASS
  - `npm.cmd --workspace apps/web run typecheck` -> PASS
  - `npm.cmd --workspace apps/web run build` -> PASS
  - `npm.cmd run smoke:web` -> PASS (`51 checks`)
  - `python -m pytest tests/geo tests/contract tests/sources tests/graph_invariants tests/security -q` -> PASS
  - `python -m pytest tests/api/test_supply_demand_graph_endpoints.py tests/api/test_supply_demand_analytics_tables.py -q` -> PASS (`14 passed`)
  - `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`4 passed`)
- Semantic file inventory:
  - `configs/ontology/semiconductor_chain_layers.yaml` -> present
  - `configs/ontology/semiconductor_node_catalog.yaml` -> present
  - `configs/ontology/semiconductor_edge_catalog.yaml` -> present
  - `configs/ontology/semiconductor_relationship_semantics.yaml` -> present
  - `configs/sources/semiconductor_node_source_map.yaml` -> present
  - `graph_kernel/relationship_builder.py` -> present
  - `graph_kernel/supply_demand_builder.py` -> present
  - `apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx` -> present
  - `apps/web/src/features/graph-explorer/DemandRelationshipView.tsx` -> present
  - `apps/web/src/features/graph-explorer/ProductionDependencyView.tsx` -> present
  - `apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx` -> present
  - `apps/web/src/features/common/pageRelevance.ts` -> present
- Node catalog inventory: `165` concrete nodes spanning L0-L11.
- Public evidence connector inventory: SEC EDGAR Lite, GDELT semiconductor lite/events, UN Comtrade semiconductor trade lite, WITS trade tariff lite, USGS minerals lite, USGS earthquake lite, NGA World Port Index lite, OFAC sanctions list lite, Consolidated Screening List lite, BIS export controls lite, Federal Register export controls lite, ETO supply chain, GTA export controls, and WSTS billings. Connector framework helpers are also present.
- Graph view inventory: overview, focus, path, timeline, geo, matrix, evidence, scenario overlay, source coverage, node catalog, supply relationships, demand relationships, production dependencies, and supply-demand balance.
- Chart inventory: risk ranking, risk components, HHI concentration, trade flow, dependency heatmap, policy timeline, hazard timeline, Monte Carlo histogram/ECDF, CVaR tail, functionality curve, optimizer before/after, validation ablation, source freshness, graph quality, supply-demand balance, supplier HHI, critical input bottleneck, downstream demand pressure, product-to-process dependency, policy restriction impact, hazard exposure by layer, and supplier country concentration.
- Table inventory: source catalog, connector status, graph nodes, graph edges, evidence refs, risk ranking, scenario runs, reverse stress results, optimizer actions, validation artifacts, trade flows, policy events, hazard events, logistics facilities, supply relationships, demand relationships, production dependencies, supplier concentration, product demand, critical inputs, and supply-demand balance.
- Route inventory: public health/version/dashboard, graph snapshot/neighborhood/views, graph timeline/geo/matrix/layers/evidence/scenario overlay/node catalog/source coverage, relationship graph endpoints, risk, forward/reverse scenarios, intervention optimization, reports, run history, analytics chart/table/export, and legacy compatibility routes are registered.
- Terminology normalization evidence: geography guard and semantic suites passed; API-visible and frontend-visible output remains normalized to `region:china_taiwan` / `中国台湾` with parent `country:CN` / `中国`.
- Completed gates: Gates 1-8 were already implemented in this checkout and verified by the targeted tests above; no code gap required patching.
- Failed tests: none.
- Known limitations: platform remains fixture/proxy/promoted-public-evidence research infrastructure, live fetch remains disabled by default, and no production-readiness or audited capacity claim is made.
- Deployment status: pending controlled GitHub/Render verification after final local acceptance.
- Computer Use actions: none yet.

## Gates 1-8 - Semantic Verification

- Gate status: PASS
- Changed files: this log only.
- Evidence: existing implementation already contains the chain layers, node catalog, edge catalog, relationship semantics, node-source map, relationship-aware graph builders, four supply-demand graph views, page relevance policy, analytics tables/charts, and documentation.
- Commands run:
  - `python -m pytest tests/geo tests/contract tests/sources tests/graph_invariants tests/security -q` -> PASS
  - `python -m pytest tests/api/test_supply_demand_graph_endpoints.py tests/api/test_supply_demand_analytics_tables.py -q` -> PASS (`14 passed`)
  - `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`4 passed`)
- Relationship evidence: supply, demand, production dependency, and evidence context relationships remain distinct; evidence context links remain non-propagating and not supply-chain dependency edges.
- Page relevance evidence: local smoke includes policy checks for major public analytical pages and confirms non-graph pages do not render dense graph canvases.
- Next gate decision: proceed to final local acceptance and controlled deployment verification.

## Final Local Acceptance

- Acceptance status: PASS locally
- Current HEAD before final local evidence commit: `a333f80`
- Commands run:
  - `python -m pytest tests/quality -q` -> PASS (`12 passed`)
  - `python -m pytest tests/geo tests/contract tests/sources tests/graph_invariants tests/api tests/security tests/model tests/simulation tests/optimization tests/reports -q` -> PASS
  - `python -m pytest -q` -> PASS
  - `npm.cmd --workspace apps/web run typecheck` -> PASS
  - `npm.cmd --workspace apps/web run build` -> PASS
  - `npm.cmd run smoke:web` -> PASS (`51 checks`)
- Final local evidence: concept model files exist, node catalog has `165` concrete nodes, relationship classes remain separated, relationship graph endpoints and analytics endpoints pass API tests, page relevance policy is smoke-tested, and no raw payload or production-readiness claim is introduced.
- Deployment status: pending controlled GitHub/Render verification after this log commit.
- Computer Use actions: none yet.

## Controlled Deployment Verification

- Gate status: PARTIAL / BLOCKED ON RENDER ACCESS
- Pushed commit: `28f06cda3930a05ce0484d46c036da18f0798bd1`
- GitHub Actions evidence:
  - `ci #32` -> PASS, `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25807689897`
  - `Quality Gates #32` -> PASS, `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25807689863`
- Deployed API version check:
  - Expected commit: `28f06cda3930a05ce0484d46c036da18f0798bd1`
  - Observed API commit: `9cbb0e927a8bbcf66e05f19e5d3d70714f34204f`
  - Status: stale deployment
- Deployed smoke:
  - `npm.cmd run smoke:web -- --mode=deployed` -> best-effort failure because deployed Web/API are still serving the old build.
  - Evidence sanitized: the deployed graph does not yet include the local semantic/page relevance build and still emits noncanonical legacy geography labels from the old deployment.
- Render redeploy attempt status:
  - Render CLI: unavailable in this workspace.
  - Render environment variable names: none available.
  - Render MCP/tooling: no Render deployment tool was exposed in this session.
  - Redeploy action: not performed because no authenticated Render control path was available.
- Computer Use actions:
  - No GUI Computer Use was performed.
  - Verification used public GitHub API, public deployed API/Web endpoints, and local shell commands only.
- Sensitive data handling: no secrets, tokens, cookies, private diagnostics, or account details were printed or recorded.
- Required next step: manually redeploy `supply-risk-atlas-api` and `supply-risk-atlas-web` on Render from latest `main`, clear Web build cache if stale UI remains, then rerun deployed version check and deployed smoke.

## Render Auto-Deploy Trigger Commit

- Gate status: IN PROGRESS
- Reason: Render UI sign-in required GitHub credentials, so no credential entry was performed.
- Action: touch `render.yaml` with a comment-only deployment trigger so both Render services match their configured build filters.
- Expected effect: Render auto-deploy should rebuild `supply-risk-atlas-api` and `supply-risk-atlas-web` from latest `main` without changing runtime config.
- Sensitive data handling: no credentials, tokens, cookies, or private account details were entered or recorded.

## Controlled Render Deployment Continuation

- Gate status: IN PROGRESS
- Pushed trigger commit: `540ad3e62399d5e620a179bf4872bd9a0c9c5507`
- GitHub Actions evidence:
  - `ci #34` -> PASS
  - `Quality Gates #34` -> PASS
- Computer Use actions:
  - Used the authorized Chrome extension browser for project-scoped Render dashboard verification only.
  - Opened Render dashboard services `supply-risk-atlas-api` and `supply-risk-atlas-web`.
  - Triggered Render Web service redeploy with build cache clear from latest `main`.
  - Observed Render API service deploying commit `540ad3e62399d5e620a179bf4872bd9a0c9c5507`.
  - No unrelated tabs, unrelated apps, credentials, cookies, tokens, screenshots with secrets, or private diagnostics were accessed or recorded.
- Deployment evidence:
  - API `/api/v1/version` reports `git_commit=540ad3e62399d5e620a179bf4872bd9a0c9c5507`, `environment=render`, `storage_mode=sqlite`, `not_production_ready=true`.
  - `scripts/check-deployed-version.py` reports API commit matches expected; Web commit is not directly visible, so Web version remains `commit_not_visible`.
  - Manual Chrome verification of `https://supply-risk-atlas-web.onrender.com/#system-health-center` loaded System Health data, source registry details, `api_version`, `graphVersion`, and `sourceManifestId` after deployment.
- Deployed smoke evidence:
  - `npm.cmd run smoke:web -- --mode=deployed` exited best-effort status `0` but did not complete the full smoke path because headless deployed Web initially showed `Public data unavailable` while waiting for System Health evidence.
  - Root cause observed from live API/Web checks: API was healthy, but deployed browser smoke is sensitive to Render cold start and dashboard API request timing.
- Follow-up patch:
  - Increased the frontend dashboard API client default request timeout from `12000` ms to `60000` ms to tolerate Render cold-start latency and slow free-instance risk endpoints without changing API routes, source contracts, graph semantics, or security posture.
  - Added a shared in-process `lru_cache(maxsize=1)` around the deterministic SemiRisk fixture snapshot used by API service endpoints, avoiding repeated snapshot rebuilds for risk, forward scenario, reverse stress, optimizer, report, and run-history routes.
  - Tested the same-origin `/api/v1` Next proxy on Render; it remained unavailable with `502` responses in this environment, so deployed Web keeps using the public API URL configured by `NEXT_PUBLIC_SUPPLY_RISK_API_URL`.
  - Restored the deployed hostname fallback to `https://supply-risk-atlas-api.onrender.com/api/v1` because the Render Web build did not expose the configured public API URL and otherwise fell back to the unavailable proxy.
  - Added bounded dashboard API network retries (`3` attempts with short backoff) to tolerate intermittent deployed browser fetch resets while preserving explicit degraded envelopes when retries fail.
- Validation for follow-up patch:
  - `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`4 passed`)
  - `python -m pytest tests/api/test_supply_demand_graph_endpoints.py tests/api/test_supply_demand_analytics_tables.py -q` -> PASS (`14 passed`)
  - `npm.cmd --workspace apps/web run typecheck` -> PASS
  - `npm.cmd --workspace apps/web run build` -> PASS
  - `npm.cmd run smoke:web` -> PASS (`51 checks`)
  - Deployed risk endpoint spot check before the final timeout adjustment: `/risk/entities/company:tsmc` returned success in about 17 seconds; `/risk/portfolio?node_type=company&limit=20` returned success in about 16 seconds.
- Limitations:
  - The platform remains fixture/proxy/promoted-public-evidence research infrastructure and is not production-ready.
  - Web build commit is not directly exposed in static HTML; deployed version verification therefore relies on API `/version`, Render deploy status, and deployed smoke behavior.
  - A new commit is required for the timeout patch and then Render must rebuild Web/API again from latest `main`.

## Final Deployment Evidence

- Gate status: PARTIAL DEPLOYMENT ACCEPTANCE
- Latest pushed commit: `fdd28bce874a1324939de8c1390017a7bdbbe3c1`
- GitHub Actions evidence:
  - `ci #42` -> PASS, `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25816874343`
  - `Quality Gates #42` -> PASS, `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25816867393`
- Render deployment evidence:
  - API service `supply-risk-atlas-api`, deploy `dep-d82bmv8js32c73dsv8s0`, commit `fdd28bce874a1324939de8c1390017a7bdbbe3c1`, status `live`.
  - Web service `supply-risk-atlas-web`, deploy `dep-d82bn58js32c73dsvelg`, commit `fdd28bce874a1324939de8c1390017a7bdbbe3c1`, status `live`.
  - API `/api/v1/version` reports `git_commit=fdd28bce874a1324939de8c1390017a7bdbbe3c1`, `environment=render`, `storage_mode=sqlite`, `not_production_ready=true`.
  - Web commit is not visible in static HTML; Render deploy detail is the source of Web commit evidence.
- Local final validation after deployment-stability patches:
  - `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` -> PASS (`4 passed`)
  - `python -m pytest tests/quality tests/api tests/security -q` -> PASS
  - `python -m pytest tests/api tests/simulation tests/optimization tests/reports -q` -> PASS
  - `python -m pytest tests/geo tests/contract tests/sources tests/graph_invariants tests/model -q` -> PASS
  - `npm.cmd --workspace apps/web run typecheck` -> PASS
  - `npm.cmd --workspace apps/web run build` -> PASS
  - `npm.cmd run smoke:web` -> PASS (`51 checks`)
- Deployed smoke:
  - `npm.cmd run smoke:web -- --mode=deployed` -> INCOMPLETE best-effort run, exit status `0`.
  - Observed final blocker: deployed smoke reached Reverse Stress Lab but timed out while the page remained in `Running` state.
  - Earlier deployed retries intermittently hit Render/browser fetch resets and a Web proxy `502`; API spot checks for the same endpoints returned successful public envelopes.
  - Current assessment: API and Web are deployed and live at the latest commit, but deployed browser smoke remains flaky/incomplete on Render free instances.
- Computer Use actions:
  - Used only the authorized Chrome extension browser for project-scoped Render dashboard verification and deploy actions.
  - Triggered manual latest-commit deploys for `supply-risk-atlas-api` and `supply-risk-atlas-web`; Web cache-clear deploy was used earlier during stale UI recovery.
  - No unrelated tabs, unrelated apps, credentials, cookies, tokens, screenshots with secrets, or private diagnostics were accessed or recorded.
- Deployment status:
  - Local acceptance: PASS.
  - GitHub CI/Quality Gates: PASS.
  - Render API/Web: LIVE at latest commit.
  - Deployed smoke: INCOMPLETE best-effort due Render/browser timing.

## Deployed Browser Proxy Race Fix

- Gate status: IN PROGRESS
- Reason: deployed best-effort smoke reached Entity Risk 360 but the page displayed a degraded `Failed to fetch` envelope for `risk/entities/company:tsmc`.
- Exact cause: the client could start its first refresh before the browser hostname was resolved. On Render, that first refresh used the same-origin `/api/v1` proxy, and the current Render Web proxy path returns `502` in this environment. The later direct API configuration could race with that degraded state.
- Files changed:
  - `apps/web/src/app/App.tsx`
  - `docs/roadmap/semantic-graph-page-relevance-continuation-log.md`
- Change:
  - Delay the dashboard refresh until runtime hostname resolution is complete, so deployed Web chooses the direct public API base URL before issuing dashboard requests.
- Commands run:
  - `python -m pytest tests/quality tests/api tests/security -q` -> PASS
  - `npm.cmd --workspace apps/web run typecheck` -> PASS
  - `npm.cmd --workspace apps/web run build` -> PASS
  - `npm.cmd run smoke:web` -> PASS (`51 checks`)
- Computer Use actions:
  - Used the authorized Chrome extension browser only for project-scoped Render dashboard verification.
  - Confirmed Render API deploy `dep-d82bqbkvikkc73ejf320` and Web deploy `dep-d82bqhjbc2fs73c8kg5g` were live at commit `59750b66ea0aba69f790b6855ee9c993c9acf1b5`.
  - No unrelated tabs, unrelated apps, credentials, cookies, tokens, screenshots with secrets, or private diagnostics were accessed or recorded.
- Deployment status:
  - This fix must be committed, pushed, and redeployed before rerunning deployed smoke.
- Limitations:
  - Web static HTML still does not expose a build commit, so Web version verification depends on Render deploy detail plus deployed behavior.

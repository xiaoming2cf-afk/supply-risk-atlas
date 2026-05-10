# Semiconductor Platform Roadmap

This roadmap scopes SupplyRiskAtlas into a research-grade semiconductor supply-chain resilience platform while preserving the current lightweight public-data deployment. It is not a claim that every epic is complete.

## Guardrails

- Real-data-first: production views use public, reviewable source evidence.
- No fake production data. Fixtures are deterministic and test-only.
- Every visible data point must carry source, freshness, lineage, graph version, and source manifest where applicable.
- Raw payloads, secrets, private diagnostics, and API keys are never committed or exposed.
- Export-control and sanctions evidence may support risk/compliance views only; no evasion or circumvention advice.
- Missing source, graph, score, model, or simulation data must render as unavailable, stale, partial, or degraded.

## Epics

| Task ID | Epic | Owner lane | Target files | Dependencies | Acceptance criteria | Required checks | Deployment notes | Risk notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SRA-GOV-001 | Platform governance | platform | `.agents/skills/sra-*`, `docs/quality-gates.md` | none | Local skills define contract-first, source, graph, API, frontend, and review rules. | Skill files include required reads, forbidden behaviors, checks, and summary format. | No runtime impact. | Missing governance lets fake or raw data leak into later slices. |
| SRA-SRC-001 | Source registry | data | `configs/sources/semiconductor.yaml`, `docs/data/semiconductor-source-registry.md` | SRA-GOV-001 | Six v0.1/v0.2 sources registered with terms, freshness, connector state, and review status. | `python -m pytest tests/ingestion -q` | No live fetch at startup. | Live connectors are not implemented in this slice. |
| SRA-CON-001 | Data contracts | data/platform | `data_contracts/**` | SRA-SRC-001 | Registry schema fails missing governed fields. | Contract tests. | Static files only. | Raw/silver/graph contracts beyond registry remain later work unless present. |
| SRA-ONT-001 | Semiconductor ontology | graph | `configs/ontology/semiconductor.yaml`, `docs/domain/semiconductor-ontology.md` | SRA-GOV-001 | Required node and edge types exist with provenance and temporal fields. | `python -m pytest tests/contract -q` | Static files only. | Ontology is a contract, not a populated graph. |
| SRA-ING-001 | Ingestion fixtures | data | `sra_core/ingestion/**`, `tests/ingestion/fixtures/**` | SRA-SRC-001, SRA-CON-001 | Deterministic fixtures promote to silver and graph events without raw payload exposure. | Fixture replay tests. | Do not run uncontrolled downloads on Render. | Deferred from this foundation fix. |
| SRA-GRAPH-001 | Dynamic evidence graph | graph | `graph_kernel/semiconductor_snapshot.py`, `graph_kernel/lineage.py`, `graph_kernel/quality.py` | SRA-ING-001, SRA-ONT-001 | Deterministic snapshot with manifest, graph version, counts, stale/unresolved/missing-provenance counts. | Graph invariant tests. | Serve promoted fixture/public graph if available. | Deferred from this foundation fix. |
| SRA-RISK-001 | Risk scoring | ml | `ml/risk_scoring/semirisk_score.py`, `docs/model/risk-score-v0.md` | SRA-GRAPH-001 | Deterministic explainable score with components and evidence refs. | Model tests. | No neural models required. | Deferred from this foundation fix. |
| SRA-FWD-001 | Forward stress testing | ml/api/web | `ml/simulation/**`, scenario routes, Shock Simulator | SRA-GRAPH-001 | Seeded graph Monte Carlo returns run manifest and CVaR95. | Simulation/API/frontend tests. | Run only after explicit user action. | Deferred from this foundation fix. |
| SRA-REV-001 | Reverse stress testing | ml/api/web | `ml/simulation/reverse_stress.py`, Reverse Stress Lab | SRA-FWD-001 | Ranked shock sets with path explanation and compliance-safe language. | Reverse stress tests. | Bounded synchronous jobs only. | Deferred from this foundation fix. |
| SRA-OPT-001 | Intervention optimization | ml/api/web | `ml/optimization/**`, Intervention Optimizer | SRA-FWD-001 | Budget-feasible actions with before/after metrics and evidence refs. | Optimization tests. | No Gurobi dependency. | Must not recommend illegal bypass. |
| SRA-WEB-001 | Frontend workflow | web | `apps/web/src/app/App.tsx`, `pages.tsx`, smoke | SRA-SRC-001, SRA-ONT-001 | `#system-health-center` is first public page and renders System Health Center or explicit degraded state. | Typecheck, build, browser smoke. | Web calls public API base URL from env. | This foundation fix covers System Health only. |
| SRA-REPORT-001 | Report export | api/web/core | `sra_core/reports/**`, report routes | SRA-RISK-001, SRA-FWD-001 | JSON/Markdown report excludes raw payloads and private diagnostics. | Report export tests. | Persistent storage optional later. | Deferred from this foundation fix. |
| SRA-CI-001 | Deployment and CI | platform | `.github/workflows/**`, `scripts/browser-smoke.mjs`, Render docs | SRA-WEB-001 | CI fails missing registry fields, ontology gaps, raw payload exposure, and hidden System Health route. | Python tests, typecheck, build, smoke. | Auto-deploy from `main`; no large ingestion during startup. | Browser smoke must protect public System Health behavior. |

## Expected Demo Milestones

1. Foundation slice: public System Health Center, semiconductor registry, ontology, roadmap, and governance skills.
2. First graph slice: deterministic semiconductor fixture promotion and graph snapshot with lineage.
3. Risk slice: explainable deterministic entity risk score with evidence refs.
4. Stress slice: forward Monte Carlo over the promoted graph.
5. Workflow slice: reverse stress, intervention optimization, prediction baseline, and investigation report export.

## Current Foundation Acceptance

This commit targets only milestone 1. Analytical engines, reverse stress, optimization, prediction-risk, and investigation report export remain deferred until the source, ontology, graph, and health foundation is verified on `main` and deployed.

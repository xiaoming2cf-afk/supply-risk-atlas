# Implementation Plan

## Phase 0 - Architecture Foundation

- Create monorepo, AGENTS.md, README, Python and TypeScript package metadata.
- Create ontology YAML for node, edge, event, and label types.
- Create Pydantic contracts and deterministic synthetic data.
- Create FastAPI health endpoint, frontend shell, CI, and tests.

## Phase 1 - Temporal Heterogeneous Graph Kernel

- Append-only edge event store.
- Point-in-time edge state materialization.
- Deterministic graph snapshots and graph diff.
- Time-aware path index and graph invariants.

## Phase 2 - Feature and Label Factory

- YAML feature and label registries.
- Point-in-time rolling-window feature generation.
- Label generation with versioning and quality report.

## Phase 3 - Model, Causal, and Simulation

- Dataset builder and sampler skeletons.
- Baseline model and DCHGT-SC skeleton.
- Counterfactual graph builder and shock simulation.

## Phase 4 - API, Frontend, and Reports

- OpenAPI-backed shared client.
- Executive-grade dashboard shell with mock/real API parity.
- Versioned reports and explanation paths.

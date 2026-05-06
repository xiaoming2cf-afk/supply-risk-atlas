# Multi-Agent Operating Model

SupplyRiskAtlas uses multiple focused agents working in parallel. This document defines how agents coordinate without blocking each other or overwriting work.

## Source of Truth

- `AGENTS.md` defines ownership lanes and repository-wide rules.
- This document defines day-to-day collaboration mechanics.
- `docs/quality-gates.md` defines checks that changes must satisfy.
- `docs/governance/real-data-governance.md` defines real-source license, freshness, schema, hygiene, and determinism evidence.
- `tests/e2e/` defines acceptance expectations for user-visible workflows.

## Agent Lanes

| Lane | Decision authority | Must coordinate with |
| --- | --- | --- |
| Product and frontend | UI workflows, visual states, client behavior | API and contracts for endpoint shape; QA and docs for acceptance changes |
| API and contracts | Endpoint semantics, shared type contracts, schema compatibility | Frontend for client behavior; data and ML for feature availability |
| Graph and core model | Entity graph, graph traversal, ontology use, graph invariants | Data and ML for inputs; API for served graph views |
| Data and ML | Feature generation, labels, training, evaluation, leakage controls | Graph and core model for topology; API for served predictions |
| Infrastructure | Runtime, deployment, environment, observability | All lanes when runtime contracts or secrets change |
| QA and docs supervisor | Governance docs, CI gates, acceptance descriptions, architecture and data-flow docs | All lanes when documented behavior changes |

## Real-Data Coordination

Real-data changes often cross lanes. The initiating agent remains responsible
for routing the change through the gates in `docs/quality-gates.md`.

- Data and ML owns source freshness, model leakage, and feature/label evidence.
- API and contracts owns schema validation and compatibility evidence.
- Graph and core model owns graph snapshot determinism and graph invariants.
- Infrastructure owns deployment boundaries, runtime logs, and secret handling.
- QA and docs supervisor owns gate documentation, changed-file routing, and CI hygiene checks.

Public no-key sources are the only allowed v1 sources. Raw source data, private
credentials, PII, and proprietary extracts must not be committed, printed in CI
logs, or uploaded as GitHub artifacts.

## Change Lifecycle

1. Orient: inspect the relevant directories and existing docs.
2. Scope: name the ownership lane, files, and expected behavior.
3. Implement: change only the files needed for the scoped outcome.
4. Validate: run local checks that match the risk of the change.
5. Handoff: list changed paths, checks run, skipped checks, and known follow-ups.

## Cross-Lane Changes

A cross-lane change is acceptable when it updates a contract between two lanes or when one lane cannot be validated without a small supporting edit in another lane.

Cross-lane edits must:

- Be documented in the final handoff.
- Avoid broad reformatting.
- Preserve existing public behavior unless the change is intentional and documented.
- Include or update the relevant quality gate.

## Documentation Rules

- Architecture changes update `docs/architecture/overview.md`.
- Data shape, lineage, or validation changes update `docs/data/data-flow.md`.
- Quality policy or CI changes update `docs/quality-gates.md`.
- User-visible workflow changes update `tests/e2e/`.
- Ownership or collaboration changes update `AGENTS.md` and this file.

## Definition of Done

A change is done when:

- The requested behavior or document outcome is present.
- The affected ownership lane is clear.
- Relevant tests or acceptance criteria exist.
- Local checks have been run, or skipped checks are explained with a concrete blocker.
- No unrelated files were reverted or reformatted.

# E2E Acceptance Suite

This directory defines end-to-end acceptance behavior for SupplyRiskAtlas. The current baseline is descriptive and should become executable as the frontend, API, graph, and data services are implemented.

## Files

- [supply-risk-atlas.feature](supply-risk-atlas.feature): Gherkin-style acceptance scenarios for core analyst workflows.

## Scope

E2E coverage should validate complete user outcomes across:

- Risk overview and portfolio triage.
- Supplier or facility detail investigation.
- Graph neighborhood exploration.
- Evidence and explanation review.
- Data freshness and degraded-state behavior.
- Export or handoff behavior when implemented.

## Scenario Requirements

Each scenario should include:

- A tag that identifies the gate, such as `@smoke`, `@risk`, `@graph`, `@explainability`, `@resilience`, or `@export`.
- A clear user role or system state.
- Observable acceptance criteria that can become automated assertions.
- No dependency on private credentials or production-only data.

## Execution Profiles

| Profile | Purpose | Expected environment |
| --- | --- | --- |
| Smoke | Fast confidence check for critical workflows | Local or CI preview |
| Full E2E | Complete user workflow validation | Integrated test environment |
| Resilience | Empty, stale, partial, or failed upstream data states | Controlled fixtures |

## Traceability

Scenarios should stay aligned with [architecture overview](../../docs/architecture/overview.md), [data flow](../../docs/data/data-flow.md), and [quality gates](../../docs/quality-gates.md).

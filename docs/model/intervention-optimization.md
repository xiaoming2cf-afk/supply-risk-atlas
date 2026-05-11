# Intervention Optimization v0.1

The intervention optimizer is a deterministic greedy baseline over the SemiRisk fixture graph. It selects budget-feasible resilience actions and reports simulation-based before/after normalized loss metrics. It does not use Gurobi, neural models, private exposure data, or financial loss estimates.

## Context

The optimizer consumes, in priority order:

1. `scenario_set`.
2. `forward_scenario_payload`.
3. `reverse_stress_payload` converted into scenario candidates.
4. A default fixture scenario if no context is supplied.

Outputs disclose `optimization_context_type`, `scenario_count`, `baseline_run_ids`, `before_simulation_run_ids`, and `after_simulation_run_ids`.

## Objective

Candidates are ranked by a risk-adjusted greedy value, but official before/after metrics come from rerunning forward Monte Carlo with adjusted scenario parameters. Heuristic estimates remain only as `heuristic_estimated_after_expected_loss` and `heuristic_estimated_after_cvar95`.

Compliance constraints are enforced by validation and by screening unsafe action wording. The optimizer never recommends evasion, sanctions circumvention, illegal rerouting, or disguise behavior.

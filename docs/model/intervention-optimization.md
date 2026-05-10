# Intervention Optimization v0.1

The intervention optimizer is a deterministic greedy baseline over the SemiRisk fixture graph. It selects budget-feasible resilience actions and reports before/after normalized loss metrics. It does not use Gurobi, neural models, or private exposure data.

## Candidate Actions

- `add_alternative_supplier`
- `increase_inventory_buffer`
- `regional_diversification`
- `improve_recovery_rate`
- `add_policy_monitoring`
- `route_redundancy`
- `qualify_backup_material`

Every action includes cost, target node, expected normalized effect, assumptions, constraints, evidence refs, and a compliance note. Policy actions are limited to monitoring and compliance review.

## Objective

Candidates are ranked by a risk-adjusted value:

```text
((expected_loss_reduction * (1 - beta)) + (cvar95_reduction * beta)) / cost
```

The greedy selector stops when the budget or `max_actions` limit is reached. Outputs include random, highest-risk, cheapest-first, and proposed greedy baselines.

All fixture outputs include `fixture_graph:not_production_ready`.

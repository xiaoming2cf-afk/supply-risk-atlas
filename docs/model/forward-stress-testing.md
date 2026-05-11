# Forward Stress Testing v0.1

The forward stress engine runs deterministic, graph-based Monte Carlo over the SemiRisk-KG v0.1 fixture graph. It is a bounded synchronous baseline for analyst-triggered stress tests and is not a production loss model.

## Inputs

In addition to scenario type, targets, severity/duration distributions, iterations, seed, `as_of_time`, and optional `graph_version`, the request accepts:

- `loss_mode`: default `resilience_integral_loss`.
- `propagation_mode`: default `auto_semiconductor`.
- `functionality_metric`: default `capacity_fulfillment`.
- `weighting_method`: default `literature_proxy_not_calibrated`.

`affected_mean` remains available only as a legacy baseline loss mode.

## Propagation

`auto_semiconductor` uses:

- `leontief_bottleneck` for `requires` and `depends_on` critical input chains.
- `noisy_or` for `restricted_by` and `impacted_by` policy/event exposure.
- `additive_cap` for other dependency, route, supply, and participation links.

The legacy `max` propagation mode is still selectable for comparisons but is not the default.

## Loss Function

The default loss is `resilience_integral_loss`, a normalized integral of functionality loss over time. Outputs also include `graph_weighted_loss`, `demand_fulfillment_loss`, `capacity_functionality_loss`, and `affected_mean` for auditability.

All losses are normalized scores. They are not dollar losses.

## Output Manifest

Every run includes `run_id`, `seed`, `graph_version`, `source_manifest_id`, `simulation_version`, `loss_mode`, `propagation_mode`, `functionality_curve`, `formula_refs`, `calibration_status`, warnings, assumptions, and evidence refs.

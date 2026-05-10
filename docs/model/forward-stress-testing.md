# Forward Stress Testing v0.1

The forward stress engine runs deterministic, graph-based Monte Carlo over the SemiRisk-KG v0.1 fixture graph. It is a bounded synchronous baseline for analyst-triggered stress tests and is not a production loss model.

## Inputs

- `scenario_type`: one of `earthquake`, `export_control`, `material_shortage`, `demand_spike`, `port_disruption`, `factory_shutdown`, `cyber_incident`, or `power_outage`.
- `targets`: fixture graph node IDs or simple selectors.
- `severity_distribution`: `fixed`, `triangular`, `beta`, `uniform`, or bounded normal parameters.
- `duration_days_distribution`: `fixed`, `triangular`, or `lognormal` parameters.
- `iterations`: capped at 5000 for lightweight deployment.
- `seed`, `as_of_time`, optional `graph_version`, and optional `assumptions`.

## Algorithm

For each iteration, the engine samples severity and duration using `random.Random(seed)`, initializes normalized target-node loss, and propagates stress over `depends_on`, `requires`, `supplies`, `produces`, `participates_in`, `routes_through`, `restricted_by`, and `impacted_by` edges. Edge weight and confidence control propagation strength. Available substitutability, inventory-buffer, and recovery-rate attributes reduce retained impact; missing attributes use documented conservative defaults.

Outputs are normalized loss scores only. Dollar losses are intentionally disabled unless a future gate adds licensed private exposure data.

## Output Manifest

Every run includes:

- `run_id`
- `seed`
- `graph_version`
- `source_manifest_id`
- `simulation_version: semirisk_forward_mc_v0.1`
- `timestamp`
- percentile losses, `cvar_95`, affected nodes, top transmission paths, warnings, assumptions, and evidence refs.

All fixture outputs include `fixture_graph:not_production_ready`.

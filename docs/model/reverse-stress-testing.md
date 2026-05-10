# Reverse Stress Testing v0.1

Reverse stress testing asks what small or plausible shock sets can breach or approach a normalized failure threshold. The first implementation uses the SemiRisk-KG v0.1 fixture graph only and evaluates candidates through the forward Monte Carlo engine.

## Algorithm

1. Generate shock candidates from fixture graph nodes and their incident evidence.
2. Score plausibility from severity, evidence confidence, shock type, and combination size.
3. Evaluate each candidate with the forward Monte Carlo engine.
4. Keep the best beam and expand combinations up to `max_combination_size`.
5. Rank shock sets by threshold satisfaction, plausibility cost, CVaR95, expected loss, and deterministic ID.

The implementation returns random and highest-criticality baselines plus the proposed beam-search output. Policy-related shocks are framed only as compliance-safe resilience planning and compliance review.

## Output

Every run includes `run_id`, `seed`, `graph_version`, `source_manifest_id`, `simulation_version: semirisk_reverse_stress_v0.1`, timestamp, ranked shock sets, baseline comparison, warnings, assumptions, and evidence refs.

All fixture outputs include `fixture_graph:not_production_ready` and exclude raw payloads.

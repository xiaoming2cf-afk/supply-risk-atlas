# Reverse Stress Testing v0.1

Reverse stress testing asks what small or plausible shock sets can breach or approach a normalized failure threshold. The first implementation uses the SemiRisk-KG v0.1 fixture graph only and evaluates candidates through the forward Monte Carlo engine.

## Thresholds

Failure thresholds are normalized to `0..100`.

- `0.35` becomes `35` and emits `failure_threshold_normalized_from_unit_interval`.
- `35` remains `35`.
- Negative thresholds fail validation.

Outputs include `failure_threshold_input`, `failure_threshold_normalized`, and `threshold_metric_basis`.

## Algorithm

The search uses greedy beam search and ranks shock sets by threshold satisfaction, selected loss mode, CVaR95, expected loss, plausibility cost, and explanation quality. The default loss mode is `resilience_integral_loss`.

Shock set explanations disclose `loss_mode`, `propagation_mode`, affected functionality, and critical dependency pathways. Policy scenarios are compliance-safe resilience planning only.

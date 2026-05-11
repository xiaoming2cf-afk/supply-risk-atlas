# Risk Score v0

Risk Score v0 is a deterministic fixture-graph model for the SemiRisk-KG v0.1 platform slice. It is not a production risk model and does not use neural networks, random forests, private exposure data, or fabricated business metrics.

## Default Method

- Feature version: `semirisk_risk_score_likelihood_impact_v0.1`.
- Scoring method: `likelihood_impact_vulnerability_framework`.
- Formula version: `semirisk_liv_framework_v0.1`.
- Calibration status: `fixture_proxy_not_calibrated`.
- Formula:

```text
score = 100 * likelihood * impact * vulnerability_modifier
```

The formula follows the NIST principle that risk assessment combines likelihood and impact. The vulnerability modifier is an implemented proxy that reflects concentration, substitution gap, recovery difficulty, and policy/event exposure. The proxy is explicitly not calibrated.

## Baseline Method

The previous weighted score is still available only as an explicit baseline:

- Feature version: `semirisk_risk_score_heuristic_v0.1`.
- Scoring method: `heuristic_weighted_sum_baseline`.
- Weight source: `heuristic_unvalidated`.
- Calibration status: `not_calibrated`.
- Required warnings: `heuristic_weights:not_literature_calibrated` and `not_for_production_decision`.

The historic `company:tsmc` score of `58.33` belongs to this baseline, not to the default API score.

## Required Metadata

Every score includes `graph_version`, `source_manifest_id`, `as_of_time`, `feature_version`, `formula_refs`, `evidence_refs`, `calibration_status`, and `fixture_graph:not_production_ready`.

## Limitations

The score uses fixture proxy inputs only. Formula references identify source principles and implemented proxies; they are not validated coefficients or production decision rules.

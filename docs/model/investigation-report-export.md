# Investigation Report Export v1

`semirisk_investigation_report_v0.1` generates an auditable report from fixture-labeled SemiRisk platform outputs. It is not a production report and does not run live ingestion.

## Methodology Disclosure

JSON and Markdown reports include:

- risk scoring method
- weighting method
- calibration status
- formula refs
- loss mode
- propagation mode
- resilience integral loss
- functionality curve summary
- HHI/concentration summary

Markdown reports include `Methodology`, `Formula Sources`, and `Model Limitations` sections.

## Safety

Reports are generated from API-visible summaries only. They exclude raw source payloads, credentials, private diagnostics, private exposure data, request internals, and hidden fields. Policy-related sections are framed as resilience planning, monitoring, approved qualification, diversification, inventory, recovery, and compliance review.

Required warnings include `fixture_graph:not_production_ready`, `not_financial_loss`, and `not_production_decision`. If a caller includes the heuristic baseline, the report must also disclose `heuristic_baseline`.

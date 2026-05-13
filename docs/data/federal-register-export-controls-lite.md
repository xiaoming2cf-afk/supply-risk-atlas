# Federal Register Export Controls Lite Connector

`federal_register_export_controls_lite` is a fixture-first connector for public Federal Register export-control policy metadata.

## Safety Boundary

- Fixture mode is required for tests and CI.
- Live mode is disabled by default and currently returns a controlled unavailable result.
- Terms review is required before any live ingestion.
- Raw rule text and bulk payloads are not exposed.
- Output is limited to compliance-risk and resilience-planning summaries with source lineage.
- The platform must provide compliance-risk summaries only and no control-avoidance guidance.

## Promoted Records

The connector promotes fixture records to `export_control_policy_event` summaries that may support policy-restriction edges in the promoted graph.

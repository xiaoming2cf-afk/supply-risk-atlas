# Consolidated Screening List Lite Connector

`consolidated_screening_list_lite` is a fixture-first connector for public screening-list metadata.

## Safety Boundary

- Fixture mode is required for tests and CI.
- Live mode is disabled by default and currently returns a controlled unavailable result.
- Raw screening-list payloads are not exposed through API, frontend, reports, or logs.
- Output is limited to compliance-risk awareness summaries and source lineage.
- The platform must provide compliance-risk summaries only and no control-avoidance guidance.

## Promoted Records

The connector promotes records to `sanctions_screening_event` summaries and compliance-risk graph context. It does not make legal determinations.

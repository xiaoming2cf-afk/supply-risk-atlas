# Investigation Report Export v1

`semirisk_investigation_report_v0.1` generates an auditable report from the
fixture-labeled SemiRisk platform outputs. It is not a production report and
does not run live ingestion.

## Inputs

- `entity_id`: graph node id, default `company:tsmc`.
- `include_entity_risk`: includes Risk Score v0 when true.
- `forward_scenario_payload`: optional forward Monte Carlo request.
- `reverse_stress_payload`: optional reverse stress request.
- `optimization_payload`: optional intervention optimization request.
- `format`: `json` or `markdown`.

## Output Contract

The report includes:

- `report_id`, `report_version`, and `generated_at`.
- Entity identity and optional risk score.
- Optional forward stress, reverse stress, and optimization sections only when
  the caller supplies the corresponding payload.
- `evidence_summary`, graph context, version metadata, warnings, assumptions,
  limitations, and a compliance-safe use note.
- `raw_payload_excluded: true` and `private_diagnostics_excluded: true`.

The version block includes `graph_version`, `source_manifest_id`,
`feature_version`, `simulation_version`, `optimization_version`, and
`report_version` where available.

## Safety

The report is generated from API-visible fixture graph summaries only. It does
not include raw source payloads, credentials, private diagnostics, private
exposure data, request internals, or hidden fields. Policy-related sections are
framed as resilience planning, monitoring, approved qualification,
diversification, inventory, recovery, and compliance review.

## Current Limitations

- The graph is the promoted test fixture graph and is always labeled
  `fixture_graph:not_production_ready`.
- Report generation is synchronous and bounded for Render-compatible hosting.
- Persistent report storage is deferred; `POST /api/v1/reports/investigation`
  returns the generated report directly.

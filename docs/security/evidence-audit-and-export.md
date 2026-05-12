# Evidence Audit And Export

Supply Risk Atlas exports are bounded research artifacts. They are not production data extracts and they do not include raw source payloads.

## API Surface

- `GET /api/v1/analytics/tables/{table_id}`
- `GET /api/v1/analytics/export/{table_id}?format=json|csv|markdown`

Supported table IDs include source catalog, source status, connector status, evidence refs, graph quality, risk rankings, trade flows, policy events, hazard events, and logistics facilities.

## Security Boundary

Exports include graph and source metadata:

- `graph_version`
- `source_manifest_id`
- `data_mode`
- `graph_mode`
- `export_time`
- `warnings`

Rows are capped at 500 maximum, with a lower default limit of 50. The sanitizer removes fields whose names indicate raw source content, payload storage, secrets, tokens, cookies, private diagnostics, authorization material, passwords, or internal path data. External text is bounded and strips script-like content before display.

## Limitations

The current exports summarize fixture/proxy/promoted public-evidence data. They are not production-ready, not financial-loss outputs, and not live data extracts. Compliance-related rows are for resilience planning and audit context only; they must not be used as workaround or evasion guidance.

# Report Sanitization

Investigation reports are public API outputs. They must be safe to render as JSON or Markdown without exposing raw inputs, private diagnostics, secrets, internal paths, or active HTML/script content.

## Input Handling

- `format` is restricted to `json` or `markdown`.
- User text is length-bounded and HTML-escaped.
- Unsafe compliance-language is rejected with a controlled error envelope.
- Secret-like text values are redacted.
- Keys containing raw payloads, source payloads, secrets, tokens, API keys, passwords, cookies, authorization, or private diagnostics are dropped.

## Output Requirements

Report outputs must include:

- `report_id`
- `report_version`
- `versions.graph_version`
- `versions.source_manifest_id`
- relevant feature, simulation, and optimization versions when included
- methodology, formula refs, warnings, assumptions, limitations, and model limitations
- `raw_payload_excluded: true`
- `private_diagnostics_excluded: true`

Report outputs must not include:

- raw source payloads or source records
- private diagnostics, stack traces, or local paths
- secret-like strings
- active `<script>` or event-handler content
- unsafe compliance or rerouting instructions

## Test Coverage

Security tests cover JSON and Markdown reports, unsupported format rejection, raw payload dropping, private diagnostic dropping, secret-like text redaction, and unsafe compliance-language rejection.

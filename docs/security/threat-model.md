# Threat Model

## Scope

This threat model covers the local API, Next.js web app, shared packages, fixture graph, validation experiments, run history, reports, deployment configuration, and CI checks. The system is fixture/proxy based and not production ready.

## Assets

- Source manifests, graph versions, formula/version metadata, evidence refs, and fixture limitations.
- Sanitized run summaries for forward scenario, reverse stress, optimizer, and investigation report workflows.
- Report exports in JSON and Markdown.
- API availability and bounded compute for simulation, search, and optimization endpoints.
- Deployment configuration such as CORS origins and API base URLs.

## Trust Boundaries

- Browser to API: user-controlled request bodies, query params, headers, and route hashes cross into API/UI logic.
- API to model code: validated payloads cross into fixture graph simulation, reverse stress, optimizer, and report generation.
- Evidence text to UI/report: evidence summaries are treated as untrusted display content.
- Run history: model results are reduced to sanitized summaries before storage.
- CI/deployment: workflow files and Render environment variables control what checks run and which origins are allowed.

## Attacker-Controlled Inputs

- Scenario payloads, target lists, candidate scopes, thresholds, iteration counts, budgets, report format, and report section options.
- User-provided notes or assumptions in report and scenario payloads.
- Evidence text or fixture source summaries if future loaders import external content.
- Request size, content type, CORS origin, and missing-route probes.
- Deployment environment variables if misconfigured by an operator.

## Required Invariants

- Raw payloads, secrets, private diagnostics, internal paths, and PII are never echoed in API responses, reports, run history, smoke artifacts, or logs.
- Unsafe export-control, sanctions, rerouting, or evasion language is rejected or neutralized rather than transformed into operational advice.
- HTML/script injection in report fields or evidence text is escaped or dropped.
- Iteration counts, beam width, combination size, action count, and request size stay bounded.
- Fixture data remains visibly labeled as fixture/proxy data and is not presented as production or financial-loss output.
- Analytical outputs keep graph/version/source/warning/evidence metadata.

## Primary Failure Modes

- Prompt injection in evidence text causes the UI or report generator to repeat instructions or unsafe wording.
- HTML/script injection in report fields renders active content in JSON/Markdown previews.
- Unsafe compliance-language is accepted and echoed in a model or report output.
- Raw payload leakage exposes source records or private diagnostic fields.
- API abuse through large iterations, beam width, combination size, request body size, or excessive action count.
- Stale fixture data is mistaken for production data because warnings or version metadata are absent.
- Render CORS/proxy misconfiguration allows unexpected origins or sends web traffic to the wrong API base URL.
- Secret leakage in logs, run summaries, report payloads, or CI artifacts.

## Current Controls

- FastAPI middleware enforces request-size bounds and security headers.
- Validation functions enforce enums and numeric caps for forward, reverse, optimizer, and report endpoints.
- Sanitizers drop raw/private/secret-like keys and redact secret-like text values.
- Report generation returns sanitized JSON/Markdown and explicit `raw_payload_excluded` and `private_diagnostics_excluded` flags.
- Run history stores bounded sanitized summaries only.
- CI runs security tests, raw payload checks, source readability checks, and the security scan script.

## Residual Risk

- The run store is in-memory and not a durable audit log.
- The graph and validation outputs are deterministic fixture/proxy artifacts.
- Future live connectors would require separate source licensing, PII, retention, and ingestion threat modeling before enablement.
- Deployed Render behavior can differ from local smoke if environment variables or proxy routing drift.

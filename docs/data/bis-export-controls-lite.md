# BIS Export Controls Lite

`BisExportControlsLiteConnector` is a fixture-first connector for public export
control policy metadata.

Fixture promotion emits `export_control_policy_event` summaries with
jurisdiction, policy type, policy title, publication date, affected item
categories, provenance URL, payload hash, source refs, confidence, and
license/terms ref.

The output is compliance-risk and resilience-planning context only. It does not
provide operational restricted-trade guidance.

Live fetching is disabled by default and not implemented for CI or startup.

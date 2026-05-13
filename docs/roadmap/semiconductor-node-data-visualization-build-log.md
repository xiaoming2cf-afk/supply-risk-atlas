# Semiconductor Node Data Visualization Build Log

## Gate 0 - Baseline And Quality Guard

- Current HEAD: `9cbb0e9`
- Gate name: baseline and readability guard
- Files changed:
  - `docs/roadmap/semiconductor-node-data-visualization-build-log.md`
- Commands run:
  - `python -m pytest tests/quality -q`
  - `python -m pytest tests/api -q`
  - `python -m pytest -q`
  - `npm.cmd --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run build`
  - `npm.cmd run smoke:web`
- Pass/fail: pass
- Evidence:
  - Quality tests passed: 8 tests.
  - API tests passed.
  - Full repository pytest passed.
  - Web typecheck passed.
  - Web production build passed.
  - Browser smoke passed 37 checks.
  - Readability tests cover `services/api`, `graph_kernel`, `ml`, `packages/sra_core/sra_core`, and `scripts`.
  - `tests/quality/test_service_layer_readability.py` exists and checks service/route modules for readable physical lines.
- Source/legal notes:
  - No live ingestion was run.
  - No raw payloads, bulk source data, private diagnostics, secrets, internal paths, cookies, authorization headers, API keys, PII, or evasion guidance were introduced.
- Limitations:
  - Current platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.
  - Generated local SQLite runtime files are local state and must not be committed.
- Next gate:
  - Proceed to Gate 1 canonical semiconductor supply-chain chain map.

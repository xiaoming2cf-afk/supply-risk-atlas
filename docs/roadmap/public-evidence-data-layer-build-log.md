# Public Evidence Data Layer Build Log

This log records the Public Evidence Data Layer and Persistent Platform Foundation gates. The platform remains a fixture/proxy/promoted-public-evidence research system, not production ready and not a production decision or financial-loss engine.

## Preflight Baseline

- Current HEAD: `8f7094238b1eeeb4ee0690cf6a760e51d7449904`
- Base visible main: `97041b54573f35f8a771baa75c407ee2ba9e45d3`
- Branch: `code-quality-repair`
- Preserved local files:
  - Untracked `apps/web/AGENTS.md`
  - Untracked `apps/web/CLAUDE.md`
- Gate name: preflight baseline after Gate 0 quality repair
- Files changed:
  - `docs/roadmap/public-evidence-data-layer-build-log.md`
- Commands run:
  - `python -m pytest tests/quality -q`
  - `python -m pytest tests/api -q`
  - `python -m pytest -q`
  - `npm.cmd --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run build`
  - `npm.cmd run smoke:web`
  - `npm.cmd run smoke:web` rerun after first smoke timeout
- Pass/fail status:
  - `python -m pytest tests/quality -q`: pass
  - `python -m pytest tests/api -q`: pass
  - `python -m pytest -q`: pass
  - `npm.cmd --workspace apps/web run typecheck`: pass
  - `npm.cmd --workspace apps/web run build`: pass
  - First `npm.cmd run smoke:web`: fail, browser navigation timeout at `about:blank`
  - Second `npm.cmd run smoke:web`: pass, 26 checks
- Failures and exact causes:
  - First browser-smoke run failed with `Timed out waiting for browser condition. Last state: "about:blank"` in `scripts/browser-smoke.mjs`; rerun passed without code changes.
- Limitations:
  - No deployed smoke was run in this preflight.
  - CI has not run for local commits until pushed.
- Source/legal notes:
  - No public data ingestion was run.
  - No raw payloads, secrets, private diagnostics, or downloaded bulk data were added.
- Next gate decision:
  - Proceed to Gate 1 SQLite persistent storage foundation.

## Gate 0 - Quality Guard Completion

- Current HEAD before Gate 0: `97041b54573f35f8a771baa75c407ee2ba9e45d3`
- Gate commit: `8f7094238b1eeeb4ee0690cf6a760e51d7449904`
- Gate name: anti-minification readability guard
- Files changed:
  - `tests/quality/test_python_source_readability.py`
  - `tests/quality/test_service_layer_readability.py`
- Commands run:
  - `python -m pytest tests/quality -q`
  - `python -m pytest tests/api -q`
  - `python -m pytest -q`
  - `npm.cmd --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run build`
  - `npm.cmd run smoke:web`
- Pass/fail status: pass
- Evidence:
  - Readability guard covers `services/api`, `graph_kernel`, `ml`, `packages/sra_core/sra_core`, and Python scripts under `scripts`.
  - Dedicated service-layer readability test covers `services/api/services/*.py` and `services/api/routes/*.py`.
  - Named guard files passed:
    - `services/api/services/graph_service.py`: 515 LF lines in git blob
    - `services/api/services/risk_service.py`: 78 LF lines in git blob
    - `services/api/services/scenario_service.py`: 60 LF lines in git blob
    - `services/api/services/system_health_service.py`: readable multi-line module
    - `services/api/routes/graph.py`: 77 LF lines in git blob
  - Graph view endpoints returned HTTP 200 success for view/focus/clusters/path-view during Gate 0 verification.
  - Evidence-context safety copy remains present: `This is not a supply-chain dependency edge.`
- Limitations:
  - Gate 0 does not add storage, source registry, connectors, or promoted graph features.
- Source/legal notes:
  - No live ingestion was run.
  - No public-source payloads were added.
- Next gate decision:
  - Proceed to Gate 1 after preflight baseline.

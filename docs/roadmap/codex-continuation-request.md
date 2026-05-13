# Codex Continuation Request

## Current Status

- Latest pushed commit: `28f06cda3930a05ce0484d46c036da18f0798bd1`
- GitHub Actions:
  - `ci #32`: success
  - `Quality Gates #32`: success
- Local final acceptance: passed.
- Deployed API/Web status: stale. The API version endpoint still reports commit `9cbb0e927a8bbcf66e05f19e5d3d70714f34204f`.
- Deployed smoke: best-effort failure because Render is still serving the old build.

## Required Manual Render Step

1. Redeploy Render service `supply-risk-atlas-api` from latest `main`.
2. Redeploy Render service `supply-risk-atlas-web` from latest `main`.
3. If the web UI remains stale, clear the web service build cache and redeploy again.
4. Verify `/api/v1/version` reports `28f06cda3930a05ce0484d46c036da18f0798bd1`.
5. Rerun deployed smoke:

```powershell
npm.cmd run smoke:web -- --mode=deployed
```

## Constraints For The Next Run

- Do not expose secrets, cookies, tokens, private diagnostics, internal account details, or raw payloads.
- Keep the canonical geography terminology: `region:china_taiwan` / `中国台湾`, with parent `country:CN` / `中国`.
- Evidence-context links remain non-dependency inspection links.
- The platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.

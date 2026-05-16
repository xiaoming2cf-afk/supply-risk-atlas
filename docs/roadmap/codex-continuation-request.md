# Codex Continuation Request

## Current Status

- Latest pushed commit: `8c04c14`.
- Branch: `main`.
- GitHub Actions for recent pushed commits:
  - `8942950`: `ci` and `Quality Gates` passed.
  - `9674e60`: `ci` and `Quality Gates` passed.
  - `8c04c14`: `ci` and `Quality Gates` passed.
- Render deployment status: `deployed_stale_or_unverified`.
  - `python scripts/check-deployed-version.py --expected-commit 8c04c14 --timeout 20` returned sanitized `stale_or_unverified`.
  - Deployed smoke reached a controlled unavailable state with sanitized endpoint diagnostics.
  - No deployed-complete claim is made until API/Web version evidence matches the latest pushed commit and deployed smoke passes or reports only expected controlled degradation.
- Local validation already recorded in the roadmap log:
  - full pytest passed.
  - web typecheck/build passed.
  - local browser smoke passed.
  - geography and raw-payload guards passed.

## Computer Use / GPT Pro Handoff Status

- Project-scoped Computer Use was used for the project ChatGPT conversation and limited Chrome verification only.
- No credentials, cookies, tokens, screenshots with secrets, raw payloads, private diagnostics, account details, or unrelated personal content were copied into the repo log.
- Private operational ChatGPT conversation links are intentionally not recorded here.
- GPT Pro second-round review returned:
  - `judgment: PASS`
  - `blocking_issue: NONE`
  - `narrow_patch_required: NONE`
  - next authorized action: run R1/R2/R3/R4 review before starting the M1-4 W6 candidate inventory.

## R1-R4 Review Status

- R1 implementation reliability: PASS.
- R2 deployment evidence: initially FAIL because short SHA and full SHA were compared by exact string in the deployed checker.
- R3 relationship semantics: PASS.
- R4 safety/governance: initially FAIL because runtime artifacts were not explicitly ignored/scanned, a private ChatGPT URL was recorded in this file, stale deployment text overclaimed an old live commit, and Web HTML commit detection could false-pass on a 7-character SHA.

## Current Narrow Patch

- Make deployed API commit matching accept only valid Git SHA hex prefixes.
- Make Web commit visibility conservative: no 7-character arbitrary HTML match.
- Ignore `data/runtime/` while preserving local files.
- Fail raw/private payload checks if runtime databases, `.raw`, `.parquet`, pickle, or other raw runtime artifacts are tracked.
- Keep deployment status as `deployed_stale_or_unverified` until Render version evidence is current.

## Request For Next Prompt

请审查当前 Codex 完成结果，并给出下一轮 prompt。

## Constraints For The Next Run

- Preserve existing public pages and API endpoints.
- Do not enable live connector fetch during import, tests, CI, app startup, or Render startup.
- Do not expose raw payloads, secrets, cookies, tokens, private diagnostics, local filesystem paths, private operational URLs, or PII.
- Keep canonical geography terminology: `region:china_taiwan` / `中国台湾`, parent `country:CN` / `中国`.
- Evidence-context links remain non-dependency inspection links.
- Keep supply, demand, production dependency, and evidence-context relationship classes separated.
- The platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.

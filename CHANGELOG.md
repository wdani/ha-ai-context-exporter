# Changelog

All notable changes to this project will be documented in this file.

## 0.0.9 - 2026-04-18

### Changed
- Improve dashboard discovery robustness by accepting small explicit wrapper shapes from readable `/lovelace/dashboards` and `/lovelace/config` payloads.
- Preserve compact `dashboard` export semantics with counts only: `dashboards`, `views`, and `cards`.
- Keep request logging token-safe by logging the normalized local path instead of the raw ingress-prefixed request path.
- Keep discovery strictly read-only with the existing local GET-only Core Proxy architecture and no new dashboard endpoint families, transport paths, relationship logic, or entity extraction.
- Bump version from `0.0.8` to `0.0.9`.
## Unreleased - 2026-04-18

### Docs
- Document that no additional GET-compatible Areas / Devices fallback path has been validated inside the current backend architecture.
- Keep Areas / Devices discovery conservative: direct readable endpoints only, no WebSocket/RPC bridge, no POST-based template fallback, and no inferred relationship data.
- Keep the application version at `0.0.8` because no functional fallback code was shipped.

## 0.0.8 - 2026-04-18

### Changed
- Improve Areas / Devices discovery robustness by counting direct list payloads and small explicit wrappers from readable `/areas` and `/devices` responses.
- Preserve compact `areas_devices` export semantics: `available` when both counts are readable, `partial` when only one count is readable, and honest unavailable/unauthorized reasons otherwise.
- Keep discovery strictly read-only with local GET requests only and no relationship, entity-context, dashboard, integration, auth, or UI changes.
- Bump version from `0.0.7` to `0.0.8`.
## 0.0.7 - 2026-04-18 (docs)

### Docs
- Add the new-chat/Codex guide and standard start prompt to the central standard-context lists.
- Standardize the documented version source path as `ha_ai_context_exporter/rootfs/app/version.py`.

## 0.0.7 - 2026-04-17 (docs)

### Docs
- Add official new-chat/Codex guide at `docs/ai/AI_NEW_CHAT_AND_CODEX_GUIDE.md`.
- Add official standard start prompt at `docs/ai/AI_STANDARD_STARTPROMPT.md`.
- Clarify the preferred one-chat, one-task, one-branch, one-review, one-merge workflow in `docs/development/AI_WORKFLOW.md`.
- Document the required Codex handoff blocks: COMMIT SUMMARY, PR / MERGE DESCRIPTION and NEXT CHAT START PROMPT.

## 0.0.7 - 2026-04-12

### Changed
- Improve integrations discovery quality by normalizing dotted component names (e.g. `mqtt.sensor`) to main integrations (e.g. `mqtt`) with stable deduplication.
- Introduce compact integration classification via `kind` (`user_integration` / `core_component`) while keeping core/internal components visible in `items`.
- Prioritize `user_integration` entries over `core_component` in `top_items` with stable alphabetical ordering and keep compact max-10 output.
- Bump version from `0.0.6` to `0.0.7`.

## 0.0.7 - 2026-04-12 (docs)

### Docs
- Repair `docs/ai/AI_DEVELOPMENT_TREE.md` formatting by removing accidental escaped newline sequences and restoring normal Markdown line breaks.
- Apply minimal roadmap status wording updates to reflect current integrations cleanup state.


## 0.0.6 - 2026-04-12

### Docs
- Add `docs/ai/AI_DEVELOPMENT_TREE.md` as official development tree/roadmap document from the provided source file.
- Update `review_bundle.md` and archive it as `docs/review_bundles/2026-04-12_0.0.6_ai-development-tree.md`.

## 0.0.6 - 2026-04-11

### Changed
- Implement first real read-only integrations discovery using `config.components` as primary source and cautious fallbacks from `services`/`states`.
- Add compact integrations fields: `count`, `items`, `top_items` with consistent semantic status.
- Bump development version from `0.0.5` to `0.0.6`.

## 0.0.5 - 2026-04-11

### Changed
### Docs
- Add persistent AI project documentation set under `docs/ai/`.
- Add AI development workflow doc under `docs/development/AI_WORKFLOW.md`.
- Add contribution guideline under `.github/CONTRIBUTING.md`.
- Archive technical review bundle at `docs/review_bundles/2026-04-11_0.0.5_ai-project-docs.md`.

- Improve discovery semantics and coverage for export categories (`system`, `areas_devices`, `dashboard`) with consistent partial/available/unavailable status handling.
- Make core proxy base explicit (`http://supervisor/core/api`) and avoid path-duplication risks.
- Increase central request timeout to 5 seconds for more robust local proxy reads.

## 0.0.4 - 2026-04-11

### Changed
- Switch primary Home Assistant read access to the official Core Proxy (`homeassistant_api: true`) using `http://supervisor/core/api/...` with `SUPERVISOR_TOKEN` for read-only GET requests.
- Add `/api/ha-auth-debug` endpoint for token-safe proxy/readability diagnostics.
- Bump development version from `0.0.3` to `0.0.4`.

## 0.0.3 - 2026-04-10

### Fixed
- Fix Home Assistant add-on schema/options compatibility by removing the default value for optional `ha_token` (`options: {}` with `schema: ha_token: "password?"`).
- Bump development version from `0.0.2` to `0.0.3`.


# Changelog

All notable changes to this project will be documented in this file.

## Unreleased - 2026-04-18

### Repository Hygiene
- Expand `.gitattributes` LF normalization coverage for the tracked text file types currently used in the repository, including Markdown, YAML, HTML, CSS, dotfiles, and `LICENSE`, to reduce CRLF-only working-tree noise on Windows.
- Keep this as a repository hygiene change only, with no exporter behavior changes and no version bump.

### Docs
- Document the dashboard GET path investigation: no additional validated Core Proxy REST GET path was found beyond the existing Lovelace probes, so no dashboard fallback code or version bump was added.
- Remove obsolete `docs/startvorlage für neuen chat-md`; the active official start guidance remains in the AI docs.

## 0.0.15 - 2026-04-19

### Changed
- Extend best-effort compact entity masking beyond literal dotted IPv4 values to the evidenced compact leak categories found in the latest real 0.0.14 export: underscored IPv4 fragments in `entity_id`, MAC-like identifiers, SSID/Wi-Fi context states, geocoded/address context states, and person-derived tokens from `person` entities.
- Preserve compact entity ordering by sorting on the original logical `entity_id` before applying output masking.
- Keep compact item structure, export keys, category names, and the `important_attributes` whitelist unchanged.
- Add the Home Assistant add-on option `allow_sensitive_values`, defaulting to `false`; only explicit boolean `true` allows compact sensitive values to remain unmasked.
- Add best-effort privacy warnings to the export `warnings` list, Markdown rendering, the existing export UI surface, and README text.
- Bump both the application version source and Home Assistant add-on metadata from `0.0.14` to `0.0.15`.

## 0.0.14 - 2026-04-19

### Changed
- Mask literal IPv4 address values in compact `entities.items` `state` and plain-string `friendly_name` values as `[redacted_ipv4]`, based on the first targeted sensitive-values check of a real 0.0.13 compact export.
- Keep compact entity item structure unchanged: no new fields, no renamed keys, no `raw_attributes`, no relationship modeling, and no export category redesign.
- Keep `entity_id`, derived `domain`, sorting by `entity_id`, and the string-only `important_attributes` whitelist unchanged.
- Bump the application version source from `0.0.13` to `0.0.14`.

### Docs
- Refresh AI validation notes to state that real compact `unit_of_measurement` and `state_class` examples are now confirmed.
- Keep validation notes open for `entity_category` real-export evidence and non-string whitelisted raw values, because the attached export did not confirm those cases.

## 0.0.13 - 2026-04-19

### Changed
- Remove the artificial 50-item cap from compact `entities.items`; all eligible compact items from readable `/states` data are now returned after the existing stable `entity_id` sort.
- Keep the compact entity item shape unchanged: `entity_id`, derived `domain`, direct `state`, direct plain-string `friendly_name`, and optional whitelisted string-only `important_attributes`.
- Keep the export read-only and GET-only with no `raw_attributes`, no relationship modeling, no dashboard/areas/devices/integrations changes, no YAML/file parsing, and no payload schema redesign.
- Bump version from `0.0.12` to `0.0.13`.

## 0.0.12 - 2026-04-19

### Changed
- Add the second small `important_attributes` refinement to compact `entities.items` by whitelisting string `entity_category` values from readable `/states.attributes`.
- Keep the existing compact entity fields unchanged: `entity_id`, derived `domain`, direct `state`, and direct plain-string `friendly_name`.
- Keep the existing `important_attributes` behavior unchanged for `device_class`, `state_class`, and `unit_of_measurement`; omit `important_attributes` entirely when no whitelisted string values are present.
- Keep the export read-only and GET-only with no `raw_attributes`, no relationship modeling, no dashboard/areas/devices/integrations changes, no YAML/file parsing, and no payload-wide expansion.
- Bump version from `0.0.11` to `0.0.12`.

## 0.0.11 - 2026-04-19

### Changed
- Add the first minimal `important_attributes` starter slice to compact `entities.items`, derived only from readable `/states.attributes` data.
- Whitelist only string values for `device_class`, `state_class`, and `unit_of_measurement`; omit `important_attributes` entirely when none of those keys are present as strings.
- Keep existing compact entity fields unchanged: `entity_id`, derived `domain`, direct `state`, and direct plain-string `friendly_name`.
- Keep the export read-only and GET-only with no `raw_attributes`, no relationship modeling, no dashboard/areas/devices/integrations changes, no YAML/file parsing, and no payload-wide expansion.
- Bump version from `0.0.10` to `0.0.11`.

## 0.0.10 - 2026-04-18

### Changed
- Add the first compact Entity Context slice under `entities.items`, built only from readable `/states` data.
- Keep existing `entities` summary fields intact while adding capped per-entity items with `entity_id`, derived `domain`, direct `state`, and direct plain-string `friendly_name`.
- Sort compact entity items by `entity_id`, cap output at 50 entries, skip malformed entries safely, and omit `items` when `/states` is unauthorized or unreadable.
- Keep the export read-only and GET-only with no relationship logic, no raw/full attributes, no dashboard/areas/devices/integrations changes, no YAML/file parsing, and no analyzer logic.
- Bump version from `0.0.9` to `0.0.10`.

## 0.0.9 - 2026-04-18

### Changed
- Improve dashboard discovery robustness by accepting small explicit wrapper shapes from readable `/lovelace/dashboards` and `/lovelace/config` payloads.
- Preserve compact `dashboard` export semantics with counts only: `dashboards`, `views`, and `cards`.
- Keep request logging token-safe by logging the normalized local path instead of the raw ingress-prefixed request path.
- Keep discovery strictly read-only with the existing local GET-only Core Proxy architecture and no new dashboard endpoint families, transport paths, relationship logic, or entity extraction.
- Bump version from `0.0.8` to `0.0.9`.

## 0.0.8 - 2026-04-18 (docs)

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

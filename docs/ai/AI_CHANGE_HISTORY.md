# AI Change History

## Version 0.0.18
- Goal: small follow-up for the ingress restart/reconnect masking-status UX after the 0.0.17 polling step.
- Pre-check finding: the repo already had the current masking mode, read-only `/api/info` polling, and a visible reconnecting message while the backend is unavailable.
- Key changes: add a tiny frontend lifecycle state for stable, reconnecting, and reconnected; after a reconnect, the page now briefly says the add-on is reachable again and that the shown masking mode is active.
- Result: the restart/reconnect transition no longer silently returns from the reconnecting message to normal steady-state text; the recovered state is visibly distinct and styled in the existing ingress page.
- Scope guard: no backend status payload change, no writable settings UI, no config mutation endpoint, no Supervisor restart control logic, no export payload behavior change, no WebSocket, no POST/PUT/PATCH/DELETE, and no service calls.

## Version 0.0.17
- Goal: small UX polish follow-up for the 0.0.16 compact masking status flow after add-on option changes and restarts.
- Key changes: rewrite the export-page masking status into clearer user-facing language, keep the raw option name secondary, and add lightweight read-only polling of `/api/info` so the page can recover from temporary backend unavailability during restart.
- Result: the export page now says whether privacy masking is on or off, explains that the setting is changed in the Home Assistant add-on configuration, shows a restart/reconnecting message when the backend is temporarily unavailable, and refreshes status automatically once reachable again.
- Scope guard: no export payload behavior changes, no writable settings UI, no config mutation endpoint, no Supervisor control logic, no full privacy redesign, no new export sections, no raw attributes, no relationship modeling, no WebSocket, no POST/template fallback, and no service calls.

## Version 0.0.16
- Goal: small corrective follow-up for the 0.0.15 configurable compact masking step.
- Real export confirmation: the latest 0.0.15 export was generated with `allow_sensitive_values=true`, which intentionally allowed raw compact values; using it as evidence showed hyphenated IPv4-like fragments in compact `friendly_name` values and a numeric measurement `state` shape that the current masker would falsely treat as MAC-like.
- Key changes: add read-only export-page clarity for the current compact masking mode and the Home Assistant add-on configuration option source, mask hyphenated IPv4-like fragments, and skip plain MAC-like masking for numeric measurement `state` values with measurement hints.
- Result: UI behavior is clearer without adding writable settings controls, hyphenated IPv4-like compact leaks are covered when masking is enabled, and legitimate numeric measurement states are preserved.
- Scope guard: no writable settings UI, no config mutation endpoint, no full privacy redesign, no new export sections, no raw attributes, no relationship modeling, no sorting changes, no `important_attributes` whitelist changes, no WebSocket, no POST/template fallback, and no service calls.

## Version 0.0.15
- Goal: add a small configurable follow-up for compact entity sensitive-value masking, based on the latest real 0.0.14 export.
- Real export confirmation: 0.0.14 already masked literal dotted IPv4 values in compact `state` and one plain-string `friendly_name`, while additional sensitive-looking compact values remained in `entity_id`, `state`, and `friendly_name`.
- Key changes: extend best-effort compact masking to underscored IPv4 fragments in `entity_id`, MAC-like identifiers, SSID/Wi-Fi context states, geocoded/address context states, and person-derived tokens from `person` entities.
- Configuration: add `allow_sensitive_values`, defaulting to `false`; only explicit boolean `true` allows compact sensitive values to remain unmasked, and missing or invalid option values keep masking enabled.
- User notice: add concise best-effort masking warnings to export warnings, Markdown rendering, the existing export UI surface, and README text.
- Result: compact entity output is privacy-safer by default while retaining the original item structure, original logical `entity_id` sort order, existing export keys, category names, and the `important_attributes` whitelist.
- Scope guard: no full-export privacy redesign, no architecture change, no new export sections, no raw attributes, no relationship modeling, no WebSocket, no POST/template fallback, no service calls, no settings UI rebuild, and no export category redesign.

## Version 0.0.14
- Goal: refresh outdated `important_attributes` validation notes against the real 0.0.13 compact export and perform a first targeted sensitive-values check for compact entity strings.
- Real export confirmation: compact `entities.items` now includes real `unit_of_measurement` and `state_class` examples; `entity_category` was not present in the attached export, and non-string whitelisted raw values remain unconfirmed because raw attributes are intentionally not exported.
- Key changes: mask literal IPv4 address values in already exported compact `state` and plain-string `friendly_name` values as `[redacted_ipv4]`.
- Result: the compact entity export no longer exposes the observed local network address literals in those fields, while item structure, export keys, `entity_id`, stable sorting, and the `important_attributes` whitelist remain unchanged.
- Scope guard: no architecture change, no transport changes, no WebSocket, no POST/template fallback, no service calls, no raw attributes, no relationship modeling, no broad anonymization redesign, no new export fields, and no export category redesign.

## Version 0.0.13
- Goal: remove the artificial 50-item limit from the existing compact `entities.items` export.
- Key changes: return all eligible compact entity items derived from readable `/states` data after the existing stable `entity_id` sort.
- Result: compact entity items are no longer truncated to the first 50 entries; the item shape and `important_attributes` whitelist behavior remain unchanged.
- Scope guard: no transport changes, no WebSocket, no POST/template fallback, no service calls, no raw attributes, no relationship modeling, no dashboard/areas/devices/integrations work, no YAML/file parsing, and no export schema redesign.

## Version 0.0.12
- Goal: add the second small, controlled important-attributes refinement inside the existing compact Entity Context slice.
- Key changes: extend the tiny string-only `important_attributes` whitelist with `entity_category`.
- Result: compact entity items can now expose Home Assistant entity category context when `/states.attributes.entity_category` is present as a string, while missing, non-string, or otherwise unwhitelisted values remain omitted.
- Scope guard: no transport changes, no WebSocket, no POST/template fallback, no service calls, no raw attributes, no relationship modeling, no dashboard/areas/devices/integrations work, no YAML/file parsing, and no payload-wide expansion.

## Version 0.0.11
- Goal: add the first small, controlled important-attributes starter step inside the existing compact Entity Context slice.
- Key changes: add optional `important_attributes` to `entities.items` from readable `/states.attributes`, limited to string values for `device_class`, `state_class`, and `unit_of_measurement`.
- Result: compact entity items expose a minimal amount of useful attribute context without duplicating `friendly_name`, emitting empty objects, or expanding into raw attributes.
- Scope guard: no transport changes, no WebSocket, no POST/template fallback, no service calls, no relationship modeling, no dashboard/areas/devices/integrations work, no YAML/file parsing, and no payload-wide expansion.

## 2026-04-18 - Repository line-ending normalization
- Goal: reduce false CRLF / line-ending noise on Windows without changing exporter behavior or project architecture.
- Key changes: expand `.gitattributes` for the tracked text file types currently used by the repository: Markdown, YAML, HTML, CSS, `.gitattributes`, `.gitignore`, and `LICENSE`, while preserving the existing Python, shell, and Dockerfile LF rules.
- Result: Git now reports explicit `text eol=lf` attributes for the current tracked text file mix, improving cross-platform stability for normal editing workflows.
- Scope guard: no exporter code, API behavior, payload semantics, Home Assistant access logic, or version files changed.
- Note: no `.editorconfig` was added because `.gitattributes` is sufficient for tracked-file normalization, and no repository-wide content renormalization was performed because tracked files were already indexed as LF.

## Version 0.0.10
- Goal: introduce the first minimal Entity Context slice without changing the read-only architecture or category semantics.
- Key changes: add compact `entities.items` from the existing readable `/states` snapshot, sorted by `entity_id` and capped at 50 entries.
- Item fields: `entity_id`, derived `domain`, direct `state`, and direct plain-string `attributes.friendly_name` as `friendly_name`; missing or non-string friendly names become `null`.
- Result: `entities` now remains a compact summary while exposing a small useful entity list for AI/system understanding; unauthorized or unreadable `/states` still omits `items` and preserves existing status/reason semantics.
- Limitation: the 50-item cap is an intentional first-slice constraint and must be reevaluated when Entity Context moves beyond this compact slice or mode-specific entity depth is introduced.
- Scope guard: no relationship logic, no raw/full attributes, no dashboard/areas/devices/integrations changes, no YAML/file parsing, and no analyzer logic.

## 2026-04-18 - Dashboard GET path investigation
- Goal: check whether one small additional dashboard GET path can improve dashboard reachability/readability after the `0.0.9` wrapper-tolerance step.
- Finding: no additional dashboard-specific REST GET path could be validated inside the existing local Core Proxy architecture; richer Home Assistant panel/dashboard access is exposed through WebSocket commands or frontend HTML, which are outside this task.
- Result: no speculative dashboard probe, no code fallback, no transport change, and no version bump; `0.0.9` remains the current application version.
- Cleanup: removed obsolete `docs/startvorlage für neuen chat-md` because the active official guidance is now in `docs/ai/AI_STANDARD_STARTPROMPT.md` and `docs/ai/AI_NEW_CHAT_AND_CODEX_GUIDE.md`.
- Next focus: continue Discovery Quality only with validated GET-compatible improvements, or explicitly plan a separate transport-alignment task before any WebSocket-based dashboard work.

## Version 0.0.9
- Goal: improve dashboard discovery robustness without architecture changes.
- Key changes: count readable `/lovelace/dashboards` payloads when they are direct lists or small explicit wrappers, read `/lovelace/config` when the real config object is directly returned or wrapped under `config`, `data`, or `result` with a clear `views` list, and keep request logging token-safe by logging normalized local paths.
- Result: `dashboard` keeps compact and honest available/partial/unavailable semantics while tolerating harmless response-shape differences on the already used GET endpoints.
- Next focus: continue Discovery Quality with additional small, validated robustness improvements only where they fit the current read-only architecture.
## 2026-04-18 - Areas / Devices fallback investigation
- Goal: check whether a tiny, safe Areas / Devices fallback can be added after `0.0.8` without changing the GET-only architecture.
- Finding: no alternate GET-compatible Areas / Devices path is currently validated inside the existing backend model.
- Result: no speculative fallback code, no transport change, no relationship inference, and no version bump; `0.0.8` remains the current application version.
- Next focus: continue Discovery Quality with dashboard robustness, unless a real HA test later validates a concrete GET-compatible Areas / Devices path.

## Version 0.0.8
- Goal: improve Areas / Devices discovery robustness without architecture changes.
- Key changes: count readable `/areas` and `/devices` payloads when they are direct lists or small explicit wrappers (`areas`, `devices`, `data`, `items`, `result`).
- Result: `areas_devices` keeps compact and honest available/partial/unavailable semantics while tolerating harmless response-shape differences.
- Next focus: continue Discovery Quality phase with dashboard robustness before deeper Entity Context or Relationship work.

## Version 0.0.7
- Goal: integrations discovery quality cleanup without architecture changes.
- Key changes: normalize dotted component names to main integration (`mqtt.sensor` -> `mqtt`), add simple `kind` classification (`user_integration` / `core_component`), keep core components visible, and prioritize user integrations in `top_items`.
- Result: smaller, clearer, and more AI-usable integration view with transparent read-only semantics.
- Next focus: continue Discovery Quality phase (areas/devices/dashboard robustness).

## Version 0.0.6
- Goal: replace integrations placeholder with first useful read-only integrations discovery.
- Key changes: direct integrations from `config.components`, cautious derived fallbacks from services/states, compact `items`/`top_items`, and semantic status (`available`/`partial`/`unavailable`).
- Result: `integrations` category can now return real discovered items when readable.
- Next focus: improve coverage quality while keeping compact semantics.

## Version 0.0.5
- Goal: improve discovery semantics and robustness.
- Key changes: explicit proxy API base, longer timeout, partial semantics for key categories.
- Result: more consistent export status evaluation and diagnostics.
- Next focus: ongoing discovery coverage and quality improvements.

## Version 0.0.4
- Goal: switch to official Core Proxy auth path.
- Key changes: `homeassistant_api: true`, core-proxy token-safe headers, `/api/ha-auth-debug`.
- Result: stable read-only proxy diagnostics and export flow.
- Next focus: semantics and discovery coverage improvements.

## Version 0.0.3
- Goal: fix add-on store schema/options parsing issue.
- Key changes: optional token schema retained, default removed (`options: {}`).
- Result: add-on config parse/build compatibility restored.
- Next focus: core-proxy-based authenticated read path.

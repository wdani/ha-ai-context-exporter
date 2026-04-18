# AI Change History

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

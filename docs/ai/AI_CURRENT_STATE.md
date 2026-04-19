# AI Current State

## Current version
`0.0.18`

## Export status currently observed
- `system = partial`
- `entities = available`
- `logic = available`
- `areas_devices = available/partial/unavailable` (depending on Areas/Devices endpoint readability)
- `integrations = available/partial` (abhängig von Lesbarkeit über Core Proxy)

## Known limitations
- Integrations discovery basiert primär auf `config.components` und nutzt `services`/`states` nur vorsichtig als Fallback.
- Komponenten mit Punktnotation (z. B. `mqtt.sensor`) werden auf Hauptintegrationen reduziert (z. B. `mqtt`).
- Core-/interne Komponenten bleiben sichtbar, werden aber als `kind = core_component` markiert.
- `top_items` priorisiert `user_integration` vor `core_component` und bleibt auf max. 10 Einträge begrenzt.
- Areas/devices discovery kann je nach Proxy-Lesbarkeit unvollständig sein.
- Areas/devices discovery now also tolerates direct list wrappers such as `areas`, `devices`, `data`, `items`, and `result`; no inferred relationships are exported.
- No additional GET-compatible Areas/Devices fallback path has been validated inside the current backend model; registry-style list access remains outside this task because it would require WebSocket/RPC-style access or POST-based template handling.
- Dashboard metadata kann je nach Endpoint-Lesbarkeit begrenzt sein.
- Dashboard discovery now tolerates small explicit wrappers for the existing `/lovelace/dashboards` and `/lovelace/config` GET payloads; output remains compact counts only with no entity extraction or relationship logic.
- A follow-up dashboard GET path investigation found no additional validated Core Proxy REST GET path beyond the existing Lovelace probes. If those existing endpoints are unreachable in a real HA environment, the dashboard category remains honestly unavailable instead of using speculative WebSocket, frontend HTML, POST/template, or file-parsing fallbacks.
- Current observed export examples may show `environment.config_path = false`; this does not block the current `/states`-only Entity Context slice, but it must be rechecked before starting any File / YAML Context work.
- The `entities` category includes the first compact Entity Context slice as `items` when `/states` is readable.
- `entities.items` contains the full eligible compact entity list derived from readable `/states` data, sorted by `entity_id`, and keeps the stable compact fields `entity_id`, derived `domain`, direct `state`, and direct plain-string `attributes.friendly_name` (or `null`).
- Compact `state` and plain-string `friendly_name` redact literal IPv4 address values as `[redacted_ipv4]` after a targeted real-export sensitive-values check found local network address literals in those already exported compact fields.
- Compact entity masking is now best-effort and enabled by default unless the add-on option `allow_sensitive_values` is explicitly set to boolean `true`; missing or invalid option values keep masking enabled.
- Current compact masking also covers the latest evidenced follow-up categories: underscored and hyphenated IPv4-like fragments, MAC-like identifiers, SSID/Wi-Fi context states, geocoded/address context states, and person-derived tokens from `person` entities. Sorting still uses the original logical `entity_id` before output masking.
- Plain MAC-like masking is narrowed for numeric measurement `state` values with measurement hints, so legitimate numeric sensor states are not accidentally corrupted.
- The export `warnings` list and existing export UI surface include a concise best-effort masking notice. The export UI shows whether privacy masking is currently on or off for compact entity values, points users to the Home Assistant add-on configuration option `allow_sensitive_values`, polls `/api/info` for refreshed status, shows a restart/reconnecting message while the backend is temporarily unavailable, and briefly shows a distinct reachable-again message when the active masking mode has been refreshed after reconnect. Users must still manually review exports before sharing them; this is not complete anonymization.
- `entities.items` can now include the second small `important_attributes` refinement, derived only from readable `/states.attributes` string values for `device_class`, `entity_category`, `state_class`, and `unit_of_measurement`.
- `important_attributes` is omitted when none of the small whitelisted keys are present as strings; empty `important_attributes` objects are not emitted.
- Current real 0.0.13 export observation confirms the basic `important_attributes` starter presence/omission pattern and real compact-item examples for `device_class`, `state_class`, and `unit_of_measurement`. The same export did not show `entity_category`; focused local helper validation covers that one-key refinement. Non-string whitelisted raw values being omitted remain pending because the compact export intentionally does not include raw attributes.
- Entity Context does not yet include `raw_attributes`, broad/domain-specific important attributes, area/device/integration relationships, aliases, semantic inference, dashboard links, or YAML/file context.

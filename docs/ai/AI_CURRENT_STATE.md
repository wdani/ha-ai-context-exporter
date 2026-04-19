# AI Current State

## Current version
`0.0.12`

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
- `entities.items` is intentionally capped at 50 entries, sorted by `entity_id`, and keeps the stable compact fields `entity_id`, derived `domain`, direct `state`, and direct plain-string `attributes.friendly_name` (or `null`).
- `entities.items` can now include the second small `important_attributes` refinement, derived only from readable `/states.attributes` string values for `device_class`, `entity_category`, `state_class`, and `unit_of_measurement`.
- `important_attributes` is omitted when none of the small whitelisted keys are present as strings; empty `important_attributes` objects are not emitted.
- Current real export observation confirms the basic `important_attributes` starter presence/omission pattern and visible `device_class` examples. Focused local helper validation now covers the one-key `entity_category` refinement. This is not a blocker for the current slice, but real-world examples for `unit_of_measurement`, `state_class`, and non-string whitelisted values being omitted remain pending for later validation on a suitable user system or through community-provided example exports/test cases.
- The 50-item cap is a temporary first-slice limitation and must be reevaluated when the project moves beyond compact Entity Context or introduces stronger mode-specific entity depth.
- Entity Context does not yet include `raw_attributes`, broad/domain-specific important attributes, area/device/integration relationships, aliases, semantic inference, dashboard links, or YAML/file context.

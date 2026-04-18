# AI Current State

## Current version
`0.0.9`

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
- Dashboard metadata kann je nach Endpoint-Lesbarkeit begrenzt sein.
- Dashboard discovery now tolerates small explicit wrappers for the existing `/lovelace/dashboards` and `/lovelace/config` GET payloads; output remains compact counts only with no entity extraction or relationship logic.

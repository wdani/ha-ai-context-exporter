# AI Current State

## Current version
`0.0.7`

## Export status currently observed
- `system = partial`
- `entities = available`
- `logic = available`
- `integrations = available/partial` (abhängig von Lesbarkeit über Core Proxy)

## Known limitations
- Integrations discovery basiert primär auf `config.components` und nutzt `services`/`states` nur vorsichtig als Fallback.
- Komponenten mit Punktnotation (z. B. `mqtt.sensor`) werden auf Hauptintegrationen reduziert (z. B. `mqtt`).
- Core-/interne Komponenten bleiben sichtbar, werden aber als `kind = core_component` markiert.
- `top_items` priorisiert `user_integration` vor `core_component` und bleibt auf max. 10 Einträge begrenzt.
- Areas/devices discovery kann je nach Proxy-Lesbarkeit unvollständig sein.
- Dashboard metadata kann je nach Endpoint-Lesbarkeit begrenzt sein.

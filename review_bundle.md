# Review Bundle

## Projekt
HA AI Context Exporter

## Umsetzung
- Neuer read-only Endpoint `GET /api/ai-export-preview` hinzugefügt.
- Endpoint nutzt ausschließlich bestehende Preview-Funktionen:
  - `get_ha_structure_preview()`
  - `get_ha_logic_preview()`
  - `get_ha_dashboard_preview()`
  - `get_ha_domain_preview()`
- Keine neuen Datenquellen, keine Datei-Schreibvorgänge, reine JSON-Response.

## Exportformat
Der Endpoint liefert:
- `tool`
- `environment`
- `system_summary`
- `logic_summary`
- `dashboard_summary`
- `top_domains`

## Frontend
- Neue Section **AI Export Preview**.
- Neuer Button **Generate AI export preview**.
- Beim Klick wird `/api/ai-export-preview` geladen und formatiert als JSON angezeigt.

## Hinweise
- Implementierung bleibt read-only.
- Bestehende Endpoints und UI-Bereiche bleiben unverändert nutzbar.

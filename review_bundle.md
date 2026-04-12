# Review Bundle

## Zusammenfassung

- Integrations-Discovery qualitativ verbessert, ohne Architekturänderungen.
- Punktnotation aus `config.components` wird auf Hauptintegration reduziert (z. B. `mqtt.sensor` -> `mqtt`).
- Neue einfache Klassifikation pro Eintrag: `kind = user_integration` oder `kind = core_component`.
- Core-/interne Komponenten bleiben in `items` sichtbar, werden aber klar markiert.
- `top_items` priorisiert `user_integration` vor `core_component` und sortiert stabil alphabetisch (max. 10).
- Version auf `0.0.7` erhöht.

## Geänderte Dateien

- `ha_ai_context_exporter/rootfs/app/export/export_integrations.py`
- `ha_ai_context_exporter/rootfs/app/version.py`
- `ha_ai_context_exporter/config.yaml`
- `docs/ai/AI_CURRENT_STATE.md`
- `docs/ai/AI_CHANGE_HISTORY.md`
- `CHANGELOG.md`
- `review_bundle.md`
- `docs/review_bundles/2026-04-12_0.0.7_integrations-cleanup.md`

## Validierung (Kurz)

- Syntaxcheck der geänderten Python-Dateien erfolgreich.
- Backend startet weiterhin lokal.
- `/api/export` liefert weiterhin gültiges JSON.
- Integrationsausgabe enthält reduzierte Hauptintegrationen statt Plattformrauschen.
- Core-Komponenten bleiben enthalten und sind als `core_component` klassifiziert.
- `top_items` priorisiert `user_integration` und bleibt kompakt.
- `warnings` bleibt Liste von Strings.
- Keine Schreiboperationen (POST/PUT/DELETE/PATCH) eingeführt.
- Keine Token-Leaks beobachtet.

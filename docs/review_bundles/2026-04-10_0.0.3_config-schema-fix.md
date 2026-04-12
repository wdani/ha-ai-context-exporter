# Review Bundle

## Kurze Zusammenfassung

- Build-Fix für Home Assistant Add-on Store umgesetzt: `options` in `config.yaml` auf `{}` gesetzt, während `schema.ha_token` als optionales Passwortfeld (`password?`) erhalten bleibt.
- Entwicklungsversion von `0.0.2` auf `0.0.3` erhöht (zentral in `rootfs/app/version.py` und konsistent in `config.yaml`).
- `CHANGELOG.md` für Version `0.0.3` ergänzt.

## Vollständige Inhalte aller geänderten Dateien

### `ha_ai_context_exporter/config.yaml`
```yaml
name: "HA AI Context Exporter"
version: "0.0.3"
slug: "ha_ai_context_exporter"
description: "Minimal scaffold for future Home Assistant AI context export features"
arch:
  - amd64
  - aarch64
  - armv7
startup: services
boot: manual
ingress: true
ingress_port: 8099
panel_icon: mdi:robot-outline
init: false
options: {}
schema:
  ha_token: "password?"

```

### `ha_ai_context_exporter/rootfs/app/version.py`
```python
"""Single source of truth for application version."""

VERSION = "0.0.3"

```

### `CHANGELOG.md`
```md
# Changelog

All notable changes to this project will be documented in this file.

## 0.0.3 - 2026-04-10

### Fixed
- Fix Home Assistant add-on schema/options compatibility by removing the default value for optional `ha_token` (`options: {}` with `schema: ha_token: "password?"`).
- Bump development version from `0.0.2` to `0.0.3`.


```

## Annahmen / Einschränkungen

- Dieser Schritt enthält bewusst nur den angeforderten Build-Fix plus Versions-/Changelog-Update; keine Änderungen an Backend-Logik, Discovery oder Export-System.
- Die optionale `ha_token`-Konfiguration bleibt erhalten und wird weiterhin über `schema: ha_token: "password?"` definiert.
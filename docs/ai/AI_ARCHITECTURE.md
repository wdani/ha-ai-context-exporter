# AI Architecture

## Backend
- Runtime: Python HTTP server (`http.server`).
- Entry point: `ha_ai_context_exporter/rootfs/app/main.py`.

## Export architecture
- Controller: `rootfs/app/export/export_controller.py`
- Category modules:
  - `export_system.py`
  - `export_entities.py`
  - `export_logic.py`
  - `export_dashboard.py`
  - `export_integrations.py`
- Renderers: `export_renderers.py` (JSON / Markdown download output).

## Discovery flow
1. Discovery probes
2. Preview structures
3. Export controller assembly
4. Renderer formatting
5. Download response

## Core Proxy base
- `http://supervisor/core/api`

## High-level request flow
Discovery → Preview → Export Controller → Renderer → Download

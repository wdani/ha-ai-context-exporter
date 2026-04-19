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

## Ingress UI container role

The current UI container is Home Assistant Ingress. The add-on metadata keeps `ingress: true`, the lightweight backend serves the static UI and API from the same Python HTTP server, and request handling is still routed through `do_GET` only.

Ingress was the right small starting point for this project because it:
- keeps the exporter inside the Home Assistant add-on surface
- avoids a second frontend distribution or authentication path
- fits the current read-only export workflow
- keeps setup low while the data model and export semantics are still evolving
- lets the UI act as a compact local control surface for previews, export download, and status visibility

Recent ingress-related work also shows two different kinds of friction that should not be mixed together.

Short-term frontend/UX implementation friction:
- ingress-relative asset and API URL handling needs careful path construction
- privacy-mode copy, source-of-truth hierarchy, reconnect messaging, and recovered-state visibility can be improved within the existing frontend
- polling `/api/info` is enough for the current read-only status display, even though the UI must handle temporary backend unavailability clearly

Structural ingress/container/lifecycle limitations:
- Home Assistant add-on option changes can restart the add-on outside the page's control
- the ingress page becomes temporarily unreachable when the backend container is restarting
- the page cannot own or fully explain Supervisor-level restart conflicts or lifecycle jobs
- browser/runtime memory is only page-local and should not be treated as durable state
- the UI remains constrained by the Home Assistant ingress shell, route prefixing, and the add-on container lifecycle

Current strategic stance:
Ingress should be treated as a consciously small tactical UI shell for the current development stage, not as an already-proven long-term product UX home. This is not a migration decision. There is no current plan to replace Ingress, add a second UI container, introduce a custom panel, or redesign the backend around a future migration. The right near-term move is to keep Ingress, keep the backend read-only and GET-only, and document its boundaries honestly while the exporter model matures.

Reevaluate the UI container later only through a separate architecture task if concrete signals appear, such as:
- repeated ingress-specific lifecycle/status work continues to consume disproportionate development effort
- user workflows require durable settings/state or richer interaction than a small read-only page can honestly provide
- the project needs accurate Supervisor lifecycle orchestration rather than passive status explanation
- future relationship, dashboard, analyzer, or file/YAML context workflows require a substantially richer navigation model
- a Home Assistant-native frontend integration becomes necessary for product fit rather than merely nicer presentation
- ingress route/prefix/container constraints become a blocker for safe, understandable user behavior

Some of these triggers are informed engineering judgment based on the current code and review history, not proof that Ingress is failing today.

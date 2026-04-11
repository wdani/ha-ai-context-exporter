# AI Project Context

## Project type
Home Assistant add-on (`ha_ai_context_exporter`) with a lightweight Python backend and ingress UI.

## Core goal
Provide a read-only AI-friendly context export of a Home Assistant instance.

## Security model
- Strictly read-only add-on.
- No state-changing operations against Home Assistant.
- No external host communication for discovery/export.
- Token material must never appear in logs, API responses, export payloads, UI output, warnings, or reasons.

## Read-only rules
Allowed:
- Local `GET` requests against Home Assistant Core API through the official Core Proxy.

Not allowed:
- `POST`, `PUT`, `DELETE`, `PATCH`
- Service calls / automation triggers
- File mutation of Home Assistant runtime data

## Core Proxy access
Primary API base:
- `http://supervisor/core/api`

Auth:
- `Authorization: Bearer ${SUPERVISOR_TOKEN}`
- Header only for allowed Core Proxy targets.

## Export categories
- `system`
- `entities`
- `areas_devices`
- `logic`
- `dashboard`
- `integrations`

## Export semantics
Category payloads use consistent fields:
- `status`
- `reason`
- `reachability`
- `readability`

Global export fields include:
- `warnings` (always list of strings)
- `data_completeness`
- `discovery_status`

## Important API endpoints
- `/health`
- `/api/info`
- `/api/ha-auth-debug`
- `/api/export`
- `/api/export/download`

## Versioning system
- `rootfs/app/version.py` is the single source of truth.
- `0.0.x` = development phase.
- `0.1.0` = first usable milestone.

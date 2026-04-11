# Review Bundle

## Zusammenfassung

- Dauerhafte AI-Projektstruktur unter `docs/ai/` und `docs/development/` angelegt.
- AI-Contributor-Regeln unter `.github/CONTRIBUTING.md` ergänzt.
- CHANGELOG um einen kurzen Dokumentations-Eintrag unter Version `0.0.5` erweitert.
- Keine Änderungen an Discovery, Auth, Export-Logik oder UI vorgenommen (reiner Struktur-/Dokumentationsschritt).

## Vollständige Inhalte aller geänderten Dateien

### `CHANGELOG.md`
```md
# Changelog

All notable changes to this project will be documented in this file.

## 0.0.5 - 2026-04-11

### Changed
### Docs
- Add persistent AI project documentation set under `docs/ai/`.
- Add AI development workflow doc under `docs/development/AI_WORKFLOW.md`.
- Add contribution guideline under `.github/CONTRIBUTING.md`.
- Archive technical review bundle at `docs/review_bundles/2026-04-11_0.0.5_ai-project-docs.md`.

- Improve discovery semantics and coverage for export categories (`system`, `areas_devices`, `dashboard`) with consistent partial/available/unavailable status handling.
- Make core proxy base explicit (`http://supervisor/core/api`) and avoid path-duplication risks.
- Increase central request timeout to 5 seconds for more robust local proxy reads.

## 0.0.4 - 2026-04-11

### Changed
- Switch primary Home Assistant read access to the official Core Proxy (`homeassistant_api: true`) using `http://supervisor/core/api/...` with `SUPERVISOR_TOKEN` for read-only GET requests.
- Add `/api/ha-auth-debug` endpoint for token-safe proxy/readability diagnostics.
- Bump development version from `0.0.3` to `0.0.4`.

## 0.0.3 - 2026-04-10

### Fixed
- Fix Home Assistant add-on schema/options compatibility by removing the default value for optional `ha_token` (`options: {}` with `schema: ha_token: "password?"`).
- Bump development version from `0.0.2` to `0.0.3`.


```

### `.github/CONTRIBUTING.md`
```md
# Contributing

## Project rules
- Keep changes incremental.
- Avoid large refactorings without explicit alignment.
- Preserve architecture and endpoint stability where possible.

## Read-only architecture
- This add-on is strictly read-only.
- Allowed: local GET requests to Home Assistant Core API through official Core Proxy.
- Not allowed: POST/PUT/DELETE/PATCH, service calls, automations triggers, state changes.

## Code style guidance
- Keep implementation simple and explicit.
- Reuse existing helpers and controller flow.
- Maintain consistent export semantics fields (`status`, `reason`, `reachability`, `readability`).

## Review process
- Update `review_bundle.md` for each task.
- Archive review bundles under `docs/review_bundles/`.
- Keep `CHANGELOG.md` human-readable and concise.

## AI docs
Before AI-driven changes, read:
- `docs/ai/AI_PROJECT_CONTEXT.md`
- `docs/ai/AI_ARCHITECTURE.md`
- `docs/ai/AI_CURRENT_STATE.md`

Use prompt scaffold:
- `docs/ai/AI_PROMPT_TEMPLATE.md`

```

### `docs/ai/AI_PROJECT_CONTEXT.md`
```md
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

```

### `docs/ai/AI_ARCHITECTURE.md`
```md
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

```

### `docs/ai/AI_CURRENT_STATE.md`
```md
# AI Current State

## Current version
`0.0.5`

## Export status currently observed
- `system = partial`
- `entities = available`
- `logic = available`

## Known limitations
- Integrations discovery remains placeholder-based.
- Areas/devices discovery can be incomplete depending on proxy readability and environment.
- Dashboard metadata can be limited depending on endpoint readability.

```

### `docs/ai/AI_PROMPT_TEMPLATE.md`
```md
# AI Prompt Template

Project: HA AI Context Exporter

Context:
`docs/ai/AI_PROJECT_CONTEXT.md`

Architecture:
`docs/ai/AI_ARCHITECTURE.md`

Current state:
`docs/ai/AI_CURRENT_STATE.md`

Task:
[describe the change]

Rules:
- no large refactorings
- read-only addon
- GET requests only
- maintain export semantics

```

### `docs/ai/AI_CHANGE_HISTORY.md`
```md
# AI Change History

## Version 0.0.3
- Goal: fix add-on store schema/options parsing issue.
- Key changes: optional token schema retained, default removed (`options: {}`).
- Result: add-on config parse/build compatibility restored.
- Next focus: core-proxy-based authenticated read path.

## Version 0.0.4
- Goal: switch to official Core Proxy auth path.
- Key changes: `homeassistant_api: true`, core-proxy token-safe headers, `/api/ha-auth-debug`.
- Result: stable read-only proxy diagnostics and export flow.
- Next focus: semantics and discovery coverage improvements.

## Version 0.0.5
- Goal: improve discovery semantics and robustness.
- Key changes: explicit proxy API base, longer timeout, partial semantics for key categories.
- Result: more consistent export status evaluation and diagnostics.
- Next focus: ongoing discovery coverage and quality improvements.

```

### `docs/ai/AI_CONTRIBUTOR_GUIDE.md`
```md
# AI Contributor Guide

## Purpose
Guide AI-assisted contributions with stable context, architecture rules, and workflow constraints.

## Read first (mandatory)
1. `docs/ai/AI_PROJECT_CONTEXT.md`
2. `docs/ai/AI_ARCHITECTURE.md`
3. `docs/ai/AI_CURRENT_STATE.md`

## Prompting
Use:
- `docs/ai/AI_PROMPT_TEMPLATE.md`

## Contribution rules
- No large refactorings.
- Respect existing architecture boundaries.
- Preserve read-only behavior.
- Keep Home Assistant interactions GET-only.
- Maintain export semantics consistency.

## Review artifacts
- Current technical review: `review_bundle.md`
- Archived review history: `docs/review_bundles/`
- Human-readable project history: `CHANGELOG.md`
- AI-oriented history: `docs/ai/AI_CHANGE_HISTORY.md`

```

### `docs/development/AI_WORKFLOW.md`
```md
# AI Workflow

## Principle
- Chat = current task execution context.
- Repository = durable project memory.

## Start-of-chat context loading
Each new chat should begin by reading:
1. `docs/ai/AI_PROJECT_CONTEXT.md`
2. `docs/ai/AI_ARCHITECTURE.md`
3. `docs/ai/AI_CURRENT_STATE.md`

## Review/documentation flow
- `review_bundle.md` = current technical review file.
- `docs/review_bundles/` = archived review bundles.
- `CHANGELOG.md` = human project history.
- `docs/ai/AI_CHANGE_HISTORY.md` = AI-oriented history.

```

## Annahmen / Einschränkungen

- Dieser Schritt ist absichtlich rein dokumentationsorientiert und enthält keine funktionalen Codeänderungen.
- Version bleibt gemäß Vorgabe auf `0.0.5`.

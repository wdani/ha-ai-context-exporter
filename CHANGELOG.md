# Changelog

All notable changes to this project will be documented in this file.

## 0.0.6 - 2026-04-12

### Docs
- Add `docs/ai/AI_DEVELOPMENT_TREE.md` as official development tree/roadmap document from the provided source file.
- Update `review_bundle.md` and archive it as `docs/review_bundles/2026-04-12_0.0.6_ai-development-tree.md`.

## 0.0.6 - 2026-04-11

### Changed
- Implement first real read-only integrations discovery using `config.components` as primary source and cautious fallbacks from `services`/`states`.
- Add compact integrations fields: `count`, `items`, `top_items` with consistent semantic status.
- Bump development version from `0.0.5` to `0.0.6`.

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


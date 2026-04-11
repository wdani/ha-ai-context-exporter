# Changelog

All notable changes to this project will be documented in this file.

## 0.0.4 - 2026-04-11

### Changed
- Switch primary Home Assistant read access to the official Core Proxy (`homeassistant_api: true`) using `http://supervisor/core/api/...` with `SUPERVISOR_TOKEN` for read-only GET requests.
- Add `/api/ha-auth-debug` endpoint for token-safe proxy/readability diagnostics.
- Bump development version from `0.0.3` to `0.0.4`.

## 0.0.3 - 2026-04-10

### Fixed
- Fix Home Assistant add-on schema/options compatibility by removing the default value for optional `ha_token` (`options: {}` with `schema: ha_token: "password?"`).
- Bump development version from `0.0.2` to `0.0.3`.


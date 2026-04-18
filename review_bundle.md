# Review Bundle

## Summary

- Improved dashboard discovery robustness without architecture changes.
- Added explicit payload-shape tolerance for readable `/lovelace/dashboards` responses.
- Added a small Lovelace config unwrap helper for direct configs or wrappers under `config`, `data`, and `result` only when `views` is clearly a list.
- Kept request logging token-safe by logging normalized local paths instead of raw ingress-prefixed request paths.
- Preserved compact `dashboard` semantics: `available`, `partial`, `unavailable`, and token-safe reasons.
- Kept the add-on strictly read-only with local GET requests only.
- Bumped version to `0.0.9`.

## Changed files

- `docs/ai/AI_CURRENT_STATE.md`
- `docs/ai/AI_CHANGE_HISTORY.md`
- `CHANGELOG.md`
- `review_bundle.md`
- `docs/review_bundles/2026-04-18_0.0.9_dashboard-discovery-robustness.md`

## Validation

- Python syntax validation was run for touched Python files.
- Dashboard preview and `/api/export` payload assembly were validated with local provider stubs.
- Dashboard semantics were checked for direct dashboard lists, wrapped dashboard lists, direct Lovelace config payloads, wrapped Lovelace config payloads, only dashboards readable, only Lovelace config readable, unauthorized, reachable but unreadable, and neither reachable cases.
- `warnings` remains a list of strings.
- Inspection confirms discovery still uses local GET requests only and introduces no Home Assistant mutations.
- Request path normalization was checked for ingress-prefixed paths before logging.
- No token-like values are exposed in logs, warnings, reasons, export payload fields, or docs.
- Touched Markdown files were checked for escaped newline sequences and merge-conflict markers.

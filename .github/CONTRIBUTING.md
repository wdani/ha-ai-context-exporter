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

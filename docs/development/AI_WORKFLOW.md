# AI Workflow

## Principle
- Chat = current task execution context.
- Repository = durable project memory.

## Preferred project workflow
- One chat = one task = one branch = one review = one merge.
- After the merge, start a new chat for the next independent step.
- Codex should provide a short handoff package: COMMIT SUMMARY / PR / MERGE DESCRIPTION / NEXT CHAT START PROMPT.

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

# Review Bundle

## Summary

- Expanded `.gitattributes` from Python/shell/Dockerfile-only coverage to the tracked text file types currently present in the repository.
- Added explicit LF normalization for Markdown, YAML, HTML, CSS, `.gitattributes`, `.gitignore`, and `LICENSE`.
- Kept the task repository-hygiene only: no exporter semantics, API behavior, payload fields, Home Assistant access code, entity context logic, or version files changed.
- Did not add `.editorconfig`; the tracked-file stability problem is addressed directly through `.gitattributes` without broad editor formatting policy.
- Did not perform repository-wide content renormalization. `git ls-files --eol` showed tracked files already indexed as LF, and the rule update made Git recognize `text eol=lf` across the current tracked text mix.
- Applied LF-only normalization only to files already touched by this task, so the branch does not carry Git line-ending warnings for its own edited files.
- Expected Windows impact: with `core.autocrlf=true`, future checkout and save behavior for these tracked text files should be less prone to CRLF-only noise. Existing checked-out files may still show their previous worktree line endings until Git refreshes them through normal checkout/reset workflows.

## Changed files

- `.gitattributes`
- `CHANGELOG.md`
- `docs/ai/AI_CHANGE_HISTORY.md`
- `review_bundle.md`
- `docs/review_bundles/2026-04-18_repository-line-ending-normalization.md`

## Validation

- Baseline status before edits was clean on `feature/crlf-noise-cleanup`.
- Baseline `.gitattributes` only covered `*.sh`, `Dockerfile`, and `*.py`.
- Tracked file mix was inspected with `git ls-files`: 31 Markdown files, 10 Python files, 2 YAML files, and one each of shell, CSS, HTML, `.gitignore`, `.gitattributes`, `Dockerfile`, and `LICENSE`.
- `git ls-files --eol` before the change showed many Markdown/YAML/HTML/CSS/dotfile/license files without explicit attributes and checked out as CRLF under the current Windows `core.autocrlf=true` setting.
- `git check-attr text eol` after the change confirmed representative Markdown, YAML, HTML, CSS, dotfile, license, and Python files now resolve to `text: set` and `eol: lf`.
- `git ls-files --eol` after the change showed the current tracked text file mix resolving to `attr/text eol=lf`.
- `git add --renormalize --dry-run .` was run as a dry-run only; it listed the now-covered tracked text candidates, but no actual renormalization or staging was performed.
- `git diff --check` passed.
- No exporter code or version files were changed.
- No POST/PUT/DELETE/PATCH paths, service calls, state changes, export key changes, status field changes, warning-shape changes, or token-like data were introduced.
- Touched Markdown files were checked for real line breaks and merge-conflict markers.

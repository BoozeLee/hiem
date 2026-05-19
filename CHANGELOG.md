# Changelog

## [0.1.1] — 2025-05-19

### Added
- Interactive chat mode (`hiem chat`) — Claude Code-style engineering agent
- File operations: read, edit, search, list files
- LLM integration with Claude fallback
- Phase discipline in chat commands
- Slash commands: /files, /status, /commits, /search, /read, /edit, /test, /lint, /gh, /pr, /issue, /ci, /release, /context

### Security
- All edits require confirmation
- Diff preview before applying changes
- No secrets exposed in chat output

## [0.1.0] — 2025-05-19

### Added
- Full CLI surface: `whoami`, `doc`, `settings`, `pr`, `issue`, `ci`, `release`, `run`, `search`, `label`, `branch`
- Typer-based command framework
- Safe subprocess runner (`gh` always called via list args, no `shell=True`)
- Secret redaction utility
- Phase discipline (P1–P5) for all mutating commands
- Unit tests for runner, redaction, phases, and CLI smoke tests
- GitHub Actions CI workflow
- `pyproject.toml` with modern packaging
- `README.md`, `LICENSE.md`, `SECURITY.md`, `CHANGELOG.md`

### Security
- Token redaction before all stdout/stderr writes
- Subprocess arguments never passed as shell strings
- `.gitignore` blocks PEM, `.env`, and token files

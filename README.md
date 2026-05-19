# HIEM — High-fidelity Engineering that Moves

![MIT](https://img.shields.io/badge/license-MIT-green.svg)

> **Correctness before cleverness. Security is mandatory.**

HIEM is a **local CLI engineering agent** built on top of the GitHub CLI (`gh`) and the GitHub REST API. It wraps `gh` subcommands in structured, axiom-driven workflows so that every engineering operation follows the same quality discipline.

```
uv tool install hiem
hiem <command>
```

---

## What HIEM is

- A **local CLI tool** that makes GitHub operations reproducible, reviewable, and auditable.
- Built on `gh auth` — reuses your existing `gh` session; **no extra tokens needed**.
- Enforces **7 axioms** and **5-phase discipline** on every mutating operation.
- Open source, part of the **Kilo Platform** (`kilocode.ai`).

## What HIEM is NOT

- **Not a GitHub App** — HIEM is not an OAuth or GitHub App marketplace integration.
- **Not a bot account** — HIEM does not drive a service account; it uses *your* authenticated `gh` session.
- **Not a long-lived daemon** — it's a CLI you run when you need it.

## Prerequisites

| Requirement | Notes |
|---|---|
| `gh` (GitHub CLI) | Already authenticated via `gh auth login` |
| Python 3.10+ | For local installs |
| `uv` (recommended) | For installation |

Verify `gh` is authenticated:

```
gh auth status
```

## Install

```bash
# Recommended — installs as an isolated tool
uv tool install hiem

# Alternative — from source
git clone https://github.com/BoozeLee/hiem
cd hiem && uv pip install -e .

# Alternative — npm
npm install -g @hiem/cli
```

## Quickstart

```bash
# Verify identity
hiem whoami

# Print the engineering prompt (axioms + phases)
hiem doc

# Show local config
hiem settings

# Manage PRs
hiem pr list
hiem pr review 42
hiem pr merge 42
hiem pr close 42

# Manage issues
hiem issue list
hiem issue triage 17

# CI
hiem ci runs
hiem ci watch 123456
hiem ci rerun 123456

# Releases
hiem release notes
hiem release create

# Dispatch a workflow
hiem run deploy.yml

# Other
hiem search "authentication bug"
hiem label list
hiem branch clean
```

## Command Reference

| Command | Description |
|---|---|
| `hiem whoami` | Show authenticated identity; never prints tokens |
| `hiem doc` | Print the full HIEM engineering prompt |
| `hiem settings` | Show local config; never prints secrets |
| `hiem pr list` | List PRs with `--state`, `--limit`, `--json` |
| `hiem pr review N` | Read-only structured PR review (no review posted) |
| `hiem pr merge N` | Squash-merge after phase checks; `--force` override |
| `hiem pr close N` | Close with reason comment |
| `hiem issue list` | List issues with filter options |
| `hiem issue triage N` | Classify + suggest labels; `--apply` to apply |
| `hiem ci runs` | Recent GitHub Actions runs |
| `hiem ci watch N` | Watch a running workflow live |
| `hiem ci rerun N` | Rerun a workflow (phases printed) |
| `hiem release create` | Create release (phases printed) |
| `hiem release notes` | Show last release notes; no create |
| `hiem run <workflow>` | Dispatch a workflow file (phases printed) |
| `hiem search <query>` | Search GitHub repos/code/issues/PRs |
| `hiem label list` | List repo labels |
| `hiem branch clean` | Delete merged local branches (safe defaults) |

## Core Axioms

| # | Axiom |
|---|---|
| 1 | **Correctness before cleverness** — if a simpler provably correct solution exists, use it |
| 2 | **Security is mandatory** — every surface area is a threat surface |
| 3 | **Delete fluently** — no dead code, no commented-out TODO blocks |
| 4 | **YAGNI ruthlessly** — abstractions need at least two call-sites today |
| 5 | **One PR, one intent** — refactor + bug-fix + feature = three PRs |
| 6 | **Readable > brief** — spell-out names; abbreviations only for `id`, `url`, `ctx` |
| 7 | **APIs are contracts** — changing a public signature = version bump first |

## Phase Discipline

Before touching any line of code, every mutating command shows all five phases:

```
P1 📖  Ground truth — read state before writing
P2 📐  Plan — one-paragraph summary
P3 🔨  Change — exact action being performed
P4 ✅  Verify — what must succeed afterwards
P5 📋  Report — result and next step
```

## Security Model

- **No secrets in output** — tokens are redacted with `***REDACTED***` before any log, error, or stdout write.
- **No `shell=True`** — every subprocess call passes arguments as a list.
- **No hardcoded credentials**, PEM files, or API keys anywhere in the repo.
- **Structured exit codes** — non-zero on failure so CI can react.
- **Timeouts** on every API call — no hanging processes.
- All user values are passed as separate list items; never interpolated into shell strings.

## Examples

```bash
# Review PR 137 before merging
hiem pr review 137
hiem pr merge 137

# Triage issue with dry-run
hiem issue triage 55
hiem issue triage 55 --apply  # actually applies suggested labels

# CI
hiem ci runs
hiem ci watch 78432109
hiem ci rerun 78432109

# Release with auto-generated notes
hiem release create

# Neat local branch cleanup
hiem branch clean
```

## Project Structure

```
hiem/
├── src/hiem/
│   ├── cli.py          # Typer app + subcommands
│   ├── runner.py       # Subprocess — gh
│   ├── config.py       # Settings / env
│   ├── redact.py       # Secret redaction
│   ├── phases.py       # P1–P5 rendering
│   └── commands/       # Subcommand modules
├── tests/              # Unit + smoke tests
└── pyproject.toml      # Package meta
```

## Development

```bash
uv pip install -e ".[dev]"
pytest
ruff check src/ tests/
python -m compileall src/
python -m build
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).  
HIEM follows its own axioms as the contribution guide.

## License

MIT © Kiliaan Vanvoorden / BoozeLee.  
Part of the [Kilo Platform](https://kilocode.ai).

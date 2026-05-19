"""hiem — High-fidelity Engineering that Moves.

CLI entry point. Typer-based, subcommands map to engineering operations.
All sub-command modules define their own ``app = typer.Typer(...)`` at
module scope; they are lazy-imported below.
"""

from __future__ import annotations

import typer


app = typer.Typer(
    name="hiem",
    no_args_is_help=True,
    help=(
        "HIEM — High-fidelity Engineering that Moves.\n\n"
        "Engineering-grade GitHub operations CLI. Wraps `gh` and the GitHub REST API."
    ),
)


@app.callback(invoke_without_command=True)
def _global(
    version: bool | None = typer.Option(
        None, "--version", help="Show version and exit", is_eager=True
    ),
) -> None:
    """HIEM CLI — global options."""
    from hiem import __version__ as _v

    if version:
        typer.echo(f"hiem {_v}")
        raise typer.Exit()


@app.command()
def whoami() -> None:
    """Show the authenticated identity and session info.

    Uses ``gh api user``. Tokens are never printed.
    """
    from ..phases import phase_separator

    phase_separator("whoami")
    result = typer.run(["gh", "api", "user", "--jq", ".login, .name, .id, .html_url"])
    typer.echo(result.stdout)


@app.command()
def doc() -> None:
    """Print the HIEM engineering prompt (axioms, phases, CLI reference)."""
    prompt = """\
HIEM — High-fidelity Engineering that Moves
https://boozelee.github.io/hiem-site/

  8 core axioms:
  1. Correctness before cleverness
  2. Security is mandatory
  3. Delete fluently
  4. YAGNI ruthlessly
  5. One PR, one intent
  6. Readable over brief
  7. APIs are contracts

  Phase discipline (always):
  P1  Ground truth acquisition — read before writing
  P2  Design & plan — one-paragraph plan, todo tracking
  P3  Implementation — smallest correct change
  P4  Verification — type-check, test, lint, security lens
  P5  Cleanup — remove dead code, update docs

  GitHub-native workflows:
  . PR review    — classifies fix/security/style
  . Issue triage — root cause → paths → fix → tests
  . CI/CD diag   — flakes/env/regression/config drift
  . Release mgmt — SemVer + conventional changelog

  Security guardrails:
  . Hardcoded creds → Critical
  . SQL concat → Critical
  . eval/new Function → Critical
  . JWT without exp → Critical
  . CORS * in prod → High
"""
    typer.echo(prompt)


@app.command()
def settings() -> None:
    """Show HIEM CLI and gh session configuration. Never prints secrets."""
    from ..config import effective_settings
    from ..phases import print_phases

    print_phases("settings", [("P1", "Read local config and gh session"), ("P5", "Printed above")])
    settings = effective_settings()
    for k, v in settings.items():
        typer.echo(f"  {k:<20} {v}")


@app.command()
def search(query: str) -> None:
    """Search GitHub code, issues, PRs, or repos."""
    typer.run(["gh", "search", "repos", query])


# ── sub-apps (lazy import avoids circular register timing) ───────────────────
def _load(name: str) -> typer.Typer:
    """Lazy-load a sub-command module and return its ``app`` Typer instance."""
    import importlib

    mod = importlib.import_module(f"hiem.commands.{name}")
    return mod.app  # type: ignore[no-any-return]


app.add_typer(_load("pr"), name="pr")
app.add_typer(_load("issue"), name="issue")
app.add_typer(_load("ci"), name="ci")
app.add_typer(_load("release"), name="release")
app.add_typer(_load("label"), name="label")
app.add_typer(_load("branch"), name="branch")
app.add_typer(_load("run_cmd"), name="run")


def main() -> None:
    """Entry point used by the ``hiem`` console script."""
    app()


if __name__ == "__main__":
    main()

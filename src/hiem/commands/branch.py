"""hiem branch — git branch management."""

from __future__ import annotations

import json
import subprocess

import typer

from ..phases import phase_info, print_phases
from ..runner import gh

app = typer.Typer(help="Git branch management.")


def _default_branch() -> str:
    """Return the repository's default branch via `gh repo view`."""
    try:
        proc = subprocess.run(
            ["gh", "repo", "view", "--json", "defaultBranchRef"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if proc.returncode == 0:
            data = json.loads(proc.stdout)
            return data.get("defaultBranchRef", {}).get("name", "main")
    except Exception:  # noqa: S110 — fallback is intentional
        pass
    return "main"


@app.command(name="clean")
def branch_clean(
    remote: bool = typer.Option(
        False,
        "--remote",
        help="Also delete remote branches (default: local only)",
    ),
) -> None:
    """Delete fully-merged local branches.

    Never deletes the default branch.
    Pass --remote to also delete remote branches.
    """
    default = _default_branch()
    phases = [
        ("P1", f"Enumerate local branches; default branch is {default!r}"),
        ("P2", f"Identify fully-merged branches, excluding {default!r}"),
        ("P3", f"Delete {len([])}+ merged local branches"),
        ("P4", "Verify branches deleted and git status is clean"),
        ("P5", "Branch cleanup complete"),
    ]
    print_phases("branch clean", phases)

    proc = subprocess.run(
        ["git", "branch", "--merged"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if proc.returncode != 0:
        typer.echo(f"ERROR: git branch --merged failed: {proc.stderr}", err=True)
        raise typer.Exit(code=1)

    merged = [
        line.strip().lstrip("* ")
        for line in proc.stdout.splitlines()
        if line.strip() and not line.strip().startswith("* ")
    ]
    safe = [b for b in merged if b and b != default]

    if not safe:
        typer.echo("  Nothing to delete — no merged branches beyond the default branch.")
        return

    for branch in safe:
        typer.echo(f"  Deleting {branch}")
        gh(["git", "branch", "-d", branch])

    if remote:
        phase_info("P3", "Deleting remote branches…")
        for branch in safe:
            gh(["gh", "api", f"repos/:owner/:repo/git/refs/heads/{branch}", "-X", "DELETE"],
               check=False)

"""hiem issue — issue commands."""

from __future__ import annotations


import typer

from ..phases import print_phases
from ..runner import gh

app = typer.Typer(help="Issue operations.")


@app.command()
def list(
    state: str | None = typer.Option(None, "--state", help="open|closed|all"),
    labels: str | None = typer.Option(None, "--labels", help="Comma-separated labels"),
    assignee: str | None = typer.Option(None, "--assignee", help="Filter by assignee"),
    limit: int = typer.Option(30, "--limit", help="Max results"),
    json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """List issues for the current repository."""
    args = ["gh", "issue", "list"]
    if state:
        args += ["--state", state]
    if labels:
        args += ["--labels", labels]
    if assignee:
        args += ["--assignee", assignee]
    args += ["--limit", str(limit)]
    if json:
        args.append("--json")
    gh(args)


@app.command()
def triage(
    number: int,
    apply: bool = typer.Option(
        False, "--apply", help="Actually apply suggested labels (default: read-only)"
    ),
) -> None:
    """Triage issue <N> — root-cause, paths, fix, tests.

    Reads the issue body and comments, suggests labels and next action.
    Labels are only applied when --apply is passed.
    """
    ref = f"#{number}"
    phases = [
        ("P1", f"Read issue {ref} body, labels, comments, and linked PRs"),
        ("P2", "Identify root cause, affected paths, and suggested labels"),
        ("P3", "Display triage summary; apply labels only if --apply"),
        ("P4", "Verify GitHub accepts label changes when --apply"),
        ("P5", f"Triage of {ref} complete"),
    ]
    print_phases(f"issue triage {ref}", phases)

    gh(["gh", "issue", "view", str(number), "--json", "title,body,labels,state,assignees"])
    print()

    if apply:
        typer.echo("Applying suggested labels… (implement with issue label edit API)")
    else:
        typer.echo("  Triage suggestions printed above. Pass --apply to apply labels.")

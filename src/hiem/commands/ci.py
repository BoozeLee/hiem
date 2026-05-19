"""hiem ci — CI / workflow operations."""

from __future__ import annotations

import typer

from ..phases import print_phases
from ..runner import gh

app = typer.Typer(help="CI / workflow operations.")


@app.command()
def runs(limit: int = typer.Option(30, "--limit", help="Max workflow runs to list")) -> None:
    """List recent GitHub Actions workflow runs."""
    gh(["gh", "run", "list", "--limit", str(limit)])


@app.command()
def watch(run_id: int = typer.Argument(..., help="Workflow run ID to watch in real time")) -> None:
    """Watch a running GitHub Actions workflow in real time."""
    gh(["gh", "run", "watch", str(run_id)])


@app.command()
def rerun(
    run_id: int = typer.Argument(..., help="Workflow run ID to rerun"),
) -> None:
    """Rerun a GitHub Actions workflow run.

    Must print P1-P5 phases before rerunning.
    """
    run_ref = str(run_id)
    phases = [
        ("P1", f"Read run {run_ref} status before rerun"),
        ("P2", "Confirm rerun intent and required permissions"),
        ("P3", f"Trigger rerun of run {run_ref}"),
        ("P4", "Verify rerun accepted by GitHub"),
        ("P5", f"Run {run_ref} rerun triggered"),
    ]
    print_phases(f"ci rerun {run_ref}", phases)
    gh(["gh", "run", "rerun", run_ref])

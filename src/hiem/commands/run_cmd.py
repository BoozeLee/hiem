"""hiem run — workflow dispatch."""

from __future__ import annotations

import json

import typer

from ..phases import print_phases
from ..runner import gh

app = typer.Typer(help="Workflow dispatch.")


@app.command()
def run(
    workflow: str = typer.Argument(..., help="Workflow file name, e.g. deploy.yml"),
    inputs: str | None = typer.Option(
        None, "--inputs", help="JSON string of inputs, e.g. '{\"env\": \"staging\"}'"
    ),
) -> None:
    """Dispatch a GitHub Actions workflow.

    Must print P1-P5 phases before dispatching.
    """
    args = ["workflow", "run", workflow]
    if inputs:
        try:
            data = json.loads(inputs)
            for k, v in data.items():
                args += ["-f", f"{k}={v}"]
        except json.JSONDecodeError:
            typer.echo("ERROR: --inputs must be valid JSON", err=True)
            raise typer.Exit(code=1) from None

    phases = [
        ("P1", f"Read workflow manifest: {workflow!r}"),
        ("P2", "Confirm inputs and required permissions"),
        ("P3", f"Dispatch workflow {workflow!r}"),
        ("P4", "Verify GitHub accepted the dispatch"),
        ("P5", f"Workflow {workflow!r} dispatched"),
    ]
    print_phases(f"run {workflow}", phases)
    gh(args)

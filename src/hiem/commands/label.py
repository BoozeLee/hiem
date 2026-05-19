"""hiem label — issue / PR label management."""

from __future__ import annotations

import typer

from ..runner import gh

app = typer.Typer(help="Issue and PR label management.")


@app.command(name="list")
def label_list() -> None:
    """List all labels for the current repository."""
    gh(["gh", "label", "list"])

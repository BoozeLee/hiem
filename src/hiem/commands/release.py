"""hiem release — release management."""

from __future__ import annotations

import re
from pathlib import Path

import typer

from ..phases import print_phases
from ..runner import gh

app = typer.Typer(help="Release management.")


def _detect_version() -> str:
    """Read version from pyproject.toml. Fall back to 0.1.0."""
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        return "0.1.0"
    text = pyproject.read_text(encoding="utf-8")
    m = re.search(r'version\s*=\s*"([^"]+)"', text)
    if m:
        return m.group(1)
    return "0.1.0"


@app.command()
def notes() -> None:
    """Show last release notes. Does NOT create a release."""
    try:
        result = gh(["release", "view", "--json", "body"])
        typer.echo(result.stdout)
    except SystemExit:
        typer.echo("No prior release found. Showing recent commits:")
        gh(["git", "log", "--oneline", "-20"])


@app.command()
def create(
    tag: str | None = typer.Option(
        None,
        "--tag",
        help="Release tag (default: v<version from pyproject.toml>)",
    ),
    notes_file: str | None = typer.Option(
        None, "--notes-file", help="Path to a file containing release notes"
    ),
    generate_notes: bool = typer.Option(
        False, "--generate-notes", help="Auto-generate release notes from git history"
    ),
    replace: bool = typer.Option(
        False, "--replace", help="Replace an existing release of the same tag"
    ),
) -> None:
    """Create a GitHub release with phase discipline.

    Detects version from pyproject.toml if --tag is not given.
    """
    detected_version = _detect_version()
    release_tag = tag or f"v{detected_version}"
    phases = [
        ("P1", f"Detected version {detected_version!r} from pyproject.toml"),
        ("P2", f"Prepare release tag {release_tag!r}"),
        ("P3", f"Create GitHub release {release_tag!r}"),
        ("P4", "Verify release appears in GitHub"),
        ("P5", f"Release {release_tag!r} created"),
    ]
    print_phases(f"release create {release_tag}", phases)

    args = ["release", "create", release_tag]
    if notes_file:
        args += ["--notes-file", notes_file]
    elif generate_notes:
        args.append("--generate-notes")
    if replace:
        args.append("--yes")

    try:
        gh(args)
    except SystemExit as exc:
        typer.echo(
            f"ERROR: Release tag {release_tag!r} already exists. "
            "Pass --replace to recreate.",
            err=True,
        )
        raise typer.Exit(code=1) from exc

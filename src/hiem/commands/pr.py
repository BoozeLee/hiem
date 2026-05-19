"""hiem pr — pull request commands."""

from __future__ import annotations


import typer

from ..phases import print_phases, phase_info, phase_separator
from ..runner import gh

app = typer.Typer(help="Pull request operations.")


def _pr_ref(number: int) -> str:
    return f"#{number}"


@app.command()
def list(
    state: str | None = typer.Option(None, "--state", help="open|closed|all"),
    limit: int = typer.Option(30, "--limit", help="Max results"),
    json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """List pull requests for the current repository."""
    args = ["pr", "list"]
    if state:
        args += ["--state", state]
    args += ["--limit", str(limit)]
    if json:
        args.append("--json")
    gh(args)


@app.command()
def review(number: int) -> None:
    """Structured HIEM-grade review of PR <N>.

    Reads PR metadata, files changed, checks, and risk notes.
    Does NOT post a GitHub review.
    """
    ref = _pr_ref(number)
    phase_separator(f"pr review {ref}")
    phase_info("P1", f"Read PR {ref} metadata, diff, and associated checks")
    phase_info("P2", "Classify change as fix / security / style / feature")
    phase_info("P3", "No GitHub review will be posted — read-only inspection")
    phase_info("P4", "Verify checks pass and note any failures")
    phase_info("P5", "Summary printed to stdout")

    gh(
        [
            "pr",
            "view",
            str(number),
            "--json",
            "title,body,state,headRefName,baseRefName,author,mergeable",
        ]
    )
    print()
    phase_info("", "── Files changed ──")
    gh(["pr", "diff", str(number)])
    print()
    phase_info("", "── Checks ──")
    gh(["pr", "checks", str(number)])
    print()
    phase_info("P5", f"Review of {ref} complete. No review was posted.")


@app.command()
def merge(
    number: int,
    force: bool = typer.Option(False, "--force", help="Merge even if checks are not green"),
) -> None:
    """Merge PR <N> after phase checks.

    Prefer squash merge. Refuse to merge if checks are not passing unless --force.
    """
    ref = _pr_ref(number)
    phases = [
        ("P1", f"Read PR {ref} state, mergeable flag, and checks"),
        ("P2", "Confirm one intent, one PR, all checks passing"),
        ("P3", f"Squash-merge {ref}"),
        ("P4", "Verify merge succeeded and branch closed"),
        ("P5", f"{ref} merged"),
    ]
    print_phases(f"pr merge {ref}", phases)

    if not force:
        # Check status — gh pr checks returns 1 if not all passing
        try:
            gh(["pr", "checks", str(number)], check=False)
        except SystemExit:
            typer.echo("ERROR: Not all checks are passing. Use --force to override.", err=True)
            raise typer.Exit(code=1) from None

    gh(["pr", "merge", str(number), "--squash", "--delete-branch"])


@app.command()
def close(
    number: int,
    reason: str | None = typer.Argument(
        None, help="Reason for closing (default: no longer needed)"
    ),
) -> None:
    """Close PR <N> without merging."""
    ref = _pr_ref(number)
    close_reason = reason or "no longer needed"
    phases = [
        ("P1", f"Read PR {ref} state before closing"),
        ("P2", f"Confirm intent to close: {close_reason}"),
        ("P3", f"Close {ref}"),
        ("P4", "Verify PR is closed"),
        ("P5", f"{ref} closed"),
    ]
    print_phases(f"pr close {ref}", phases)
    gh(["pr", "close", str(number), "--comment", close_reason])

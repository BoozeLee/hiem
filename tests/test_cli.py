"""CLI smoke tests for hiem. No live GitHub calls."""

from __future__ import annotations

import subprocess
import sys

import typer
import typer.testing

import hiem.cli


_runner = typer.testing.CliRunner()


def _invoke(*args: str) -> typer.testing.Result:
    return _runner.invoke(hiem.cli.app, list(args))


def test_help():
    result = _invoke("--help")
    assert result.exit_code == 0
    assert "HIEM" in result.stdout


def test_version():
    result = _invoke("--version")
    assert result.exit_code == 0


def test_doc():
    result = _invoke("doc")
    assert result.exit_code == 0
    assert "Correctness" in result.stdout


def test_security_no_secrets_in_help_output() -> None:
    result = _invoke("--help")
    assert result.exit_code == 0
    # must not leak any real tokens or private key blocks
    assert "gho_" not in result.stdout
    assert "ghp_" not in result.stdout
    assert "PRIVATE KEY" not in result.stdout


def test_no_real_token_in_source():
    """Scan source tree for real token values, excluding pattern-definition files."""
    import pathlib

    repo_root = pathlib.Path(__file__).parent.parent

    # Real GitHub tokens are pattern + 20+ chars
    bad = [
        "gho_" + "a" * 21,
        "ghp_" + "a" * 21,
        "ghs_" + "a" * 21,
        "github_pat_" + "a" * 21,
    ]
    scan = (
        "import pathlib\n"
        f"root = pathlib.Path('{repo_root}')\n"
        f"bads = {bad}\n"
        "for p in sorted(root.rglob('*.py')):\n"
        "    for tgt in bads:\n"
        "        if tgt in p.read_text():\n"
        "            print('FOUND_SECRET', p, tgt)\n"
        "            raise SystemExit(1)\n"
        "print('NO_SECRETS')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", scan],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert "FOUND_SECRET" not in result.stdout, (
        f"Token-like strings found in source:\n{result.stdout}"
    )

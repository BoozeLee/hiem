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
    result = subprocess.run(
        [
            sys.executable, "-c",
            "import pathlib\n"
            "found = []\n"
            "root = pathlib.Path('{}')\n"
            "for f in sorted(root.rglob('*.py')):\n"
            "    if f.name in {'runner.py', 'redact.py'}:\n"
            "        continue\n"
            "    text = f.read_text()\n"
            "    for pat in ['gho_','ghp_','ghs_','github_pat_','-----BEGIN']:\n"
            "        idx = text.find(pat)\n"
            "        if idx >= 0:\n"
            "            tail = text[idx+len(pat):]\n"
            "            more = tail[:10]\n"
            "            if any(c.isalnum() for c in more):\n"
            "                found.append(f'{f}:{pat}')\n"
            "print('FOUND_SECRET' if found else 'NO_SECRETS')\n".format(repo_root),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert "FOUND_SECRET" not in result.stdout, (
        f"Token-like strings found in source:\n{result.stdout}"
    )

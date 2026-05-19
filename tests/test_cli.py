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
    assert "gho_" not in result.stdout
    assert "ghp_" not in result.stdout
    assert "PRIVATE KEY" not in result.stdout


def test_no_real_token_in_source():
    """Scan source tree for long token-like strings."""
    import pathlib

    repo_root = pathlib.Path(__file__).parent.parent
    # Build a script via the file system to avoid quoting hell
    script_path = repo_root / "_sec_scan.py"
    script_path.write_text(
        "import pathlib, re, sys\n"
        "root = pathlib.Path(sys.argv[1])\n"
        'prefixes = [\'gho_\', "ghp_", "ghs_", "github_pat_"]\n'
        "for p in sorted(root.rglob('*.py')):\n"
        '    if p.name in {"runner.py", "redact.py"}:\n'
        "        continue\n"
        "    t = p.read_text()\n"
        "    for pre in prefixes:\n"
        "        m = re.search(re.escape(pre) + r'[A-Za-z0-9_]{16,}', t)\n"
        "        if m:\n"
        '            print(f"FAIL {p} {m.group()[:40]}")\n'
        "            sys.exit(1)\n"
        'print("OK")\n'
    )
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), str(repo_root)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
        assert result.returncode == 0, (
            f"Token-like strings found:\n{result.stdout}\n{result.stderr}"
        )
    finally:
        script_path.unlink(missing_ok=True)

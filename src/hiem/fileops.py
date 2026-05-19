"""File operations for codebase inspection and editing."""

from __future__ import annotations

import difflib
import subprocess
from pathlib import Path


def read_file(path: str | Path) -> str:
    """Read a file's contents. Returns empty string if not found."""
    p = Path(path)
    if not p.exists():
        return f"File not found: {p}"
    return p.read_text(encoding="utf-8", errors="replace")


def list_files(root: str = ".", pattern: str = "*.py") -> list[str]:
    """List files matching pattern under root."""
    root_path = Path(root)
    return [str(p) for p in root_path.rglob(pattern) if p.is_file()]


def get_git_status() -> str:
    """Get git status summary."""
    try:
        proc = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.stdout or "Nothing to commit, working tree clean."
    except Exception:
        return "Not a git repository or git unavailable."


def get_changed_files() -> list[str]:
    """Get list of changed files in git."""
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return [f.strip() for f in proc.stdout.splitlines() if f.strip()]
    except Exception:
        return []


def apply_edit(file_path: str, old_text: str, new_text: str) -> str:
    """Apply an edit to a file. Returns diff summary."""
    p = Path(file_path)
    content = p.read_text(encoding="utf-8", errors="replace")

    if old_text not in content:
        return f"ERROR: old text not found in {file_path}"

    new_content = content.replace(old_text, new_text, 1)
    diff = difflib.unified_diff(
        content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=file_path,
        tofile=file_path,
    )
    diff_text = "".join(diff)

    p.write_text(new_content, encoding="utf-8")
    return diff_text or "No changes (text already matched)."


def run_tests(test_path: str | None = None) -> str:
    """Run pytest on test_path or all tests."""
    cmd = ["pytest"]
    if test_path:
        cmd.append(test_path)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return proc.stdout or proc.stderr or "Tests completed."
    except subprocess.TimeoutExpired:
        return "ERROR: Tests timed out after 120s"
    except Exception as e:
        return f"ERROR: {e}"


def run_linter() -> str:
    """Run ruff lint on src/."""
    try:
        proc = subprocess.run(
            ["ruff", "check", "src/"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return proc.stdout or proc.stderr or "Lint passed."
    except Exception as e:
        return f"ERROR: {e}"


def get_repo_root() -> Path:
    """Get the git repository root."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode == 0:
            return Path(proc.stdout.strip())
    except Exception:  # noqa: S110
        pass
    return Path.cwd()


def search_code(query: str, path: str = ".") -> list[str]:
    """Search for text in code files."""
    results = []
    root = Path(path)
    for py_file in root.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8", errors="replace")
            if query.lower() in content.lower():
                results.append(str(py_file))
        except Exception:  # noqa: S112
            continue
    return results


def get_recent_commits(n: int = 5) -> str:
    """Get recent git commits."""
    try:
        proc = subprocess.run(
            ["git", "log", "--oneline", f"-{n}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.stdout or "No commits."
    except Exception as e:
        return f"ERROR: {e}"

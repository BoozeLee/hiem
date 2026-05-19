"""Safe subprocess runner for gh commands.

All gh invocations go through this module so that:
- No shell string interpolation is ever used.
- All user values are passed as list arguments.
- Timeouts are applied to every call.
- Secrets are never included in traced args.
- Non-zero exit codes are surfaced as exceptions.
"""

from __future__ import annotations

import subprocess
import sys
from typing import Any

# Patterns that look like tokens — used for redaction in error/log output.
_TOKEN_PATTERNS = (
    "gho_",
    "ghp_",
    "github_pat_",
    "-----BEGIN",
    "ghs_",
    "ghat_",
)

_DEFAULT_TIMEOUT = 60


def _redact(text: str) -> str:
    """Replace token-like substrings with ***REDACTED***."""
    result = text
    for pat in _TOKEN_PATTERNS:
        idx = result.find(pat)
        if idx >= 0:
            end = idx + len(pat) + 40
            result = result[:idx] + "***REDACTED***" + result[end:]
    return result


def run(
    args: list[str],
    *,
    timeout: int = _DEFAULT_TIMEOUT,
    check: bool = True,
    capture: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Run gh (or any subprocess) safely.

    Args:
        args: Command + arguments as a list. Never pass a shell string.
        timeout: Seconds before killing the process.
        check: If True raise CalledProcessError on non-zero exit.
        capture: If True capture stdout/stderr; if False pipe to terminal.
        env: Optional environment overrides.

    Returns:
        CompletedProcess with stdout/stderr as strings (when capture=True).
    """
    cmd_display = " ".join(
        str(a) if not any(p in str(a) for p in _TOKEN_PATTERNS) else "<redacted>"
        for a in args
    )
    try:
        proc = subprocess.run(
            args,
            capture_output=capture,
            text=True,
            timeout=timeout,
            check=check,
            env=env,
        )
        return proc
    except subprocess.TimeoutExpired:
        print(f"ERROR: command timed out after {timeout}s: {cmd_display}", file=sys.stderr)
        raise
    except subprocess.CalledProcessError as exc:
        stdout = _redact(exc.stdout) if exc.stdout else ""
        stderr = _redact(exc.stderr) if exc.stderr else ""
        print(f"ERROR: command failed: {cmd_display}", file=sys.stderr)
        if stdout:
            print(f"  stdout: {stdout[:500]}", file=sys.stderr)
        if stderr:
            print(f"  stderr: {stderr[:500]}", file=sys.stderr)
        raise


def gh(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess:
    """Convenience wrapper: run gh with the given sub-command list."""
    return run(["gh"] + args, **kwargs)

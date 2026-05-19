"""LLM integration for Claude Code-style guidance."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any


def call_claude(messages: list[dict[str, str]]) -> str:
    """Call Claude API via claude-code CLI if available.

    Falls back to a stub response if claude is not installed.
    """
    claude_cmd = os.environ.get("CLAUDE_CMD", "claude")

    try:
        # Try to run claude via subprocess
        input_data = json.dumps({"messages": messages}).encode()
        proc = subprocess.run(
            [claude_cmd, "--messages", "-"],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout.strip()
    except FileNotFoundError:
        pass
    except Exception as e:
        return f"[LLM unavailable: {e}]"

    # Fallback: simple rule-based responses
    return _fallback_response(messages)


def _fallback_response(messages: list[dict[str, str]]) -> str:
    """Simple fallback when Claude CLI is not available."""
    last_msg = messages[-1].get("content", "") if messages else ""
    last_msg_lower = last_msg.lower()

    if any(kw in last_msg_lower for kw in ["fix", "bug", "error"]):
        return "To fix: 1) Read files, 2) Identify cause, 3) Apply change, 4) Run tests."
    elif any(kw in last_msg_lower for kw in ["test", "pytest"]):
        return "Run: pytest src/ tests/"
    elif any(kw in last_msg_lower for kw in ["pr", "merge", "review"]):
        return "Use hiem pr review <N>, then hiem pr merge <N> after checks pass."
    elif any(kw in last_msg_lower for kw in ["issue", "triage"]):
        return "Use hiem issue triage <N>. Pass --apply to apply labels."
    elif any(kw in last_msg_lower for kw in ["ci", "rerun", "fail"]):
        return "Use hiem ci rerun <run-id> to retry failed workflow."
    elif any(kw in last_msg_lower for kw in ["release", "create"]):
        return "Use hiem release create. Version from pyproject.toml."
    elif any(kw in last_msg_lower for kw in ["edit", "change", "modify"]):
        return "I can help edit files. What file would you like to edit?"
    elif any(kw in last_msg_lower for kw in ["read", "view", "show", "cat"]):
        return "What file would you like me to read?"
    else:
        return "I can help with: fixing bugs, running tests, managing PRs/issues/CI, editing files."


def format_context(context: dict[str, Any]) -> str:
    """Format tool context for LLM messages."""
    lines = [f"Context: {context.get('summary', '')}"]
    if context.get('files'):
        lines.append(f"Files: {', '.join(context['files'][:5])}")
    if context.get('git_status'):
        lines.append(f"Git status: {context['git_status'][:200]}")
    if context.get('recent_commits'):
        lines.append(f"Recent commits: {context['recent_commits']}")
    return "\n".join(lines)

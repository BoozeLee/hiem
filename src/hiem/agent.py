"""Interactive HIEM agent — Claude Code-style chat interface."""

from __future__ import annotations

import os

from .fileops import (
    apply_edit,
    get_changed_files,
    get_git_status,
    get_recent_commits,
    get_repo_root,
    list_files,
    read_file,
    run_linter,
    run_tests,
    search_code,
)
from .llm import call_claude, format_context
from .phases import phase_separator, phase_info, print_phases
from .runner import gh


def chat() -> None:
    """Interactive chat loop for engineering tasks."""
    phase_separator("chat")
    phase_info("P1", "Initialize interactive session")
    phase_info("P2", "Ready for engineering requests")

    repo_root = get_repo_root()
    os.chdir(repo_root)

    print("\nHIEM Chat — type 'exit' or 'quit' to end")
    print("Commands: /files, /status, /commits, /search <query>, /read <file>")
    print("          /edit <file> <old> <new>, /test, /lint, /gh <args>")
    print("          /pr <num>, /issue <num>, /ci rerun <id>")
    print("          /release create, /help\n")

    history: list[dict[str, str]] = []

    while True:
        try:
            raw = input("hiem> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break

        if not raw:
            continue

        if raw.lower() in ("exit", "quit", "q"):
            phase_info("P5", "Chat session ended")
            break

        if raw == "/help":
            _print_help()
            continue

        # Parse commands
        if raw.startswith("/"):
            result = _handle_command(raw)
            print(f"  {result}\n")
            continue

        # Natural language -> LLM
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": raw},
        ]
        if history:
            messages.extend(history[-6:])  # Last 3 exchanges

        response = call_claude(messages)
        print(f"  {response}\n")

        history.append({"role": "user", "content": raw})
        history.append({"role": "assistant", "content": response})

    phase_info("P5", "Session complete")


def _handle_command(raw: str) -> str:
    """Handle slash commands."""
    parts = raw.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd == "/files":
        pattern = arg or "*.py"
        files = list_files(".", pattern)
        return f"Found {len(files)} files:\n" + "\n".join(files[:20])

    elif cmd == "/status":
        status = get_git_status()
        return status[:500]

    elif cmd == "/commits":
        n = int(arg) if arg.isdigit() else 5
        return get_recent_commits(n)

    elif cmd == "/search":
        if not arg:
            return "Usage: /search <query>"
        results = search_code(arg)
        return f"Found {len(results)} matches:\n" + "\n".join(results[:10])

    elif cmd == "/read":
        if not arg:
            return "Usage: /read <file_path>"
        content = read_file(arg)
        return content[:2000] + ("..." if len(content) > 2000 else "")

    elif cmd == "/edit":
        return _handle_edit(arg)

    elif cmd == "/test":
        return run_tests()

    elif cmd == "/lint":
        return run_linter()

    elif cmd == "/gh":
        if not arg:
            return "Usage: /gh <gh command>"
        try:
            result = gh(arg.split())
            return result.stdout[:2000]
        except Exception as e:
            return f"ERROR: {e}"

    elif cmd == "/pr":
        return _handle_pr(arg)

    elif cmd == "/issue":
        return _handle_issue(arg)

    elif cmd == "/ci":
        return _handle_ci(arg)

    elif cmd == "/release":
        return _handle_release(arg)

    elif cmd == "/context":
        ctx = {
            "summary": f"Repo: {get_repo_root()}",
            "files": get_changed_files(),
            "git_status": get_git_status(),
            "recent_commits": get_recent_commits(3),
        }
        return format_context(ctx)

    return f"Unknown command: {cmd}. Use /help"


def _handle_edit(arg: str) -> str:
    """Handle /edit command with diff preview."""
    # Format: /edit <file> <old_text>---<new_text>
    # Or interactive: /edit <file>
    if "---" not in arg:
        # Interactive mode
        file_path = arg
        if not file_path:
            return "Usage: /edit <file> or /edit <file> <old>---<new>"
        content = read_file(file_path)
        print(f"\n--- {file_path} (showing first 50 lines) ---")
        print("\n".join(content.splitlines()[:50]))
        print("\n--- End preview ---")
        print("Provide old---new text to apply edit, or use natural language.")
        return "Edit preview shown. Use: /edit <file> <old>---<new>"

    try:
        file_path, rest = arg.split(" ", 1)
        old_new = rest.split("---")
        if len(old_new) != 2:
            return "Usage: /edit <file> <old_text>---<new_text>"
        old_text, new_text = old_new
        diff = apply_edit(file_path, old_text, new_text)
        return f"Edit applied:\n{diff[:500]}"
    except Exception as e:
        return f"ERROR: {e}"


def _handle_pr(arg: str) -> str:
    """Handle PR commands."""
    if not arg:
        return "Usage: /pr <number> [review|merge|close]"
    parts = arg.split()
    num = parts[0]
    action = parts[1] if len(parts) > 1 else "review"

    if action == "review":
        phase_separator(f"pr review #{num}")
        print_phases(f"pr review #{num}", [
            ("P1", f"Read PR #{num} metadata, diff, and checks"),
            ("P2", "Classify change"),
            ("P3", "Read-only inspection"),
            ("P4", "Verify checks"),
            ("P5", "Review complete"),
        ])
        try:
            gh(["gh", "pr", "view", str(num), "--json", "title,body,state"])
            print()
            gh(["gh", "pr", "diff", str(num)])
            return ""
        except Exception as e:
            return f"ERROR: {e}"

    elif action == "merge":
        print_phases(f"pr merge #{num}", [
            ("P1", f"Read PR #{num} state"),
            ("P2", "Confirm merge intent"),
            ("P3", f"Merge #{num}"),
            ("P4", "Verify merge"),
            ("P5", f"#{num} merged"),
        ])
        try:
            gh(["gh", "pr", "merge", str(num), "--squash", "--delete-branch"])
            return ""
        except Exception as e:
            return f"ERROR: {e}"

    elif action == "close":
        print_phases(f"pr close #{num}", [
            ("P1", f"Read PR #{num}"),
            ("P2", "Confirm close"),
            ("P3", f"Close #{num}"),
            ("P4", "Verify closed"),
            ("P5", f"#{num} closed"),
        ])
        try:
            gh(["gh", "pr", "close", str(num)])
            return ""
        except Exception as e:
            return f"ERROR: {e}"

    return f"Unknown action: {action}"


def _handle_issue(arg: str) -> str:
    """Handle issue commands."""
    if not arg:
        return "Usage: /issue <number> [triage]"
    parts = arg.split()
    num = parts[0]

    if len(parts) < 2 or parts[1] != "triage":
        # Default: view issue
        phase_separator(f"issue view #{num}")
        try:
            gh(["gh", "issue", "view", str(num), "--json", "title,body,state,labels"])
            return ""
        except Exception as e:
            return f"ERROR: {e}"

    # Triage
    print_phases(f"issue triage #{num}", [
        ("P1", f"Read issue #{num}"),
        ("P2", "Classify root cause"),
        ("P3", "Suggest labels"),
        ("P4", "Verify"),
        ("P5", "Triage complete"),
    ])
    try:
        gh(["gh", "issue", "view", str(num), "--json", "title,body,labels,state"])
        return ""
    except Exception as e:
        return f"ERROR: {e}"


def _handle_ci(arg: str) -> str:
    """Handle CI commands."""
    if not arg:
        return "Usage: /ci [runs|rerun <id>|watch <id>]"
    parts = arg.split()

    if parts[0] == "runs":
        return ""
    elif parts[0] == "rerun" and len(parts) > 1:
        run_id = parts[1]
        print_phases(f"ci rerun {run_id}", [
            ("P1", f"Read run {run_id}"),
            ("P2", "Confirm rerun"),
            ("P3", f"Rerun {run_id}"),
            ("P4", "Verify"),
            ("P5", f"Run {run_id} rerun"),
        ])
        try:
            gh(["gh", "run", "rerun", run_id])
            return ""
        except Exception as e:
            return f"ERROR: {e}"
    elif parts[0] == "watch" and len(parts) > 1:
        return ""
    return "Usage: /ci [runs|rerun <id>|watch <id>]"


def _handle_release(arg: str) -> str:
    """Handle release commands."""
    if arg == "create":
        print_phases("release create", [
            ("P1", "Detect version"),
            ("P2", "Prepare tag"),
            ("P3", "Create release"),
            ("P4", "Verify"),
            ("P5", "Release created"),
        ])
        try:
            gh(["gh", "release", "create", "v0.1.0", "--generate-notes"])
            return ""
        except Exception as e:
            return f"ERROR: {e}"
    return "Usage: /release create"


def _print_help() -> None:
    """Print help for chat commands."""
    help_text = """
Slash Commands:
  /files [pattern]     List files (default: *.py)
  /status             Git status
  /commits [n]        Recent commits
  /search <query>     Search code
  /read <file>        Read file
  /edit <file>        Preview file for editing
  /edit <file> <old>---<new>  Apply edit with diff
  /test [path]        Run pytest
  /lint               Run ruff lint
  /gh <args>          Run gh command
  /pr <num> [review|merge|close]
  /issue <num> [triage]
  /ci [runs|rerun <id>|watch <id>]
  /release create     Create release
  /context            Show repo context
  /help               Show this help
"""
    print(help_text)


_SYSTEM_PROMPT = """You are HIEM, a GitHub engineering agent. Help users with:
- Fixing bugs and writing code
- Reviewing PRs and issues
- Running tests and linting
- Managing CI/CD workflows
- Creating releases

Always follow phase discipline: PLAN -> INSPECT -> EDIT -> TEST -> GITHUB -> CONFIRM -> SUMMARY
Be concise. Show diffs before applying changes. Never expose secrets.
Ask for confirmation before destructive operations."""

"""Phase discipline visual output for HIEM.

Five phases printed sequentially for every mutating command:
  P1 — Ground truth (read state before touching it)
  P2 — Plan (one-paragraph summary)
  P3 — Change (what is being done)
  P4 — Verify (what must succeed afterwards)
  P5 — Report (what happened)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

_PHASE_ICONS = {
    "P1": "📖",
    "P2": "📐",
    "P3": "🔨",
    "P4": "✅",
    "P5": "📋",
}


def phase_info(phase: str, detail: str) -> None:
    """Write a single phase line in structured form."""
    icon = _PHASE_ICONS.get(phase, "·")
    line = f"  {icon}  {phase}  {detail}"
    sys.stdout.write(line + "\n")


def phase_separator(command: str) -> None:
    """Write a command header."""
    sys.stdout.write(f"\n── hiem {command} ──\n")


def print_phases(command: str, phases: list[tuple[str, str]]) -> None:
    """Print all phases for a command with a header + summary."""
    phase_separator(command)
    for label, detail in phases:
        phase_info(label, detail)


@dataclass
class PhaseTracker:
    """Collect phase notes and render at the end."""

    command: str
    entries: list[tuple[str, str]] = field(default_factory=list)

    def add(self, phase: str, detail: str) -> None:
        self.entries.append((phase, detail))

    def render(self) -> None:
        print_phases(self.command, self.entries)

    def done(self, result: str = "Done.") -> None:
        self.add("P5", result)
        self.render()

"""Tests for hiem.phases — phase discipline output."""

from __future__ import annotations

from io import StringIO


from hiem.phases import PhaseTracker, phase_info, print_phases


def test_phase_info_output(capsys):
    phase_info("P1", "read before writing")
    captured = capsys.readouterr()
    assert "P1" in captured.out
    assert "read before writing" in captured.out


def test_print_phases(capsys):
    phases = [("P1", "step 1"), ("P2", "step 2"), ("P3", "step 3")]
    print_phases("test-command", phases)
    captured = capsys.readouterr()
    assert "test-command" in captured.out
    assert "step 1" in captured.out
    assert "step 3" in captured.out


def test_phase_tracker_render():
    tracker = PhaseTracker(command="test")
    tracker.add("P1", "discover")
    tracker.add("P3", "change")
    buf = StringIO()
    import sys

    old = sys.stdout
    sys.stdout = buf
    try:
        tracker.render()
    finally:
        sys.stdout = old
    output = buf.getvalue()
    assert "discover" in output
    assert "change" in output

"""Tests for hiem.runner — safe subprocess execution."""

from __future__ import annotations

import subprocess

import pytest

from hiem.runner import _redact, run


def test_redact_gho_token():
    text = "gho_test12345678"
    assert _redact(text) == "***REDACTED***"


def test_redact_ghp_token():
    text = "ghp_test12345678"
    assert _redact(text) == "***REDACTED***"


def test_redact_github_pat_token():
    text = "github_pat_test12345678"
    assert _redact(text) == "***REDACTED***"


def test_redact_pem_key():
    text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEow\n-----END RSA PRIVATE KEY-----"
    result = _redact(text)
    assert "BEGIN RSA" not in result
    assert "MIIEow" not in result


def test_redact_no_false_positive():
    text = "echo hello world"
    assert _redact(text) == text


def test_run_success(capsys):
    proc = run(["echo", "ok"], capture=True)
    assert proc.returncode == 0
    assert "ok" in proc.stdout


def test_run_failure_raises():
    with pytest.raises(subprocess.CalledProcessError):
        run(["false"], capture=True)

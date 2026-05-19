"""Tests for hiem.redact — secret redaction."""

from __future__ import annotations


from hiem.redact import has_secret, redact


def test_redact_gho():
    assert redact("token=gho_abc123") == "token=***REDACTED***"


def test_redact_ghp():
    assert "ghp_" not in redact("ghp_xyz789 and more text")


def test_redact_ghs():
    assert "ghs_" not in redact("ghs_secret000")


def test_redact_github_pat():
    assert "github_pat_" not in redact("github_pat_abcdefg")


def test_redact_pem_block():
    pem = "bla\n-----BEGIN PRIVATE KEY-----\nABC\n-----END PRIVATE KEY-----\nend"
    result = redact(pem)
    assert "BEGIN PRIVATE KEY" not in result
    assert "ABC" not in result
    assert "***REDACTED_PRIVATE_KEY***" in result


def test_redact_env_assignment():
    assert redact("SECRET=hunter2") == "SECRET=***REDACTED***"


def test_redact_no_match():
    assert redact("safe text here") == "safe text here"


def test_has_secret_true():
    assert has_secret("gho_token") is True


def test_has_secret_false():
    assert has_secret("nothing here") is False

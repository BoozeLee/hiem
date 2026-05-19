"""Secret / token redaction utility.

Covers:
- GitHub tokens (gho_, ghp_, ghs_, ghat_, github_pat_)
- PEM private keys (-----BEGIN ...-----)
- Generic SECRET/TOKEN/API_KEY assignments in code
"""

from __future__ import annotations

import re

_PATTERNS = [
    # GitHub OAuth / fine-grained token
    (re.compile(r"(gho_[A-Za-z0-9_]+)"), "***REDACTED***"),
    (re.compile(r"(ghp_[A-Za-z0-9_]+)"), "***REDACTED***"),
    (re.compile(r"(ghs_[A-Za-z0-9_]+)"), "***REDACTED***"),
    (re.compile(r"(ghat_[A-Za-z0-9_]+)"), "***REDACTED***"),
    (re.compile(r"(github_pat_[A-Za-z0-9_]+)"), "***REDACTED***"),
    # PEM private key block
    (
        re.compile(
            r"(-----BEGIN (?:RSA |EC )?PRIVATE KEY-----.*?-----END (?:RSA |EC )?PRIVATE KEY-----)",
            re.DOTALL,
        ),
        "***REDACTED_PRIVATE_KEY***",
    ),
    # Generic SECRET/TOKEN env-style assignment
    (
        re.compile(r"((?:SECRET|TOKEN|API_KEY)\s*=\s*['\"]?)[^\s'\"]+"),
        r"\g<1>***REDACTED***",
    ),
]


def redact(text: str) -> str:
    """Return *text* with all known secret patterns replaced."""
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def has_secret(text: str) -> bool:
    """Return True if any secret pattern is found in *text*."""
    for pattern, _ in _PATTERNS:
        if pattern.search(text):
            return True
    return False

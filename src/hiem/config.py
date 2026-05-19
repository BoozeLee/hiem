"""HIEM configuration — local paths and effective settings.

Never prints secrets. Reads from env, then file, then defaults.
"""

from __future__ import annotations

import os
from pathlib import Path

_DEFAULT_CONFIG_DIR = Path.home() / ".config" / "hiem"
_DEFAULT_CONFIG_FILE = _DEFAULT_CONFIG_DIR / "config.json"


def config_path() -> Path:
    explicit = os.environ.get("HIEM_CONFIG")
    return Path(explicit) if explicit else _DEFAULT_CONFIG_FILE


def effective_settings() -> dict[str, str]:
    env_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    env_default_limit = os.environ.get("HIEM_LIMIT", "30")
    return {
        "config_path": str(config_path()),
        "gh_token_status": "present" if env_token else "absent",
        "default_limit": env_default_limit,
    }

#!/usr/bin/env python3
"""
Configuration for the AI-GM system (game-system-agnostic core).

The core knows nothing about any game system and nothing about any
specific campaign:
  - Game rules    come from the active system package (systems/<id>/),
                  selected by ACTIVE_SYSTEM (env, default "dcc").
  - Campaign data comes from the active campaign directory, selected by
                  DATA_DIR (env, e.g. ./campaigns/dying_earth).

Rules never live here. Systems and campaigns are pluggable; see
systems/README.md and campaigns/README.md.
"""

import os
import sys
from pathlib import Path

# Repo root (gm_core/config.py -> parent = gm_core -> parent = repo root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Active campaign data root (env-driven; default: campaigns/default)
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "campaigns" / "default"))).resolve()
ADVENTURES_DIR = DATA_DIR / "adventures"
WORLD_STATE_DIR = DATA_DIR / "world_state"
CHARACTERS_DIR = DATA_DIR / "characters"

# Ensure directories exist
for dir_path in [DATA_DIR, ADVENTURES_DIR, WORLD_STATE_DIR, CHARACTERS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


def active_system() -> str:
    """Return the active game-system id (env ACTIVE_SYSTEM, default 'dcc')."""
    return os.getenv("ACTIVE_SYSTEM", "dcc")


def load_system_rules(system_id: str) -> str:
    """Load the rules reference for a game system via the systems registry.

    Returns the system's rules_text() (markdown), or a placeholder message
    if the system is missing or broken — the core must never crash because
    a system module is incomplete.
    """
    if BASE_DIR not in [Path(p).resolve() for p in sys.path]:
        sys.path.insert(0, str(BASE_DIR))
    try:
        mod = __import__(f"systems.{system_id}", fromlist=["rules_text"])
        return mod.rules_text()
    except Exception as exc:  # registry must degrade gracefully
        return f"[system rules unavailable for '{system_id}': {exc}]"


# API Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Discord Configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
DISCORD_GAME_CHANNEL_ID = os.getenv("DISCORD_GAME_CHANNEL_ID", "")


def validate_config():
    """Validate configuration on startup."""
    errors = []

    if not DEEPSEEK_API_KEY:
        errors.append("DEEPSEEK_API_KEY environment variable not set")

    # Discord is optional for CLI mode
    if not DISCORD_BOT_TOKEN:
        print("⚠️  DISCORD_BOT_TOKEN not set - Discord features disabled")

    if not DISCORD_GAME_CHANNEL_ID:
        print("⚠️  DISCORD_GAME_CHANNEL_ID not set - Discord features disabled")

    # Check data directories
    for dir_path, name in [
        (ADVENTURES_DIR, "adventures"),
        (WORLD_STATE_DIR, "world_state"),
        (CHARACTERS_DIR, "characters"),
    ]:
        if not dir_path.exists():
            errors.append(f"Data directory missing: {dir_path}")

    return errors


if __name__ == "__main__":
    errors = validate_config()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        exit(1)
    else:
        print(f"Configuration valid (system={active_system()}, data={DATA_DIR})")

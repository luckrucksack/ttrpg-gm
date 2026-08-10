"""gm_core — game-system-agnostic AI Game Master engine.

This package is the core of the AI-GM system. It knows nothing about any
specific game system and nothing about any specific campaign. All game
rules come from `systems/<id>/`, all campaign data comes from the active
campaign directory (see gm_core/config.py: DATA_DIR).
"""

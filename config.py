#!/usr/bin/env python3
"""
Configuration for AI TTRPG GM System
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ADVENTURES_DIR = DATA_DIR / "adventures"
WORLD_STATE_DIR = DATA_DIR / "world_state"
CHARACTERS_DIR = DATA_DIR / "characters"

# Ensure directories exist
for dir_path in [DATA_DIR, ADVENTURES_DIR, WORLD_STATE_DIR, CHARACTERS_DIR]:
    dir_path.mkdir(exist_ok=True)

# API Configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# Discord Configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
DISCORD_GAME_CHANNEL_ID = os.getenv("DISCORD_GAME_CHANNEL_ID", "")

# System Rules Reference (D&D 5e basics)
SYSTEM_RULES = """
Dungeons & Dragons 5th Edition Rules Reference:

ABILITY SCORES & MODIFIERS:
- Strength (STR): Athletics
- Dexterity (DEX): Acrobatics, Sleight of Hand, Stealth
- Constitution (CON): No skills
- Intelligence (INT): Arcana, History, Investigation, Nature, Religion
- Wisdom (WIS): Animal Handling, Insight, Medicine, Perception, Survival
- Charisma (CHA): Deception, Intimidation, Performance, Persuasion

SKILL CHECKS: d20 + ability modifier + proficiency (if proficient)
SAVING THROWS: d20 + ability modifier + proficiency (if proficient)
ATTACK ROLLS: d20 + ability modifier + proficiency
DAMAGE ROLLS: Weapon/spell dice + ability modifier (if applicable)

COMBAT:
- Initiative: d20 + DEX modifier
- Armor Class (AC): 10 + DEX modifier (unarmored) or armor base + DEX (max)
- Hit Points: Current/Total
- Conditions: Blinded, Charmed, Deafened, Frightened, Grappled, etc.

MAGIC:
- Spell Slots: Level 1-9, tracked per class
- Spell Save DC: 8 + proficiency + spellcasting ability modifier
- Spell Attack: d20 + proficiency + spellcasting ability modifier

COMMON DICE:
- d4, d6, d8, d10, d12, d20, d100
- Advantage: Roll 2d20, take higher
- Disadvantage: Roll 2d20, take lower

This is a simplified reference. The full adventure text provides specific rules.
"""

# Validation
def validate_config():
    """Validate configuration on startup"""
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
        (CHARACTERS_DIR, "characters")
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
        print("Configuration valid")
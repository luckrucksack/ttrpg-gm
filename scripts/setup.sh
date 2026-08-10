#!/bin/bash
# Setup script for AI TTRPG GM System

set -e

echo "========================================="
echo "AI TTRPG GM System Setup"
echo "========================================="

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo -e "\nCreating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo -e "\nUpgrading pip..."
pip install --upgrade pip

# Install requirements
echo -e "\nInstalling requirements..."
pip install -r requirements.txt

# Create necessary directories (campaign layer, see campaigns/README.md)
echo -e "\nCreating directory structure..."
mkdir -p campaigns/dying_earth/{adventures,world_state,characters}
mkdir -p logs

# Create environment template
echo -e "\nCreating environment template..."
cat > .env.template << 'EOF'
# DeepSeek API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Discord Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GAME_CHANNEL_ID=your_discord_channel_id_here

# System Configuration
LOG_LEVEL=INFO
ACTIVE_SYSTEM=dcc
DATA_DIR=./campaigns/dying_earth
EOF

echo -e "\nCopying template to .env (edit with your actual values)..."
cp .env.template .env

# Create a sample adventure for testing
echo -e "\nCreating sample adventure structure..."
cat > campaigns/dying_earth/world_state/sample_adventure.json << 'EOF'
{
  "metadata": {
    "adventure_name": "sample_adventure",
    "created": "2024-01-01T00:00:00",
    "version": 1
  },
  "rooms": {
    "room1": "A dusty chamber with stone walls. Torches flicker in sconces, casting long shadows. In the center of the room stands a stone pedestal with a glowing crystal.",
    "room2": "A narrow corridor stretches into darkness. The air is cold and damp. Faint scratching sounds echo from further down the passage."
  },
  "read_aloud": {
    "room1_enter": "As you push open the heavy oak door, dust motes dance in the beam of light from your torch. The chamber before you is silent save for the crackle of flames.",
    "room2_enter": "The corridor narrows as you proceed, the ceiling dropping lower until you must crouch. The scratching grows louder."
  },
  "monsters": {
    "Giant Rat": {
      "hp": 7,
      "ac": 12,
      "stats_text": "HP: 7, AC: 12, Bite: +4 to hit, 1d4+2 piercing damage"
    }
  },
  "traps": {
    "trap1": {
      "description": "A pressure plate in the floor triggers a dart trap from the wall.",
      "dc": 15,
      "damage": "1d4 piercing"
    }
  },
  "current_location": {
    "id": "room1",
    "description": "Starting chamber"
  }
}
EOF

# Create a sample character
echo -e "\nCreating sample character..."
cat > campaigns/dying_earth/characters/sample_character.json << 'EOF'
{
  "name": "Sample Character",
  "class": "Fighter",
  "level": 1,
  "hp": {
    "current": 12,
    "max": 12
  },
  "abilities": {
    "str": 16,
    "dex": 12,
    "con": 14,
    "int": 10,
    "wis": 8,
    "cha": 13
  },
  "inventory": [
    {
      "name": "Longsword",
      "quantity": 1
    },
    {
      "name": "Shield",
      "quantity": 1
    },
    {
      "name": "Healing Potion",
      "quantity": 2
    }
  ],
  "conditions": [],
  "_metadata": {
    "created": "2024-01-01T00:00:00",
    "version": 1
  }
}
EOF

# Make scripts executable
echo -e "\nMaking scripts executable..."
chmod +x main.py
find gm_core systems tests -name "*.py" -exec chmod +x {} \;

# Create a quick test script
echo -e "\nCreating test script..."
cat > tests/test_system.py << 'EOF'
#!/usr/bin/env python3
"""
Quick test of system components.
"""

import sys
sys.path.insert(0, '.')

from gm_core.dice import DiceRoller

print("Testing Dice Roller...")
roller = DiceRoller()

test_rolls = ["1d20", "2d6+3", "4d10", "1d100"]
for notation in test_rolls:
    result = roller.roll(notation)
    print(f"{notation}: {result['details']}")

print("\nTesting ability check...")
check = roller.roll_ability_check("Perception", 5, advantage=True)
print(check["details"])

print("\n✅ Basic components working!")
print("\nNext steps:")
print("1. Edit .env with your API keys")
print("2. Add adventure PDFs to campaigns/dying_earth/adventures/")
print("3. Run: python main.py --import <pdf_path> <adventure_name>")
print("4. Run: python main.py <adventure_name>")
EOF

chmod +x tests/test_system.py

echo -e "\n========================================="
echo "Setup complete!"
echo "========================================="
echo -e "\nNext steps:"
echo "1. Edit .env with your actual API keys and Discord tokens"
echo "2. Run: ./test_system.py (to verify installation)"
echo "3. Add adventure PDFs to campaigns/dying_earth/adventures/"
echo "4. Import an adventure: python main.py --import <pdf> <name>"
echo "5. Run the system: python main.py <adventure_name>"
echo -e "\nFor Discord bot setup:"
echo "- Create a bot at https://discord.com/developers/applications"
echo "- Invite bot to your server with appropriate permissions"
echo "- Get channel ID (enable Developer Mode in Discord settings)"
echo -e "\nFor DeepSeek API:"
echo "- Get API key from https://platform.deepseek.com/api_keys"
echo -e "\nDocumentation in README.md"
echo "========================================="
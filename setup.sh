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

# Create necessary directories
echo -e "\nCreating directory structure..."
mkdir -p data/{adventures,world_state,characters}
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
DATA_DIR=./data
EOF

echo -e "\nCopying template to .env (edit with your actual values)..."
cp .env.template .env



# Make scripts executable
echo -e "\nMaking scripts executable..."
chmod +x main.py
find agents/ -name "*.py" -exec chmod +x {} \;

# Create a quick test script
echo -e "\nCreating test script..."
cat > test_system.py << 'EOF'
#!/usr/bin/env python3
"""
Quick test of system components.
"""

import sys
sys.path.insert(0, '.')

from agents.dice_roller import DiceRoller

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
print("2. Add adventure PDFs to data/adventures/")
print("3. Run: python main.py --import <pdf_path> <adventure_name>")
print("4. Run: python main.py <adventure_name>")
EOF

chmod +x test_system.py

echo -e "\n========================================="
echo "Setup complete!"
echo "========================================="
echo -e "\nNext steps:"
echo "1. Edit .env with your actual API keys and Discord tokens"
echo "2. Run: ./test_system.py (to verify installation)"
echo "3. Add adventure PDFs to data/adventures/"
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
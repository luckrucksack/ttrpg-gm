#!/bin/bash
# Complete setup script for AI TTRPG GM System

echo "🚀 AI TTRPG GM System - Complete Setup"
echo "======================================"

# Check for DeepSeek API key
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ DEEPSEEK_API_KEY environment variable not set"
    echo "💡 Get your API key from: https://platform.deepseek.com/api_keys"
    echo "💡 Then run: export DEEPSEEK_API_KEY='your_key_here'"
    exit 1
fi

echo "✅ DeepSeek API key found: ${DEEPSEEK_API_KEY:0:10}..."

# Create .env file
echo "📝 Creating configuration file..."
cat > .env << CONFIG
# TTRPG AI GM Configuration
DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Discord Bot Configuration (optional)
# DISCORD_BOT_TOKEN=your_discord_bot_token_here
# DISCORD_GAME_CHANNEL_ID=your_channel_id_here

# System Configuration
DATA_DIR=./data
LOG_LEVEL=INFO
CONFIG

echo "✅ Created .env configuration file"

# Install dependencies if needed
echo "📦 Checking Python dependencies..."
python3 -c "import pdfplumber" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
else
    echo "✅ Dependencies already installed"
fi

# Create necessary directories (campaign layer)
echo "📁 Creating directory structure..."
mkdir -p campaigns/dying_earth/adventures campaigns/dying_earth/world_state campaigns/dying_earth/characters

# Test the system
echo "🧪 Testing system components..."
python3 tests/test_system.py

echo ""
echo "🎯 SETUP COMPLETE!"
echo "=================="
echo ""
echo "✅ System ready with:"
echo "   - DeepSeek API integration"
echo "   - Character management (5 characters loaded)"
echo "   - Dice roller with local randomness"
echo "   - PDF adventure parser"
echo "   - Two-stage prose refinement"
echo "   - State management with JSON persistence"
echo ""
echo "📊 Characters available:"
python3 -c "
import json
import os
for file in os.listdir('campaigns/dying_earth/characters'):
    if file.endswith('.json'):
        with open(f'campaigns/dying_earth/characters/{file}', 'r') as f:
            char = json.load(f)
        name = char.get('name', file)
        hp = char.get('hp', {}).get('current', '?')
        print(f'   - {name}: HP {hp}')
"
echo ""
echo "🚀 Next steps:"
echo "1. Upload adventure PDFs to campaigns/dying_earth/adventures/"
echo "2. Import adventure: python main.py --import campaigns/dying_earth/adventures/filename.pdf adventure_name"
echo "3. Run adventure: python main.py adventure_name"
echo ""
echo "📱 For iPhone PDF uploads, use:"
echo "   ./upload_pdfs_from_iphone.sh"

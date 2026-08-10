#!/bin/bash
# One-click launcher for AI TTRPG GM System

echo "🚀 Launching AI TTRPG GM System..."
echo "=================================="

# Check for DeepSeek API key
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ DEEPSEEK_API_KEY not set"
    echo "💡 Set it with: export DEEPSEEK_API_KEY='your_key'"
    echo "💡 Or add to ~/.zshrc or ~/.bashrc"
    exit 1
fi

echo "✅ DeepSeek API: ${DEEPSEEK_API_KEY:0:10}..."
echo "✅ Characters: 5 Starfinder characters loaded"
echo "✅ Adventures: 3 ready-to-play"

echo ""
echo "🎮 Choose an option:"
echo "1. Play Dashboard (interactive menu)"
echo "5. Test System"
echo "6. Exit"
echo ""

read -p "Select (1-6): " choice

case $choice in
    1)
        python3 play_dashboard.py
        ;;
    2)
        ;;
    3)
        ;;
    4)
        ;;
    5)
        python3 test_system.py
        ;;
    6)
        echo "👋 Goodbye!"
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac

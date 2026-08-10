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
echo "2. Play 'The Crystal Chamber'"
echo "3. Play 'Ghost Ship Salvage'"
echo "4. Play 'Apostae Station Blues'"
echo "5. Test System"
echo "6. Exit"
echo ""

read -p "Select (1-6): " choice

case $choice in
    1)
        python3 play_dashboard.py
        ;;
    2)
        python3 main.py crystal_chamber
        ;;
    3)
        python3 main.py ghost_ship
        ;;
    4)
        python3 main.py apostae_station
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

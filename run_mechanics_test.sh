#!/bin/bash

# DCC Mechanics Test Adventure Runner
# Created: March 22, 2026
# Purpose: Run the comprehensive DCC mechanics test adventure

echo "================================================"
echo "DCC MECHANICS TEST ADVENTURE"
echo "================================================"
echo "Adventure: The Sunken Observatory of Zothique"
echo "System: Dungeon Crawl Classics"
echo "Campaign: Dying Earth"
echo "Duration: 30-45 minutes"
echo "Characters: 4 pre-generated Dying Earth heroes"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "dcc_judge.py" ]; then
    echo "Error: dcc_judge.py not found in current directory"
    echo "Please run from: /Users/chriscoon/ttrpg_gm/"
    exit 1
fi

# Check adventure file
ADVENTURE_FILE="data/adventures/dcc_mechanics_test_adventure.md"
if [ ! -f "$ADVENTURE_FILE" ]; then
    echo "Error: Adventure file not found: $ADVENTURE_FILE"
    exit 1
fi

echo "✅ Adventure file found: $(basename "$ADVENTURE_FILE")"
echo ""

# Character files
CHARACTERS=(
    "data/characters/dying_earth_noble.json"
    "data/characters/dying_earth_thief.json" 
    "data/characters/dying_earth_wizard.json"
    "data/characters/dying_earth_cleric.json"
)

# Verify all characters exist
echo "Checking character files..."
for char in "${CHARACTERS[@]}"; do
    if [ -f "$char" ]; then
        CHAR_NAME=$(python3 -c "import json; print(json.load(open('$char'))['name'])" 2>/dev/null || echo "Unknown")
        echo "  ✅ $(basename "$char"): $CHAR_NAME"
    else
        echo "  ❌ Missing: $(basename "$char")"
        exit 1
    fi
done

echo ""
echo "================================================"
echo "ADVENTURE SUMMARY"
echo "================================================"
echo ""
echo "This adventure tests ALL DCC mechanics:"
echo "  • Spellburn (Wizard burning STR/AGI/STA)"
echo "  • Corruption (Failed spell consequences)"
echo "  • Luck System (Burnable luck points)"
echo "  • Mercurial Magic (d8 spell effects)"
echo "  • Mighty Deeds (Warrior d3 deed die)"
echo "  • Thief Skills (1-in-6 to 3-in-6)"
echo "  • Turn Undead (Cleric vs spectral guardian)"
echo "  • Crit/Fumble Tables (Class-specific)"
echo ""
echo "Literary Style: Dying Earth (Jack Vance inspired)"
echo "  • Archaic, poetic language"
echo "  • Melancholy beauty of decay"
echo "  • Ironic, elaborate descriptions"
echo ""
echo "Testing Focus: System mechanics + literary quality"
echo ""

# Ask for confirmation
read -p "Start the DCC Mechanics Test Adventure? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Adventure cancelled."
    exit 0
fi

echo ""
echo "================================================"
echo "STARTING ADVENTURE..."
echo "================================================"
echo ""

# Build character list for command
CHAR_LIST=""
for char in "${CHARACTERS[@]}"; do
    CHAR_LIST="$CHAR_LIST,$char"
done
CHAR_LIST=${CHAR_LIST:1}  # Remove leading comma

# Run the adventure
echo "Command: python3 dcc_judge.py --adventure \"$ADVENTURE_FILE\" --characters \"$CHAR_LIST\""
echo ""
echo "------------------------------------------------"
echo ""

python3 dcc_judge.py --adventure "$ADVENTURE_FILE" --characters "$CHAR_LIST"

ADVENTURE_RESULT=$?

echo ""
echo "================================================"
echo "ADVENTURE COMPLETE"
echo "================================================"
echo ""

if [ $ADVENTURE_RESULT -eq 0 ]; then
    echo "✅ Adventure completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Review the test results in the adventure output"
    echo "2. Check if all mechanics worked correctly"
    echo "3. Note any issues in DCC_QUICK_START_GUIDE.md"
    echo "4. Consider the literary quality and pacing"
else
    echo "⚠ Adventure encountered issues (exit code: $ADVENTURE_RESULT)"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check error messages above"
    echo "2. Verify all character files are valid JSON"
    echo "3. Check DCC Judge system status"
    echo "4. Review adventure file format"
fi

echo ""
echo "Test results template available in: $ADVENTURE_FILE"
echo "Full testing guide: DCC_QUICK_START_GUIDE.md"
echo "================================================"
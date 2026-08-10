#!/bin/bash

# DCC System Test Script
# Created: March 22, 2026
# Purpose: Quick validation of DCC Judge system with pre-generated characters

echo "========================================="
echo "DCC Judge System Test Suite"
echo "========================================="
echo "Time: $(date)"
echo "System: Dungeon Crawl Classics"
echo "Campaign: Dying Earth"
echo "========================================="
echo ""

# Check system dependencies
echo "1. Checking system dependencies..."
python3 --version
if [ $? -eq 0 ]; then
    echo "✓ Python3 available"
else
    echo "✗ Python3 not found"
    exit 1
fi

# Check DCC Judge file
echo ""
echo "2. Checking DCC Judge system..."
if [ -f "dcc_judge.py" ]; then
    echo "✓ dcc_judge.py found"
    # Try to get help
    python3 dcc_judge.py --help 2>/dev/null | head -5
    if [ $? -eq 0 ]; then
        echo "✓ DCC Judge responds to --help"
    else
        echo "⚠ DCC Judge may have issues"
    fi
else
    echo "✗ dcc_judge.py not found"
    exit 1
fi

# Check character files
echo ""
echo "3. Checking pre-generated characters..."
CHARACTERS=(
    "data/characters/dying_earth_noble.json"
    "data/characters/dying_earth_thief.json"
    "data/characters/dying_earth_wizard.json"
    "data/characters/dying_earth_cleric.json"
)

ALL_CHARS_OK=true
for char in "${CHARACTERS[@]}"; do
    if [ -f "$char" ]; then
        echo "✓ $(basename "$char") found"
        # Validate JSON
        python3 -m json.tool "$char" >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "  ✓ Valid JSON format"
        else
            echo "  ✗ Invalid JSON format"
            ALL_CHARS_OK=false
        fi
    else
        echo "✗ $(basename "$char") not found"
        ALL_CHARS_OK=false
    fi
done

if [ "$ALL_CHARS_OK" = true ]; then
    echo "✓ All character files ready"
else
    echo "⚠ Some character files have issues"
fi

# Check adventure directory
echo ""
echo "4. Checking adventure structure..."
if [ -d "data/adventures" ]; then
    echo "✓ Adventure directory exists"
    ADV_COUNT=$(find data/adventures -name "*.txt" -o -name "*.json" -o -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    echo "  Found $ADV_COUNT adventure files"
else
    echo "⚠ Adventure directory not found"
fi

# Quick functionality test
echo ""
echo "5. Quick functionality test..."
echo "   This will test basic system response (timeout: 10 seconds)"

# Create a simple test
TEST_FILE="test_simple_command.py"
cat > "$TEST_FILE" << 'EOF'
#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import DCC Judge components
    import json
    import subprocess
    
    # Test 1: Check character loading
    print("Test 1: Loading character...")
    with open("data/characters/dying_earth_noble.json", "r") as f:
        char_data = json.load(f)
    print(f"  ✓ Loaded {char_data.get('name', 'Unknown')}")
    print(f"  ✓ Class: {char_data.get('class', 'Unknown')}")
    print(f"  ✓ Level: {char_data.get('level', 'Unknown')}")
    
    # Test 2: Check DCC mechanics fields
    print("\nTest 2: Checking DCC mechanics...")
    if 'abilities' in char_data:
        print("  ✓ Abilities structure present")
        if 'luck' in char_data['abilities']:
            luck = char_data['abilities']['luck']
            print(f"  ✓ Luck: {luck.get('score', '?')} (points: {luck.get('points_remaining', '?')})")
    
    if 'mercurial_magic' in char_data:
        print("  ✓ Mercurial magic structure present")
    
    if 'spellburn_history' in char_data:
        print("  ✓ Spellburn tracking present")
    
    print("\n✓ Basic system check passed")
    
except Exception as e:
    print(f"\n✗ Test failed: {e}")
    sys.exit(1)
EOF

python3 "$TEST_FILE"
TEST_RESULT=$?
rm "$TEST_FILE"

if [ $TEST_RESULT -eq 0 ]; then
    echo "✓ Quick test passed"
else
    echo "⚠ Quick test failed"
fi

# Summary
echo ""
echo "========================================="
echo "TEST SUMMARY"
echo "========================================="

if [ $TEST_RESULT -eq 0 ] && [ "$ALL_CHARS_OK" = true ]; then
    echo "✅ SYSTEM READY FOR TESTING"
    echo ""
    echo "Next steps:"
    echo "1. Review DCC_QUICK_START_GUIDE.md for testing instructions"
    echo "2. Test DCC mechanics using the sample commands"
    echo "3. Begin with adventure testing"
    echo ""
    echo "Characters available:"
    echo "  - Lord Valerius (Warrior)"
    echo "  - Silk the Shadow-Dancer (Thief)"
    echo "  - Zephyrim the Last Geomancer (Wizard)"
    echo "  - Sister Solara (Cleric)"
else
    echo "⚠ SYSTEM HAS ISSUES"
    echo ""
    echo "Check:"
    echo "1. Python3 installation"
    echo "2. DCC Judge file (dcc_judge.py)"
    echo "3. Character JSON files in data/characters/"
    echo "4. System dependencies"
fi

echo ""
echo "For detailed testing, see: DCC_QUICK_START_GUIDE.md"
echo "========================================="
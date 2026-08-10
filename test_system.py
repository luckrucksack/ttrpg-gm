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

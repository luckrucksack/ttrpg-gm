#!/usr/bin/env python3
"""
Test script for DCC Dice Roller
Demonstrates all DCC dice types and mechanics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from systems.dcc.dice import DCCDiceRoller, roll_d20, roll_d6, roll_percentage, roll_spell_check, roll_crit, roll_fumble

def test_all_dice_types():
    """Test all DCC dice types"""
    print("=== TESTING ALL DCC DICE TYPES ===")
    roller = DCCDiceRoller()
    
    dice_types = [
        'd3', 'd4', 'd5', 'd6', 'd7', 'd8',
        'd10', 'd12', 'd14', 'd16', 'd20', 'd24', 'd30', 'd%'
    ]
    
    for dice_type in dice_types:
        if dice_type == 'd%':
            result, description = roller.roll_percentage()
            print(f"  {dice_type}: {result}% - {description}")
        else:
            result = roller.roll(dice_type)
            print(f"  {dice_type}: {result}")

def test_dice_chain():
    """Test DCC dice chain stepping"""
    print("\n=== TESTING DICE CHAIN ===")
    roller = DCCDiceRoller()
    
    current = 'd6'
    print(f"Starting at: {current}")
    
    # Step up 3 times
    for i in range(3):
        current = roller.roll_dice_chain(current, 'up')
        roll = roller.roll(current)
        print(f"  Step up {i+1}: {current} → {roll}")
    
    # Step down 2 times
    for i in range(2):
        current = roller.roll_dice_chain(current, 'down')
        roll = roller.roll(current)
        print(f"  Step down {i+1}: {current} → {roll}")

def test_spell_checks():
    """Test DCC spell checks"""
    print("\n=== TESTING SPELL CHECKS ===")
    
    for spell_level in [1, 2, 3]:
        result = roll_spell_check(spell_level)
        print(f"\nSpell Level {spell_level}:")
        print(f"  Base Roll: {result['base_roll']}")
        print(f"  Target: {result['target']}")
        print(f"  Success: {result['success']}")
        if result['spellburn_needed']:
            print(f"  Spellburn Needed: {result['spellburn_amount']} points")
        if result['mercurial_effect']:
            print(f"  Mercurial Effect: {result['mercurial_effect']}")

def test_crit_fumble():
    """Test critical hits and fumbles"""
    print("\n=== TESTING CRITICALS & FUMBLES ===")
    
    # Test crit for different weapon types
    weapon_types = ['normal', 'warrior', 'dwarf', 'elf', 'halfling', 'thief']
    attack_rolls = [15, 24, 30]  # Normal, severe, massive
    
    for attack_roll in attack_rolls:
        for weapon_type in weapon_types[:2]:  # Just test first two for brevity
            result = roll_crit(attack_roll, weapon_type)
            print(f"\nAttack {attack_roll} with {weapon_type}:")
            print(f"  Crit Roll: {result['crit_roll']} on {result['crit_die']}")
            print(f"  Extra Dice: {result['extra_dice']}")
            print(f"  Damage: {result['damage_rolls']} = {result['total_damage']}")
            print(f"  Severity: {result['severity']}")
    
    # Test fumble
    print("\n=== TESTING FUMBLE ===")
    fumble_result = roll_fumble()
    print(f"Fumble Roll: {fumble_result['fumble_roll']}")
    print(f"Severity: {fumble_result['severity']}")
    print(f"Effect Roll: {fumble_result['effect_roll']} on {fumble_result['effect_die']}")
    print(f"Recovery Roll: {fumble_result['recovery_roll']}")

def test_luck_checks():
    """Test DCC luck checks"""
    print("\n=== TESTING LUCK CHECKS ===")
    
    for luck_score in [5, 10, 15, 18]:
        roller = DCCDiceRoller()
        result = roller.roll_luck_check(luck_score)
        print(f"\nLuck Score {luck_score}:")
        print(f"  Luck Roll: {result['luck_roll']}")
        print(f"  Success: {result['success']}")
        if result['luck_burned']:
            print(f"  Luck Burned! New Score: {result['new_luck_score']}")

def test_batch_rolls():
    """Test batch rolling"""
    print("\n=== TESTING BATCH ROLLS ===")
    roller = DCCDiceRoller()
    
    # Roll multiple dice at once
    batch = [
        ('d20', 1, 0),      # Attack roll
        ('d6', 2, 3),       # Damage: 2d6+3
        ('d%', 1, 0),       # Percentage
        ('d30', 1, 0),      # Mercurial magic
    ]
    
    results = roller.batch_roll(batch)
    
    print("Batch Roll Results:")
    for i, (dice_type, count, modifier) in enumerate(batch):
        result = results[i]
        if dice_type == 'd%':
            # Percentage roll returns a tuple (roll, desc); tolerate int too
            if isinstance(result, tuple):
                roll, desc = result
                print(f"  {count}{dice_type}: {roll}% - {desc}")
            else:
                print(f"  {count}{dice_type}: {result}%")
        else:
            print(f"  {count}{dice_type}: {result}")

def test_convenience_functions():
    """Test convenience functions"""
    print("\n=== TESTING CONVENIENCE FUNCTIONS ===")
    
    # d20 roll
    d20_result = roll_d20(2)  # d20+2
    print(f"d20+2: {d20_result}")
    
    # 3d6 roll
    d6_result = roll_d6(3, 1)  # 3d6+1
    print(f"3d6+1: {d6_result}")
    
    # Percentage roll
    percent_result, desc = roll_percentage()
    print(f"Percentage: {percent_result}% - {desc}")

def main():
    """Run all tests"""
    print("DCC DICE ROLLER TEST SUITE")
    print("=" * 50)
    
    test_all_dice_types()
    test_dice_chain()
    test_spell_checks()
    test_crit_fumble()
    test_luck_checks()
    test_batch_rolls()
    test_convenience_functions()
    
    print("\n" + "=" * 50)
    print("✅ DCC Dice Roller Test Complete")
    print("\nDice Types Available:")
    roller = DCCDiceRoller()
    for dice_type in roller.DICE_TYPES:
        print(f"  - {dice_type}")
    
    print("\nUsage Examples:")
    print("  roller.roll('d20')                    # Single d20")
    print("  roller.roll('d6', 3, 2)              # 3d6+2")
    print("  roller.roll_percentage()             # d% with description")
    print("  roller.roll_spell_check(2)           # Level 2 spell check")
    print("  roller.roll_crit(24, 'warrior')      # Warrior crit on 24")
    print("  roller.roll_fumble()                 # Random fumble")

if __name__ == "__main__":
    main()
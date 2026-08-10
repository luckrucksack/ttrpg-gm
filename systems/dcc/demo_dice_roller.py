#!/usr/bin/env python3
"""
Demonstration of the DCC Dice Roller
Shows practical usage for DCC gameplay
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from systems.dcc.dice import DCCDiceRoller

def demonstrate_basic_rolls():
    """Show basic dice rolling"""
    print("=== BASIC DICE ROLLS ===")
    roller = DCCDiceRoller()
    
    # Common rolls
    print("\nCommon Rolls:")
    print(f"  Initiative: d20 → {roller.roll('d20')}")
    print(f"  Attack: d20+3 → {roller.roll('d20', modifier=3)}")
    print(f"  Damage: 2d6+1 → {roller.roll('d6', 2, 1)}")
    
    # DCC-specific dice
    print("\nDCC-Specific Dice:")
    print(f"  Mercurial Magic: d30 → {roller.roll('d30')}")
    print(f"  Warrior Crit: d24 → {roller.roll('d24')}")
    print(f"  Dwarf Crit: d16 → {roller.roll('d16')}")
    print(f"  Halfling Crit: d12 → {roller.roll('d12')}")
    
    # Percentage
    percent, desc = roller.roll_percentage()
    print(f"  Percentage: d% → {percent}% ({desc})")

def demonstrate_spellcasting():
    """Show spellcasting with dice roller"""
    print("\n=== SPELLCASTING DEMO ===")
    roller = DCCDiceRoller()
    
    print("\nLevel 1 Wizard casting Magic Missile:")
    result = roller.roll_spell_check(1)
    print(f"  Spell Check: d20 → {result['base_roll']}")
    print(f"  Target: {result['target']}")
    print(f"  Success: {result['success']}")
    
    if result['spellburn_needed']:
        print(f"  ❗ Spellburn Needed: {result['spellburn_amount']} points")
        print("  (Sacrifice STR/AGI/STA for bonus)")
    else:
        print(f"  ✅ Spell succeeds!")
        print(f"  Mercurial Effect: {result['mercurial_effect']}")
    
    print("\nLevel 3 Wizard casting Fireball:")
    result = roller.roll_spell_check(3)
    print(f"  Spell Check: d20 → {result['base_roll']}")
    print(f"  Target: {result['target']}")
    print(f"  Success: {result['success']}")
    
    if result['spellburn_needed']:
        print(f"  ❗ Spellburn Needed: {result['spellburn_amount']} points")
    else:
        print(f"  ✅ Spell succeeds!")
        print(f"  Mercurial Effect: {result['mercurial_effect']}")

def demonstrate_combat():
    """Show combat mechanics"""
    print("\n=== COMBAT DEMO ===")
    roller = DCCDiceRoller()
    
    print("\nWarrior attacking with longsword:")
    attack_roll = roller.roll('d20', modifier=5)
    print(f"  Attack Roll: d20+5 → {attack_roll}")
    
    if attack_roll >= 20:  # Critical hit
        print(f"  ✅ CRITICAL HIT!")
        crit_result = roller.roll_crit(attack_roll, 'warrior')
        print(f"  Crit Roll: {crit_result['crit_roll']} on {crit_result['crit_die']}")
        print(f"  Extra Damage Dice: {crit_result['extra_dice']}")
        print(f"  Damage Rolls: {crit_result['damage_rolls']}")
        print(f"  Total Damage: {crit_result['total_damage']}")
        print(f"  Severity: {crit_result['severity']}")
    elif attack_roll == 1:  # Fumble
        print(f"  ❌ FUMBLE!")
        fumble_result = roller.roll_fumble(attack_roll)
        print(f"  Fumble Severity: {fumble_result['severity']}")
        print(f"  Effect Roll: {fumble_result['effect_roll']} on {fumble_result['effect_die']}")
        print(f"  Recovery Roll: d4 → {fumble_result['recovery_roll']}")
    else:
        # Normal hit
        damage = roller.roll('d8', modifier=3)
        print(f"  Damage: d8+3 → {damage}")

def demonstrate_luck():
    """Show luck mechanics"""
    print("\n=== LUCK MECHANICS ===")
    roller = DCCDiceRoller()
    
    print("\nCharacter with Luck 12:")
    result = roller.roll_luck_check(12)
    print(f"  Luck Check: d20 → {result['luck_roll']}")
    print(f"  Target: ≤{result['luck_score']}")
    print(f"  Success: {result['success']}")
    
    if result['luck_burned']:
        print(f"  ❗ Luck Burned! New Luck: {result['new_luck_score']}")
    else:
        print(f"  ✅ Luck holds!")
    
    print("\nCharacter with Luck 18 (very lucky):")
    result = roller.roll_luck_check(18)
    print(f"  Luck Check: d20 → {result['luck_roll']}")
    print(f"  Target: ≤{result['luck_score']}")
    print(f"  Success: {result['success']}")
    
    if result['luck_burned']:
        print(f"  ❗ Luck Burned! New Luck: {result['new_luck_score']}")
    else:
        print(f"  ✅ Luck holds!")

def demonstrate_dice_chain():
    """Show dice chain mechanics"""
    print("\n=== DICE CHAIN DEMO ===")
    roller = DCCDiceRoller()
    
    print("Starting at d6 (typical starting spell check die):")
    current = 'd6'
    
    for i in range(5):
        roll = roller.roll(current)
        print(f"  Roll {i+1}: {current} → {roll}")
        
        # Step up for high-level caster
        current = roller.roll_dice_chain(current, 'up')
    
    print("\nNow stepping back down:")
    for i in range(3):
        current = roller.roll_dice_chain(current, 'down')
        roll = roller.roll(current)
        print(f"  Step down {i+1}: {current} → {roll}")

def demonstrate_batch_rolls():
    """Show batch rolling for efficiency"""
    print("\n=== BATCH ROLLING ===")
    roller = DCCDiceRoller()
    
    # Simulate a combat round (without d% for batch)
    batch = [
        ('d20', 1, 5),   # Attack roll
        ('d8', 1, 3),    # Damage roll
        ('d20', 1, 0),   # Saving throw
        ('d6', 2, 0),    # Healing
    ]
    
    results = roller.batch_roll(batch)
    
    print("Combat Round Batch Rolls:")
    actions = ["Attack", "Damage", "Save", "Healing"]
    
    for i, (action, (dice_type, count, modifier), result) in enumerate(zip(actions, batch, results)):
        print(f"  {action}: {count}{dice_type}{'+' + str(modifier) if modifier > 0 else ''} → {result}")
    
    # Show percentage separately
    print("\nPercentage Roll (separate):")
    percent, desc = roller.roll_percentage()
    print(f"  Random Chance: d% → {percent}% ({desc})")
    print("\n=== BATCH ROLLING ===")
    roller = DCCDiceRoller()
    
    # Simulate a combat round
    batch = [
        ('d20', 1, 5),   # Attack roll
        ('d8', 1, 3),    # Damage roll
        ('d20', 1, 0),   # Saving throw
        ('d6', 2, 0),    # Healing
        ('d%', 1, 0),    # Random chance
    ]
    
    results = roller.batch_roll(batch)
    
    print("Combat Round Batch Rolls:")
    actions = ["Attack", "Damage", "Save", "Healing", "Random"]
    
    for i, (action, (dice_type, count, modifier), result) in enumerate(zip(actions, batch, results)):
        if dice_type == 'd%':
            # Handle percentage roll specially
            try:
                roll, desc = result
                print(f"  {action}: {count}{dice_type} → {roll}% ({desc})")
            except (TypeError, ValueError):
                # Fallback if batch_roll doesn't return tuple for d%
                print(f"  {action}: {count}{dice_type} → {result}")
        else:
            print(f"  {action}: {count}{dice_type}{'+' + str(modifier) if modifier > 0 else ''} → {result}")

def main():
    """Run all demonstrations"""
    print("DCC DICE ROLLER DEMONSTRATION")
    print("=" * 60)
    
    demonstrate_basic_rolls()
    demonstrate_spellcasting()
    demonstrate_combat()
    demonstrate_luck()
    demonstrate_dice_chain()
    demonstrate_batch_rolls()
    
    print("\n" + "=" * 60)
    print("🎲 DICE ROLLER READY FOR DCC GAMEPLAY")
    print("\nThe dice roller provides:")
    print("  ✅ True random generation (cryptographically secure)")
    print("  ✅ All DCC dice types (d3-d30, d%)")
    print("  ✅ Specialized DCC mechanics (spellburn, crits, fumbles)")
    print("  ✅ Dice chain stepping (mercurial magic)")
    print("  ✅ Batch rolling for efficiency")
    print("  ✅ Integration with DCC Judge system")
    
    print("\nUsage in DCC Judge:")
    print("  !roll d20           # Basic roll")
    print("  !roll d6 3 2        # 3d6+2")
    print("  !percent            # d% with description")
    print("  !spell_check 2      # Level 2 spell check")
    print("  !crit_roll 24 warrior # Warrior critical")
    print("  !fumble_roll        # Random fumble")
    print("  !luck_check 12      # Luck check")

if __name__ == "__main__":
    main()
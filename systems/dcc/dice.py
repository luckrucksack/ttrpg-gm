#!/usr/bin/env python3
"""
DCC Dice Roller - True Random Generator for Dungeon Crawl Classics
Provides all DCC dice types: d3, d4, d5, d6, d7, d8, d10, d12, d14, d16, d20, d24, d30, d%
"""

import random
import secrets
import time
from typing import List, Tuple, Union, Dict, Optional
import hashlib
import os

class DCCDiceRoller:
    """
    True random dice roller for Dungeon Crawl Classics.
    Uses cryptographically secure random number generation.
    """
    
    # DCC dice types
    DICE_TYPES = {
        'd3': 3, 'd4': 4, 'd5': 5, 'd6': 6, 'd7': 7, 'd8': 8,
        'd10': 10, 'd12': 12, 'd14': 14, 'd16': 16, 'd20': 20,
        'd24': 24, 'd30': 30, 'd%': 100
    }
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the dice roller.
        
        Args:
            seed: Optional seed for reproducible results (for testing only).
                  If None, uses cryptographically secure random.
        """
        self.use_secure_random = seed is None
        if seed is not None:
            random.seed(seed)
        
        # Initialize entropy sources for secure random
        self.entropy_sources = []
        self._initialize_entropy()
    
    def _initialize_entropy(self):
        """Initialize entropy sources for cryptographically secure random."""
        if self.use_secure_random:
            # Collect entropy from multiple sources
            self.entropy_sources = [
                str(time.time_ns()),
                str(os.urandom(32)),
                str(os.getpid()),
                str(hashlib.sha256(str(time.perf_counter_ns()).encode()).hexdigest())
            ]
    
    def _get_secure_random(self) -> float:
        """
        Get cryptographically secure random float between 0 and 1.
        
        Returns:
            Secure random float
        """
        # Mix multiple entropy sources
        entropy_string = ''.join(self.entropy_sources)
        entropy_bytes = entropy_string.encode()
        
        # Update entropy sources for next call
        self.entropy_sources.append(str(time.perf_counter_ns()))
        self.entropy_sources.append(str(os.urandom(16)))
        
        # Generate secure random using SHA-256
        hash_digest = hashlib.sha256(entropy_bytes).digest()
        random_int = int.from_bytes(hash_digest[:8], 'big')
        
        # Convert to float between 0 and 1
        return random_int / (2**64 - 1)
    
    def roll(self, dice_type: str, count: int = 1, modifier: int = 0) -> Union[int, List[int]]:
        """
        Roll one or more dice of a specific type.
        
        Args:
            dice_type: Type of dice (e.g., 'd6', 'd20', 'd%')
            count: Number of dice to roll
            modifier: Modifier to add to total
        
        Returns:
            Single roll result or list of individual rolls
        """
        if dice_type not in self.DICE_TYPES:
            raise ValueError(f"Invalid dice type: {dice_type}. Valid types: {list(self.DICE_TYPES.keys())}")
        
        sides = self.DICE_TYPES[dice_type]
        
        if count == 1:
            result = self._roll_single(sides)
            return result + modifier
        else:
            results = [self._roll_single(sides) for _ in range(count)]
            return [r + modifier for r in results]
    
    def _roll_single(self, sides: int) -> int:
        """
        Roll a single die with the given number of sides.
        
        Args:
            sides: Number of sides on the die
        
        Returns:
            Random integer between 1 and sides (inclusive)
        """
        if self.use_secure_random:
            # Use cryptographically secure random
            random_float = self._get_secure_random()
            result = int(random_float * sides) + 1
            # Ensure result is within bounds
            return max(1, min(sides, result))
        else:
            # Use seeded random for testing
            return random.randint(1, sides)
    
    def roll_dice_chain(self, current_die: str, direction: str = 'up') -> str:
        """
        Roll on the DCC dice chain (step up or down).
        
        Args:
            current_die: Current die type (e.g., 'd6')
            direction: 'up' to step up, 'down' to step down
        
        Returns:
            New die type after stepping
        """
        dice_chain = ['d3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd10', 'd12', 'd14', 'd16', 'd20', 'd24', 'd30']
        
        if current_die not in dice_chain:
            raise ValueError(f"Invalid die for dice chain: {current_die}")
        
        current_index = dice_chain.index(current_die)
        
        if direction == 'up':
            new_index = min(current_index + 1, len(dice_chain) - 1)
        elif direction == 'down':
            new_index = max(current_index - 1, 0)
        else:
            raise ValueError("Direction must be 'up' or 'down'")
        
        return dice_chain[new_index]
    
    def roll_table(self, table: Dict[int, str], dice_type: str = 'd20') -> str:
        """
        Roll on a table using the specified dice type.
        
        Args:
            table: Dictionary mapping roll results to outcomes
            dice_type: Type of dice to use for the roll
        
        Returns:
            Table outcome
        """
        roll_result = self.roll(dice_type)
        
        # Find the closest key (for tables with gaps)
        if roll_result in table:
            return table[roll_result]
        else:
            # Find the nearest key
            keys = list(table.keys())
            closest_key = min(keys, key=lambda x: abs(x - roll_result))
            return table[closest_key]
    
    def roll_percentage(self) -> Tuple[int, str]:
        """
        Roll a percentage die (d%).
        
        Returns:
            Tuple of (roll_result, description)
        """
        result = self.roll('d%')
        
        # Add descriptive text based on result
        if result == 1:
            description = "Critical Success (Natural 1%)"
        elif result == 100:
            description = "Critical Failure (Natural 100%)"
        elif result <= 5:
            description = "Exceptional Success"
        elif result >= 95:
            description = "Exceptional Failure"
        elif result <= 25:
            description = "Good Success"
        elif result >= 75:
            description = "Poor Failure"
        else:
            description = "Average Result"
        
        return result, description
    
    def roll_spell_check(self, spell_level: int, caster_level: int = 1) -> Dict[str, Union[int, str, bool]]:
        """
        Roll a DCC spell check with potential spellburn.
        
        Args:
            spell_level: Level of the spell being cast
            caster_level: Level of the caster
        
        Returns:
            Dictionary with spell check results
        """
        # Base roll
        base_roll = self.roll('d20')
        
        # Determine if spellburn is needed/possible
        target = 10 + spell_level * 2
        success = base_roll >= target
        
        result = {
            'base_roll': base_roll,
            'spell_level': spell_level,
            'target': target,
            'success': success,
            'spellburn_needed': not success and (target - base_roll) > 0,
            'spellburn_amount': max(0, target - base_roll) if not success else 0,
            'mercurial_effect': self.roll('d30') if success else None
        }
        
        return result
    
    def roll_crit(self, attack_roll: int, weapon_type: str = 'normal') -> Dict[str, Union[int, str, List[int]]]:
        """
        Roll a DCC critical hit.
        
        Args:
            attack_roll: The attack roll that triggered the crit
            weapon_type: Type of weapon ('normal', 'warrior', 'dwarf', 'elf', 'halfling', 'thief')
        
        Returns:
            Dictionary with crit results
        """
        # Determine crit table based on weapon type
        crit_tables = {
            'normal': 'd14',
            'warrior': 'd24',
            'dwarf': 'd16',
            'elf': 'd20',
            'halfling': 'd12',
            'thief': 'd10'
        }
        
        crit_die = crit_tables.get(weapon_type, 'd14')
        crit_roll = self.roll(crit_die)
        
        # Roll additional damage dice
        if attack_roll >= 30:
            extra_dice = 3
        elif attack_roll >= 24:
            extra_dice = 2
        else:
            extra_dice = 1
        
        # Roll damage (using weapon-appropriate die)
        damage_die = 'd6'  # Default, would vary by weapon
        damage_rolls = [self.roll(damage_die) for _ in range(extra_dice)]
        
        result = {
            'attack_roll': attack_roll,
            'crit_roll': crit_roll,
            'crit_die': crit_die,
            'extra_dice': extra_dice,
            'damage_rolls': damage_rolls,
            'total_damage': sum(damage_rolls),
            'severity': 'MASSIVE' if attack_roll >= 30 else 'SEVERE' if attack_roll >= 24 else 'NORMAL'
        }
        
        return result
    
    def roll_fumble(self, fumble_roll: int = None) -> Dict[str, Union[int, str, List[int]]]:
        """
        Roll a DCC fumble.
        
        Args:
            fumble_roll: Optional fumble roll (if None, rolls d20)
        
        Returns:
            Dictionary with fumble results
        """
        if fumble_roll is None:
            fumble_roll = self.roll('d20')
        
        # Determine fumble severity
        if fumble_roll == 1:
            severity = 'CATASTROPHIC'
            effect_die = 'd30'
        elif fumble_roll <= 5:
            severity = 'SEVERE'
            effect_die = 'd16'
        else:
            severity = 'NORMAL'
            effect_die = 'd8'
        
        effect_roll = self.roll(effect_die)
        
        result = {
            'fumble_roll': fumble_roll,
            'severity': severity,
            'effect_die': effect_die,
            'effect_roll': effect_roll,
            'recovery_roll': self.roll('d4')  # Rolls to recover from fumble
        }
        
        return result
    
    def roll_luck_check(self, luck_score: int) -> Dict[str, Union[int, str, bool]]:
        """
        Roll a DCC luck check.
        
        Args:
            luck_score: Character's current luck score
        
        Returns:
            Dictionary with luck check results
        """
        luck_roll = self.roll('d20')
        success = luck_roll <= luck_score
        
        result = {
            'luck_roll': luck_roll,
            'luck_score': luck_score,
            'success': success,
            'luck_burned': not success,
            'new_luck_score': max(0, luck_score - 1) if not success else luck_score
        }
        
        return result
    
    def batch_roll(self, rolls: List[Tuple[str, int, int]]) -> List[Union[int, List[int]]]:
        """
        Perform multiple rolls at once.
        
        Args:
            rolls: List of (dice_type, count, modifier) tuples
        
        Returns:
            List of roll results
        """
        results = []
        for dice_type, count, modifier in rolls:
            results.append(self.roll(dice_type, count, modifier))
        return results
    
    def get_statistics(self, dice_type: str, num_rolls: int = 1000) -> Dict[str, float]:
        """
        Generate statistics for a dice type (for analysis).
        
        Args:
            dice_type: Type of dice to analyze
            num_rolls: Number of rolls to perform
        
        Returns:
            Dictionary with statistical analysis
        """
        if dice_type not in self.DICE_TYPES:
            raise ValueError(f"Invalid dice type: {dice_type}")
        
        sides = self.DICE_TYPES[dice_type]
        rolls = [self.roll(dice_type) for _ in range(num_rolls)]
        
        return {
            'dice_type': dice_type,
            'sides': sides,
            'num_rolls': num_rolls,
            'mean': sum(rolls) / num_rolls,
            'min': min(rolls),
            'max': max(rolls),
            'std_dev': (sum((x - (sum(rolls) / num_rolls)) ** 2 for x in rolls) / num_rolls) ** 0.5,
            'distribution': {i: rolls.count(i) for i in range(1, sides + 1)}
        }


# Convenience functions for common rolls
def roll_d20(modifier: int = 0) -> int:
    """Roll a d20 with optional modifier."""
    roller = DCCDiceRoller()
    return roller.roll('d20', modifier=modifier)

def roll_d6(count: int = 1, modifier: int = 0) -> Union[int, List[int]]:
    """Roll one or more d6 dice."""
    roller = DCCDiceRoller()
    return roller.roll('d6', count=count, modifier=modifier)

def roll_percentage() -> Tuple[int, str]:
    """Roll a percentage die."""
    roller = DCCDiceRoller()
    return roller.roll_percentage()

def roll_dice_chain(current_die: str, direction: str = 'up') -> str:
    """Roll on the DCC dice chain."""
    roller = DCCDiceRoller()
    return roller.roll_dice_chain(current_die, direction)

def roll_spell_check(spell_level: int, caster_level: int = 1) -> Dict[str, Union[int, str, bool]]:
    """Roll a DCC spell check."""
    roller = DCCDiceRoller()
    return roller.roll_spell_check(spell_level, caster_level)

def roll_crit(attack_roll: int, weapon_type: str = 'normal') -> Dict[str, Union[int, str, List[int]]]:
    """Roll a DCC critical hit."""
    roller = DCCDiceRoller()
    return roller.roll_crit(attack_roll, weapon_type)

def roll_fumble(fumble_roll: int = None) -> Dict[str, Union[int, str, List[int]]]:
    """Roll a DCC fumble."""
    roller = DCCDiceRoller()
    return roller.roll_fumble(fumble_roll)


if __name__ == "__main__":
    # Test the dice roller
    print("=== DCC Dice Roller Test ===")
    roller = DCCDiceRoller()
    
    # Test all dice types
    print("\nTesting all DCC dice types:")
    for dice_type in roller.DICE_TYPES:
        result = roller.roll(dice_type)
        print(f"  {dice_type}: {result}")
    
    # Test dice chain
    print("\nTesting dice chain (starting at d6):")
    current = 'd6'
    print(f"  Start: {current}")
    for i in range(3):
        current = roller.roll_dice_chain(current, 'up')
        print(f"  Step up {i+1}: {current}")
    
    # Test percentage roll
    print("\nTesting percentage roll:")
    percent_result, description = roller.roll_percentage()
    print(f"  Roll: {percent_result}% - {description}")
    
    # Test spell check
    print("\nTesting spell check (Level 2 spell):")
    spell_result = roller.roll_spell_check(2)
    for key, value in spell_result.items():
        print(f"  {key}: {value}")
    
    # Test crit roll
    print("\nTesting critical hit (attack roll 27, warrior):")
    crit_result = roller.roll_crit(27, 'warrior')
    for key, value in crit_result.items():
        print(f"  {key}: {value}")
    
    # Test fumble roll
    print("\nTesting fumble:")
    fumble_result = roller.roll_fumble()
    for key, value in fumble_result.items():
        print(f"  {key}: {value}")
    
    print("\n=== Dice Roller Ready for DCC Gameplay ===")
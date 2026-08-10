#!/usr/bin/env python3
"""
Local dice rolling engine.
Never calls external bots for randomness.
"""

import random
import re
from typing import Dict, List, Tuple, Union

class DiceRoller:
    """Local dice roller for TTRPG games"""
    
    def __init__(self):
        self.roll_history = []
    
    def parse_dice_notation(self, notation: str) -> Tuple[List[Tuple[int, int]], int]:
        """
        Parse dice notation like "2d6+3" or "1d20"
        Returns: list of (num_dice, dice_size), modifier
        """
        # Remove whitespace
        notation = notation.replace(" ", "")
        
        # Pattern for dice notation: NdX[+-]modifier
        pattern = r'^(\d+)d(\d+)([+-]\d+)?$'
        match = re.match(pattern, notation)
        
        if not match:
            raise ValueError(f"Invalid dice notation: {notation}")
        
        num_dice = int(match.group(1))
        dice_size = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        return [(num_dice, dice_size)], modifier
    
    def roll_dice(self, num_dice: int, dice_size: int) -> List[int]:
        """Roll multiple dice of same size"""
        return [random.randint(1, dice_size) for _ in range(num_dice)]
    
    def roll(self, notation: str) -> Dict[str, Union[int, List[int], str]]:
        """
        Roll dice based on notation.
        Returns: {
            "total": int,
            "rolls": List[int],
            "modifier": int,
            "notation": str,
            "details": str
        }
        """
        try:
            dice_groups, modifier = self.parse_dice_notation(notation)
            
            all_rolls = []
            total = modifier
            details_parts = []
            
            for num_dice, dice_size in dice_groups:
                rolls = self.roll_dice(num_dice, dice_size)
                all_rolls.extend(rolls)
                group_total = sum(rolls)
                total += group_total
                
                details_parts.append(f"{num_dice}d{dice_size}: {rolls} = {group_total}")
            
            if modifier != 0:
                details_parts.append(f"modifier: {modifier:+d}")
            
            details = " + ".join(details_parts)
            if len(details_parts) > 1:
                details += f" = {total}"
            
            result = {
                "total": total,
                "rolls": all_rolls,
                "modifier": modifier,
                "notation": notation,
                "details": details
            }
            
            # Add to history
            self.roll_history.append(result)
            
            return result
            
        except ValueError as e:
            raise ValueError(f"Dice roll error: {e}")
    
    def roll_ability_check(self, ability: str, modifier: int, advantage: bool = False, 
                          disadvantage: bool = False) -> Dict[str, Union[int, List[int], str]]:
        """Roll an ability check with optional advantage/disadvantage"""
        if advantage and disadvantage:
            advantage = disadvantage = False
        
        if advantage or disadvantage:
            rolls = [random.randint(1, 20), random.randint(1, 20)]
            if advantage:
                roll = max(rolls)
                roll_type = "advantage"
            else:
                roll = min(rolls)
                roll_type = "disadvantage"
            
            total = roll + modifier
            details = f"{ability} check ({roll_type}): {rolls} -> {roll} + {modifier} = {total}"
            
            result = {
                "total": total,
                "rolls": rolls,
                "modifier": modifier,
                "notation": f"2d20{modifier:+d} ({roll_type})",
                "details": details,
                "ability": ability,
                "roll_type": roll_type
            }
        else:
            roll = random.randint(1, 20)
            total = roll + modifier
            details = f"{ability} check: {roll} + {modifier} = {total}"
            
            result = {
                "total": total,
                "rolls": [roll],
                "modifier": modifier,
                "notation": f"1d20{modifier:+d}",
                "details": details,
                "ability": ability,
                "roll_type": "normal"
            }
        
        self.roll_history.append(result)
        return result
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent roll history"""
        return self.roll_history[-limit:] if self.roll_history else []
    
    def clear_history(self):
        """Clear roll history"""
        self.roll_history.clear()

# Global instance
roller = DiceRoller()

if __name__ == "__main__":
    # Test the dice roller
    test_cases = ["1d20", "2d6+3", "1d8-1", "4d10+5"]
    
    print("Testing Dice Roller:")
    print("-" * 40)
    
    for notation in test_cases:
        try:
            result = roller.roll(notation)
            print(f"{notation}: {result['details']}")
        except ValueError as e:
            print(f"{notation}: ERROR - {e}")
    
    print("\nTesting ability checks:")
    print("-" * 40)
    
    # Test ability checks
    check = roller.roll_ability_check("Perception", 5)
    print(check["details"])
    
    check = roller.roll_ability_check("Stealth", 3, advantage=True)
    print(check["details"])
    
    check = roller.roll_ability_check("Athletics", 2, disadvantage=True)
    print(check["details"])
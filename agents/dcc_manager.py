#!/usr/bin/env python3
"""
DCC-specific state manager for Dungeon Crawl Classics mechanics.
Handles spellburn, corruption, mercurial magic, luck points, and dice chain.
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from enum import Enum
import sys
import os

# Add parent directory to path to import dice_roller
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dice_roller import DCCDiceRoller

class DCCDice(Enum):
    """DCC dice chain"""
    D3 = "d3"
    D4 = "d4"
    D5 = "d5"
    D6 = "d6"
    D7 = "d7"
    D8 = "d8"
    D10 = "d10"
    D12 = "d12"
    D14 = "d14"
    D16 = "d16"
    D20 = "d20"
    D24 = "d24"
    D30 = "d30"

class DCCManager:
    """Manages DCC-specific mechanics and state"""
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.dice_chain = list(DCCDice)
        self.dice_roller = DCCDiceRoller()  # True random dice roller
        
        # DCC-specific tables (simplified versions)
        self.crit_tables = self._load_crit_tables()
        self.fumble_tables = self._load_fumble_tables()
        self.corruption_tables = self._load_corruption_tables()
    
    def _load_crit_tables(self) -> Dict[str, List[str]]:
        """Load simplified crit tables by class"""
        return {
            "Warrior": [
                "1-2: Minor wound - target takes 1d3 extra damage",
                "3-4: Deep cut - target takes 1d4 extra damage and bleeds for 1d3 next round",
                "5-6: Serious wound - target takes 1d6 extra damage and is stunned 1 round",
                "7-8: Grievous wound - target takes 1d8 extra damage and is at -2 to attacks next round",
                "9-10: Devastating blow - target takes 1d10 extra damage and is knocked prone",
                "11-12: Maiming strike - target takes 1d12 extra damage and loses use of one limb",
                "13-14: Mortal wound - target takes 1d14 extra damage and is dying",
                "15-16: Decapitating blow - target takes 1d16 extra damage and dies instantly",
                "17-18: Obliterating strike - target takes 1d20 extra damage and is destroyed",
                "19-20: Legendary blow - target takes 1d24 extra damage and allies are demoralized"
            ],
            "Wizard": [
                "1-2: Minor magical feedback - target takes 1d3 extra damage",
                "3-4: Arcane surge - target takes 1d4 extra damage and is dazzled 1 round",
                "5-6: Elemental burst - target takes 1d6 extra damage and environment is affected",
                "7-8: Reality warp - target takes 1d8 extra damage and is confused 1d3 rounds",
                "9-10: Dimensional rift - target takes 1d10 extra damage and may be teleported",
                "11-12: Soul burn - target takes 1d12 extra damage and loses 1d3 Luck",
                "13-14: Time distortion - target takes 1d14 extra damage and ages 1d10 years",
                "15-16: Planar tear - target takes 1d16 extra damage and may be banished",
                "17-18: Cosmic annihilation - target takes 1d20 extra damage and area is devastated",
                "19-20: Divine retribution - target takes 1d24 extra damage and is marked by gods"
            ],
            "Cleric": [
                "1-2: Divine nudge - target takes 1d3 extra damage",
                "3-4: Holy smite - target takes 1d4 extra damage and is blinded 1 round",
                "5-6: Sacred flame - target takes 1d6 extra damage and burns for 1d3 next round",
                "7-8: Divine judgment - target takes 1d8 extra damage and is cursed -2 to saves",
                "9-10: Angelic wrath - target takes 1d10 extra damage and is frightened",
                "11-12: God's fist - target takes 1d12 extra damage and is knocked prone",
                "13-14: Celestial purge - target takes 1d14 extra damage and evil creatures flee",
                "15-16: Apocalyptic sign - target takes 1d16 extra damage and area is sanctified",
                "17-18: Divine intervention - target takes 1d20 extra damage and is smote",
                "19-20: Miracle - target takes 1d24 extra damage and is utterly destroyed"
            ],
            "Thief": [
                "1-2: Precise strike - target takes 1d3 extra damage",
                "3-4: Vital hit - target takes 1d4 extra damage and bleeds for 1d3 next round",
                "5-6: Crippling blow - target takes 1d6 extra damage and movement halved",
                "7-8: Disabling strike - target takes 1d8 extra damage and loses action next round",
                "9-10: Assassin's touch - target takes 1d10 extra damage and poisoned",
                "11-12: Death strike - target takes 1d12 extra damage and must save or die",
                "13-14: Shadow kill - target takes 1d14 extra damage and vanishes from sight",
                "15-16: Phantom blade - target takes 1d16 extra damage and cannot be healed",
                "17-18: Soul steal - target takes 1d20 extra damage and thief gains 1d3 Luck",
                "19-20: Legendary assassination - target takes 1d24 extra damage and dies silently"
            ]
        }
    
    def _load_fumble_tables(self) -> Dict[str, List[str]]:
        """Load simplified fumble tables by class"""
        return {
            "Warrior": [
                "1-2: Drop weapon - must spend action to retrieve",
                "3-4: Off balance - -2 to AC until next turn",
                "5-6: Stumble - fall prone",
                "7-8: Weapon break - non-magical weapon breaks",
                "9-10: Hit ally - accidentally attack nearest ally",
                "11-12: Self injury - take 1d3 damage",
                "13-14: Disarmed - weapon flies 1d20 feet away",
                "15-16: Equipment failure - armor or shield damaged",
                "17-18: Critical failure - weapon explodes, take 1d6 damage",
                "19-20: Legendary fumble - weapon cursed, -1 to attacks until cleansed"
            ],
            "Wizard": [
                "1-2: Spell fizzle - no effect, waste action",
                "3-4: Backfire - take 1d3 damage",
                "5-6: Wild magic - random spell effect occurs",
                "7-8: Arcane feedback - stunned 1 round",
                "9-10: Spell corruption - gain minor corruption",
                "11-12: Mana burn - lose 1d3 spellcasting ability",
                "13-14: Dimensional rift - random creature summoned",
                "15-16: Spell theft - forget spell for 1d3 days",
                "17-18: Reality collapse - area becomes wild magic zone",
                "19-20: Patron anger - patron displeased, -1d3 Luck"
            ],
            "Cleric": [
                "1-2: Divine disfavor - spell fails",
                "3-4: Holy backlash - take 1d3 damage",
                "5-6: Faith shaken - -1 to turning for 1d3 rounds",
                "7-8: Sacred desecration - holy symbol damaged",
                "9-10: God's wrath - struck by lightning for 1d6 damage",
                "11-12: Heretical act - lose 1d3 spellcasting ability",
                "13-14: Divine abandonment - cannot cast spells for 1d3 rounds",
                "15-16: Unholy mark - gain corruption from opposing deity",
                "17-18: Apostasy - deity withdraws favor, -1d3 Luck",
                "19-20: Blasphemy - excommunicated, lose all clerical powers"
            ],
            "Thief": [
                "1-2: Slippery fingers - drop item",
                "3-4: Exposed - lose stealth, enemies get free attack",
                "5-6: Trip - fall prone",
                "7-8: Equipment jam - tool or weapon unusable",
                "9-10: Backfire - trap or trick affects thief instead",
                "11-12: Caught red-handed - immediately arrested if guards present",
                "13-14: Reputation ruined - -2 to social interactions",
                "15-16: Guild mark - marked for death by thieves guild",
                "17-18: Cursed loot - stolen item is cursed",
                "19-20: Legendary blunder - become wanted with huge bounty"
            ]
        }
    
    def _load_corruption_tables(self) -> Dict[str, List[str]]:
        """Load corruption tables for spell failures"""
        return {
            "minor": [
                "Eyes glow with unnatural light",
                "Skin takes on pallid, corpse-like hue",
                "Hair turns white or falls out",
                "Voice becomes raspy or echoes",
                "Fingers elongate slightly",
                "Breath smells of ozone or decay",
                "Shadow moves independently",
                "Reflection shows different face"
            ],
            "major": [
                "Grow small horns or antlers",
                "Skin becomes scaly or leathery",
                "Eyes become solid color (red, black, gold)",
                "Gain minor tentacle or extra digit",
                "Hair becomes living snakes or vines",
                "Body emits faint magical aura",
                "Gain animal feature (cat eyes, goat legs)",
                "Age rapidly or become ageless"
            ],
            "severe": [
                "Gain functional wings (bat, insect, bird)",
                "Body partially transforms into elemental form",
                "Gain extra functional limb",
                "Become partially ethereal or shadowy",
                "Skin becomes stone, bark, or crystal",
                "Eyes become gems or portals",
                "Gain patron-specific feature (tentacles, eyes, mouths)",
                "Become permanently surrounded by minor spell effects"
            ]
        }
    
    # ===== DICE CHAIN METHODS =====
    
    def roll_dice_chain(self, dice_type: str, modifier: int = 0) -> Tuple[int, str]:
        """Roll a dice from the DCC dice chain using true random generator"""
        try:
            # Use the true random dice roller
            roll = self.dice_roller.roll(dice_type, modifier=modifier)
            return roll, dice_type
        except ValueError:
            # Fall back to standard dice
            return self.dice_roller.roll('d20', modifier=modifier), "d20"
    
    def roll_dice(self, dice_type: str, count: int = 1, modifier: int = 0) -> Union[int, List[int]]:
        """
        Roll dice using the true random generator.
        
        Args:
            dice_type: Type of dice (e.g., 'd6', 'd20', 'd%')
            count: Number of dice to roll
            modifier: Modifier to add to total
        
        Returns:
            Single roll result or list of individual rolls
        """
        return self.dice_roller.roll(dice_type, count, modifier)
    
    def roll_percentage(self) -> Tuple[int, str]:
        """Roll a percentage die (d%)."""
        return self.dice_roller.roll_percentage()
    
    def roll_spell_check(self, spell_level: int, caster_level: int = 1) -> Dict[str, Union[int, str, bool]]:
        """Roll a DCC spell check with potential spellburn."""
        return self.dice_roller.roll_spell_check(spell_level, caster_level)
    
    def roll_crit(self, attack_roll: int, weapon_type: str = 'normal') -> Dict[str, Union[int, str, List[int]]]:
        """Roll a DCC critical hit."""
        return self.dice_roller.roll_crit(attack_roll, weapon_type)
    
    def roll_fumble(self, fumble_roll: int = None) -> Dict[str, Union[int, str, List[int]]]:
        """Roll a DCC fumble."""
        return self.dice_roller.roll_fumble(fumble_roll)
    
    def roll_luck_check(self, luck_score: int) -> Dict[str, Union[int, str, bool]]:
        """Roll a DCC luck check."""
        return self.dice_roller.roll_luck_check(luck_score)
    
    def roll_table(self, table: Dict[int, str], dice_type: str = 'd20') -> str:
        """Roll on a table using the specified dice type."""
        return self.dice_roller.roll_table(table, dice_type)
    
    def batch_roll(self, rolls: List[Tuple[str, int, int]]) -> List[Union[int, List[int]]]:
        """Perform multiple rolls at once."""
        return self.dice_roller.batch_roll(rolls)
    
    def step_up_dice(self, current_dice: str) -> str:
        """Step up one die in the chain (for high-level casters)"""
        try:
            current = DCCDice(current_dice)
            current_index = self.dice_chain.index(current)
            if current_index < len(self.dice_chain) - 1:
                return self.dice_chain[current_index + 1].value
            return current_dice
        except (ValueError, IndexError):
            return current_dice
    
    def step_down_dice(self, current_dice: str) -> str:
        """Step down one die in the chain"""
        try:
            current = DCCDice(current_dice)
            current_index = self.dice_chain.index(current)
            if current_index > 0:
                return self.dice_chain[current_index - 1].value
            return current_dice
        except (ValueError, IndexError):
            return current_dice
    
    # ===== SPELLBURN METHODS =====
    
    def apply_spellburn(self, character_name: str, ability: str, points: int) -> Dict[str, Any]:
        """Apply spellburn to a character's ability score"""
        character = self.state_manager.get_character(character_name)
        if not character:
            return {"error": f"Character not found: {character_name}"}
        
        if ability not in ["strength", "agility", "stamina"]:
            return {"error": f"Cannot spellburn {ability}. Must be strength, agility, or stamina."}
        
        current_score = character["abilities"][ability]["score"]
        if current_score - points < 3:
            return {"error": f"Cannot reduce {ability} below 3. Current: {current_score}, requested: {points}"}
        
        # Apply spellburn
        character["abilities"][ability]["score"] -= points
        character["abilities"][ability]["spellburn_used"] += points
        
        # Add to history
        spellburn_entry = {
            "timestamp": datetime.now().isoformat(),
            "ability": ability,
            "points": points,
            "new_score": character["abilities"][ability]["score"],
            "bonus_applied": points  # 1:1 bonus to spell check
        }
        
        if "spellburn_history" not in character:
            character["spellburn_history"] = []
        character["spellburn_history"].append(spellburn_entry)
        
        # Save character
        self.state_manager.save_character(character_name, character)
        
        return {
            "success": True,
            "character": character_name,
            "ability": ability,
            "points_burned": points,
            "new_score": character["abilities"][ability]["score"],
            "spell_check_bonus": points,
            "recovery_rate": "1 point per day"
        }
    
    def recover_spellburn(self, character_name: str, days: int = 1) -> Dict[str, Any]:
        """Recover spellburn points over time"""
        character = self.state_manager.get_character(character_name)
        if not character:
            return {"error": f"Character not found: {character_name}"}
        
        recovered = {}
        for ability in ["strength", "agility", "stamina"]:
            if character["abilities"][ability]["spellburn_used"] > 0:
                # Recover 1 point per day per ability
                recovery = min(days, character["abilities"][ability]["spellburn_used"])
                character["abilities"][ability]["score"] += recovery
                character["abilities"][ability]["spellburn_used"] -= recovery
                character["abilities"][ability]["spellburn_recovery"] += recovery
                
                recovered[ability] = {
                    "points_recovered": recovery,
                    "new_score": character["abilities"][ability]["score"],
                    "remaining_spellburn": character["abilities"][ability]["spellburn_used"]
                }
        
        if recovered:
            self.state_manager.save_character(character_name, character)
        
        return {
            "success": True,
            "character": character_name,
            "days_rested": days,
            "recovered": recovered
        }
    
    # ===== LUCK METHODS =====
    
    def burn_luck(self, character_name: str, points: int) -> Dict[str, Any]:
        """Burn Luck points for a bonus"""
        character = self.state_manager.get_character(character_name)
        if not character:
            return {"error": f"Character not found: {character_name}"}
        
        current_luck = character["abilities"]["luck"]["score"]
        if points > current_luck:
            return {"error": f"Not enough Luck. Current: {current_luck}, requested: {points}"}
        
        # Burn Luck (permanent reduction)
        character["abilities"]["luck"]["score"] -= points
        character["abilities"]["luck"]["points_burned"] += points
        character["abilities"]["luck"]["permanent_loss"] += points
        
        # Add to history
        luck_entry = {
            "timestamp": datetime.now().isoformat(),
            "points_burned": points,
            "new_luck_score": character["abilities"]["luck"]["score"],
            "bonus": f"+{points}d to check"  # +1d per point burned
        }
        
        if "luck_burn_history" not in character:
            character["luck_burn_history"] = []
        character["luck_burn_history"].append(luck_entry)
        
        # Save character
        self.state_manager.save_character(character_name, character)
        
        return {
            "success": True,
            "character": character_name,
            "luck_points_burned": points,
            "new_luck_score": character["abilities"]["luck"]["score"],
            "bonus": f"+{points}d to check (step up dice chain)",
            "permanent": True
        }
    
    # ===== CORRUPTION METHODS =====
    
    def apply_corruption(self, character_name: str, severity: str = "minor") -> Dict[str, Any]:
        """Apply corruption to a character from spell failure"""
        character = self.state_manager.get_character(character_name)
        if not character:
            return {"error": f"Character not found: {character_name}"}
        
        if severity not in self.corruption_tables:
            severity = "minor"
        
        # Select random corruption
        corruption_options = self.corruption_tables[severity]
        corruption = random.choice(corruption_options)
        
        # Add to character
        if "corruption" not in character:
            character["corruption"] = []
        character["corruption"].append(corruption)
        
        # Add to history
        corruption_entry = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "description": corruption,
            "source": "spell failure"
        }
        
        if "corruption_history" not in character:
            character["corruption_history"] = []
        character["corruption_history"].append(corruption_entry)
        
        # Update mercurial magic taint
        if "mercurial_magic" not in character:
            character["mercurial_magic"] = {}
        character["mercurial_magic"]["taint_level"] = character["mercurial_magic"].get("taint_level", 0) + 1
        
        # Save character
        self.state_manager.save_character(character_name, character)
        
        return {
            "success": True,
            "character": character_name,
            "severity": severity,
            "corruption": corruption,
            "taint_level": character["mercurial_magic"]["taint_level"],
            "warning": "Corruption is permanent and may have gameplay effects"
        }
    
    # ===== CRITICAL HIT/FUMBLE METHODS =====
    
    def resolve_critical(self, character_name: str, roll: int) -> Dict[str, Any]:
        """Resolve a critical hit based on class and roll"""
        character = self.state_manager.get_character(character_name)
        if not character:
            return {"error": f"Character not found: {character_name}"}
        
        character_class = character.get("class", "Warrior")
        if character_class not in self.crit_tables:
            character_class = "Warrior"
        
        crit_table = self.crit_tables[character_class]
        
        # Determine result based on roll (1-20 maps to table index)
        table_index = min(roll - 1, len(crit_table) - 1) if roll <= 20 else len(crit_table) - 1
        result = crit_table[table_index]
        
        return {
            "success": True,
            "character": character_name,
            "class": character_class,
            "roll": roll,
            "result": result,
            "table_index": table_index + 1
        }
    
    def resolve_fumble(self, character_name: str, roll: int) -> Dict[str, Any]:
        """Resolve a fumble based on class and roll"""
        character = self.state_manager.get_character(character_name)
        if not character:
            return {"error": f"Character not found: {character_name}"}
        
        character_class = character.get("class", "Warrior")
        if character_class not in self.fumble_tables:
            character_class = "Warrior"
        
        fumble_table = self.fumble_tables[character_class]
        
        # Determine result based on roll (1-20 maps to table index)
        table_index = min(roll - 1, len(fumble_table) - 1) if roll <= 20 else len(fumble_table) - 1
        result = fumble_table[table_index]
        
        return {
            "success": True,
            "character": character_name,
            "class": character_class,
            "roll": roll,
            "result": result,
            "table_index": table_index + 1
        }
    
    # ===== MIGHTY DEEDS OF ARMS =====
    
    def attempt_deed(self, character_name: str, deed_description: str, deed_die: str = "d3") -> Dict[str, Any]:
        """Attempt a Mighty Deed of Arms (Warrior/Dwarf special ability)"""
        character = self.state_manager.get_character(character_name)
        if not character:
            return {"error": f"Character not found: {character_name}"}
        
        character_class = character.get("class", "")
        if character_class not in ["Warrior", "Dwarf"]:
            return {"error": f"{character_class} cannot perform Mighty Deeds of Arms"}
        
        # Roll deed die
        deed_roll, _ = self.roll_dice_chain(deed_die)
        
        # Deed succeeds if roll is 3 or higher (on d3)
        success = deed_roll >= 3
        
        # Record deed attempt
        deed_entry = {
            "timestamp": datetime.now().isoformat(),
            "description": deed_description,
            "deed_die": deed_die,
            "roll": deed_roll,
            "success": success
        }
        
        if "deeds" not in character:
            character["deeds"] = {}
        if "deeds_attempted" not in character["deeds"]:
            character["deeds"]["deeds_attempted"] = []
        character["deeds"]["deeds_attempted"].append(deed_entry)
        
        if success:
            if "deeds_succeeded" not in character["deeds"]:
                character["deeds"]["deeds_succeeded"] = []
            character["deeds"]["deeds_succeeded"].append(deed_entry)
        
        # Save character
        self.state_manager.save_character(character_name, character)
        
        return {
            "success": success,
            "character": character_name,
            "class": character_class,
            "deed": deed_description,
            "deed_die": deed_die,
            "roll": deed_roll,
            "result": "Success" if success else "Failure",
            "effect": "Special maneuver succeeds with attack" if success else "Normal attack only"
        }
    
    # ===== TURN UNDEAD =====
    
    def turn_undead(self, character_name: str, target_hd: int) -> Dict[str, Any]:
        """Attempt to turn undead (Cleric special ability)"""
        character = self.state_manager.get_character(character_name)
        if not character:
            return {"error": f"Character not found: {character_name}"}
        
        character_class = character.get("class", "")
        if character_class != "Cleric":
            return {"error": f"{character_class} cannot turn undead"}
        
        # Roll turn attempt
        turn_roll, _ = self.roll_dice_chain("d20")
        
        # Simple turning logic: succeed if roll > target HD
        success = turn_roll > target_hd
        degree = turn_roll - target_hd
        
        # Record turn attempt
        turn_entry = {
            "timestamp": datetime.now().isoformat(),
            "target_hd": target_hd,
            "roll": turn_roll,
            "success": success,
            "degree": degree
        }
        
        if "turn_undead" not in character:
            character["turn_undead"] = {}
        if "turns_attempted" not in character["turn_undead"]:
            character["turn_undead"]["turns_attempted"] = 0
        character["turn_undead"]["turns_attempted"] += 1
        
        if success:
            if "turns_succeeded" not in character["turn_undead"]:
                character["turn_undead"]["turns_succeeded"] = 0
            character["turn_undead"]["turns_succeeded"] += 1
        
        # Save character
        self.state_manager.save_character(character_name, character)
        
        return {
            "success": success,
            "character": character_name,
            "class": character_class,
            "target_hd": target_hd,
            "roll": turn_roll,
            "degree": degree,
            "result": f"Turned (flee for {degree} rounds)" if success else "No effect",
            "turns_attempted": character["turn_undead"]["turns_attempted"],
            "turns_succeeded": character["turn_undead"].get("turns_succeeded", 0)
        }
    
    # ===== SPELL CHECK SYSTEM =====
    
    def spell_check(self, character_name: str, spell_level: int, modifiers: Dict[str, int] = None) -> Dict[str, Any]:
        """Perform a DCC spell check with all modifiers"""
        character = self.state_manager.get_character(character_name)
        if not character:
            return {"error": f"Character not found: {character_name}"}
        
        character_class = character.get("class", "")
        if character_class not in ["Wizard", "Elf"]:
            return {"error": f"{character_class} cannot cast arcane spells"}
        
        # Base spell check die
        spell_die = character.get("mercurial_magic", {}).get("spell_check_dice", "d20")
        
        # Calculate modifiers
        mod_dict = modifiers or {}
        intelligence_mod = character["abilities"]["intelligence"]["modifier"]
        level_mod = character.get("level", 1)
        spellburn_bonus = sum(
            character["abilities"][ability]["spellburn_used"]
            for ability in ["strength", "agility", "stamina"]
        )
        
        # Total modifier
        total_mod = (
            self._parse_modifier(intelligence_mod) +
            level_mod +
            spellburn_bonus +
            mod_dict.get("other", 0)
        )
        
        # Roll spell check
        roll, die_used = self.roll_dice_chain(spell_die, total_mod)
        
        # Determine result
        if roll == 1:
            result = "Mishap"
            # Apply corruption on natural 1
            corruption_result = self.apply_corruption(character_name, "minor")
        elif roll < 10 + spell_level:
            result = "Failure"
        elif roll < 20 + spell_level:
            result = "Success"
        else:
            result = "Critical Success"
            # Step up die for future casts on critical
            new_die = self.step_up_dice(spell_die)
            if "mercurial_magic" not in character:
                character["mercurial_magic"] = {}
            character["mercurial_magic"]["spell_check_dice"] = new_die
            self.state_manager.save_character(character_name, character)
        
        return {
            "success": True,
            "character": character_name,
            "class": character_class,
            "spell_level": spell_level,
            "spell_die": spell_die,
            "roll": roll,
            "die_used": die_used,
            "modifiers": {
                "intelligence": self._parse_modifier(intelligence_mod),
                "level": level_mod,
                "spellburn": spellburn_bonus,
                "other": mod_dict.get("other", 0),
                "total": total_mod
            },
            "result": result,
            "effect": self._get_spell_effect(result, spell_level, roll)
        }
    
    def _parse_modifier(self, mod_str: str) -> int:
        """Parse modifier string like '+2' or '-1' to integer"""
        try:
            return int(mod_str)
        except (ValueError, TypeError):
            # Try to extract number
            if isinstance(mod_str, str):
                if mod_str.startswith("+"):
                    return int(mod_str[1:]) if mod_str[1:].isdigit() else 0
                elif mod_str.startswith("-"):
                    return -int(mod_str[1:]) if mod_str[1:].isdigit() else 0
                else:
                    return int(mod_str) if mod_str.isdigit() else 0
            return 0
    
    def _get_spell_effect(self, result: str, spell_level: int, roll: int) -> str:
        """Get description of spell effect based on result"""
        if result == "Mishap":
            return "Spell fails catastrophically. Caster suffers corruption and possible additional effects."
        elif result == "Failure":
            return "Spell fails with no effect. Spell is not lost and may be attempted again."
        elif result == "Success":
            duration = f"{spell_level + roll - 10} rounds" if roll < 20 else "1 hour"
            intensity = "Standard" if roll < 15 else "Enhanced"
            return f"Spell succeeds with {intensity} effect. Duration: {duration}."
        elif result == "Critical Success":
            duration = "1 day"
            intensity = "Maximum"
            return f"Spell succeeds with {intensity} effect. Duration: {duration}. Spell check die steps up for future casts."
        return "Unknown result"
    
    # ===== UTILITY METHODS =====
    
    def get_character_summary(self, character_name: str) -> Dict[str, Any]:
        """Get a summary of DCC-specific character state"""
        character = self.state_manager.get_character(character_name)
        if not character:
            return {"error": f"Character not found: {character_name}"}
        
        return {
            "name": character["name"],
            "class": character.get("class", "Unknown"),
            "level": character.get("level", 1),
            "hit_points": character.get("hit_points", {}),
            "abilities": {
                ability: {
                    "score": data["score"],
                    "modifier": data["modifier"],
                    "spellburn_used": data.get("spellburn_used", 0)
                }
                for ability, data in character.get("abilities", {}).items()
                if ability in ["strength", "agility", "stamina", "intelligence", "personality", "luck"]
            },
            "luck": {
                "score": character["abilities"]["luck"]["score"],
                "points_burned": character["abilities"]["luck"].get("points_burned", 0),
                "permanent_loss": character["abilities"]["luck"].get("permanent_loss", 0)
            },
            "corruption": character.get("corruption", []),
            "corruption_count": len(character.get("corruption", [])),
            "spellburn_history": len(character.get("spellburn_history", [])),
            "mercurial_magic": character.get("mercurial_magic", {}),
            "deeds_attempted": len(character.get("deeds", {}).get("deeds_attempted", [])),
            "deeds_succeeded": len(character.get("deeds", {}).get("deeds_succeeded", [])),
            "turns_attempted": character.get("turn_undead", {}).get("turns_attempted", 0),
            "turns_succeeded": character.get("turn_undead", {}).get("turns_succeeded", 0)
        }
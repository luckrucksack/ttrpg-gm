#!/usr/bin/env python3
"""
DCC Judge System - Specialized AI Judge for Dungeon Crawl Classics.
Integrates with existing TTRPG GM system but adds DCC-specific mechanics.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import signal
import threading

# Bootstrap repo root so package imports resolve regardless of cwd
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from gm_core.config import validate_config, DATA_DIR
from systems.dcc.dice import DCCDiceRoller  # DCC dice chain
from gm_core.agents.pdf_ingestor import PDFIngestor
from gm_core.agents.deepseek_client import DeepSeekClient
from gm_core.agents.prose_refiner import ProseRefiner
from gm_core.agents.state_manager import StateManager
from gm_core.agents.discord_bridge import DiscordBridge, run_discord_bridge
from systems.dcc.manager import DCCManager

class DCCJudge:
    """DCC-specific AI Judge with all DCC mechanics integrated"""
    
    def __init__(self):
        self.config_errors = validate_config()
        if self.config_errors:
            print("Configuration errors:")
            for error in self.config_errors:
                print(f"  - {error}")
            raise RuntimeError("Configuration validation failed")
        
        # Initialize core components
        self.dice_roller = DCCDiceRoller()  # True random DCC dice roller
        self.pdf_ingestor = PDFIngestor()
        self.deepseek = DeepSeekClient()
        self.prose_refiner = ProseRefiner(self.deepseek)
        self.state_manager = StateManager(DATA_DIR)
        
        # Initialize DCC-specific manager
        self.dcc_manager = DCCManager(self.state_manager)
        
        # Discord bridge will be initialized when needed
        self.discord_bridge = None
        
        # Runtime state
        self.current_adventure = None
        self.current_scene = None
        self.party_members = []
        
        # DCC-specific state
        self.dcc_rules_active = True
        self.last_crit_table_used = None
        self.last_fumble_table_used = None
        
        print("✅ DCC Judge System initialized")
        print("   - DCC Mechanics: Spellburn, Corruption, Mercurial Magic")
        print("   - Dice Chain: d3-d30 with step up/down")
        print("   - Critical/Fumble Tables: Class-specific")
        print("   - Luck System: Burnable with permanent effects")
    
    # ===== CORE RUNTIME LOOP =====
    
    async def run_judge_loop(self, adventure_name: str):
        """Main DCC Judge runtime loop"""
        print(f"🚀 Starting DCC Judge for adventure: {adventure_name}")
        
        # Load adventure
        if not await self._load_adventure(adventure_name):
            print(f"❌ Failed to load adventure: {adventure_name}")
            return
        
        # Load party
        if not await self._load_party():
            print("❌ No party members found")
            return
        
        print(f"✅ Adventure loaded: {adventure_name}")
        print(f"✅ Party loaded: {len(self.party_members)} characters")
        print("\n🎭 DCC Judge is ready. Awaiting player input...")
        print("   Type '!help' for DCC-specific commands")
        
        # Main loop
        while True:
            try:
                # Get player input (from Discord or console)
                player_input = await self._get_player_input()
                if not player_input:
                    await asyncio.sleep(1)
                    continue
                
                # Process input through DCC Judge pipeline
                response = await self._process_dcc_turn(player_input)
                
                # Deliver response
                await self._deliver_response(response)
                
            except KeyboardInterrupt:
                print("\n🛑 DCC Judge shutting down...")
                break
            except Exception as e:
                print(f"❌ Error in judge loop: {e}")
                await asyncio.sleep(1)
    
    async def _load_adventure(self, adventure_name: str) -> bool:
        """Load a DCC adventure"""
        adventure_path = DATA_DIR / "adventures" / f"{adventure_name}.txt"
        
        if not adventure_path.exists():
            print(f"❌ Adventure file not found: {adventure_path}")
            return False
        
        try:
            with open(adventure_path, 'r') as f:
                adventure_content = f.read()
            
            # Parse adventure (simplified)
            self.current_adventure = {
                "name": adventure_name,
                "content": adventure_content,
                "scenes": self._extract_scenes(adventure_content),
                "loaded_at": datetime.now().isoformat()
            }
            
            # Set initial scene
            if self.current_adventure["scenes"]:
                self.current_scene = self.current_adventure["scenes"][0]
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading adventure: {e}")
            return False
    
    def _extract_scenes(self, content: str) -> List[Dict]:
        """Extract scenes from adventure text (simplified)"""
        scenes = []
        lines = content.split('\n')
        
        current_scene = None
        for line in lines:
            line = line.strip()
            if line.startswith('# Scene:'):
                if current_scene:
                    scenes.append(current_scene)
                current_scene = {
                    "title": line.replace('# Scene:', '').strip(),
                    "description": "",
                    "encounters": [],
                    "treasures": [],
                    "exits": []
                }
            elif line.startswith('## ') and current_scene:
                current_scene["description"] += line.replace('## ', '') + '\n'
            elif line.startswith('- Encounter:') and current_scene:
                current_scene["encounters"].append(line.replace('- Encounter:', '').strip())
            elif line.startswith('- Treasure:') and current_scene:
                current_scene["treasures"].append(line.replace('- Treasure:', '').strip())
            elif line.startswith('->') and current_scene:
                current_scene["exits"].append(line.replace('->', '').strip())
        
        if current_scene:
            scenes.append(current_scene)
        
        return scenes
    
    async def _load_party(self) -> bool:
        """Load party members for DCC adventure"""
        party_path = DATA_DIR / "party_dcc.json"
        
        if party_path.exists():
            try:
                with open(party_path, 'r') as f:
                    party_data = json.load(f)
                self.party_members = party_data.get("members", [])
            except Exception as e:
                print(f"❌ Error loading party: {e}")
                return False
        else:
            # Look for DCC characters in characters directory
            chars_dir = DATA_DIR / "characters"
            dcc_chars = []
            
            for char_file in chars_dir.glob("*.json"):
                try:
                    with open(char_file, 'r') as f:
                        char_data = json.load(f)
                    if char_data.get("system") == "Dungeon Crawl Classics":
                        dcc_chars.append(char_data["name"])
                except:
                    continue
            
            self.party_members = dcc_chars
        
        return len(self.party_members) > 0
    
    async def _get_player_input(self) -> Optional[str]:
        """Get player input (simplified - would integrate with Discord)"""
        # For now, read from console
        try:
            return await asyncio.get_event_loop().run_in_executor(
                None, input, "Player > "
            )
        except (EOFError, KeyboardInterrupt):
            return None
    
    async def _process_dcc_turn(self, player_input: str) -> Dict[str, Any]:
        """Process a player turn through the DCC Judge pipeline"""
        print(f"🔍 Processing: {player_input}")
        
        # Check for DCC-specific commands
        dcc_command = self._parse_dcc_command(player_input)
        if dcc_command:
            return await self._handle_dcc_command(dcc_command)
        
        # Normal AI Judge processing
        return await self._handle_normal_turn(player_input)
    
    def _parse_dcc_command(self, input_text: str) -> Optional[Dict]:
        """Parse DCC-specific commands"""
        input_lower = input_text.lower().strip()
        
        # DCC-specific commands
        if input_lower.startswith("!spellburn"):
            parts = input_lower.split()
            if len(parts) >= 3:
                return {
                    "type": "spellburn",
                    "character": parts[1],
                    "ability": parts[2],
                    "points": int(parts[3]) if len(parts) > 3 else 1
                }
        
        elif input_lower.startswith("!luck"):
            parts = input_lower.split()
            if len(parts) >= 2:
                return {
                    "type": "luck",
                    "character": parts[1],
                    "points": int(parts[2]) if len(parts) > 2 else 1
                }
        
        elif input_lower.startswith("!deed"):
            # Extract deed description
            deed_desc = input_text[5:].strip()
            if deed_desc:
                parts = deed_desc.split(maxsplit=1)
                if len(parts) >= 1:
                    return {
                        "type": "deed",
                        "character": parts[0],
                        "description": parts[1] if len(parts) > 1 else "Mighty Deed"
                    }
        
        elif input_lower.startswith("!turn"):
            parts = input_lower.split()
            if len(parts) >= 3:
                return {
                    "type": "turn",
                    "character": parts[1],
                    "target_hd": int(parts[2])
                }
        
        elif input_lower.startswith("!spell"):
            parts = input_lower.split()
            if len(parts) >= 3:
                return {
                    "type": "spell",
                    "character": parts[1],
                    "spell_level": int(parts[2]),
                    "modifiers": {"other": int(parts[3])} if len(parts) > 3 else {}
                }
        
        elif input_lower.startswith("!crit"):
            parts = input_lower.split()
            if len(parts) >= 2:
                return {
                    "type": "crit",
                    "character": parts[1],
                    "roll": int(parts[2]) if len(parts) > 2 else random.randint(1, 20)
                }
        
        elif input_lower.startswith("!fumble"):
            parts = input_lower.split()
            if len(parts) >= 2:
                return {
                    "type": "fumble",
                    "character": parts[1],
                    "roll": int(parts[2]) if len(parts) > 2 else random.randint(1, 20)
                }
        
        elif input_lower.startswith("!dcc"):
            return {"type": "help"}
        
        return None
    
    async def _handle_dcc_command(self, command: Dict) -> Dict[str, Any]:
        """Handle DCC-specific commands"""
        cmd_type = command["type"]
        
        if cmd_type == "spellburn":
            result = self.dcc_manager.apply_spellburn(
                command["character"],
                command["ability"],
                command["points"]
            )
            return self._format_dcc_response("spellburn", result)
        
        elif cmd_type == "luck":
            result = self.dcc_manager.burn_luck(
                command["character"],
                command["points"]
            )
            return self._format_dcc_response("luck", result)
        
        elif cmd_type == "deed":
            result = self.dcc_manager.attempt_deed(
                command["character"],
                command["description"]
            )
            return self._format_dcc_response("deed", result)
        
        elif cmd_type == "turn":
            result = self.dcc_manager.turn_undead(
                command["character"],
                command["target_hd"]
            )
            return self._format_dcc_response("turn", result)
        
        elif cmd_type == "spell":
            result = self.dcc_manager.spell_check(
                command["character"],
                command["spell_level"],
                command.get("modifiers", {})
            )
            return self._format_dcc_response("spell", result)
        
        elif cmd_type == "crit":
            result = self.dcc_manager.resolve_critical(
                command["character"],
                command["roll"]
            )
            return self._format_dcc_response("crit", result)
        
        elif cmd_type == "fumble":
            result = self.dcc_manager.resolve_fumble(
                command["character"],
                command["roll"]
            )
            return self._format_dcc_response("fumble", result)
        
        elif cmd_type == "roll":
            # Handle dice rolling commands
            dice_type = command.get("dice", "d20")
            count = command.get("count", 1)
            modifier = command.get("modifier", 0)
            
            result = self.dcc_manager.roll_dice(dice_type, count, modifier)
            return self._format_dice_response(dice_type, count, modifier, result)
        
        elif cmd_type == "percent":
            result, description = self.dcc_manager.roll_percentage()
            return {
                "text": f"🎲 Percentage Roll: **{result}%** - {description}",
                "type": "dice",
                "raw_result": {"roll": result, "description": description}
            }
        
        elif cmd_type == "spell_check":
            spell_level = command.get("spell_level", 1)
            caster_level = command.get("caster_level", 1)
            result = self.dcc_manager.roll_spell_check(spell_level, caster_level)
            return self._format_dcc_response("spell_check", result)
        
        elif cmd_type == "crit_roll":
            attack_roll = command.get("attack_roll", 20)
            weapon_type = command.get("weapon_type", "normal")
            result = self.dcc_manager.roll_crit(attack_roll, weapon_type)
            return self._format_dcc_response("crit_roll", result)
        
        elif cmd_type == "fumble_roll":
            fumble_roll = command.get("fumble_roll")
            result = self.dcc_manager.roll_fumble(fumble_roll)
            return self._format_dcc_response("fumble_roll", result)
        
        elif cmd_type == "luck_check":
            luck_score = command.get("luck_score", 10)
            result = self.dcc_manager.roll_luck_check(luck_score)
            return self._format_dcc_response("luck_check", result)
        
        elif cmd_type == "help":
            return self._get_dcc_help()
        
        return {"error": f"Unknown DCC command: {cmd_type}"}
    
    def _format_dice_response(self, dice_type: str, count: int, modifier: int, result) -> Dict[str, Any]:
        """Format dice roll response for delivery"""
        if isinstance(result, list):
            if count == 1:
                # Single die rolled as list
                total = result[0]
                details = f"Roll: {result[0]}"
            else:
                # Multiple dice
                total = sum(result)
                details = f"Rolls: {', '.join(str(r) for r in result)} = {total}"
        else:
            # Single die rolled as int
            total = result
            details = f"Roll: {result}"
        
        if modifier != 0:
            details += f" + {modifier} = {total}"
        
        text = f"🎲 **DICE ROLL**\n"
        text += f"Type: {count}{dice_type}"
        if modifier != 0:
            text += f"{'+' if modifier > 0 else ''}{modifier}"
        text += f"\nResult: **{total}**\n"
        text += f"Details: {details}"
        
        return {
            "text": text,
            "type": "dice",
            "raw_result": {
                "dice_type": dice_type,
                "count": count,
                "modifier": modifier,
                "result": result,
                "total": total
            }
        }
    
    def _format_dcc_response(self, action: str, result: Dict) -> Dict[str, Any]:
        """Format DCC action response for delivery"""
        if "error" in result:
            return {
                "text": f"❌ DCC {action.title()} Error: {result['error']}",
                "type": "error",
                "raw_result": result
            }
        
        # Format based on action type
        if action == "spellburn":
            text = (
                f"🔥 **SPELLBURN APPLIED**\n"
                f"Character: {result['character']}\n"
                f"Ability: {result['ability'].title()}\n"
                f"Points Burned: {result['points_burned']}\n"
                f"New Score: {result['new_score']}\n"
                f"Spell Check Bonus: +{result['spell_check_bonus']}\n"
                f"Recovery: {result['recovery_rate']}"
            )
        
        elif action == "luck":
            text = (
                f"🍀 **LUCK BURNED**\n"
                f"Character: {result['character']}\n"
                f"Points Burned: {result['luck_points_burned']}\n"
                f"New Luck Score: {result['new_luck_score']}\n"
                f"Bonus: {result['bonus']}\n"
                f"Effect: {result['permanent']}"
            )
        
        elif action == "deed":
            success_icon = "✅" if result["success"] else "❌"
            text = (
                f"⚔️ **MIGHTY DEED OF ARMS** {success_icon}\n"
                f"Character: {result['character']} ({result['class']})\n"
                f"Deed: {result['deed']}\n"
                f"Deed Die: {result['deed_die']} → {result['roll']}\n"
                f"Result: {result['result']}\n"
                f"Effect: {result['effect']}"
            )
        
        elif action == "turn":
            success_icon = "✅" if result["success"] else "❌"
            text = (
                f"✝️ **TURN UNDEAD** {success_icon}\n"
                f"Character: {result['character']} ({result['class']})\n"
                f"Target HD: {result['target_hd']}\n"
                f"Roll: {result['roll']}\n"
                f"Result: {result['result']}\n"
                f"Success Rate: {result['turns_succeeded']}/{result['turns_attempted']}"
            )
        
        elif action == "spell":
            # Map result to icon
            result_icons = {
                "Mishap": "💥",
                "Failure": "❌",
                "Success": "✅",
                "Critical Success": "🌟"
            }
            icon = result_icons.get(result["result"], "❓")
            
            text = (
                f"🔮 **SPELL CHECK** {icon}\n"
                f"Character: {result['character']} ({result['class']})\n"
                f"Spell Level: {result['spell_level']}\n"
                f"Roll: {result['die_used']} + {result['modifiers']['total']} = {result['roll']}\n"
                f"Result: {result['result']}\n"
                f"Effect: {result['effect']}"
            )
        
        elif action == "crit":
            text = (
                f"💥 **CRITICAL HIT**\n"
                f"Character: {result['character']} ({result['class']})\n"
                f"Roll: {result['roll']}\n"
                f"Table: {result['table_index']}\n"
                f"Result: {result['result']}"
            )
        
        elif action == "fumble":
            text = (
                f"🤦 **FUMBLE**\n"
                f"Character: {result['character']} ({result['class']})\n"
                f"Roll: {result['roll']}\n"
                f"Table: {result['table_index']}\n"
                f"Result: {result['result']}"
            )
        
        else:
            text = f"DCC Action: {action}\nResult: {json.dumps(result, indent=2)}"
        
        return {
            "text": text,
            "type": f"dcc_{action}",
            "raw_result": result
        }
    
    def _get_dcc_help(self) -> Dict[str, Any]:
        """Get DCC-specific help"""
        help_text = (
            "🎮 **DCC JUDGE COMMANDS**\n\n"
            "**Core Mechanics:**\n"
            "`!spellburn <character> <ability> <points>` - Burn ability points for spell bonus\n"
            "`!luck <character> <points>` - Burn Luck points for bonus (permanent)\n"
            "`!deed <character> <description>` - Attempt Mighty Deed of Arms\n"
            "`!turn <character> <target_hd>` - Attempt to turn undead\n"
            "`!spell <character> <spell_level> [modifier]` - Perform spell check\n"
            "`!crit <character> [roll]` - Resolve critical hit\n"
            "`!fumble <character> [roll]` - Resolve fumble\n\n"
            "**Examples:**\n"
            "`!spellburn grom strength 3` - Burn 3 Strength for +3 spell check\n"
            "`!luck elara 2` - Burn 2 Luck for +2d bonus\n"
            "`!deed thorin disarm the ogre` - Attempt disarming deed\n"
            "`!turn merlin 4` - Turn undead of 4 HD\n"
            "`!spell zephyr 2` - Cast 2nd level spell\n"
            "`!crit grom 17` - Critical hit roll 17\n\n"
            "**DCC Unique Features:**\n"
            "• **Spellburn**: Sacrifice STR/AGI/STA for spell power\n"
            "• **Corruption**: Spell failures cause physical changes\n"
            "• **Mercurial Magic**: Spells improve with critical success\n"
            "• **Luck Points**: Burn for bonuses, permanently reduced\n"
            "• **Dice Chain**: d3-d30 with step up/down mechanics\n"
            "• **Class Tables**: Unique crit/fumble tables per class"
        )
        
        return {
            "text": help_text,
            "type": "help",
            "raw_result": {"command": "dcc_help"}
        }
    
    async def _handle_normal_turn(self, player_input: str) -> Dict[str, Any]:
        """Handle normal player turn through AI Judge"""
        # This would integrate with the existing AI GM system
        # For now, return a placeholder response
        
        return {
            "text": f"The Judge considers your action: '{player_input}'\n\n*The DCC system is active. Use !dcc for special commands.*",
            "type": "narration",
            "scene": self.current_scene["title"] if self.current_scene else "Unknown",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _deliver_response(self, response: Dict[str, Any]):
        """Deliver response to players"""
        # This would integrate with Discord
        # For now, print to console
        
        print("\n" + "="*60)
        print(response["text"])
        print("="*60 + "\n")
    
    # ===== UTILITY METHODS =====
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get DCC Judge system status"""
        return {
            "system": "DCC Judge",
            "status": "active" if self.current_adventure else "idle",
            "adventure": self.current_adventure["name"] if self.current_adventure else None,
            "scene": self.current_scene["title"] if self.current_scene else None,
            "party_size": len(self.party_members),
            "dcc_mechanics_active": self.dcc_rules_active,
            "components": {
                "dice_roller": "active",
                "state_manager": "active",
                "dcc_manager": "active",
                "prose_refiner": "active",
                "deepseek_client": "active"
            }
        }
    
    def create_dcc_character(self, character_data: Dict) -> Dict[str, Any]:
        """Create a new DCC character"""
        # Use the template as base
        template_path = DATA_DIR / "characters" / "dcc_template.json"
        
        try:
            with open(template_path, 'r') as f:
                template = json.load(f)
            
            # Merge with provided data
            character = {**template, **character_data}
            character["name"] = character_data.get("name", "Unnamed DCC Character")
            character["metadata"]["created"] = datetime.now().isoformat()
            character["metadata"]["source"] = "dcc_judge"
            
            # Save character
            char_name_safe = character["name"].lower().replace(" ", "_")
            char_path = DATA_DIR / "characters" / f"{char_name_safe}.json"
            
            with open(char_path, 'w') as f:
                json.dump(character, f, indent=2)
            
            # Add to party if not already there
            if character["name"] not in self.party_members:
                self.party_members.append(character["name"])
                self._save_party()
            
            return {
                "success": True,
                "character": character["name"],
                "file": str(char_path),
                "system": "Dungeon Crawl Classics",
                "message": f"DCC character '{character['name']}' created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create DCC character: {e}"
            }
    
    def _save_party(self):
        """Save current party to file"""
        party_path = DATA_DIR / "party_dcc.json"
        
        party_data = {
            "system": "Dungeon Crawl Classics",
            "created": datetime.now().isoformat(),
            "members": self.party_members,
            "adventure": self.current_adventure["name"] if self.current_adventure else None
        }
        
        with open(party_path, 'w') as f:
            json.dump(party_data, f, indent=2)

# ===== MAIN ENTRY POINT =====

async def main():
    """Main entry point for DCC Judge"""
    print("="*60)
    print("DUNGEON CRAWL CLASSICS JUDGE SYSTEM")
    print("="*60)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="DCC AI Judge System")
    parser.add_argument("adventure", nargs="?", help="Adventure name to run")
    parser.add_argument("--create-character", help="Create a DCC character from JSON file")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--test", action="store_true", help="Run DCC mechanics tests")
    
    args = parser.parse_args()
    
    # Initialize DCC Judge
    try:
        judge = DCCJudge()
    except Exception as e:
        print(f"❌ Failed to initialize DCC Judge: {e}")
        return
    
    # Handle commands
    if args.create_character:
        # Create character from JSON file
        try:
            with open(args.create_character, 'r') as f:
                char_data = json.load(f)
            result = judge.create_dcc_character(char_data)
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"❌ Error creating character: {e}")
    
    elif args.status:
        # Show system status
        status = judge.get_system_status()
        print(json.dumps(status, indent=2))
    
    elif args.test:
        # Run DCC mechanics tests
        await run_dcc_tests(judge)
    
    elif args.adventure:
        # Run adventure
        await judge.run_judge_loop(args.adventure)
    
    else:
        # Interactive mode
        print("\nAvailable commands:")
        print("  python systems/dcc/judge.py <adventure_name>  - Run adventure")
        print("  python systems/dcc/judge.py --status          - Show system status")
        print("  python systems/dcc/judge.py --test            - Run DCC mechanics tests")
        print("\nExample adventures in campaigns/dying_earth/adventures/:")
        adventures_dir = DATA_DIR / "adventures"
        if adventures_dir.exists():
            for adv_file in adventures_dir.glob("*.txt"):
                print(f"  • {adv_file.stem}")

async def run_dcc_tests(judge):
    """Run DCC mechanics tests"""
    print("\n🧪 RUNNING DCC MECHANICS TESTS")
    print("="*60)
    
    # Create test character
    test_char = {
        "name": "Test DCC Warrior",
        "class": "Warrior",
        "level": 1,
        "race": "Human",
        "abilities": {
            "strength": {"score": 14, "modifier": "+1"},
            "agility": {"score": 12, "modifier": "+0"},
            "stamina": {"score": 13, "modifier": "+1"},
            "personality": {"score": 10, "modifier": "+0"},
            "intelligence": {"score": 11, "modifier": "+0"},
            "luck": {"score": 15, "modifier": "+1"}
        },
        "hit_points": {"current": 8, "maximum": 8}
    }
    
    result = judge.create_dcc_character(test_char)
    print(f"✅ Created test character: {result['character']}")
    
    # Test spellburn
    print("\n🔥 Testing Spellburn:")
    spellburn_result = judge.dcc_manager.apply_spellburn("test_dcc_warrior", "strength", 2)
    print(f"   Result: {spellburn_result}")
    
    # Test luck burn
    print("\n🍀 Testing Luck Burn:")
    luck_result = judge.dcc_manager.burn_luck("test_dcc_warrior", 1)
    print(f"   Result: {luck_result}")
    
    # Test critical hit
    print("\n💥 Testing Critical Hit:")
    crit_result = judge.dcc_manager.resolve_critical("test_dcc_warrior", 15)
    print(f"   Result: {crit_result['result']}")
    
    # Test fumble
    print("\n🤦 Testing Fumble:")
    fumble_result = judge.dcc_manager.resolve_fumble("test_dcc_warrior", 8)
    print(f"   Result: {fumble_result['result']}")
    
    # Test deed
    print("\n⚔️ Testing Mighty Deed:")
    deed_result = judge.dcc_manager.attempt_deed("test_dcc_warrior", "Disarm opponent")
    print(f"   Result: {deed_result['result']} (Roll: {deed_result['roll']})")
    
    print("\n" + "="*60)
    print("✅ DCC MECHANICS TESTS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
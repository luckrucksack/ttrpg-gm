#!/usr/bin/env python3
"""
Central automation loop for AI TTRPG GM.
Coordinates all agents and manages the runtime loop.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import signal
import threading

# Add agents directory to path
sys.path.insert(0, str(Path(__file__).parent / "agents"))

from config import validate_config, SYSTEM_RULES
from agents.dice_roller import DiceRoller
from agents.pdf_ingestor import PDFIngestor
from agents.deepseek_client import DeepSeekClient
from agents.prose_refiner import ProseRefiner
from agents.state_manager import StateManager
from agents.discord_bridge import DiscordBridge, run_discord_bridge

class AIGameMaster:
    """Main AI Game Master automation engine"""
    
    def __init__(self):
        self.config_errors = validate_config()
        if self.config_errors:
            print("Configuration errors:")
            for error in self.config_errors:
                print(f"  - {error}")
            raise RuntimeError("Configuration validation failed")
        
        # Initialize components
        self.dice_roller = DiceRoller()
        self.pdf_ingestor = PDFIngestor()
        self.deepseek = DeepSeekClient()
        self.prose_refiner = ProseRefiner(self.deepseek)
        self.state_manager = StateManager(Path(__file__).parent / "data")
        
        # Discord bridge will be initialized when needed
        self.discord_bridge = None
        
        # Runtime state
        self.current_adventure = None
        self.current_scene = None
        self.active_characters = []
        self.recent_history = []
        self.is_running = False
        self.is_paused = False  # For !override
        
        # Message queue for async processing
        self.message_queue = asyncio.Queue()
        
        # Statistics
        self.stats = {
            "turns_processed": 0,
            "dice_rolled": 0,
            "messages_sent": 0,
            "start_time": datetime.now().isoformat()
        }
    
    async def initialize_discord(self):
        """Initialize Discord bridge with callbacks"""
        self.discord_bridge = DiscordBridge(
            message_callback=self._handle_player_message,
            roll_callback=self._handle_player_roll
        )
    
    async def _handle_player_message(self, message, override=False, resume=False):
        """Callback for player messages from Discord"""
        if override:
            await self._handle_override()
            return
        
        if resume:
            await self._handle_resume()
            return
        
        # Add to message queue for processing
        await self.message_queue.put({
            "type": "player_message",
            "content": message.content,
            "author": str(message.author),
            "timestamp": datetime.now().isoformat(),
            "message_obj": message
        })
    
    async def _handle_player_roll(self, roll_result, message):
        """Callback for player dice rolls from Discord"""
        # Record player roll
        roll_info = {
            "type": "player_roll",
            "player": str(message.author),
            "roll": roll_result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to recent history for context
        self.recent_history.append(roll_info)
        
        # Trim history
        if len(self.recent_history) > 20:
            self.recent_history = self.recent_history[-20:]
    
    async def _handle_override(self):
        """Handle !override command - halt all operations"""
        print("OVERRIDE: Halting all operations")
        self.is_paused = True
        
        # Clear message queue
        while not self.message_queue.empty():
            try:
                self.message_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
    
    async def _handle_resume(self):
        """Handle !resume command - resume operations"""
        print("RESUME: Resuming operations")
        
        # Re-read all JSONs from disk
        self.state_manager._load_all_states()
        
        # Review Discord history for anything during pause
        if self.discord_bridge:
            recent_messages = self.discord_bridge.get_recent_messages(limit=20)
            for msg in recent_messages:
                if msg.get("type") != "bot_post":  # Player messages during pause
                    await self.message_queue.put({
                        "type": "player_message",
                        "content": msg.get("content", ""),
                        "author": msg.get("author", "Unknown"),
                        "timestamp": msg.get("timestamp", ""),
                        "reconcile": True  # Flag for reconciliation
                    })
        
        self.is_paused = False
    
    def load_adventure(self, adventure_name: str):
        """Load an adventure and prime DeepSeek"""
        # Load adventure JSON
        adventure_path = Path(__file__).parent / "data" / "world_state" / f"{adventure_name}.json"
        
        if not adventure_path.exists():
            print(f"Adventure not found: {adventure_name}")
            return False
        
        with open(adventure_path, 'r') as f:
            adventure_data = json.load(f)
        
        self.current_adventure = adventure_name
        
        # Extract adventure text for priming
        adventure_text = self._extract_adventure_text(adventure_data)
        
        # Prime DeepSeek
        self.deepseek.prime_with_adventure(adventure_text, SYSTEM_RULES)
        
        # Set initial scene
        if "current_location" in adventure_data:
            self.current_scene = adventure_data["current_location"].get("id")
        elif "rooms" in adventure_data and adventure_data["rooms"]:
            self.current_scene = list(adventure_data["rooms"].keys())[0]
        
        print(f"Adventure loaded: {adventure_name}")
        print(f"Initial scene: {self.current_scene}")
        
        return True
    
    def _extract_adventure_text(self, adventure_data: Dict) -> str:
        """Extract readable text from adventure data for priming"""
        text_parts = []
        
        # Add rooms
        if "rooms" in adventure_data:
            for room_id, room_desc in adventure_data["rooms"].items():
                text_parts.append(f"Room {room_id}: {room_desc}")
        
        # Add read-aloud text
        if "read_aloud" in adventure_data:
            for key, text in adventure_data["read_aloud"].items():
                text_parts.append(f"Read Aloud ({key}): {text}")
        
        # Add monsters
        if "monsters" in adventure_data:
            for monster_name, monster_data in adventure_data["monsters"].items():
                text_parts.append(f"Monster: {monster_name}")
                if "stats_text" in monster_data:
                    text_parts.append(monster_data["stats_text"])
        
        # Add NPCs
        if "npcs" in adventure_data:
            for npc_id, npc_data in adventure_data["npcs"].items():
                text_parts.append(f"NPC ({npc_id}): {npc_data.get('description', '')}")
        
        # Add traps
        if "traps" in adventure_data:
            for trap_id, trap_data in adventure_data["traps"].items():
                text_parts.append(f"Trap ({trap_id}): {trap_data.get('description', '')}")
        
        return "\n\n".join(text_parts)
    
    def build_context(self) -> Dict[str, Any]:
        """Build current context for DeepSeek"""
        context = {
            "scene": self.current_scene,
            "adventure": self.current_adventure,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add scene data
        if self.current_adventure and self.current_scene:
            scene_data = self.state_manager.get_scene_data(
                self.current_adventure, 
                self.current_scene
            )
            if scene_data:
                context["scene_data"] = scene_data
        
        # Add characters
        if self.active_characters:
            character_data = []
            for char_name in self.active_characters:
                char = self.state_manager.get_character(char_name)
                if char:
                    # Extract relevant info
                    char_info = {
                        "name": char_name,
                        "hp": char.get("hp", {}).get("current", 0),
                        "max_hp": char.get("hp", {}).get("max", 0),
                        "conditions": char.get("conditions", []),
                        "class": char.get("class", "Unknown"),
                        "level": char.get("level", 1)
                    }
                    character_data.append(char_info)
            context["characters"] = character_data
        
        # Add recent history
        if self.recent_history:
            # Format recent history
            history_text = []
            for item in self.recent_history[-5:]:  # Last 5 items
                if item["type"] == "player_message":
                    history_text.append(f"{item['author']}: {item['content']}")
                elif item["type"] == "player_roll":
                    history_text.append(f"{item['player']} rolled {item['roll'].get('notation')} = {item['roll'].get('total')}")
                elif item["type"] == "gm_response":
                    history_text.append(f"GM: {item['content'][:100]}...")
            
            if history_text:
                context["recent_history"] = "\n".join(history_text)
        
        # Add current world state summary
        if self.current_adventure:
            world_state = self.state_manager.get_world_state(self.current_adventure)
            if world_state:
                # Extract key state info
                state_summary = {}
                if "current_location" in world_state:
                    state_summary["location"] = world_state["current_location"]
                
                # Add any flags or important state
                for key in ["flags", "variables", "triggers"]:
                    if key in world_state:
                        state_summary[key] = world_state[key]
                
                if state_summary:
                    context["state"] = state_summary
        
        return context
    
    async def process_directive(self, directive: Dict[str, str]) -> Optional[Dict]:
        """
        Process a directive from DeepSeek.
        Returns result dict for feedback to DeepSeek.
        """
        directive_type = directive["type"]
        parameters = directive["parameters"]
        
        print(f"Processing directive: {directive_type}: {parameters}")
        
        if directive_type == "REQUEST_ROLL":
            # Parse dice notation
            try:
                result = self.dice_roller.roll(parameters)
                self.stats["dice_rolled"] += 1
                
                # Post to Discord
                if self.discord_bridge:
                    await self.discord_bridge.post_dice_result(
                        result, 
                        "GM roll"
                    )
                
                return {
                    "type": "roll_result",
                    "result": result["total"],
                    "details": result["details"],
                    "notation": parameters
                }
                
            except ValueError as e:
                print(f"Error rolling dice: {e}")
                return {
                    "type": "error",
                    "message": f"Invalid dice notation: {parameters}"
                }
        
        elif directive_type == "UPDATE_STATE":
            # Format: "field.path, value"
            if self.current_adventure:
                try:
                    # Parse field and value
                    if "," in parameters:
                        field, value = parameters.split(",", 1)
                        field = field.strip()
                        value = value.strip()
                        
                        # Try to parse value as appropriate type
                        try:
                            if value.lower() == "true":
                                value = True
                            elif value.lower() == "false":
                                value = False
                            elif value.isdigit():
                                value = int(value)
                            elif value.replace('.', '', 1).isdigit():
                                value = float(value)
                        except:
                            pass  # Keep as string
                        
                        success = self.state_manager.update_world_state(
                            self.current_adventure, field, value
                        )
                        
                        return {
                            "type": "state_updated",
                            "field": field,
                            "value": value,
                            "success": success
                        }
                    else:
                        return {
                            "type": "error",
                            "message": f"Invalid UPDATE_STATE format: {parameters}"
                        }
                        
                except Exception as e:
                    print(f"Error updating state: {e}")
                    return {
                        "type": "error",
                        "message": f"Error updating state: {e}"
                    }
            else:
                return {
                    "type": "error",
                    "message": "No adventure loaded"
                }
        
        elif directive_type == "UPDATE_CHARACTER":
            # Format: "character_name, field.path, value"
            if "," in parameters:
                parts = parameters.split(",", 2)
                if len(parts) == 3:
                    character, field, value = parts
                    character = character.strip()
                    field = field.strip()
                    value = value.strip()
                    
                    # Try to parse value
                    try:
                        if value.lower() == "true":
                            value = True
                        elif value.lower() == "false":
                            value = False
                        elif value.isdigit():
                            value = int(value)
                        elif value.replace('.', '', 1).isdigit():
                            value = float(value)
                    except:
                        pass
                    
                    success = self.state_manager.update_character(character, field, value)
                    
                    return {
                        "type": "character_updated",
                        "character": character,
                        "field": field,
                        "value": value,
                        "success": success
                    }
            
            return {
                "type": "error",
                "message": f"Invalid UPDATE_CHARACTER format: {parameters}"
            }
        
        elif directive_type == "MOVE_SCENE":
            # Format: "location_id"
            location_id = parameters.strip()
            
            if self.current_adventure and self.current_scene:
                success = self.state_manager.move_scene(
                    self.current_adventure, self.current_scene, location_id
                )
                
                if success:
                    self.current_scene = location_id
                    # Load new scene data
                    scene_data = self.state_manager.get_scene_data(
                        self.current_adventure, location_id
                    )
                    
                    return {
                        "type": "scene_moved",
                        "from": self.current_scene,
                        "to": location_id,
                        "success": True,
                        "scene_data": scene_data
                    }
            
            return {
                "type": "error",
                "message": f"Failed to move to scene: {location_id}"
            }
        
        else:
            return {
                "type": "error",
                "message": f"Unknown directive type: {directive_type}"
            }
    
    async def process_player_message(self, player_message: str, context: Dict) -> str:
        """
        Process a player message through the full pipeline:
        1. Generate DeepSeek response with directives
        2. Process directives
        3. Refine prose
        4. Return final narrative
        """
        # Generate DeepSeek response
        raw_response = self.deepseek.generate_gm_response(player_message, context)
        
        # Extract directives
        directives = self.deepseek.extract_directives(raw_response)
        
        # Process each directive and collect results
        directive_results = []
        for directive in directives:
            result = await self.process_directive(directive)
            if result:
                directive_results.append(result)
        
        # Remove directives from text for refinement
        narrative_without_directives = self.deepseek.remove_directives(raw_response)
        
        # Add directive results to context for refinement
        refinement_context = context.copy()
        if directive_results:
            refinement_context["directive_results"] = directive_results
        
        # Two-stage prose refinement
        refined_narrative = self.prose_refiner.refine(
            narrative_without_directives, 
            refinement_context
        )
        
        # Record in history
        self.recent_history.append({
            "type": "gm_response",
            "content": refined_narrative,
            "timestamp": datetime.now().isoformat(),
            "directives_processed": len(directives)
        })
        
        # Trim history
        if len(self.recent_history) > 20:
            self.recent_history = self.recent_history[-20:]
        
        self.stats["turns_processed"] += 1
        
        return refined_narrative
    
    async def runtime_loop(self):
        """Main runtime loop - processes messages from queue"""
        print("Starting AI GM runtime loop...")
        self.is_running = True
        
        while self.is_running:
            if self.is_paused:
                # Wait while paused
                await asyncio.sleep(1)
                continue
            
            try:
                # Wait for next message with timeout
                try:
                    message_data = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                if message_data["type"] == "player_message":
                    print(f"Processing message from {message_data['author']}: {message_data['content'][:50]}...")
                    
                    # Build current context
                    context = self.build_context()
                    
                    # Process through pipeline
                    refined_narrative = await self.process_player_message(
                        message_data["content"], 
                        context
                    )
                    
                    # Post to Discord
                    if self.discord_bridge:
                        await self.discord_bridge.post_gm_narrative(
                            refined_narrative,
                            {"location": self.current_scene}
                        )
                        self.stats["messages_sent"] += 1
                    
                    # Mark task as done
                    self.message_queue.task_done()
                    
            except Exception as e:
                print(f"Error in runtime loop: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(1)  # Prevent tight error loop
    
    async def run(self):
        """Main entry point - runs the complete system"""
        print("=" * 60)
        print("AI TTRPG Game Master System")
        print("=" * 60)
        
        # Initialize Discord
        print("Initializing Discord bridge...")
        await self.initialize_discord()
        
        # Start Discord bridge in background
        discord_task = asyncio.create_task(self.discord_bridge.start())
        
        # Wait for Discord connection
        await asyncio.sleep(2)
        
        if not self.discord_bridge.is_connected:
            print("Warning: Discord not connected, continuing anyway...")
        
        # Load adventure if specified
        if len(sys.argv) > 1:
            adventure_name = sys.argv[1]
            if self.load_adventure(adventure_name):
                print(f"Adventure loaded: {adventure_name}")
            else:
                print(f"Failed to load adventure: {adventure_name}")
                print("Please specify a valid adventure name.")
                print("Available adventures:", self.state_manager.list_adventures())
        else:
            # List available adventures
            adventures = self.state_manager.list_adventures()
            if adventures:
                print("Available adventures:")
                for adv in adventures:
                    print(f"  - {adv}")
                print("\nUsage: python main.py <adventure_name>")
            else:
                print("No adventures found. Please add adventure PDFs to data/adventures/")
                print("Then run: python -m agents.pdf_ingestor to process them.")
        
        # Start runtime loop
        print("\nStarting runtime loop...")
        print("System ready. Waiting for player messages in Discord.")
        print("Commands: !override (pause), !resume (continue)")
        print("-" * 60)
        
        try:
            # Run runtime loop
            runtime_task = asyncio.create_task(self.runtime_loop())
            
            # Wait for both tasks
            await asyncio.gather(discord_task, runtime_task)
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.is_running = False
            
            # Stop Discord
            if self.discord_bridge:
                await self.discord_bridge.stop()
            
            # Print statistics
            self.print_statistics()
            
        except Exception as e:
            print(f"Fatal error: {e}")
            import traceback
            traceback.print_exc()
            
            # Cleanup
            self.is_running = False
            if self.discord_bridge:
                await self.discord_bridge.stop()
    
    def print_statistics(self):
        """Print system statistics"""
        print("\n" + "=" * 60)
        print("SYSTEM STATISTICS")
        print("=" * 60)
        print(f"Runtime: {self.stats['start_time']} to {datetime.now().isoformat()}")
        print(f"Turns processed: {self.stats['turns_processed']}")
        print(f"Dice rolled: {self.stats['dice_rolled']}")
        print(f"Messages sent: {self.stats['messages_sent']}")
        
        # Token usage
        token_usage = self.deepseek.get_token_usage()
        print(f"DeepSeek tokens used: {token_usage['total_tokens']:,}")
        print(f"Conversations: {token_usage['conversation_count']}")
        
        # State statistics
        state_stats = self.state_manager.get_stats()
        print(f"World states: {state_stats['world_states']}")
        print(f"Characters: {state_stats['characters']}")
        
        print("=" * 60)

async def main():
    """Main entry point"""
    try:
        gm = AIGameMaster()
        await gm.run()
    except RuntimeError as e:
        print(f"Failed to start: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Set up signal handlers for clean shutdown
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        loop.close()

# ===== UTILITY FUNCTIONS =====

def import_adventure(pdf_path: str, adventure_name: str):
    """
    Utility function to import an adventure PDF.
    Run from command line: python main.py --import <pdf_path> <adventure_name>
    """
    from agents.pdf_ingestor import PDFIngestor
    
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return False
    
    ingestor = PDFIngestor()
    
    print(f"Extracting adventure from: {pdf_path.name}")
    adventure = ingestor.extract_adventure_structure(pdf_path)
    
    # Save to world_state directory
    output_path = Path(__file__).parent / "data" / "world_state" / f"{adventure_name}.json"
    ingestor.save_adventure_json(adventure, output_path)
    
    print(f"Adventure saved to: {output_path}")
    return True

def import_character(pdf_path: str, character_name: str):
    """
    Utility function to import a character sheet PDF.
    Note: This is a placeholder - character sheet parsing is complex.
    For now, creates a template character file.
    """
    # Create template character
    template = {
        "name": character_name,
        "class": "Adventurer",
        "level": 1,
        "hp": {
            "current": 10,
            "max": 10
        },
        "abilities": {
            "str": 10,
            "dex": 10,
            "con": 10,
            "int": 10,
            "wis": 10,
            "cha": 10
        },
        "inventory": [],
        "conditions": [],
        "spell_slots": {},
        "notes": f"Imported from {pdf_path}"
    }
    
    output_path = Path(__file__).parent / "data" / "characters" / f"{character_name}.json"
    
    with open(output_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"Character template created: {output_path}")
    print("Note: Manual editing required for accurate stats.")
    return True

# Command line interface
if __name__ == "__main__" and len(sys.argv) > 1:
    if sys.argv[1] == "--import":
        if len(sys.argv) >= 4:
            pdf_path = sys.argv[2]
            adventure_name = sys.argv[3]
            import_adventure(pdf_path, adventure_name)
        else:
            print("Usage: python main.py --import <pdf_path> <adventure_name>")
    elif sys.argv[1] == "--import-character":
        if len(sys.argv) >= 4:
            pdf_path = sys.argv[2]
            character_name = sys.argv[3]
            import_character(pdf_path, character_name)
        else:
            print("Usage: python main.py --import-character <pdf_path> <character_name>")
    elif sys.argv[1] == "--list":
        # Quick list of available data
        data_dir = Path(__file__).parent / "data"
        print("Adventures:", list((data_dir / "world_state").glob("*.json")))
        print("Characters:", list((data_dir / "characters").glob("*.json")))
    else:
        # Normal run
        asyncio.run(main())

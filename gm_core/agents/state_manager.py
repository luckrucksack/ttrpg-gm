#!/usr/bin/env python3
"""
State manager for world state and character tracking.
JSONs are ground truth - if DeepSeek conflicts with JSON, JSON wins.
State updates happen immediately when triggered.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import threading

class StateManager:
    """Manages world state and character state with immediate persistence"""
    
    def __init__(self, base_data_dir: Path):
        self.base_data_dir = Path(base_data_dir)
        self.world_state_dir = self.base_data_dir / "world_state"
        self.characters_dir = self.base_data_dir / "characters"
        
        # Ensure directories exist
        self.world_state_dir.mkdir(exist_ok=True, parents=True)
        self.characters_dir.mkdir(exist_ok=True, parents=True)
        
        # In-memory cache
        self.world_states = {}  # adventure_name -> state dict
        self.characters = {}    # character_name -> character dict
        
        # Lock for thread safety
        self.lock = threading.RLock()
        
        # Load existing data
        self._load_all_states()
    
    def _load_all_states(self):
        """Load all existing world states and characters"""
        # Load world states
        for json_file in self.world_state_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    state = json.load(f)
                    adventure_name = json_file.stem
                    self.world_states[adventure_name] = state
                    print(f"Loaded world state: {adventure_name}")
            except Exception as e:
                print(f"Error loading world state {json_file}: {e}")
        
        # Load characters
        for json_file in self.characters_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    character = json.load(f)
                    character_name = json_file.stem
                    self.characters[character_name] = character
                    print(f"Loaded character: {character_name}")
            except Exception as e:
                print(f"Error loading character {json_file}: {e}")
    
    # ===== WORLD STATE METHODS =====
    
    def create_world_state(self, adventure_name: str, initial_state: Dict) -> bool:
        """Create a new world state for an adventure"""
        with self.lock:
            if adventure_name in self.world_states:
                print(f"World state already exists: {adventure_name}")
                return False
            
            # Add metadata
            state_with_meta = {
                **initial_state,
                "_metadata": {
                    "created": datetime.now().isoformat(),
                    "adventure_name": adventure_name,
                    "version": 1
                }
            }
            
            self.world_states[adventure_name] = state_with_meta
            return self._save_world_state(adventure_name)
    
    def get_world_state(self, adventure_name: str) -> Optional[Dict]:
        """Get world state for an adventure"""
        with self.lock:
            return self.world_states.get(adventure_name)
    
    def update_world_state(self, adventure_name: str, field_path: str, value: Any) -> bool:
        """
        Update a field in world state immediately.
        Field path can be dot notation: "rooms.room1.monsters.goblin.hp"
        """
        with self.lock:
            if adventure_name not in self.world_states:
                print(f"World state not found: {adventure_name}")
                return False
            
            state = self.world_states[adventure_name]
            
            # Navigate to the field
            parts = field_path.split('.')
            current = state
            
            # Navigate to parent
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Update the field
            last_part = parts[-1]
            current[last_part] = value
            
            # Update metadata
            if "_metadata" in state:
                state["_metadata"]["last_updated"] = datetime.now().isoformat()
                state["_metadata"]["version"] = state["_metadata"].get("version", 1) + 1
            
            # Save immediately
            return self._save_world_state(adventure_name)
    
    def update_world_state_bulk(self, adventure_name: str, updates: Dict[str, Any]) -> bool:
        """Update multiple fields in world state at once"""
        with self.lock:
            if adventure_name not in self.world_states:
                print(f"World state not found: {adventure_name}")
                return False
            
            state = self.world_states[adventure_name]
            
            for field_path, value in updates.items():
                parts = field_path.split('.')
                current = state
                
                # Navigate to parent
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Update the field
                last_part = parts[-1]
                current[last_part] = value
            
            # Update metadata
            if "_metadata" in state:
                state["_metadata"]["last_updated"] = datetime.now().isoformat()
                state["_metadata"]["version"] = state["_metadata"].get("version", 1) + 1
            
            # Save immediately
            return self._save_world_state(adventure_name)
    
    def get_scene_data(self, adventure_name: str, location_id: str) -> Optional[Dict]:
        """Get data for a specific scene/location"""
        with self.lock:
            if adventure_name not in self.world_states:
                return None
            
            state = self.world_states[adventure_name]
            
            # Look for location in various possible structures
            locations_to_check = [
                f"rooms.{location_id}",
                f"locations.{location_id}",
                f"scenes.{location_id}",
                location_id  # Direct key
            ]
            
            for location_path in locations_to_check:
                parts = location_path.split('.')
                current = state
                
                try:
                    for part in parts:
                        current = current[part]
                    return current
                except (KeyError, TypeError):
                    continue
            
            return None
    
    def move_scene(self, adventure_name: str, from_location: str, to_location: str) -> bool:
        """Move from one scene to another, updating state"""
        with self.lock:
            if adventure_name not in self.world_states:
                return False
            
            state = self.world_states[adventure_name]
            
            # Update current location
            if "current_location" not in state:
                state["current_location"] = {}
            
            state["current_location"]["id"] = to_location
            state["current_location"]["previous"] = from_location
            state["current_location"]["moved_at"] = datetime.now().isoformat()
            
            # Save immediately
            return self._save_world_state(adventure_name)
    
    # ===== CHARACTER METHODS =====
    
    def create_character(self, character_name: str, character_data: Dict) -> bool:
        """Create a new character"""
        with self.lock:
            if character_name in self.characters:
                print(f"Character already exists: {character_name}")
                return False
            
            # Add metadata
            char_with_meta = {
                **character_data,
                "_metadata": {
                    "created": datetime.now().isoformat(),
                    "character_name": character_name,
                    "version": 1
                }
            }
            
            self.characters[character_name] = char_with_meta
            return self._save_character(character_name)
    
    def get_character(self, character_name: str) -> Optional[Dict]:
        """Get character data"""
        with self.lock:
            return self.characters.get(character_name)
    
    def update_character(self, character_name: str, field_path: str, value: Any) -> bool:
        """
        Update a character field immediately.
        Field path can be dot notation: "hp.current" or "inventory.0.quantity"
        """
        with self.lock:
            if character_name not in self.characters:
                print(f"Character not found: {character_name}")
                return False
            
            character = self.characters[character_name]
            
            # Navigate to the field
            parts = field_path.split('.')
            current = character
            
            # Navigate to parent
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Update the field
            last_part = parts[-1]
            current[last_part] = value
            
            # Update metadata
            if "_metadata" in character:
                character["_metadata"]["last_updated"] = datetime.now().isoformat()
                character["_metadata"]["version"] = character["_metadata"].get("version", 1) + 1
            
            # Save immediately
            return self._save_character(character_name)
    
    def update_character_hp(self, character_name: str, change: int) -> bool:
        """Update character HP (positive for healing, negative for damage)"""
        with self.lock:
            if character_name not in self.characters:
                return False
            
            character = self.characters[character_name]
            
            # Get current HP
            current_hp = character.get("hp", {}).get("current", 0)
            max_hp = character.get("hp", {}).get("max", 0)
            
            # Calculate new HP
            new_hp = current_hp + change
            new_hp = max(0, min(new_hp, max_hp))  # Clamp between 0 and max
            
            # Update
            if "hp" not in character:
                character["hp"] = {}
            
            character["hp"]["current"] = new_hp
            character["hp"]["last_updated"] = datetime.now().isoformat()
            
            # Add to history if significant change
            if change != 0:
                if "hp_history" not in character:
                    character["hp_history"] = []
                
                character["hp_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "change": change,
                    "from": current_hp,
                    "to": new_hp,
                    "reason": "combat" if change < 0 else "healing"
                })
            
            # Update metadata
            if "_metadata" in character:
                character["_metadata"]["last_updated"] = datetime.now().isoformat()
                character["_metadata"]["version"] = character["_metadata"].get("version", 1) + 1
            
            # Save immediately
            return self._save_character(character_name)
    
    def add_character_condition(self, character_name: str, condition: str) -> bool:
        """Add a condition to a character"""
        with self.lock:
            if character_name not in self.characters:
                return False
            
            character = self.characters[character_name]
            
            if "conditions" not in character:
                character["conditions"] = []
            
            if condition not in character["conditions"]:
                character["conditions"].append(condition)
                
                # Update metadata
                if "_metadata" in character:
                    character["_metadata"]["last_updated"] = datetime.now().isoformat()
                    character["_metadata"]["version"] = character["_metadata"].get("version", 1) + 1
                
                # Save immediately
                return self._save_character(character_name)
            
            return True  # Condition already present
    
    def remove_character_condition(self, character_name: str, condition: str) -> bool:
        """Remove a condition from a character"""
        with self.lock:
            if character_name not in self.characters:
                return False
            
            character = self.characters[character_name]
            
            if "conditions" in character and condition in character["conditions"]:
                character["conditions"].remove(condition)
                
                # Update metadata
                if "_metadata" in character:
                    character["_metadata"]["last_updated"] = datetime.now().isoformat()
                    character["_metadata"]["version"] = character["_metadata"].get("version", 1) + 1
                
                # Save immediately
                return self._save_character(character_name)
            
            return True  # Condition not present
    
    def update_character_inventory(self, character_name: str, item: str, quantity: int = 1) -> bool:
        """Update character inventory"""
        with self.lock:
            if character_name not in self.characters:
                return False
            
            character = self.characters[character_name]
            
            if "inventory" not in character:
                character["inventory"] = []
            
            # Find existing item
            item_found = False
            for inv_item in character["inventory"]:
                if inv_item.get("name") == item:
                    inv_item["quantity"] = max(0, inv_item.get("quantity", 0) + quantity)
                    item_found = True
                    break
            
            # Add new item if not found and quantity > 0
            if not item_found and quantity > 0:
                character["inventory"].append({
                    "name": item,
                    "quantity": quantity,
                    "added": datetime.now().isoformat()
                })
            
            # Remove items with quantity 0
            character["inventory"] = [item for item in character["inventory"] if item.get("quantity", 0) > 0]
            
            # Update metadata
            if "_metadata" in character:
                character["_metadata"]["last_updated"] = datetime.now().isoformat()
                character["_metadata"]["version"] = character["_metadata"].get("version", 1) + 1
            
            # Save immediately
            return self._save_character(character_name)
    
    # ===== PERSISTENCE METHODS =====
    
    def _save_world_state(self, adventure_name: str) -> bool:
        """Save world state to JSON file"""
        try:
            if adventure_name not in self.world_states:
                return False
            
            file_path = self.world_state_dir / f"{adventure_name}.json"
            
            # Create backup if file exists
            if file_path.exists():
                backup_path = file_path.with_suffix('.json.bak')
                file_path.rename(backup_path)
            
            # Save with pretty formatting
            with open(file_path, 'w') as f:
                json.dump(self.world_states[adventure_name], f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving world state {adventure_name}: {e}")
            return False
    
    def _save_character(self, character_name: str) -> bool:
        """Save character to JSON file"""
        try:
            if character_name not in self.characters:
                return False
            
            file_path = self.characters_dir / f"{character_name}.json"
            
            # Create backup if file exists
            if file_path.exists():
                backup_path = file_path.with_suffix('.json.bak')
                file_path.rename(backup_path)
            
            # Save with pretty formatting
            with open(file_path, 'w') as f:
                json.dump(self.characters[character_name], f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving character {character_name}: {e}")
            return False
    
    # ===== UTILITY METHODS =====
    
    def list_adventures(self) -> List[str]:
        """List all loaded adventures"""
        with self.lock:
            return list(self.world_states.keys())
    
    def list_characters(self) -> List[str]:
        """List all loaded characters"""
        with self.lock:
            return list(self.characters.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        with self.lock:
            return {
                "world_states": len(self.world_states),
                "characters": len(self.characters),
                "world_state_dir": str(self.world_state_dir),
                "characters_dir": str(self.characters_dir)
            }
    
    def backup_all(self, backup_dir: Path) -> bool:
        """Create backup of all data"""
        try:
            backup_dir = Path(backup_dir)
            backup_dir.mkdir(exist_ok=True, parents=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Backup world states
            for adventure_name, state in self.world_states.items():
                backup_file = backup_dir / f"world_state_{adventure_name}_{timestamp}.json"
                with open(backup_file, 'w') as f:
                    json.dump(state, f, indent=2)
            
            # Backup characters
            for character_name, character in self.characters.items():
                backup_file = backup_dir / f"character_{character_name}_{timestamp}.json"
                with open(backup_file, 'w') as f:
                    json.dump(character, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

if __name__ == "__main__":
    print("State Manager Module")
    print("-" * 40)
    print("Manages world state and character state with immediate persistence.")
    print("\nKey principles:")
    print("1. JSONs are ground truth")
    print("2. State updates happen immediately")
    print("3. Thread-safe operations")
    print("\nUsage:")
    print("  manager = StateManager(Path('/path/to/data'))")
    print("  manager.update_world_state('adventure1', 'rooms.room1.monsters.goblin.hp', 5)")
    print("  manager.update_character('fighter', 'hp.current', 15)")
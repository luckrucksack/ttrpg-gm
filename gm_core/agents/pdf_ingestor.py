#!/usr/bin/env python3
"""
PDF parsing for adventure modules and character sheets.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import PyPDF2
import pdfplumber

class PDFIngestor:
    """Extract text from PDFs and structure it for the AI GM system"""
    
    def __init__(self):
        self.text_cache = {}
    
    def extract_text(self, pdf_path: Path) -> str:
        """Extract all text from PDF using multiple methods for robustness"""
        if str(pdf_path) in self.text_cache:
            return self.text_cache[str(pdf_path)]
        
        text = ""
        
        # Method 1: Try pdfplumber first (better for formatted text)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            print(f"pdfplumber failed: {e}, trying PyPDF2...")
        
        # Method 2: Fall back to PyPDF2
        if not text.strip():
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
            except Exception as e:
                print(f"PyPDF2 failed: {e}")
        
        # Cache the result
        self.text_cache[str(pdf_path)] = text
        return text
    
    def extract_adventure_structure(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract adventure structure from PDF:
        - Room descriptions
        - Read-aloud text
        - Monster stats
        - Traps
        - Treasure
        - Encounter tables
        - NPC data
        - Special rules
        """
        text = self.extract_text(pdf_path)
        
        # Initialize structure
        adventure = {
            "metadata": {
                "filename": pdf_path.name,
                "path": str(pdf_path),
                "total_pages": self.get_page_count(pdf_path)
            },
            "rooms": {},
            "monsters": {},
            "npcs": {},
            "traps": {},
            "treasure": {},
            "encounters": {},
            "read_aloud": {},
            "special_rules": {}
        }
        
        # Parse rooms (look for room numbers, locations)
        rooms = self._extract_rooms(text)
        adventure["rooms"] = rooms
        
        # Parse monsters (look for stat blocks)
        monsters = self._extract_monsters(text)
        adventure["monsters"] = monsters
        
        # Parse read-aloud text (italicized or quoted text)
        read_aloud = self._extract_read_aloud(text)
        adventure["read_aloud"] = read_aloud
        
        # Parse traps (look for trap descriptions)
        traps = self._extract_traps(text)
        adventure["traps"] = traps
        
        # Parse treasure (look for treasure descriptions)
        treasure = self._extract_treasure(text)
        adventure["treasure"] = treasure
        
        # Parse NPCs (look for NPC descriptions)
        npcs = self._extract_npcs(text)
        adventure["npcs"] = npcs
        
        return adventure
    
    def _extract_rooms(self, text: str) -> Dict[str, str]:
        """Extract room descriptions"""
        rooms = {}
        
        # Look for patterns like "Room 1:", "Area A:", "Chamber 3"
        room_patterns = [
            r'(?:Room|Area|Chamber|Location)\s+(\d+|[A-Z]):?\s*(.*?)(?=(?:Room|Area|Chamber|Location)\s+(\d+|[A-Z])|$)',
            r'(\d+)\.[\s]*(.*?)(?=\d+\.|$)'
        ]
        
        for pattern in room_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                room_id = match.group(1).strip()
                description = match.group(2).strip()
                if room_id and description:
                    rooms[room_id] = description
        
        return rooms
    
    def _extract_monsters(self, text: str) -> Dict[str, Dict]:
        """Extract monster stat blocks"""
        monsters = {}
        
        # Look for monster names followed by stats
        # Pattern: Monster Name (CR X) ... HP: ... AC: ... etc.
        monster_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(CR\s+[\d/]+\)(.*?)(?=(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(CR|$)'
        
        matches = re.finditer(monster_pattern, text, re.DOTALL)
        for match in matches:
            name = match.group(1).strip()
            stats_text = match.group(2).strip()
            
            monster = {
                "name": name,
                "stats_text": stats_text,
                "hp": self._extract_hp(stats_text),
                "ac": self._extract_ac(stats_text),
                "abilities": self._extract_abilities(stats_text),
                "actions": self._extract_actions(stats_text)
            }
            
            monsters[name] = monster
        
        return monsters
    
    def _extract_read_aloud(self, text: str) -> Dict[str, str]:
        """Extract read-aloud text (italicized or in quotes)"""
        read_aloud = {}
        
        # Look for italicized text (often read-aloud in PDFs)
        italic_pattern = r'\*(.*?)\*'
        matches = re.finditer(italic_pattern, text)
        
        for i, match in enumerate(matches, 1):
            read_aloud[f"read_aloud_{i}"] = match.group(1).strip()
        
        # Look for quoted text
        quote_pattern = r'"(.*?)"'
        matches = re.finditer(quote_pattern, text)
        
        for i, match in enumerate(len(read_aloud) + 1, 1):
            read_aloud[f"read_aloud_{i}"] = match.group(1).strip()
        
        return read_aloud
    
    def _extract_traps(self, text: str) -> Dict[str, Dict]:
        """Extract trap descriptions"""
        traps = {}
        
        # Look for trap descriptions
        trap_pattern = r'(?:Trap|Hazard):?\s*(.*?)(?=(?:Trap|Hazard):|\.\s+[A-Z]|$)'
        matches = re.finditer(trap_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for i, match in enumerate(matches, 1):
            description = match.group(1).strip()
            if description:
                trap_id = f"trap_{i}"
                traps[trap_id] = {
                    "description": description,
                    "triggers": self._extract_trap_triggers(description),
                    "effects": self._extract_trap_effects(description),
                    "dc": self._extract_dc(description)
                }
        
        return traps
    
    def _extract_treasure(self, text: str) -> Dict[str, Dict]:
        """Extract treasure descriptions"""
        treasure = {}
        
        # Look for treasure descriptions
        treasure_pattern = r'(?:Treasure|Loot|Reward):?\s*(.*?)(?=(?:Treasure|Loot|Reward):|\.\s+[A-Z]|$)'
        matches = re.finditer(treasure_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for i, match in enumerate(matches, 1):
            description = match.group(1).strip()
            if description:
                treasure_id = f"treasure_{i}"
                treasure[treasure_id] = {
                    "description": description,
                    "items": self._extract_treasure_items(description),
                    "value": self._extract_treasure_value(description)
                }
        
        return treasure
    
    def _extract_npcs(self, text: str) -> Dict[str, Dict]:
        """Extract NPC descriptions"""
        npcs = {}
        
        # Look for NPC descriptions
        npc_pattern = r'(?:NPC|Non-Player Character):?\s*(.*?)(?=(?:NPC|Non-Player Character):|\.\s+[A-Z]|$)'
        matches = re.finditer(npc_pattern, text, re.IGNORECASE | re.DOTALL)
        
        for i, match in enumerate(matches, 1):
            description = match.group(1).strip()
            if description:
                npc_id = f"npc_{i}"
                npcs[npc_id] = {
                    "description": description,
                    "alignment": self._extract_alignment(description),
                    "motivation": self._extract_motivation(description)
                }
        
        return npcs
    
    # Helper extraction methods
    def _extract_hp(self, text: str) -> Optional[str]:
        match = re.search(r'HP\s*[:]?\s*(\d+)', text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_ac(self, text: str) -> Optional[str]:
        match = re.search(r'AC\s*[:]?\s*(\d+)', text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_abilities(self, text: str) -> Dict[str, str]:
        abilities = {}
        ability_pattern = r'(\w+)\s+([+-]?\d+)'
        matches = re.finditer(ability_pattern, text)
        for match in matches:
            abilities[match.group(1)] = match.group(2)
        return abilities
    
    def _extract_actions(self, text: str) -> List[str]:
        actions = []
        # Look for action descriptions
        action_matches = re.finditer(r'(?:\n|^)(\w+ Attack|Cast|Use).*?(?=\n\w|$)', text, re.DOTALL)
        for match in action_matches:
            actions.append(match.group(0).strip())
        return actions
    
    def _extract_trap_triggers(self, text: str) -> List[str]:
        triggers = []
        # Simple trigger extraction
        if "when" in text.lower():
            parts = text.lower().split("when")
            if len(parts) > 1:
                triggers.append(parts[1].split(".")[0].strip())
        return triggers
    
    def _extract_trap_effects(self, text: str) -> List[str]:
        effects = []
        # Look for damage or effect descriptions
        damage_match = re.search(r'(\d+d\d+[+-]?\d*)\s*(?:damage|points)', text, re.IGNORECASE)
        if damage_match:
            effects.append(f"Damage: {damage_match.group(1)}")
        return effects
    
    def _extract_dc(self, text: str) -> Optional[str]:
        match = re.search(r'DC\s*(\d+)', text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_treasure_items(self, text: str) -> List[str]:
        items = []
        # Look for item lists
        item_matches = re.finditer(r'(\d+)\s+(gp|sp|cp|gold|silver|copper|[a-z]+)', text, re.IGNORECASE)
        for match in item_matches:
            items.append(match.group(0).strip())
        return items
    
    def _extract_treasure_value(self, text: str) -> Optional[str]:
        match = re.search(r'(\d+)\s*(gp|gold)', text, re.IGNORECASE)
        return match.group(0) if match else None
    
    def _extract_alignment(self, text: str) -> Optional[str]:
        alignments = ["Lawful Good", "Neutral Good", "Chaotic Good", 
                     "Lawful Neutral", "True Neutral", "Chaotic Neutral",
                     "Lawful Evil", "Neutral Evil", "Chaotic Evil"]
        for alignment in alignments:
            if alignment.lower() in text.lower():
                return alignment
        return None
    
    def _extract_motivation(self, text: str) -> Optional[str]:
        # Simple motivation extraction
        motivation_keywords = ["wants", "desires", "seeks", "motivated by", "goal is"]
        for keyword in motivation_keywords:
            if keyword in text.lower():
                # Extract the phrase after the keyword
                start = text.lower().find(keyword) + len(keyword)
                end = text.find(".", start)
                if end == -1:
                    end = len(text)
                return text[start:end].strip()
        return None
    
    def get_page_count(self, pdf_path: Path) -> int:
        """Get number of pages in PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except:
            return 0
    
    def save_adventure_json(self, adventure: Dict, output_path: Path):
        """Save adventure structure to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(adventure, f, indent=2)
    
    def load_adventure_json(self, json_path: Path) -> Dict:
        """Load adventure structure from JSON file"""
        with open(json_path, 'r') as f:
            return json.load(f)

if __name__ == "__main__":
    # Test the PDF ingestor
    ingestor = PDFIngestor()
    
    # Create a test directory if it doesn't exist
    test_dir = Path(__file__).resolve().parent.parent / "campaigns" / "dying_earth" / "adventures"
    test_dir.mkdir(exist_ok=True)
    
    print("PDF Ingestor Test")
    print("-" * 40)
    print("Note: This is a demonstration. To test with actual PDFs,")
    print("place adventure PDFs in:", test_dir)
    print("\nAvailable methods:")
    print("1. extract_adventure_structure(pdf_path)")
    print("2. save_adventure_json(adventure, output_path)")
    print("3. load_adventure_json(json_path)")
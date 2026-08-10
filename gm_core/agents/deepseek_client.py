#!/usr/bin/env python3
"""
DeepSeek API client for AI GM system.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

class DeepSeekClient:
    """Client for DeepSeek API interactions"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = base_url or "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
        self.conversation_history = []
        self.total_tokens_used = 0
        
        if not self.api_key:
            raise ValueError("DeepSeek API key not provided. Set DEEPSEEK_API_KEY environment variable.")
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       temperature: float = 0.7,
                       max_tokens: int = 2000,
                       system_message: Optional[str] = None) -> str:
        """
        Send chat completion request to DeepSeek API.
        
        Args:
            messages: List of message dicts with "role" and "content"
            temperature: Creativity parameter (0.0-1.0)
            max_tokens: Maximum tokens in response
            system_message: Optional system message to prepend
        
        Returns:
            Assistant's response text
        """
        # Prepare messages with optional system message
        api_messages = []
        if system_message:
            api_messages.append({"role": "system", "content": system_message})
        api_messages.extend(messages)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract response
            assistant_message = data["choices"][0]["message"]["content"]
            
            # Track token usage
            usage = data.get("usage", {})
            self.total_tokens_used += usage.get("total_tokens", 0)
            
            # Record in history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "messages": messages,
                "response": assistant_message,
                "usage": usage,
                "temperature": temperature
            })
            
            return assistant_message.strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid API response: {e}")
    
    def prime_with_adventure(self, adventure_text: str, system_rules: str) -> None:
        """
        Prime DeepSeek with adventure text and system rules.
        This should be called before the first player message.
        """
        system_message = f"""You are an expert Dungeon Master running a published adventure. Your role is to:
1. Narrate the world based on the adventure text
2. Respond to player actions within the rules
3. Track game state through directives
4. Create immersive, engaging experiences

ADVENTURE TEXT:
{adventure_text}

SYSTEM RULES:
{system_rules}

DIRECTIVE FORMAT:
When you need the system to perform an action, use these directives:
- [REQUEST_ROLL: NdX+modifier] - Request a dice roll
- [UPDATE_STATE: field, value] - Update world state
- [UPDATE_CHARACTER: character, field, value] - Update character sheet
- [MOVE_SCENE: location_id] - Move to new location

Your responses should include narrative text and directives as needed.
Always maintain consistency with the adventure text and system rules."""
        
        # Store the primed system message for future use
        self.primed_system_message = system_message
    
    def generate_gm_response(self, 
                            player_message: str,
                            context: Dict[str, Any],
                            include_directives: bool = True) -> str:
        """
        Generate GM response based on player message and context.
        
        Args:
            player_message: The player's message/action
            context: Current game context (scene, characters, etc.)
            include_directives: Whether to include directives in response
        
        Returns:
            GM response text (may include directives)
        """
        # Build context description
        context_text = self._build_context_text(context)
        
        # Prepare messages
        messages = []
        
        # Add system message if primed
        if hasattr(self, 'primed_system_message'):
            messages.append({"role": "system", "content": self.primed_system_message})
        
        # Add context
        messages.append({
            "role": "system", 
            "content": f"CURRENT CONTEXT:\n{context_text}"
        })
        
        # Add player message
        messages.append({
            "role": "user",
            "content": player_message
        })
        
        # Add instruction about directives
        if include_directives:
            directive_instruction = "\n\nInclude directives in your response when needed (e.g., [REQUEST_ROLL: 1d20+5])."
            if messages[-1]["role"] == "user":
                messages[-1]["content"] += directive_instruction
            else:
                messages.append({"role": "system", "content": directive_instruction})
        
        # Generate response
        response = self.chat_completion(
            messages=messages,
            temperature=0.8,  # Creative but consistent
            max_tokens=1500
        )
        
        return response
    
    def _build_context_text(self, context: Dict[str, Any]) -> str:
        """Build readable context text from context dict"""
        parts = []
        
        # Scene/Location
        if "scene" in context:
            parts.append(f"SCENE: {context['scene']}")
        if "location" in context:
            parts.append(f"LOCATION: {context['location']}")
        
        # Characters
        if "characters" in context and context["characters"]:
            char_info = []
            for char in context["characters"]:
                char_str = char.get("name", "Unknown")
                if "hp" in char:
                    char_str += f" (HP: {char['hp']})"
                if "conditions" in char and char["conditions"]:
                    char_str += f" [{', '.join(char['conditions'])}]"
                char_info.append(char_str)
            parts.append(f"CHARACTERS: {', '.join(char_info)}")
        
        # Monsters/NPCs
        if "monsters" in context and context["monsters"]:
            monster_info = []
            for monster in context["monsters"]:
                monster_str = monster.get("name", "Unknown")
                if "hp" in monster:
                    monster_str += f" (HP: {monster['hp']})"
                monster_info.append(monster_str)
            parts.append(f"MONSTERS: {', '.join(monster_info)}")
        
        # Recent history
        if "recent_history" in context and context["recent_history"]:
            parts.append(f"RECENT HISTORY:\n{context['recent_history']}")
        
        # Current state
        if "state" in context:
            state_items = []
            for key, value in context["state"].items():
                if isinstance(value, (str, int, float, bool)):
                    state_items.append(f"{key}: {value}")
            if state_items:
                parts.append(f"STATE: {', '.join(state_items)}")
        
        return "\n".join(parts)
    
    def extract_directives(self, text: str) -> List[Dict[str, str]]:
        """
        Extract directives from GM response text.
        Returns list of dicts with "type" and "parameters".
        """
        directives = []
        
        # Pattern for directives: [TYPE: parameters]
        pattern = r'\[([A-Z_]+):\s*(.*?)\]'
        
        matches = re.finditer(pattern, text)
        for match in matches:
            directive_type = match.group(1)
            parameters = match.group(2).strip()
            
            directives.append({
                "type": directive_type,
                "parameters": parameters,
                "raw": match.group(0),
                "position": match.start()
            })
        
        return directives
    
    def remove_directives(self, text: str) -> str:
        """Remove directive markers from text, leaving clean narrative"""
        # Remove directive brackets but keep the text inside
        cleaned = re.sub(r'\[([A-Z_]+):\s*(.*?)\]', r'\2', text)
        return cleaned.strip()
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        self.total_tokens_used = 0
    
    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage statistics"""
        return {
            "total_tokens": self.total_tokens_used,
            "conversation_count": len(self.conversation_history)
        }

if __name__ == "__main__":
    print("DeepSeek Client Module")
    print("-" * 40)
    print("This module handles all DeepSeek API interactions.")
    print("\nKey features:")
    print("1. Chat completion with context management")
    print("2. Adventure priming (system context)")
    print("3. Directive extraction and removal")
    print("4. Token usage tracking")
    print("\nEnvironment variable needed:")
    print("  DEEPSEEK_API_KEY=your_api_key_here")
    print("\nUsage:")
    print("  client = DeepSeekClient()")
    print("  response = client.generate_gm_response(player_message, context)")
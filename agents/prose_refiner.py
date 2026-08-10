#!/usr/bin/env python3
"""
Two-stage prose refinement for AI GM output.
Raw DeepSeek output never reaches players.
"""

import re
from typing import Dict, Optional
from .deepseek_client import DeepSeekClient

class ProseRefiner:
    """
    Two-stage refinement:
    1. Dialectic Removal - remove contrastive/antithesis structures
    2. Literary Rewrite - improve pacing, sensory specificity, tone
    """
    
    def __init__(self, deepseek_client: DeepSeekClient):
        self.deepseek = deepseek_client
        self.refinement_history = []
    
    def refine(self, raw_text: str, context: Optional[Dict] = None) -> str:
        """
        Run both refinement stages on raw DeepSeek output.
        Returns refined text ready for Discord.
        """
        if context is None:
            context = {}
        
        # Stage 1: Dialectic Removal
        stage1_text = self._stage1_dialectic_removal(raw_text)
        
        # Stage 2: Literary Rewrite
        stage2_text = self._stage2_literary_rewrite(stage1_text, context)
        
        # Record in history
        self.refinement_history.append({
            "raw": raw_text,
            "stage1": stage1_text,
            "stage2": stage2_text,
            "context": context
        })
        
        return stage2_text
    
    def _stage1_dialectic_removal(self, text: str) -> str:
        """
        Stage 1: Remove contrastive/antithesis structures.
        Instructions to DeepSeek:
        "Identify every contrastive or antithesis structure in this text — 
        constructions such as 'It's not A, it's B,' 'Not just X, but Y,' 
        or any pattern that negates or diminishes something in order to 
        elevate something else. Rewrite each instance as a direct affirmative 
        statement. Change nothing else. Return only the rewritten text."
        """
        prompt = f"""Identify every contrastive or antithesis structure in this text — constructions such as "It's not A, it's B," "Not just X, but Y," or any pattern that negates or diminishes something in order to elevate something else. Rewrite each instance as a direct affirmative statement. Change nothing else. Return only the rewritten text.

Text to refine:
{text}"""
        
        try:
            response = self.deepseek.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=len(text) + 500
            )
            return response.strip()
        except Exception as e:
            print(f"Stage 1 refinement failed: {e}")
            # Fallback: simple dialectic removal
            return self._simple_dialectic_removal(text)
    
    def _stage2_literary_rewrite(self, text: str, context: Dict) -> str:
        """
        Stage 2: Literary rewrite for pacing, sensory specificity, tone.
        Instructions to DeepSeek:
        "You are a literary editor working on atmospheric fiction. 
        Rewrite this passage for pacing, sensory specificity, tonal consistency, 
        and immersive detail. It should read like skilled prose, not chatbot output. 
        Preserve all game-mechanical facts exactly. Return only the rewritten passage."
        """
        # Build context description
        context_desc = self._build_context_description(context)
        
        prompt = f"""You are a literary editor working on atmospheric fiction. Rewrite this passage for pacing, sensory specificity, tonal consistency, and immersive detail. It should read like skilled prose, not chatbot output. Preserve all game-mechanical facts exactly. Return only the rewritten passage.

Context: {context_desc}

Passage to rewrite:
{text}"""
        
        try:
            response = self.deepseek.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=len(text) + 1000
            )
            return response.strip()
        except Exception as e:
            print(f"Stage 2 refinement failed: {e}")
            return text  # Return Stage 1 text as fallback
    
    def _simple_dialectic_removal(self, text: str) -> str:
        """
        Simple regex-based dialectic removal (fallback when API fails).
        Removes common contrastive patterns.
        """
        # Common dialectic patterns
        patterns = [
            # "It's not A, it's B"
            (r'[Ii]t\'s not (\w+), it\'s (\w+)', r'It is \2'),
            # "Not just X, but Y"
            (r'[Nn]ot just (\w+), but (\w+)', r'Both \1 and \2'),
            # "Not only X, but also Y"
            (r'[Nn]ot only (\w+), but also (\w+)', r'Both \1 and \2'),
            # "Less X, more Y"
            (r'[Ll]ess (\w+), more (\w+)', r'More \2'),
            # "Not X, but rather Y"
            (r'[Nn]ot (\w+), but rather (\w+)', r'\2'),
            # "Not so much X as Y"
            (r'[Nn]ot so much (\w+) as (\w+)', r'More \2 than \1'),
            # "Not X, but Y"
            (r'[Nn]ot (\w+), but (\w+)', r'\2'),
        ]
        
        refined = text
        for pattern, replacement in patterns:
            refined = re.sub(pattern, replacement, refined)
        
        return refined
    
    def _build_context_description(self, context: Dict) -> str:
        """Build a description of the current context for Stage 2"""
        parts = []
        
        if "scene" in context:
            parts.append(f"Scene: {context['scene']}")
        
        if "location" in context:
            parts.append(f"Location: {context['location']}")
        
        if "characters" in context:
            char_names = [char.get("name", "Unknown") for char in context["characters"]]
            parts.append(f"Characters present: {', '.join(char_names)}")
        
        if "mood" in context:
            parts.append(f"Mood: {context['mood']}")
        
        if "time" in context:
            parts.append(f"Time: {context['time']}")
        
        if "weather" in context:
            parts.append(f"Weather: {context['weather']}")
        
        return "; ".join(parts) if parts else "General adventure context"
    
    def get_refinement_history(self, limit: int = 5) -> list:
        """Get recent refinement history"""
        return self.refinement_history[-limit:] if self.refinement_history else []
    
    def clear_history(self):
        """Clear refinement history"""
        self.refinement_history.clear()

# Example usage
if __name__ == "__main__":
    # This requires a DeepSeekClient to be properly configured
    print("Prose Refiner Module")
    print("-" * 40)
    print("This module requires DeepSeek API access.")
    print("\nTwo-stage refinement process:")
    print("1. Dialectic Removal: Remove contrastive structures")
    print("2. Literary Rewrite: Improve prose quality")
    print("\nExample raw input:")
    print('  "It\'s not just a dark room, but a chamber filled with eerie whispers."')
    print("\nAfter Stage 1:")
    print('  "It is a chamber filled with eerie whispers."')
    print("\nAfter Stage 2:")
    print('  "The chamber stretches before you, shadows clinging to the walls like velvet. From the darkness comes the soft susurrus of whispers, too faint to decipher, yet persistent enough to raise the hairs on your neck."')
#!/usr/bin/env python3
"""
Discord listener and poster for AI GM system.
"""

import os
import asyncio
import discord
from discord.ext import commands
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import json

class DiscordBridge:
    """Bridge between Discord and the AI GM system"""
    
    def __init__(self, 
                 bot_token: Optional[str] = None,
                 game_channel_id: Optional[str] = None,
                 message_callback: Optional[Callable] = None,
                 roll_callback: Optional[Callable] = None):
        
        self.bot_token = bot_token or os.getenv("DISCORD_BOT_TOKEN", "")
        self.game_channel_id = game_channel_id or os.getenv("DISCORD_GAME_CHANNEL_ID", "")
        
        if not self.bot_token:
            raise ValueError("Discord bot token not provided. Set DISCORD_BOT_TOKEN environment variable.")
        
        if not self.game_channel_id:
            raise ValueError("Game channel ID not provided. Set DISCORD_GAME_CHANNEL_ID environment variable.")
        
        self.message_callback = message_callback
        self.roll_callback = roll_callback
        self.bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
        self.game_channel = None
        self.message_history = []
        self.is_connected = False
        
        # Set up event handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up Discord event handlers"""
        
        @self.bot.event
        async def on_ready():
            print(f"Discord bot logged in as {self.bot.user}")
            self.is_connected = True
            
            # Get game channel
            try:
                self.game_channel = self.bot.get_channel(int(self.game_channel_id))
                if self.game_channel:
                    print(f"Connected to game channel: {self.game_channel.name}")
                else:
                    print(f"Warning: Could not find channel with ID {self.game_channel_id}")
            except ValueError:
                print(f"Error: Invalid channel ID {self.game_channel_id}")
        
        @self.bot.event
        async def on_message(message):
            # Ignore bot's own messages
            if message.author == self.bot.user:
                return
            
            # Only process messages in the game channel
            if str(message.channel.id) != self.game_channel_id:
                return
            
            # Check for override commands
            if message.content.lower() == "!override":
                await self._handle_override(message)
                return
            
            if message.content.lower() == "!resume":
                await self._handle_resume(message)
                return
            
            # Record message in history
            self.message_history.append({
                "timestamp": datetime.now().isoformat(),
                "author": str(message.author),
                "content": message.content,
                "channel": str(message.channel.name)
            })
            
            # Trim history
            if len(self.message_history) > 100:
                self.message_history = self.message_history[-100:]
            
            # Check for dice rolls in player messages
            dice_result = self._extract_dice_roll(message.content)
            if dice_result and self.roll_callback:
                await self.roll_callback(dice_result, message)
            
            # Pass message to callback for processing
            if self.message_callback:
                await self.message_callback(message)
            
            # Don't process commands further
            await self.bot.process_commands(message)
    
    async def _handle_override(self, message):
        """Handle !override command - halt all operations"""
        print(f"OVERRIDE triggered by {message.author}")
        await message.channel.send("⏸️ **OVERRIDE ACTIVATED** - All operations halted. Use `!resume` to continue.")
        
        # Signal override to system (callback would handle this)
        if self.message_callback:
            await self.message_callback(message, override=True)
    
    async def _handle_resume(self, message):
        """Handle !resume command - resume operations"""
        print(f"RESUME triggered by {message.author}")
        await message.channel.send("▶️ **RESUMING** - Reconciling state and continuing...")
        
        # Signal resume to system (callback would handle this)
        if self.message_callback:
            await self.message_callback(message, resume=True)
    
    def _extract_dice_roll(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract dice roll from player message.
        Looks for patterns like "1d20+5" or "rolls 2d6".
        """
        import re
        
        # Common dice patterns
        patterns = [
            r'(\d+)d(\d+)([+-]\d+)?',  # Standard notation
            r'rolls?\s*(\d+)d(\d+)([+-]\d+)?',  # "rolls 1d20+5"
            r'\[(\d+)d(\d+)([+-]\d+)?\]',  # Bracket notation
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                num_dice = int(match.group(1))
                dice_size = int(match.group(2))
                modifier = int(match.group(3)) if match.group(3) else 0
                
                notation = f"{num_dice}d{dice_size}"
                if modifier != 0:
                    notation += f"{modifier:+d}"
                
                return {
                    "notation": notation,
                    "num_dice": num_dice,
                    "dice_size": dice_size,
                    "modifier": modifier,
                    "text": text,
                    "matched": match.group(0)
                }
        
        return None
    
    async def start(self):
        """Start the Discord bot"""
        if not self.bot_token:
            raise ValueError("Bot token not set")
        
        print("Starting Discord bot...")
        try:
            await self.bot.start(self.bot_token)
        except discord.LoginFailure:
            print("Error: Invalid bot token")
            raise
        except Exception as e:
            print(f"Error starting bot: {e}")
            raise
    
    async def stop(self):
        """Stop the Discord bot"""
        print("Stopping Discord bot...")
        await self.bot.close()
        self.is_connected = False
    
    async def post_message(self, content: str, embed: Optional[discord.Embed] = None) -> Optional[discord.Message]:
        """
        Post a message to the game channel.
        
        Args:
            content: Message text
            embed: Optional Discord embed
        
        Returns:
            The posted message object, or None if failed
        """
        if not self.game_channel:
            print("Error: Game channel not available")
            return None
        
        try:
            # Ensure content is within Discord limits
            if len(content) > 2000:
                print(f"Warning: Truncating message from {len(content)} to 2000 characters")
                content = content[:1997] + "..."
            
            message = await self.game_channel.send(content=content, embed=embed)
            
            # Record in history
            self.message_history.append({
                "timestamp": datetime.now().isoformat(),
                "author": "GM Bot",
                "content": content[:100] + "..." if len(content) > 100 else content,
                "channel": str(self.game_channel.name),
                "type": "bot_post"
            })
            
            return message
            
        except discord.HTTPException as e:
            print(f"Error posting message: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error posting message: {e}")
            return None
    
    async def post_dice_result(self, roll_result: Dict[str, Any], description: str = "") -> Optional[discord.Message]:
        """
        Post dice roll result to Discord.
        
        Args:
            roll_result: Result from dice_roller.py
            description: Optional description of the roll
        
        Returns:
            The posted message object
        """
        notation = roll_result.get("notation", "Unknown")
        total = roll_result.get("total", 0)
        details = roll_result.get("details", "")
        
        # Create embed for dice roll
        embed = discord.Embed(
            title=f"🎲 {notation}",
            description=description,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Result", value=f"**{total}**", inline=True)
        
        if details:
            embed.add_field(name="Details", value=details, inline=False)
        
        # Add footer with audit trail
        embed.set_footer(text="Local dice roller • Audit trail maintained")
        
        return await self.post_message(content="", embed=embed)
    
    async def post_gm_narrative(self, narrative: str, scene_context: Optional[Dict] = None) -> Optional[discord.Message]:
        """
        Post GM narrative to Discord.
        
        Args:
            narrative: Refined narrative text
            scene_context: Optional scene context for formatting
        
        Returns:
            The posted message object
        """
        # Format based on context
        if scene_context and "location" in scene_context:
            location = scene_context["location"]
            header = f"**{location}**\n\n"
        else:
            header = ""
        
        full_content = header + narrative
        
        # Create embed for better presentation
        embed = discord.Embed(
            description=narrative,
            color=discord.Color.dark_purple(),
            timestamp=datetime.now()
        )
        
        if scene_context:
            if "location" in scene_context:
                embed.set_author(name=scene_context["location"])
            if "mood" in scene_context:
                embed.set_footer(text=f"Mood: {scene_context['mood']}")
        
        return await self.post_message(content=header, embed=embed)
    
    def get_recent_messages(self, limit: int = 10, author: Optional[str] = None) -> List[Dict]:
        """
        Get recent messages from history.
        
        Args:
            limit: Maximum number of messages to return
            author: Filter by author name
        
        Returns:
            List of message dicts
        """
        messages = self.message_history
        
        if author:
            messages = [msg for msg in messages if msg.get("author") == author]
        
        return messages[-limit:] if messages else []
    
    def clear_message_history(self):
        """Clear message history"""
        self.message_history.clear()

# Utility function to run the bridge
async def run_discord_bridge(bot_token: str, channel_id: str, 
                            message_callback: Optional[Callable] = None,
                            roll_callback: Optional[Callable] = None):
    """
    Run the Discord bridge.
    
    Args:
        bot_token: Discord bot token
        channel_id: Game channel ID
        message_callback: Callback for player messages
        roll_callback: Callback for dice rolls
    """
    bridge = DiscordBridge(
        bot_token=bot_token,
        game_channel_id=channel_id,
        message_callback=message_callback,
        roll_callback=roll_callback
    )
    
    try:
        await bridge.start()
    except KeyboardInterrupt:
        print("\nShutting down Discord bot...")
        await bridge.stop()
    except Exception as e:
        print(f"Error running Discord bridge: {e}")
        await bridge.stop()

if __name__ == "__main__":
    print("Discord Bridge Module")
    print("-" * 40)
    print("This module handles Discord communication for the AI GM system.")
    print("\nEnvironment variables needed:")
    print("  DISCORD_BOT_TOKEN=your_bot_token_here")
    print("  DISCORD_GAME_CHANNEL_ID=your_channel_id_here")
    print("\nFeatures:")
    print("1. Listens for player messages in game channel")
    print("2. Posts GM narratives and dice results")
    print("3. Handles !override and !resume commands")
    print("4. Extracts dice rolls from player messages")
    print("\nTo test, run with callbacks:")
    print("  python3 -m agents.discord_bridge")
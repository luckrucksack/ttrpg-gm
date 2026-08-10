#!/usr/bin/env python3
"""
One-Click Play Dashboard for AI TTRPG GM System
Run with: python3 play_dashboard.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent

def print_header():
    print("=" * 60)
    print("🎮 AI TTRPG GM - ONE-CLICK PLAY DASHBOARD")
    print("=" * 60)
    print()

def check_system():
    print("🔍 System Status Check:")
    print("-" * 40)
    
    # Check DeepSeek API
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if api_key:
        print(f"✅ DeepSeek API: Configured ({api_key[:10]}...)")
    else:
        print("❌ DeepSeek API: Not configured")
        print("   Set with: export DEEPSEEK_API_KEY='your_key'")
    
    # Check characters
    chars_dir = BASE_DIR / "data" / "characters"
    if chars_dir.exists():
        char_files = list(chars_dir.glob("*.json"))
        print(f"✅ Characters: {len(char_files)} loaded")
    else:
        print("❌ Characters: No characters found")
    
    # Check adventures
    adventures_dir = BASE_DIR / "data" / "adventures"
    if adventures_dir.exists():
        adventures = []
        for ext in ['.txt', '.pdf']:
            adventures.extend(adventures_dir.glob(f"*{ext}"))
        print(f"✅ Adventures: {len(adventures)} available")
    else:
        print("❌ Adventures: No adventures found")
    
    print()

def list_adventures():
    print("📚 Available Adventures:")
    print("-" * 40)
    
    adventures = [
        ("crystal_chamber", "The Crystal Chamber", "Level 3 | 1-2 hours | Abandoned Drift station"),
        ("ghost_ship", "Ghost Ship Salvage", "Level 3 | 2-3 hours | Derelict starship"),
        ("apostae_station", "Apostae Station Blues", "Level 3 | 3-4 hours | Asteroid mining station")
    ]
    
    for i, (id, name, desc) in enumerate(adventures, 1):
        print(f"{i}. {name}")
        print(f"   📝 {desc}")
        print(f"   🎮 Command: python main.py {id}")
        print()
    
    return adventures

def list_characters():
    print("👥 Available Characters:")
    print("-" * 40)
    
    chars_dir = BASE_DIR / "data" / "characters"
    if not chars_dir.exists():
        print("No characters found")
        return []
    
    characters = []
    for char_file in chars_dir.glob("*.json"):
        try:
            with open(char_file, 'r') as f:
                char = json.load(f)
            name = char.get('name', char_file.stem)
            level = char.get('level', '?')
            hp = char.get('hp', {}).get('current', '?')
            characters.append((name, level, hp))
        except:
            characters.append((char_file.stem, '?', '?'))
    
    for i, (name, level, hp) in enumerate(characters, 1):
        print(f"{i}. {name}")
        print(f"   📊 Level {level}, HP: {hp}")
    
    print()
    return characters

def quick_start_menu():
    print("🚀 Quick Start Options:")
    print("-" * 40)
    print("1. Play 'The Crystal Chamber' (recommended for first-time)")
    print("2. Play 'Ghost Ship Salvage'")
    print("3. Play 'Apostae Station Blues'")
    print("4. Test system components")
    print("5. View character details")
    print("6. Exit")
    print()

def run_adventure(adventure_id):
    print(f"🎮 Starting '{adventure_id}'...")
    print("-" * 40)
    
    cmd = ["python3", "main.py", adventure_id]
    print(f"Command: {' '.join(cmd)}")
    print()
    print("📢 The AI GM will now start. Follow the prompts in Discord.")
    print("💡 Type '!help' for available commands.")
    print("🛑 Type '!override' to pause the game.")
    print()
    
    # Ask for confirmation
    response = input("Start adventure? (y/n): ").strip().lower()
    if response == 'y':
        print("🚀 Launching adventure...")
        subprocess.run(cmd)
    else:
        print("❌ Adventure cancelled")

def test_system():
    print("🧪 System Test:")
    print("-" * 40)
    
    tests = [
        ("DeepSeek API", "python3 -c \"import os; from agents.deepseek_client import DeepSeekClient; client = DeepSeekClient(); print('✅ API connected')\""),
        ("Dice Roller", "python3 -c \"from agents.dice_roller import DiceRoller; r = DiceRoller(); result = r.roll('1d20'); print(f'✅ Dice roll: {result}')\""),
        ("State Manager", "python3 -c \"from agents.state_manager import StateManager; sm = StateManager('data'); print(f'✅ Loaded {len(sm.characters)} characters')\""),
    ]
    
    for name, cmd in tests:
        print(f"Testing {name}...")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {name}: PASS")
            else:
                print(f"❌ {name}: FAIL - {result.stderr}")
        except Exception as e:
            print(f"❌ {name}: ERROR - {e}")
        print()

def main():
    print_header()
    check_system()
    
    while True:
        list_adventures()
        list_characters()
        quick_start_menu()
        
        try:
            choice = input("Select option (1-6): ").strip()
            
            if choice == '1':
                run_adventure('crystal_chamber')
            elif choice == '2':
                run_adventure('ghost_ship')
            elif choice == '3':
                run_adventure('apostae_station')
            elif choice == '4':
                test_system()
            elif choice == '5':
                list_characters()
                input("Press Enter to continue...")
            elif choice == '6':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-6.")
                
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Dashboard closed")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

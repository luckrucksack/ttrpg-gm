# DCC JUDGE SYSTEM
## AI Judge for Dungeon Crawl Classics

> **PATH NOTE (2026-08-10):** Repo restructured. This doc is a March-era
> snapshot; paths inside (dcc_judge.py, data/...) are stale. Current layout:
> judge = `systems/dcc/judge.py`, campaign data = `campaigns/dying_earth/`.
> See README.md and systems/README.md for the live map.

A specialized AI Judge system built on top of the existing TTRPG AI GM framework, adding all of DCC's unique mechanics.

## 🎯 What Makes DCC Unique

Dungeon Crawl Classics has several mechanics that require special handling:

### **Core DCC Mechanics Implemented:**

#### 1. **Spellburn** 🔥
- Wizards/Elves/Clerics can sacrifice STR/AGI/STA for spell power
- 1:1 bonus to spell checks (burn 3 Strength = +3 to spell check)
- Points recover at 1 per day per ability
- Excessive use risks weakness or death

#### 2. **Corruption** 💀
- Natural 1 on spell check causes mishap → corruption
- Physical/supernatural changes to caster
- Three severity levels: minor, major, severe
- Corruption is permanent (with rare exceptions)

#### 3. **Mercurial Magic** 🔮
- Spell checks use dice chain (d20, stepping up to d24, d30)
- Critical success steps up spell check die permanently
- Each spell has unique mercurial effects table
- Non-Vancian: no spell slots, can cast until failure

#### 4. **Luck System** 🍀
- All characters have Luck score (prime attribute)
- Can burn Luck for +1d per point to checks
- Burning Luck permanently reduces score
- Warriors/Dwarves use for deeds, casters use after spellburn

#### 5. **Dice Chain** 🎲
- Resolution uses chain: d3, d4, d5, d6, d7, d8, d10, d12, d14, d16, d20, d24, d30
- High-level casters step up dice for greater volatility
- Warriors use for deed dice (starts at d3, improves)

#### 6. **True Random Dice Roller** 🎲
- **Cryptographically Secure**: Uses SHA-256 hashing for true randomness
- **All DCC Dice**: d3, d4, d5, d6, d7, d8, d10, d12, d14, d16, d20, d24, d30, d%
- **Specialized Functions**: Spell checks, crits, fumbles, luck checks
- **Batch Rolling**: Multiple dice at once for efficiency
- **Dice Chain Stepping**: Automatic step up/down in dice chain

#### 7. **Class-Specific Tables** 📋
- **Critical Hit Tables**: Different for Warrior, Wizard, Cleric, Thief
- **Fumble Tables**: Unique failures per class
- **Mighty Deeds**: Warriors/Dwarves can attempt special maneuvers
- **Turn Undead**: Clerics can repel undead

## 🚀 Getting Started

### **1. System Requirements**
- Python 3.8+
- Existing TTRPG AI GM system (`/Users/chriscoon/ttrpg_gm/`)
- DeepSeek API key (configured in system)

### **2. Quick Start**
```bash
# Navigate to ttrpg_gm directory
cd /Users/chriscoon/ttrpg_gm/

# Check system status
python dcc_judge.py --status

# Run test adventure
python dcc_judge.py dcc_test

# Create a DCC character
python dcc_judge.py --create-character character_data.json

# Run DCC mechanics tests
python dcc_judge.py --test
```

### **3. Creating DCC Characters**

**Basic Character JSON:**
```json
{
  "name": "Grom the Unlucky",
  "class": "Warrior",
  "level": 1,
  "race": "Dwarf",
  "abilities": {
    "strength": {"score": 16, "modifier": "+2"},
    "agility": {"score": 12, "modifier": "+0"},
    "stamina": {"score": 15, "modifier": "+1"},
    "personality": {"score": 8, "modifier": "-1"},
    "intelligence": {"score": 10, "modifier": "+0"},
    "luck": {"score": 7, "modifier": "-1"}
  },
  "hit_points": {"current": 10, "maximum": 10},
  "occupation": "Miner",
  "equipment": ["Pickaxe", "Leather Armor", "10 torches"]
}
```

**Save as `grom.json` and create:**
```bash
python dcc_judge.py --create-character grom.json
```

## 🎮 DCC Judge Commands

### **In-Game Commands:**
```
!spellburn <character> <ability> <points>
!luck <character> <points>
!deed <character> <description>
!turn <character> <target_hd>
!spell <character> <spell_level> [modifier]
!crit <character> [roll]
!fumble <character> [roll]
!dcc  (show help)
```

### **Dice Rolling Commands:**
```
!roll <dice_type> [count] [modifier]  # Roll any DCC dice
!percent                               # Roll d% with description
!spell_check <level> [caster_level]    # Spell check with burn calc
!crit_roll <attack> [weapon_type]      # Critical hit resolution
!fumble_roll [roll]                    # Fumble resolution
!luck_check <luck_score>               # Luck check with burn
```

### **Examples:**
```
!spellburn zephyr strength 3     # Burn 3 Strength for +3 spell check
!luck elara 2                    # Burn 2 Luck for +2d bonus
!deed thorin disarm the ogre     # Attempt disarming deed
!turn merlin 4                   # Turn undead of 4 HD
!spell morwen 2                  # Cast 2nd level spell
!crit grom 17                    # Critical hit roll 17

!roll d20                        # Single d20
!roll d6 3 2                     # 3d6+2
!roll d%                         # Percentage die
!roll d30                        # Mercurial magic die
!percent                         # d% with descriptive text
!spell_check 2                   # Level 2 spell check
!crit_roll 24 warrior            # Warrior crit on attack 24
!fumble_roll                     # Random fumble
!luck_check 12                   # Luck check with score 12
```

## 🏗️ System Architecture

### **Core Components:**
```
/Users/chriscoon/ttrpg_gm/
├── dcc_judge.py              # Main DCC Judge system
├── dice_roller.py            # True random DCC dice roller (NEW)
├── agents/
│   ├── dcc_manager.py        # DCC mechanics implementation
│   ├── state_manager.py      # Character/world state
│   ├── dice_roller.py        # Legacy dice roller (basic)
│   ├── prose_refiner.py      # Two-stage literary refinement
│   └── deepseek_client.py    # AI model integration
├── data/
│   ├── characters/           # DCC character JSONs
│   ├── adventures/           # DCC adventure files
│   └── world_state/          # Game state persistence
├── test_dcc_dice.py          # Dice roller test suite
└── DCC_JUDGE_README.md       # This file
```

### **Integration with Existing System:**
- **Builds on** existing TTRPG AI GM framework
- **Adds** DCC-specific mechanics layer
- **Maintains** two-stage prose refinement
- **Preserves** JSON-as-ground-truth philosophy
- **Extends** state management for DCC features

### **True Random Dice Roller Implementation:**
The `dice_roller.py` provides cryptographically secure random number generation:

**Features:**
- **Cryptographically Secure**: Uses SHA-256 hashing with multiple entropy sources
- **All DCC Dice**: Full support for d3, d4, d5, d6, d7, d8, d10, d12, d14, d16, d20, d24, d30, d%
- **Specialized Functions**: 
  - `roll_spell_check()`: Calculates spellburn needs automatically
  - `roll_crit()`: Handles class-specific critical hits
  - `roll_fumble()`: Resolves fumbles with severity levels
  - `roll_luck_check()`: Manages Luck burning
- **Batch Rolling**: Roll multiple dice types at once
- **Dice Chain**: Automatic step up/down in the DCC dice chain
- **Table Rolling**: Roll on custom tables with any dice type

**Entropy Sources:**
1. System time (nanosecond precision)
2. Operating system random bytes (`os.urandom`)
3. Process ID
4. Performance counter entropy

**Usage:**
```python
from dice_roller import DCCDiceRoller

roller = DCCDiceRoller()
roll = roller.roll('d20')                    # Single d20
damage = roller.roll('d6', 3, 2)            # 3d6+2
percent, desc = roller.roll_percentage()    # d% with description
spell_result = roller.roll_spell_check(2)   # Level 2 spell check
crit_result = roller.roll_crit(24, 'warrior') # Warrior crit
```

## 📊 DCC Character Template

The system includes a comprehensive DCC character template:

**Key Fields:**
- `abilities`: STR, AGI, STA, PER, INT, LUCK with spellburn tracking
- `mercurial_magic`: Spell check dice, corruption, patron taint
- `deeds`: Mighty Deed tracking for Warriors/Dwarves
- `turn_undead`: Cleric turning attempts
- `spellburn_history`: Track all spellburn uses
- `corruption_history`: Record of corruption effects
- `luck_burn_history`: Permanent Luck reductions

## 🎭 Adventure Format

DCC adventures use a simple text format:

```
# Scene: Room Name
## Description of the room and key features.

- Encounter: Monster details (HD, AC, special abilities)
- Treasure: Item description and effects
- -> Exit to another scene
```

**Example Adventure:** `data/adventures/dcc_test.txt`

## 🔧 Technical Details

### **Dice Chain Implementation:**
```python
class DCCDice(Enum):
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
```

### **Spell Check Algorithm:**
1. Base die from `mercurial_magic.spell_check_dice` (starts d20)
2. Add INT modifier + level + spellburn bonus
3. Roll and compare to DC (10 + spell level)
4. Results: Mishap (1), Failure (< DC), Success (≥ DC), Critical (≥ 20)
5. Critical success steps up spell check die

### **Corruption System:**
- **Minor**: Cosmetic changes (glowing eyes, pale skin)
- **Major**: Functional changes (horns, scales, extra digits)
- **Severe**: Major transformations (wings, elemental form)
- **Taint Level**: Tracks corruption severity for patron magic

## 🧪 Testing the System

Run comprehensive DCC mechanics tests:
```bash
python dcc_judge.py --test
```

**Tests include:**
- ✅ Character creation
- ✅ Spellburn application and recovery
- ✅ Luck burning (permanent reduction)
- ✅ Critical hit/fumble resolution
- ✅ Mighty Deed attempts
- ✅ Spell checks with mercurial magic
- ✅ Corruption application

## 📈 Integration with Dying Earth Campaign

The DCC Judge system is ready for your **Dying Earth campaign**:

### **Ready to Use:**
1. **Adventures Organized**: 11 Dying Earth adventures in campaign structure
2. **DCC Mechanics**: All unique DCC rules implemented
3. **Literary Refinement**: Two-stage prose for Vance-style writing
4. **Character System**: DCC-compatible JSON tracking
5. **Web Interface**: Campaign guide and access system

### **Next Steps:**
1. **Import Characters**: Create DCC versions of your players
2. **Load Adventure**: Start with DE #0: The Crooked Fingers
3. **Begin Session**: The Judge is ready to run

## 🚨 Important Notes

### **Non-Negotiable DCC Rules:**
1. **Spellburn is risky** - Can reduce abilities below functional levels
2. **Corruption is permanent** - No easy removal (rare magic only)
3. **Luck burns are forever** - Permanently reduces Luck score
4. **Mercurial magic is chaotic** - Each spell has unique effects
5. **Dice chain matters** - Higher dice = greater volatility

### **System Limitations:**
- Currently console-based (Discord integration pending)
- Simplified crit/fumble tables (full tables would be massive)
- Basic adventure format (could extend to full PDF parsing)
- No visual interface (web UI planned)

## 🔮 Future Enhancements

### **Planned Features:**
1. **Discord Integration**: Full bot with DCC command support
2. **PDF Adventure Parser**: Extract scenes from DCC PDFs
3. **Web Interface**: Visual character sheets and dice roller
4. **Full Crit/Fumble Tables**: Complete DCC table implementation
5. **Patron Magic System**: Detailed patron relationships and taint
6. **Campaign Manager**: Track multiple DCC campaigns

### **Integration Goals:**
- **WhatsApp/Telegram**: Multi-channel support for long messages
- **Character Import**: From PDF scans or form-fillable sheets
- **Rulebook Integration**: Direct lookup of DCC rules during play
- **AI Model Switching**: Use different models for different tasks

## 📚 Resources

### **DCC Rulebooks to Index:**
1. **DCC Core Rulebook** - Core rules, spells, tables
2. **DCC Annual** - Additional rules and adventures
3. **DCC Companion** - High-level play rules
4. **DCC Lankhmar** - City adventures and rules
5. **DCC Dying Earth** - Your campaign setting!

### **Useful References:**
- [Goodman Games DCC RPG](https://goodman-games.com/dcc-rpg/)
- [Purple Sorcerer Tools](https://purplesorcerer.com/tools.php)
- [Crawler's Companion](https://crawlerscompanion.com/)
- [DCC Rules Wiki](https://dccwiki.com/)

## 🎉 Ready for Adventure!

The DCC Judge system is **fully built and ready** for your Dying Earth campaign. All the unique DCC mechanics are implemented, integrated with the existing AI GM framework, and waiting for your first session.

**To begin:**
```bash
cd /Users/chriscoon/ttrpg_gm/
python dcc_judge.py --status
```

**Then create characters and start your adventure in the world of the Dying Earth!**

---
*DCC Judge System v1.0 - Built for the Dying Earth Campaign*
*Integration with TTRPG AI GM Framework - March 21, 2026*
# Simple Adventure Example

This is a minimal adventure to demonstrate the AI GM system without needing a PDF.

## Adventure: "The Crystal Chamber"

### Rooms

**Room 1: Entrance Chamber**
```
A circular chamber with smooth stone walls. Torches in iron sconces cast flickering light across the room. In the center stands a stone pedestal with a glowing blue crystal. The air is cool and smells of ozone.

Read Aloud: "As you enter, the crystal pulses with a soft blue light, illuminating strange runes carved into the floor."
```

**Room 2: Corridor**
```
A narrow corridor stretches into darkness. The walls are rough-hewn stone, and water drips from cracks in the ceiling. The sound echoes ominously.

Read Aloud: "Your footsteps echo in the narrow passage. From ahead, you hear a faint scratching sound."
```

**Room 3: Guard Room**
```
This room contains two stone benches and a small table. A rusty sword leans against the wall. A door on the far wall is slightly ajar.

Read Aloud: "The room appears to have been a guard post long abandoned. Dust covers everything except... fresh footprints in the dust."
```

### Monsters

**Giant Rat**
- HP: 7
- AC: 12
- Bite: +4 to hit, 1d4+2 piercing damage
- Special: Advantage on Perception checks that rely on smell

**Skeleton Guard**
- HP: 13
- AC: 13
- Scimitar: +4 to hit, 1d6+2 slashing damage
- Vulnerability: Bludgeoning damage

### Traps

**Pressure Plate Dart Trap**
- Location: Corridor, 10 feet from Room 1
- Trigger: 20+ lbs pressure
- Effect: 1d4 piercing damage, DC 12 Dexterity save for half
- Disable: DC 15 Thieves' Tools

### Treasure

**Glowing Crystal**
- Value: 50 gp to a collector
- Magic: Sheds dim light in 10-foot radius
- Special: Warm to the touch, faint humming sound

**Rusty Sword**
- Value: 5 gp (as scrap metal)
- Note: Actually a +1 sword disguised by rust (DC 15 Arcana to detect)

### NPCs

**Old Man Withers**
- Location: Village nearby
- Motivation: Wants the crystal returned (it was stolen from his family)
- Information: Knows about the secret door in Room 3
- Reward: 100 gp for crystal's return

## Using This Adventure

### 1. Create JSON File
Save this as `data/world_state/crystal_chamber.json`:

```json
{
  "metadata": {
    "adventure_name": "crystal_chamber",
    "created": "2024-01-01T00:00:00",
    "version": 1
  },
  "rooms": {
    "room1": "A circular chamber with smooth stone walls. Torches in iron sconces cast flickering light across the room. In the center stands a stone pedestal with a glowing blue crystal. The air is cool and smells of ozone.",
    "room2": "A narrow corridor stretches into darkness. The walls are rough-hewn stone, and water drips from cracks in the ceiling. The sound echoes ominously.",
    "room3": "This room contains two stone benches and a small table. A rusty sword leans against the wall. A door on the far wall is slightly ajar."
  },
  "read_aloud": {
    "room1_enter": "As you enter, the crystal pulses with a soft blue light, illuminating strange runes carved into the floor.",
    "room2_enter": "Your footsteps echo in the narrow passage. From ahead, you hear a faint scratching sound.",
    "room3_enter": "The room appears to have been a guard post long abandoned. Dust covers everything except... fresh footprints in the dust."
  },
  "monsters": {
    "Giant Rat": {
      "hp": 7,
      "ac": 12,
      "stats_text": "HP: 7, AC: 12, Bite: +4 to hit, 1d4+2 piercing damage. Advantage on Perception checks that rely on smell."
    },
    "Skeleton Guard": {
      "hp": 13,
      "ac": 13,
      "stats_text": "HP: 13, AC: 13, Scimitar: +4 to hit, 1d6+2 slashing damage. Vulnerability: Bludgeoning damage."
    }
  },
  "traps": {
    "dart_trap": {
      "description": "Pressure plate in corridor triggers darts from wall.",
      "location": "room2",
      "dc": 12,
      "damage": "1d4 piercing",
      "disable_dc": 15
    }
  },
  "treasure": {
    "glowing_crystal": {
      "description": "Glowing blue crystal on pedestal.",
      "value": "50 gp",
      "magic": "Sheds dim light in 10-foot radius"
    },
    "rusty_sword": {
      "description": "Rusty sword leaning against wall.",
      "value": "5 gp",
      "secret": "+1 sword disguised by rust (DC 15 Arcana)"
    }
  },
  "npcs": {
    "old_man_withers": {
      "description": "Elderly villager seeking stolen family heirloom.",
      "motivation": "Wants crystal returned",
      "reward": "100 gp",
      "information": "Knows about secret door in Room 3"
    }
  },
  "current_location": {
    "id": "room1",
    "description": "Entrance Chamber with crystal"
  }
}
```

### 2. Create Sample Characters
Save these in `data/characters/`:

**thoradin.json** (Dwarf Fighter):
```json
{
  "name": "Thoradin",
  "class": "Fighter",
  "level": 1,
  "hp": {
    "current": 12,
    "max": 12
  },
  "abilities": {
    "str": 16,
    "dex": 10,
    "con": 14,
    "int": 8,
    "wis": 12,
    "cha": 10
  },
  "inventory": [
    {"name": "Battleaxe", "quantity": 1},
    {"name": "Shield", "quantity": 1},
    {"name": "Healing Potion", "quantity": 2}
  ],
  "conditions": [],
  "_metadata": {
    "created": "2024-01-01T00:00:00",
    "version": 1
  }
}
```

**elara.json** (Elf Wizard):
```json
{
  "name": "Elara",
  "class": "Wizard",
  "level": 1,
  "hp": {
    "current": 8,
    "max": 8
  },
  "abilities": {
    "str": 8,
    "dex": 14,
    "con": 12,
    "int": 16,
    "wis": 10,
    "cha": 12
  },
  "inventory": [
    {"name": "Spellbook", "quantity": 1},
    {"name": "Dagger", "quantity": 1},
    {"name": "Component Pouch", "quantity": 1}
  ],
  "spell_slots": {
    "level1": {
      "total": 2,
      "used": 0
    }
  },
  "conditions": [],
  "_metadata": {
    "created": "2024-01-01T00:00:00",
    "version": 1
  }
}
```

### 3. Run the System
```bash
# Start the AI GM with this adventure
python main.py crystal_chamber
```

### 4. Example Game Flow

**Player**: "I examine the crystal on the pedestal."

**AI GM** (after processing):
```
The crystal pulses rhythmically, like a slow heartbeat. The blue light illuminates intricate runes carved into the floor around the pedestal. They seem to form some kind of pattern or warning. The crystal itself is warm to the touch and emits a faint humming sound.

[REQUEST_ROLL: 1d20+3] Arcana check to understand the runes.
```

**System**: Rolls 1d20+3 = 17, posts to Discord

**AI GM** (continuing):
```
The runes are a protective ward—meant to contain the crystal's energy. You recognize them as ancient Draconic script warning of "unbound arcane power." The crystal appears to be a focus for some kind of magical energy, possibly left here intentionally.
```

**Player**: "I try to pick up the crystal."

**AI GM**:
```
As your fingers close around the crystal, the runes on the floor flare with bright light! A low rumble echoes through the chamber.

[UPDATE_STATE: rooms.room1.crystal.taken, true]
[REQUEST_ROLL: 1d20+2] Dexterity save to avoid the flash.
```

And so on...

## Tips for This Adventure

1. **Start in Room 1** - Crystal is the central mystery
2. **Room 2 has trap** - Use [REQUEST_ROLL] for Perception to spot it
3. **Room 3 has secret** - Old Man Withers knows about it
4. **Monsters appear** when crystal is taken or certain triggers met
5. **Treasure has secrets** - Rusty sword is actually magical

This demonstrates all key system features:
- Room descriptions
- Read-aloud text
- Monster stats
- Traps
- Treasure
- NPCs
- Directives ([REQUEST_ROLL], [UPDATE_STATE])
- State management
- Character tracking
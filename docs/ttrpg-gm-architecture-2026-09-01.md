# AI Game Master — System Architecture 2026-09-01

**Status:** Architecture + pipeline built, awaiting Foundry MCP user setup and first test session.

## Overview

The AI Game Master system runs published TTRPG adventures in Foundry VTT
with a Hermes Agent Bot acting as the Game Master. It's modular — each
component can be swapped or extended independently.

## System Map

```
┌─────────────────────────────────────────────────────────────────┐
│                      PLAYER SURFACES                            │
│  Discord channel │ Hermex/webui │ Foundry VTT chat              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    GM BOT (ttrpg profile)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Hermes Bot Mode — persistent named agent                │   │
│  │  Model: deepseek/deepseek-v4-flash (OpenRouter)          │   │
│  │  Skills: narrator, prohibitions, foundry-bridge,         │   │
│  │          campaign-tools                                   │   │
│  │  Memory: TencentDB Agent Memory (:8421)                   │   │
│  │  Tools: MCP (Foundry), terminal, delegate_task           │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┼──────────────────┐
        │               │                  │
┌───────▼──────┐ ┌──────▼──────┐  ┌───────▼──────┐
│  NPC BOTS    │ │  NPC BOTS   │  │  NPC BOTS     │
│  (Hermes     │ │  (Hermes    │  │  (Hermes      │
│  profiles)   │ │  profiles)   │  │   profiles)   │
│              │ │              │  │              │
│ Model: ox-   │ │ Model: ox-   │  │ Model: ox-   │
│ alpha (free) │ │ alpha (free)│  │ alpha (free) │
│ Memory: iso- │ │ Memory: iso- │  │ Memory: iso- │
│ lated per NPC│ │ lated per   │  │ lated per    │
│ Skills: NPC  │ │ NPC         │  │ NPC          │
│ personality  │ │              │  │              │
└──────────────┘ └──────────────┘  └──────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                FOUNDRY VTT (:30000)                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Native MCP Server (laurigates/foundryvtt-mcp)         │    │
│  │  ─ search/create/update actors, items, journals        │    │
│  │  ─ combat management, initiative, conditions           │    │
│  │  ─ token movement, dice rolling                        │    │
│  │  ─ world search, scene info                            │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Published adventures imported as:                               │
│  ─ Journal entries = room descriptions, NPC dialogue            │
│  ─ Actors = NPCs, monsters with full statblocks                 │
│  ─ Scenes = maps with walls, lighting, tokens                   │
│  ─ Items = equipment, magic items, spells                       │
│  ─ Roll tables = encounters, loot, random events                │
└─────────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│               CAMPAIGN MEMORY (TencentDB :8421)                  │
│  Structured by: scene blocks, persona, episodic, instruction    │
│  ─ Player character profiles                                    │
│  ─ Session logs + summaries                                     │
│  ─ NPC relationship state                                       │
│  ─ Plot thread tracker                                          │
│  ─ World state snapshots                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Pipeline — PDF Adventure Ingestion (`pipeline/`)

Converts PDF adventures into Foundry-readable JSON:

```
PDF → MarkItDown (text) → LLM extraction (JSON) → MCP import (Foundry)
```

- `ingest.py`: Stage 1-3, outputs `output/<adventure>/` with actors.json,
  journals.json, items.json, roll_tables.json
- `import_foundry.py`: Connects to Foundry MCP, calls create_actor,
  create_journal_entry, etc. for each entity

### 2. Bridge — Foundry Connection (`bridge/`)

The GM Bot talks to Foundry via Hermes's native MCP client, which
connects to `laurigates/foundryvtt-mcp` (MIT, OSS).

Config in `~/.hermes/profiles/ttrpg/config.yaml` under `mcp_servers`.

### 3. GM Bot (`bot/`)

Hermes Bot Mode agent running in the ttrpg profile. Loads 4 skills:
- `ttrpg-narrator` — prose style, pacing, voice
- `ttrpg-prohibitions` — anti-cliché enforcement
- `ttrpg-foundry-bridge` — MCP tool reference
- `ttrpg-campaign-tools` — session management, memory

### 4. NPC Bots (`bot/npc-template/`)

Each NPC is an isolated Hermes profile with:
- Cheap model (ox-alpha)
- Isolated memory (the blacksmith doesn't know the dungeon's secret)
- SOUL.md defining personality, voice, knowledge boundaries
- Activated via delegate_task by the GM Bot

### 5. Campaign Memory

TencentDB Agent Memory on port :8421.
- Scene blocks for compressed session logs
- Episodic memory for narrative history
- Persona for character profiles
- Instruction for running decisions

## Session Flow

1. **Setup** — Buy adventure PDF or Foundry premium module. If PDF:
   `python -m pipeline.ingest path/to/adventure.pdf`
   `python -m pipeline.import_foundry import output/<name>/`
2. **Pregame** — Player connects via Discord/Foundry chat. GM Bot loads
   campaign memory and current Foundry state
3. **Play** — GM Bot narrates from adventure journals via narrator skill.
   Foundry handles all mechanics (combat, dice, conditions) via MCP.
   Deep NPC interactions delegated to NPC Bots
4. **End** — GM Bot writes session log to campaign memory, advances
   NPC agendas via cron

## File Layout

```
~/ttrpg_gm/
├── pipeline/           # PDF adventure ingestion
│   ├── __init__.py
│   ├── ingest.py       # MarkItDown → LLM → JSON
│   └── import_foundry.py  # JSON → MCP → Foundry
├── bridge/
│   └── README.md       # MCP server setup docs
├── bot/
│   ├── README.md       # GM Bot config
│   ├── skills/
│   │   ├── ttrpg-narrator.md
│   │   ├── ttrpg-prohibitions.md
│   │   ├── ttrpg-foundry-bridge.md
│   │   └── ttrpg-campaign-tools.md
│   └── npc-template/
│       └── README.md   # NPC Bot template
├── docs/               # MkDocs site (auto-published to GitHub Pages)
├── campaigns/          # Adventure data
├── README.md
└── mkdocs.yml
```

## Getting Started

1. Install the Foundry MCP server (see `bridge/README.md`)
2. Add MCP config to ttrpg profile
3. Import a published adventure (buy from Foundry marketplace
   or use pipeline for a PDF)
4. Start a session via the GM Bot in Bot Mode

## Future Extensions

- **Critique loop**: z.ai GLM 5.2 reviews narrative output against
  prohibitions before it reaches the player
- **NPC auto-pilot**: monster tactics during combat, NPC roleplay on
  autopilot during downtime
- **Campaign memory consolidation**: cron-driven weekly summary compaction
- **Published adventure marketplace scraper**: auto-detect new imports
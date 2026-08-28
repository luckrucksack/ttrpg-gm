# AI Game Master — Hermes Bot Architecture

**Date:** 2026-08-27
**Last updated:** 2026-08-27 (DCC Python framework retired — Foundry handles game mechanics)
**Status:** Architecture proposal, not yet built
**Context:** Decision to retire the custom Python AI-GM framework (`gm_core/`, `systems/dcc/`, `main.py`) and move the TTRPG project onto the Hermes Agent platform — replacing a duplicated agent framework with the actual one.

## Why This Exists

The original `~/ttrpg_gm/` repo was built as a **standalone AI agent runtime** — its own orchestrator, state manager, LLM client, Discord bridge, and DCC mechanics engine. It duplicated what Hermes already provides, and its DCC game mechanics layer duplicated what Foundry VTT already provides. Hermes Bot Mode + profiles + skills + memory + gateway + Foundry address every concern that old repo was trying to solve.

The Python code was ~5,300 lines across ~35 files, with zero actual game sessions run. The design knowledge in the docs is the durable asset. This document describes the replacement.

## Layer Map (top to bottom)

```
┌─────────────────────────────────────────────────────────────┐
│                      PLAYER SURFACES                        │
│  Discord channel │ Hermex/webui │ Foundry VTT chat         │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                  GM BOT (ttrpg profile)                      │
│                                                              │
│  Roles: orchestrate sessions, adjudicate rules, generate     │
│  narrative, coordinate NPC Bots, keep campaign memory        │
│                                                              │
│  Provider: deepseek/deepseek-v4-flash via OpenRouter         │
│  Memory: TencentDB ttrpg (:8421) — campaign world store      │
│  Tools: terminal (dice), delegate_task (NPC Bots), Foundry   │
│  Skills: ~6 loaded (see skills block below)                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  NPC BOTS    │ │  NPC BOTS   │ │  NPC BOTS   │
│  (Hermes     │ │  (Hermes    │ │  (Hermes    │
│   profiles)   │ │   profiles)  │ │   profiles)  │
│              │ │              │ │              │
│ Model: ox-   │ │ Model: ox-   │ │ Model: ox-   │
│ alpha (free) │ │ alpha (free)│ │ alpha (free)│
│ Memory: iso- │ │ Memory: iso- │ │ Memory: iso- │
│ lated per NPC│ │ lated per NPC│ │ lated per NPC│
│ Skills: NPC  │ │ Skills: NPC  │ │ Skills: NPC  │
│ personality  │ │ personality  │ │ personality  │
└──────────────┘ └──────────────┘ └──────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    FOUNDRY VTT (:30000)                      │
│                                                              │
│  Source of truth for: actors, scenes, combat, dice, maps,    │
│  ALL game mechanics. No separate rules engine needed —       │
│  Foundry handles DCC, D&D5e, and any other system natively.  │
│  Bridge: direct REST calls (MVP) → MCP server (long-term).   │
└─────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    CAMPAIGN MEMORY                           │
│                                                              │
│  TencentDB Agent Memory (:8421) on ttrpg profile              │
│  Structured types: character profiles, location descriptions,│
│  plot threads, faction relationship graph, session logs,     │
│  NPC knowledge boundaries                                    │
│  Cron: weekly consolidation (existing, works)                │
└─────────────────────────────────────────────────────────────┘
```

## How a Session Actually Flows

### Player says "I go see Moses the blacksmith"

1. **GM Bot** receives the message via Discord Hermex
2. **GM Bot** loads campaign memory from TencentDB — who Moses is, what the party owes him, last interaction
3. **GM Bot** looks up Moses's current Foundry state via bridge (HP, location, inventory)
4. **GM Bot** decides: "this warrants a full NPC interaction" -> spawns Moses Bot via `delegate_task` with context brief
5. **Moses Bot** wakes (ox-alpha, cheap), reads its isolated memory + the brief, responds in-character
6. **GM Bot** receives NPC response, writes new interaction to campaign memory, pushes state update to Foundry
7. **GM Bot** relays narrative back to player

### Between sessions — the world breathes

- **Cron routines** advance NPC agendas: the vizier Bot DMs the guard captain Bot to increase patrols
- **GM Bot** surfaces relevant changes next session: "While you slept, the East Gate guards have doubled"
- **TencentDB consolidation cron** compacts session logs into durable scene blocks (weekly, existing)

## Skills the GM Bot Needs

| Skill | Purpose | Source |
|-------|---------|--------|
| `ttrpg-narrator` | Prose style guide, tone rules, pacing, scene framing | Extract from the GM master prompt research |
| `ttrpg-prohibitions` | Verbatim anti-cliché ban list, what the GM must NOT do | From Apple Notes canonicals (backlog item) |
| `ttrpg-npc-gen` | Enneagram/MBTI questionnaire + anti-cliché tension rules | From `docs/development-notes.md` |
| `ttrpg-foundry-bridge` | How to read/write Foundry actors, scenes, combat | TBD — depends on bridge mechanism chosen |
| `ttrpg-campaign-tools` | Session log format, world state conventions, faction tracking | To be written |
| `ttrpg-faction-system` | Faction advancement rules, reputation, between-session events | Future |

**DCC mechanics are NOT a skill.** Foundry VTT handles all game system mechanics — dice, tables, character creation, combat resolution. The GM Bot queries Foundry for mechanical outcomes rather than implementing them in a skill. This eliminates the need to maintain parallel rule implementations.

## NPC Bots — Design Notes

Each significant NPC is a **Hermes profile** under `~/.hermes/profiles/npc-<name>/`:

- **Profile:** mini Hermes instance with own memory, skills, and cron
- **Model:** ox-alpha (OpenRouter free tier) — zero cost until activated
- **Memory:** isolated TencentDB per NPC — the merchant can't know the dungeon's secret
- **Skills:** 1-2 personality/domain prompts per NPC
- **Dormancy:** zero runtime cost — just a config + empty session DB when idle
- **Lifecycle:** created during campaign prep, archived on NPC death (or haunted)

**Cost model for a session:**
- GM Bot: ~5-15 turns, V4 Flash (~$0.15-0.45)
- NPC Bots per interaction: ~2-4 turns, ox-alpha (free or ~$0.0002/turn)
- Total: ~$0.20-0.60 per active session hour

## What Survives From the Old Repo

**Kept (already in docs/):**
- All research docs — prompt architecture, landscape survey, VTT comparison, memory backend analysis, token reduction playbook
- NPC Bots design sketch
- Enneagram/MBTI questionnaire concept (in development-notes.md)
- The prompt architecture research (`docs/ai-dm-prompt-architecture-2026-08-07.md`) — years of iteration on what makes an AI GM work: the prohibitions doctrine, named engines (Anti-Formulaic, Drift, Affirmative Reality, d20/d12 Dual-Axis, Signal Scrambler), and failure modes
- `integrations/foundry/NOTES.md` — Foundry bridge reference

**Removed (Python framework, replaced by Hermes + Foundry):**
- `gm_core/` runtime, agents, config — Hermes replaces all of it
- `systems/dcc/` DCC mechanics — Foundry handles all game mechanics
- `systems/dnd5e/` rules stub — Foundry handles this too
- `main.py` — Hermes shell replaces it
- `scripts/` launchers — Hermes cron replaces them
- `requirements.txt` — no Python runtime deps needed
- `.env.template` — credentials in Hermes .env now
- `examples/` — demo adventure for the old runtime

## What Was Built (Retired Python Framework — DCC System)

This section documents the full scope of what was removed, so the design effort isn't lost even though none of these modules were ever run in a real game session. The DCC system was approximately 2,376 lines across 13 files, plus supporting docs.

### systems/dcc/dice.py (455 lines)

A DCC-specific dice roller with cryptographically secure entropy generation. Implemented the full DCC dice chain (d3, d4, d5, d6, d7, d8, d10, d12, d14, d16, d20, d24, d30, d%) with step-up and step-down operations through the chain. Supported table lookups (rolling on weighted result tables), percentage rolls with descriptive outcomes, spell checks (d20 + caster level vs. spell level target), critical hit rolls with class-specific crit tables and extra damage scaling based on attack roll thresholds, fumble rolls with severity categories, luck checks (roll-under with permanent luck burn mechanics), and batch rolling for multiple simultaneous dice. Included an entropy harvester that mixed time_ns, os.urandom, PID, and SHA-256 hashes to produce cryptographically secure random outputs, with a seeded mode for reproducible testing. Had a `get_statistics()` method for distribution analysis across 1000+ roll samples.

### systems/dcc/manager.py (727 lines)

The DCC game mechanics state manager. Responsible for spellburn (sacrificing Strength, Agility, or Stamina for spell bonuses at 1:1 ratio, with 1-point-per-day recovery), corruption (random table-driven permanent body mutations from spell failure, with minor/major/severe severity levels), mercurial magic taint tracking, luck point burning (permanent reduction for temporary dice chain bonuses), turning undead, Mighty Deeds of Arms (Warrior/Dwarf class ability with d3/d4/d5 deed dice), critical hit resolution from class-specific tables (Warrior/Wizard/Cleric/Thief with 10 severity levels each), fumble resolution by class, and class-specific dice chain lookup tables for all class abilities. All persisted through the gm_core StateManager's JSON-on-disk pattern.

### systems/dcc/judge.py (785 lines)

The DCC Judge — the full AI runtime for DCC game sessions. Extended the gm_core runtime loop with DCC-specific command parsing (bang-commands: !spellburn, !luck, !deed, !turn, !spell, !crit, !fumble, !dice, !percent), adventure file loading and scene extraction from markdown-structured text (parsing `# Scene:` headers into encounter/treasure/exit objects), party loading from JSON character files tagged with system=Dungeon Crawl Classics, formatted response delivery for all DCC action types with emoji-coded severity indicators, and a main runtime loop that listened for Discord or console input and routed through the DCC Judge pipeline. Had its own `_extract_scenes()` parser that turned narrative markdown into structured scene objects.

### DCC Documentation (5 docs, ~369 lines each)

Full documentation set including: a DCC JUDGE README describing all implemented mechanics and usage, a quick reference card for DCC rules, a quick start guide for DM setup, a delivery summary for the system, health check scripts, roadmap, and a validation report. These were comprehensive system docs for an engine that was never played.

### DCC Tests (2 test files + 2 shell scripts, ~176+ lines)

The test suite included a `test_dcc_dice.py` testing all dice types, dice chain stepping, and statistical distribution, plus shell-based mechanics tests and system health checks.

### systems/dnd5e/rules.md (32 lines)

A minimalist D&D 5th Edition rules reference stub — ability scores and skills list. Never meaningfully developed.

---

## What Was Built (Retired Python Framework — gm_core System)

### gm_core/runtime.py (754 lines)

The central orchestration loop for the AI-GM system. Coordinated all agents (DeepSeekClient, StateManager, ProseRefiner, DiscordBridge, PDFIngestor), managed asynchronous runtime with signal handling, parsed structured directives from LLM output (REQUEST_ROLL, UPDATE_STATE, UPDATE_CHARACTER, MOVE_SCENE), maintained scene state and narrative buffer, handled input/output routing between Discord and CLI modes, and ran the session lifecycle (adventure loading, party management, scene progression, session persistence).

### gm_core/agents/deepseek_client.py (279 lines)

Custom API client for DeepSeek's chat completions endpoint. Handled prompt construction, response parsing, token counting, conversation history management, retry logic with exponential backoff, and system prompt injection. Tightly coupled to a specific provider and model — no provider abstraction layer, no credential rotation, no model fallback.

### gm_core/agents/state_manager.py (495 lines)

JSON-based world state and character persistence. Thread-safe file I/O with in-memory caching and locks. Loaded/saved JSON per adventure (world_state) and per character. Character model included abilities, inventory, conditions, spell lists, and narrative history. Enforced the invariant that on-disk JSON wins over model assertions.

### gm_core/agents/prose_refiner.py (178 lines)

Two-stage output refinement that ensured raw LLM output never reached players directly. First stage removed dialectic/contrastive/antithetical structures ("But wait!", "However, ...", "On one hand..."). Second stage was a literary rewrite that improved pacing, sensory specificity, and tone consistency. A direct code implementation of the prompt architecture's "Signal Scrambler" and "Anti-Formulaic" engines.

### gm_core/agents/discord_bridge.py (350 lines)

Discord bot integration using discord.py. Managed bot lifecycle, channel routing, message formatting, and command dispatch. Included guild setup, message queue scheduling, intent configuration, rate-limit handling, and Discord-native dice roll formatting.

### gm_core/agents/pdf_ingestor.py (349 lines)

PDF adventure module and character sheet parser using PyPDF2 and pdfplumber. Extracted text, detected section boundaries, parsed stat blocks, and structured the result into adventure/scene/encounter objects. Included a fallback extraction mode for scanned/image PDFs.

### gm_core/config.py (99 lines)

Environment-driven configuration with path resolution, campaign data directory bootstrapping, system module loading via import, and startup validation for API keys and directory existence. Added repo root to sys.path for import resolution.

### gm_core/dice.py (171 lines) and gm_core/__init__.py (7 lines)

Generic (non-DCC-specific) dice parser that handled standard dice notation (NdX+modifier), plus the package init. The generic dice module was small — the heavy dice logic lived in systems/dcc/dice.py.

### main.py (15 lines)

Entry shim that imported and called gm_core.runtime.main(). Minimal, but represented the old execution model.

### Scripts (5 scripts)

Included bash launchers (launch_gm.sh, setup.sh, setup_complete.sh), a Python play dashboard (play_dashboard.py), and a PDF download workflow document. All tied to the old Python runtime execution model.

### examples/simple_adventure.md (264 lines)

A demo adventure "The Crystal Chamber" with 8 rooms, encounters, and treasure — written to demonstrate the AI GM system without needing a PDF. Never run.

---

## Foundry Bridge — Three Options (TBD)

| Option | How | Complexity |
|--------|-----|-----------|
| A. Foundry API via MCP | Write a small MCP server that exposes Foundry actors/combat/scenes as tools | Medium |
| B. Hermes desktop plugin | Desktop plugin that talks Foundry API + registers slash commands | Medium-high |
| C. Direct REST calls | Hermes just curls Foundry's REST API endpoints | Low (start here) |

Foundry has a REST API (port 30000, needs a token). Option C gets us running fastest — Hermes can `terminal("curl ...")` to read/write state. Option A is the long-term clean path.

## Immediate Next Steps (ordered)

1. **Wire Foundry REST bridge** — minimal curl-based read/write to show it works (Option C)
2. **Write the prohibition catalog skill** — extract exact prohibition wording from Apple Notes canonicals (backlog item from 08-10)
3. **Test-run a scene** — first actual game session via the GM Bot talking to Foundry
4. **Build the narrator skill** — prose style guide from the GM master prompt research
5. **Build first NPC Bot** — Moses the blacksmith as a working profile
6. **Campaign memory conventions** — session log format, world state schema, faction tracking
7. **Enneagram/MBTI question bank** — lowest priority, after proving the pipeline works

## Related Documents

- `docs/npc-bots-design-sketch-2026-08-26.md` — the NPC Bot concept
- `docs/development-notes.md` — Enneagram/MBTI questionnaire design
- `docs/ai-dm-prompt-architecture-2026-08-07.md` — the prohibition layer and engine design
- `docs/ai-dm-landscape-2026-08-06.md` — original landscape research
- `docs/backlog.md` — project backlog
- `integrations/foundry/NOTES.md` — Foundry bridge notes
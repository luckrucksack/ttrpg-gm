# AI Game Master — Hermes Bot Architecture

**Date:** 2026-08-27
**Status:** Architecture proposal, not yet built
**Context:** Decision to retire the custom Python AI-GM framework (`gm_core/runtime.py` etc.) and move the TTRPG project onto the Hermes Agent platform — replacing a duplicated agent framework with the actual one.

## Why This Exists

The original `~/ttrpg_gm/` repo was built as a **standalone AI agent runtime** — its own orchestrator, state manager, LLM client, and Discord bridge. It duplicated what Hermes already provides. Hermes Bot Mode + profiles + skills + memory + gateway address every concern that repo was trying to solve.

The Python code is ~5,300 lines, zero actual game sessions run. The design knowledge in the docs is the durable asset. This document describes the replacement.

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
│  Skills: ~8 loaded (see skills block below)                  │
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
│  Source of truth for: actors, scenes, combat, dice, maps     │
│  Bridge: MCP server or lightweight websocket adapter         │
│  Hermes reads/writes Foundry state via bridge                │
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

1. **GM Bot** (you, in the ttrpg profile) receives the message
2. **GM Bot** loads campaign memory from TencentDB — who Moses is, what the party owes him, last interaction
3. **GM Bot** decides: "this warrants a full NPC interaction" → spawns Moses Bot via `delegate_task` with context brief
4. **Moses Bot** wakes (cheap model), reads its isolated memory + the brief, responds in-character
5. **GM Bot** receives NPC response, potentially checks it against Foundry state, relays to player
6. **GM Bot** writes new interaction to both campaign memory (TencentDB) and Moses Bot's memory

### Between sessions — the world breathes

- **Cron routines** advance NPC agendas: the vizier Bot DMs the guard captain Bot to increase patrols
- **GM Bot** surfaces relevant changes next session: "While you slept, the East Gate guards have doubled"
- **TencentDB consolidation cron** compacts session logs into durable scene blocks (weekly, existing)

## Skills the GM Bot Needs

| Skill | Purpose | Source |
|-------|---------|--------|
| `ttrpg-dcc-rules` | DCC mechanics, dice chain tables, character creation, spell mishaps | Extract from `systems/dcc/dice.py` + `judge.py` |
| `ttrpg-narrator` | Prose style guide, tone rules, pacing, scene framing | Extract from the GM master prompt research |
| `ttrpg-prohibitions` | Verbatim anti-cliché ban list, what the GM must NOT do | From Apple Notes canonicals (backlog item) |
| `ttrpg-npc-gen` | Enneagram/MBTI questionnaire + anti-cliché tension rules | From `docs/development-notes.md` |
| `ttrpg-foundry-bridge` | How to read/write Foundry actors, scenes, combat | TBD — depends on bridge mechanism chosen |
| `ttrpg-campaign-tools` | Session log format, world state conventions, faction tracking | To be written |
| `ttrpg-faction-system` | Faction advancement rules, reputation, between-session events | Future |

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

## What We Keep From the Old Repo

**Keep as-is (move into docs/ or convert to skills):**
- `systems/dcc/dice.py` → DCC dice chain encoding (convert to reference or Python script)
- `systems/dcc/judge.py` → DCC mechanics knowledge (extract the rules into a skill)
- `systems/dcc/manager.py` → state/session patterns (inform the campaign memory design)
- `gm_core/dice.py` → dice roller (usable as a terminal tool or Foundry handles this)
- All `docs/` files — research is durable
- NPC Bots design sketch → already in docs/
- Enneagram/MBTI questionnaire concept → already documented

**Shed:**
- `gm_core/runtime.py` — Hermes is the runtime now
- `gm_core/agents/` (all 5 agents) — each maps to a Hermes concern (provider, gateway, memory, etc.)
- `gm_core/config.py` — replaced by Hermes config.yaml
- `main.py` — Hermes shell replaces it
- `scripts/` launchers — Hermes cron replaces them
- `requirements.txt` — no Python runtime deps needed
- `.env.template` — credentials live in Hermes .env now

**The prompt architecture** (`gm_core/prompts/README.md` + the docs) is the most valuable non-code asset. It documents years of iteration on what makes an AI GM work — the prohibitions, the named engines, the failure modes. That knowledge survives into the skills.

## Foundry Bridge — Three Options (TBD)

| Option | How | Complexity |
|--------|-----|-----------|
| A. Foundry API via MCP | Write a small MCP server that exposes Foundry actors/combat/scenes as tools | Medium |
| B. Hermes plugin | Desktop plugin that talks Foundry API + registers slash commands | Medium-high |
| C. Direct REST calls | Hermes just curls Foundry's REST API endpoints | Low (start here) |

Foundry has a REST API (port 30000, needs a token). Option C gets us running fastest — Hermes can `terminal("curl ...")` to read/write state. Option A is the long-term clean path.

## Immediate Next Steps (ordered)

1. **Extract DCC mechanics into a skill** — `skill_manage(create, name='ttrpg-dcc-rules')` with dice tables, character creation, action resolution baked in
2. **Write the prohibition catalog skill** — the backlog item from 08-10: extract the exact prohibition wording from Apple Notes canonicals
3. **Wire Foundry REST bridge** — minimal curl-based read/write to show it works
4. **Test-run a scene** — first actual game session via the GM Bot
5. **Build first NPC Bot** — Moses the blacksmith as a working profile
6. **Then the question bank** (Enneagram/MBTI) — lower priority than proving the pipeline works

## Related Documents

- `docs/npc-bots-design-sketch-2026-08-26.md` — the NPC Bot concept
- `docs/development-notes.md` — Enneagram/MBTI questionnaire design
- `docs/ai-dm-prompt-architecture-2026-08-07.md` — the prohibition layer and engine design
- `docs/ai-dm-landscape-2026-08-06.md` — original landscape research
- `docs/backlog.md` — project backlog
- `integrations/foundry/NOTES.md` — Foundry bridge notes
- `README.md` — old architecture (will be replaced)
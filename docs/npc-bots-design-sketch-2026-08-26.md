# NPC Bots: Hermes Bot Mode as TTRPG Non-Player Characters

**Date:** 2026-08-26
**Context:** Triggered by reading about Hermes Bot Mode (desktop app feature where each Hermes profile is a named Bot with persistent chat, memory, skills, and routines). Realization that an NPC is already a person with knowledge, personality, relationships, and memory who only acts when engaged — the exact shape of a dormant Hermes Bot.

## Core Idea

Each significant NPC is a dedicated Hermes Bot — an isolated profile with its own:
- Memory (session history from every interaction with the party)
- Skills (domain knowledge — town rumors, economy, faction relationships)
- Personality prompt (voice, mannerisms, knowledge boundaries)
- Recurring routines (cron jobs that advance the NPC's agenda between sessions)
- Strict information isolation (must NOT know things the NPC shouldn't know)

## How It Would Work at the Table

1. Player says "I go see Moses the blacksmith about that sword"
2. GM Bot (the orchestrator) identifies the target NPC
3. GM Bot sends a brief to Moses Bot's Bot Chat: "Party arrives, reference prior interaction from 3 sessions ago, they want to discuss a custom sword order"
4. Moses Bot responds in-character, with its own memory of the party's previous interactions, debts, and reputation
5. GM Bot relays the response to Foundry VTT / the player channel

## Key Design Decisions Collected

- **Cost discipline:** NPC Bots use a cheap model (ox-alpha) for routine conversation. Only the GM Bot escalates to the expensive model for game-critical decisions. NPC bots are idle (zero cost) until activated.
- **Orchestration protocol:** GM Bot is the traffic cop — it decides when to delegate to an NPC Bot vs answer inline. Casual small talk (weather, directions) handled inline. Plot-relevant conversations get the full NPC Bot treatment.
- **No shared memory:** Each NPC Bot has its own isolated memory store (profile isolation). A merchant Bot cannot recall the secret door in the duke's castle. This is enforced by the profile boundary, not by trust.
- **Memory compaction:** NPC Bots accumulate interaction history. Need a periodic summarization routine to compact long-running NPC memory without losing important relationship data.
- **Dormant NPCs cost nothing:** A Bot is just a config file + session DB when idle. No daemon, no context, no tokens burned.

## The Trippy Part (Emergent Behavior)

Bot-to-Bot DMs between NPCs means the game world has a subconscious layer:
- The vizier Bot DMs the captain of the guard Bot: "Increase patrols at the east gate"
- The merchant Bot messages the town crier Bot: "The party skipped town without paying"
- The thieves' guild Bot coordinates its member NPCs autonomously
- These interactions happen via cron routines between sessions, without the GM thinking about them
- The GM Bot surfaces whatever becomes relevant next session

This is distinct from existing TTRPG AI tools — nobody is using persistent agent instances as discrete NPCs with autonomous between-session routines and inter-NPC communication.

## Open Questions for Next Pass

- Cost model: what does 5 NPC bots + 1 villain bot cost per session on ox-alpha vs V4 Flash?
- Activation protocol: how does the GM Bot decide "this conversation is worth an NPC Bot turn" vs "I'll handle it inline"?
- NPC lifecycle: what happens when an NPC dies? Do we archive the Bot, delete it, or let it haunt from beyond?
- Bot-to-Bot latency: NPC DMs between sessions are fine (cron-driven, async), but in-session NPC-to-NPC interaction needs a fast path
- Foundry bridge: do NPC Bots drive Foundry tokens directly, or does all Foundry interaction go through the GM Bot?
- Campaign memory boundary: campaign world state lives in the ttrpg-gm repo. NPC Bots reference it via tools, not by loading it into their own memory. Keeps knowledge boundaries honest.

## Architecture Options (from earlier discussion)

- **Option A — Single AI GM Bot.** One Bot runs everything, talks to Foundry via MCP/plugins. Simple. Gets context-heavy.
- **Option B — Specialist Bots.** GM Bot orchestrates, Rules Bot adjudicates mechanics, Narrator Bot writes prose, NPC Bots handle characters. Each focused, cheap.
- **Option C — Bot Mode as player portal only.** AI GM stays headless (current model). Bot Mode is just the chat surface players talk to. Less ambitious, proven path.

The NPC-as-Bot concept slots into Option B naturally but could also sit atop Option C.

## Related Files

- `docs/ai-dm-landscape-2026-08-06.md` — original AI DM landscape research
- `docs/ai-dm-prompt-architecture-2026-08-07.md` — prompt architecture
- `docs/noodlr-vs-foundryai-2026-08-06.md` — Foundry bridge decision research
- `integrations/foundry/NOTES.md` — Foundry integration notes
- `STATUS.md` — project status
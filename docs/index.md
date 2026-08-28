# TTRPG Game Master — Architecture & Design Docs

This repository contains the design documentation for a self-hosted AI Game Master system.

**System:** [Hermes Bot Mode](https://hermes-agent.nousresearch.com) as the GM runtime, [Foundry VTT](https://foundryvtt.com) as the game surface, and isolated Hermes profile Bots as individual NPCs.

**Status:** Architecture settled. Build phase begins next.

## Start Here

- [Full Architecture](ttrpg-gm-architecture-2026-08-27.md) — the current design, layer map, session flow, and full description of the retired Python framework
- [NPC Bots Design](npc-bots-design-sketch-2026-08-26.md) — using isolated Hermes Bot profiles as persistent TTRPG NPCs
- [Prompt Architecture](ai-dm-prompt-architecture-2026-08-07.md) — the prohibition layer and named engines from years of Apple Notes iteration

## Project History

This was originally a ~5,300-line custom Python AI agent framework. On 2026-08-27 it was retired: the runtime duplicated Hermes, and the game mechanics duplicated Foundry VTT. The design knowledge survived into these docs.

See also: [Project Backlog](backlog.md)
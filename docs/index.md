# TTRPG Game Master — Architecture & Design Docs

This repository documents a self-hosted AI Game Master system that runs
published TTRPG adventures in Foundry VTT with a Hermes Agent Bot as the GM.

**System:** [Hermes Bot Mode](https://hermes-agent.nousresearch.com) (GM Bot),
[Foundry VTT](https://foundryvtt.com) (game mechanics + maps),
[laurigates/foundryvtt-mcp](https://github.com/laurigates/foundryvtt-mcp) (bridge),
Isolated Hermes Bot profiles (NPCs).

**Status:** Architecture v2, pipeline built, awaiting first test session.

## Start Here

- [Current Architecture](ttrpg-gm-architecture-2026-09-01.md) — the modular
  system: pipeline, bridge, bot, NPC template, campaign memory
- [Previous Architecture (v1)](ttrpg-gm-architecture-2026-08-27.md) — the
  original design that this system was built from
- [NPC Bots Design](npc-bots-design-sketch-2026-08-26.md) — using isolated
  Hermes Bot profiles as persistent TTRPG NPCs
- [Prompt Architecture](ai-dm-prompt-architecture-2026-08-07.md) — the
  prohibition layer and named engines from years of Apple Notes iteration

## Components

| Piece | What |
|-------|------|
| `pipeline/ingest.py` | PDF → MarkItDown → LLM extraction → Foundry JSON |
| `bridge/` | MCP server setup for Foundry ↔ Hermes communication |
| `bot/skills/` | 4 skills: narrator, prohibitions, foundry-bridge, campaign-tools |
| `bot/npc-template/` | Template for creating isolated NPC Bot profiles |
| `docs/` | MkDocs site (auto-published to GitHub Pages) |

## Project History

Originally a ~5,300-line custom Python AI agent framework. Retired 2026-08-27.
Replaced by Hermes bot integration + Foundry. Now modular with PDF ingestion pipeline.
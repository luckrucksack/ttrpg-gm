# TTRPG Game Master — Architecture & Design Docs

This repository documents a self-hosted AI Game Master system that runs
published TTRPG adventures in Foundry VTT with a Hermes Agent Bot as the GM.

**System:** [Hermes Bot Mode](https://hermes-agent.nousresearch.com) (GM Bot),
[Foundry VTT](https://foundryvtt.com) (game mechanics + maps),
[laurigates/foundryvtt-mcp](https://github.com/laurigates/foundryvtt-mcp) (bridge),
GM-only NPC dossiers in the Foundry world.

**Status:** the Convergence campaign is complete. The GM doctrine now includes
the Pre-Game Protocol. The next build is the offscreen world engine.

## Start Here

- [Current Architecture (v4, 2026-09-29)](ttrpg-gm-architecture-2026-09-29.md) —
  the system layer by layer, verified state, session lifecycle, operational
  knowledge
- [Offscreen World Engine — target architecture](architecture/offscreen-world-engine.md) —
  the parallel-timeline engine the GM needs, with the research brief
- [Pre-Game Protocol](../bot/skills/ttrpg-prep.md) — what every new GM instance
  does before the first scene
- [Repo Map](REPO-MAP.md) — what lives where, the reading order, and the known
  gaps
- [Prompt Architecture](ai-dm-prompt-architecture-2026-08-07.md) — the
  prohibition layer and named engines from years of Apple Notes iteration

## Components

- `pipeline/ingest.py` — PDF to MarkItDown to LLM extraction to Foundry JSON
- `bridge/` — MCP server setup for Foundry and Hermes communication
- `bot/skills/` — the AI GM doctrine set: core (`ttrpg-ai-gm.md`), prep,
  narrator, prohibitions, campaign tools, foundry bridge
- NPC dossiers — GM-only journals in the Foundry world, single home, no repo
  copy
- `docs/` — MkDocs site, auto-published to GitHub Pages

## Project History

Originally a ~5,300-line custom Python AI agent framework, retired 2026-08-27.
Replaced by Hermes bot integration plus Foundry. Now modular with a PDF
ingestion pipeline. Older architecture revisions live in `docs/archive/`.

# TTRPG Game Master — AI-Powered Published Adventure Runner

An open-source AI Game Master system that runs published TTRPG adventures
in Foundry VTT with a Hermes Agent Bot as the GM.

**What it does:**
- Import a published adventure (buy premium or convert a PDF)
- Talk to a GM Bot that narrates, runs combat, voices NPCs
- Everything runs locally — no SaaS, no per-session fees

**Architecture:**
- **GM Bot** — Hermes Bot Mode agent (deepseek-v4-flash via OpenRouter)
- **Foundry VTT** — game mechanics, maps, actors, combat engine
- **NPC Bots** — isolated Hermes profiles for key NPCs (ox-alpha free tier)
- **Pipeline** — PDF → MarkItDown → LLM → Foundry JSON import
- **Bridge** — MCP server (laurigates/foundryvtt-mcp, MIT) connects bot to Foundry
- **Memory** — TencentDB Agent Memory for campaign persistence

## Quick Start

```bash
# 1. Install Foundry MCP server
npx -y foundryvtt-mcp

# 2. Convert a PDF adventure
python -m pipeline.ingest path/to/adventure.pdf
python -m pipeline.import_foundry import pipeline/output/<name>/

# 3. Start playing via the GM Bot
hermes -p ttrpg
```

## Repository Layout

```
pipeline/       PDF adventure ingestion (MarkItDown + LLM)
bridge/         Foundry MCP connection setup
bot/            GM Bot config + NPC Bot template + skills
docs/           Architecture docs + MkDocs site (auto-published)
```

## License

MIT
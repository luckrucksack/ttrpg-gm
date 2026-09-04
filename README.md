# TTRPG Game Master — AI-Powered Published Adventure Runner

An open-source AI Game Master system that runs published TTRPG adventures
in Foundry VTT with a Hermes Agent Bot as the GM.

**What it does:**
- Import a published adventure (buy premium or convert a PDF)
- Talk to a GM Bot that narrates, runs combat, voices NPCs
- Self-hosted core (Foundry, Hermes, memory); model calls via OpenRouter
  (~$0.20–0.60 per active session hour — see the token-reduction playbook)

**Architecture:**
- **GM Bot** — Hermes Bot Mode agent (deepseek-v4-flash via OpenRouter; v4-pro for heavy scenes)
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

# 3. Generate the Foundry import plan (executed by the GM Bot via MCP)
python -m pipeline.import_foundry plan pipeline/output/<name>/

# 4. Start playing via the GM Bot
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
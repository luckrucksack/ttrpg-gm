# STATUS

**Current:** Architecture v2 (2026-09-01) — Hermes Bot Mode as the GM runtime, Foundry VTT as the mechanics engine, NPCs as isolated Hermes profiles. No game sessions played yet.

## What's in this repo

- `pipeline/` — PDF adventure ingestion (`ingest.py` = MarkItDown → LLM → JSON; `import_foundry.py` = JSON validation + import manifest for the GM Bot to execute via its MCP client)
- `bridge/` — Foundry MCP server (foundryvtt-mcp) setup docs
- `bot/` — GM Bot config docs, 4 skills, NPC Bot template
- `docs/` — architecture and research docs (published to GitHub Pages by CI)
- `scripts/setup.sh` — one-time setup helper

## Verified state (2026-09-04)

- `ingest.py` runs — needs `OPENROUTER_API_KEY` / `OPENAI_API_KEY` and MarkItDown installed
- `import_foundry.py` is a manifest generator, not a direct importer — Foundry writes happen through the GM Bot's native MCP client (foundryvtt-mcp has **no `create_actor` tool**; actors and roll tables import manually — see `pipeline/import_foundry.py` header)
- GitHub Pages CI: fixed 2026-09-04 (workflow was missing `mkdocs-material`); the deploy pipeline now builds with `--strict`
- ttrpg profile configured: skills external_dirs, TencentDB memory (:8421), Foundry MCP server block (needs a real `mcp-api` password — currently `<your-password>`)

## Not yet done

- Foundry MCP API user not created; MCP connection unauthenticated
- No adventure imported; zero sessions played
- z.ai editing loop not wired
- NPC profiles not created

See `docs/backlog.md`.
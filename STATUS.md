# STATUS

**Current:** Architecture v2 (2026-09-01) — Hermes Bot Mode as the GM runtime, Foundry VTT as the mechanics engine, NPCs as isolated Hermes profiles. No game sessions played yet.

## What's in this repo

- `pipeline/` — PDF adventure ingestion (`ingest.py` = MarkItDown → LLM → JSON; `import_foundry.py` = JSON validation + import manifest for the GM Bot to execute via its MCP client)
- `bridge/` — Foundry MCP server (foundryvtt-mcp) setup docs + `check.sh` verification harness
- `bot/` — GM Bot config docs, 4 skills, NPC Bot template
- `docs/` — architecture and research docs (published to GitHub Pages by CI)
- `scripts/setup.sh` — one-time setup helper

## Verified state (2026-09-09)

- **Foundry bridge is LIVE and verified end to end.** `bash bridge/check.sh` passes all three gates: Foundry `:30000` answers → `mcp-api` credentials authenticate → the MCP server registers all **33 `mcp_foundry_*` tools**. Server admin key restored (`Config/admin.txt` copied back from `admin.txt.bak`; the `.bak` is kept).
- `mcp-api` service account created in the `deltagreen` world (role 3, Assistant GM). Its password lives only in `~/.hermes/profiles/ttrpg/.env` as `MCP_FOUNDRY_PASSWORD`; `config.yaml` references it as `${MCP_FOUNDRY_PASSWORD}`.
- `foundryvtt-mcp` **pinned to v1.5.2** in the ttrpg profile — tool names and parameter shapes are version-specific.
- `bot/skills/ttrpg-foundry-bridge.md` rewritten against the real v1.5.2 schemas. The previous version had **9 wrong parameter names and 1 nonexistent tool**, and omitted `search_compendium` (the tool that reaches purchased adventure content).
- `ingest.py` runs — needs `OPENROUTER_API_KEY` / `OPENAI_API_KEY` and MarkItDown installed
- `import_foundry.py` is a manifest generator, not a direct importer — Foundry writes happen through the GM Bot's native MCP client (foundryvtt-mcp has **no `create_actor` tool**; actors and roll tables import manually — see `pipeline/import_foundry.py` header)
- GitHub Pages CI: fixed 2026-09-04 (workflow was missing `mkdocs-material`); the deploy pipeline now builds with `--strict`

## Not yet done

- No adventure imported; zero sessions played
- ttrpg profile gateway is not running; config changes take effect on next start
- z.ai editing loop not wired
- NPC profiles not created
- Foundry UPnP is enabled (`options.json` → `upnp: true`), so Foundry may be requesting a router port mapping for `:30000`. Turn it off unless remote play is actually needed.

See `docs/backlog.md`.

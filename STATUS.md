# STATUS

**Current:** Architecture v3 (2026-09-25) — see `docs/ttrpg-gm-architecture-2026-09-25.md`. Bridge and memory verified live **again 2026-09-25** (see ledger below); content intake defined (VTT modules primary, PDF secondary); Delta Green world being provisioned. No game sessions played yet. **Hard blocker: Foundry has zero add-on modules installed** — the Delta Green adventure is purchased but not redeemable/installed yet.

## What's in this repo

- `pipeline/` — PDF adventure ingestion (`ingest.py` = MarkItDown → LLM → JSON; `import_foundry.py` = JSON validation + import manifest for the GM Bot to execute via its MCP client)
- `bridge/` — Foundry MCP server (foundryvtt-mcp) setup docs + `check.sh` verification harness
- `bot/` — GM Bot config docs, 4 skills, NPC Bot template
- `docs/` — architecture and research docs (published to GitHub Pages by CI)
- `scripts/setup.sh` — one-time setup helper

## Verified state — re-verified live 2026-09-25

- **Foundry VTT 14.365 is running** (`:30000`, launchd `com.hermes.foundryvtt` → `/Applications/FoundryVTT.app`); `/api/status` reports world `deltagreen` active, system `deltagreen` 1.7.0, 1 user.
- **Foundry bridge is LIVE and verified end to end.** `bash bridge/check.sh` passes all three gates: Foundry `:30000` answers → `mcp-api` credentials authenticate → the MCP server registers all **33 `mcp_foundry_*` tools**. Verified again through Hermes itself: `hermes mcp test foundry --profile ttrpg` → `✓ Connected`, `✓ Tools discovered: 33` (re-run 2026-09-25 after the env-ref fix below).
- **Launch-cwd trap fixed.** The MCP server loads `.env` from its working directory via `dotenv`; the repo `.env` carried `LOG_LEVEL=INFO`, which failed the server's lowercase enum and killed it with an opaque "Connection closed". Value corrected to `info` and `cwd: .../bridge` pinned.
- `mcp-api` service account created in the `deltagreen` world (role 3, Assistant GM). Its password lives only in `~/.hermes/profiles/ttrpg/.env` as `MCP_FOUNDRY_PASSWORD`; `config.yaml` references it as `${env:MCP_FOUNDRY_PASSWORD}`. **Fixed 2026-09-25:** the config had drifted and carried the literal password in plaintext — restored to the env ref and re-verified (`✓ Connected`, 33 tools). Backup: `config.yaml.bak-20260925-175758-mcp-envref`.
- **Memory store isolated and healthy.** `127.0.0.1:8421/health` → `status: ok`, store `~/.memory-tencentdb/ttrpg-memory`. Note `stores.embeddingService: false` — semantic recall is dark, keyword search only (default profile's `:8420` reports `true`).
- `foundryvtt-mcp` **pinned to v1.5.2** in the ttrpg profile — tool names and parameter shapes are version-specific.
- `bot/skills/ttrpg-foundry-bridge.md` rewritten against the real v1.5.2 schemas. The previous version had **9 wrong parameter names and 1 nonexistent tool**, and omitted `search_compendium` (the tool that reaches purchased adventure content).
- `ingest.py` runs — needs `OPENROUTER_API_KEY` / `OPENAI_API_KEY` and MarkItDown installed
- `import_foundry.py` is a manifest generator, not a direct importer — Foundry writes happen through the GM Bot's native MCP client (foundryvtt-mcp has **no `create_actor` tool**; actors and roll tables import manually — see `pipeline/import_foundry.py` header)
- GitHub Pages CI: fixed 2026-09-04 (workflow was missing `mkdocs-material`); the deploy pipeline now builds with `--strict`

## Not yet done

- No adventure imported; zero sessions played
- **No Foundry add-on modules are installed at all** (`Library/Application Support/FoundryVTT/Data/modules` contains only `README.txt`) — so neither the Delta Green adventure module nor the Foundry Local REST API module is present. Nothing has been activated since 2026-08-29 (`Config/license.json` → `version 11.293`, `time 2026-08-29T23:21Z`).
- Foundry Local REST API module not installed (compendium search + diagnostics dark)
- Delta Green module: content activation key appears registered in the profile env, but redemption + install are still pending — **suspect labeling**: the key sits in a var named `FOUNDRY_LICENSE_KEY` (with the 2026-08-05 VTT license demoted to `FOUNDRY_LICENSE_KEY_PREV`), which makes the two hard to tell apart. Worth relabeling before the next redeem attempt.
- ttrpg profile gateway is not running; config changes take effect on next start
- z.ai editing loop not wired
- NPC profiles not created
- Foundry UPnP is enabled (`options.json` → `upnp: true`), so Foundry may be requesting a router port mapping for `:30000`. Turn it off unless remote play is actually needed.

See `docs/backlog.md`.

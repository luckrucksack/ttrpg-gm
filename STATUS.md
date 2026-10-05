# STATUS

**Current:** Architecture v4 (2026-09-29) — see `docs/ttrpg-gm-architecture-2026-09-29.md`. Basic architecture (layers, ownership, session lifecycle, operational knowledge) re-verified against the live runtime **2026-09-29**: bridge green (33 tools), world `deltagreen` active, memory store healthy with embeddings on.

**Update 2026-10-04 — NPC bots: maker built, first bot live.** `bot/npc-maker/` now exists (dossier standard, SOUL scaffold, `make-npc.sh`, activation/voice protocol). First NPC bot: **Billy Ray Spivey** — profile `npc-billy-ray-spivey`, verified end-to-end (free OpenRouter model via `model.default`, Bot Mode marker, canonical Bot Chat, `message_agent` + live roster proven; first voice check in character, ~7s turns). GM doctrine updated (`ttrpg-campaign-tools.md` → NPC Bots section). Old `bot/npc-template/` retired. Remaining: free-model pick from the bake-off, campaign-layer persona archive, first live scene.

**Update 2026-09-29 — world provisioned, first session starting.** Delta Green world `deltagreen` is live and playable: `delta-green-convergence` module installed, Agent Wizard module installed + active, and the player's Agent **Musky Jouse** is built and finished (Federal Agent; stats/skills applied). The earlier "zero add-on modules / adventure not installed" blocker is resolved — mechanics log in `docs/foundry-live-session-2026-09-28.md`. Bridge re-verified live 2026-09-29 (`hermes mcp test foundry --profile ttrpg` → connected, tools discovered).

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
- **Memory store isolated and healthy, with embeddings live (fixed 2026-09-25).** `127.0.0.1:8421/health` → `status: ok`, store `~/.memory-tencentdb/ttrpg-memory`. The store had been running with `embeddingService: false` — every write landed as a zero vector, so recall was keyword-only. Cause: its `TDAI_GATEWAY_CONFIG` was a literal unexpanded `$HOME` path (falls back to the default store's config) and the spawn env had no `OPENROUTER_API_KEY`. Fixed via a per-store `tdai-gateway.yaml` + absolute config path + spawn command that sources the profile `.env`; all 23 L1 / 6 L0 records re-embedded. Live search now reports `strategy: hybrid`.
- `foundryvtt-mcp` **pinned to v1.5.2** in the ttrpg profile — tool names and parameter shapes are version-specific.
- `bot/skills/ttrpg-foundry-bridge.md` rewritten against the real v1.5.2 schemas. The previous version had **9 wrong parameter names and 1 nonexistent tool**, and omitted `search_compendium` (the tool that reaches purchased adventure content).
- `ingest.py` runs — needs `OPENROUTER_API_KEY` / `OPENAI_API_KEY` and MarkItDown installed
- `import_foundry.py` is a manifest generator, not a direct importer — Foundry writes happen through the GM Bot's native MCP client (foundryvtt-mcp has **no `create_actor` tool**; actors and roll tables import manually — see `pipeline/import_foundry.py` header)
- GitHub Pages CI: fixed 2026-09-04 (workflow was missing `mkdocs-material`); the deploy pipeline now builds with `--strict`

## Not yet done

- 2026-09-29: adventure module now installed; first session starting (was: no adventure imported, zero sessions played)
- 2026-09-29: add-on modules installed + active (`delta-green-convergence`, `delta-green-agent-wizard`) — earlier "zero modules installed" blocker resolved. Foundry Local REST API module still not installed.
- Foundry Local REST API module not installed (compendium search + diagnostics dark)
- Delta Green module: content activation key appears registered in the profile env, but redemption + install are still pending — **suspect labeling**: the key sits in a var named `FOUNDRY_LICENSE_KEY` (with the 2026-08-05 VTT license demoted to `FOUNDRY_LICENSE_KEY_PREV`), which makes the two hard to tell apart. Worth relabeling before the next redeem attempt.
- ttrpg profile gateway is not running; config changes take effect on next start
- z.ai editing loop not wired
- NPC profiles not created
- Foundry UPnP is enabled (`options.json` → `upnp: true`), so Foundry may be requesting a router port mapping for `:30000`. Turn it off unless remote play is actually needed.

See `docs/backlog.md`.

# Foundry VTT integration — decision record

Status: **superseded.** The Foundry bridge is now `laurigates/foundryvtt-mcp`
(see `bridge/README.md`), wired into the Hermes ttrpg profile as a native MCP
server. The subject of this note was the pre-pivot survey. Retained facts
below still hold.

## Verified against the live install (2026-08)

- Foundry v14.365 runs under launchd (`com.hermes.foundryvtt`, port 30000).
- Foundry core has no built-in AI; all AI modules are third-party.
- v14 removed the server-side `main` manifest entry — classic
  server-side-module patterns are gone; modules talk to the world via
  `socket: true` + socket.io.

## Module survey (2026-08-06, superseded)

Surveyed in `docs/ai-dm-landscape-2026-08-06.md` and
`docs/noodlr-vs-foundryai-2026-08-06.md`:
- Noodlr (MIT, pre-1.0) — system-agnostic; thesis = LLMs lack memory /
  authoritative state / restraint. Strongest architectural fit *for a
  module-led design*.
- FoundryAI — most polished, OpenRouter-only + per-browser memory.
- RPGX — fully local via Ollama; quality ceiling on a MacBook Air.

## Why the MCP route won

The AI-DM architecture (2026-09-01) decided the GM is a **Hermes Bot**, not a
Foundry module. Foundry already owns mechanics, maps, and state; the bot needs a
*tool bridge*, not an in-VTT AI module. `foundryvtt-mcp` (MIT, OSS) exposes
Foundry's documents as MCP tools the bot calls through Hermes' native MCP
client. Module-led approaches (Noodlr et al.) remain an option for in-app AI
assistance but are not the architecture's integration point.

## Current bridge

See `bridge/README.md` — setup, config block, and the verified tool list.
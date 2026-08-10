# Foundry VTT integration — current state (NOTES)

Status: **research only. No integration code exists.**

## Known facts (verified against the live install)

- Foundry v14.365 runs under launchd (`com.hermes.foundryvtt`, port 30000).
- Foundry core has no built-in AI; all AI modules are third-party.
- v14 removed the server-side `main` manifest entry — classic
  server-side-module patterns are gone; modules talk to the world via
  `socket: true` + socket.io.
- Candidate modules surveyed in docs/ai-dm-landscape-2026-08-06.md and
  docs/noodlr-vs-foundryai-2026-08-06.md:
  - Noodlr (MIT, pre-1.0) — system-agnostic, native-DeepSeek-compatible,
    thesis = LLMs lack memory / authoritative state / restraint (matches
    this project's design DNA). Strongest architectural fit.
  - FoundryAI — most polished, but OpenRouter-only + per-browser memory.
  - RPGX — fully local via Ollama; quality ceiling on a MacBook Air.

## What the final architecture will depend on

The Foundry integration decision (adopt Noodlr / build custom bridge /
port gm_core) determines how `gm_core`, `systems/`, and `campaigns/`
must be shaped for consumption by the tabletop. Until that decision is
made, treat the layer layout as provisional (see STATUS.md).

## Next step (backlog)

Decide: ready-made vs custom vs hybrid (Noodlr + ttrpg TencentDB memory).
Then this directory becomes the home of the chosen integration.

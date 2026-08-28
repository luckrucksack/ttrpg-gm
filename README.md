# AI Game Master System (ttrpg-gm)

## STATUS: ARCHITECTURE REBOOT

**ARCHITECTURE SETTLED 2026-08-27:** The custom Python AI-GM framework has been retired in favor of **Hermes Bot Mode** as the GM runtime, with Foundry VTT handling all game mechanics. See **[`docs/ttrpg-gm-architecture-2026-08-27.md`](docs/ttrpg-gm-architecture-2026-08-27.md)** for the new design.

**The old code (40 files, ~5,300 lines) has been deleted.** What remains:
- `docs/` — research artifacts and design knowledge (the durable asset)
- `integrations/foundry/NOTES.md` — Foundry bridge reference
- This README

The next phase is building the Hermes Bot Mode architecture — skills, Foundry bridge, NPC Bots — as described in the architecture doc.

## What this repo was

A self-hosted, game-system-agnostic AI Game Master: a stateful LLM agent that was designed to run TTRPG sessions — ingest adventure PDFs, maintain game state, arbitrate rules and dice, generate narrative, and deliver it to players. All Python implementation has been removed as the architecture shifted to Hermes Bot Mode. The design knowledge and research survive in `docs/`.

## Invariants (the prohibitions, made physical — retained for the new architecture)

1. Raw LLM output never reaches players — both prose-refinement stages always run.
2. All randomness comes from the local dice roller (or Foundry); results are posted for audit.
3. JSONs win over model assumptions — state conflicts resolve to disk.
4. State updates happen immediately when triggered, never deferred.

These are the code-enforced core of the prompt architecture's prohibition layer. In the new architecture they become enforced at the Hermes skill and tool level.

## Pointers

- New architecture: `docs/ttrpg-gm-architecture-2026-08-27.md`
- Backlog / open items: `docs/backlog.md`
- Prompt architecture (design DNA): `docs/ai-dm-prompt-architecture-2026-08-07.md`
- NPC Bots design: `docs/npc-bots-design-sketch-2026-08-26.md`
- Foundry landscape: `integrations/foundry/NOTES.md` + `docs/ai-dm-landscape-2026-08-06.md`
- Development notes / Enneagram questionnaire: `docs/development-notes.md`
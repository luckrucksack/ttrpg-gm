# AI Game Master System (ttrpg-gm)

## STATUS: UNDER CONSTRUCTION

**FINAL ARCHITECTURE SETTLED 2026-08-27:** The custom Python AI-GM framework has been retired in favor of **Hermes Bot Mode** as the GM runtime. See **[`docs/ttrpg-gm-architecture-2026-08-27.md`](docs/ttrpg-gm-architecture-2026-08-27.md)** for the new design. The old `gm_core/` and `main.py` remain in the repo but are scheduled for removal once the Bot Mode path is validated. Design knowledge (prompt architecture, prohibitions, DCC mechanics) survives into skills and docs.

## What this is

A self-hosted, **game-system-agnostic AI Game Master**: a stateful LLM agent
that runs TTRPG sessions — ingests adventure PDFs, maintains authoritative
game state, arbitrates rules and dice, generates narrative, and delivers it
to players. DeepSeek-powered, designed to be consumed by Hermes directly
(ported, bridged, or wired into Foundry VTT). It is not written for a human
end-user; it is written for the agent that will operate it.

## Layer map

- `gm_core/` — the system-agnostic engine. Runtime loop, LLM client, dice,
  state manager, PDF ingestion, prose refinement, channel bridges, prompt
  architecture. **Contains no game rules and no campaign data.**
- `systems/` — the game-system layer. One self-contained package per ruleset
  (`dcc/` = Dungeon Crawl Classics/Judge, `dnd5e/` = rules reference only).
  Selected by `ACTIVE_SYSTEM` (default `dcc`). Contract: `systems/README.md`.
- `campaigns/` — the campaign layer. Data only (licensed PDFs, character
  sheets, world state, adventure logs) — **gitignored**, never committed.
  Selected by `DATA_DIR` (default `campaigns/default`; `.env` sets
  `./campaigns/dying_earth`). Layout: `campaigns/README.md`.
- `integrations/` — external wiring. Foundry VTT notes only; nothing
  implemented. Final shape TBD.
- `docs/` — research and design artifacts (AI-DM landscape, prompt
  architecture extraction, Noodlr-vs-FoundryAI, backlog).
- `tests/` — system-agnostic tests; `systems/<id>/tests/` for system-specific.

## How to consume (agent brief)

- **Entrypoints:** `main.py` (shim → `gm_core.runtime.AIGameMaster`) for the
  generic runtime; `systems/dcc/judge.py` for the DCC Judge.
- **Env (see .env.template):** `DEEPSEEK_API_KEY`, `DISCORD_BOT_TOKEN`,
  `DISCORD_GAME_CHANNEL_ID`, `ACTIVE_SYSTEM`, `DATA_DIR`.
- **Rules:** enter the LLM context only via `systems/<id>/rules_text()`.
  The core is rules-free by construction (`gm_core/config.py`:
  `load_system_rules(active_system())`).
- **State:** JSON under `DATA_DIR` is ground truth. The model proposes
  structured directives — `[REQUEST_ROLL]`, `[UPDATE_STATE]`,
  `[UPDATE_CHARACTER]`, `[MOVE_SCENE]` — the runtime executes them.
- **Run:** `source venv/bin/activate && python main.py` (needs API keys).

## Invariants (the prohibitions, made physical)

1. Raw LLM output never reaches players — both prose-refinement stages
   always run.
2. All randomness comes from the local dice roller; results are posted to
   the channel for audit.
3. JSONs win over model assumptions — state conflicts resolve to disk.
4. State updates happen immediately when triggered, never deferred.

These are the code-enforced core of the prompt architecture's prohibition
layer (see `gm_core/prompts/README.md`).

## Pointers

- Backlog / open items: `docs/backlog.md`
- Prompt architecture (design DNA): `gm_core/prompts/README.md` +
  `docs/ai-dm-prompt-architecture-2026-08-07.md`
- Foundry landscape: `integrations/foundry/NOTES.md` +
  `docs/ai-dm-landscape-2026-08-06.md`
- Systems contract: `systems/README.md`
- Campaign layout: `campaigns/README.md`

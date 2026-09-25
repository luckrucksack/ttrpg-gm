# TTRPG Game Master — Architecture

**Version 3 — 2026-09-25** · Supersedes [v2 (2026-09-01)](ttrpg-gm-architecture-2026-09-01.md) and [v1 (2026-08-27)](ttrpg-gm-architecture-2026-08-27.md)

**What it is:** An AI Game Master that runs *published* TTRPG adventures end-to-end in Foundry VTT. A Hermes Agent Bot narrates, voices, paces, and decides; **Foundry VTT owns every rule, roll, token, and point of state**. Campaign memory records what happened, so the story persists between sessions.

The bar: *take a bought adventure from "purchased" to "a full session played" with no human scripting the rules.*

## Principles

1. **Modular.** Every piece is swappable at a documented seam — bridge, pipeline, skills, memory, surfaces. The GM's logic talks to Foundry only through MCP tool calls, so the backend can be replaced without touching narration, and vice versa.
2. **Foundry is the source of truth** for game state (stats, HP, conditions, positions). Campaign memory is the source of truth for narrative (who trusts whom, what was promised). On conflict: Foundry wins for state, memory wins for story.
3. **Published content only.** No invented adventures, demo campaigns, or filler — ever. The owner supplies every adventure.
4. **Verify against the live runtime.** The installed package, the running service — not READMEs, not config comments. `bridge/check.sh` is the reference harness.

## Content intake — two paths, and only two

**Path A — Purchased VTT modules (the primary path).**
Buy the adventure as a Foundry-ready module (official Marketplace, or external stores like DriveThruRPG which provide a *content activation key*). Then:

1. Redeem the key: foundryvtt.com → Purchased Content → paste key → Activate.
2. Install: Foundry Setup → Add-on Modules → Package Installer → Premium Content → Install.
3. Enable: in-world → Settings → Manage Modules → check it → Save.
4. The content lives in **Compendiums**. The GM Bot reads it through the bridge (`search_compendium`, `get_journal`, actor reads) or imports selected pieces into the world.

No PDF tooling anywhere in this path. Activation keys are registered in the profile env for provenance.

**Path B — PDFs (occasional, when no VTT edition exists).**
`pipeline/ingest.py`: PDF → MarkItDown → LLM extraction → JSON → import manifest for Foundry. This path applies *sometimes* — it is not the default intake.

## System map

```
Player surfaces
  webui chat · Discord · Foundry chat
          │
    GM Bot  (Hermes ttrpg profile)
    skills + memory client
          │
    Bridge  (foundryvtt-mcp, 33 MCP tools)
       ┌──┴───────────────┐
  Foundry VTT          Memory gateway
  :30000               TencentDB :8421
  (game state)         (narrative memory)
```

## Components — state as of 2026-09-25

**Bridge.** `foundryvtt-mcp@1.5.2`, pinned. Verified live: 33 `mcp_foundry_*` tools; service account `mcp-api` (Assistant GM); write access enabled; cwd pinned to `bridge/`. Harness: `bash bridge/check.sh`. Known upgrade path: the upstream "Foundry Local REST API" module adds compendium search + diagnostics; not yet installed.

**Foundry VTT.** v14.365 on `:30000` (launchd). Active world: `deltagreen` (system `deltagreen` 1.7.0), currently zero modules enabled — the Delta Green adventure module is purchased and awaiting redemption/install.

**GM Bot.** The Hermes `ttrpg` profile with four skills: `ttrpg-narrator`, `ttrpg-prohibitions`, `ttrpg-foundry-bridge` (v1.5.2-accurate), `ttrpg-campaign-tools`.

**Memory.** TencentDB gateway, isolated store (`~/.memory-tencentdb/ttrpg-memory`) on `127.0.0.1:8421`. Auto-spawn fixed 2026-09-25 (needs the Hermes node bin on PATH). Embedding config open (keyword search works today).

**Pipeline (Path B).** `pipeline/ingest.py` + `pipeline/import_foundry.py` (manifest generator; Foundry writes execute through the bridge).

**Surfaces.** Players: webui chat, Discord, Foundry chat. Operator-side interfaces: see next section.

## How the GM touches the game

- **MCP tools** — every state operation the GM needs: search/read actors, journals, scenes, compendiums; create/update documents; combat; dice; tokens. This is the mechanism for play.
- **Browser** — the Foundry app itself is reachable from the operator side (verified). Used for visual grounding (look at the map) and for UI-only operations: installing/enabling modules, importing compendium content, world management.
- **Desktop (computer-use)** — full local UI control when something needs real clicks and drags (map work, dialogs). Used sparingly; browser + MCP cover most needs.
- **Never invented:** if the bridge is down, the GM says so and runs narrative-only. Fabricated Foundry state is forbidden.

## Worked example — standing up a Delta Green world

1. Redeem the Delta Green module key on foundryvtt.com *(in progress)*.
2. Install the DG module + the Foundry Local REST API module (Setup → Package Installer).
3. Enable both in the world; wire `FOUNDRY_API_KEY` for the bridge.
4. Verify: compendium search reaches the adventure; journals readable.
5. Prep real characters (owner-supplied) — no test content.
6. Play.

## NPC Bots — reserved design slot (pinned)

Concept: each significant NPC as an isolated Hermes profile with its own memory and SOUL — the blacksmith genuinely cannot know the dungeon's secret. The GM Bot delegates deep dialogue to them. Design sketch: [`npc-bots-design-sketch-2026-08-26.md`](npc-bots-design-sketch-2026-08-26.md).

**Status: pinned by owner 2026-09-24. Not built.** The architecture keeps the seam (profile-per-NPC, delegated dialogue); no work happens here until unpinned.

## Roadmap

- [x] Bridge live + verified (33 tools)
- [x] Memory store isolated + verified
- [x] Content intake paths defined (this doc)
- [ ] Foundry Local REST API module → compendium search + diagnostics
- [ ] Delta Green module: redeem → install → enable
- [ ] First session scaffold: real characters, real scenario, dry-run the loop
- [ ] NPC bots (pinned)
- [ ] Narrative critique loop (z.ai)

## Open items

- Embedding provider for the ttrpg memory store (semantic recall).
- Same PATH guard for the default/ssdi profile memory envs.
- `bridge/check.sh` leaves a stray process per run — process-group kill on cleanup.

## Revision history

- **v3 (2026-09-25)** — current. Two intake paths clarified; browser/desktop operator surfaces added; NPC bots pinned; verified-state ledger.
- [v2 (2026-09-01)](ttrpg-gm-architecture-2026-09-01.md) — Hermes Bot Mode as the GM runtime.
- [v1 (2026-08-27)](ttrpg-gm-architecture-2026-08-27.md) — first modular design.

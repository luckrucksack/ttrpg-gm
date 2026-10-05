# TTRPG Game Master — Architecture

**Version 4 — 2026-09-29** · Supersedes [v3 (2026-09-25)](ttrpg-gm-architecture-2026-09-25.md);
[v2 (2026-09-01)](ttrpg-gm-architecture-2026-09-01.md) and
[v1 (2026-08-27)](ttrpg-gm-architecture-2026-08-27.md) are kept for history.

**What it is:** an AI Game Master that runs *published* TTRPG adventures
end-to-end in Foundry VTT. A Hermes Agent profile (the GM Bot) narrates, voices
NPCs, paces scenes, and adjudicates; **Foundry VTT owns every rule, roll, token,
and point of state**. Campaign memory records what happened, so the story
survives between sessions.

**The bar:** take a bought adventure from "purchased" to "a full session played,
with no human scripting the rules."

## Principles

1. **Modular.** Every piece is swappable at a documented seam — bridge,
   pipeline, skills, memory, surfaces. The GM's logic reaches Foundry *only*
   through MCP tool calls, so the backend can be replaced without touching
   narration, and vice versa.
2. **Foundry is the source of truth for state** (stats, HP, conditions,
   positions). **Campaign memory is the source of truth for narrative** (who
   trusts whom, what was promised). On conflict: Foundry wins state, memory
   wins story.
3. **Published content only.** No invented adventures, demo campaigns, test
   worlds, or filler — ever. The owner supplies every adventure. This binds
   every agent that touches the project (`AGENTS.md`).
4. **Verify against the live runtime.** The installed package, the running
   service — not READMEs, not config comments. `bridge/check.sh` is the
   reference harness.
5. **The GM's behavior is doctrine, not code.** Campaign style, prohibitions,
   and table mechanics live in markdown doctrine files the owner dictates;
   agents read them and extend them in place, never regenerate or "clean up."

## System map

```
Player surfaces                     Operator surfaces
  WebUI/Hermex (iPhone, desktop)      browser (staffed Firefox → Foundry UI)
  Discord                             computer-use (cua-driver, real clicks)
  Foundry chat                        terminal (ops, DB tooling)
        │                                     │
        └──────────────┬──────────────────────┘
                       │
             GM Bot — Hermes profile `ttrpg`
             (deepseek-flash; SOUL + 1 profile skill
              + 4 campaign doctrine files + memory client)
                       │
              Bridge — foundryvtt-mcp@1.5.2 (33 mcp_foundry_* tools)
                 ┌─────┴──────────────┬──────────────────────┐
          Foundry VTT             Memory gateway          PDF pipeline
          :30000                  TencentDB :8421         (Path B, occasional)
          game state              narrative memory
                 │
          (Bot Mode) NPC bots — isolated Hermes profiles, one per NPC
```

## Layers, and what each one owns

**1. Surfaces.** Players interact by chat: WebUI/Hermex (the owner's phone and
desktop), Discord, and Foundry's own chat. The operator side has three more:
a browser attached to the Foundry app for visual grounding and UI-only
operations, `cua-driver` desktop control when something genuinely needs clicks
and drags, and a terminal for ops work. All live play happens where the player
can see it.

**2. GM Bot — the Hermes `ttrpg` profile.** Model `deepseek-flash` (provider
`deepseek`). It carries:
- `SOUL.md` — the agent's base voice.
- Profile skill `foundry-vtt-gm-operations` (with `references/mcp-bridge.md`,
  `references/content-provisioning.md`, `references/session-orientation.md`) —
  the operational how-to: bridge verification, the tool inventory, the
  zero-tools failure ladder, orientation discipline.
- Four campaign doctrine documents in this repo's `bot/skills/`:
  `ttrpg-narrator.md` (voice, Character & Relationship Doctrine,
  dialogue-first fill-in), `ttrpg-prohibitions.md` (the Prohibited Clichés
  registry, written from the owner's own notes), `ttrpg-campaign-tools.md`
  (Table & Mechanics Doctrine: crunchy mechanics, active coaching, stop at
  every roll, rolls shown openly from real RNG), `ttrpg-foundry-bridge.md`
  (v1.5.2-accurate tool reference).
  These are **living documents**: owner-dictated items are appended in place,
  often verbatim.

**3. Bridge — the enforcement seam.** `foundryvtt-mcp@1.5.2`, pinned (tool
names and parameter shapes are version-specific; a float to latest can rename
them silently). Configured in the profile's `config.yaml` as
`mcp_servers.foundry`: `npx -y foundryvtt-mcp@1.5.2`, cwd pinned to
`ttrpg_gm/bridge`, user `mcp-api`, write access enabled, password referenced as
`${env:MCP_FOUNDRY_PASSWORD}` (never inline). The bridge exposes 33
`mcp_foundry_*` tools — the complete vocabulary the GM uses to touch the game:
read/search actors, journals, scenes, compendiums, roll tables; create/update
documents; combat; dice; tokens. Two ways to prove it live: `bash
bridge/check.sh` (Foundry answers → secret present → credentials authenticate →
tools register) and `hermes mcp test foundry --profile ttrpg`.

**4. Foundry VTT.** v14.365 on `:30000`, launchd `com.hermes.foundryvtt`.
Bound `*:30000`, so LAN and Tailscale clients join at the Mac's Tailscale IP.
Founded world management, module activation, and world-file writes are operator
actions, not bridge actions.

**5. Memory — narrative persistence.** TencentDB Agent Memory gateway on
`127.0.0.1:8421`, isolated store `~/.memory-tencentdb/ttrpg-memory`. The
profile's memory provider is `memory_tencentdb`. Recall is hybrid (keyword +
embeddings); the store is deliberately separate from the `default` and `ssdi`
stores.

**6. Pipeline (Path B).** `pipeline/ingest.py` (PDF → MarkItDown → LLM
extraction → JSON) and `pipeline/import_foundry.py` (JSON validation + import
manifest). The manifest is *executed by the GM Bot through MCP* — the pipeline
generates, it does not write to Foundry itself. There is no `create_actor`
tool in the bridge, so actors and roll tables import through the UI/compendium
path.

**7. NPC bots — first bot in build (2026-10-04).** Each significant, recurring
NPC becomes an isolated Hermes profile with its own SOUL, voice, and memory, so
the blacksmith genuinely cannot know the dungeon's secret. Design sketch:
[`npc-bots-design-sketch-2026-08-26.md`](npc-bots-design-sketch-2026-08-26.md).
Workstream settled 2026-10-04: **roster location** — `campaigns/<id>/npcs/<slug>/`
(dossier.md + soul.md + bot.yaml, campaign data layer); **maker** —
`bot/npc-maker/` (creation script, dossier standard, SOUL scaffold, model
policy); **activation** — Bot Mode bot-to-bot DM (`message_agent`; protocol
injection proven on-runtime; the old `delegate_task` protocol is retired);
**voice protocol** — the NPC answers in character, the GM relays and owns
outcomes. First NPC: **Billy Ray Spivey** (`npc-billy-ray-spivey`) — dossier and
persona authored; profile build completing this pass.

## Content intake — two paths, and only two

**Path A — purchased VTT modules (the primary path).** Acquire the adventure as
a Foundry-ready module (official Marketplace, or an external store issuing a
content activation key), redeem the key on foundryvtt.com, install it via the
Setup → Package Installer, enable it in-world, and read it out of the module's
**compendiums** — through the bridge (`search_compendium`, journal reads, actor
reads) or by importing selected pieces into the world. **No PDF tooling
anywhere in this path.** Key provenance lives in the profile env.

**Path B — PDFs (occasional, when no VTT edition exists).** The `pipeline/`
path above. It applies *sometimes*; it is not the default intake.

## Operating model — how the GM touches the game

- **MCP tools** — the mechanism for play. Every state change goes through them.
- **Browser** — visual grounding (look at the map) and UI-only operations:
  installing/enabling modules, importing compendium content, world management.
- **Desktop (cua-driver)** — full local UI control when something needs real
  clicks and drags. Used sparingly.
- **Never invented.** If the bridge is down or the tools are missing, the GM
  says so and runs narrative-only: resolve actions in chat, coach sheet changes
  as exact player taps, keep a ledger, reconcile once the seat heals.
  Fabricated Foundry state is forbidden.

## Session lifecycle

1. **Arrive oriented.** Read the recorded trail first — the live-session handoff
   doc, `STATUS.md`, the ops thread. Nothing between sessions is derived from
   scratch.
2. **Health check.** `bridge/check.sh`, and confirm the tool set is present in
   *this* session (bridge-level and session-level absence are different
   failures — see below).
3. **World ops** (when needed) — headless stop/launch, no UI:
   `POST /join {action:"shutdown", adminPassword}` then
   `POST /setup {action:"launchWorld", world, adminPassword}` with the same
   cookie jar. World-file and LevelDB edits happen **only** while the world is
   stopped.
4. **Play.** State through MCP, narration through the doctrine files, memory
   writes as the story lands.
5. **Record.** Mechanics that cost time go into the handoff doc, not into
   memory.

## Operational knowledge worth keeping (each of these cost real time)

- **Zero `mcp_foundry_*` tools has two causes.** *Bridge-level*: Foundry down or
  bad credentials ⇒ the server exits and every surface loses the tools; prove it
  with `check.sh`. *Session-level* (WebUI/Hermex): the bridge is green but this
  session's toolset was built without it — serving backends hold MCP
  registrations process-wide, and a registration left stale by an earlier world
  bounce makes later sessions skip the re-spawn. Cure ladder: `/reload-mcp` in
  the chat → a fresh chat → restart the serving backend (owner consent only).
  Evidence lives in the profile's `logs/mcp-stderr.log` and Foundry's own log
  (`Created client session` → `User authentication successful` → `Vended World
  data` marks a completed connection).
- **The `dotenv` cwd trap.** `foundryvtt-mcp` calls `dotenv.config()`, so it
  reads `.env` from its *working directory*. A stray or invalid `.env` there
  kills it at startup with an opaque "Connection closed". cwd is pinned to
  `bridge/`, and its values are kept valid (`LOG_LEVEL=info`, lowercase).
- **v14 module activation is a world setting, not a manifest field.**
  `core.moduleConfiguration` in the world's settings DB decides which modules
  load; editing `world.json`'s `modules` array does nothing.
- **Auth is pbkdf2.** Stored password = `pbkdf2Sync(pw, salt, 1000, 64,
  'sha512')`; **passwordless = pbkdf2 of the empty string**. The seat is
  passwordless by design — but always verify the join form's password field
  reads empty before submitting (saved logins and autofill both break it).
- **LevelDB datastores are locked while the world runs.** Users, settings, and
  actors DBs are LevelDB: stop the world, then use the copy-then-read pattern
  for verification and drain-then-put for writes. Back up before every write.
- **The memory gateway spawn command must be quote-free.**
  `MEMORY_TENCENTDB_GATEWAY_CMD` is expanded with `shlex.split()`, so nested
  `sh -c '…'` quoting breaks the spawn. It now points at
  `~/.hermes/scripts/memory-gateway-launch.sh <profile>`, which sources the
  profile `.env` and exports the Hermes node bin.
- **WebUI-hosted sessions need MCP creds in the WebUI's own env.**
  `${env:MCP_FOUNDRY_PASSWORD}` resolves from the *serving process* env, not the
  profile `.env`, so `~/hermes-webui/.env` carries it (mode 600) alongside
  `HERMES_WEBUI_PYTHON`. This is what makes ttrpg play possible from the phone.
- **Never coach rules from memory.** The installed system is greppable ground
  truth — its `lang/en.json` and roll implementation define skills, crit/fumble,
  and modifier steps. Check before stating odds.

## Verified state — 2026-09-29

- **Foundry VTT 14.365 running** (`:30000`, launchd `com.hermes.foundryvtt`);
  `/api/status` → world `deltagreen` active, system `deltagreen` 1.7.0.
- **Bridge live, all three gates green**: `bash bridge/check.sh` → Foundry
  responds → `MCP_FOUNDRY_PASSWORD` present → **33 tools registered**.
- **Memory store healthy with embeddings on**: `/health` → `status: ok`,
  `vectorStore: true`, `embeddingService: true`, state backend connected.
- **World provisioned and playable**: adventure module and a community chargen
  wizard installed and active (activation via `core.moduleConfiguration`);
  the player's Agent built and finished. Player role patched to allow actor and
  item creation. Details in
  [`foundry-live-session-2026-09-28.md`](foundry-live-session-2026-09-28.md).
- **GM Bot skills in place**: profile skill `foundry-vtt-gm-operations` plus the
  four campaign doctrine files, including the owner's Character & Relationship
  Doctrine (2026-09-29) and the Prohibited Clichés registry.
- **Docs site** builds `--strict` in CI and publishes to GitHub Pages.

## Roadmap

- [x] Bridge live + verified (33 tools), version pinned
- [x] Memory store isolated, embeddings live, gateway spawn fixed
- [x] Bot skills + campaign doctrine files established
- [x] Content intake paths defined (purchased modules primary, PDF secondary)
- [x] World provisioned: module installed/enabled, character creation unblocked
- [x] WebUI seat can hold Foundry creds and memory gateway (Hermex repair,
      2026-09-29)
- [ ] **Session-level MCP seating in WebUI** — make the seat reliably self-heal
      instead of needing `/reload-mcp` or a fresh chat
- [ ] Foundry Local REST API module → compendium search + diagnostics (blocked
      upstream; see `backlog.md` for the two options)
- [ ] Narrative critique loop (z.ai)
- [ ] NPC bots — maker + first NPC (Billy Ray Spivey) live 2026-10-04 (model: deepseek-flash, owner call); remaining:
      first live GM→NPC round-trip, campaign-dir persona archive, per-NPC memory decision

## Open items

- **`FOUNDRY_LICENSE_KEY` labeling.** A content activation key and the Foundry
  VTT license sit in adjacent variables (`FOUNDRY_LICENSE_KEY` /
  `FOUNDRY_LICENSE_KEY_PREV`); relabel before the next redeem attempt so the two
  cannot be confused.
- **`FOUNDRY_GM_PASSWORD` is stale** — the GM seat is passwordless; remove the
  variable.
- **`bridge/check.sh` leaves a stray process per run** — needs process-group
  kill on cleanup.
- **Foundry UPnP is enabled** (`options.json` → `upnp: true`) — turn it off
  unless remote play is actually needed.
- Restore `check.sh`-adjacent hygiene: define a supported way to run the harness
  under a timeout on macOS (`timeout` is not installed by default).

## Revision history

- **v4 (2026-09-29)** — current. Layer-by-layer ownership; verified-state ledger
  refreshed against the live runtime; session lifecycle and operational
  knowledge (auth, LevelDB, module activation, memory gateway spawn, WebUI env)
  recorded; roadmap and open items re-based.
- [v3 (2026-09-25)](ttrpg-gm-architecture-2026-09-25.md) — two intake paths
  clarified; browser/desktop operator surfaces; NPC bots pinned.
- [v2 (2026-09-01)](ttrpg-gm-architecture-2026-09-01.md) — Hermes Bot Mode as
  the GM runtime.
- [v1 (2026-08-27)](ttrpg-gm-architecture-2026-08-27.md) — first modular design.

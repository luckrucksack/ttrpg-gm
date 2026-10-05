# NPC Bot Maker

**What this is.** The standard way an NPC in a running campaign becomes a live
Hermes Bot: one isolated profile per NPC, with its own persona, voice, and
memory boundary, that the GM Bot can message at the table. The GM Bot stays the
orchestrator; NPC bots are the characters it hands a scene to when the moment
deserves a full person instead of a paragraph.

Background: `docs/npc-bots-design-sketch-2026-08-26.md`. The activation
mechanism was settled and proven on 2026-10-04 — see "Activation protocol."

> Supersedes `bot/npc-template/` (retired 2026-10-04). The old template's
> `delegate_task` activation never worked: `delegate_task` spawns a generic
> subagent in the *calling* profile and never loads another profile's SOUL,
> skills, or memory. Bot Mode's bot-to-bot messaging replaces it.

## A Bot is a profile

Each NPC is an isolated Hermes profile under `~/.hermes/profiles/npc-<slug>/`
with its own SOUL, chat history, memory, and credentials. Dormant bots cost
nothing — a profile is a config file plus an empty database until it runs.
Two Bot Mode requirements make a profile a *reachable* bot:

1. A canonical chat titled exactly **`Bot Chat`** (the forever-chat the
   messaging protocol injects into).
2. A `ui_meta: { hermes-bots: ... }` block in `profile.yaml` — at least one
   profile on the install must carry it (ttrpg does), which marks the whole
   install as Bot-Mode-managed.

The maker script handles both.

## Roster location (settled 2026-10-04)

Campaign NPC data lives in the campaign data layer (gitignored by design, see
`campaigns/README.md`):

```
campaigns/<campaign_id>/npcs/<npc-slug>/
├── dossier.md   # the answered character sheet (template: bot/npc-maker/dossier-template.md)
├── soul.md      # the bot's persona file — copied in as the profile's SOUL.md
└── bot.yaml     # title / description / model
```

The repo holds the templates and the maker; the campaign holds the content.

## Making one

```bash
bash bot/npc-maker/make-npc.sh <campaign_id> <npc_slug>
# e.g.
bash bot/npc-maker/make-npc.sh delta-green-convergence billy-ray-spivey
# re-verify an existing bot without changing it:
bash bot/npc-maker/make-npc.sh delta-green-convergence billy-ray-spivey --verify-only
# build from a draft persona file outside the campaign tree (while iterating):
bash bot/npc-maker/make-npc.sh <campaign_id> <npc_slug> --soul-source ~/path/to/persona.md
```

What the script does, in order:

1. Validates the three source files exist; reads `bot.yaml`.
2. `hermes profile create npc-<slug> --no-skills` (minimal profile; idempotent).
3. Wires the model: `model.provider openrouter`, `model.default` = the raw
   model id from `bot.yaml`. Deliberately NOT an alias: a value whose vendor
   token is a provider name — like `qwen/…` — gets re-routed by the CLI's
   provider auto-detection when it arrives via an alias. Raw ids stay on the
   configured provider (verified 2026-10-04). Plus small agent/memory limits.
4. Writes the profile `.env` by script (never by hand): only
   `OPENROUTER_API_KEY`, with a timestamped backup first. The key value is
   never printed.
5. Copies `soul.md` → profile `SOUL.md` and `dossier.md` → profile `dossier.md`.
6. Appends the Bot Mode marker (`ui_meta.hermes-bots.title`) to `profile.yaml`.
7. Creates the canonical `Bot Chat` session.
8. Prints a verification block (model, env, marker, chat).

## Model policy

- NPC bots run **free OpenRouter models** (owner constraint, 2026-10-01). The GM
  stays on `deepseek-flash`.
- The bind is **one line**: `hermes -p npc-<slug> config set model.default <model-id>`.
  Keep it a RAW model id, never an alias — an alias value starting with a
  provider vendor token (`qwen/…`) gets re-routed to that vendor's own provider
  by the CLI's auto-detection (observed 2026-10-04: alias → "Qwen CLI
  credentials not found"; the raw id routed to OpenRouter correctly).
- Model survey + bake-off guidance:
  `docs/free-models-for-npc-bots-2026-10-01.md`. Stealth/free listings rotate
  (ox-alpha died; Space Bunny expires 2026-10-05) — never hardwire.

## Activation protocol (GM side)

The GM reaches an NPC with Bot Mode's bot-to-bot DM. This is proven on the
installed runtime: a session titled `Bot Chat` carries the messaging protocol
and the `message_agent` tool, with a live teammate roster.

- **Target:** `message_agent(target="npc-<slug>", message="<brief>")` — the
  profile name, or the NPC's @handle from the roster.
- **The brief is composed by the GM** (never forward the player's words
  verbatim). A good brief: where the scene stands, what was just said or asked,
  what the NPC knows, and what the table needs from them.
- **Delivery is fire-and-forget.** The acknowledgement is not the reply; the
  NPC runs its turn (seconds, on a free model) and the reply arrives as a
  background completion notification — relay it into the scene faithfully. If
  the ack says `reply_delivery: poll`, follow its `process wait` instruction
  before ending the turn.
- **Fallback — never stall play.** If delivery fails or the reply doesn't
  arrive, run the NPC inline the way the GM always has, and flag the miss.
  A missed DM is not a missed turn.
- **Delegate vs. inline:** plot-relevant, character-deep interactions get the
  bot; flavor and small talk stay inline (design sketch, 2026-08-26).

## Voice protocol (GM side)

- The NPC answers in their own voice — their words and small physical beats
  only. No outcomes, no dice, no other characters, no world events. The GM owns
  consequences, narration, and the stop-before-decisions rule.
- The GM relays the reply faithfully: weave it into narration, compress around
  it, keep the novel register — but never contradict or extend what the NPC
  actually said.
- The full character sheet is the GM's deep reference: read the campaign copy
  (`campaigns/<id>/npcs/<slug>/dossier.md`) or the profile copy
  (`~/.hermes/profiles/npc-<slug>/dossier.md`) when a scene needs depth.
- **The prohibitions apply to NPC output too.** A bot's reply must obey the
  same Prohibited Clichés registry as GM narration
  (`bot/skills/ttrpg-prohibitions.md`); the SOUL scaffold carries the standing
  item so bots are briefed on it.

## Memory (settled for v1 — deliberate)

An NPC bot's memory for now: its canonical Bot Chat (persistent, forever —
`/new` becomes `/compact` there by design) plus its profile's built-in memory
(small, capped at 500 chars via the maker). That covers "remembers every
interaction with the party" for a played arc.

Deliberately **not** wired yet: a per-NPC TencentDB store. The mechanism exists
(`~/.hermes/scripts/memory-gateway-launch.sh <profile>` takes any profile; each
store = a port + `tdai-gateway.yaml` + env block, mirroring `ttrpg-memory`), but
each active NPC would add a gateway process. Settle that upgrade when a second
NPC or a long-lived arc genuinely needs cross-session recall. This is a
decision, not an omission.

## Lifecycle

- **Create** during campaign prep (this maker).
- **Dormant:** zero runtime cost — config + empty DB. Shows in the desktop Bots
  roster with its avatar/title.
- **Active:** runs turns when the GM messages it, or when played directly from
  the Bots tab / `hermes -p npc-<slug> chat -c "Bot Chat"`.
- **Death:** archive the profile (do not delete — retired chats and history are
  preserved; it can haunt). **Permanently gone:** delete the profile.

## Verify

```bash
hermes -p npc-<slug> config get model.default          # → the bound raw model id
hermes -p npc-<slug> config get model.provider         # → openrouter
grep -o '^[A-Z_]*=' ~/.hermes/profiles/npc-<slug>/.env # → only OPENROUTER_API_KEY
sqlite3 ~/.hermes/profiles/npc-<slug>/state.db \
  "SELECT id, title FROM sessions WHERE title='Bot Chat';"
```

First-light check (optional): run one turn in the Bot Chat and confirm the
character answers in voice.

## Status

- **2026-10-04:** Maker built; first NPC bot live — **Billy Ray Spivey**
  (profile `npc-billy-ray-spivey`). Verified end-to-end: ~7–8s turns on the
  free OpenRouter tier, Bot Mode marker + canonical Bot Chat present, messaging
  protocol injects with the live roster, first voice check in character.
  Activation settled (`message_agent`, proven on-runtime). Bake-off samples
  recorded for the binding pick; swap `model.default` (one line).

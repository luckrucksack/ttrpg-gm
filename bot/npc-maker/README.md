# NPC Bot Maker

**What this is.** The standard way an NPC in a running campaign becomes a live
Hermes Bot: one isolated profile per NPC, with its own persona, voice, and
memory boundary, that the GM Bot can message at the table. The GM Bot stays the
orchestrator; NPC bots are the characters it hands a scene to when the moment
deserves a full person instead of a paragraph.

Background: `docs/npc-bots-design-sketch-2026-08-26.md`. The activation
mechanism was settled and proven on 2026-10-04 — see "Activation protocol."
Base structure v2 (2026-10-09) — context isolation, tool lockdown, memory
stance, verification tooling — is defined in
`docs/npc-bot-base-structure-v2-2026-10-09.md`.

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
└── bot.yaml     # title / description / model (+ optional provider)
```

The repo holds the templates and the maker; the campaign holds the content.

## Making one

```bash
bash bot/npc-maker/make-npc.sh <campaign_id> <npc_slug>
# e.g.
bash bot/npc-maker/make-npc.sh delta-green-convergence billy-ray-spivey
# re-verify an existing bot without changing it:
bash bot/npc-maker/make-npc.sh delta-green-convergence billy-ray-spivey --verify-only
# re-verify + one live voice turn into the Bot Chat (evidence in logs/agent.log):
bash bot/npc-maker/make-npc.sh delta-green-convergence billy-ray-spivey --verify-only --smoke
# build from a draft persona file outside the campaign tree (while iterating):
bash bot/npc-maker/make-npc.sh <campaign_id> <npc_slug> --soul-source ~/path/to/persona.md
```

What the script does, in order:

1. Validates sources; reads `bot.yaml`. On a refresh (profile already exists),
   a missing `soul.md` / `dossier.md` source is tolerated — the profile's
   existing copy is kept and noted, so a bot can be re-verified and re-tuned
   before its canon write lands.
2. `hermes profile create npc-<slug> --no-skills` (minimal profile; idempotent).
3. Wires the model: `model.provider` + `model.default` from `bot.yaml` (defaults:
   `deepseek` / `deepseek-flash` — same stack as the GM). Deliberately NOT an
   alias: a value whose vendor token is a provider name — like `qwen/…` — gets
   re-routed by the CLI's provider auto-detection when it arrives via an alias.
   Raw ids stay on the configured provider (verified 2026-10-04). Plus small
   agent/memory limits (memory cap 1000 chars).
4. Context isolation (v2): pins `terminal.cwd` to the profile's own empty
   `workspace/` dir, so no project context (AGENTS.md, git snapshots) can load
   into a character prompt from wherever a turn is launched.
5. Tools policy (v2): disables every toolset except `memory`
   (`NPC_KEEP_TOOLSETS` overrides). `message_agent` is Bot Mode-injected, not a
   toolset — it survives the lockdown.
6. Writes the profile `.env` by script (never by hand): only the provider's
   key (`DEEPSEEK_API_KEY` by default; `OPENROUTER_API_KEY` for cost-mode
   swaps), with a timestamped backup first. The key value is never printed.
7. Copies `soul.md` → `SOUL.md` and `dossier.md` → `dossier.md` (skipping what
   a refresh is keeping).
8. Appends the Bot Mode marker (`ui_meta.hermes-bots.title`) to `profile.yaml`.
9. Creates the canonical `Bot Chat` session (from the neutral workspace).
10. Prints a verification block — model, provider, env keys, marker,
    `terminal.cwd`, enabled toolsets, memory limits, persona/dossier, Bot Chat.
11. `--smoke` (opt-in): one live voice turn into the Bot Chat + the
    `agent.log` turn line as evidence.

## Model policy

- NPCs run the **same model stack as the GM** — default `deepseek-flash` on the
  `deepseek` provider (owner call, 2026-10-04; supersedes the earlier
  free-OpenRouter-for-NPCs constraint). One provider, one credential story, no
  free-tier rate roulette mid-scene.
- The bind is **one line**: `hermes -p npc-<slug> config set model.default <model-id>`.
  Keep it a RAW model id, never an alias — an alias value starting with a
  provider vendor token (`qwen/…`) gets re-routed to that vendor's own provider
  by the CLI's auto-detection (observed 2026-10-04: alias → "Qwen CLI
  credentials not found"; the raw id routed to OpenRouter correctly).
- Cost-mode option (documented, not default): the free-model survey + bake-off
  (`docs/free-models-for-npc-bots-2026-10-01.md`) remains the reference for
  swapping an NPC to a $0 model if cost ever demands; the swap stays one line.
- **Sessions remember their model.** After any switch, sessions keep the OLD
  model as their stored pin until their rows are updated — run
  `bash bot/npc-maker/repin-model.sh <npc_slug>`: it backs up `state.db`,
  re-pins every session to the profile's current stack (model + billing
  fields; base URL from the GM profile's known-good same-stack session), and
  proves the effective model with one live resumed turn + the bot's
  `logs/agent.log` (`conversation turn: … model=`). `-m` on the CLI is
  per-invocation only; config readback alone proves nothing. Keep `bot.yaml`
  in sync so maker rebuilds don't regress.

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
  actually said. The relay is invisible: the fiction never mentions bots,
  relays, or process (owner directive 2026-10-04).
- **Bot-voice marker (owner-directed 2026-10-04; in force 2026-10-08).** A
  relayed line carries a caret with no space immediately before its opening
  quote — `^"Was it me, sir."` — the player-visible signal that the NPC's own
  bot spoke it. Only bot-backed lines carry it; GM-invented voices (and inline
  fallbacks) stay unmarked. The one deliberate exception to the invisible
  relay.
- The full character sheet is the GM's deep reference: read the campaign copy
  (`campaigns/<id>/npcs/<slug>/dossier.md`) or the profile copy
  (`~/.hermes/profiles/npc-<slug>/dossier.md`) when a scene needs depth.
- **The prohibitions apply to NPC output too.** A bot's reply must obey the
  same Prohibited Clichés registry as GM narration
  (`bot/skills/ttrpg-prohibitions.md`); the SOUL scaffold carries the standing
  item so bots are briefed on it.

## Memory (three layers — settled 2026-10-09)

1. **The canonical Bot Chat** — the forever-chat; `/new` becomes `/compact`
   there by design. The operative memory of play.
2. **Built-in `MEMORY.md`** per profile — the memory toolset is the one tool
   left enabled; the maker caps it at 1000 chars so a bot can keep compact,
   durable notes.
3. **Not default — per-NPC TencentDB store** for semantic recall when a long
   arc genuinely needs it. The mechanism exists
   (`~/.hermes/scripts/memory-gateway-launch.sh <profile>` takes any profile;
   each store = a port + `tdai-gateway.yaml` + env block, mirroring
   `ttrpg-memory`), but each active NPC would add a gateway process — dormant
   bots cost $0 by design. Enable per NPC when needed; full stance in
   `docs/npc-bot-base-structure-v2-2026-10-09.md`. This is a decision, not an
   omission.

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
hermes -p npc-<slug> config get model.provider         # → deepseek (or chosen provider)
grep -o '^[A-Z_]*=' ~/.hermes/profiles/npc-<slug>/.env # → the provider key(s) present
sqlite3 ~/.hermes/profiles/npc-<slug>/state.db \
  "SELECT id, title FROM sessions WHERE title='Bot Chat';"
```

First-light check (optional): run one turn in the Bot Chat and confirm the
character answers in voice. Faster paths: `--verify-only` (read-only drift
check across all of the above) and `--verify-only --smoke` (adds one live
voice turn with evidence).

## Status

- **2026-10-04:** Maker built; first NPC bot live — **Billy Ray Spivey**
  (profile `npc-billy-ray-spivey`), running `deepseek-flash` (owner call — same
  stack as the GM; supersedes the free-model bind). Verified end-to-end: ~7s
  turns, Bot Mode marker + canonical Bot Chat present, messaging protocol
  injects with the live roster, first voice check in character. Activation
  settled (`message_agent`, proven on-runtime). Free-model survey retained as
  the cost-mode swap reference; swap = `model.default` (one line).
- **2026-10-08:** Bot-voice marker in force (decided 2026-10-04): a caret with
  no space before the opening quote of a bot-spoken line (`^"…"`) — the
  player-visible signal that an activated bot is speaking. Written into both GM
  skills (`ttrpg-campaign-tools`, `ttrpg-narrator`) and the voice protocol
  above.
- **2026-10-08 (later):** Roster expanded for *Convergence* — five more bots
  built end-to-end from the Literary Build standard: **Sheriff Dan Oakley**
  (`npc-dan-oakley`), **Frank Carincola** (`npc-frank-carincola`), **Jane
  Allen** (`npc-jane-allen`), **Angel Spivey** (`npc-angel-spivey`), **James
  Derringer** (`npc-james-derringer`). Profiles verified + voice-checked
  in-character (~3–4 s turns). Dossiers are first drafts pending the owner's
  pass; the six campaign-side `soul.md` canon writes (incl. Billy's backfill)
  are queued as one watched approval sitting — profiles were built from staged
  drafts via `--soul-source` until then.
- **2026-10-09:** Base structure v2 (see
  `docs/npc-bot-base-structure-v2-2026-10-09.md`). Context isolation
  (`terminal.cwd` → per-bot empty `workspace/`; stored-prompt audit clean),
  tools policy (`memory` only; `message_agent` stays Bot Mode-injected; NPC
  prompt ~66k → ~18k chars), memory limit 1000 with the three-layer stance
  settled, maker `--smoke` live verification, and `repin-model.sh` for safe
  session model re-pins. Applied + live-verified across all six bots
  (in-voice smokes; full GM → NPC → GM round trip landed on the rail).

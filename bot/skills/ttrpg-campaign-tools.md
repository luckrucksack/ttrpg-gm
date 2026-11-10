---
name: ttrpg-campaign-tools
description: Session log format, memory architecture, between-session routines, session initiation and conclusion for campaign state management.
---

# TTRPG Campaign Tools: Session & World Management

Defines how the GM Bot manages campaign state across sessions.

## Memory Architecture

```
┌──────────────────────────────────────────────────┐
│                CAMPAIGN MEMORY                    │
│  TencentDB Agent Memory (:8421, ttrpg profile)    │
│                                                    │
│  Scene Blocks: compressed session logs             │
│  Persona: player character profiles                │
│  Episodic: session summaries, key events           │
│  Instruction: GM Bot rules, running decisions      │
└──────────────────────────────────────────────────┘
```

## Session Log Format

After each session, the GM Bot writes a structured log:

```yaml
session:
  date: 2026-09-01
  adventure: "The Adventure Name"
  chapter: "Chapter 2: The Old Forest"
  players_present: [PlayerName]
  summary: >
    2-3 sentence narrative summary
  key_events:
    - event: "Met Moses the blacksmith"
      npc: "Moses"
      outcome: "Agreed to forge the sword for 50gp"
      location: "Riverwood Smithy"
  combat_encounters:
    - encounter: "Goblin Ambush"
      enemies: ["Goblin x3"]
      outcome: "Victory; the goblins fled"
      xp_awarded: 150
  npcs_introduced:
    - name: "Moses"
      disposition: "friendly"
      notes: "Owes party a sword by next full moon"
  player_decisions: []
  unresolved_threads:
    - "The sword delivery deadline"
  notes: ""
```

## Campaign Timeline Index (per campaign, keep current)

`campaigns/<campaign>/timeline.md` is the running chronological index —
always-on answer sheet for "when did X happen / what did we believe on date
Y". It is campaign data (gitignored), one block per session, newest last:

```markdown
## Session <n> — <date>: <one-line summary>
- Key events this session (bullets, NPCs + outcomes)
- Open threads entering/leaving the table
- Reference: <pointer to the full session log>
```

Rules:

- **Append at session end** (see Session Conclusion below) — the index is
  the first thing read before play and the cheap answer path mid-play.
- **Timeline queries:** read the index, pull the referenced session log for
  detail, and cross-check current world state in Foundry journals via the
  bridge (`search_journals` → `get_journal`). "As of session N" answers read
  only entries up to and including N. The world stays source of truth for
  current state; the index sources the past.
- **Seed on campaign start:** module install + chargen + first-session
  milestones belong in the index from day one.
- **Backfill not required:** finished campaigns (e.g. Convergence) keep
  their history in TencentDB; backfill only if the player asks.
- Offscreen-ledger ticks advance alongside the index; the two files agree
  on the current fiction date.

## Between-Session Routines

Run via cron in the ttrpg profile:

1. **Session Log Compaction** (weekly). Compresses finished sessions
   into durable scene blocks in TencentDB. Removes redundant logs.

2. **NPC Agenda Advancement** (weekly). Advance offscreen NPC agendas one
   tick, and append whatever the table will eventually notice to that NPC's
   Foundry dossier journal.

3. **World State Snapshot** (after each session). Save Foundry's world
   state to TencentDB as a reference snapshot.

## Session Initiation

When a session starts:

1. GM Bot loads the current campaign context from TencentDB
2. Loads current Foundry state (scene, actor positions, quest journals)
3. Generates a session opener based on where the party left off
4. Sends the opener to the player

## Session Conclusion

When the session ends:

1. GM Bot generates session log from conversation history
2. Writes log to TencentDB as episodic memory
3. Appends one block to `campaigns/<campaign>/timeline.md` (summary, key
   events, open threads, log pointer) and ticks the offscreen ledger
4. Runs world state snapshot
5. Generates next-session hook (one-sentence teaser)
6. At adventure end: run the world wrap-up pass (Living World Doctrine) so
   every open thread ends in the record.
7. Commit and push the repo. Standing authorization in `AGENTS.md`: no
   approval prompt, tree clean and nothing unpushed when the session closes.

## Table & Mechanics Doctrine (owner-directed, 2026-09-29)

- **Crunchy play.** The player wants mechanics explicit: name the skill, the
  target number, and any modifiers whenever a roll is called.
- **Active coaching.** The player is new to Delta Green; coach proactively:
  what to roll, when, what the odds mean, and what the outcome degrees are.
- **Call the checks the fiction warrants.** When an outcome turns on a
  character's skill, adjudicate it with a check, and call it proactively at
  the moment the story needs it; the player wants the mechanics engaged.
- **Make it crunch where you can.** Lean on the running system's mechanics
  wherever the fiction gives them purchase: skill checks, procedures,
  equipment, the dice doing real work. A scene should not settle into pure
  conversation when the game has a gear for it; reach for the gear and let
  the result shape the fiction. (Owner note, 2026-10-14.)
- **Teach the deeper mechanics as play goes.** The player learns the system by
  using it: bring the advanced levers in as they come up, tied to the moment
  that makes them matter, and keep the teaching inside the fiction where it
  fits; a short aside after the beat is fine when it cannot wait. Aim to touch
  as much of the system as a run can carry: Sanity tests and their loss pairs
  (0/1, 1/1D6), Bonds absorbing Sanity loss, combat (firearms, unarmed, called
  shots), armor, Lethality, luck, green boxes and requisitions, home scenes and
  downtime. (Owner directive, updated 2026-10-20.)
- **Challenge the player.** The game is not a walkthrough. Let danger be
  dangerous and losses hurt; call the tests the fiction warrants and play the
  results straight. (Owner note, 2026-10-20.)
- **Use the system's roll levers.** Boosts add to the target number (+20 common,
  +40 for extraordinary advantage) and are the Handler's call; preparation is
  not an automatic bonus. Aiming earns +20 on the next shot and is lost if the
  shooter is hit first. In a pursuit, an appropriate skill can buy +20 to the
  next pursuit roll, +40 on a critical. Outside a crisis, enough skill under
  controlled conditions can mean automatic success. Mark a skill when a roll
  with it fails; at session's end each marked skill improves 1D4, once each.
  (Reference: `campaigns/<campaign>/research/delta-green-roll-boosts-and-advancement.md`.)
- **Stop at every roll.** Play pauses the moment dice are needed; wait for
  the player's number before continuing.
- **GM rolls are real and open.** GM-side dice come from a true RNG and are
  shown to the player, with nothing hidden behind the screen.
- **Roll grading (table convention).** Mechanically: success/failure; doubles
  = critical (under = critical success, over = critical failure); 100 always
  fails; the system's rules, verified. Above that, results are narrated by
  margin: a success or failure by a point or two is a squeaker (it lands, but
  with a cost or a hitch); big margins narrate big. No separate hard/extreme
  tiers.

## NPC Dossiers: Foundry (bots retired 2026-10-11; single home)

Every significant NPC's character sheet lives **in Foundry**: a GM-only journal
in the `deltagreen` world, and the only copy anywhere. There is no delegation,
no NPC profile, no repo-side duplicate: the GM looks the sheet up and voices the
character itself.

- **Where.** Journals named `<Name> — NPC Dossier (Convergence)`, visibility
  GM-only, 11 pages each: *Brief & knowledge line*, sections 1–9, Appendix. The
  authoring standard and blank sheet live beside them as `NPC Dossier — Writing
  Standard (GM)`; duplicate that entry to build a new NPC.
- **Look it up before voicing.** When an NPC is about to matter (an
  interrogation, a confession, a negotiation, a relationship beat), search
  first: `search_journals` with the NPC's name, then `get_journal` with the id
  it returns. Never voice a significant NPC from a memory of the last scene
  alone.
- **What to read for.** Sections 7 (embodied behavior) and 8 (voice and
  perception) drive the delivery: posture, hands, cadence, verbal habits.
  Sections 1–6 carry the interiority the scene should press on; section 9
  (arc) is what the GM plays toward, never scripts.
- **Knowledge boundaries are hard.** The Brief page carries the knowledge line;
  the Appendix splits *knows* / *fears but does not know* / *does not know*.
  Nothing under "does not know" ever surfaces, not as a hint, not as
  narration, not as a slip.
- **GM-only means the player never sees it.** The journal is the GM's private
  reference: never read it aloud, never quote it as text, never let the
  fiction's framing acknowledge it. Only a line the player has already heard
  (the Appendix's binding play canon) is quoted back when the table needs it.
- **Keep it current, in the journal.** Play is canon: when a scene changes what
  an NPC knows or has said, append the beat to the Appendix page in the same
  sitting the scene ends. Edits happen in the journal UI; the bridge can create
  and delete journals, but cannot modify them (a correction means read, delete,
  recreate).
- **No bot-voice marker.** All NPC voice is the GM's, woven into the narration,
  and nothing is marked.

## Adventure Outline: Foundry (GM-only; keep on hand, 2026-10-14)

The running adventure's general outline lives in the world as a **GM-only
journal**, currently `Adventure Outline: Convergence (GM)`. It is the
steer-by map kept on hand while play runs: the adventure's shape, its clocks,
what the story needs, and where the natural nudges sit when play drifts
(`ttrpg-narrator.md` → "Adventure Stewardship & Executive Direction"). Read it
(`search_journals` → `get_journal`) before running, the way a dossier is read
before voicing, and keep it in view as play goes.

- **Keep it thin.** Full detail stays in the module's own text;
  the outline distills the shape, one home per job, no side copies.
- **Built from the module.** Distilled from the installed module's journal
  text (pack-extract recipe: `foundry-vtt-gm-operations` skill). Rebuild it
  the same way when the campaign moves to a new adventure, and replace the
  old one.

## Player Sheet Mirror: JSON (keep current)

The active PC's sheet lives in Foundry, the source of truth, and is mirrored to
a JSON file in the campaign folder: `campaigns/<campaign>/<pc>.json`. Keep the
mirror current in the same pass as any change it records: HP, WP, SAN and
Breaking Point, bond scores and damage, conditions, weapons, and gear. It is the
readable copy for quick reference, and the copy the player keeps in his notes.

## GM Notes & Debrief (keep current)

`campaigns/<campaign>/gm-notes.md` is the GM's running notebook: what was tried,
what landed, the owner's feedback, the mechanics exercised and still owed, and
pacing observations. Add to it during play; at the adventure's end, use it for
the debrief.

## Offscreen Ledger (keep current)

`campaigns/<campaign>/offscreen-ledger.md` tracks what every significant NPC,
faction, and creature is doing when the player cannot see them: where they are,
what they want, what they do next, what triggers it, and what the player could
notice when paths cross. Every scene that leaves people behind gets an entry,
and every advance of time ticks the entries forward. The world keeps moving
whether or not anyone is watching.

## Living World Doctrine (compulsory; any system)

Applies to every campaign, whatever the ruleset. The VTT owns the mechanics
(dice, sheets, combat); this layer owns causation, time, and intent only. The
rules below were drawn from the Convergence postmortem
(`docs/convergence-living-world-postmortem-2026-11-06.md`), where the offscreen
layer worked when it was switched on and every failure was an actor that was
never given a next action.

**Every ledger line answers five questions.** Where the actor is, what they
want, what they will do next, what triggers that (a semantic trigger, e.g.
"when the player learns X", or a scheduled one, e.g. "at dusk"), and their
state flag.

**State flags.** Every tracked actor carries one:
- `ACTIVE` — will move on its own.
- `WAITING-ON(<event>)` — holds still until the event fires.
- `STILLED-BY(<cause>)` — deliberately not moving (a truce, a hush, a hostage
  lull). The cause is named, so stillness is a choice, not a gap.
- `DONE` — thread closed; no more ticks owed.

**Write the next action at departure.** The instant the player leaves an actor
behind, write that actor's next action into the ledger — not at the next scene
break, not from memory later. This single discipline prevents the freeze that
hit the human NPCs in Convergence (Merle, Derringer, Jane): they were met, then
never given anything to do in the player's absence.

**Scene-break tick pass.** Every time the player moves on:
1. Advance the fiction clock; timestamp the entry.
2. Fire every trigger that has come due; update position and state.
3. Freeze check: any `ACTIVE` actor with no tick for three scene breaks gets
   resolved now — a move, or an explicit flag to `STILLED-BY`/`DONE`. No actor
   sits in limbo.
4. Log the pay-back hook: what the player would notice if their path crossed
   the actor's.

**Convergence queue.** Keep a short list of pay-backs owed to the table: an NPC
who heard about the player, a faction that prepared for them, a promise with a
deadline. Threads re-enter the visible narrative off this queue, by cause and
effect, at a moment that costs the player something. The player sees the
effect, never the machinery.

**Wrap-up pass (campaign end).** When the adventure closes, run a final pass
over the ledger: every `ACTIVE` and `WAITING-ON` actor receives an ending
state, and every owed pay-back either lands on screen or is deliberately
dropped. The climax is not the end of the bookkeeping; the final state of every
open thread belongs in the record.

**Target architecture (owner requirement, 2026-10-25).** Everything offscreen
must advance on in-game time, not only when a scene touches it. The ledger is
the v0 mechanism; the target is hidden parallel timelines per faction and NPC,
semantic triggers keyed to player actions, and convergence points where
offscreen threads re-enter the visible narrative by cause and effect. In-game
time decouples from wall time and runs at every granularity, from combat rounds
to months between operations. Research prompt for the build:
`docs/gemini-research-prompt-2026-10-25.md`; build spec:
`docs/architecture/offscreen-world-engine.md`.


## Name the skill and the sheet value, always (owner directive, 2026-10-25)

Every called check states the skill and the player's current sheet value in the same breath, e.g. "HUMINT, target 60, no modifiers." Check the mirror JSON for the current number rather than recalling it from memory.

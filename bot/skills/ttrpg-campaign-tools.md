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
3. Runs world state snapshot
4. Generates next-session hook (one-sentence teaser)

## Table & Mechanics Doctrine (owner-directed, 2026-09-29)

- **Crunchy play.** The player wants mechanics explicit: name the skill, the
  target number, and any modifiers whenever a roll is called.
- **Active coaching.** The player is new to Delta Green; coach proactively:
  what to roll, when, what the odds mean, and what the outcome degrees are.
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

---
name: ttrpg-campaign-tools
description: Session log format, memory architecture, between-session routines, session initiation and conclusion for campaign state management.
---

# TTRPG Campaign Tools — Session & World Management

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
      outcome: "Victory — goblins fled"
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

1. **Session Log Compaction** — weekly. Compresses finished sessions
   into durable scene blocks in TencentDB. Removes redundant logs.

2. **NPC Agenda Advancement** — weekly. For NPCs with cron routines,
   advance their agendas one tick. If the NPC Bot detects the result
   is significant for the party, flag it to the GM Bot.

3. **World State Snapshot** — after each session. Save Foundry's world
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
- **Active coaching.** The player is new to Delta Green — coach proactively:
  what to roll, when, what the odds mean, and what the outcome degrees are.
- **Stop at every roll.** Play pauses the moment dice are needed; wait for
  the player's number before continuing.
- **GM rolls are real and open.** GM-side dice come from a true RNG and are
  shown to the player — nothing hidden behind the screen.
- **Roll grading (table convention).** Mechanically: success/failure; doubles
  = critical (under = critical success, over = critical failure); 100 always
  fails — the system's rules, verified. Above that, results are narrated by
  margin: a success or failure by a point or two is a squeaker (it lands, but
  with a cost or a hitch); big margins narrate big. No separate hard/extreme
  tiers.

## NPC Bots — Activation & Voice Protocol (built 2026-10-04)

Significant NPCs run as isolated Hermes Bots (one profile per NPC). When a scene
goes deep with one of them, the GM hands the scene to the NPC's bot. Maker and
full doctrine: `~/ttrpg_gm/bot/npc-maker/`.

- **When to delegate.** Plot-relevant, character-deep interactions —
  interrogations, confessions, negotiations, relationship beats — go to the NPC
  Bot. Flavor and small talk stay inline.
- **How to activate.** Send a scene brief:
  `message_agent(target="npc-<slug>", message="<brief>")`. Compose the brief —
  never forward the player's words verbatim: where the scene stands, what was
  just said or asked, anything the NPC knows that matters, and what the table
  needs from them. Current roster: `npc-billy-ray-spivey` (Billy Ray Spivey).
- **Receiving the reply.** Fire-and-forget: the acknowledgement is not the
  reply. The NPC answers on a free model (seconds); the reply arrives as a
  completion notification — relay it into the scene faithfully. If delivery
  fails, do not stall play: run the NPC inline as always, and flag the miss.
- **Voice discipline.** The NPC answers in their own voice — words and small
  beats only: no outcomes, no dice, no other characters, no world events. The GM
  keeps consequences, narration, and the stop-before-decisions rule. Weave the
  NPC's words in; never contradict or extend them. Full character sheet:
  `campaigns/<campaign_id>/npcs/<slug>/dossier.md` — read it when a scene needs
  depth.
- **Knowledge boundaries are hard.** An NPC bot knows only what the character
  knows; the dossier marks the line. Never brief them past it, and never let
  them leak what they don't know.
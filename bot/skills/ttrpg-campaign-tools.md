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
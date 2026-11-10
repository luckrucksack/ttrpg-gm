# Convergence: Living-World Postmortem — 2026-11-06

Status: analysis of the complete Delta Green "Convergence" campaign record
(campaigns/delta-green-convergence/: offscreen-ledger.md, gm-notes.md,
player-notes.md; docs/foundry-live-session-2026-09-28.md; ttrpg Bot Chat
transcripts). Purpose: find where NPCs failed to act offscreen, where they
lived, and turn both into rules for the offscreen world engine
(docs/architecture/offscreen-world-engine.md).

## TL;DR

The world engine works when it is switched on. Every strong offscreen moment
clusters in the final ~36 in-fiction hours, after the ledger started
(2026-10-24, two days before the campaign ended). Most of the campaign ran
with no offscreen layer at all, and the failures concentrate exactly where the
light was not on: lone human NPCs with phones, motives, and no tick. The
monster faction ticked; the people did not.

## Evidence base / caveats

- The ledger's last entry is Day 3 ~8:15 a.m. The campaign continued past it
  (quarantine at 9, Frank at 1 p.m., ending 2, Majestic). The finale's
  world-state is unrecorded — whether the board moved, whether Majestic
  arrived, is not in the record. Analyse accordingly: two kinds of failure
  below, ones proven by the record and ones that are record-gaps. Both count.

## Failures — NPCs that froze after the scene broke

1. **Merle Barn, post-confession — the worst.** He makes exactly one
   offscreen move (a genuinely good one: he files a complaint against the
   federal man who shot out his window — lawfare, "the complaint is on the
   record"). Then: "sat up all night at his desk. He knows what sealing the
   barn means and what it makes him." The man who knows the network will
   kill him for talking, who is the richest man in town, who has a phone —
   never warns the board, never flees, never burns evidence, never comes for
   Musky, and the network never collects him. Gone from the record at dawn.
2. **Derringer (SAC) — the handler's ghost.** "Knoxville. Waiting for a
   report." once, and then total silence through a fire, a federal
   complaint, a quarantine, a sealed barn. A Delta Green handler with a
   compromised agent in a hot county would call, send assets, or start
   covering tracks. The player's own open question ("What does Derringer
   actually want me to find?") never gets answered on record. He is the
   player's boss; his stillness is the loudest absence in the campaign.
3. **Angel Spivey + Joe** — one ledger line ("At the farm with Amy and Joe.
   Waiting.") and never another. Waiting for what was never defined. The
   "ask her plain some other time" hook (player notes) never pays. She is
   the boy's mother, uncompromised, the most motivated human in the county.
4. **Jane Allen — the central clock stops.** She is moved to Knoxville
   General with a deputy on the door and "asked after Musky" (a good beat).
   Then nothing: no CDC interest, no board attempt to retrieve her, no
   labour scare, no Frazier follow-up. The pregnancy clock that the whole
   scenario turns on goes dark exactly when it should be loudest.
5. **Frank Carincola + the Phenomen-X crew** — "holds the story until 1
   p.m., then calls New York" is his final state. A TV producer holding 40
   seconds of lights footage, with a dead source in room nine, a burned
   motel, a federal agent in town and a quarantine going up — his own
   dossier says the crew comes on day three and his scenes are "a clock the
   agents wind or waste." The clock never fires; the crew never arrives.
6. **Three seeded set-ups with no resolution:** the ramp "may have been
   bait" (the network anticipated Musky — the best set-up in the ledger),
   the board gathering at the hall when the barn goes dark, and the
   morning depot check. All pending when the ledger stops; none resolved
   on record. Unpaid set-ups retroactively feel like the world was fake.
7. **The board / Town Hall** — pre-decided as a mid-investigation lead,
   and then the faction exists only as ledger furniture ("None of them go
   home", "will gather at the hall, not scatter"). No on-screen
   intersection with the player anywhere in the record.
8. **Adams's laptop route** — seeded "pending" in the pre-decisions, never
   followed and never closed; the world's second route to the barn simply
   evaporated (the ridge flight-path route carried the campaign).

## Successes — NPCs that lived offscreen

1. **The one-hour network cascade (the gold standard).** After the fire:
   "Their network moved within the hour: the board was told what burned and
   who did it. The chief deputy was told. A watch is being put on the
   reservoir and the north ramp." NPCs communicating about the player and
   preparing against him — exactly the requested behaviour.
2. **Anticipation of routine.** "The lookout that was supposed to watch the
   ramp never showed. The network anticipated Musky tonight; the ramp may
   have been bait." The world observed the player's pattern (Tuesday
   tanker run) and adapted its plan around it.
3. **Independent survival.** The tub mass: "not in the burned room. It
   went down the drain into the town main before the fire." The player
   returned to a scene the world had already changed without him.
4. **Oakley — the best-tended NPC.** Between scenes he moved (Knoxville
   trip), his situation evolved (no warrant and knows it; trust tested;
   "I am getting hard to help, Jouse"), his knowledge was interrogated.
   He is the NPC who stayed in contact with the player and got ticked —
   the two conditions that kept him warm.
5. **Pre-existing world.** NRO DELTA's staging (state land bought in
   June, fenced, guard) answered the chopper question before it was given
   a shape; and Derringer's standing order had primed Oakley before the
   player arrived ("he expects you; he goes sour if treated like
   furniture"). Offscreen causation the player never saw — exactly right.
6. **Passive sensors.** Oakley as listening device for the mi-go means the
   network's knowledge plausibly rode in on every scene Musky played with
   the sheriff. The one compromised-NPC-as-window pattern that paid off.

## The pattern (why the successes clustered)

Successes share: a faction with strong goals, a clear event, a schedule
(tanker Tuesdays, "moved within the hour"). Failures share: a lone human,
diffuse goals, quiet time, and no schedule. The ledger gave the network a
goal structure the module already supplied; it gave the people nothing to
do when the player left the room — so they did nothing.

## Rules for the offscreen world engine

1. **Reaction functions for every tracked NPC, not just factions.** "X
   hears Y → X does Z by time T." Derive them from the dossiers — they
   already contain them (Frank's day-three crew, Oakley's arc toward the
   moment of truth). The engine imports reactions; the GM doesn't invent
   them mid-scene.
2. **Explicit state flags per NPC: ACTIVE / WAITING-ON(<trigger>) /
   STILLED-BY(<cause>) / DONE.** Some stillness is the horror tone (the
   board's hush, protomatter-sedated Nancy). Flags make stillness an
   intentional annotation instead of an accident, and make a freeze audit
   possible. Derringer as WAITING-ON(a report) would have read as a
   missed beat; Derringer as DONE would have read as a choice.
3. **Owed-beats queue.** Every ticked NPC owes an on-screen or reachable
   pay-back. The engine schedules the convergence (Angels' farm again,
   Frank's 1 p.m. call surfacing on a radio at the cordon), so "paid back
   on screen" stops being a hope.
4. **Freeze detector.** Any NPC not ticked in N scene-breaks gets asked in
   the tick pass: why is X still identical? This would have caught Merle,
   Angel, Derringer, Jane and Frank by dawn of Day 3.
5. **Advance the ledger through the finale.** The last scene break is not
   the end: run a world wrap-up pass that closes or defuses every pending
   consequence (the bait, the watch, the depot check, Majestic's
   arrival, the board's gathering). The climax is where the engine earns
   its keep and where this campaign went blind.
6. **Write the NPC's next action when the player leaves them**, not at
   some later tick. The scene-break hook already exists in doctrine; this
   makes the reaction the departure-event itself rather than a later
   memory scan.

## What this changes

- `docs/architecture/offscreen-world-engine.md` — rules folded into the
  target architecture (see that file).
- This postmortem is the evidence base for the prototype's tick pass and
  event table schema (Next steps in the engine doc).

Evidence files: campaigns/delta-green-convergence/offscreen-ledger.md
(entries Day 3 afternoon → 8:15 a.m.), gm-notes.md (Oct 24 doctrine line:
"NPCs are ticked forward between scenes and paid back on screen"),
player-notes.md (open questions), ttrpg Bot Chat transcripts (scene-level
play record, 2026-09-29 → 2026-10-27).
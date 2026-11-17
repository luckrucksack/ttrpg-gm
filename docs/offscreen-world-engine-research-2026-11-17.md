# Offscreen world engine — prior art and recommended architecture

2026-11-17. Answers `docs/gemini-research-prompt-2026-10-25.md`, constrained by `docs/architecture/offscreen-world-engine.md` and `docs/convergence-living-world-postmortem-2026-11-06.md`.

Three requirements decide the design: in-game time jumpable from seconds to months, causal but invisible offscreen state, and an LLM outside the inner loop.

## Prior art

**LLM world simulations.** Generative agents run a 25-agent town on memory, reflection, and planning, every actor an LLM (Park et al., 2023, https://arxiv.org/abs/2304.03442), so cost scales with population. Concordia is the closest published match: a special Game Master entity simulates the environment and resolves natural-language actions, with an engine assigning player/GM roles per `run_loop` and supporting asynchronous action (DeepMind, https://github.com/google-deepmind/concordia). AI Town runs agents in a real-time game loop with async LLM calls to separate tables (a16z, https://github.com/a16z-infra/ai-town/blob/main/ARCHITECTURE.md). All simulate actors; none has an explicit mechanism for deferred consequences.

**Narrative selection.** A storylet is content with prerequisites and effects on world state; qualities can be anything (Short, 2019, https://emshort.blog/2019/11/29/storylets-you-want-them). Salience-based narrative picks the most applicable content rather than letting the player choose (Short, 2016, https://emshort.blog/2016/04/12/beyond-branching-quality-based-and-salience-based-narrative-structures). Ryan's chronicler → story sifter → narrativizer split states the layer I need: the world records what happened, a sifter finds narratively potent material in that record, a narrativizer tells it (Ryan, 2018, https://jamesryan.computer/thesis/05-refining-emergent-narrative.md). Viv implements that sifting as an engine that detects emergent storylines as they develop (Sifty, https://viv.sifty.studio/).

**Drama management.** Façade's invisible drama manager adds or retracts behaviours, organised into beats with author-set preconditions and effects (Mateas & Stern, 2003, https://users.soe.ucsc.edu/~michaelm/publications/mateas-gdc2003.pdf). Left 4 Dead's Director paces separately: estimate survivor intensity, then build, sustain, and fade threat populations (Booth, 2009, https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf). RimWorld's storytellers are the reduced form: an "unseeable God" with no body that periodically creates events (RimWorld Wiki, https://rimworldwiki.com/wiki/AI_Storytellers). Pacing is a controller over event supply, not a world property.

**Authored behaviour and memory.** Versu authored character-agnostic social practices, separating roles from the characters filling them (Evans & Short, 2014, https://versu.com/wp-content/uploads/2014/05/versu.pdf). Shadow of Mordor's Nemesis system lets NPCs remember prior interactions and react later (https://en.wikipedia.org/wiki/Nemesis_system). Remembered, authored state reads as agency; generative prose does not. The postmortem's rule follows: import reactions from dossiers, don't invent them mid-scene.

**AI GMs.** CriticaLLM claims a fully automated GM running entire TTRPG sessions, evaluated with real players (Berlaimont et al., 2026, https://arxiv.org/abs/2610.21525); its abstract describes full-session GMing, not an offscreen clock. The D&D dialog challenge tested whether tracking game state improved the plausibility of generated turns (Callison-Burch et al., 2022, https://arxiv.org/abs/2210.07109). Hidden Door's FAQ describes "a very light stats system" and a card-deck world; no world clock appears (https://www.hiddendoor.co/help/faq). The field is good at next-scene narration and weak at persistent world state.

## Patterns

Event sourcing folds state from an append-only log; snapshots bound replay, and external side effects break replay unless gated (Fowler, 2005, https://martinfowler.com/eaaDev/EventSourcing.html). Discrete-event simulation places events at instants, changes nothing between them, and jumps time to the next event (https://en.wikipedia.org/wiki/Discrete-event_simulation). ECS composes entities from components and runs systems over every entity that has them (https://en.wikipedia.org/wiki/Entity_component_system). Bitemporal history separates actual history from record history, so a correction changes what you knew without rewriting what happened (Fowler, 2021, https://martinfowler.com/articles/bitemporal-history.html).

Fit: event log + DES scheduler + small typed state + bitemporal facts. DES gives the property I need most — a three-month skip is one pop from the queue, not millions of ticks. Event sourcing gives replay, audit, and cheap "what did this faction know at T" queries; its weakness is changing the past, hence void-by-append. ECS suits thousands of entities with per-frame systems; at thirty NPCs it is ceremony.

Advance-on-read: I found no rigorous treatment for narrative worlds. What exists is DES's next-event jump, reduced-fidelity background simulation — The Sims 3 Story Progression keeps every household running without the player (https://en.wikipedia.org/wiki/The_Sims_3) — and wall-clock games. Treat it as a policy on DES, not a validated pattern.

## Minimal viable design

Clock: integer seconds from a campaign epoch, monotonic, changed only by explicit `advance_to(t)`, with granularities (round 6s, scene, day). Never reads system time.

Event table: id, due_at, actor, kind, thread_id, preconditions (predicate JSON), effects (typed deltas), status (pending/fired/dormant/void), source_event, narration. Index on (status, due_at) — that is the queue.

Semantic triggers in two layers: the LLM turns a dossier line into a reaction function at authoring time ("when X learns Y → X does Z after delay D, if P"); Python evaluates P against facts at runtime. The LLM writes the rule; Python fires it.

The LLM sits at authoring (scene break, and when the player leaves an NPC — postmortem rule 6) and at convergence narration. Not at advancement.

Cost: ~2.5k in / 400 out per scene break; twenty breaks is ~50k input tokens a session, about $0.15 at $3/Mtok (https://platform.claude.com/docs/en/build-with-claude/prompt-caching). Cache the fixed system+dossier prefix: 5-minute writes +25%, reads 0.1x. A per-event judge at 40 events/tick and 1.5k tokens each is ~60k per tick; a 300-event skip is seven times worse in one burst. Bound each call to ~4k tokens: system, dossier slice, last three thread events, scene facts. Send a digest, not the log. Models use context edges better than the middle (Liu et al., 2023, https://arxiv.org/abs/2307.03172), so put decision facts first and the schema last.

## Parallel narrative

Don't store branches. Store threads: id, cast, stakes, state, next_due, owed_beat, `surface_when` — a predicate over player-observable facts (knowledge, location, time), so a thread becomes eligible when the player learns the water is contaminated, not when a counter hits three. Every fired event appends one fiction-language effect line plus typed deltas; the narrator sees the line, never the table. The ledger becomes a projection of fired events, not a hand-written file.

Knowledge is per actor: `knows(actor, fact, learned_at, source)`. Factions act on what their sensors told them. That prevents omniscience and rewards the player's surveillance.

The convergence queue ranks by owed-beat age, stakes, due_at, and fires only at scene boundaries. A thread that cannot surface within N in-game days is flagged and must be surfaced or voided next session. A campaign-end wrap-up closes every open thread — exactly where Convergence went blind.

## Failure modes

- Drift: the postmortem's frozen NPCs. Reaction functions, explicit ACTIVE / WAITING-ON / STILLED-BY / DONE flags, freeze-detector query.
- Unpaid set-ups: owed-beats queue, maximum age, finale wrap-up.
- Retcon pressure: append a void or correction event, never edit; replay from snapshot; keep valid time separate from record time.
- Tick explosion: per-tick event budget, aggregate excess into one interval-summary event, cap active threads per faction.
- Never converging: every thread needs a time-based fallback, not only a knowledge condition.
- LLM inconsistency: one writer, schema-validated output, deterministic default. MAST clusters multi-agent failures into system design, misalignment, and verification (Cemri et al., 2025, https://arxiv.org/abs/2503.13657) — fewer agents, more checks.

## Time passing while away

Three shipped answers. Wall clock: Animal Crossing runs on the console clock, so seasons and holidays pass in real time (https://en.wikipedia.org/wiki/Animal_Crossing). Passive progression: EVE trains skills while logged out (https://en.wikipedia.org/wiki/EVE_Online). Explicit downtime: Blades in the Dark's downtime after each score (https://bladesinthedark.com/downtime), Delta Green's Home scenes between missions (https://en.wikipedia.org/wiki/Delta_Green), and Apocalypse World's love letters, written when time has passed since the last session (https://diceexploder.com/posts/transcript-love-letters-apocalypse-world-with-aaron-king). Recurring schedules — tanker Tuesdays, a nightly patrol — are events with a repeat rule. The tabletop ones are the right model: time passes because the fiction says so, and someone authors what happened. Wall-clock ageing is wrong when a week away should not age an operation a week.

## Recommended architecture for this repo

What shipped on 2026-11-17 is the deterministic core of this design, in
`~/ttrpg_gm/worldengine/` (stdlib, JSON state, no daemon):

- `clock.py` — in-game time as naive ISO datetimes plus a fiction label, every
  granularity, moved only by `tick --by/--to`; nothing reads the system clock.
- `store.py` / `engine.py` — event table, `evaluate()` (advance-on-read),
  conditions over evidence flags, reaction rules, convergence queue, freeze
  audit, wrap-up pass, markdown rendering. State is one `engine.json` per
  campaign; the markdown ledger is a projection appended at scene breaks.
- `migrate.py` / `cli.py` — one-way ledger import and the GM's command surface.

Three deliberate simplifications against the survey above, all reversible:
JSON instead of SQLite (a campaign is a few hundred events; the file diffs and
backs up for free); single-writer flags instead of bitemporal
`knows(actor, fact)` (per-actor knowledge is the next thing worth adding —
today a flag means the player has seen it, which is what triggers read);
actors-plus-events instead of a separate thread registry (a thread is an
actor's event chain, and `owed` carries the pay-back).

Deferred, in order: per-actor knowledge, snapshot/replay, and the authoring
schema with a deterministic fallback. Hooks today: session start runs `status`,
the scene break runs `tick`, campaign end runs `wrapup --strict`.

## What we are deliberately not building

- No wall-clock continuous simulation or background daemon.
- No per-NPC LLM agents. Expensive, slow, and they turn world state into model output.
- No ECS; thirty actors don't need it.
- No economy, physics, or demographic solver.
- No natural-language-only state. Prose renders; it never decides.
- No automatic retcon. Corrections are explicit events.
- No player-facing simulation UI; the player sees effects.

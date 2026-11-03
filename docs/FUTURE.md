# Future work, pinned with triggers

Items that are better done later. Each has a trigger and an action, so the next
GM instance knows when to pick it up. If a trigger fires and the item is already
done, delete the item.

## Temporal triggers

- **Two weeks after 2026-10-25 (cron reminder exists).** Review whether the
  offscreen engine prototype has started. If not, start it from
  `docs/architecture/offscreen-world-engine.md` and issue #1.
- **First week of each quarter.** Review dated docs: anything that no longer
  informs a decision moves to `docs/archive/` and the nav is updated.

## Semantic triggers

- **When the Extremophilia module is installed.** Run the Pre-Game Protocol in
  full, write the prep notes in `campaigns/extremophilia/`, start the clock and
  the offscreen ledger, and settle the agent and Foundry-world decisions.
- **When a new adventure is linked.** Run `bot/skills/ttrpg-prep.md` in full
  before the first scene. No exceptions, no partial reads.
- **When a new campaign starts.** Create the campaign folder, the sheet mirror,
  the GM notes, and the offscreen ledger with a day-one timestamp before play.
- **When the campaign reaches its ending.** Run the wind-down rule, then the
  post mortem, then file the lessons into the doctrine set.
- **When the player gives GMing feedback.** File it in the owning doctrine file
  and the core ledger in the same pass.
- **When Foundry VTT or the bridge version changes.** Re-run
  `bridge/vendor/setup.sh` and `bash bridge/check.sh`; update the pin note.
- **When a module or adventure file is updated by the publisher.** Re-read the
  changed module text before the next session. Do not trust memory of it.
- **When the map phase begins.** The bridge has no create-scene or create-token
  tool. Solve that first (Foundry-side setup, or extend the bridge), then wire
  scene reading into the session start.

## Pinned, no trigger yet

- **Live on-screen Foundry orchestration** (fog, tokens, lighting, voice in and
  out). Phase plan is in `docs/architecture/offscreen-world-engine.md`. Start
  only after the engine runs and a cheap model path is proven.
- **Cost pass on the GM loop.** Measure tokens per scene once the engine ticks
  exist, then tune.

# STATUS

**Current as of 2026-11-17.** The Convergence campaign is complete. The AI GM
doctrine set includes the Pre-Game Protocol (`bot/skills/ttrpg-prep.md`). The
offscreen world engine is built; the next test is running it in play.

## Where things stand

- **Campaign:** `delta-green-convergence` finished. The world `deltagreen`
  holds the character, the dossiers, and the adventure outline journal.
  Campaign files (sheet mirror, GM notes, offscreen ledger, research) live in
  `campaigns/delta-green-convergence/` and are not tracked.
- **CAMPAIGN_TIMELINE (2026-11-04):** `campaigns/extremophilia/timeline.md`
  is the running index; the GM appends a block per session and answers
  timeline queries from it + Foundry journals via the bridge. Cheap path
  adopted (doctrine in `bot/skills/ttrpg-campaign-tools.md`, session
  conclusion step 3); Graphiti stays parked.
- **GM bots:** `ttrpg` holds the Convergence history; `extremophilia` is a
  cloned bot profile (deepseek flash, same doctrine via `skills.external_dirs`)
  with its own permanent Bot Chat for the next campaign.
- **GM doctrine:** six files in `bot/skills/`: core (`ttrpg-ai-gm.md`), prep,
  narrator, prohibitions, campaign tools, foundry bridge. All read before
  narrating.
- **Table rules in force:** crunchy with coaching; name the skill and the
  sheet value on every check; stop at every roll; real open GM rolls; doubles
  verified digit by digit; WP spent before the roll; marked failures improve
  at session end; fiction first, no meta.
- **Offscreen world engine (2026-11-17):** `worldengine/` is the v1 prototype —
  in-game clock, event table with scheduled and semantic triggers, evidence
  flags, convergence queue, freeze audit, wrap-up pass, ledger importer; 24
  tests. Doctrine wired into `ttrpg-campaign-tools.md` (status before the
  opener, tick at the scene break). Convergence's ledger is migrated: 51
  entries, 8 sections, 22 actors awaiting state flags. Not yet exercised in
  live play. Architecture: `docs/architecture/offscreen-world-engine.md`.
- **Docs site:** MkDocs publishes `docs/` to GitHub Pages. Older architecture
  revisions are in `docs/archive/`. The repo map is `docs/REPO-MAP.md`.

## Verified environment

- Foundry VTT 14.365 on `:30000`, launchd service, world `deltagreen`, system
  `deltagreen` 2.0.1 (upgraded from 1.7.0 and migrated 2026-11-03).
- Bridge: vendored patched `foundryvtt-mcp` (full journal reads, journal
  delete). `bash bridge/check.sh` is the gate. Tool count printed by the
  script.
- Memory store: `~/.memory-tencentdb/ttrpg-memory`, embeddings on, hybrid
  search.

## Next

1. Exercise the engine in play: the first Extremophilia scene initializes the
   clock, the actor set, and the event table; review the freeze audit after the
   session, not before.
2. Triage Convergence's migrated actors to state flags (three of the 22 are the
   same man under different names), or leave them as an archive.
3. Add map and token awareness to the GM workflow: read scene and token data
   through the bridge even when playing theater of the mind.
4. Evaluate on-screen Foundry orchestration (fog, tokens, lighting) as a
   later phase, cost-conscious.

## Pointers

- Future work with triggers: `docs/FUTURE.md`
- History: `CHANGELOG.md`
- Reading order and gaps: `docs/REPO-MAP.md`
- Conventions: `AGENTS.md`
- Living-world lessons (2026-11-06): `docs/convergence-living-world-postmortem-2026-11-06.md`

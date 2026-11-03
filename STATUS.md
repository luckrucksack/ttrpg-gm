# STATUS

**Current as of 2026-10-25.** The Convergence campaign is complete. The AI GM
doctrine set includes the Pre-Game Protocol (`bot/skills/ttrpg-prep.md`). The
next build is the offscreen world engine.

## Where things stand

- **Campaign:** `delta-green-convergence` finished. The world `deltagreen`
  holds the character, the dossiers, and the adventure outline journal.
  Campaign files (sheet mirror, GM notes, offscreen ledger, research) live in
  `campaigns/delta-green-convergence/` and are not tracked.
- **GM doctrine:** six files in `bot/skills/`: core (`ttrpg-ai-gm.md`), prep,
  narrator, prohibitions, campaign tools, foundry bridge. All read before
  narrating.
- **Table rules in force:** crunchy with coaching; name the skill and the
  sheet value on every check; stop at every roll; real open GM rolls; doubles
  verified digit by digit; WP spent before the roll; marked failures improve
  at session end; fiction first, no meta.
- **Offscreen world:** the campaign ledger runs as v0 of the engine. Target
  architecture and research brief are in
  `docs/architecture/offscreen-world-engine.md`; tracking issue #1 on GitHub.
- **Docs site:** MkDocs publishes `docs/` to GitHub Pages. Older architecture
  revisions are in `docs/archive/`. The repo map is `docs/REPO-MAP.md`.

## Verified environment

- Foundry VTT 14.365 on `:30000`, launchd service, world `deltagreen`, system
  `deltagreen`.
- Bridge: vendored patched `foundryvtt-mcp` (full journal reads, journal
  delete). `bash bridge/check.sh` is the gate. Tool count printed by the
  script.
- Memory store: `~/.memory-tencentdb/ttrpg-memory`, embeddings on, hybrid
  search.

## Next

1. Review the Gemini research findings on the offscreen engine, then
   prototype the clock and event table.
2. Add map and token awareness to the GM workflow: read scene and token data
   through the bridge even when playing theater of the mind.
3. Evaluate on-screen Foundry orchestration (fog, tokens, lighting) as a
   later phase, cost-conscious.

## Pointers

- History: `CHANGELOG.md`
- Reading order and gaps: `docs/REPO-MAP.md`
- Conventions: `AGENTS.md`

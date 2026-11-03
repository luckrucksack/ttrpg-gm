# Repo Map and Survey (2026-10-25)

The survey of the repository after the Convergence campaign, with the reading
order, what was reorganized, and what still needs work.

## What this repo is

A working AI Game Master: Hermes Agent as the GM, Foundry VTT as the game
engine, a vendored MCP bridge, GM doctrine files, and the docs that explain
how it all fits together.

## Reading order

For a human, or a new GM instance orienting itself:

1. `README.md` — what the project is and how to start it
2. `STATUS.md` — current state and what is next
3. `docs/index.md` — the doc site front page
4. `docs/ttrpg-gm-architecture-2026-09-29.md` — the full system, layer by layer
5. `docs/architecture/offscreen-world-engine.md` — the next build, with the
   research brief
6. `bot/skills/ttrpg-ai-gm.md` — the GM core, then the doctrine set it indexes
7. `bot/skills/ttrpg-prep.md` — what every GM instance does before play
8. `AGENTS.md` — the standing rules for any agent in this repo
9. `CHANGELOG.md` — the history, newest first

## Layout

- `README.md` — project overview and quick start
- `STATUS.md` — current state, verified environment, next steps
- `CHANGELOG.md` — chronological history (formerly STATUS.md)
- `AGENTS.md` — standing rules for agents working here
- `docs/` — MkDocs site, published to GitHub Pages
  - `index.md` — front page
  - `ttrpg-gm-architecture-2026-09-29.md` — current architecture (v4)
  - `architecture/offscreen-world-engine.md` — the parallel world engine
  - `REPO-MAP.md` — this file
  - `archive/` — older architecture revisions, kept for history
  - research and design documents, each dated
- `bot/` — GM bot docs
  - `skills/` — the doctrine set: `ttrpg-ai-gm.md` (core), `ttrpg-prep.md`,
    `ttrpg-narrator.md`, `ttrpg-prohibitions.md`, `ttrpg-campaign-tools.md`,
    `ttrpg-foundry-bridge.md`
- `bridge/` — the Foundry MCP bridge: setup, check script, vendored patch
- `pipeline/` — PDF adventure ingestion (MarkItDown to LLM to Foundry JSON)
- `scripts/setup.sh` — one-time setup helper
- `campaigns/README.md` — the untracked campaign folder convention

## Fixed in this pass

- Added `bot/skills/ttrpg-prep.md`, the Pre-Game Protocol, and wired it into
  the GM core and the Foundry skill so every new instance reads it before the
  first scene.
- Split the old STATUS into a real status page and `CHANGELOG.md`.
- Moved the three older architecture revisions into `docs/archive/` and
  updated the MkDocs navigation and every link that pointed at them.
- Removed the tables from `docs/index.md` and `bot/README.md` (house rule:
  lists, not tables) and added the missing `ttrpg-prep` entry.
- Fixed a factual error in `bot/README.md`: the GM narrates in second person,
  not third.
- Added the Foundry orchestration goals to the architecture outline.

## Known gaps, in priority order

1. **The offscreen engine is still a file, not a clock.** The ledger is v0.
   The research brief exists; the prototype does not. This is the next build.
2. **The architecture doc predates the prep protocol and the campaign
   outcome.** It needs one refresh paragraph pointing at `ttrpg-prep.md` and
   the engine doc, and its "next" section should match `STATUS.md`.
3. **Maps are unused.** The module ships maps and tokens; the GM has never
   read scene or token data during play. Even for theater of the mind, scene
   state should be read for distance and layout. See the goals in
   `docs/architecture/offscreen-world-engine.md`.
4. **The pipeline is still manifest-only.** `import_foundry.py` generates a
   plan that a human or GM executes. That is acceptable until the engine work
   is done, but it should be stated plainly in `README.md`.
5. **Dated research documents accumulate.** They are useful history. The
   current-state documents should always link to the newest, and older ones
   can move to `docs/archive/` when they stop informing decisions.

# TTRPG Project Backlog

Moved out of the default-profile inbox on 2026-08-10 (isolation policy: TTRPG is a separate product from the general Hermes architecture work). Tracks open items for the AI-DM / Foundry project. Work on these should run in **ttrpg-profile** sessions so memory capture routes to the ttrpg store.

## Major Pivot — 2026-08-27

Custom Python framework retired and **deleted from the repo** (40 files, ~5,300 lines). New architecture: **Hermes Bot Mode** as the GM runtime, with Foundry VTT handling ALL game mechanics and NPCs as isolated Hermes profile Bots. See **[`docs/ttrpg-gm-architecture-2026-08-27.md`](ttrpg-gm-architecture-2026-08-27.md)** for the full design, including a complete description of what was built and retired.

The old code covered: `gm_core/` (runtime loop, 5 agents, config, dice), `systems/dcc/` (DCC Judge, DCC manager, DCC dice chain, tests, full documentation), `systems/dnd5e/` (rules stub), `main.py`, `scripts/` (launchers), `requirements.txt`, `.env.template`, `examples/`, and `tests/`.

Design knowledge (prompt architecture, prohibitions, NPC Bot concept, Enneagram/MBTI questionnaire) survives in docs/ and will be encoded as Hermes skills as the new architecture is built.

## Ideas worth looking into

- 2026-08-10 — **Verbatim AI-DM prohibition catalog** — Apple Notes TCC permission granted (595 notes readable). Extract exact prohibition wording from the canonicals (GM MASTER PROMPT 14.0, DM Master Prompt 2.7, SF2E 5.0 FINAL, Unified 6.0, GM Master Prompt Annex). Research brief: `docs/ai-dm-notes-research-brief.md`. Output artifacts → this repo (`docs/`).
- 2026-08-14 — **Character questionnaire system (Enneagram/MBTI)** — flesh out PCs/NPCs via structured questionnaire; idea + execution design in `docs/development-notes.md`. Anti-cliché mechanisms: sampled questions (seeded RNG), per-campaign diversity counter, per-type ban lists, tension rule. Next step when Chris wants: question bank + sampling script.
- 2026-08-10 — **DM bridge / built-in AI modules options** — Chris wants both of us hip to all current AI-DM module options before deciding. First pass: `docs/ai-dm-landscape-2026-08-06.md` (Foundry modules, Noodlr, custom-bridge analysis).
- 2026-08-05 — **Foundry VTT learning** — licensed, running on :30000 (launchd `com.hermes.foundryvtt`); eventually human-DM'd games on Discord.

## Notes

- Architecture extraction: `docs/ai-dm-prompt-architecture-2026-08-07.md` — the design DNA of the GM/DM prompt lineages (82 Notes, version trees, named engines, prohibitions layer).
- The DM memory consolidation pipeline runs from this profile's cron (weekly Mon 10am): `~/.hermes/profiles/ttrpg/scripts/dm-consolidate.py` against `~/.memory-tencentdb/ttrpg-memory/vectors.db`.
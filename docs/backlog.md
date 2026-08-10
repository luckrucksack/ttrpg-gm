# TTRPG Project Backlog

Moved out of the default-profile inbox on 2026-08-10 (isolation policy: TTRPG is a separate product from the general Hermes architecture work). Tracks open items for the AI-DM / Foundry project. Work on these should run in **ttrpg-profile** sessions so memory capture routes to the ttrpg store.

## Ideas worth looking into

- 2026-08-10 — **Verbatim AI-DM prohibition catalog** — Apple Notes TCC permission granted (595 notes readable). Extract exact prohibition wording from the canonicals (GM MASTER PROMPT 14.0, DM Master Prompt 2.7, SF2E 5.0 FINAL, Unified 6.0, GM Master Prompt Annex). Research brief: `docs/ai-dm-notes-research-brief.md`. Output artifacts → this repo (`docs/`).
- 2026-08-10 — **DM bridge / built-in AI modules options** — Chris wants both of us hip to all current AI-DM module options before deciding. First pass: `docs/ai-dm-landscape-2026-08-06.md` (Foundry modules, Noodlr, custom-bridge analysis).
- 2026-08-05 — **Foundry VTT learning** — licensed, running on :30000 (launchd `com.hermes.foundryvtt`); eventually human-DM'd games on Discord.

## Notes

- Architecture extraction: `docs/ai-dm-prompt-architecture-2026-08-07.md` — the design DNA of the GM/DM prompt lineages (82 Notes, version trees, named engines, prohibitions layer).
- The DM memory consolidation pipeline runs from this profile's cron (weekly Mon 10am): `~/.hermes/profiles/ttrpg/scripts/dm-consolidate.py` against `~/.memory-tencentdb/ttrpg-memory/vectors.db`.

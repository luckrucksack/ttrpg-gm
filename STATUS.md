# STATUS — UNDER CONSTRUCTION

**This repository is under active construction. The final architecture is
NOT settled and is TBD based on what the Foundry VTT integration will
require this codebase to look like.**

What this means in practice:

- The layer boundaries below (`gm_core` / `systems` / `campaigns` /
  `integrations`) are a first cut, not a contract. They were drawn to make
  the system game-system-agnostic and campaign-separated, but the Foundry
  wiring (module vs. bridge vs. port) will likely reshape them.
- `integrations/foundry/` is a placeholder. Nothing there is implemented.
- The prompt-architecture layer (`gm_core/prompts/`) is currently pointers
  into `docs/`; the verbatim prohibition catalog extraction is a backlog
  item (see `docs/backlog.md`).
- Treat every path and import in this repo as provisional. Probe before
  assuming; prefer `gm_core` and `systems` contracts over hardcoded paths.

Last restructured: 2026-08-10 (layer split; DCC moved under systems/dcc/;
campaign data moved under campaigns/; core stripped of game rules).

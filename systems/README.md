# systems/ — game-system layer

Every game system lives in its own self-contained package here. The core
(`gm_core/`) is **system-agnostic by contract**: it never imports a system
directly. Systems are selected at runtime via the `ACTIVE_SYSTEM` env var
(default `dcc`) and looked up through the registry in `systems/__init__.py`.

## Contract for a system package `systems/<id>/`

Required:
- `__init__.py` exposing:
  - `SYSTEM_ID` (str) — the system identifier, e.g. `"dcc"`
  - `rules_text() -> str` — the rules reference used to prime LLM context
    (markdown; may return `""` if the system ships no rules file)

Optional (whatever the system needs; keep it in its own package):
- `judge.py` / `manager.py` / `dice.py` — GM runtime, state, dice mechanics
- `docs/` — rules docs, system-specific references (e.g. DCC Judge manuals)
- `tests/` — system-specific tests

## Rules of the layer

- No game-rules text in `gm_core/`. Rules enter the LLM context only via
  `rules_text()` from the active system.
- No core imports of `systems.<id>` by name. If the core needs a system
  capability, add it to the registry contract instead.
- A system may not assume a campaign layout; it receives data dirs via the
  core (gm_core/config.py `DATA_DIR`).

## Present

- `dcc/` — Dungeon Crawl Classics (Judge): full implementation (judge,
  manager, dice chain d3–d30, spellburn/corruption/luck, docs, tests).
- `dnd5e/` — D&D 5e: rules reference only (the minimal contract example).

Adding a new system = copy the `dnd5e/` skeleton, fill in `rules_text()`
and any mechanics modules, then set `ACTIVE_SYSTEM=<id>`.

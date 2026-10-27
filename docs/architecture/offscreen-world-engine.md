# Offscreen World Engine — Architecture Outline

## What the player wants

Everything offscreen must advance on in-game time, not only when a scene touches it. Player actions seed consequences that mature in hidden parallel timelines: an alien faction survives a barn fire, communicates across its network, and directs its assets to set traps. Those threads re-enter the visible narrative later, by cause and effect, not by GM fiat.

## Current state (v0)

The campaign's offscreen ledger (`campaigns/<id>/offscreen-ledger.md`) is advanced at every scene break and timestamped to the fiction's clock. It records faction moves, NPC schedules, and pending consequences. This is a file, not a live simulation. It works but it only moves when the GM touches it.

## Target architecture

- In-game clock decoupled from wall time, supporting every granularity from combat rounds to months between operations.
- Event/clock table per faction and significant NPC: pending triggers keyed to in-game timestamps and player actions.
- Semantic triggers, not numeric: "if the player learns the water source, the board sets a watch at the reservoir," not "T+3h, spawn event X."
- Advance-on-read evaluation (lazy) as the primary mode, with optional background ticks while the player is idle.
- Convergence points where offscreen threads detect cause-effect relevance and re-enter the visible narrative. The player sees only the effect, never the simulation.

## Research prompt

See `docs/gemini-research-prompt-2026-10-25.md` for the full brief to Gemini Deep Research, covering prior art, patterns, MV design, convergence mechanics, and failure modes.

## Next steps

1. Review Gemini research findings.
2. Prototype the clock/event table in Python.
3. Integrate into the GM bot session start/end hooks.
4. Migrate the offscreen ledger to the event table format.
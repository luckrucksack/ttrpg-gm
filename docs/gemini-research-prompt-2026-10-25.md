# Research prompt for Gemini (Deep Research) — the offscreen world engine

I am building a self-hosted AI game master (Hermes Agent plus Foundry VTT) that runs tabletop RPG campaigns. The current campaign is Delta Green. I want research on how to implement an "offscreen world engine": a subsystem that lets the game universe keep moving outside the player's view, driven by an in-game clock, with LLM-authored cause and effect.

## The problem, stated precisely

Today everything in the game world exists frozen in time outside the visible narrative. NPCs, factions, and threats only move when the GM happens to touch them. I want secret parallel timelines: when the player does something (burns a barn full of alien machinery, interrogates a town official), that action seeds consequences that mature offscreen. The aliens reconstitute, communicate across their network, and direct their human assets to set traps. Those threads re-enter the visible narrative later, at moments dictated by cause and effect.

The simulation must advance on in-game time at every granularity: combat rounds (seconds), scenes (minutes), an investigation day (hours), weeks and months between operations. It must persist across sessions and across days of real time.

Triggers must be semantic, not merely numeric: "if the player discovers the water contamination, the board tightens surveillance," not "T plus 3 hours, spawn event X." The player must never see the simulation itself, only its effects.

## Questions to research

1. Prior art. I know of Stanford's generative agents (Smallville), story sifting, emergent narrative research, and Dwarf Fortress / Radiant AI style autonomous actors. What else exists, especially work aimed at interactive fiction, TTRPGs, or LLM-driven world simulation?

2. Architectural patterns for event-driven world simulation keyed to a simulated clock: event sourcing, discrete event simulation, advance-on-read (lazy) versus continuous background simulation, ECS with time-cued systems. Which maps best to an LLM-authored world state?

3. A minimal viable design for a single-user, self-hosted setup where the world engine runs as an agentic LLM process rather than a hardcoded simulation. Where should the LLM's judgment sit: at event creation, at advancement, at convergence? How do you bound the cost and the context window of each tick?

4. Representing parallel narrative so it can converge cleanly. Offscreen state must stay invisible but causal. How should it be stored (event log, clock table, world-state diff, natural-language journal) so a future GM turn can detect "this thread is now relevant" and pay it off?

5. Failure modes to design against: drift, the simulation contradicting established fiction, retcon pressure, tick cost explosion, long time skips, and the player never triggering a convergence.

6. How existing games and hobby projects handle "time passing while you are away": cron-style wall-clock ticks versus in-game clocks, journaled event logs, checkpointed world state, NPC daily schedules.

## Deliverable

A short survey of prior art, then a concrete recommended architecture I can prototype in Python on one machine. Include: an in-game clock decoupled from wall time, an event/clock table design, a semantic-trigger design (who fires triggers and when), a convergence mechanic (how offscreen threads re-enter play), and a cost model for LLM ticks. Assume a solo operator, a budget-conscious LLM API, and that correctness and reversibility matter more than fidelity.

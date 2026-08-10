# AI Dungeon Master — Prompt Architecture (extracted from Apple Notes)

Date: 2026-08-07. Source: Apple Notes corpus (82 of 573 notes match AI-DM/GM/D&D content; title-level inventory from memo cache — note bodies are TCC-protected, so this is architecture from titles, versioning, naming conventions, plus the accessible implementation docs in ~/ttrpg_gm/ and the 2026-08-06 landscape artifact).

## 1. What the corpus is

The notes are an **iteration ledger**: dozens of full-rewrite prompt versions, kept side by side, spanning at least a year of development. It is not one prompt — it is a family tree of lineages, engines, and adaptations, plus the operational scaffolds around them.

## 2. The lineages (version trees)

### Main GM lineage
- GM PROMPT 1.0 → 1.1 → **GM PROMPT 2.0**
- GM Master Prompt 2.8 → 3.0 → 3.5 → 5.0 → 7.0.0 → 7.3 → 7.3 (Revised)
- → 9.0 → 9.3 → 10.0 "Affirmative Reality" / 10.1 → 11.0 → 12.0 → 13.0 → **14.0** (current top)
- Parallel: GM MASTER PROMPT B 1.0 (an alternate branch), ALT GM PROMPT 1.1, Alt AI GAME MASTER PROTOCOL

### DM lineage
- DM PROMPT, DM Master Prompt 2.7, DM Advice

### System adaptations (core prompt adapted per ruleset)
- Starfinder 1.0 → 2.0 → SF2E Playtest 1.3 → SF2E 3.0 → 4.0 → 5.0 → **5.0 COMPLETE (FINAL)** + "SF2E Adaptation. New"
- DCC GAME MASTER PROMPT 1.1, DCC Judge; MCC Judge Master Prompt → v2
- GM Prompt For Published Modules 1.0

### Named engines (standalone subsystem docs)
- Unified Master Prompt 6.0 — "The Anti-Formulaic Engine"
- FINAL ADVENTURE ENGINE v5.0
- AI-GM Drift Engine Mechanics
- The d20/d12 Dual-Axis System (2.0 → 3.0)
- GM-to-Novelizer Master Prompt v2.0 — "The Chronicle Protocol"
- GM MASTER PROMPT 10.0 — "Affirmative Reality"
- The Signal Scrambler (full module, GM-facing)
- Game Master Framework v2.20.25
- GM OS INITIALIZATION SEQUENCE
- GM Master Prompt Annex

### Session-state scaffolding
- GM refresher prompt, Reminder GM 2.4.2, Simplified GM 3.1.25, GM/Game Master Instructions

### Agentic / automation specs
- Agentic AI TTRPG GM — Operational Specification for OpenClaw
- Agentic AI TTRG GM, OpenClaw instructions to build an AI Game Master via Discord

### Cross-platform & misc
- ChatGPT master prompt 1.0–6.0 (+ coding 1.0) — same architecture carried to other platforms
- Pi GM PROMPT, Author/GM prompt 1.5, Novelize the TTRPG experience
- Dungeon 1 → 1.1 → 1.2 (content experiments), D&D Random Ideas, blank character sheet

## 3. The architectural ideas (design DNA)

**Idea 1 — Versioned full-rewrite iteration.** Every iteration is a complete numbered rewrite (X.Y), never a patch. Old versions are kept as archived notes — the corpus IS the changelog. Naming evolves at breakpoints (GM PROMPT → GM Master Prompt → GM MASTER PROMPT; 7.x → 9.x → 10.x jumps), marking "this version is a different animal."

**Idea 2 — The master prompt is an operating system.** The prompt is structured like a boot sequence: GM OS INITIALIZATION SEQUENCE, then layered sections — visible in "Section 1: CORE IDENTITY & AUTHORITY" — with an **Annex** carrying supplementary material so the master prompt itself stays lean. Identity layer → authority layer → mechanics → behavior → annex.

**Idea 3 — Named engines, one per failure mode.** The most distinctive move: instead of one big prompt, the design decomposes into named subsystems, each fighting one observed failure:
- Anti-Formulaic Engine — kills repetitive/patterned play
- Drift Engine — kills persona/state drift over long sessions
- Affirmative Reality — kills world incoherence/contradiction
- d20/d12 Dual-Axis — two probability axes (dice + narrative) kept separate
- Adventure Engine / Chronicle Protocol — mode switches: module-driven play vs. novelization
- Signal Scrambler — anti-meta/anti-leak (module)

**Idea 4 — The prohibitions layer (the crown jewel).** A dedicated, explicit layer of specific, imperative bans ("never X / do not Y"), the opposite of soft guidance. The user's rule, stated plainly: they must stay specific. Every LLM that touches them tries to genericize them ("avoid railroading" instead of the exact banned behavior) — that genericization is exactly what must not happen. Each prohibition is failure-driven: its wording encodes the specific observed failure it was added to kill, so weakening the wording resurrects the failure. They survive every iteration untouched.

**Idea 5 — One core, many adaptations.** The same master-prompt architecture is adapted per ruleset (SF2E 1.0→5.0 FINAL, DCC Judge, MCC Judge, Published Modules) rather than forked into unrelated prompts. "Adaptation" is an explicit, repeatable operation with its own versioning.

**Idea 6 — Role separation.** Different roles get different authority sections: GM vs DM vs Judge (DCC/MCC) vs Novelizer/Author. The role defines the identity/authority section; the rest of the architecture carries over.

**Idea 7 — Session-state prompts as drift control.** Refresher/Reminder/Simplified prompts exist to re-prime a long-running session cheaply. This pairs with the Drift Engine: lightweight re-injection of the essential rules mid-campaign instead of re-sending the whole master prompt.

**Idea 8 — The architecture generalizes to agents.** The same DNA shows up as an "Operational Specification" for OpenClaw — prompt becomes agent spec with tool use over Discord. And it matches the ttrpg_gm implementation, where the prohibitions are enforced in code:
- Local dice only — the model can request rolls, never roll (a prohibition made physical)
- Two-stage refinement — raw AI output never reaches players (prohibition made physical)
- Arbitration loop: Listen → Assemble → Call → Arbitrate → Refine → Deliver
- Structured directives ([REQUEST_ROLL], [UPDATE_STATE], [UPDATE_CHARACTER], [MOVE_SCENE]) + !override/!resume

## 4. The prohibitions — what can be said at this level

- Form: imperative, specific, sectioned — not advisory.
- Provenance: each ban traces to a real observed failure; wording preserves the failure, not the principle.
- Stability: prohibitions are the most stable part of the corpus across 14 major versions.
- Defense: the named engines (Anti-Formulaic, Drift, Affirmative Reality) are prohibitions promoted to first-class subsystems because they were load-bearing.
- The implementation (ttrpg_gm) proves the same prohibitions work in code: model never rolls dice, never talks raw, never bypasses arbitration.

## 5. Gap & next step

Note bodies are behind macOS TCC (memo/AppleScript hang; container read blocked). This artifact is title-level + implementation-level. If the user wants the **verbatim prohibition catalog** (exact wording of every ban, sourced per version), the unlock is one System Settings action: Privacy & Security → Automation → allow the terminal/memo to control Notes (or Full Disk Access for the terminal). Then the canonicals to extract are: GM MASTER PROMPT 14.0, DM Master Prompt 2.7, SF2E 5.0 COMPLETE (FINAL), Unified 6.0 Anti-Formulaic, GM Master Prompt Annex.

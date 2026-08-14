# Development Notes — AI GM Project

Running log of ideas, problems, and decisions. Latest entry first. Companion to `backlog.md` (tracking) — this file holds the *why* and the *how*.

---

## 2026-08-14 — Character development via Enneagram/MBTI questionnaire

**Source:** Chris, from a conversation with a friend. "I did it ad hoc, but for my AI GM I came up with a set of questions sourced from the Enneagram and Myers-Briggs personality assessments for the GM to use to flesh out the characters and NPCs interactions. That was a long time ago."

### The idea

A structured questionnaire (Enneagram + MBTI sourced) the GM runs to flesh out characters and NPCs — their personalities, motivations, and how they interact. Built ad hoc years ago, back in the pure-chatbot era, so everything lived inside the GM master prompt.

### The two failure modes observed (and their root causes)

1. **Clichéd type-fitting** — the AI assigned characteristics that were clichés of a given personality type.
   Root cause: *stereotype collapse*. Type labels (ENFJ, Type 2, etc.) are strongly associated with a small descriptor set in the model's training distribution; when asked to "flesh out a character of this type," the model anchors on the prototype instead of the individual. The type label becomes a stereotype shortcut.
2. **Limited trait vocabulary** — it always grabbed from a small numerical set of characteristics within that set.
   Root cause: *no diversity pressure in free generation*. Asked to generate from nothing, the model returns the highest-probability tokens — the same ~10–15 descriptors per type, every time. Nothing in a single chat prompt forces spread.

Plus the meta-problem that made the fix impossible in the old era:

3. **Prompt overload / parts canceling out** — the master prompt carried personality, world, mechanics, and prohibitions together; sections fought each other, and the inference-time cognitive load exceeded what the model could reliably hold.
   Root cause: attention dilution + instruction competition inside one giant context. This is exactly what the prohibitions layer (see `ai-dm-prompt-architecture-2026-08-07.md`) fought symptom-by-symptom — the structural fix is modularization, which Hermes gives us for free.

### Execution blanks filled — how to build this properly on the Hermes orchestrator

**1. Take the choice out of the model's hands (mechanize the randomness).**
The LLM must never select *which* traits to consider — that's the source of both failure modes.
- The **orchestrator** picks the question subset per character: a seeded RNG samples N questions from the bank, stratified across dimensions (Enneagram core triad + wings, MBTI axes, values/fears/motivations, relational style).
- The model only **answers** the questions asked; a deterministic assembler builds the profile from the answers. Diversity comes from the sampling layer, not the model's whim.
- **Per-campaign diversity counter** in `state_manager`: every characteristic descriptor used gets counted; once a descriptor exceeds K uses (e.g. 2), it's deprioritized for the next character. A counter, not a prompt line.

**2. Anti-cliché guardrails — the prohibitions layer, applied mechanically.**
- Per-type **ban lists**: the specific clichéd descriptors models reach for (e.g. "wise old mentor" traits for a Type 5), written as explicit prohibitions with exact wording — same doctrine as the GM master prompt prohibitions.
- **Tension rule**: the assembler mechanically assigns 1–2 traits that *contradict* the type's stereotype (a lawful ENFJ who lies easily to protect others). Models are excellent at rationalizing imposed constraints and terrible at inventing diversity — so impose, don't ask.

**3. Modular orchestration (solves prompt overload).**
One god-prompt → specialist agents, spawned on the fly, each with a small single-purpose prompt:
- `psych-profiler` — questionnaire → profile (spawned only when a character/NPC needs creation)
- `lore-keeper` — world/campaign memory (TencentDB, ttrpg :8421)
- `rules-adjudicator` — mechanics and dice (local dice, no model-rolled)
- `narrator` — scene prose
- `foundry-sync` — state in/out of Foundry VTT

**4. Cost control (multiple API calls concern).**
- **Tiered routing**: questionnaire answering + profile assembly + prose refinement run on cheap/free tiers (OpenRouter `:free` models, OAuth free tiers via Hermes proxy); only adjudication and scene direction run on the paid tier (V4 Flash default, V4 Pro for heavy scenes).
- Independent NPC generations run **in parallel** (wall-clock win; cost is the sum — tiering is what keeps the sum acceptable).
- Bounded contexts: the questionnaire is Q&A, not essay — each answer is a few tokens; assembly is template + fill.
- Config-level token savings already identified: `docs/ai-dm-token-reduction-playbook-2026-08-13.md`.

**5. Foundry VTT bridge (the target).**
- **Foundry is the source of truth** for characters/NPCs (actors, journals) — no state living in prompts, no model-rolled dice (consistent with `ai-dm-landscape-2026-08-06.md`).
- Flow: orchestrator detects a new PC/NPC → spawns `psych-profiler` → profile written to the Foundry actor (via `integrations/foundry/`, see NOTES.md) + campaign memory.
- The questionnaire answers are stored per-character (journal/world_state) — the canonical record. Next session **re-reads answers, never re-asks**.
- Long-term campaign memory: **TencentDB Agent Memory in the ttrpg profile** — decision locked 2026-08-13 (see `ai-dm-memory-backend-deep-dive-2026-08-13.md`; Hy-Memory rejected: single-maintainer adapter, no migration path, self-disclosed benchmarks).

### Status

Idea captured; nothing built yet — Chris is still learning/playing (slow, savory process; fine). Next concrete steps when he wants them:
1. Question bank + sampling script (pure Python, no LLM needed for the bank).
2. `psych-profiler` agent: small prompt + per-type ban lists + tension rule.
3. Diversity counter wired into `state_manager`.
4. Foundry actor write path in `integrations/foundry/`.

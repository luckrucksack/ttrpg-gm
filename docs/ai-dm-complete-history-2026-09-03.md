# AI-DM / TTRPG Game Master — Complete Project History
## Segmented Report for Cross-LLM R&D
### Generated 2026-09-03

---

## HOW TO USE THIS DOCUMENT

This is a complete chronological record of the AI-DM (AI Game Master) project — a self-hosted TTRPG GM system running published adventures in Foundry VTT with a Hermes Agent Bot as the GM. Each segment is self-contained. Feed segments individually or the whole document to any LLM for analysis, critique, or extension.

---

## PHASE 0: PROVENANCE & CONTEXT (Before Recorded History)

### Person
- Chris (chriscoon / luckrucksack / Luther von Ruckerson / f4useless)
- MacBook Air, iPhone via Tailscale
- ADHD, hand tremor, chronic insomnia — compensated by external systems
- Self-hosted Hermes Agent + Hermex WebUI (tailscale)
- OpenRouter default (deepseek/deepseek-v4-flash), native DeepSeek fallback
- TencentDB Agent Memory as long-term memory backend (Hy-Memory rejected — maturity / single-maintainer risk, not cost; it was MIT/free)
- Cost-pragmatic: flips providers within hours of price hikes
- Games: Dungeon Crawl Classics (DCC) installed, system-agnostic design
- Campaign: Dying Earth (Vance) + Starfinder seeded in gitignored campaigns/
- Discord server: "Eberron Campaign" with channels, roles, Avrae bot

### Pre-History (before AI recording started — July 2026)
- A ~5,300-line custom Python AI-GM framework was built across ~35 files
- 14 major versions of GM master prompts in Apple Notes (full-rewrite lineage)
- Named "engines" per failure mode: Anti-Formulaic Engine, Drift Engine, Affirmative Reality, d20/d12 Dual-Axis, Adventure Engine, Chronicle Protocol, Signal Scrambler
- Prohibitions layer: imperative, specific bans encoding exact observed failures
- Chronically fatal flaw: prompt overload — master prompt carrying personality, world, mechanics, and prohibitions together; sections fought each other
- Zero actual game sessions run using the custom framework
- Foundry VTT :30000 installed but integration never wired
- Repo: `luckrucksack/ttrpg-gm` (initially private, later made public)

---

## PHASE 1: INITIAL ARCHITECTURE (2026-08-06 — 2026-08-14)

### Trigger
Chris surveyed DM-bridge options for Foundry VTT, including built-in AI modules (FoundryAI, Noodlr, RPGX, Simulacrum). Wanted both himself and the AI up to date on all options before choosing. On 2026-08-14 he shared his AI-DM design triggered by clichéd type-fitting and prompt-overload.

### Key Design Decisions
- Enneagram/MBTI-based character model, not generic type-fitting
- AI-DM must be lean, orchestrated, cost-conscious
- Reuse Foundry VTT's built-in GM functionality
- DCC mechanics delegated to Foundry, not reimplemented
- Game-system-agnostic core design

### NPC Questionnaire Design (2026-08-14 — development-notes.md)
- Structured Enneagram + MBTI-sourced questionnaire for fleshing out characters
- Two observed failure modes:
  1. **Clichéd type-fitting**: type labels cause stereotype collapse
  2. **Limited trait vocabulary**: model returns same ~10-15 descriptors per type
  3. **Prompt overload**: sections fight each other in one giant context

### Mechanization Strategy for Questionnaire
- Orchestrator (not LLM) picks question subsets via seeded RNG, stratified across dimensions
- Model only answers questions asked; deterministic assembler builds profile
- Per-campaign diversity counter: descriptor use tracked, excess traits deprioritized
- Per-type ban lists + tension rule (assembler assigns 1-2 traits that contradict stereotype)

### Modular Orchestration (response to prompt overload)
- Single god-prompt → specialist agents spawned on demand:
  - `psych-profiler` — questionnaire → profile (spawned only for character creation)
  - `lore-keeper` — campaign memory (TencentDB ttrpg :8421)
  - `rules-adjudicator` — mechanics and dice (local dice only)
  - `narrator` — scene prose
  - `foundry-sync` — state in/out of Foundry VTT
- Tiered model routing: cheap/free for questionnaire, profile assembly, prose refinement; paid V4 Flash for adjudication and scene direction
- NPC generations run in parallel (wall-clock win)

### State of Artifacts
- docs/ created with architecture doc, research docs, backlog
- Python framework still present in repo (not yet retired)
- Foundry integration: placeholder only, nothing wired

---

## PHASE 2: FOUNDRY INSIGHT & BOT MODE PIVOT (2026-08-26 — 2026-08-28)

### Trigger Moment
Chris realized: "much of the functionality I want the AI GM to be is already contained in the virtual tabletop." Foundry already handles: maps, tokens, fog of war, dice rolling, combat tracking, character sheets, condition tracking, sound, lighting. The AI GM doesn't need to own those layers — it needs to orchestrate them through Foundry.

Simultaneously, Hermes v0.21.0 shipped Bot Mode — named, persistent profiles with isolated memory, skills, and cron.

### Hermes Bot Mode Features (relevant subset)
- Named bots = Hermes profiles with isolated memory/skills/config
- Canonical Bot Chat (persistent, never-resets conversation)
- Bot-to-Bot DMs
- Group chats / rosters (multiple bots deliberating)
- Profile isolation per NPC
- Cron jobs with delivery to Bot Chat
- Zero overhead when idle (just config + empty session DB)

### Architecture Options Explored

**Option A — Single GM Bot**: One bot runs everything — rules, narrative, world state, NPCs. Simple, but a lot of context for one session.

**Option B — Specialist Bots, one job each**:
- GM Bot — orchestrator, delegates
- Rules Bot — rulebook knowledge, mechanics
- Narrator Bot — pure prose, scene description
- NPC Emoter Bot — dialogue, mannerisms
- World Lore Bot — setting canon
- Bots deliberate in group chat or message directly

**Option C — Bot Mode as player-facing layer only**: AI GM stays as headless Hermes process, Bot Mode is just the player portal.

### Decision: Option B adopted as target architecture

### NPC Bot Design (2026-08-26)
- Each significant NPC = Hermes profile under ~/.hermes/profiles/npc-<name>/
- Profile: mini Hermes instance with own memory, skills, cron
- Model: ox-alpha (OpenRouter free tier) — zero cost until activated
- Memory: isolated TencentDB per NPC (merchant can't know dungeon secret)
- Skills: 1-2 personality/domain prompts per NPC
- Dormancy: zero runtime cost when idle
- Lifecycle: created during campaign prep, archived on NPC death
- Bot-to-Bot subconscious layer: NPC bots message each other via DM to advance agendas between sessions (cron-driven)

### Code Repo Restructured (2026-08-27)

**Removed from git:**
- gm_core/ runtime, agents, config (~3,200 lines)
- systems/dcc/ DCC mechanics (~2,376 lines across 13 files)
- systems/dnd5e/ rules stub
- main.py, scripts/, requirements.txt, .env.template, examples/

**Preserved in docs/:**
- Research docs: prompt architecture, landscape survey, VTT comparison, memory backend analysis
- NPC Bots design sketch
- Enneagram/MBTI questionnaire concept
- Prompt architecture research (prohibitions doctrine, named engines, failure modes)
- Foundry bridge reference notes

### DCC System — What Was Lost (documented for posterity)
Full written description preserved in architecture doc:
- **dice.py** (455 lines): DCC dice chain with cryptographic entropy, table lookups, spell checks, crit/fumble tables, luck checks
- **manager.py** (727 lines): Spellburn, corruption, mercuric magic taint, luck burning, turning undead, Mighty Deeds of Arms, class-specific tables
- **judge.py** (785 lines): Full DCC Judge AI runtime with bang-commands, adventure loading, party management
- 5 DCC docs, 2 test files, shell health checks

### GitHub Presence Established
- Repo made public: `github.com/luckrucksack/ttrpg-gm`
- GitHub Pages via mkdocs + Actions — workflow added but **broken from 2026-09-01**
  (missing `mkdocs-material` dependency; fixed 2026-09-04 — see Phase 5)
- 5 topics, description set (verified 2026-09-04: ai-game-master, design-docs,
  foundry-vtt, hermes-agent, ttrpg)
- Secrets verified clean (full history scan)
- Campaign data (licensed PDFs) gitignored

### Status after Phase 2
- Architecture resolved, documented, published
- Zero lines of Python framework remain in repo
- Build now happens as Hermes skills, profiles, and Foundry bridge config
- Bot Mode identified as the substrate
- Foundry MCP (laurigates/foundryvtt-mcp, MIT, OSS) identified as bridge

---

## PHASE 3: CLEAN-SLATE REBUILD (2026-09-01)

### Trigger
Even the residual bespoke pieces felt redundant after the architecture settled. The Python framework was already dead in git; the next step is building on native bot functionality.

### Key Decisions (2026-09-01)
- Start from scratch using Hermes Bot Mode as the substrate
- Build own Foundry REST API rather than rely on existing module
- All components integrated modularly, hosted on GitHub
- Microsoft MarkItdown for PDF adventure ingestion
- z.ai API key stored for future editing loop (not yet set up)

### PDF Ingestion Pipeline (Decided)
```
PDF → MarkItDown (text) → LLM extraction (JSON) → MCP import (Foundry)
```
- `pipeline/ingest.py`: Stage 1-3, outputs `output/<adventure>/` with actors.json, journals.json, items.json, roll_tables.json
- `pipeline/import_foundry.py`: Connects to Foundry MCP, calls create_actor, create_journal_entry, etc.
- Maps, walls, and token placement: manual (honest scoping — MarkItdown handles text, spatial geometry stays manual)

### Current System Architecture (2026-09-01)

```
PLAYER SURFACES — Discord channel | Hermex/webui | Foundry VTT chat
        │
GM BOT (ttrpg profile)
  - Hermes Bot Mode — persistent named agent
  - Model: deepseek/deepseek-v4-flash (OpenRouter)
  - Skills: narrator, prohibitions, foundry-bridge, campaign-tools
  - Memory: TencentDB Agent Memory (:8421)
  - Tools: MCP (Foundry), terminal, delegate_task
        │
NPC BOTS (Hermes profiles, per-NPC isolated)
  - Model: ox-alpha (free)
  - Memory: isolated per NPC
  - Skills: NPC personality/domain prompts
  - Activated via delegate_task by GM Bot
        │
FOUNDRY VTT (:30000)
  - Native MCP Server (laurigates/foundryvtt-mcp)
  - Source of truth for: actors, scenes, combat, dice, mechanics
  - Published adventures imported as journals, actors, scenes, items, roll tables
        │
CAMPAIGN MEMORY (TencentDB :8421)
  - Scene blocks for compressed session logs
  - Episodic memory for narrative history
  - Persona for character profiles
  - Instruction for running decisions
```

### File Layout (Current)
```
~/ttrpg_gm/
├── pipeline/           # PDF adventure ingestion
│   ├── __init__.py
│   ├── ingest.py       # MarkItDown → LLM → JSON
│   └── import_foundry.py  # JSON → MCP → Foundry
├── bridge/
│   └── README.md       # MCP server setup docs
├── bot/
│   ├── README.md       # GM Bot config
│   ├── skills/
│   │   ├── ttrpg-narrator.md
│   │   ├── ttrpg-prohibitions.md
│   │   ├── ttrpg-foundry-bridge.md
│   │   └── ttrpg-campaign-tools.md
│   └── npc-template/
│       └── README.md   # NPC Bot template
├── docs/               # MkDocs site (GitHub Pages)
├── campaigns/          # Adventure data (gitignored)
├── README.md
└── mkdocs.yml
```

### Session Flow
1. **Setup** — Buy adventure PDF or Foundry premium module. If PDF: run pipeline ingest + import
2. **Pregame** — Player connects via Discord/Foundry chat. GM Bot loads campaign memory and current Foundry state
3. **Play** — GM Bot narrates from adventure journals via narrator skill. Foundry handles all mechanics via MCP. NPC interactions delegated to NPC Bots
4. **End** — GM Bot writes session log to campaign memory, advances NPC agendas via cron

### Cost Model
- GM Bot: ~5-15 turns, V4 Flash (~$0.15-0.45 per session hour)
- NPC Bots per interaction: ~2-4 turns, ox-alpha (free)
- Total: ~$0.20-0.60 per active session hour

---

## PHASE 4: CURRENT STATE (2026-09-03) & OPEN QUESTIONS

### What Exists Right Now
- Architecture docs: 2 versions (08-27, 09-01) with full system map
- Pipeline: ingest.py (MarkItDown → LLM → JSON) + import_foundry.py
  (validates JSON and generates the MCP import manifest the GM Bot executes —
  NOT a direct importer; foundryvtt-mcp has no create_actor tool)
- Bot skills: 4 SKILL.md files written (narrator, prohibitions, foundry-bridge, campaign-tools)
- NPC template: README.md with config example
- TencentDB ttrpg instance running on :8421 (separate from main)
- TTRPG profile configured with:
  - model: deepseek/deepseek-v4-flash default (was v4-pro; re-routed 09-04),
    v4-pro for heavy scenes via per-session /model switch
  - TencentDB memory on :8421
  - Foundry MCP server wired in config (password placeholder — needs real creds)
  - skills.external_dirs pointing to ~/ttrpg_gm/bot/skills/

### What Does NOT Exist Yet
- Foundry MCP server not yet running (user setup TBD)
- NPC profiles not created (no NPCs generated)
- Critique/editing loop not set up (z.ai key stored, no pipeline)
- Questionnaire bank + sampling script not written
- Own Foundry REST API decided but not built
- Zero actual game sessions played
- No Foundry adventure data imported

### Open Design Questions
1. **Editing loop**: z.ai GLM 5.2 reviews narrative output against prohibitions before player delivery — not set up, exact role of z.ai unconfirmed
2. **Own Foundry REST API**: resolved 2026-09-04 — dropped. foundryvtt-mcp
   (laurigates, MIT) is the bridge; own REST API would duplicate it
3. **Orchestration plan**: detailed action flow for a session not yet specified
4. **Questionnaire mechanics**: question bank, sampling algorithm, per-type ban lists not written
5. **Trait vocabulary scope**: diversity counter, threshold, and descriptor universe not defined
6. **GM Bot mode**: active/standby player interaction patterns not designed
7. **NPC Bot lifecycle**: creation, activation, archival, death procedures not operationalized
8. **Memory schema**: exact TencentDB L1/L2/L3 structures for campaign state not finalized
9. **Maps/walls/tokens**: manual placement acknowledged but workflow not designed
10. **Published module import**: workflow for Foundry premium modules vs PDF pipeline not aligned

### Preferences Governing Next Steps
- Learn-first: wants option landscape before decisions
- Step-back plan → honest critique → execute
- Cost is a hard constraint
- No paid software/plugins
- Game-system-agnostic
- Existing tools win (Hermes Bot Mode, MarkItdown, Foundry MCP)
- Own code where the glue is the differentiator (Foundry integration layer)
- Infrastructure prepared ahead of need (z.ai key stored before editing loop exists)
- Both human and AI kept up to date on all options before decisions

---

## PHASE 5: HONESTY AUDIT (2026-09-04)

### Trigger
Review of the history doc against the actual repo and GitHub surfaced
discrepancies. Fix-first pass — no new features.

### Verified against GitHub + live system
- Repo public; 5 topics + description confirmed on GitHub (ai-game-master,
  design-docs, foundry-vtt, hermes-agent, ttrpg)
- **GitHub Pages CI was broken** from 2026-09-01: `mkdocs.yml` uses the
  `material` theme but the workflow only installed `mkdocs` (not
  `mkdocs-material`) → every build failed, site stale since 08-28.
  Fixed: workflow installs `mkdocs-material`.
- `mkdocs.yml` referenced `../STATUS.md` in nav (outside docs_dir) — removed;
  STATUS.md stays at repo root as a GitHub-rendered status, not a site page.
- `pipeline/import_foundry.py` was performative: posted MCP JSON-RPC to
  Foundry's web port (:30000) — foundryvtt-mcp is stdio, no HTTP endpoint,
  and has **no `create_actor` tool**. Could never work. Rewritten as an
  honest import-plan generator (validates JSON, emits manifest.json of MCP
  calls for the GM Bot to execute; actors + roll tables flagged manual).
- `ingest.py` hardcoded the OpenRouter base URL even when falling back to
  OPENAI_API_KEY — now routes to the provider whose key is actually set.
- `campaigns/README.md` and `integrations/foundry/NOTES.md` referenced the
  deleted Python framework (gm_core, DATA_DIR) — rewritten to current
  architecture / decision record.
- STATUS.md claimed "no executable code" while pipeline/ + scripts/ existed —
  rewritten to verified state.
- bridge/README.md tool table verified against upstream v1.5.x; upstream
  stubs (lookup_rule, diagnose_errors) and the no-create_actor constraint
  now documented.
- bot/README.md model claims corrected to flash-default routing.
- scripts/setup.sh: removed a `npx --version` check that would hang on an
  MCP server; fixed stale commands.

### Model routing (user directive 2026-09-04)
- ttrpg profile default re-routed: flash (deepseek/deepseek-v4-flash via
  OpenRouter) for routine GM work; **v4-pro for heavy scenes** via
  per-session `/model v4-pro` — not a permanent default.
- Aliases wired in ttrpg profile: v4-pro, v4-flash, ox-alpha.

### Status after Phase 5
- CI should go green on next push (mkdocs-material installed, strict build).
- Zero repo changes to runtime behavior — docs and tooling honesty pass.

---

## KEY TENSION: THE ARCHITECTURE ARC

The project went through four distinct architectural phases:

**Phase 0**: Custom Python framework — standalone agent runtime duplicating Hermes, with DCC mechanics duplicating Foundry. ~5,300 lines, zero sessions played.

**Phase 1**: Research and design — Foundry options surveyed, modular orchestration planned, Enneagram/MBTI questionnaire designed, prohibitions doctrine established.

**Phase 2**: Pivot to Hermes Bot Mode — Foundry insight (VTT already does the mechanics), Python framework retired, NPC Bot design, public repo with GitHub Pages.

**Phase 3**: Clean-slate rebuild — native Bot Mode as substrate, MarkItdown PDF pipeline, own Foundry REST API, modular GitHub-hosted integration.

**The unresolved design question across all phases**: what is the minimal Hermes agent that can drive Foundry's API, and what does it need its own campaign memory for versus what Foundry already tracks? The pendulum swung from "build everything" to "let Foundry handle everything" — the right answer is somewhere in the middle, and it hasn't been determined yet.

---

## TECHNICAL REFERENCE — COMPONENT DETAILS

### Foundry MCP Server (laurigates/foundryvtt-mcp)
- MIT license, OSS, active
- 25+ tools: read/write actors, scenes, combat, journals, dice, tokens
- Enable FOUNDRY_WRITE_ENABLED=true for state mutation
- Designed for any MCP client — Claude Code, VS Code, Hermes native MCP client
- The bridge layer that connects Hermes Bot to Foundry

### TencentDB Agent Memory (ttrpg profile :8421)
- Four-layer system: L0 (raw conversation) → L1 (atoms) → L2 (scenes) → L3 (persona)
- Campaign world store: character profiles, location descriptions, plot threads, faction relationships, session logs, NPC knowledge boundaries
- Weekly consolidation cron (Mondays 10am)

### Hermes Bot Mode Features (v0.21.0)
- Named bots = Hermes profiles with isolated memory
- Permanent Bot Chat (never resets, compacts on /new)
- Bot-to-Bot direct messages
- Group chats with multiple bots deliberating
- Cron delivery to Bot Chat
- Avatar, title, description per bot
- Zero idle cost

### Available Models & Providers
- Default GM: deepseek/deepseek-v4-flash via OpenRouter
- Heavy scenes: deepseek-v4-pro (ttrpg profile default)
- NPCs: ox-alpha (OpenRouter free tier)
- Editing loop: z.ai GLM 5.2 (key stored, not wired)
- Provider hierarchy: OpenRouter (primary) → native DeepSeek (fallback)

---

## APPENDIX: CROSS-REFERENCES

All docs live under ~/ttrpg_gm/docs/:
- `index.md` — Docs landing page (the MkDocs home)
- `ttrpg-gm-architecture-2026-09-01.md` — Current architecture
- `ttrpg-gm-architecture-2026-08-27.md` — Previous architecture (Bot Mode pivot)
- `development-notes.md` — NPC questionnaire design, execution blanks
- `npc-bots-design-sketch-2026-08-26.md` — NPC Bot concept
- `ai-dm-prompt-architecture-2026-08-07.md` — Prompt lineage research
- `ai-dm-notes-research-brief.md` — Apple Notes prohibition catalog brief
- `dm-research-prompt.md` — DM research prompt draft
- `ai-dm-landscape-2026-08-06.md` — Foundry AI module survey
- `foundry-modules-review-2026-08-06.md` — Detailed Foundry module comparison
- `noodlr-vs-foundryai-2026-08-06.md` — Two-module comparison
- `ai-dm-memory-backend-deep-dive-2026-08-13.md` — TencentDB vs Hy-Memory analysis
- `ai-dm-token-reduction-playbook-2026-08-13.md` — Token cost strategies
- `backlog.md` — Open issues and tracking
- `vtt-landscape-2026-08-05.md` — VTT landscape survey

Bot skills under ~/ttrpg_gm/bot/skills/:
- `ttrpg-narrator.md` — Prose style guide
- `ttrpg-prohibitions.md` — Anti-cliché ban list
- `ttrpg-foundry-bridge.md` — MCP tool reference
- `ttrpg-campaign-tools.md` — Session management conventions

Repo: `github.com/luckrucksack/ttrpg-gm` (public)
Pages: `https://luckrucksack.github.io/ttrpg-gm/`

---

## END OF REPORT
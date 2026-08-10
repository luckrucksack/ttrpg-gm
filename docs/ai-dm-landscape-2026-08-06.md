# AI-DM Landscape for Foundry VTT — 2026-08-06

Status: research snapshot. Nothing installed. Decisions pending with Chris.

## Context
- Foundry 14.365 running (launchd, :30000), DCC system installed, world not yet created.
- Foundry core has NO built-in AI. All "AI modules" are third-party.
- Chris has: native DeepSeek API key (OpenAI-compatible), an OpenRouter key (free-tier use), self-hosted TencentDB memory stack (ttrpg profile planned as campaign memory).

## Category A — Ready-made AI-DM modules (install-and-go)

### FoundryAI (derekhearst/FoundryAI)
- The flagship popular module. Foundry v13+ (verified v14 compatible).
- Features: AI chat sidebar, RAG over journals/actors/scenes (in-browser IndexedDB, zero setup), 40+ tools (tokens, combat, audio, spell templates, search), actor roleplay sessions, session recaps, TTS, per-category tool toggles.
- Provider: OpenRouter only (any model incl. DeepSeek hosted there).
- Cost: free module; you pay OpenRouter token rates.
- Caveats: keys stored in world settings (readable by determined players); OpenRouter dependency; in-browser memory is per-browser, not shared.

### Loremaster
- Claude-only AI Game Master; narration, NPCs, game mechanics, PDF adventure upload, multi-player batching, canon/history.
- Requires connection to Loremaster proxy (loremastervtt.com) — subscription service, provider-locked. Weak fit for cost-conscious/sovereignty setup.

### Familiar (familiarvtt.com)
- SaaS AI DM for Foundry; 28 providers (Claude/ChatGPT/Gemini...); 14-day free trial.
- D&D 5e ONLY — wrong fit for DCC. Subscription. Out.

### RPGX AI Assistant
- 100% local via Ollama (no API keys, no cloud). System-agnostic, Foundry v10+.
- Optional RAG via RPGX Proton (separate premium app).
- Local-only quality ceiling on a MacBook Air; zero-leak, zero-cost. CC BY-NC 4.0.

### Phil's AI Assistant
- "Prompt engineer" bridge: reads actors/journals, builds a prompt, you paste into a free web AI. Manual, clunky, zero cost.

## Category B — Integration foundation (build on rails)

### Integrate AI (SirNiloc)
- Developer module: common plumbing for modules to reach local/remote AI APIs.
- The base layer if we build a custom module rather than adopt a full AI-DM.

## Category C — Open-source AI-DM (contribution/wheelhouse)

### Noodlr (gobsmacked1/noodlr) — MIT, v0.4.x pre-1.0
- Thesis: LLMs lack (1) reliable memory, (2) authoritative game state, (3) restraint — the module supplies all three. Nearly identical to our original AI-DM Bridge plan.
- Game-system-agnostic: zero hardcoded rules; feed it your books (DCC works).
- Memory: real vector/RAG — in-browser (zero setup) OR standalone `noodlr-memory` service (server-side embeddings, PDF ingestion, shared across GM machines).
- State: Foundry is source of truth — real `{{roll}}` macros, combat tracker rebuilt from Foundry each turn, no model-rolled dice.
- Providers: OpenRouter OR any hand-entered OpenAI-compatible base URL — native DeepSeek API qualifies directly.
- GM/player bot split with privilege enforcement at access layer (secrets never reach player clients), audit-logged remembers, retract-able memory records, GM-ONLY replies.
- API surface for macros/modules (game.modules.get("noodlr").api...).
- Caveats: pre-1.0 (rough edges, settings will move); keys in world settings (use credit-capped key).

### AI Combat Assistant (PF2e) — system-specific; skip for DCC.

## Category D — Custom bridge (original plan)
- Build our own module + local WebSocket/JSON endpoint + ttrpg TencentDB as memory.
- Absolute control, full DCC + campaign tailoring, no provider lock.
- Heavy: module dev, socket auth, RAG plumbing — weeks of iteration.
- Noodlr's memory service + API now covers most of this rationale; custom only if we need something neither ready-made option offers.

## Fit summary vs our constraints
- DCC system: Noodlr, FoundryAI, RPGX all system-agnostic. Familiar/Loremaster out or weak.
- Cost: all free modules; token costs via existing keys (DeepSeek native or OpenRouter). SaaS out.
- Sovereignty: Noodlr (self-host memory, OpenAI-compatible endpoint) and RPGX (fully local) strongest; FoundryAI middle (OpenRouter + browser memory).
- Contribution angle: Noodlr MIT + pre-1.0 = real upstream contribution potential (matches Chris's GitHub enthusiasm).
- Maturity: FoundryAI most polished; Noodlr most architecturally aligned with our plans; RPGX simplest/local.

## Open questions for Chris
1. Ready-made (FoundryAI / Noodlr / RPGX) vs custom bridge vs hybrid (Noodlr + TencentDB memory)?
2. Provider: native DeepSeek (OpenAI-compatible) or OpenRouter or both?
3. Where should campaign memory live long-term (Noodlr memory service, in-browser, ttrpg TencentDB)?
4. Which game system first: DCC strictly, or keep agnostic?

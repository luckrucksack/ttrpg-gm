# AI-GM Landscape — research snapshot 2026-11-06

Status: research snapshot, fresh survey across commercial products, Foundry ecosystem,
open-source, and player discourse. Supersedes the module-level view of
`ai-dm-landscape-2026-08-06.md` (most of that doc is now stale, see Updates below).

## TL;DR
- The agentic AI-GM is no longer hypothetical. Exactly one turn-key product
  (**Familiar**) genuinely PLAYS the DM inside Foundry, and one independent dev
  (**Noodlr**) is building the same architecture we already run. A crowded
  "bring-your-own-agent" MCP layer lets any Claude/Codex-class agent reproduce
  our pattern. The "agentic GM in Foundry" lane is now maybe 3–4 real entities,
  and we are one of them — but we are no longer the only one.
- Everything else commercial (AI Dungeon, Voyage, TableForge, AI Realm, StoryRoll,
  Friends & Fables, Hidden Door, NovelAI) is a standalone walled app: no VTT,
  dice/rules in their own code, features tiered by subscription.
- Player discourse (2025–26) converges on one finding: sustained multi-session
  campaigns are RARE and only credible when the LLM is stripped of control over
  numbers/state — "engine owns truth, AI owns presentation." That is exactly our
  architecture. No public, third-party-verified completed-campaign log exists
  anywhere; every comparable success is self-reported (ours included).

## 1. Commercial products (as of 2026-11-06)
- **Familiar** (familiarvtt.com) — agentic AI DM inside Foundry. 230 tools over
  MCP; runs the DM side of an imported D&D 5e adventure (initiative, monster
  turns, per-NPC voices, scene building, walls/lights/weather, correct 5e-2024
  dice). $6/mo after trial; BYO models across 31 providers incl. DeepSeek, local
  OpenAI-compatible servers, and free ChatGPT/Google plans via MCP (ships MCP
  Setup Wizard for Claude/ChatGPT/Grok/Muse). Any Foundry system claimed, deepest
  on 5e. Closest converged peer to our build; rules/dice live in its own code.
- **Standalone walled apps** (no VTT, subscription-tiered): TableForge (5e, real
  objects, own LEGEND test), AI Realm, StoryRoll, Friends & Fables (Franz, 100k+
  players, tactical 5e combat), Voyage (Latitude's 2026 AI-native RPG, best
  measured memory 4.25/5), AI Dungeon (incumbent), NovelAI, Hidden Door
  (licensed IP), AIDungeonMaster.ai (waitlist).
- **Market signals**: Inworld pivoted to voice-model infra (exit signal from the
  consumer AI-GM app); WotC/Hasbro ship actual-play shows + D&D Beyond, avoid AI
  in core content; AI Dungeon turned "improve the AI" data opt-in default-on
  (Sept 2026). Recurring industry failures per TableForge's LEGEND test: daily
  turn caps, model quality tiered by subscription.
- **Milo**: no 2025–26 product/reviewer of that name found. If the 2024–25
  kids-AI-DM startup was being tracked, it is gone/renamed — nothing current.

## 2. Foundry ecosystem & MCP (updates vs Aug doc)
- **FoundryAI** — DORMANT 8 months (last release v1.3.0 2026-03-16). Our Aug doc
  called it the flagship; it is now abandonware-adjacent. Chat-sidebar assistant,
  never autonomous.
- **Noodlr** (gobsmacked1) — ACTIVE v0.8.x, mirrors our doctrine: RAG memory +
  Foundry-authoritative state (HP/init/conditions/dice) + system-agnostic; agentic
  "verb" layer staged for v0.9. GitHub-only, ~0 stars. Our architecture twin.
- **Familiar** = the only full agentic GM. Launched ~Apr 2026, v2.26.0 Oct 2026.
- **Assistant tier**: Phil's AI Assistant (still copy/paste), RPGX (local QA + KB),
  Loremaster (unverified 2026 activity), Integrate AI dormant, Intelligent GM
  Assistant dead.
- **MCP layer (crowded, active)**: laurigates/foundryvtt-mcp (v1.5.3, now has
  write tools — our vendored patch is a fork of this), adambdooley/foundry-vtt-mcp
  + Foundry MCP Bridge (v0.8.6), Nitrmoon commercial Foundry API Bridge
  (script-sandbox), Ninjo's MCP, Foundry Browser MCP, Txpple/fvtt-mcp-dnd5e +
  Claude Code skills, DroiD16/fvtt-world-cli (ships an Agent Skill).
  → Anyone with a Claude/Codex-class agent now has build-it-yourself agentic GM rails.

## 3. Open-source / community
- Agentic frameworks (2026 wave, mostly <6 months old): claude-dnd-skill
  (~171★), open-tabletop-gm, loreweaver (CoC 7e + 5e, "code keeps the score"),
  DMCP (~170 tools), project-sentinel (Git-backed schema-gated world state),
  RPG-OS (file-based campaign state, any agent), EldritchDM (local Discord bot),
  dungeon-ultimate (local 5e + real 3D physics dice), NarrativeEngine-P (~121★),
  GauthierJeannenot/ai-dungeon-master (deterministic MCP engine + Postgres).
- Chat-frontend tier (vast majority): SillyTavern + rpg-companion extension,
  KoboldAI, etc.
- Research (Arcanum index, 63 papers): long-context memory fails (~42% story
  integrity after 20 turns, NCP-Bench); externally-tool-tracked state is the only
  robustness lever found. Validates our design, not just our preference.

## 4. Player discourse / failure modes (2025–26)
- **The goldfish problem** — continuity loss is the dominant, repeatedly
  documented failure (NPC/vault/lore drift, retconning, forgotten inventory).
- **Roll integrity** — "engine owns truth, AI owns presentation" is the
  community/architect consensus; raw-chat AI GMs "will drift. Not might, will."
- **Soft rails** — AI never challenges the player, no real stakes (100+ session
  player: "I never got challenged").
- **AI-isms** — verbal ticks break immersion (one player built an LLM-ism bingo).
- **Correction loop poison** — spend more time fixing than playing.
- **Vendor noise** — many glowing comments are self-disclosed vendors; 2026
  communities run hot (700+ upvote anti-LLM-critique rules; mod policing of ads).
- Sustained-campaign wins reported (Descent into Avernus via Codex engine; 1→20+
  two-model pipeline; ENWorld "flawlessly" claim) — all self-reported, some
  immediately rebutted.

## Fit vs our constraints
- **Architecture**: we are now one of ~3–4 genuine agentic-VTT entities (Familiar,
  Noodlr, us, plus DIY MCP setups). No commercial product replicates our full
  stack: self-hosted + tool-level VTT control + real dice integrity + durable
  memory + system-agnostic + near-zero cost + completed published campaign.
- **Updates our Aug doc got wrong/now-stale**: Familiar is NOT 5e-only anymore
  (any-system claim, BYO models — the "Subscription. Out." call needs revisit);
  FoundryAI is not the flagship (dormant).
- **Gaps vs Familiar**: on-screen orchestration (fog/tokens/lighting) is still
  "later phase" in STATUS; Familiar ships scene-building, voices, auto-pilot
  combat as a product. We lead on sovereignty, cost, dice honesty, agnosticism,
  and a completed campaign trace.
- **Defensible differentiator if we want one**: publish a LOGGED campaign
  (session-by-session log + dice verification + timeline) — clears the
  community's own "show me turn 60" bar; nobody public has done it.

## Sources
familiarvtt.com; foundryvtt.com/packages/*; github.com/laurigates/foundryvtt-mcp,
gobsmacked1/noodlr, neuralinitiative/claude-dnd-skill, 1A7432/loreweaver,
shawnrushefsky/dmcp, russalo/project-sentinel, Sagesheep/NarrativeEngine-P;
arxiv 2602.11865; arcanumrpgs.com (research index + reviews); r/Solo_Roleplaying,
r/FoundryVTT, r/rpg, ENWorld, Fantasy Grounds forums, HN (2025–01-14 item 42698610).
Survey run 2026-11-06 by parallel research agents; key claims spot-verified.
# Foundry Module Catalog Review — 2026-08-06

Status: research snapshot, verified live against foundryvtt.com catalog + GitHub activity 2026-08-06. Nothing installed. Shortlist pending Chris's approval.

## Method
- Browsed the official catalog (5,827 add-on modules) via site search by category (dice, combat, automation, calendar, pdf, token, journal, sound, macro, AI tools).
- Every shortlist candidate checked against THREE filters: (1) system-agnostic (per Chris's directive — nothing D&D/Delta-Green-locked), (2) v14 compatibility, (3) actively maintained — the "relic rule" (months of silence = study it, don't run it).
- Cross-checked maintenance via GitHub API (last push date) + the package page's version history.

## Verified candidates — recommended

### Dice So Nice! (JDW)
- 3D physics dice for every roll; deep customization, persistent dice, special effects, extensible API.
- v14+ compatible. AGPL. System-agnostic (works with any system's rolls).
- Massive ecosystem (142 search hits of companion themes). Community standard.
- Verdict: INSTALL. The table-feel baseline.

### PDF Pager
- Opens PDFs at specific pages, form-fillable PDF as actor sheet, scene notes linking to PDF pages in journals, auto-load PDF.
- v14 maintained (explicitly tracks v14.361 pdfjs restrictions — actively kept current).
- System-agnostic. Free.
- Verdict: INSTALL. Big for Delta Green (ops documents, handouts, fillable sheets at the table).

### Simple Calendar Reborn (Fireblight-Studios fork)
- Timekeeping/calendar module; custom months, years, seasons, leap rules; works with all systems.
- IMPORTANT FINDING: the original (vigoren/foundryvtt-simple-calendar) has been DORMANT 15 months (last push 2025-05-12, 144 open issues). The community continuation is the "Reborn" fork: pushed 2026-08-02 (4 days ago), v2.6.x. Install the Reborn package, not the original.
- Verdict: INSTALL (Reborn). Delta Green runs on real-world dates — calendar is genuinely useful.

### Monk's Active Tiles
- Tile-trigger interactivity: doors, traps, transitions, teleports, ambient effects, all clickable.
- v14+ (Verified 14), updated ~6 weeks ago. System-agnostic. The Monk's family split into focused sub-modules (Combat Details, Bloodsplats, Chat Timer, Combat Marker, Sound Enhancements) — active maintenance pattern.
- Verdict: INSTALL when the world has real maps. The map-interactivity pillar.

### Monk's Little Details
- QoL polish: token HUD, status effects naming/sorting, dominant scene colors, chat sidebar solid background.
- Active (same author family as above). System-agnostic.
- Verdict: OPTIONAL INSTALL — cheap win, but lower priority than the four above.

## Verified candidates — AI-DM relevant (the bigger question)

### Simulacrum: AI Campaign Copilot (Daxiongmao87)
- In-sidebar AI copilot: natural-language document management (create/read/update NPCs, items, journals), compendium tools, asset search, schema introspection, macro + JS execution, permission controls.
- MIT. v13+ (Verified 14). Pushed 2026-07-19 (3 weeks ago) — alive. 41 open issues (small project).
- Provider: ANY OpenAI-compatible endpoint with function calling — DeepSeek native qualifies directly. No SaaS, no relay.
- Caveat: CLIENT-SIDE module — lives in the GM's browser sidebar; when no browser is open, it's dead. Complements, not replaces, a server-side bridge for autonomous prep.
- Verdict: STRONG candidate for live-table AI-DM work; evaluate against Noodlr.

### Noodlr (gobsmacked1/noodlr)
- Not in the Foundry catalog (installs via GitHub manifest URL). MIT, v0.4.x, commits daily, game-agnostic, OpenAI-compatible (DeepSeek native), real RAG memory (in-browser or standalone service), Foundry-authoritative dice/state.
- Same client-side caveat as Simulacrum for live play.
- Verdict: Still the architectural favorite for the AI-DM long game (from 2026-08-06 landscape doc). Decision: Simulacrum vs Noodlr — pick before world setup.

### Rejected AI modules (relic or SaaS rule)
- FoundryAI — dormant since 2026-03-16 (5 months), unanswered custom-system issue. RELIC.
- foundry-mcp-bridge / foundry-api-bridge — Patreon-gated cloud relay (foundry-mcp.com). SaaS + data through their server. OUT.
- Loremaster — Claude-only + paid proxy. OUT.
- Familiar — D&D 5e only + SaaS trial. OUT.
- HTTP API module — 3 years stale. RELIC.
- RPGX AI Assistant — local Ollama only; MacBook Air ceiling for DM work. Weak fit, fallback only.

## Checked and passed over
- DFreds Convenient Effects — very active (daily releases) but pre-made effects are 5e-leaning. Marginal for system-agnostic; can revisit if a system needs it.
- Live Actors — mic lip-sync animations. Niche; needs mic permissions; not for our play style.
- Monk's Combat Details — combat automation; review once combat matters (system-specific behavior).

## Recommended install set (pending approval)
Tier 1 (table baseline): Dice So Nice!, PDF Pager, Simple Calendar Reborn
Tier 2 (map interactivity): Monk's Active Tiles, Monk's Little Details
Tier 3 (AI-DM decision): Simulacrum vs Noodlr — one pick before world setup

## Open questions for Chris
1. Approve Tier 1 + Tier 2 (5 modules)?
2. Simulacrum vs Noodlr for the AI-DM slot?
3. Install before or after the Delta Green world is created? (Modules install at Foundry level; enable per-world.)

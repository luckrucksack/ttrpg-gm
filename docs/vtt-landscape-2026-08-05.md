# VTT Landscape for the AI-DM — 2026-08-05

**Question:** Which virtual tabletop can host the Eberron campaign *and* be driven by the ttrpg-profile agent as an AI dungeon master?

**Answer up front:** Foundry VTT — license already owned, the only option with a real automation surface (module API + WebSocket + headless server), and an actively-maintained open-source DCC system. Owlbear Rodeo is a viable browser-side fallback for the friend's table; Ogres is a promising project but too immature to build on today. Contribution target: the MIT DCC system (foundryvtt-dcc/dcc), not a VTT fork.

---

## The landscape

**Foundry VTT** — closed core (the GitHub repo is a stub; core ships from foundryvtt.com), but every *system* is open source (dnd5e: MIT, 580 stars, active). One-time license (owned). Node.js application; runs headless; module ecosystem in the thousands; automation via the module API (Hooks, documents, canvas, macros, sockets). Self-hosted. The de-facto standard for table automation.

**Ogres (samcf/ogres)** — AGPL-3.0, Clojure, 184 stars, 17MB repo. "Free online virtual tabletop… lightweight… limited core feature-set." Scenes, initiative tracker, responsive UI, no sign-ups. Docker-only deployment per README. **Last push 2026-05-05 — dormant ~3 months.** No extension/API surface documented. Clojure (deps.edn) is niche; forking = owning a whole VTT.

**Owlbear Rodeo** — closed core, official SDK (owlbear-rodeo/sdk) + docs (docs.owlbear.rodeo/extensions/apis/). Extensions are **browser-side iframe sandboxes** — scene/player APIs, but no server-side control, no headless mode. Great UX; automation ceiling is "act like a user in the browser." Friend's table uses it.

**MapTool (RPTools)** — AGPL-3.0, Java, 921 stars, very active (pushed today). Long history, own macro scripting language, desktop-app architecture; the least modern UX of the serious options.

**D20Pro / Digital D20** — closed, commercial, no automation story worth the license. Ruled out.

---

## DCC (Dungeon Crawl Classics) support

- **Foundry:** `foundryvtt-dcc/dcc` — MIT, maintained by Tim L. White (@cyface), **v0.70.45 released 2026-08-05** (today), 3 open issues, real user guide (readthedocs), translations. Sheets + rollable mechanics; copyrighted Goodman Games *content* (adventures, art) is a separate paid compendium license key from the Goodman Games store. This is the strongest DCC support in the landscape.
- **Ogres:** system-agnostic by design ("easy to use for other game systems") — meaning no DCC support and none planned.
- **Owlbear:** system-agnostic; you'd build DCC sheets yourself as an extension.
- **MapTool:** community frameworks exist but DCC support is DIY.

---

## AI-DM bridge: what each option actually allows

**Foundry** — the automation surface:
- Headless server mode (runs without UI, exposes the full API)
- Module API: scenes, tokens, fog of war, dice rolls, chat, journal, macros — all scriptable from a module
- WebSocket socket layer for module↔external communication — an "AI DM Bridge" module can expose a JSON/WebSocket endpoint the agent calls (same bridge pattern as the existing composio bridge)
- Community precedent: voice/DM bots, music managers, external tool integrations are all built this way

**Owlbear** — extension API is client-side only: an extension could render DM actions and drive the scene *in the browser*, but nothing runs server-side. Works for a human-assisted DM; weak for autonomous orchestration.

**Ogres** — no API. To bridge an AI you'd have to fork and build the API yourself. Scope: large, and the project is dormant.

**MapTool** — scriptable macros exist, but the architecture (desktop Java app) makes remote agent control awkward.

---

## Licensing & contribution angles

- **Foundry core:** closed — no upstream contribution possible there.
- **foundryvtt-dcc/dcc:** MIT, active maintainer, healthy issue load → a genuine upstream contribution target. Chris's OSS-contribution interest maps here: fixes/tests/translations/docs on a system he actually plays.
- **Ogres:** AGPL, dormant — could be revived as a contribution project (e.g., a JSON API PR), but that's a bet on project momentum, not a foundation for the campaign.
- **MapTool:** AGPL Java — contribution possible but the stack is a poor fit for the AI-DM goal.

---

## Decision & phased path

**Use Foundry VTT** as the table. Owned license, best automation surface, active DCC system, headless-capable.

1. **Table setup:** Foundry server (already licensed) on the Mac or the Pi-class box; install DCC system v0.70.x; Goodman Games compendium license if we want official content.
2. **AI-DM Bridge module:** a small Foundry module exposing a local WebSocket API (authenticated): create scene, place token, roll dice, send chat, toggle fog. The ttrpg agent calls it through a thin client script — same pattern as the composio_drive bridge.
3. **Knowledge layer:** DCC rulebooks + campaign briefs live in the ttrpg TencentDB (RAG via Markitdown for PDFs, per the original area-loader vision); bridge calls answer rules/encounters from the store.
4. **Contribution track:** pick up issues in foundryvtt-dcc/dcc (MIT, active) — real upstream PRs under Chris's identity, low-risk, directly serves the campaign.
5. **Owlbear:** keep the extension path documented as the fallback if the table ever plays there; no build effort now.
6. **Ogres:** revisit quarterly. If it gains commits/stars, the contribution (JSON API PR) becomes worth a spike; until then it stays a watch-list item.

---

## Why not a fork (Ogres) today

A fork is a maintenance contract: upstream fixes, dependency updates, security patches — for a dormant, 184-star, Docker-only Clojure app with no API. Building the AI-DM on it means building the VTT *and* the bridge. Foundry buys the VTT (closed but stable, industry-standard) and leaves us to build only the bridge — the part that matters for the AI-DM vision. Open-source values are honored where it counts: the DCC system is MIT and gets our contributions.

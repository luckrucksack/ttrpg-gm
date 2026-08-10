# Noodlr vs FoundryAI — Head-to-Head, 2026-08-06

Status: research snapshot, live repo data pulled 2026-08-06. Nothing installed. Decision still Chris's.

## Why this doc exists
The AI-DM landscape (ai-dm-landscape-2026-08-06.md) left two real candidates: FoundryAI (described as "polished, popular flagship") and Noodlr (open-source, architecturally aligned with our original custom-bridge plan). Live repo data changes that picture significantly — the popularity/activity assumption behind FoundryAI is stale.

## Hard data (GitHub API, 2026-08-06)

### FoundryAI (derekhearst/FoundryAI)
- Created 2026-02-22. Last push 2026-03-16. **~5 months dormant.**
- Stars 3, forks 4, license MIT, 1 open issue.
- Releases: 1.0.1 → 1.3.0, all between Feb 24 and Mar 16. Nothing since.
- Open issue #1 "Multi/Custom System Support" (2026-03-20) — **0 comments, unanswered**.
- Foundry v13 targeted; v14 compatibility unverified.

### Noodlr (gobsmacked1/noodlr)
- Created 2026-07-22. Last push 2026-08-06 (**today**). Two weeks old.
- Stars 0, forks 0, license MIT, 0 open issues.
- Releases: v0.4.35 → v0.4.39 in **two days** (08-05/08-06) — daily iteration.
- Recent commits are real GM work: action/bonus/reaction economy, dash semantics, combat-tracker rebuilds, concealment, Nondetection.
- Verified against Foundry v13 and v14.

## What the dormancy means
FoundryAI's package page markets "v13, 40+ tools, RAG, OpenRouter" — but the project stopped the week after its last release, and its single open issue is exactly our use case (custom systems like DCC). A module living on top of a fast-moving Foundry API that's been silent 5 months is a maintenance risk: when v14+ breaks it, nobody fixes it.

Noodlr is the opposite: pre-1.0 rough edges (its own README admits settings will move), but it's being developed *daily*, its thesis matches our original AI-DM Bridge plan almost exactly (reliable memory, Foundry-authoritative state, restraint), it's game-system-agnostic (feed it your DCC books), and it accepts **any OpenAI-compatible endpoint — native DeepSeek plugs in directly**.

## Fit vs our constraints

DCC support: Noodlr yes (agnostic by design); FoundryAI no (custom-system issue unanswered — effectively 5e-leaning).
Maintenance: Noodlr daily commits; FoundryAI dormant 5 months.
Provider: Noodlr DeepSeek-native or OpenRouter; FoundryAI OpenRouter-only.
Memory: Noodlr real RAG — in-browser or self-hosted standalone service; FoundryAI in-browser IndexedDB only (per-browser, not shared).
Security model: Noodlr GM/player privilege split (secrets never reach player clients), audit-logged memory writes, retract-able records; FoundryAI stores keys in world settings like everyone else.
Contribution angle: Noodlr MIT + pre-1.0 + active maintainer = genuine upstream contribution target (matches Chris's GitHub enthusiasm); FoundryAI dormant = no one to review a PR.
Sovereignty: Noodlr self-host memory + native API; FoundryAI depends on OpenRouter.

## Recommendation
**Noodlr**, with eyes open on its pre-1.0 status:
1. Install into the Foundry world (module manifest URL from GitHub releases).
2. Plug native DeepSeek key via OpenAI-compatible base URL — **but** keys live in world settings (readable by determined players): use a rotation-able/capped key for the table, keep the full key for GM-only use.
3. Start with in-browser memory (zero setup); evaluate the standalone noodlr-memory service only if we want shared/server-side memory + PDF ingestion.
4. The custom AI-DM Bridge + ttrpg TencentDB plan stays as the fallback if Noodlr's iteration veers away from our needs — its rationale is largely covered by Noodlr today.
5. Contribution hook: report bugs/issues as we hit them; a pre-1.0 MIT project this active will take good issue reports and PRs.

## Open questions for Chris
1. Green-light Noodlr install, or keep researching?
2. DeepSeek key handling at the table: capped/rotated key acceptable, or GM-only bot usage?
3. Do we set up the world now (DCC system, Noodlr enabled, empty world), or wait for the ttrpg gateway + profile review first?

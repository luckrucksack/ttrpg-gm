# AI Dungeon Master — Long-Term Memory Backend Deep Dive

**TencentDB Agent Memory vs Hy-Memory** · researched 2026-08-13 · based on primary sources (repos, official docs, package registries)

## Executive summary

Both systems are Tencent products, both are MIT-licensed and self-hostable, and both work with DeepSeek-native APIs. The earlier comparison got several load-bearing claims wrong, and the real engineering differences are narrower — and more interesting — than "enterprise hub vs. narrative brain":

- **TencentDB Agent Memory (v2.0.0)** is a 4-layer memory pipeline (L0 raw → L1 atoms → L2 scenarios → L3 persona) plus three non-chat asset types: Skill, Wiki (document knowledge), and CodeGraph. It has official, actively-published Hermes support and you already run it in both profiles.
- **Hy-Memory (Tencent Hunyuan, v1.2.4)** is a 6-layer cognitive memory framework (L1 raw traces → L6 forward intents) with System1/System2 processing and causal **evolution chains** built on `supersedes` pointers. It is officially an OpenClaw plugin; the Hermes path is a capable but community-maintained provider plugin.
- The decision is not "switch or stay" on features alone — it's a tradeoff between **narrative causality + compaction** (Hy-Memory's genuine strengths) and **document knowledge, evidence fidelity, and integration certainty** (TencentDB's strengths), with a real migration cost for existing campaign data.

**Verdict:** stay on TencentDB for the ttrpg profile today; adopt Hy-Memory's three best ideas (session-end consolidation, evolution chains, conflict resolution) inside the current architecture; revisit only if the Hermes adapter gains official/active maintenance or you hit measurable context-cost pain.

## Corrections to the earlier comparison

1. **"Shrinks token size by over 70%" — wrong attribution.** The official Hy-Memory claims are "70%+ fewer memories" and "45%+ higher info density per memory", and "35% less token usage on ultra-long contexts" [8]. "Fewer memories" is compaction, not token shrinkage. TencentDB's 61.4% token reduction is real but measured on a different benchmark (WideSearch) and includes its short-term tool-log compression, not just long-term memory [5]. These numbers are not directly comparable.
2. **"TencentDB lacks emotional tracking" — unverified and arguably backwards.** Neither system documents an emotion feature [unverified]. But Hy-Memory's evolution chain (attitude arcs with `supersedes` pointers) is the closest thing either system has to tracking emotional/causal change — and it is precisely what a narrative DM needs [6].
3. **"Hy-Memory is a community plugin, TencentDB is the stable choice" — both are Tencent.** Hy-Memory is built by the Tencent Hunyuan team ("由腾讯混元团队研发"), distributed on npm/PyPI as an official Hunyuan project [3][4]. The community-grade part is its Hermes adapter — 7 stars, single maintainer — which is the real fragility, not the product [2].
4. **"Hy-Memory struggles to store rulebooks" — partially true, but the framing is wrong.** Hy-Memory has no document/wiki ingestion layer — that's TencentDB's Wiki (inspired by Karpathy's LLM-wiki) [1]. But Hy-Memory retains raw traces at L1 and can recall them via vector search [2], and the deeper point is that rule mechanics shouldn't live in the memory backend at all when Foundry VTT (:30000) is the source of truth. See "The source-of-truth argument".
5. **"TencentDB adds unnecessary processing weight" — overstated.** The team/ACL machinery is ignorable in solo mode; the async extraction pipeline runs regardless, but it runs on the gateway, not the agent loop [5][10].

## What TencentDB Agent Memory actually is (as of 2026-08-13)

- **Current release v2.0.0**, MIT license, self-hosted Docker deployment (three images, one-command start, multi-arch), with a Memory Hub web panel and a v2→v3 data migration tool [1][9].
- **Four memory assets** [1]:
  - **Chat Memory** — the L0→L1→L2→L3 semantic pyramid: raw conversation (L0, verbatim evidence), atomic facts (L1), scenario/scene blocks (L2), synthesized persona (L3) [1][10].
  - **Skill** — reusable, versioned procedures extracted from conversations. Notably, TencentDB's Skill asset management is built on code from Hermes Agent itself [1].
  - **Wiki** — document ingestion with a link graph, inspired by Karpathy's LLM-wiki. This is the mechanism for rulebooks, homebrew rules, world lore documents [1].
  - **CodeGraph** — code indexing; irrelevant to a TTRPG DM.
- **Retrieval design**: normally L2/L3 bootstrap context fast; when specific facts are needed, BM25 + vector retrieval + RRF falls back to L1/L0; results are capped by item count, character budget, and timeout so memory can't flood the context window [1].
- **Operational shape (Hermes)**: Node.js Gateway sidecar on port 8420 + thin Python provider; capture → L0 → LLM extraction to L1 every N turns → L2 scene synthesis (~every 50 memories) → L3 persona; circuit breaker on gateway failures; L0 written synchronously so nothing is lost [5]. This matches the deployment you already run — gateway on :8420 in the default profile, :8421 in ttrpg [5].
- **Pitfall worth knowing**: default BM25 language is Chinese (jieba); English conversations need the config switched to "en" [5].
- **Benchmarks (vendor-reported)**: PersonaMem 48% → 76% with memory (+59% relative) [1]; WideSearch token usage 221M → 85M (-61.4%) with success rate 33% → 50% [5].
- **Roadmap**: v2.0.1 next (zero-config cold start, faster Wiki generation, Skill export) [1].

## What Hy-Memory actually is (as of 2026-08-13)

- **Tencent Hunyuan's official memory plugin**, "based on Tencent Hunyuan's high-dimensional cognitive memory evolution framework" [3]. Independent coverage of the launch describes the same design — 6-layer framework, System1/System2, evolution chains [11]. npm `openclaw-hy-memory` v1.2.4 (published 2026-07-22, MIT, maintainer: seventhsummer); PyPI `hy-memory` v1.2.21 ("Industrial-grade dual-system cognitive memory framework", MIT) [4].
- **Six memory layers** [6]:
  - L1 raw traces (verbatim input, the raw material)
  - L2 atomic facts (searchable, mergeable fact fragments)
  - L3 identity/profile (stable long-term traits, reusable across agents)
  - L4 session summaries (one-line digests of long sessions)
  - L5 mental models (cognitive frameworks extracted from behavior)
  - L6 forward intents (asynchronously predicted next intents)
- **System1 / System2 split** [6]: System1 writes L1–L4 online, the same second the user speaks (fast path); System2 runs in the background — "sleep replay" — and grows L5/L6 (slow path). For a DM this literally maps to in-session capture vs. post-session consolidation.
- **Evolution chains** [6]: memories are strung into causal chains with `supersedes` pointers at write time; hitting any node in a chain pulls the whole causal line (attitude shift → disappointment → rejection → new direction). Conflict resolution is explicit: old facts fade, new facts solidify. The official docs' example is a musician's arc across streaming platforms — a narrative arc by another name.
- **Three modes** [4][6]:
  - **Lite** — vector write/recall only, zero LLM cost per write.
  - **Pro** — synchronous MemAgent extraction/summarization/reflection, no background worker.
  - **Ultra** — full System1+System2 with embedded Kuzu graph database (local, no extra service).
- **Benchmarks (self-disclosed, reproducible setup)**: LongMemEval 85.20% overall — first across all six subtask types vs mem0 and Graphiti; PersonaMem 76.91% — first in 7/7 subtasks; write latency 12.3 s/k tokens vs Graphiti's 97.8 (≈1/8); memory volume ≈1/4 of mem0/Graphiti; info density ≈2.5× mem0 [6]. Disclosure: memory/answer model Kimi-K2.5, judge DeepSeek-V3.2, evaluated 2025-Q4/2026-Q1, Pro mode [6].
- **Official launch claims**: solves memory fragmentation; 70%+ fewer memories; 45%+ higher info density per memory; 35% less token usage on ultra-long contexts [8].
- **Known rough edge**: OpenClaw issue #92743 documents `autoRecall` feeding the full conversation envelope (metadata, history, tool logs) as the search query, making recall expensive and noisy in QQ direct sessions; the reporter hotfixed locally and proposed an upstream fix [7]. Community-adapter bugs like this are the realistic failure mode to watch [7].

## Hermes integration: the real difference

- **Hermes bundled providers**: Hermes ships 8–9 external memory provider plugins (Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory, Memori) — only one external provider active at a time, built-in MEMORY.md/USER.md always alongside [12]. Neither TencentDB nor Hy-Memory is among the bundled set; both install as third-party provider plugins [12].
- **TencentDB → Hermes**: official support (Hermes is listed as a supported framework in TencentDB's README, alongside OpenClaw, Claude Code, CodeBuddy) [1]; provider package `@tencentdb-agent-memory/memory-tencentdb` v1.0.1, published 2026-07-14 [npm registry]; architecture documented end-to-end for Hermes including troubleshooting [5]. This is Tencent-maintained.
- **Hy-Memory → Hermes**: community provider plugin `hermes-hy-memory` (Rycen7822) [2]. It is a real, purpose-built memory provider — no MCP bridge needed — with:
  - managed venv runtime (worker subprocess owns hy-memory/Chroma/Kuzu imports, keeps the Hermes runtime clean)
  - LLM routing through Hermes' own auxiliary client (DeepSeek config applies; no second API key for the LLM)
  - `hy_memory(action=add|search|get|update|delete|list|status)` aggregate tool, auto-recall and auto-capture hooks, local read-only dashboard on :18999, bundled curation skill
  - auto-capture deliberately disabled for cron/flush/subagent contexts to avoid polluting primary user memory [2]
  - **Maintenance reality**: MIT, 7 stars, 1 fork, last push 2026-07-05 — a single-maintainer project, quiet for over a month [2]. This is the honest fragility: the SDK underneath is official Tencent and active, but the Hermes adapter is one person's bridge.
  - **Community adoption exists**: a r/hermesagent user reports swapping a five-agent Hermes fleet from Mnemosyne to Hy-Memory, citing the same cross-session amnesia problem the ttrpg profile is built to avoid [13].
- **Embeddings**: Hy-Memory requires an embedding provider (OpenAI-compatible; example config uses BAAI/bge-m3 via SiliconFlow) [2]. Local Ollama embeddings are a zero-cost option. TencentDB's default runs on local SQLite + sqlite-vec with no cloud dependency [5][9].
- **LLM**: both accept any OpenAI-compatible API — your native DeepSeek setup works with both (Hy-Memory's npm README lists DeepSeek as a first-class provider) [4][5].

## Mapping to the AI-DM workload (ttrpg profile)

What a long campaign actually needs, and which backend answers it:

- **NPC/player attitude arcs** (faction betrayal, character growth, "why did the party distrust the duke") → **Hy-Memory wins**: evolution chains with `supersedes` pointers recall the whole causal chain, not just the latest fact [6]. TencentDB stores the latest L1 atoms; the "why" must be reconstructed from L0.
- **Session recaps & quest logs** → **both fine**: TencentDB L2 scenario blocks (grouped around quests/dungeons) [1][10] vs Hy-Memory L4 session summaries [6]. TencentDB's are coarser and extraction-driven; Hy-Memory's are per-session digests.
- **World lore & rulebooks** → **TencentDB wins**: Wiki layer imports documents into structured, link-graph pages [1]. Hy-Memory has no document ingestion; it's conversation memory only [4][6].
- **Player persona tracking** → **near-tie with different flavors**: TencentDB L3 persona (76% PersonaMem [1]) vs Hy-Memory L3 identity + L5 mental models + L6 forward-intent prediction (76.91% PersonaMem [6]). L6 "what does this player intend to do next" is unique to Hy-Memory.
- **Verbatim evidence** ("exactly what was said in session 9") → both retain raw: TencentDB L0 [1], Hy-Memory L1 raw traces [2].
- **Conflict handling** ("duke is actually a vampire" must supersede "duke is trustworthy") → **Hy-Memory wins on design**: explicit conflict resolution where old facts fade and new facts solidify [6]. TencentDB relies on the extraction pipeline updating atoms — same effect, less explicit.
- **Context cost over long sessions** → both cap recall (TencentDB budget caps [1]; Hy-Memory topK/min-score); Hy-Memory claims 35% less token usage on ultra-long contexts plus 70%+ fewer memories [8]; TencentDB claims 61.4% on WideSearch including short-term compression [5]. Neither claim is directly comparable — different benchmarks, different scopes.
- **Post-session consolidation** → Hy-Memory's System2 "sleep replay" is literally a session-recap engine [6]; TencentDB's async L2/L3 synthesis is the equivalent [5].
- **Foundry VTT mechanics** → **neither integrates with Foundry**. Both are agent-side memory; neither exposes Foundry-specific hooks [1][4]. The Foundry connection stays whatever it is today (Hermes → Foundry API :30000). The memory backend's only job is remembering what the DM did with Foundry.

## The source-of-truth argument

Rule mechanics (stat blocks, spell math, homebrew rules) should not be duplicated into any memory backend while Foundry owns them — duplicated state drifts, and memory summaries are the wrong place for load-bearing numbers. The clean split:

- **Foundry VTT** = mechanical source of truth (queried live via its API).
- **Git (~/ttrpg_gm)** = gm_core/systems/campaigns design docs (already the case).
- **Memory backend** = narrative state: who knows what, who feels how, what changed, what's next — plus pointers back to Foundry/git for the exact numbers.

Under that split, Hy-Memory's lack of a wiki layer loses most of its sting, and its narrative strengths become the deciding factor — which is exactly why this is a close call rather than a rout.

## Cost, ops, and isolation

- **Money**: both free, MIT, self-hosted [1][4]. Hy-Memory adds an embedder dependency (local Ollama = free, or a paid API); TencentDB runs on your existing DeepSeek + local storage [5].
- **Extraction LLM cost**: TencentDB pays for L1/L2/L3 extraction on its cadence [5]; Hy-Memory Lite pays zero per write, Pro/Ultra pay per write window + background System2 calls [4][6]. For a weekly campaign with long sessions, both are modest; Hy-Memory Lite is the cheapest possible write path but gives up structuring.
- **Runtime footprint**: TencentDB = Node.js gateway sidecar (already running) [5]; Hy-Memory = Python worker venv (chromadb, kuzu, scikit-learn) inside the Hermes plugin [2]. Comparable; both small.
- **Isolation (campaign knowledge must not re-enter the default store)**: your separate-instance pattern (:8420/:8421) works unchanged with either. Hy-Memory additionally supports user_id/agent_id scoping [4]; TencentDB v2.0 has agent-level bindings and ACLs [1]. Neither forces cross-profile leakage.
- **Migration**: switching today means rebuilding campaign memory. TencentDB has a v2→v3 data migration tool for its own upgrades [1]; Hy-Memory ships `import-from-openclaw` (OpenClaw's native markdown memory) but **no importer for TencentDB data** [4]. Existing L0/L1/L2/L3 campaign state would have to be re-seeded manually.

## Decision

**Stay on TencentDB Agent Memory in the ttrpg profile.** Reasons, in order of weight:

1. Already deployed and stable there (:8421), with official, actively-published Hermes support [1][5] vs. a 7-star single-maintainer adapter for Hy-Memory [2].
2. Wiki layer is the only mechanism either system has for ingesting rulebooks/world-lore documents [1].
3. L0 verbatim evidence + budget-capped recall is a solid foundation for session continuity [1][5].
4. No migration path for existing campaign memory [1][4].
5. Hy-Memory's benchmark edge (LongMemEval 85.2%) is real but self-disclosed, evaluated in Pro mode with a different model stack than yours [6] — and PersonaMem is essentially a tie (76.91% vs 76%).

**Adopt Hy-Memory's three best ideas inside the current architecture** (cheap, no backend switch) [6]:

1. **Session-end consolidation** (System2 analog): a cron job in the ttrpg profile that, after each session, reads the session's L0/L1 and writes a structured recap into L2 + updates the campaign ledger in git — the "sleep replay" pattern, implemented with tools you already have.
2. **Evolution chains**: keep a campaign-level "attitude ledger" (faction/NPC/player arcs) in the ttrpg repo; when facts conflict, write the supersede explicitly ("old fact fades, new fact solidifies") instead of letting extraction silently overwrite.
3. **Conflict resolution policy**: encode "contradictions don't coexist" in the memory extraction prompts — new facts supersede old ones with the chain preserved.

**Revisit Hy-Memory when** (any of):

- its Hermes adapter gains official Tencent maintenance or sustained community velocity (watch the repo; it's been quiet since 2026-07-05) [2];
- you measure real context-cost pain from session logs that compaction would fix (35% claim is the one to test) [8];
- a direct TencentDB→Hy-Memory importer appears, removing the re-seed cost [4].

## Sources

[1] https://github.com/TencentCloud/TencentDB-Agent-Memory — TencentDB Agent Memory repo
[2] https://github.com/Rycen7822/hermes-hy-memory — hermes-hy-memory provider plugin
[3] https://hy-memory.com — Hy-Memory official site
[4] https://www.npmjs.com/package/openclaw-hy-memory — openclaw-hy-memory npm
[5] https://regolo.ai/tencentdb-agent-memory-the-complete-guide-to-persistent-memory-for-hermes-and-openclaw-with-zero-data-retention — Regolo Hermes/OpenClaw setup guide
[6] https://memory.hunyuan.tencent.com — Hy-Memory official docs (CN)
[7] https://github.com/openclaw/openclaw/issues/92743 — OpenClaw issue 92743 hy-memory AutoRecall
[8] https://x.com/TencentHunyuan/status/2061372535267357029 — Tencent Hunyuan Hy-Memory launch post
[9] https://www.marktechpost.com/2026/08/07/tencent-cloud-open-sources-tencentdb-agent-memory-v2-0 — MarkTechPost TencentDB v2.0
[10] https://deepwiki.com/TencentCloud/TencentDB-Agent-Memory/1.2-architecture-overview — TencentDB DeepWiki architecture
[11] https://alphasignal.ai/news/tencent-s-hy-memory-fixes-ai-agents-that-forget-you-after-20-sessions — AlphaSignal Hy-Memory coverage
[12] https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers — Hermes docs: Memory Providers
[13] https://www.reddit.com/r/hermesagent/comments/1vmgw4l/i_swapped_my_hermes_fleet_from_mnemosyne_to — Reddit: swapped Hermes fleet to Hy-Memory

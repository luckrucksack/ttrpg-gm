# AI Dungeon Master — Token-Reduction Playbook

**DeepSeek price-hike edition** · researched/audited 2026-08-13 · targets: Hermes (default + ttrpg profiles) + TencentDB Agent Memory gateways

## 1. The price event

DeepSeek announced price increases effective **16:00 UTC, 2026-08-16**, with a new peak/off-peak structure. Peak hours: 01:00–04:00 and 06:00–10:00 UTC; off-peak rates are half of peak [14].

- V4-Flash output: $0.28/M → **$1.32/M peak** / $0.66 off-peak (≈4.7× at peak) [14].
- V4-Flash cache-miss input: $0.14/M → **$0.44/M peak** (≈3.1×) [14].
- V4-Pro output: $0.87/M → $3.96/M peak / $1.98 off-peak [14].
- V4-Pro cache-miss input: $0.435/M → $1.32/M peak [14].
- Cache-hit pricing: previously ~98% off cache-miss ($0.0028/M Flash) [15]; the hike "massively increased" cache-hit prices and community reports describe the old ~95% discount effectively gone [16].

**What this means for the AI DM:** the dominant cost is no longer output — it's the per-turn input context (system prompt + memory recall injection + tool listings), which is now ~3× at peak with cache subsidies gutted. Long campaign sessions (4+ hours of turns, each resending the same prefix) are exactly the workload this punishes. The levers that matter: fewer tokens per turn in context, fewer memory-extraction calls, zero retry storms, and (for what cache discount remains) keeping prefixes stable.

Note for scheduling: US Pacific evening sessions (18:00–21:00 and 23:00–03:00 PDT) fall inside peak windows [14] — a DM who plays in the evening pays full peak rates; the config levers below matter more than the schedule.

## 2. Audit results — what's already right, what's wrong (2026-08-13, live configs)

**Default profile (~/.hermes/config.yaml)** — already good [17]:
- compression threshold 0.3 / target_ratio 0.1 / protect_last_n 20 — already at recommended values [17]
- prompt_caching.cache_ttl 30m, response_cache_ttl 1800 [17]
- tool_search deferral active: 31 core/visible tools, 79 deferred (~41K tokens of schemas kept out of prompt), names-only listing at ~1200-token budget [17] — this is exactly the "don't drag Drive around" outcome; the 77 Composio Drive tools cost ~1.2K tokens/turn as a name list, not ~40K
- memory gateway extraction model: deepseek-v4-flash on native DeepSeek ✓ (cheapest tier already) [20]
- gateway embeddings: OpenRouter free model (nvidia/llama-nemotron-embed-vl-1b-v2:free) ✓ zero cost [19]
- auxiliary.vision on OpenRouter flash-class model ✓ (vision only, rare) [17]

**Default profile — problems:**
- agent.api_max_retries: 3 ⚠ — a retry storm at ~3× prices is ~3× worse [17]
- composio MCP server enabled (deferred, names-only) — acceptable, but a per-tool whitelist would shave the last ~1.2K tokens/turn if Drive is rarely used [17]
- gateway BM25 recall language: not configured → plugin default is Chinese (jieba) [5] — English recall is likely degraded (quality issue, and wasted recall rounds) [19]

**ttrpg profile (~/.hermes/profiles/ttrpg/config.yaml)** — the AI DM's profile [18]:
- compression threshold 0.5 / target_ratio 0.2 ⚠ — factory defaults, untuned; the profile with the longest sessions has the weakest compression [18]
- prompt_caching.cache_ttl 5m / response_cache_ttl 300 ⚠ — cache routes reset constantly; prefixes get recomputed at full price [18]
- agent.api_max_retries: 3 ⚠ [18]
- reasoning_effort: medium ✓ (good for narrative quality/cost balance) [18]
- no composio / no Drive MCP server ✓ (nothing to drag around) [18]
- memory provider memory_tencentdb on the :8421 gateway ✓ [18]
- ttrpg gateway config file not found under the profile dir — the same gateway defaults (BM25 zh, 5-turn extraction cadence) very likely apply; locate via TDAI_GATEWAY_CONFIG in the ttrpg profile's .env and check [18]

## 3. Tier 1 — config changes, highest ROI (≈10 minutes)

1. **ttrpg compression tuning** (saves 30–60% of history tokens in long sessions) [18]:
   HERMES_HOME=~/.hermes/profiles/ttrpg hermes config set compression.threshold 0.30
   HERMES_HOME=~/.hermes/profiles/ttrpg hermes config set compression.target_ratio 0.10
   Quality impact: low — Hermes summarization keeps decisions/events; protect_last_n 20 already protects the current scene [18]. Same values already proven on the default profile [17].

2. **ttrpg cache TTL** (keeps whatever cache discount remains + less recompute) [18]:
   HERMES_HOME=~/.hermes/profiles/ttrpg hermes config set prompt_caching.cache_ttl 30m
   HERMES_HOME=~/.hermes/profiles/ttrpg hermes config set openrouter.response_cache_ttl 1800

3. **Retries to 1 in both profiles** (kills retry-storm multipliers) [17][18]:
   hermes config set agent.api_max_retries 1
   HERMES_HOME=~/.hermes/profiles/ttrpg hermes config set agent.api_max_retries 1

4. **BM25 recall language → English** (quality + fewer wasted recall rounds) [5]:
   Add to the gateway config (default: ~/.memory-tencentdb/memory-tdai/tdai-gateway.yaml) [19]; locate the ttrpg gateway's config the same way and apply. This fixes degraded English recall — not a token lever per se, but better recall means fewer repeat searches.

5. **Composio (default profile only, optional):** already names-only deferred [17]. If Drive is genuinely rare, whitelist the 3–5 tools you use (mcp_servers.composio.tools.include) or set mcp_servers.composio.enabled false; re-enable on demand [17]. ttrpg profile: nothing to do — Drive isn't configured there [18].

6. **Session scheduling (optional, honest caveat):** US evening play = peak hours [14]. If a session can start before 18:00 PDT or run past 03:00, it rides off-peak at half price [14]. Not a lever to contort a D&D night around — listed for completeness.

## 4. Tier 2 — memory pipeline (the DM's specific cost center)

- **Extraction model: already deepseek-v4-flash** ✓ — keep; do not move extraction to Pro [20].
- **Extraction cadence:** plugin default is L1 extraction every 5 turns, L2 persona synthesis every 50 new memories [5]. At 3× prices this is the second-biggest bill after per-turn context. If bills hurt: stretch L1 cadence (every 10 turns) — narrative facts change slowly; L0 raw is always retained for exact recall [1]. Keep the persona cadence as-is (narrative quality).
- **Recall injection budget:** recall is capped by item count + char budget [1]. If per-turn context still feels heavy after Tier 1, tighten the char budget in the gateway config rather than lowering k — precision over volume.
- **Session-end consolidation (narrative + cost):** one batched post-session recap (L2 scene write + campaign attitude ledger in git) replaces scattered reliance on incremental extraction [1]. One extraction call per session, bounded cost, and this is the Hy-Memory-inspired "System2 sleep replay" idea from the deep dive — better continuity for the same or fewer tokens.
- **L0 retention:** capture.l0l1RetentionDays affects disk, not tokens [5]. Leave at 0 unless disk is a concern.

## 5. Tier 3 — behavior (free)

- Use /compress manually in very long sessions instead of waiting for the threshold (auto-compression is enabled in both profiles [17][18]).
- Cron jobs: restrict enabled_toolsets to what each job needs — a scheduled job currently carries the full tool listing in its system prompt every run.
- Delegation: keep the existing bound pattern (read-only briefs, cheap model, watch transcript, kill on loop).
- Background/aux tasks: stay on auto/flash; never point memory or background tasks at premium models [17].

## 6. Expected impact (estimates; measure with /usage before and after)

- ttrpg long-session history tokens: **30–60% lower** after compression tuning [18].
- Cache TTL fix: fewer full-price prefix recomputes (magnitude depends on the new cache rates, which are being cut [16]; still reduces latency).
- Retries to 1: eliminates the worst-case 3× multiplier events [17].
- BM25 "en": recall quality improvement (the only change that strictly helps quality) [5].
- Combined expectation: 30–50% reduction in per-session input tokens for long campaign sessions at near-zero quality loss — plus the session-consolidation cron improves narrative continuity on top [1].

## Sources

[1] https://github.com/TencentCloud/TencentDB-Agent-Memory — TencentDB Agent Memory repo
[5] https://regolo.ai/tencentdb-agent-memory-the-complete-guide-to-persistent-memory-for-hermes-and-openclaw-with-zero-data-retention — Regolo Hermes/OpenClaw setup guide
[14] https://finance.yahoo.com/technology/ai/articles/deepseek-raising-api-prices-1-174027670.html — Yahoo: DeepSeek raising API prices Aug 16
[15] https://api-docs.deepseek.com/quick_start/pricing — DeepSeek official pricing docs
[16] https://www.reddit.com/r/DeepSeek/comments/1vn81do/deepseek_just_massively_increased_their_api — Reddit r/DeepSeek: price increase thread
[17] file:///Users/chriscoon/.hermes/config.yaml — default profile config (audited 2026-08-13)
[18] file:///Users/chriscoon/.hermes/profiles/ttrpg/config.yaml — ttrpg profile config (audited 2026-08-13)
[19] file:///Users/chriscoon/.memory-tencentdb/memory-tdai/tdai-gateway.yaml — memory gateway config (audited 2026-08-13)
[20] file:///Users/chriscoon/.hermes/scripts/start-tencentdb-gateway.sh — gateway launchd launcher script (audited 2026-08-13)

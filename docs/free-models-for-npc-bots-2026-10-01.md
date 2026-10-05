# Free Models for NPC Bots — 2026-10-01

**Purpose.** Pick the free OpenRouter model(s) that run the **NPC bots**. The GM bot
stays on `deepseek-flash` — free models are for NPCs only (owner constraint, 2026-10-01).

**Method.** Live pull of `GET https://openrouter.ai/api/v1/models` on 2026-10-01 ~19:50 PT,
filtered for $0 in/out pricing: **21 of 464 models are free**. Quality scores below come
from CostGoat's free-model table (Theozard scores); usage signals come from OpenRouter's
own collections (updated Sep 2026); stealth facts from the model pages and the 2026-09-29
Space Bunny guide.

## Headline findings

- **ox-alpha (the original NPC pick) is no longer free.** Its model page now reads
  "The free stealth period has ended" and points at a paid successor. The claims in
  `bot/` docs were corrected in the same pass as this survey.
- **The free stealth model of the moment is `stealth/space-bunny-alpha`** — currently the
  **#1 roleplay model on OpenRouter by real usage**, ahead of paid DeepSeek V4.1 Flash and
  GLM 5.3 Flash. 1M context, tool calling, image/video input, $0.
  **⚠ Its listing expires 2026-10-05** (the API's own `expiration_date` field).
  Audition it; do not wire it in long-term.
- **Stealth listings rotate by design.** ox-alpha lasted about six weeks. Any NPC model
  binding must be a one-line, swappable config (`model.default`) — never hardwired.

## The free list tonight — the ones worth knowing

Chat/text models, all tool-calling capable:

- `stealth/space-bunny-alpha` — 1M ctx — **free preview ends 2026-10-05** — top RP usage
- `qwen/qwen3.8-27b:free` — 262K — quality 58 (top of the free bench) — vision
- `thinkingmachines/inkling:free` — 1M — quality 43 — reasoning, vision
- `thinkingmachines/inkling-small:free` — 1M — quality 48 — reasoning, vision
- `nvidia/nemotron-3-ultra-550b-a55b:free` — 1M — quality 40 — most-used free model on the
  platform (3.85T tokens / last 7 days)
- `nvidia/nemotron-3.5-lightning:free` — 1M — high-throughput MoE (3B active)
- `nvidia/nemotron-3-super-120b-a12b:free` — 262K
- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` — 256K
- `apodex/apodex-1.1-mini:free` — 262K — launched 2026-10-01 (day one; unvetted; reasoning-first)
- `dots-studio/dots-3-note-preview:free` — 512K — popular; **preview expires 2026-12-31**
- `poolside/laguna-s-2.1:free` / `laguna-xs-2.1:free` — 262K — coding-focused
- `google/gemma-4-31b-it:free` / `gemma-4-26b-a4b-it:free` — 262K — vision
- `inclusionai/ling-3.0-flash-sante:free` / `-fin:free` — 262K — finance-tuned
- `cohere/north-mini-code:free` — 256K — coding
- `liquid/lfm-2.5-2.6b:free` — 66K — tiny

Not usable for NPCs: `nvidia/nemotron-3.5-content-safety:free` (classifier),
`google/lyria-3-*` (music). **`openrouter/free`** (router that picks a random free model
per request) is fine for off-agent chores but **wrong for NPCs** — the voice would change
scene to scene.

Refresh anytime — the exact same filter this survey used:

```bash
curl -s https://openrouter.ai/api/v1/models | python3 -c \
  "import json,sys; [print(m['id']) for m in json.load(sys.stdin)['data'] \
   if m.get('pricing',{}).get('prompt')=='0' and m.get('pricing',{}).get('completion')=='0']"
```

## Rate limits (per account)

- Free models carry per-minute and per-day caps. Per OpenRouter's FAQ/blog: **50 free-model
  requests/day**, raised to **1,000/day once at least $10 of credits have been purchased**
  (lifetime). Commonly cited per-minute cap: ~20/min.
- Extra API keys don't help (limits are governed globally per account) — but limits differ
  **by model**, so load can be spread across models if ever needed.
- **This account qualifies for the 1,000/day tier** (checked 2026-10-01 via `GET /api/v1/key`:
  credits purchased before; $21.78 lifetime usage; key cap $10 with ~$10 remaining).
- Keep the balance at or above $0 — a negative balance errors even on free models.

## Recommendation

1. **Binding:** keep the NPC model a one-line swap (`model.default`, raw id — never an
   alias). Stealth and `:free` listings rotate — see ox-alpha. *(Superseded 2026-10-04
   evening: NPCs consolidated onto the GM stack — `deepseek-flash`; this survey stands
   as the cost-mode / fallback reference.)*
2. **Bake-off when NPC #1 is built:** same SOUL + same scene brief through 3 candidates,
   judge voice in one sitting:
   - Space Bunny Alpha (while it lasts — until Oct 5) — the current RP leader
   - Qwen3.8-27B:free — stable, highest quality score
   - Inkling (or Inkling-small):free — stable, 1M context
   - Wildcard: Nemotron 3 Ultra — the most battle-tested free listing
3. **Fallback:** define a second model as fallback so a 429 or a delisted model degrades
   to another free model instead of stalling the table.
4. **Privacy:** free and stealth listings retain prompts per their terms (stealth ones
   retain but do not train; some open-weight free variants train on inputs). Game fiction
   only — nothing sensitive should flow through NPC chat anyway.

## Related

- `~/workspace/free-model-offload-research-2026-08-04.md` — earlier offload research
  (rate-limit empirics: 8 rapid calls, no 429; free tier for off-agent work)
- `docs/npc-bots-design-sketch-2026-08-26.md` — NPC-as-profile design
- `bot/npc-maker/README.md` — the NPC bot maker: dossier standard, creation script, activation/voice protocol, model policy + swap one-liner

## Bake-off results — 2026-10-04 (first NPC: Billy Ray Spivey)

The voice bake-off prescribed above was run (same persona, same scene brief —
the interview room, the open door) while NPC bot #1 was built:

- **Nemotron 3 Ultra 550B `:free`** — full, in-voice sample; writes Billy novel-style (third-person beats, first-person dialogue). Consistent across runs.
- **Space Bunny Alpha** — clean, spare, first-person sample. Listing expires 2026-10-05: audition only, never a long-term bind.
- **Qwen3.8-27B `:free`** — a reasoning model: at a 500-token budget it spent everything thinking and emitted no content. With ~1.6k of headroom it produced a solid in-voice sample (one retry hit a free-tier 429 first — worth knowing for burst usage).
- **Inkling / Inkling-small `:free`** — 403 for direct API calls: *"only available on agentic harnesses"* — OpenRouter gates these free endpoints to approved harness/app clients. Possibly reachable through Hermes itself; untested.
- Raw samples: ttrpg profile scratch, `bakeoff/`. The binding is one line: `hermes -p npc-<slug> config set model.default <model-id>` — raw ids only (alias values with a provider-name vendor token get re-routed by provider auto-detection; see maker README). **Runtime-verified 2026-10-04:** qwen3.8-27B holds ~7–8s turns through the profile.

**Policy update — 2026-10-04 (evening).** Owner call: NPC bots run the same model
stack as the GM — `deepseek-flash` on the `deepseek` provider — superseding the
free-model binding for NPCs. This survey and the bake-off above remain the
reference for cost-mode swaps and fallbacks (the bind stays one line:
`model.default`).

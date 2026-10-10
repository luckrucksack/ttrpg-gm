# AI NPC Agents for TTRPGs — Landscape Survey (Oct 2026)

*Who else is doing what we're doing: persistent per-NPC agents + an orchestrating GM agent, live in a VTT.*

- **Survey date:** 2026-10-08 · **Method:** three parallel research passes (products/tools/VTT integrations; community/practitioner practice; academic + industry), ~40 searches; headline links spot-checked live. Vendor self-descriptions marked as such.
- **Headline finding:** no public product, project, or play report found that replicates our exact pattern — one persistent agent per NPC (own memory, own voice) plus a separate GM agent orchestrating them agent-to-agent, across sessions, live in a VTT. The building blocks all exist separately; the full assembly is unclaimed in public as of this date.

## Closest on Foundry VTT (our platform)
- **Familiar** — https://foundryvtt.com/packages/familiar (site: https://familiarvtt.com/) — AI co-pilot for the DM side; "every NPC in its own voice"; memory bank carries campaign facts across sessions; BYOK (23+ providers); MCP server (npm `familiar-vtt`); $6/mo or $99 lifetime. It is one AI running the whole cast — not one agent per NPC. Closest deployed Foundry piece. *(verified live)*
- **Chronicle Keeper** — https://foundryvtt.com/packages/chronicle-keeper — local-Ollama co-DM; NPCs remember your name, past interactions, secret motivations; "living memory" of facts/relationships. Per-NPC memory inside one engine. *(verified live)*
- **Intelligent NPCs** — https://foundryvtt.com/packages/intelligent-npcs — AI NPC dialogue; persistence claims, Patreon-gated.
- **Archive of Voices Pro** — https://foundryvtt.com/creators/shadowdrake-creations/ — AI NPC dialogue + memory tracking.
- **UnKenny** — https://foundryvtt.com/packages/unkenny — limited "tiny dialogue" prototype.
- **MCP bridges** (same layer we use, independent projects): https://github.com/adambdooley/foundry-vtt-mcp · https://github.com/Gnuminator/Foundry-VTT-MCP-Ai-Tool · https://foundryvtt.com/packages/ninjos-foundry-mcp
- **Roll20:** nothing official; DIY forum threads only. **Fantasy Grounds:** one community Claude-NPC thread.

## Open-source / self-hosted
- **Corvus Story Core** — https://github.com/JustLateNightAI/Corvus-Story-Core — local-first GM; auto-generated NPC cards each with a running memory of past interactions; distinct voices. Closest OSS to our per-NPC-memory half. *(verified live)*
- **NarrativeEngine-P** — https://github.com/Sagesheep/NarrativeEngine-P — self-hosted AI DM; multi-session persistent memory; "living NPCs."
- **dmcp** — https://github.com/shawnrushefsky/dmcp — MCP server giving AI DMs 170 tools incl. multi-agent collaboration, per-character secrets, factions, relationships. Closest to our messaging half.
- **open-tabletop-gm** — https://github.com/Bobby-Gray/open-tabletop-gm — persistent campaigns as Markdown state; runs on Claude Code / local models.
- **ITMO ai-dungeon-master** — https://github.com/ITMO-Agentic-AI/ai-dungeon-master — 8 role-specialized LangGraph agents on shared state (multi-agent GM, not per-NPC).

## Academic anchors
- **Orchestrated Reality** — https://arxiv.org/abs/2606.16014 (2026) — singleton orchestration agent "analogous to the tabletop GM" over persistent world state. Closest formal framing of our GM half. *(verified live)*
- **Generative Agents** — https://arxiv.org/abs/2304.03442 (Stanford, UIST 2023) — the memory-stream architecture most per-NPC projects copy.
- **MemGPT / Letta** — https://arxiv.org/abs/2310.08560 — persistent memory substrate, productized as Letta (https://www.letta.com/).
- Also: "Guiding, Not Railroading" (IUI '26) https://dl.acm.org/doi/10.1145/3742413.3789218 · "Static vs. Agentic GM" https://arxiv.org/abs/2502.19519 · Lifelong SOTOPIA https://arxiv.org/abs/2506.12666 · Project Sid https://arxiv.org/abs/2411.00114 · D&D Agents (NeurIPS 2025) https://openreview.net/pdf?id=3Op7kJOvaD · AWS Strands multi-agent GM demo https://dev.to/aws/dev-track-spotlight-build-a-multi-agent-role-playing-game-master-with-strands-agents-dev330-4ia1

## Industry
- **Inworld** — https://inworld.ai/ — conversational-NPC runtime (video games).
- **Convai** — https://convai.com/ + "Mimir" long-term NPC memory https://convai.com/blog/long-term-memory---a-technical-overview — closest industry analog of memory-bearing NPCs.
- **NVIDIA ACE** — https://developer.nvidia.com/ace-for-games — autonomous character stack.
- **Everwhere** — https://everwhere.app/blog/ai-dungeon-master-dnd-guide — claims a multi-agent GM (GM agent owns plot/rules/NPC portrayal). Vendor claim, unverified.
- **Friends & Fables** — https://fables.gg/ — AI GM with persistent game-state DB. **Hidden Door** — https://www.hiddendoor.co/ — stateful AI storytelling.
- **Fable Forge** — listed at https://arcanumrpgs.com/clients/compare/ — preview platform claiming per-NPC auto-generated memories (third-party description, pre-release).
- **Resource:** The AI RPG Directory (2026) — https://arcanumrpgs.com/blog/llm-rpg-games/ — best single landscape source.

## Community / practitioner
- No public play report of the full pattern found. Current vanguard = "AI GM with memory": r/LLMDevs memory-wall thread https://www.reddit.com/r/LLMDevs/comments/1tf7oxb/ · r/LocalLLaMA persistent-world build https://www.reddit.com/r/LocalLLaMA/comments/1v6ol1n/ · local-LLM-assisted campaign https://www.reddit.com/r/DungeonsAndDragons/comments/1lgrfii/
- Inversion case: a UK TTRPG writer running AI agents as the *players* — https://redcirclegames.co.uk/posts/2026/05/14/ai-dungeon-masters-but-what-about-ai-players.html
- Venues where this crowd lives: EN World "AI Echo Cave" sub-forum; r/dndai; r/Solo_Roleplaying.

## Hermes-specific (found during survey)
- **"Understanding The Hermes Agent Through D&D"** — Raghunaathan, Towards AI, 2026-04-19 — https://pub.towardsai.net/understanding-the-hermes-agent-through-d-d-0f7db2d53d77 — Hermes Agent explained as a D&D DM: four-layer memory, a custom SQLite MCP server for game state (HP/inventory/dice), skills-as-playbook, security guardrails. Single agent as DM; no per-NPC agents. *(read in full; Cloudflare-walled to curl, readable in a browser)*
- Community refs it cites: hermesagents.net "one agent, many front doors" https://hermesagents.net/blog/seven-chat-platforms-one-gateway/ · "I Built an AI Dungeon Master That Actually Plays D&D" (Medium, Micheal Lanham).

## Caveats
- Public web only; "none found" means none found publicly, not proof of absence.
- Several entries are vendor self-descriptions (Everwhere, Fable Forge, NarrativeEngine-P) — rated from public docs, internals not verified.
- Reddit bodies were network-blocked during the sweep; those entries rest on search snippets (one full thread read via browser).

I'm setting up Hermes Agent as an AI Dungeon Master for tabletop RPGs. Here's the architecture I'm working with and what I need researched.

## Current Hermes Setup

- **Main model**: DeepSeek V4 Pro (via DeepSeek direct)
- **Provider**: OpenRouter API key configured for auxiliary tasks
- **Auxiliary models configured so far**:
  - `background_review` → MoonshotAI Kimi K3 (2.8T params, $3/M in, $15/M out)
  - `kanban_decomposer` → MoonshotAI Kimi K3
  - `vision` → Google Gemini 3 Flash Preview (considering switching to Qwen3-VL-235B or UI-TARS-1.5)
  - `title_generation` → Google Gemini 3 Flash Preview
  - All other auxiliary tasks → auto (DeepSeek V4 Pro)
- **PDF pipeline**: `marker-pdf` for PDF → Markdown conversion (via ocr-and-documents skill)
- **Platforms**: Discord, Telegram, WebUI connected
- **Profiles**: Has a separate `ttrpg` Hermes profile

## The DM Architecture Plan

Published D&D modules come as PDFs. The pipeline:
1. PDF → marker-pdf → Markdown text
2. Markdown stored as reference documents
3. At game time, RAG retrieves relevant sections (room descriptions, NPC stats, encounter tables)
4. Only currently relevant content enters the context window

## Open Questions

1. **Map strategy**: I plan to keep maps as images (NOT convert to Markdown — spatial info would be destroyed). The vision model reads maps on demand. For persistent state (party position, explored areas, fog of war), maintain structured spatial data. Is there a better approach for LLM-based TTRPG map handling?

2. **Context management for long campaigns**: D&D sessions can run many hours with dozens of turns. What are the best strategies for keeping context lean during long sessions — beyond Hermes' built-in compression? Specifically: how to structure the DM's "working memory" (current scene, active NPCs, combat state) vs "long-term memory" (world state, completed quests, NPC relationships)?

3. **Innovative approaches since mid-2026**: What's the state of the art for LLM-powered TTRPG DMing? Specifically:
   - Spatial graph representations for maps (nodes = rooms, edges = connections, coordinates)
   - Multi-agent DM architectures (separate agents for narration, combat mechanics, NPC dialogue)
   - Tools or frameworks for structured encounter management
   - Any purpose-built tools/skills for Hermes Agent specifically

4. **Token optimization for TTRPG modules**: What's the best way to chunk and retrieve from large rulebooks/modules? Any advances in RAG specifically for structured RPG content (stat blocks, tables, hierarchical location descriptions)?

5. **Best Chinese/cheap vision model for map reading**: For understanding dungeon maps, battle maps, and region maps. Need accurate spatial comprehension, distance estimation, and layout description. Comparing Qwen3-VL-235B vs UI-TARS-1.5 vs alternatives.

6. **Anything else I'm not thinking of** that would meaningfully improve an LLM-based DM.

Return a structured analysis with recommendations prioritized by impact/cost ratio.

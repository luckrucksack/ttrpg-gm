# GM Bot — Hermes Bot Configuration

The GM Bot is a Hermes Bot running in the `ttrpg` profile.
It's the primary orchestrator that talks to the player, manages
Foundry, coordinates NPC Bots, and maintains campaign memory.

## Profile

The ttrpg profile is already configured at
`~/.hermes/profiles/ttrpg/` with:

- **Provider**: OpenRouter (key in profile `.env`)
- **Default model**: `deepseek/deepseek-v4-flash` — routine GM work
- **Heavy scenes** (complex adjudication, deep prose): switch to
  `deepseek/deepseek-v4-pro` via `/model` for that session — see
  Model Routing below
- **Memory**: TencentDB Agent Memory (:8421)
- **Skills**: loaded from this repo's `bot/skills/`

## Model Routing

| Job | Model |
|-----|-------|
| Routine GM work (narration, MCP ops, session flow) | deepseek-v4-flash (default) |
| Heavy scenes (complex adjudication, long prose) | deepseek-v4-pro — switch with `/model` mid-session |
| NPC Bots (isolated profiles) | ox-alpha (free tier) |
| Editing loop (future) | z.ai GLM 5.2 (key stored, not wired) |

Rule: default stays flash; promote to pro per-session only when the scene
needs it. Cost is the constraint — see
`docs/ai-dm-token-reduction-playbook-2026-08-13.md`.

## Required config additions

Add to `~/.hermes/profiles/ttrpg/config.yaml`:

```yaml
# MCP: Foundry bridge
mcp_servers:
  foundry:
    command: "npx"
    args: ["-y", "foundryvtt-mcp"]
    env:
      FOUNDRY_URL: "http://localhost:30000"
      FOUNDRY_USERNAME: "mcp-api"
      FOUNDRY_PASSWORD: "<your-password>"
      FOUNDRY_WRITE_ENABLED: "true"
    timeout: 120
    connect_timeout: 30

# Skills from this repo
skills:
  external_dirs:
    - ~/ttrpg_gm/bot/skills
```

## Loaded Skills

| Skill | Purpose |
|-------|---------|
| `ttrpg-narrator` | Prose style guide, tone, pacing, scene framing |
| `ttrpg-prohibitions` | Anti-cliché ban list, self-check rules |
| `ttrpg-foundry-bridge` | MCP tool reference for Foundry operations |
| `ttrpg-campaign-tools` | Session log format, world state conventions |

## GM Bot Persona (SOUL.md)

The GM Bot itself has a defined voice — it narrates in third-person,
uses present tense, and adheres to the narrator skill's style guide.
It does NOT roleplay as NPCs directly (that's what NPC Bots are for).
It describes what NPCs do and say, then delegates deep interaction.

## Session Mode

The GM Bot runs in Hermes Bot Mode — a named bot with persistent
chat history, reachable via the Bots tab in the Hermes desktop app
or via Discord through the ttrpg profile's gateway.
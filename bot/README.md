# GM Bot — Hermes Bot Configuration

The GM Bot is a Hermes Bot running in the `ttrpg` profile.
It's the primary orchestrator that talks to the player, manages
Foundry (including the NPC dossiers), and maintains campaign memory.

## Profile

The ttrpg profile is already configured at
`~/.hermes/profiles/ttrpg/` with:

- **Provider**: DeepSeek (native API; key in profile `.env`)
- **Default model**: `deepseek-flash` (provider `deepseek`) — routine GM work
- **Heavy scenes** (complex adjudication, deep prose): switch to
  `deepseek/deepseek-v4-pro` via `/model` for that session — see
  Model Routing below
- **Memory**: TencentDB Agent Memory (:8421)
- **Skills**: loaded from this repo's `bot/skills/`

## Model Routing

| Job | Model |
|-----|-------|
| Routine GM work (narration, MCP ops, session flow) | `deepseek-flash` (default) |
| Heavy scenes (complex adjudication, long prose) | deepseek-v4-pro — switch with `/model` mid-session |
| Editing loop (future) | z.ai GLM 5.2 (key stored, not wired) |

Rule: default stays flash; promote to pro per-session only when the scene
needs it. Cost is the constraint — see
`docs/ai-dm-token-reduction-playbook-2026-08-13.md`.

## Required config additions

Add to `~/.hermes/profiles/ttrpg/config.yaml`:

```yaml
# MCP: Foundry bridge (vendored patched build — see bridge/vendor/setup.sh)
mcp_servers:
  foundry:
    command: "/Users/chriscoon/.local/bin/node"
    args: ["/Users/chriscoon/ttrpg_gm/bridge/vendor/foundryvtt-mcp/dist/index.js"]
    env:
      FOUNDRY_URL: "http://localhost:30000"
      FOUNDRY_USERNAME: "mcp-api"
      FOUNDRY_PASSWORD: "${MCP_FOUNDRY_PASSWORD}"   # expanded from the profile .env
      FOUNDRY_WRITE_ENABLED: "true"
      FOUNDRY_JOURNAL_TEXT_LIMIT: "20000"
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
| `ttrpg-ai-gm` | The AI GM core — identity, doctrine index, owner feedback ledger; the entry point |
| `ttrpg-narrator` | Prose style guide, tone, pacing, scene framing |
| `ttrpg-prohibitions` | Anti-cliché ban list, self-check rules |
| `ttrpg-foundry-bridge` | MCP tool reference for Foundry operations |
| `ttrpg-campaign-tools` | Session log format, world state conventions |

`ttrpg-ai-gm` is read first every session; it routes to the doctrine files
and logs the owner's feedback as it comes.

## GM Bot Persona (SOUL.md)

The GM Bot itself has a defined voice — it narrates in third-person,
uses present tense, and adheres to the narrator skill's style guide.
It voices every NPC itself, working from that NPC's Foundry dossier; it
never delegates a character to another agent.

## NPC Dossiers (Foundry)

Every significant NPC's character sheet lives in Foundry — a **GM-only journal**
in the `deltagreen` world, one per NPC, which the GM Bot looks up
(`search_journals` → `get_journal`) when that NPC takes a real part in a scene,
and voices inline. There is no delegation, no NPC profile, and no repo-side
copy: the journal is the only home. The authoring standard and blank sheet live
in Foundry beside the dossiers (`NPC Dossier — Writing Standard (GM)`).

The NPC bot system (one isolated Hermes profile per NPC, driven through Bot
Mode's `message_agent`) and its maker were **retired 2026-10-11**; the retired
base structure is kept as history in
`docs/npc-bot-base-structure-v2-2026-10-09.md`.

## Session Mode

The GM Bot runs in Hermes Bot Mode — a named bot with persistent
chat history, reachable via the Bots tab in the Hermes desktop app
or via Discord through the ttrpg profile's gateway.
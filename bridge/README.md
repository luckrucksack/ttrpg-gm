# Bridge: Foundry VTT MCP Connection

This module connects the Hermes GM Bot to Foundry VTT via
[laurigates/foundryvtt-mcp](https://github.com/laurigates/foundryvtt-mcp) — an
open-source MCP server that exposes Foundry's internal API as tools.

## Architecture

```
GM Bot (Hermes ttrpg profile)
  ┃ native MCP client
  ┃
  ┃ foundryvtt-mcp (Node.js process, managed by Hermes)
  ┃  ─ reads actors, journals, scenes
  ┃  ─ creates/updates documents
  ┃  ─ manages combat, initiative, conditions
  ┃  ─ rolls dice via Foundry's engine
  ┃
  ▼
Foundry VTT (:30000)
```

## Setup

### 1. Create a Foundry user for the MCP server

In Foundry VTT:
1. Go to **Configuration → User Management**
2. Click **Create User**
3. Username: `mcp-api`
4. Password: generate a strong one
5. Role: **Assistant GM** (needed to read world data and mutate game state)
6. Save

### 2. Configure the MCP server

The server is installed on demand via npx (no global install needed):

```bash
npx -y foundryvtt-mcp
```

### 3. Wire into Hermes as native MCP server

Add to `~/.hermes/profiles/ttrpg/config.yaml`:

```yaml
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
```

Restart the ttrpg profile. On next load, Hermes discovers these MCP tools
and makes them available to the GM Bot.

## Available Tools

Verified against `foundryvtt-mcp` v1.5.x. Selected tools (full list at the
[upstream repo](https://github.com/laurigates/foundryvtt-mcp)):

| Tool | Purpose |
|------|---------|
| `search_actors` | Find characters/NPCs by name |
| `get_actor_details` | Full character/npc sheet |
| `search_items` | Find equipment, spells |
| `get_scene_info` | Current scene details |
| `search_journals` | Find notes and handouts |
| `get_journal` | Retrieve a specific journal |
| `get_users` | List online users |
| `get_combat_state` | Combat and initiative |
| `get_chat_messages` | Recent chat log |
| `start_combat` | Begin encounter |
| `next_turn` | Advance initiative |
| `end_combat` | End encounter |
| `set_initiative` | Set combatant turn order |
| `move_token` | Move token on scene |
| `apply_status_effect` | Apply/remove conditions |
| `update_actor_attributes` | Update HP, stats |
| `create_actor_item` | Add item to actor |
| `update_actor_item` | Modify actor item |
| `delete_actor_item` | Remove actor item |
| `create_journal_entry` | Create journal entry |
| `search_world` | Full-text search all entities |
| `get_world_summary` | Overview of world state |
| `roll_dice` | Roll dice via Foundry |
| `generate_npc` | NPC text (not written to world) |
| `generate_loot` | Treasure text (not written to world) |

Stubs present upstream — do NOT rely on their output: `lookup_rule`
(placeholder), `diagnose_errors` (fixed "no errors" reply).

Writes require `FOUNDRY_WRITE_ENABLED=true` **and** the connecting user to have
GM/owner permission. There is **no `create_actor` tool** — actors are created
in Foundry's UI, then referenced by the bot (see `pipeline/import_foundry.py`).

MCP tool names are prefixed by Hermes: `mcp_foundry_search_actors`,
`mcp_foundry_roll_dice`, etc.

## Extending

If the MCP server lacks a tool we need (e.g., roll table CRUD, NPC auto-pilot,
campaign memory management), the repo can be forked and extended.

The bridge is designed to be replaced transparently — all GM Bot code talks
to Foundry through these tool abstractions, not direct HTTP calls. Swap the
backend by changing the MCP server.
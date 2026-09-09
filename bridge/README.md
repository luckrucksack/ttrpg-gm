# Bridge: Foundry VTT MCP Connection

Connects the Hermes GM Bot to Foundry VTT via
[laurigates/foundryvtt-mcp](https://github.com/laurigates/foundryvtt-mcp) — an
open-source MCP server that exposes Foundry's document API as tools.

## Architecture

```
GM Bot (Hermes ttrpg profile)
  ┃ native MCP client
  ┃
  ┃ foundryvtt-mcp (Node.js process, managed by Hermes)
  ┃  ─ reads actors, journals, compendia, scenes
  ┃  ─ creates/updates documents
  ┃  ─ manages combat, initiative, conditions
  ┃  ─ rolls dice via Foundry's engine
  ┃
  ▼
Foundry VTT (:30000)
```

## Setup

### 1. Create a Foundry user for the MCP server

In Foundry VTT, with the world running:

1. **Configuration → User Management → Create User**
2. Username: `mcp-api`
3. Password: the value of `MCP_FOUNDRY_PASSWORD` in the profile `.env`
   (see step 3 — read it from there rather than inventing one)
4. Role: **Assistant GM** (required to read world data and mutate game state)
5. Save

Foundry hashes the password server-side on create, so the same plaintext value
works for the socket login.

### 2. Confirm the server runs

```bash
npx -y foundryvtt-mcp@1.5.2
```

It speaks stdio MCP; a bare run with valid env vars stays attached and silent.
That is success. It exits non-zero on a bad URL, bad credentials, or a stopped
world.

### 3. Wire into Hermes

`~/.hermes/profiles/ttrpg/config.yaml`:

```yaml
mcp_servers:
  foundry:
    command: "npx"
    args: ["-y", "foundryvtt-mcp@1.5.2"]
    env:
      FOUNDRY_URL: "http://localhost:30000"
      FOUNDRY_USERNAME: "mcp-api"
      FOUNDRY_PASSWORD: "${MCP_FOUNDRY_PASSWORD}"
      FOUNDRY_WRITE_ENABLED: "true"
    timeout: 120
    connect_timeout: 30
```

The secret itself lives in `~/.hermes/profiles/ttrpg/.env` (mode 600):

```
MCP_FOUNDRY_PASSWORD=<generated at provisioning time>
```

Hermes expands `${VAR}` from the profile's secret scope at launch, so the
password never appears in `config.yaml` or in git.

> Gotcha: an **unset** variable is passed through literally. If auth fails with
> a password that looks like `${...}`, the variable is missing from the `.env`
> the profile loads.

Pin the version (`@1.5.2`). `npx -y foundryvtt-mcp` floats to latest and a
tool-signature change would silently break the skill's parameter names.

### 4. Restart the ttrpg profile, then verify

```bash
bash bridge/check.sh
```

## Verifying the bridge

`bridge/check.sh` proves all four links in one shot: Foundry reachable → service
account exists → credentials authenticate → the MCP server registers tools. Run
it after any Foundry or Hermes update. A bridge that is "configured" but not
"authenticated" looks identical in `config.yaml`; this is the check that tells
them apart.

## Available Tools

Verified against the installed `foundryvtt-mcp@1.5.2` (33 tools).

Read / query:
- `roll_dice` — roll a formula through Foundry's dice engine
- `search_actors`, `get_actor_details` — find and inspect actors
- `search_items` — find items by name/type/rarity
- `search_compendium` — search installed compendium packs (adventure content)
- `search_journals`, `get_journal` — find and read journal entries
- `search_world` — one search across all collections
- `get_scene_info`, `get_world_summary`, `get_users`, `get_chat_messages`
- `refresh_world_data` — force a re-fetch after a Foundry restart
- `generate_npc`, `generate_loot` — dnd5e-shaped text generators, no world writes

Write (require `FOUNDRY_WRITE_ENABLED=true` **and** Assistant GM+ permission):
- `update_actor_attributes` — patch `actor.system` fields by dot-path
- `create_actor_item`, `update_actor_item`, `delete_actor_item`
- `create_journal_entry` — GM-only visibility unless `visibility` is passed
- `start_combat`, `next_turn`, `end_combat`, `set_initiative`
- `move_token`, `apply_status_effect`

Not usable as documented by upstream:
- `lookup_rule` — stub, returns a templated placeholder, consults no rules source
- `diagnose_errors` — stub, always reports "no errors detected"
- `get_recent_logs`, `search_logs`, `get_system_health`, `get_health_status` —
  require the third-party REST API module, which is **not installed** in this
  world (world.json lists zero modules)

There is **no `create_actor` tool**. Actors are created in Foundry's UI or
imported, then referenced by the bot (see `pipeline/import_foundry.py`).

Hermes prefixes every tool: `mcp_foundry_search_actors`, `mcp_foundry_roll_dice`, …

## Failure modes (verified)

- **Foundry down or credentials wrong ⇒ the MCP server exits.** It does not
  start in a degraded state; Hermes ends up with *no* `mcp_foundry_*` tools at
  all. Any GM logic that assumes tools exist must check first.
- **Foundry restart ⇒ stale cache.** Reads are cached and follow live document
  changes, but a restart can leave the cache cold. Call `refresh_world_data()`.
- **Auth is a socket login, not an API key.** The username must exist in the
  *running world*; a user in a different world does nothing.

## Extending

If the MCP server lacks a tool we need (roll table CRUD, NPC auto-pilot,
campaign memory management), fork and extend. The bridge is designed to be
swapped transparently: GM Bot logic talks to Foundry only through these tool
abstractions, so the backend can be replaced by changing the MCP server.

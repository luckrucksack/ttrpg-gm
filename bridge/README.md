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

### 2. Build the vendored server

The GM runs a **vendored, patched** copy of the pinned package. Upstream
hard-codes a 500-character limit on journal page text, which truncates long
entries (the NPC dossiers) mid-sentence.

```bash
bash bridge/vendor/setup.sh          # vendors foundryvtt-mcp@1.5.2 + applies the local patch
node bridge/vendor/foundryvtt-mcp/dist/index.js    # bare run: attached and silent = success
```

The vendored tree is gitignored; `setup.sh` rebuilds it from npm plus the patch
and prints the delta. It speaks stdio MCP; a bare run with valid env vars stays
attached and silent. That is success. It exits non-zero on a bad URL, bad
credentials, or a stopped world.

### 3. Wire into Hermes

`~/.hermes/profiles/ttrpg/config.yaml`:

```yaml
mcp_servers:
  foundry:
    command: /Users/chriscoon/.local/bin/node
    args: [/Users/chriscoon/ttrpg_gm/bridge/vendor/foundryvtt-mcp/dist/index.js]
    env:
      FOUNDRY_URL: "http://localhost:30000"
      FOUNDRY_USERNAME: "mcp-api"
      FOUNDRY_PASSWORD: "${MCP_FOUNDRY_PASSWORD}"
      FOUNDRY_WRITE_ENABLED: "true"
      FOUNDRY_JOURNAL_TEXT_LIMIT: "20000"   # the local patch reads this; stock builds ignore it
    timeout: 120
    connect_timeout: 30
```

(Live values are set with `hermes -p ttrpg config set`; see `STATUS.md`.)

The secret itself lives in `~/.hermes/profiles/ttrpg/.env` (mode 600):

```
MCP_FOUNDRY_PASSWORD=<generated at provisioning time>
```

Hermes expands `${VAR}` from the profile's secret scope at launch, so the
password never appears in `config.yaml` or in git.

> Gotcha: an **unset** variable is passed through literally. If auth fails with
> a password that looks like `${...}`, the variable is missing from the `.env`
> the profile loads.

Pin the version (`1.5.2`, pinned in `vendor/setup.sh`). A float to latest can
rename tool parameters silently. The pin is now a **vendor pin**: the patched
build is generated from that exact version, so a version bump means re-running
`setup.sh` and re-checking the delta.

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

Verified against the vendored `foundryvtt-mcp@1.5.2` + local patch (34 tools:
33 upstream + `delete_journal_entry`).

Read / query:
- `roll_dice` — roll a formula through Foundry's dice engine
- `search_actors`, `get_actor_details` — find and inspect actors
- `search_items` — find items by name/type/rarity
- `search_compendium` — search installed compendium packs (adventure content)
- `search_journals`, `get_journal` — find and read journal entries
  (`get_journal` page text is capped at `FOUNDRY_JOURNAL_TEXT_LIMIT`; the local
  patch of upstream's hard-coded 500, set to 20000 in the profile env)
- `search_world` — one search across all collections
- `get_scene_info`, `get_world_summary`, `get_users`, `get_chat_messages`
- `refresh_world_data` — force a re-fetch after a Foundry restart
- `generate_npc`, `generate_loot` — dnd5e-shaped text generators, no world writes

Write (require `FOUNDRY_WRITE_ENABLED=true` **and** Assistant GM+ permission):
- `update_actor_attributes` — patch `actor.system` fields by dot-path
- `create_actor_item`, `update_actor_item`, `delete_actor_item`
- `create_journal_entry` — GM-only visibility unless `visibility` is passed
- `delete_journal_entry` — delete a journal by id (local patch; upstream ships
  no update and no delete — an edit is delete + recreate)
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

- **A stray `.env` in the server's working directory can kill it.** The server
  calls `dotenv.config()`, which reads `.env` from its *cwd*. This repo's `.env`
  had `LOG_LEVEL=INFO` (uppercase) and the server's schema accepts only
  `debug|info|warn|error` — so launching with the repo as cwd died instantly
  with an opaque `Connection closed`. Fixed twice over: the value is now
  `info`, and `cwd: /Users/chriscoon/ttrpg_gm/bridge` is pinned in the profile
  config so the server never inherits an arbitrary directory. `check.sh` pins
  the same cwd and prints the server's stderr on failure.
- **Foundry down or credentials wrong ⇒ the MCP server exits.** It does not
  start in a degraded state; Hermes ends up with *no* `mcp_foundry_*` tools at
  all. Any GM logic that assumes tools exist must check first.
- **Foundry restart ⇒ stale cache.** Reads are cached and follow live document
  changes, but a restart can leave the cache cold. Call `refresh_world_data()`.
- **Auth is a socket login, not an API key.** The username must exist in the
  *running world*; a user in a different world does nothing.

## Local patch — `bridge/vendor/`

Upstream `foundryvtt-mcp` stops at 33 tools and hard-codes the journal page
text limit at 500 characters. Rather than fork the project, `bridge/vendor/setup.sh`
vendors the pinned npm package and applies a small, auditable delta (it prints
`diff -u` against `dist.pristine/` every run):

1. `get_journal` page text limit comes from `FOUNDRY_JOURNAL_TEXT_LIMIT`
   (default 500, upstream behavior) and pages render readably — bullets, line
   breaks, decoded entities — instead of run-together text.
2. `delete_journal_entry` — the missing delete path (via the core
   `modifyDocument` socket protocol, same as create).

Bump the version → re-run `setup.sh` → `bash bridge/check.sh`. Anything else the
bridge lacks gets patched the same way, not forked wholesale.

---
name: ttrpg-foundry-bridge
description: MCP tool reference for Foundry VTT operations — actor, journal, compendium, combat, and state management via the foundryvtt-mcp server.
---

# TTRPG Foundry Bridge — MCP Tool Reference

The GM Bot talks to Foundry VTT through Hermes' native MCP client, which
launches `laurigates/foundryvtt-mcp`. All Foundry tools are prefixed
`mcp_foundry_*` and are first-class Hermes tools.

Parameter names below are the **exact** input names from the installed server
(verified against v1.5.2). Foundry rejects unknown or missing required
parameters, so copy them verbatim — `actorId`, not `actor_id`.

## Availability check — do this first

The MCP server **exits at startup if Foundry is unreachable or the credentials
are wrong**. There is no partial mode: either every `mcp_foundry_*` tool exists
or none do.

- Tools missing from your toolset ⇒ Foundry or the bridge is down. Say so
  plainly and run narrative-only. **Never invent Foundry state.**
- After a Foundry restart, call `mcp_foundry_refresh_world_data()` before
  trusting cached reads.

## Reading adventure content

```
mcp_foundry_search_journals(query="Chapter 1")
mcp_foundry_get_journal(journalId="...")
mcp_foundry_search_compendium(query="Moses")
mcp_foundry_search_world(query="dagger")
```

- `search_compendium` reaches content inside installed adventure modules
  (journals, NPCs, items) without importing it first. Scope with
  `filters={compendiumId: "..."}` or `filters={packType: "Actor"}`.
- `search_world` searches all collections at once and groups by type.

## Actors

```
mcp_foundry_search_actors(query="Moses", type="npc")
mcp_foundry_get_actor_details(actorId="...")
mcp_foundry_update_actor_attributes(actorId="...", patch={"attributes.hp.value": 15})
```

- `get_actor_details` returns type, level, current/max HP, AC, and ability
  scores. It does **not** return biography text or the item list.
- `patch` keys are **dot-paths relative to `actor.system`** — write
  `"attributes.hp.value"`, never `"system.attributes.hp.value"`. Values must be
  number, string, or boolean. Read the current shape with `get_actor_details`
  first.
- Items on an actor: `create_actor_item(actorId, source)`,
  `update_actor_item(actorId, itemId, patch)`, `delete_actor_item(actorId, itemId)`.

## Combat

```
mcp_foundry_start_combat()                          # seeds combatants from scene tokens
mcp_foundry_start_combat(tokenIds=["...","..."])    # or an explicit subset
mcp_foundry_get_combat_state()
mcp_foundry_set_initiative(combatantId="...", initiative=18)
mcp_foundry_next_turn(skipDefeated=true)
mcp_foundry_end_combat()
mcp_foundry_roll_dice(formula="1d20+2")
```

Marking a combatant defeated is **not a tool**. Set the actor's health/wound
field with `update_actor_attributes` (read the exact path from
`get_actor_details` for this world's game system), then advance with
`next_turn(skipDefeated=true)`.

## Tokens & conditions

```
mcp_foundry_apply_status_effect(tokenId="...", statusId="prone")
mcp_foundry_apply_status_effect(tokenId="...", statusId="prone", active=false)
mcp_foundry_move_token(tokenId="...", x=1200, y=800)
```

`statusId` is Foundry's condition id (lowercase: `prone`, `stunned`,
`blinded`), not a display label. `active=false` removes the condition.

## Scenes & journals

```
mcp_foundry_get_scene_info()              # active scene
mcp_foundry_get_scene_info(sceneId="...")
mcp_foundry_create_journal_entry(
    name="Session 1",
    pages=[{name: "Notes", content: "..."}]
)
```

`create_journal_entry` is **GM-only by default**; pass `visibility` to widen it.
Each page is `{name, content}` where `content` is HTML or plain text.

## Session flow

### Player says "I go see the blacksmith"

1. `mcp_foundry_search_actors(query="blacksmith")` — find the NPC
2. `mcp_foundry_get_actor_details(actorId)` — current stats and state
3. Check campaign memory (TencentDB) for prior interactions
4. Narrate the scene and NPC dialogue via the narrator skill
5. Deep NPC interaction ⇒ delegate to the NPC Bot profile

### Combat starts

1. `mcp_foundry_start_combat()` — seeds combatants from the scene
2. `mcp_foundry_roll_dice(formula=...)` for initiative, then
   `set_initiative(combatantId, initiative)`
3. Narrate the opening
4. Each turn: `get_combat_state()` → tactics → `next_turn(skipDefeated=true)`
5. Damage/conditions: `update_actor_attributes` and
   `apply_status_effect(tokenId, statusId)`
6. Defeated: zero the actor's health field (see Combat above)

## Error handling

- A failed tool call: retry once after 2s, then report the failure plainly.
- All `mcp_foundry_*` tools missing ⇒ bridge is down (see availability check).
  Narrative-only mode, and tell the user the bridge is offline.
- `lookup_rule` and `diagnose_errors` are upstream stubs that return
  placeholder text — never use them.
- `generate_npc` / `generate_loot` are dnd5e-shaped text generators that do not
  write to the world. Not used for this campaign.
- Diagnostics tools (`get_recent_logs`, `search_logs`, `get_system_health`,
  `get_health_status`, `diagnose_errors`) require the third-party REST API
  module, which is not installed — treat them as unavailable.
- Log all Foundry interactions to campaign memory.

## Campaign Memory Integration

Foundry is the source of truth for game state. Campaign memory (TencentDB) is
the source of truth for narrative history.

Rule: on a conflict, **Foundry wins** for stats/state, **memory wins** for
narrative details (NPC relationships, plot threads).

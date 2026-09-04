---
name: ttrpg-foundry-bridge
description: MCP tool reference for Foundry VTT operations — actor, journal, combat, state management via the foundryvtt-mcp server.
---

# TTRPG Foundry Bridge — MCP Tool Reference

The GM Bot communicates with Foundry VTT via the native MCP client,
which connects to `laurigates/foundryvtt-mcp`.

All Foundry tools are prefixed `mcp_foundry_*` and are available
as first-class Hermes tools.

## Common Operations

### Reading adventure content (journals)
```
mcp_foundry_search_journals(query="Chapter 1")
mcp_foundry_get_journal(id="...")
```

### Managing actors (NPCs, monsters, PCs)
```
mcp_foundry_search_actors(query="Moses")
mcp_foundry_get_actor_details(id="...")
mcp_foundry_update_actor_attributes(
    actor_id="...",
    attributes={"system.attributes.hp.value": 15}
)
```

### Running combat
```
mcp_foundry_start_combat()
mcp_foundry_get_combat_state()
mcp_foundry_next_turn()
mcp_foundry_set_initiative(combatant_id="...", value=18)
mcp_foundry_end_combat()
```

### Managing state
```
mcp_foundry_apply_status_effect(actor_id="...", effect="Prone")
mcp_foundry_move_token(token_id="...", x=1200, y=800)
mcp_foundry_create_journal_entry(name="Session Notes", content="...")
mcp_foundry_roll_dice(formula="1d20+5")
```

### World info
```
mcp_foundry_get_world_summary()
mcp_foundry_get_scene_info(scene_id="...")
mcp_foundry_search_world(query="dagger")
```

## Session Flow

### Player says "I go see the blacksmith"

1. GM Bot calls `mcp_foundry_search_actors(query="blacksmith")` to
   find the NPC in Foundry
2. GM Bot calls `mcp_foundry_get_actor_details(id)` to get current
   stats, inventory, description
3. GM Bot checks campaign memory (TencentDB) for prior interactions
4. GM Bot generates narrative and NPC dialogue via narrator skill
5. If a deep NPC interaction is warranted → delegate to NPC Bot

### Combat starts

1. GM Bot calls `mcp_foundry_start_combat()` to create the encounter
2. GM Bot calls `mcp_foundry_roll_dice(formula="1d20+2")` for initiative
3. GM Bot narrates the opening of combat
4. Each turn: GM Bot checks state via `mcp_foundry_get_combat_state()`
5. GM Bot runs monster tactics, calls `mcp_foundry_next_turn()`
6. GM Bot applies damage/conditions via `mcp_foundry_apply_status_effect()`
7. On defeat: `mcp_foundry_set_combatant_defeated(id)`

## Error Handling

- If an MCP tool call fails, retry once with 2s delay
- If Foundry is unreachable, fall back to narrative-only mode
  (describe the scene, resolve rolls manually)
- Log all Foundry interactions to campaign memory

## Campaign Memory Integration

Foundry is the source of truth for game state. Campaign memory
(TencentDB) is the source of truth for narrative history.

Rule: When there's a conflict between what Foundry says and what
memory says, **Foundry wins** for stats/state. **Memory wins**
for narrative details (NPC relationships, plot threads).
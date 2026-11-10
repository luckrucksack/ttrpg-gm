# Familiar scene/token orchestration — engineering notes 2026-11-06

Status: research notes for the future map phase. Nothing to build now.
Pulled 2026-11-06 from familiarvtt.com (capabilities, guides), foundryvtt.com/packages/familiar,
Foundry Hub listing (v2.26.0), and github.com/Ryanjansen92/familiar-releases.
Purpose: record how the closest commercial product implements on-screen
orchestration, and the design choices where we can do it better.

## What Familiar does on the canvas

- Builds a scene on request: creates/activates the scene, spawns tokens from
  compendiums ("drops the goblin tokens into cover"), positions them.
- Draws walls, doors, trigger regions; sets lighting, darkness, weather
  (particles + sound: rain, thunder).
- Fog of war, drawings, measured templates, tiles: all listed under its canvas
  control domains.
- Binds atmosphere per scene: names a mood → crossfades to a matching playlist
  track, generates a creaking door or thunderclap if the library has none,
  binds it to the scene; "on Automatic, one switch a minute" recues music.
- Map art: generates battle-map backgrounds/portraits through image providers
  (fal.ai can animate a still into a looping clip laid over the scene as a
  moving map); Familiar Studio keeps generated assets in one window.
- Combat-facing (5e-only engine): start combat, roll initiative for everyone,
  damage/conditions/rests/XP from chat; Combat AI reads the battlefield and
  plays a monster's turn (target choice + strategy), Foundry resolves with
  real dice; reactions (Shield/Counterspell) fire on their own.

## How it works (mechanism, per public docs)

- Two surfaces to the same 230 tools / 26 domains: the module's built-in chat
  (BYO API key, ~16 chat providers, incl. OpenRouter/DeepSeek/local
  OpenAI-compatible servers), and an MCP server for external agents
  (Claude Desktop/Codex/Antigravity/Grok Build/Muse) — the Setup Wizard emits
  the config block so your own paid plan drives the table.
- The model only decides intent (what to build, where, which token); Foundry
  executes geometry through its Document APIs (Scene/Token/Wall/AmbientLight/
  WeatherEffect). Everything is a real Foundry document → persistent, saveable,
  undoable by normal Foundry means.
- Rules engine is D&D 5e (2024) ONLY. The seam is explicit: dice/maths live in
  Foundry's engine ("No 'you rolled a 47'"), the AI is stripped of number
  authority. Canvas/voice/journal features run on any system.
- Product posture: "runs a published adventure you imported; never invents the
  story" — same doctrine line as our AGENTS.md.

## Our current state (relevant pins)

- Bridge (vendored foundryvtt-mcp v1.5.3-era): NO create-scene, NO
  create-token, NO wall/light/weather tools. Has journal create, token move,
  status effects, combat start from upstream's June–Sep 2026 write-tool push.
- STATUS "Next" #2: read scene + token data through the bridge even while
  playing theater of the mind. #3: on-screen orchestration = later phase.
- FUTURE.md trigger: "When the map phase begins. The bridge has no
  create-scene or create-token tool. Solve that first (Foundry-side setup, or
  extend the bridge), then wire scene reading into the session start."

## Options when the map phase begins (all surveyed 2026-11-06)

1. **Re-vendor upstream first.** laurigates/foundryvtt-mcp keeps adding write
   tools (move_token, apply_status_effect, create_journal_entry, start_combat
   by v1.5.3, 2026-09-10). Check whether scene/token creation landed upstream
   before writing our own — the vendored-fork pattern already exists.
2. **DroiD16/fvtt-world-cli** (v1.2.0, ~2026-11-03): builds/edits actors,
   journals, scenes, tokens, walls, lights via Document APIs; ships a CLI +
   local daemon + Agent Skill; zero AI included ("bring your own reasoning
   agent"). Strongest off-the-shelf canvas authoring layer; v13+v14 verified.
3. **Nitrmoon Foundry API Bridge** (commercial, hosted MCP, script-sandbox
   execution): capable but hosted + Patreon; conflicts with self-host
   constraint. Skip unless option 2 fails.
4. **Ninjo's Foundry MCP** (v14.2609.6, ~Oct 2026): scene building from a
   disk image/video with auto-measured dimensions — use-case specific, nice
   for pre-made maps.
5. **Foundry Browser MCP**: leans on execute_js; contradicts our verify-don't-
   trust doctrine and prohibitions. Avoid as a base.

## Where we can do it better (design notes, not hype)

- **Composite verbs over raw tool-per-op.** Familiar's 230 tools are mostly
  primitives; a scene build costs the model many calls and lots of schema to
  navigate. We already have a doctrine/skill layer — define HIGH-LEVEL scene
  verbs (scene_from_journal, encounter_setup, atmosphere_set) that expand to
  Foundry operations. Fewer calls, fewer failure modes, and the grammar is
  ours: Delta Green scene grammar (dim light, fog, dossier-driven token spawn,
  no color, horror pacing) lives in the verb, not in the prompt.
- **Verify after every mutation.** Our bridge already has the check.sh gate
  and a read-verified doctrine. Add mandatory read-back-after-write: build a
  scene → re-read scene/token state → assert → report diff to the player.
  Familiar's docs show single-shot execution ("ask for a scene and it builds
  one") with no documented verification pass. This is our real edge: the
  player can see WHAT changed and trust it.
- **Transactional snapshot + rollback verb.** Snapshot scene documents before
  mutation; if verification fails, roll back. Familiar only has step-back on
  the combat tracker, not on canvas ops.
- **System-agnostic by construction.** Both features are canvas-level (any
  system) and we have no rules-engine dependency at all — Foundry's DG system
  plus our roll discipline covers the whole table. We never inherit the
  5e-lock Familiar carries into the game engine.
- **Cost stays zero.** The same tool calls ride free-tier models. Their 230
  tools are a product surface; our 33 are a doctrine surface. If the upstream
  bridge grows 40 more tools, we keep verbs thin and let models route.

## Recommended sequence (when trigger fires, not now)

1. Re-vendor upstream; check for scene/token/wall/light write tools.
2. If absent, adopt/adapt fvtt-world-cli (option 2) as the authoring layer.
3. Build the verb layer in `bot/skills/ttrpg-foundry-bridge.md` (scene_from_
   journal, encounter_setup, atmosphere_set) with the verification + rollback
   rules above.
4. Wire "read scene state into session start" (STATUS Next #2) in the same
   pass. Cost pass after (FUTURE.md pinned item).

Sources: familiarvtt.com/capabilities, familiarvtt.com/guides, foundryvtt.com/packages/familiar,
foundryvtt-hub.com/package/familiar, github.com/Ryanjansen92/familiar-releases,
github.com/laurigates/foundryvtt-mcp, foundryvtt.com/packages/fvtt-world-cli.
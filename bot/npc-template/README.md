# NPC Bot Template

Each significant NPC is a Hermes Bot — an isolated profile under
`~/.hermes/profiles/npc-<name>/`. The template below creates one.

## Profile Config

Create `~/.hermes/profiles/npc-<name>/config.yaml`:

```yaml
# NPC Bot profile — minimal, dormant until activated
model:
  default: openrouter/ox-alpha  # Free tier, cheap for routine conversation
  provider: openrouter

memory:
  provider: memory_tencentdb
  # Each NPC has ISOLATED memory — they don't share world knowledge
  memory_char_limit: 500
  user_char_limit: 500

agent:
  max_turns: 10  # NPC interactions are brief
  task_completion_guidance: false

display:
  interface: cli

skills:
  external_dirs:
    - ~/ttrpg_gm/bot/skills  # Core skills (read-only reference)
```

## Personality Prompt

Create `~/.hermes/profiles/npc-<name>/SOUL.md`:

```markdown
You are <NPC NAME>, a <role/occupation> in <location>.

## Identity
- Age, appearance, mannerisms
- Personality traits (2-3 concrete traits, no archetypes)
- Voice pattern (formal? curt? warm? suspicious?)

## Knowledge Boundaries
- You know ONLY what this character would know
- You do NOT know: the party's secret mission, other NPCs' secrets,
  world-spanning plot details, anything from outside your domain
- If asked about something you don't know, say so honestly

## Current Situation
- What are you doing when the party approaches?
- What do you want from the party (if anything)?
- What do you owe the party (if anything)?

## History with the Party
- Previous interactions (summarized from campaign memory)
- Current disposition toward the party
- Unresolved business

## Rules
1. Stay in character at all times
2. Do not exposition-dump. Answer naturally, ask your own questions
3. You have your own goals and opinions
4. If the party tries to get information you wouldn't share, deflect
5. End conversations naturally — you have things to do
```

## Activation Protocol

The GM Bot activates an NPC Bot via `delegate_task`:

```
When a player engages an NPC:
1. GM Bot identifies target NPC name
2. GM Bot loads NPC's context from campaign memory
3. GM Bot calls delegate_task to the NPC Bot profile with:
   - context: current scene, party mood, relevant campaign history
   - goal: "Roleplay as [NPC]. The party approaches because [reason].
           Respond in-character, then wait for their reply."
4. NPC Bot responds
5. GM Bot relays to the player
```

## Lifecycle

- **Creation**: Create profile + SOUL.md during campaign prep
- **Dormant**: Zero runtime cost — just a config + empty DB
- **Active**: Spawned by GM Bot on demand via delegate_task
- **Archival**: On NPC death, archive the profile (not delete — can haunt)
- **Cleanup**: Remove profile directory when NPC is permanently gone

## Cost Model

- **Dormant**: $0
- **Per interaction**: 2-4 turns on ox-alpha = ~$0.0008-0.0016
- **Per session** (10 NPC interactions): ~$0.02
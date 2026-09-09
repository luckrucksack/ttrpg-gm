# AGENTS.md — rules for any agent working in this repo

Owner-stated standing rules (2026-09-09). These bind every agent and every
session that touches this project.

## Standing rules

1. **Never create sample adventures, demo campaigns, test worlds, or filler
   content.** The owner supplies every adventure, explicitly. If content seems
   to be needed, ask — do not invent it.
2. **No mini rulebooks.** Do not write new prose restating game rules, Foundry
   mechanics, or "style guides." Use the system's own content plus the skills
   that already exist in `bot/skills/`.
3. **No unrequested scaffolding.** No speculative scripts, frameworks,
   directories, or abstractions. Improve what exists; add only what the task
   requires.
4. **Fix duct tape proactively.** Broken, stubbed, misleading, or placeholder
   code, docs, and config found in this repo get fixed in the same pass, and
   the fix gets reported.
5. **No shortcut code.** Modern, efficient, effective. Verify against the real
   runtime (the installed package, the live service) rather than trusting
   READMEs or config comments.

## Verify the Foundry bridge before trusting it

```
bash bridge/check.sh
```

Proves, in order: Foundry answers → the secret exists → credentials authenticate
→ the MCP server registers its tools. Run it after any Foundry, credential, or
config change.

## Boundaries

- Do not create, launch, or delete Foundry worlds.
- Do not modify `~/Library/Application Support/FoundryVTT/Config/` without
  explicit approval (this includes the server admin key).
- Never print secrets. `MCP_FOUNDRY_PASSWORD` lives in the profile `.env`,
  never in `config.yaml` or this repo.

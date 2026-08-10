# integrations/ — external system wiring (TBD)

This layer is where the AI-GM system connects to the outside world. Its
final shape is **undecided** — it will be dictated by what the Foundry VTT
integration needs (see STATUS.md).

Open questions (tracked in docs/backlog.md):
- Ready-made Foundry AI-DM module (Noodlr is the architecturally aligned
  candidate) vs. custom bridge module vs. port of gm_core into Foundry.
- Messaging surface: Discord today (gm_core/agents/discord_bridge.py);
  Foundry chat and/or Hermes channels later.
- Where campaign memory lives long-term (Noodlr memory service, in-browser,
  or the ttrpg TencentDB store).

Nothing here is implemented yet. `foundry/` holds current-state notes.

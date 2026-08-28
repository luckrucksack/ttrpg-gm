# STATUS — ARCHITECTURE REBOOT

**ARCHITECTURE RESOLVED 2026-08-27:** The custom Python AI-GM framework has been retired in favor of **Hermes Bot Mode** as the GM runtime, with Foundry VTT handling all game mechanics. The Python code (40 files, ~5,300 lines) has been deleted from the repo.

See [`docs/ttrpg-gm-architecture-2026-08-27.md`](docs/ttrpg-gm-architecture-2026-08-27.md) for the new architecture.

What this means:
- The old layer boundaries (gm_core / systems / campaigns / integrations) no longer apply
- The repo now holds only docs/ and integrations/reference — no executable code
- The design knowledge (prompt architecture, NPC Bot concept, research) survives in docs/
- The actual build now happens as Hermes skills, profiles, and Foundry bridge configuration

Last restructured: 2026-08-27 (full Python framework removed; architecture reset to doc-only)
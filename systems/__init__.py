"""systems — game-system registry.

Every game system is a self-contained package under systems/<id>/.
The core (gm_core) never imports a system directly; it looks systems up
through this registry by id (env ACTIVE_SYSTEM). See systems/README.md
for the contract.
"""

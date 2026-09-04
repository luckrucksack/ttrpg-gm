"""
pipeline/import_foundry.py — Import plan generator for Foundry VTT.

HONEST SCOPE
------------
This script does NOT connect to Foundry directly, and it does NOT create
documents by itself. Foundry writes happen through the GM Bot's native MCP
client (the `foundryvtt-mcp` stdio server wired into the Hermes ttrpg
profile). That server has no HTTP endpoint and no `create_actor` tool.

What this script actually does:
  1. Validates the pipeline's extracted JSON (actors, journals, items,
     roll_tables).
  2. Emits `manifest.json` — an ordered list of MCP tool calls the GM Bot
     should execute, plus a list of entities that have NO MCP tool and must
     be created manually in Foundry (actors, roll tables).

Usage:
    python -m pipeline.import_foundry plan output/<adventure-name>/ [--dry-run]
    python -m pipeline.import_foundry status

`status` only checks that the Foundry web server responds on :30000. It does
not verify the MCP connection — that happens when the GM Bot loads its MCP
tools (see bridge/README.md).
"""

import json
import sys
from pathlib import Path


# Tools that exist in foundryvtt-mcp 1.5.x (verified against upstream README).
EXISTING_TOOLS = {
    "create_journal_entry",  # GM-only by default; pass "visibility" for players
    "create_actor_item",     # add inline item to an EXISTING actor
}
# Entity types with NO create tool in foundryvtt-mcp (verified upstream):
#   - actors      → no create_actor tool; create in Foundry UI, or fork/extend MCP
#   - roll_tables → no roll-table tool at all; create in Foundry UI


def load_entities(import_dir: Path) -> dict:
    """Load the four entity files; missing files become empty lists."""
    entities = {}
    for name in ("actors", "journals", "items", "roll_tables"):
        f = import_dir / f"{name}.json"
        if f.exists():
            entities[name] = json.loads(f.read_text())
        else:
            entities[name] = []
    return entities


def build_plan(entities: dict) -> dict:
    """Map extracted entities to MCP tool calls the GM Bot can execute."""

    calls = []
    manual = []

    # Journals → create_journal_entry (exists upstream)
    for entry in entities["journals"]:
        calls.append({
            "tool": "create_journal_entry",
            "arguments": {
                "name": entry.get("name", "Journal Entry"),
                "content": entry.get("content", ""),
            },
        })

    # Items → create_actor_item (exists upstream, but requires an existing actor)
    for item in entities["items"]:
        calls.append({
            "tool": "create_actor_item",
            "arguments": {
                "actor_id": "<RESOLVE IN FOUNDRY — actor must exist first>",
                "name": item.get("name", "Item"),
                "type": item.get("type", "weapon"),
            },
        })

    # Actors → NO create tool upstream; manual or upstream extension
    for actor in entities["actors"]:
        manual.append({
            "entity": "actor",
            "name": actor.get("name", "Unnamed"),
            "why": "foundryvtt-mcp has no create_actor tool — create in Foundry UI, "
                   "or fork the MCP server to add one",
        })

    # Roll tables → NO tool upstream; manual
    for table in entities["roll_tables"]:
        manual.append({
            "entity": "roll_table",
            "name": table.get("name", "Unnamed Table"),
            "why": "foundryvtt-mcp has no roll-table tool — create in Foundry UI",
        })

    return {
        "generated_for": "GM Bot (Hermes ttrpg profile, native MCP client)",
        "mcp_calls": calls,
        "manual_only": manual,
    }


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    command = args[0]

    if command == "status":
        from urllib import request
        try:
            req = request.Request("http://localhost:30000", method="GET")
            with request.urlopen(req, timeout=10) as resp:
                print(f"Foundry web server: responding (HTTP {resp.status})")
        except Exception as e:
            print(f"Foundry web server: NOT responding ({e})")
            print("This is NOT an MCP check. MCP connectivity is verified when the")
            print("GM Bot loads its tools — see bridge/README.md.")
        sys.exit(0)

    if command == "plan":
        if len(args) < 2:
            print("Usage: python -m pipeline.import_foundry plan output/<name>/ [--dry-run]",
                  file=sys.stderr)
            sys.exit(1)
        import_dir = Path(args[1])
        if not import_dir.is_dir():
            print(f"Not a directory: {import_dir}", file=sys.stderr)
            sys.exit(1)

        entities = load_entities(import_dir)
        plan = build_plan(entities)

        for name in ("actors", "journals", "items", "roll_tables"):
            print(f"  loaded {len(entities[name])} {name}")

        if len(args) > 2 and args[2] == "--dry-run":
            print("\nMCP calls the GM Bot would execute:")
            for call in plan["mcp_calls"]:
                print(f"  → {call['tool']} {call['arguments'].get('name', '')!r}")
            print("\nManual-only entities (no MCP tool available):")
            for entry in plan["manual_only"]:
                print(f"  → {entry['entity']}: {entry['name']!r} — {entry['why']}")
            print("\nNo files written (--dry-run).")
            sys.exit(0)

        out = import_dir / "manifest.json"
        with open(out, "w") as f:
            json.dump(plan, f, indent=2)
        print(f"\nWrote {out}")
        print(f"  {len(plan['mcp_calls'])} MCP calls for the GM Bot to execute")
        print(f"  {len(plan['manual_only'])} entities to create manually in Foundry")
        print("\nNext: give the GM Bot this manifest; it executes mcp_foundry_* calls.")
        sys.exit(0)

    print(f"Unknown command: {command}", file=sys.stderr)
    print(__doc__, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
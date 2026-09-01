"""
pipeline/import_foundry.py — Import extracted adventure data into Foundry VTT.

Connects to Foundry via the MCP server (laurigates/foundryvtt-mcp)
and creates actors, journals, items, and roll tables from the
pipeline's JSON output.

Usage:
    python -m pipeline.import_foundry import output/<adventure-name>/
    python -m pipeline.import_foundry status   # check MCP server health
"""

import json
import sys
import os
from pathlib import Path
from urllib import request, error


MCP_TOOL_URL = os.environ.get("FOUNDRY_MCP_URL", "http://localhost:30000")


def mcp_call(tool: str, args: dict = None) -> dict:
    """Call an MCP tool on Foundry via HTTP (MCP JSON-RPC)."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": args or {}},
    }
    req = request.Request(
        MCP_TOOL_URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except error.URLError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": f"JSON decode: {e}"}


def import_actors(actors: list, dry_run: bool = False):
    """Import actors into Foundry via MCP create_actor."""
    imported = 0
    for actor in actors:
        name = actor.get("name", "Unnamed")
        if dry_run:
            print(f"  [dry] actor: {name}")
            continue
        # The MCP server exposes create_actor — call it
        result = mcp_call("create_actor", {
            "name": name,
            "type": actor.get("type", "npc"),
            "system": actor.get("stats", {}),
        })
        if "error" in result:
            print(f"  ✗ actor: {name} — {result['error']}")
        else:
            imported += 1
    return imported


def import_journals(journals: list, dry_run: bool = False):
    """Import journals into Foundry via MCP create_journal_entry."""
    imported = 0
    for entry in journals:
        name = entry.get("name", "Journal Entry")
        if dry_run:
            print(f"  [dry] journal: {name}")
            continue
        # MCP tool: create_journal_entry
        result = mcp_call("create_journal_entry", {
            "name": name,
            "content": entry.get("content", ""),
        })
        if "error" in result:
            print(f"  ✗ journal: {name} — {result['error']}")
        else:
            imported += 1
    return imported


def import_items(items: list, dry_run: bool = False):
    """Import items into Foundry via MCP create_actor_item."""
    imported = 0
    for item in items:
        name = item.get("name", "Item")
        if dry_run:
            print(f"  [dry] item: {name}")
            continue
        result = mcp_call("create_actor_item", {
            "name": name,
            "type": item.get("type", "weapon"),
            "system": item.get("stats", {}),
        })
        if "error" in result:
            print(f"  ✗ item: {name} — {result['error']}")
        else:
            imported += 1
    return imported


def check_status() -> dict:
    """Check MCP server health."""
    # Try to list actors as a connectivity check
    result = mcp_call("search_actors", {"query": ""})
    return {
        "status": "ok" if "error" not in result else "error",
        "detail": result,
    }


# ── CLI ────────────────────────────────────────────────────────────────

def cmd_import():
    import_dir = sys.argv[2]
    p = Path(import_dir)
    if not p.is_dir():
        print(f"Not a directory: {import_dir}", file=sys.stderr)
        sys.exit(1)

    dry_run = "--dry-run" in sys.argv
    label = "DRY RUN" if dry_run else "IMPORT"

    # Load extracted data
    entities = {}
    for name in ("actors", "journals", "items", "roll_tables"):
        f = p / f"{name}.json"
        if f.exists():
            with open(f) as fp:
                entities[name] = json.load(fp)
            print(f"  loaded {len(entities[name])} {name}")
        else:
            entities[name] = []

    print(f"\n{label} to Foundry VTT via MCP...")

    counts = {}
    if entities["actors"]:
        counts["actors"] = import_actors(entities["actors"], dry_run)

    if entities["journals"]:
        counts["journals"] = import_journals(entities["journals"], dry_run)

    if entities["items"]:
        counts["items"] = import_items(entities["items"], dry_run)

    if entities["roll_tables"]:
        print("  [note] roll_tables import needs MCP extend — manual via Foundry UI for now")

    if not dry_run:
        print(f"\nImported: {json.dumps(counts)}")
    else:
        print("\nDry run complete. Run without --dry-run to import.")


def cmd_status():
    result = check_status()
    if result["status"] == "ok":
        print("MCP server: connected ✓")
    else:
        print(f"MCP server: {result}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    if command == "import":
        cmd_import()
    elif command == "status":
        cmd_status()
    elif command == "--help":
        print(__doc__)
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
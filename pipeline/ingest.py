"""
pipeline/ingest.py — PDF adventure ingestion pipeline.

Takes a PDF adventure module, converts to markdown via MarkItDown,
then uses an LLM to extract structured Foundry data.

Usage:
    python -m pipeline.ingest path/to/adventure.pdf

Output:
    ./output/<adventure-name>/  — extracted JSON per Foundry entity type
      actors.json      — NPCs, monsters
      journals.json    — adventure text, room descriptions
      items.json       — magic items, equipment
      roll_tables.json — encounter/loot tables
      metadata.json    — adventure metadata
"""

import os
import json
import sys
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────
OUTPUT_BASE = Path(__file__).resolve().parent / "output"
EXTRACTION_PROVIDER = "openrouter"       # Models: deepseek-v4-flash etc.
EXTRACTION_MODEL = "deepseek/deepseek-v4-flash"
MAX_PDF_PAGES_CHUNK = 20  # Process in chunks to avoid context overflow

# ── Stage 1: MarkItDown ────────────────────────────────────────────────

def markitdown_convert(pdf_path: str) -> str:
    """Convert PDF to markdown text via MarkItDown with OCR."""
    from markitdown import MarkItDown
    md = MarkItDown(enable_plugins=True)
    result = md.convert(pdf_path)
    return result.text_content


# ── Stage 2: LLM Extraction ─────────────────────────────────────────────

EXTRACT_SYSTEM_PROMPT = """You are an expert TTRPG adventure parser. Your task is to extract structured data from an adventure module's text and produce valid JSON.

Extract the following entity types from the adventure text:

1. **actors** — Every named NPC, monster, or significant creature. Include:
   - name, type (npc/monster), system-specific stats (as a JSON object)
   - description, personality traits, appearance
   - challenge rating / level if present
   - source location (which scene/chapter they're found in)

2. **journals** — Adventure text broken into logical sections. Each journal entry represents a chapter, scene, or room description. Include:
   - name (section title)
   - content (full description text, formatted as markdown)
   - folder (chapter/area grouping)
   - sort order

3. **items** — Magic items, equipment, weapons, armor, potions, scrolls. Include:
   - name, type, description, system-specific stats (JSON)
   - source location

4. **roll_tables** — Encounter tables, loot tables, random events. Include:
   - name, description, table entries (weight, text, min/max range)
   - dice formula (e.g. "1d12")

Output format:
{
  "adventure_name": "...",
  "system": "dnd5e" | "pf2e" | "dcc" | "generic",
  "actors": [...],
  "journals": [...],
  "items": [...],
  "roll_tables": [...]
}

Rules:
- Do NOT invent content. If the text doesn't contain statblocks, leave stats as an empty object, not fabricated values.
- Extract statblocks PRESERVING original numbers. Do not normalize, convert, or adjust.
- For journals, preserve the original prose. Do not rewrite or summarize.
- If a section has maps, note "has_map: true" in the journal entry.
- If a statblock references a specific game system, set system accordingly.
- Be thorough. Every named entity should appear.
"""

def llm_extract(markdown_text: str, adventure_name: str) -> dict:
    """Send markdown text to LLM and get structured JSON back."""
    from openai import OpenAI
    import os as _os

    api_key = _os.environ.get("OPENROUTER_API_KEY") or _os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("No API key found — set OPENROUTER_API_KEY or OPENAI_API_KEY")

    # Route to the provider matching the key that was actually set.
    if _os.environ.get("OPENROUTER_API_KEY"):
        base_url = "https://openrouter.ai/api/v1"
    else:
        base_url = "https://api.openai.com/v1"

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    # Chunk if too big
    # A conservative token budget: ~3000 chars per 1000 tokens
    char_limit = 60000  # ~20K tokens, safe for most models
    if len(markdown_text) > char_limit:
        # Simple truncation with note
        markdown_text = (
            markdown_text[:char_limit]
            + f"\n\n[... {len(markdown_text) - char_limit} more characters truncated — "
            f"run with smaller chunk or increase MAX_PDF_PAGES_CHUNK]"
        )

    resp = client.chat.completions.create(
        model=EXTRACTION_MODEL,
        messages=[
            {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract adventure data from:\n\n{markdown_text}"},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    content = resp.choices[0].message.content
    # The response_format=json_object guarantees valid JSON
    data = json.loads(content)
    data["_source_file"] = adventure_name
    return data


# ── Stage 3: Write Output Files ─────────────────────────────────────────

def write_output(data: dict, output_dir: Path):
    """Write each entity collection to its own JSON file."""
    output_dir.mkdir(parents=True, exist_ok=True)

    collections = {
        "actors": data.get("actors", []),
        "journals": data.get("journals", []),
        "items": data.get("items", []),
        "roll_tables": data.get("roll_tables", []),
    }

    for name, entries in collections.items():
        if entries:
            path = output_dir / f"{name}.json"
            with open(path, "w") as f:
                json.dump(entries, f, indent=2)
            print(f"  wrote {len(entries)} {name} → {path}")

    # Metadata
    meta = {
        "adventure_name": data.get("adventure_name", "unknown"),
        "system": data.get("system", "generic"),
        "extracted_at": __import__("datetime").datetime.now().isoformat(),
        "source_file": data.get("_source_file", ""),
        "counts": {k: len(collections[k]) for k in collections},
    }
    meta_path = output_dir / "metadata.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  wrote metadata → {meta_path}")


# ── CLI Entry Point ─────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m pipeline.ingest path/to/adventure.pdf", file=sys.stderr)
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    name = Path(pdf_path).stem.replace(" ", "-").lower()
    output_dir = OUTPUT_BASE / name
    print(f"Ingesting: {pdf_path}")
    print(f"Output:    {output_dir}")
    print()

    # Stage 1: MarkItDown
    print("[1/3] Converting PDF to markdown via MarkItDown...")
    markdown_text = markitdown_convert(pdf_path)
    print(f"  extracted {len(markdown_text):,} chars of text")

    # Save raw markdown for inspection
    raw_path = output_dir / "raw.md"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(raw_path, "w") as f:
        f.write(markdown_text)
    print(f"  raw text → {raw_path}")

    # Stage 2: LLM extraction
    print(f"[2/3] Extracting structured data via {EXTRACTION_MODEL}...")
    data = llm_extract(markdown_text, name)
    print(f"  found: {len(data.get('actors', []))} actors, "
          f"{len(data.get('journals', []))} journal entries, "
          f"{len(data.get('items', []))} items, "
          f"{len(data.get('roll_tables', []))} roll tables")

    # Stage 3: Write output
    print("[3/3] Writing output files...")
    write_output(data, output_dir)

    print(f"\nDone. Import into Foundry with:")
    print(f"  python -m pipeline.import_foundry import {output_dir}")


if __name__ == "__main__":
    main()
"""Dungeon Crawl Classics (DCC) — game-system module.

DCC calls its GM the *Judge*. This package contains everything DCC-specific:
the Judge runtime, DCC state manager (spellburn, corruption, mercurial magic,
luck, dice chain), the DCC dice (d3, d5, d7, d14, d16, d24, d30), rules docs,
and tests. Nothing here is imported by gm_core directly — gm_core only calls
rules_text() via the systems registry.
"""

SYSTEM_ID = "dcc"


def rules_text() -> str:
    """Return the DCC rules reference used to prime the LLM context."""
    from pathlib import Path
    p = Path(__file__).resolve().parent / "docs" / "DCC_QUICK_REFERENCE.md"
    try:
        return p.read_text()
    except FileNotFoundError:
        return ""

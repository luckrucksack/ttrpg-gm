"""Dungeons & Dragons 5e — game-system module (rules reference only).

Kept as the reference implementation of the systems contract: a rules
module with zero runtime code. The rules text was extracted verbatim from
the original core config so the core itself stays system-agnostic.
"""

SYSTEM_ID = "dnd5e"


def rules_text() -> str:
    from pathlib import Path
    p = Path(__file__).resolve().parent / "rules.md"
    try:
        return p.read_text()
    except FileNotFoundError:
        return ""

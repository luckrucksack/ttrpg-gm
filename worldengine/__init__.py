"""Offscreen world engine: deterministic bookkeeping for hidden parallel timelines.

The LLM authors events; this package decides when they fire, who owes the table
a pay-back, and which actors have gone quiet.
"""

from .clock import Clock, format_iso, parse_duration, parse_iso
from .store import ACTOR_STATES, SCHEMA_VERSION, Store, StoreError

__all__ = [
    "ACTOR_STATES",
    "SCHEMA_VERSION",
    "Clock",
    "Store",
    "StoreError",
    "format_iso",
    "parse_duration",
    "parse_iso",
]

"""The seam between this engine and any virtual tabletop.

The engine never imports a VTT. It emits intents, and a backend carries them
out. Foundry, Roll20, a paper notebook and a Discord channel are all backends;
so is a recorder used in tests.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, Any


@dataclass(frozen=True)
class Intent:
    """A request to the table, in table-neutral terms."""
    kind: str                      # activate_scene | place_token | move_token |
                                   # push_handout | roll | write_stat | log
    payload: dict[str, Any] = field(default_factory=dict)


class Backend(Protocol):
    def apply(self, intent: Intent) -> Any: ...


class Recorder:
    """A backend that only remembers. Used by tests and by offline prep."""

    def __init__(self) -> None:
        self.intents: list[Intent] = []

    def apply(self, intent: Intent) -> None:
        self.intents.append(intent)

    def __len__(self) -> int:
        return len(self.intents)


class Table:
    """Thin facade: the only object the runtime touches."""

    def __init__(self, backend: Backend) -> None:
        self.backend = backend

    # --- scene and tokens ------------------------------------------------
    def activate_scene(self, scene: str) -> None:
        self.backend.apply(Intent("activate_scene", {"scene": scene}))

    def place_token(self, actor: str, at: str | None = None) -> None:
        self.backend.apply(Intent("place_token", {"actor": actor, "at": at}))

    def move_token(self, actor: str, at: Any) -> None:
        self.backend.apply(Intent("move_token", {"actor": actor, "at": at}))

    # --- information ------------------------------------------------------
    def push_handout(self, handout: str) -> None:
        self.backend.apply(Intent("push_handout", {"handout": handout}))

    # --- mechanics --------------------------------------------------------
    def roll(self, formula: str, reason: str = "") -> None:
        self.backend.apply(Intent("roll", {"formula": formula, "reason": reason}))

    def write_stat(self, actor: str, path: str, value: Any) -> None:
        self.backend.apply(Intent("write_stat", {"actor": actor, "path": path, "value": value}))

"""Data model. Declarative, immutable, no behaviour beyond loading."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import yaml


@dataclass(frozen=True)
class Clue:
    """One route by which the players can reach a node or a conclusion."""
    id: str
    text: str
    leads_to: str
    source: str = "printed"          # printed | improvised | prepared
    anchor: str | None = None        # required when source == "improvised"
    found_at: str | None = None      # node id where it can be found


@dataclass(frozen=True)
class Node:
    """A place, scene, or situation the players can enter."""
    id: str
    title: str
    summary: str = ""
    entry: bool = False              # a starting point, needs no inbound clue
    requires: tuple[str, ...] = ()   # facts that must hold to enter
    yields: tuple[str, ...] = ()     # facts learned on entry
    scene: str | None = None         # Foundry scene name
    printed: str | None = None       # module page to read before running


@dataclass(frozen=True)
class Conclusion:
    """Something the players must be able to work out."""
    id: str
    statement: str
    clues: tuple[str, ...] = ()      # clue ids pointing at it


@dataclass(frozen=True)
class Tick:
    """A scheduled offscreen event. System-agnostic: day, actor, event."""
    id: str
    day: int
    actor: str
    event: str
    affects: tuple[str, ...] = ()


@dataclass(frozen=True)
class Actor:
    id: str
    name: str
    source: str = "printed"
    anchor: str | None = None        # improvised people attach to something printed
    note: str = ""


@dataclass(frozen=True)
class Improv:
    """Bridge material invented when play left the text."""
    id: str
    anchor: str                      # node/clue/conclusion/actor it attaches to
    why: str                         # what player choice forced it
    text: str


@dataclass(frozen=True)
class Scenario:
    id: str
    title: str
    system: str = "agnostic"
    nodes: tuple[Node, ...] = ()
    clues: tuple[Clue, ...] = ()
    conclusions: tuple[Conclusion, ...] = ()
    ticks: tuple[Tick, ...] = ()
    actors: tuple[Actor, ...] = ()
    improv: tuple[Improv, ...] = ()

    # ---- lookups -------------------------------------------------------
    def node(self, nid: str) -> Node | None:
        return next((n for n in self.nodes if n.id == nid), None)

    def ids(self) -> set[str]:
        return ({n.id for n in self.nodes} | {c.id for c in self.clues}
                | {c.id for c in self.conclusions} | {a.id for a in self.actors})

    def clues_pointing_at(self, target: str) -> tuple[Clue, ...]:
        return tuple(c for c in self.clues if c.leads_to == target)

    def entry_nodes(self) -> tuple[Node, ...]:
        return tuple(n for n in self.nodes if n.entry)


def _t(cls, raw: dict[str, Any]):
    """Build a frozen dataclass from a mapping, ignoring unknown keys loudly."""
    allowed = {f for f in cls.__dataclass_fields__}
    unknown = set(raw) - allowed
    if unknown:
        raise ValueError(f"{cls.__name__}: unknown keys {sorted(unknown)}")
    kw = {}
    for k, v in raw.items():
        if isinstance(v, list):
            v = tuple(v)
        kw[k] = v
    return cls(**kw)


def load(path: str) -> Scenario:
    with open(path) as fh:
        raw = yaml.safe_load(fh)
    return Scenario(
        id=raw["id"],
        title=raw["title"],
        system=raw.get("system", "agnostic"),
        nodes=tuple(_t(Node, n) for n in raw.get("nodes", [])),
        clues=tuple(_t(Clue, c) for c in raw.get("clues", [])),
        conclusions=tuple(_t(Conclusion, c) for c in raw.get("conclusions", [])),
        ticks=tuple(_t(Tick, t) for t in raw.get("ticks", [])),
        actors=tuple(_t(Actor, a) for a in raw.get("actors", [])),
        improv=tuple(_t(Improv, i) for i in raw.get("improv", [])),
    )

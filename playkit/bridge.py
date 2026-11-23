"""Making improvisation first-class, so it can be audited and reused.

The GM invents when player choice leaves the text. That invention is legal,
but it is not free-floating: every piece attaches to canon, and the attachment
is recorded so the next session knows what the module said and what we made up.
"""
from __future__ import annotations
from dataclasses import replace
from .model import Scenario, Clue, Actor, Improv


class Unanchored(Exception):
    pass


def _require(scn: Scenario, anchor: str) -> None:
    if anchor not in scn.ids():
        raise Unanchored(f"{anchor!r} is not a declared part of this scenario")


def clue(scn: Scenario, *, id: str, text: str, leads_to: str, anchor: str,
         found_at: str | None = None) -> Scenario:
    """Add an invented route to something the module already contains."""
    _require(scn, anchor)
    _require(scn, leads_to)
    return replace(scn, clues=scn.clues + (Clue(
        id=id, text=text, leads_to=leads_to, source="improvised",
        anchor=anchor, found_at=found_at),))


def actor(scn: Scenario, *, id: str, name: str, anchor: str, note: str = "") -> Scenario:
    """Add a person the module did not name, tied to someone or something it did."""
    _require(scn, anchor)
    return replace(scn, actors=scn.actors + (Actor(
        id=id, name=name, source="improvised", anchor=anchor, note=note),))


def scene(scn: Scenario, *, id: str, anchor: str, why: str, text: str) -> Scenario:
    """Record a bridge scene: what forced it, what it attaches to, what happened."""
    _require(scn, anchor)
    return replace(scn, improv=scn.improv + (Improv(
        id=id, anchor=anchor, why=why, text=text),))


def audit(scn: Scenario) -> list[str]:
    """Everything invented, with its tether. Empty means play has stayed in the text."""
    out = []
    for c in scn.clues:
        if c.source == "improvised":
            out.append(f"clue {c.id} -> {c.anchor} ({c.leads_to})")
    for a in scn.actors:
        if a.source == "improvised":
            out.append(f"actor {a.id} -> {a.anchor}")
    for i in scn.improv:
        out.append(f"scene {i.id} -> {i.anchor}: {i.why}")
    return out

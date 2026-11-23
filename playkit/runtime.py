"""Queries against scenario + state. Pure functions; no I/O.

The interesting one is thin_conclusions(): the list of things the players must
be able to work out that currently have fewer than three live routes. That list
is the GM's invention brief, and every item on it names what the new material
attaches to.
"""
from __future__ import annotations
from .model import Scenario
from .state import State


def available(scn: Scenario, st: State) -> list:
    """Nodes the players can enter right now."""
    out = []
    for n in scn.nodes:
        if n.id in st.resolved:
            continue
        if all(req in st.facts for req in n.requires):
            out.append(n)
    return out


def live_clues(scn: Scenario, st: State, target: str) -> list:
    """Clues pointing at target that have not been burned."""
    live = []
    for c in scn.clues:
        if c.leads_to != target or c.id in st.resolved:
            continue
        if c.found_at is None or c.found_at in st.visited:
            live.append(c)
    return live


def thin_conclusions(scn: Scenario, st: State, minimum: int = 3) -> list[dict]:
    """Conclusions with too few live routes, with the material to anchor new ones."""
    thin = []
    for con in scn.conclusions:
        live = live_clues(scn, st, con.id)
        if len(live) < minimum:
            anchors = sorted({c.found_at for c in scn.clues if c.found_at} & st.visited)
            routes_at = sorted({c.found_at for c in scn.clues
                                if c.leads_to == con.id and c.found_at})
            thin.append({
                "conclusion": con.id,
                "statement": con.statement,
                "live": len(live),
                "need": minimum - len(live),
                "anchors": anchors,
                "routes_at": routes_at,
            })
    return thin


def due_ticks(scn: Scenario, st: State) -> list:
    """Scheduled events that have come due and not been logged."""
    return [t for t in scn.ticks if t.day <= st.day and t.id not in st.resolved]


def brief(scn: Scenario, st: State) -> str:
    av = available(scn, st)
    lines = [f"{scn.title} — day {st.day}, {st.clock}"]
    lines.append("open nodes: " + (", ".join(n.id for n in av) or "none"))
    dues = due_ticks(scn, st)
    if dues:
        lines.append("due now: " + ", ".join(f"{t.id} ({t.actor})" for t in dues))
    thin = thin_conclusions(scn, st)
    if thin:
        lines.append("thin conclusions:")
        for t in thin:
            where = ", ".join(t["routes_at"]) or "nowhere yet"
            lines.append(f"  - {t['conclusion']} ({t['live']} live, needs {t['need']} more); "
                         f"routes are at: {where}; anchor new material to: "
                         + (", ".join(t["anchors"]) or "any visited node"))
    return "\n".join(lines)

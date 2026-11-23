"""Static checks on a scenario declaration.

The linter encodes the standing rules: the three-clue rule, no dangling
references, no orphans, no unanchored improvisation. It is the thing that
catches a thin investigation before the table does.
"""
from __future__ import annotations
from dataclasses import dataclass
from .model import Scenario

ERROR, WARN = "error", "warn"


@dataclass(frozen=True)
class Issue:
    code: str
    where: str
    message: str
    severity: str = ERROR

    def __str__(self) -> str:
        return f"[{self.severity}] {self.code} {self.where}: {self.message}"


def lint(scn: Scenario) -> list[Issue]:
    issues: list[Issue] = []
    known = scn.ids()

    # 1. Dangling references anywhere.
    for c in scn.clues:
        if c.leads_to not in known:
            issues.append(Issue("DANGLING_CLUE", c.id, f"leads_to unknown target {c.leads_to!r}"))
        if c.found_at and scn.node(c.found_at) is None:
            issues.append(Issue("DANGLING_CLUE", c.id, f"found_at unknown node {c.found_at!r}"))
        if c.source == "improvised" and not c.anchor:
            issues.append(Issue("UNANCHORED", c.id, "improvised clue names no anchor to printed material"))
        if c.anchor and c.anchor not in known:
            issues.append(Issue("DANGLING_ANCHOR", c.id, f"anchor {c.anchor!r} does not exist"))

    for t in scn.ticks:
        if t.actor not in {a.id for a in scn.actors}:
            issues.append(Issue("CLOCK_UNKNOWN_ACTOR", t.id, f"actor {t.actor!r} is not declared"))
        for a in t.affects:
            if a not in known:
                issues.append(Issue("DANGLING_TICK", t.id, f"affects unknown {a!r}"))

    for i in scn.improv:
        if i.anchor not in known:
            issues.append(Issue("IMPROV_UNANCHORED", i.id, f"anchor {i.anchor!r} does not exist"))
    for a in scn.actors:
        if a.source == "improvised" and a.anchor not in known:
            issues.append(Issue("IMPROV_UNANCHORED", a.id, "improvised actor names no printed anchor"))

    # 2. The three-clue rule, per conclusion.
    for con in scn.conclusions:
        if len(con.clues) < 3:
            issues.append(Issue("THREE_CLUE", con.id,
                                f"{len(con.clues)} clue(s); the rule asks for 3"))
        for cid in con.clues:
            if cid not in known:
                issues.append(Issue("DANGLING_CLUE", con.id, f"cites unknown clue {cid!r}"))

    # 3. Orphans and reachability.
    inbound = {c.leads_to for c in scn.clues}
    for n in scn.nodes:
        if not n.entry and n.id not in inbound:
            issues.append(Issue("ORPHAN_NODE", n.id, "no clue leads here and it is not an entry point"))
    reachable = _reachable(scn)
    for n in scn.nodes:
        if n.id not in reachable:
            issues.append(Issue("UNREACHABLE", n.id, "cannot be reached from any entry point"))

    # 4. Hints with nothing to find.
    for n in scn.nodes:
        if not n.yields and not n.entry:
            issues.append(Issue("DEAD_NODE", n.id, "yields no facts and opens nothing", WARN))

    return sorted(issues, key=lambda i: (i.severity != ERROR, i.code, i.where))


def _reachable(scn: Scenario) -> set[str]:
    seen: set[str] = set()
    frontier = [n.id for n in scn.entry_nodes()]
    while frontier:
        cur = frontier.pop()
        if cur in seen:
            continue
        seen.add(cur)
        for c in scn.clues:
            if c.found_at == cur or c.found_at is None:
                if c.leads_to not in seen and scn.node(c.leads_to):
                    frontier.append(c.leads_to)
    return seen

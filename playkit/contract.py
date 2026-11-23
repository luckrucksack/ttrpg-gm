"""The contract: what fidelity means, and where flexibility lives.

Fidelity and flexibility pull against each other, so the system states them
separately and refuses to blur them.

Fidelity invariants are non-negotiable. Any violation is a defect in the
declaration, not a judgement call at the table.

Flexibility is a declared surface, not a loophole. Invented material is legal
provided it (a) names the canon it attaches to, and (b) is marked as invented,
so that a later session can tell the module from the bridge.
"""
from __future__ import annotations
from dataclasses import dataclass
from .model import Scenario
from .state import State
from .lint import lint, Issue

FIDELITY, FLEXIBILITY = "fidelity", "flexibility"


@dataclass(frozen=True)
class Invariant:
    id: str
    kind: str
    rule: str
    codes: tuple[str, ...] = ()


INVARIANTS: tuple[Invariant, ...] = (
    Invariant("F1", FIDELITY, "every declaration resolves to something real",
              ("DANGLING_CLUE", "DANGLING_ANCHOR", "DANGLING_TICK")),
    Invariant("F2", FIDELITY, "every truth is reachable by three routes", ("THREE_CLUE",)),
    Invariant("F3", FIDELITY, "no node is stranded", ("ORPHAN_NODE", "UNREACHABLE")),
    Invariant("F4", FIDELITY, "the clock names actors that exist", ("CLOCK_UNKNOWN_ACTOR",)),
    Invariant("F5", FIDELITY, "invented material names its anchor", ("IMPROV_UNANCHORED", "UNANCHORED")),
)

_by_code = {code: inv for inv in INVARIANTS for code in inv.codes}


@dataclass(frozen=True)
class Report:
    violations: tuple[Issue, ...]
    warnings: tuple[Issue, ...]
    invented: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.violations

    def invariant_for(self, issue: Issue) -> str:
        inv = _by_code.get(issue.code)
        return inv.id if inv else "?"


def report(scn: Scenario, st: State | None = None) -> Report:
    issues = lint(scn)
    viol = tuple(i for i in issues if i.severity == "error")
    warn = tuple(i for i in issues if i.severity != "error")
    invented = tuple(sorted(
        [f"clue:{c.id}" for c in scn.clues if c.source == "improvised"]
        + [f"actor:{a.id}" for a in scn.actors if a.source == "improvised"]
        + [f"improv:{i.id}" for i in scn.improv]
    ))
    return Report(viol, warn, invented)


DRIFT_RATIO_ALARM = 1.0   # invented material outweighing printed material


def drift(scn: Scenario, st: State | None = None) -> dict:
    """The paraphrase alarm.

    Provenance counts alone are a smoke alarm, not a verdict: a campaign can
    carry a lot of invented scaffolding and still be faithful, because the
    spine is printed and the scaffolding sits between its joints. So this
    combines four signals and reports them together.

      printed       things the module contains
      invented      bridge material, all of it tethered
      ratio         invented routes per printed route
      coverage      share of printed nodes the player has actually entered
      bypassed      printed nodes reachable but not visited, once their
                    neighbours have been seen (the text quietly skipped)
    """
    printed_nodes = [n for n in scn.nodes]
    printed_clues = [c for c in scn.clues if c.source == "printed"]
    inv_clues = [c for c in scn.clues if c.source != "printed"]
    ratio = (len(inv_clues) / len(printed_clues)) if printed_clues else 0.0
    out = {
        "printed_clues": len(printed_clues),
        "invented_clues": len(inv_clues),
        "invented_actors": sum(1 for a in scn.actors if a.source != "printed"),
        "bridge_scenes": len(scn.improv),
        "ratio": round(ratio, 3),
    }
    if st is not None:
        visited_printed = [n.id for n in printed_nodes if n.id in st.visited]
        out["coverage"] = round(len(visited_printed) / len(printed_nodes), 3) if printed_nodes else 0.0
        neighbours_seen = {n.id for n in printed_nodes
                           if n.id in st.visited or n.id in st.resolved}
        bypassed = []
        for n in printed_nodes:
            if n.id in st.visited or n.id in st.resolved:
                continue
            inbound = [c for c in scn.clues
                       if c.leads_to == n.id and (c.found_at is None or c.found_at in neighbours_seen)]
            if inbound:
                bypassed.append(n.id)
        out["bypassed"] = bypassed
    out["alarm"] = ratio > DRIFT_RATIO_ALARM or bool(out.get("bypassed"))
    return out


def flexibility_used(scn: Scenario) -> dict[str, int]:
    """How much bridge material a campaign is carrying, by kind."""
    return {
        "improvised_clues": sum(1 for c in scn.clues if c.source == "improvised"),
        "improvised_actors": sum(1 for a in scn.actors if a.source == "improvised"),
        "bridge_scenes": len(scn.improv),
        "printed_clues": sum(1 for c in scn.clues if c.source == "printed"),
    }

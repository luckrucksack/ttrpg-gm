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


def flexibility_used(scn: Scenario) -> dict[str, int]:
    """How much bridge material a campaign is carrying, by kind."""
    return {
        "improvised_clues": sum(1 for c in scn.clues if c.source == "improvised"),
        "improvised_actors": sum(1 for a in scn.actors if a.source == "improvised"),
        "bridge_scenes": len(scn.improv),
        "printed_clues": sum(1 for c in scn.clues if c.source == "printed"),
    }

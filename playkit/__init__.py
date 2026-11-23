"""playkit: a system-agnostic runtime for running published adventures.

Two premises:

1. The written scenario is canonical. Its nodes, clues, clocks and cast are
   facts, and play follows them wherever play can.
2. Players leave the text. When they do, the GM invents. Invented material
   enters the record as a first-class object that must name what it attaches
   to, so improvisation stays tethered to the published adventure instead of
   drifting away from it.

Nothing here knows what a d20 is. See docs/playkit-architecture.md.
"""

from .model import Scenario, Node, Clue, Tick, Actor, Improv, Conclusion, load
from .lint import lint, Issue
from .state import State
from .contract import report, flexibility_used, drift, INVARIANTS, Report
from .backend import Intent, Backend, Recorder, Table
from . import runtime, bridge

__all__ = ["Scenario", "Node", "Clue", "Tick", "Actor", "Improv", "Conclusion",
           "load", "lint", "Issue", "State", "report", "flexibility_used", "drift",
           "INVARIANTS", "Report", "Intent", "Backend", "Recorder", "Table",
           "runtime", "bridge"]

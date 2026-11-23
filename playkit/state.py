"""Mutable play state: what has happened, in a file that survives the session."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
import json, os, time


@dataclass
class State:
    scenario: str = ""
    day: int = 1
    clock: str = "15:00"          # in-world 24h time
    date: str = ""                 # mm.dd.yy
    facts: set[str] = field(default_factory=set)
    visited: set[str] = field(default_factory=set)
    resolved: set[str] = field(default_factory=set)
    log: list[str] = field(default_factory=list)

    # ---- mutation ------------------------------------------------------
    def learn(self, *facts: str) -> None:
        for f in facts:
            self.facts.add(f)
            self.log.append(f"day {self.day} {self.clock}: learned {f}")

    def visit(self, node: str, at: str | None = None) -> None:
        if at:
            self.clock = at
        self.visited.add(node)
        self.log.append(f"day {self.day} {self.clock}: visited {node}")

    def resolve(self, node: str) -> None:
        self.resolved.add(node)
        self.log.append(f"day {self.day} {self.clock}: resolved {node}")

    def advance(self, days: int = 1) -> None:
        self.day += days
        self.log.append(f"day advanced to {self.day}")

    # ---- persistence ---------------------------------------------------
    def save(self, path: str) -> None:
        d = asdict(self)
        for k in ("facts", "visited", "resolved"):
            d[k] = sorted(d[k])
        d["saved"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as fh:
            json.dump(d, fh, indent=1)

    @classmethod
    def load(cls, path: str) -> "State":
        if not os.path.exists(path):
            return cls()
        with open(path) as fh:
            d = json.load(fh)
        return cls(
            scenario=d.get("scenario", ""), day=d.get("day", 1),
            clock=d.get("clock", "15:00"), date=d.get("date", ""),
            facts=set(d.get("facts", [])), visited=set(d.get("visited", [])),
            resolved=set(d.get("resolved", [])), log=list(d.get("log", [])),
        )

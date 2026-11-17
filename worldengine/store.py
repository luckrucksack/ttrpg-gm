"""World state: one JSON document per campaign.

`engine.json` is the machine record. The markdown ledger stays the human
narrative and is appended from the engine's tick report; it is never rewritten
by the engine, so nothing the table wrote can be lost.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .clock import Clock, format_iso, parse_iso

SCHEMA_VERSION = 1
ACTOR_STATES = ("ACTIVE", "WAITING-ON", "STILLED-BY", "DONE", "UNREVIEWED")
ACTOR_KINDS = ("npc", "faction", "creature", "place", "other")
EVENT_KINDS = ("scheduled", "semantic")


class StoreError(RuntimeError):
    """Missing or malformed engine state."""


def new_actor(name: str, kind: str = "npc", **fields: Any) -> dict:
    actor = {
        "name": name,
        "kind": kind,
        "state": "ACTIVE",
        "state_detail": "",
        "where": "",
        "wants": "",
        "next": "",
        "reactions": [],
        "last_tick": None,
        "last_tick_break": 0,
        "tick_count": 0,
        "notes": [],
    }
    actor.update(fields)
    return actor


def new_event(
    *,
    actor: str | None,
    kind: str,
    text: str,
    at: str | None = None,
    when: dict | None = None,
    when_text: str = "",
    owed: bool = False,
    payoff: str = "",
    applied: dict | None = None,
) -> dict:
    return {
        "id": None,
        "actor": actor,
        "kind": kind,
        "at": at,
        "when": when,
        "when_text": when_text,
        "text": text,
        "status": "pending",
        "created_at": None,
        "fired_at": None,
        "apply": applied or {},
        "owed": owed,
        "payoff": payoff,
    }


def new_convergence(actor: str, what: str, opened: str) -> dict:
    return {
        "id": None,
        "actor": actor,
        "what": what,
        "opened": opened,
        "status": "owed",
        "paid_at": None,
        "note": "",
    }


class Store:
    def __init__(self, path: Path, data: dict):
        self.path = path
        self.data = data

    # -- lifecycle -----------------------------------------------------

    @classmethod
    def create(cls, path: Path, campaign: str, clock: str | None, label: str) -> "Store":
        data = {
            "schema": SCHEMA_VERSION,
            "campaign": campaign,
            "clock": {"at": clock, "label": label},
            "settings": {"freeze_after_breaks": 3},
            "scene_breaks": 0,
            "flags": {},
            "actors": {},
            "events": [],
            "log": [],
            "convergence": [],
        }
        return cls(path, data)

    @classmethod
    def load(cls, path: Path) -> "Store":
        if not path.exists():
            raise StoreError(
                f"no engine state at {path}; run `init` for this campaign first"
            )
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise StoreError(f"{path} is not valid JSON: {exc}") from exc
        if data.get("schema") != SCHEMA_VERSION:
            raise StoreError(
                f"{path}: schema {data.get('schema')!r}, expected {SCHEMA_VERSION}"
            )
        return cls(path, data)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self.data, indent=2, ensure_ascii=False) + "\n"
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=".engine-", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
            os.replace(tmp, self.path)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise

    # -- typed accessors ----------------------------------------------

    @property
    def clock(self) -> Clock:
        raw = self.data["clock"]
        return Clock(parse_iso(raw["at"]) if raw.get("at") else None, raw.get("label", ""))

    def set_clock(self, clock: Clock) -> None:
        self.data["clock"] = {
            "at": format_iso(clock.at) if clock.at else None,
            "label": clock.label,
        }

    @property
    def now_iso(self) -> str:
        clock = self.clock
        return format_iso(clock.require())

    @property
    def actors(self) -> dict[str, dict]:
        return self.data["actors"]

    @property
    def events(self) -> list[dict]:
        return self.data["events"]

    @property
    def flags(self) -> dict[str, dict]:
        return self.data["flags"]

    @property
    def log(self) -> list[dict]:
        return self.data["log"]

    @property
    def convergence(self) -> list[dict]:
        return self.data["convergence"]

    @property
    def scene_breaks(self) -> int:
        return int(self.data.get("scene_breaks", 0))

    @property
    def freeze_after(self) -> int:
        return int(self.data.get("settings", {}).get("freeze_after_breaks", 3))

    # -- helpers -------------------------------------------------------

    def next_id(self, prefix: str, collection: list[dict]) -> str:
        highest = 0
        for item in collection:
            raw = item.get("id") or ""
            if raw.startswith(prefix + "-"):
                try:
                    highest = max(highest, int(raw.split("-", 1)[1]))
                except ValueError:
                    continue
        return f"{prefix}-{highest + 1:04d}"

    def actor(self, name: str, create: bool = False) -> dict:
        found = self.actors.get(name)
        if found:
            return found
        if not create:
            raise StoreError(f"unknown actor {name!r}; add it first or use --create")
        if not name.strip():
            raise StoreError("actor name cannot be empty")
        actor = new_actor(name.strip())
        actor["last_tick_break"] = self.scene_breaks
        if self.clock.started:
            actor["last_tick"] = format_iso(self.clock.require())
        self.actors[actor["name"]] = actor
        return actor

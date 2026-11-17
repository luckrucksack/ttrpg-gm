"""One-way import of a hand-written offscreen ledger into engine state.

The ledger is prose with a shape: `## <time label>` sections of
`- **Actor**: disposition` bullets. Migration keeps every line verbatim in the
log, registers each named actor, and marks them UNREVIEWED — the engine will
not guess a state flag or a next action the table never wrote.
"""

from __future__ import annotations

import re
from pathlib import Path

from .clock import Clock, parse_iso
from .store import Store, StoreError, new_actor

_HEADING = re.compile(r"^##\s+(.+?)\s*$")
_BULLET = re.compile(r"^[-*]\s+(.+?)\s*$")
_BOLD_LEAD = re.compile(r"^\*\*(.+?)\*\*\s*:?\s*(.*)$")
_PAREN = re.compile(r"\s*\([^)]*\)\s*$")
_CONNECTORS = {"of", "the", "and", "at", "de", "van", "der", "von", "del", "la", "le", "el"}


def _looks_like_actor(head: str) -> bool:
    """Gate the colon heuristic to noun phrases.

    Without this, a bullet like "Their network moved within the hour: ..."
    registers a fake actor. Bold leads bypass the check — that is the ledger's
    own convention for naming someone.
    """
    name = _PAREN.sub("", head).strip()
    words = name.split()
    if not 0 < len(words) <= 5:
        return False
    if name.isupper():
        return True
    strong = [word for word in words if word[:1].isupper()]
    weak = [word for word in words if not word[:1].isupper()]
    if not strong:
        return False
    if len(strong) < len(words):
        if not all(word.lower() in _CONNECTORS for word in weak):
            return False
    return len(strong) >= 2 or len(words) == 1


def _actor_and_text(line: str) -> tuple[str | None, str]:
    bold = _BOLD_LEAD.match(line)
    if bold:
        return bold.group(1).strip(), bold.group(2).strip() or ""
    if ":" in line:
        head, _, tail = line.partition(":")
        head = head.strip()
        if 0 < len(head) <= 48 and not head.endswith((".", "?", "!")) and _looks_like_actor(head):
            return head, tail.strip()
    return None, line


def parse_ledger(text: str) -> list[dict]:
    """Split the ledger into ordered sections of entries."""
    sections: list[dict] = []
    current: dict | None = None
    for raw in text.splitlines():
        heading = _HEADING.match(raw)
        if heading:
            current = {"label": heading.group(1), "entries": []}
            sections.append(current)
            continue
        if current is None:
            continue
        bullet = _BULLET.match(raw)
        if bullet:
            actor, body = _actor_and_text(bullet.group(1))
            current["entries"].append({"actor": actor, "text": body})
            continue
        if raw.strip() and raw.startswith((" ", "\t")) and current["entries"]:
            current["entries"][-1]["text"] += " " + raw.strip()
    return [section for section in sections if section["entries"]]


def migrate(store: Store, ledger_text: str, clock: str | None = None) -> dict:
    sections = parse_ledger(ledger_text)
    if not sections:
        raise StoreError("no `## <time>` sections with bullets found in the ledger")

    for section in sections:
        for entry in section["entries"]:
            name = entry["actor"]
            if name:
                if name not in store.actors:
                    actor = new_actor(name)
                    actor["state"] = "UNREVIEWED"
                    actor["last_tick_break"] = 0
                    store.actors[name] = actor
                store.actors[name].setdefault("notes", []).append(
                    f"{section['label']}: {entry['text']}"
                )
            store.log.append(
                {
                    "seq": len(store.log) + 1,
                    "at": None,
                    "label": section["label"],
                    "kind": "migrate",
                    "actor": name,
                    "event": None,
                    "text": entry["text"],
                }
            )

    store.data["scene_breaks"] = len(sections)
    store.set_clock(Clock(parse_iso(clock) if clock else None, sections[-1]["label"]))
    return {
        "sections": len(sections),
        "entries": sum(len(section["entries"]) for section in sections),
        "actors": len(store.actors),
        "first": sections[0]["label"],
        "last": sections[-1]["label"],
    }


def migrate_file(
    campaign_dir: Path, ledger_path: Path, clock: str | None, force: bool
) -> tuple[Store, dict]:
    target = campaign_dir / "engine.json"
    if target.exists() and not force:
        raise StoreError(f"{target} already exists; pass --force to overwrite")
    store = Store.create(target, campaign_dir.name, None, "")
    summary = migrate(store, ledger_path.read_text(encoding="utf-8"), clock)
    store.save()
    return store, summary

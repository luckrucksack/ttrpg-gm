"""Deterministic world engine: clock, event table, triggers, convergence.

The engine does bookkeeping only. It never invents fiction: the LLM authors
events, the engine fires them on time or on evidence, and reports what changed.
That split is the cost model — no model call per event, one call per tick when
the GM narrates.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any, Iterable

from .clock import Clock, format_iso, parse_duration, parse_iso
from .store import ACTOR_STATES, Store, StoreError, new_convergence, new_event

APPLY_FIELDS = ("state", "state_detail", "where", "wants", "next")


# -- conditions --------------------------------------------------------


def eval_condition(cond: dict, flags: dict[str, dict]) -> bool:
    """Evaluate a trigger condition. Grammar:

    {"flag": "name", "is": true|false}   flag set (or explicitly false)
    {"all": [cond, ...]}                 every child true
    {"any": [cond, ...]}                 at least one child true
    {"not": cond}                        negation

    Anything else is a typo, and a typo must fail loudly rather than silently
    never fire.
    """
    if not isinstance(cond, dict) or not cond:
        raise StoreError(f"malformed condition: {cond!r}")
    if "all" in cond:
        return all(eval_condition(child, flags) for child in cond["all"])
    if "any" in cond:
        return any(eval_condition(child, flags) for child in cond["any"])
    if "not" in cond:
        return not eval_condition(cond["not"], flags)
    if "flag" in cond:
        name = cond["flag"]
        if not isinstance(name, str):
            raise StoreError(f"malformed flag name: {name!r}")
        wanted = cond.get("is", True)
        if not isinstance(wanted, bool):
            raise StoreError(f"`is` must be true or false in {cond!r}")
        return bool(flags.get(name, {}).get("value", False)) is wanted
    raise StoreError(f"unknown condition type: {cond!r}")


def flag_condition(name: str, is_set: bool = True) -> dict:
    return {"flag": name, "is": is_set}


# -- firing ------------------------------------------------------------


def _fire(store: Store, event: dict, now_iso: str) -> None:
    event["status"] = "fired"
    event["fired_at"] = now_iso

    actor = store.actors.get(event["actor"]) if event.get("actor") else None
    if actor is not None:
        actor["last_tick"] = now_iso
        actor["last_tick_break"] = store.scene_breaks
        actor["tick_count"] = int(actor.get("tick_count", 0)) + 1
        applied = event.get("apply") or {}
        for field in APPLY_FIELDS:
            if applied.get(field):
                actor[field] = applied[field]
        if actor["state"] == "WAITING-ON" and "state" not in applied:
            actor["state"] = "ACTIVE"
            actor["state_detail"] = ""
        if event.get("text"):
            actor.setdefault("notes", []).append(f"{now_iso}: {event['text']}")

    if event.get("owed"):
        item = new_convergence(
            event.get("actor") or "world",
            event.get("payoff") or event["text"],
            now_iso,
        )
        item["id"] = store.next_id("cv", store.convergence)
        store.convergence.append(item)

    store.log.append(
        {
            "seq": len(store.log) + 1,
            "at": now_iso,
            "label": store.clock.label,
            "kind": "fire",
            "actor": event.get("actor"),
            "event": event["id"],
            "text": event["text"],
        }
    )


def evaluate(store: Store) -> list[dict]:
    """Fire everything due at the current in-game time. Idempotent.

    Advance-on-read: every command that reads the world calls this first, so
    a thread that should have moved while nobody looked moves before it is
    looked at.
    """
    if not store.clock.started:
        return []
    now = store.clock.require()
    now_iso = format_iso(now)
    fired: list[dict] = []
    settled = False
    guards = 0
    while not settled:
        guards += 1
        if guards > 1000:
            raise StoreError("trigger cascade never settled; check for a loop")
        settled = True
        for event in list(store.events):
            if event.get("status") != "pending":
                continue
            if event["kind"] == "scheduled":
                due = event.get("at") and parse_iso(event["at"]) <= now
            else:
                due = event.get("when") and eval_condition(event["when"], store.flags)
            if due:
                _fire(store, event, now_iso)
                fired.append(event)
                settled = False
    return fired


def set_flag(store: Store, name: str, value: bool = True, note: str = "") -> list[dict]:
    """Set or clear an evidence flag, then schedule any reactions to it.

    A reaction is an NPC's standing rule — 'hears X -> does Z, after D' —
    imported from the dossier so the engine does not have to invent a response
    mid-scene.
    """
    store.flags[name] = {
        "value": value,
        "at": store.now_iso if store.clock.started else None,
        "note": note,
    }
    scheduled: list[dict] = []
    if not value:
        return scheduled
    now = store.clock.require()
    for actor in store.actors.values():
        for reaction in actor.get("reactions", []):
            if reaction.get("on_flag") != name or reaction.get("fired_at"):
                continue
            reaction["fired_at"] = format_iso(now)
            delay = parse_duration(reaction.get("after") or "0s")
            event = new_event(
                actor=actor["name"],
                kind="scheduled",
                text=reaction["does"],
                at=format_iso(now + delay),
                owed=bool(reaction.get("owed")),
                payoff=reaction.get("payoff", ""),
            )
            event["id"] = store.next_id("ev", store.events)
            event["created_at"] = format_iso(now)
            store.events.append(event)
            scheduled.append(event)
    store.log.append(
        {
            "seq": len(store.log) + 1,
            "at": store.now_iso if store.clock.started else "",
            "label": store.clock.label,
            "kind": "flag",
            "actor": None,
            "event": None,
            "text": f"{name} = {value}" + (f" ({note})" if note else ""),
        }
    )
    return scheduled


# -- clock -------------------------------------------------------------


def tick(
    store: Store,
    *,
    by: str | None = None,
    to: str | None = None,
    label: str | None = None,
    note: str = "",
) -> dict:
    """Advance the fiction clock one scene break, then fire what came due."""
    clock = store.clock
    before = clock.at
    if to:
        target = parse_iso(to)
    elif by:
        target = clock.require() + parse_duration(by)
    else:
        raise StoreError("tick needs --by or --to")
    if before is not None and target <= before:
        raise StoreError(
            f"clock cannot move backwards ({format_iso(before)} -> {format_iso(target)})"
        )
    clock.at = target
    if label is not None:
        clock.label = label
    store.set_clock(clock)
    store.data["scene_breaks"] = store.scene_breaks + 1
    if note:
        store.log.append(
            {
                "seq": len(store.log) + 1,
                "at": format_iso(target),
                "label": clock.label,
                "kind": "note",
                "actor": None,
                "event": None,
                "text": note,
            }
        )
    fired = evaluate(store)
    return {
        "from": format_iso(before) if before else None,
        "to": format_iso(target),
        "label": clock.label,
        "scene_break": store.scene_breaks,
        "fired": fired,
    }


# -- audits ------------------------------------------------------------


def freeze_audit(store: Store) -> list[dict]:
    """ACTIVE actors nobody has moved in `freeze_after_breaks` scene breaks.

    Convergence's failure was silence, not error: NPCs met once and never
    ticked again. This names them before the table notices.
    """
    frozen = []
    for actor in store.actors.values():
        if actor["state"] != "ACTIVE":
            continue
        idle = store.scene_breaks - int(actor.get("last_tick_break", 0))
        if idle >= store.freeze_after:
            frozen.append(
                {
                    "name": actor["name"],
                    "idle_breaks": idle,
                    "where": actor.get("where", ""),
                    "next": actor.get("next", ""),
                }
            )
    return sorted(frozen, key=lambda item: (-item["idle_breaks"], item["name"]))


def pending(store: Store) -> list[dict]:
    events = [e for e in store.events if e.get("status") == "pending"]
    return sorted(
        events,
        key=lambda e: (e.get("at") or "9999", e.get("id") or ""),
    )


def owed(store: Store) -> list[dict]:
    return [item for item in store.convergence if item.get("status") == "owed"]


def counts(store: Store) -> dict[str, int]:
    tally = {state: 0 for state in ACTOR_STATES}
    for actor in store.actors.values():
        state = actor.get("state", "UNREVIEWED")
        tally[state] = tally.get(state, 0) + 1
    return tally


def status(store: Store) -> dict:
    fired = evaluate(store)
    clock = store.clock
    return {
        "campaign": store.data["campaign"],
        "clock": {
            "at": format_iso(clock.at) if clock.at else None,
            "label": clock.label,
            "scene_breaks": store.scene_breaks,
        },
        "fired_on_read": fired,
        "counts": counts(store),
        "freeze": freeze_audit(store),
        "pending": pending(store),
        "owed": owed(store),
        "unreviewed": [
            a["name"] for a in store.actors.values() if a["state"] == "UNREVIEWED"
        ],
    }


def wrapup(store: Store) -> dict:
    """The campaign-end pass: name every thread still open."""
    open_actors = [
        {
            "name": a["name"],
            "state": a["state"],
            "state_detail": a.get("state_detail", ""),
            "next": a.get("next", ""),
            "where": a.get("where", ""),
        }
        for a in store.actors.values()
        if a["state"] in ("ACTIVE", "WAITING-ON", "UNREVIEWED")
    ]
    debts = [
        {"id": item["id"], "actor": item["actor"], "what": item["what"]}
        for item in owed(store)
    ]
    queued = [
        {"id": event["id"], "actor": event["actor"], "text": event["text"]}
        for event in pending(store)
    ]
    return {
        "ready": not open_actors and not debts and not queued,
        "open_actors": open_actors,
        "owed": debts,
        "pending": queued,
    }


# -- convergence -------------------------------------------------------


def add_convergence(store: Store, actor: str, what: str, note: str = "") -> dict:
    item = new_convergence(actor, what, store.now_iso)
    item["id"] = store.next_id("cv", store.convergence)
    item["note"] = note
    store.convergence.append(item)
    return item


def settle_convergence(store: Store, cid: str, outcome: str, note: str = "") -> dict:
    if outcome not in ("paid", "dropped"):
        raise StoreError(f"convergence outcome must be paid or dropped, not {outcome!r}")
    for item in store.convergence:
        if item["id"] == cid:
            item["status"] = outcome
            item["paid_at"] = store.now_iso if store.clock.started else None
            if note:
                item["note"] = note
            return item
    raise StoreError(f"no convergence item {cid!r}")


# -- rendering ---------------------------------------------------------

_STATE_ORDER = ("ACTIVE", "WAITING-ON", "STILLED-BY", "UNREVIEWED", "DONE")


def status_markdown(store: Store) -> str:
    snap = status(store)
    clock = snap["clock"]
    lines = [f"# World engine — {snap['campaign']}", ""]
    when = clock["at"] or "clock unset"
    lines.append(f"Clock: {when}" + (f" ({clock['label']})" if clock["label"] else ""))
    lines.append(f"Scene breaks: {clock['scene_breaks']}")
    tally = ", ".join(
        f"{snap['counts'].get(state, 0)} {state.lower()}" for state in _STATE_ORDER
    )
    lines.append(f"Actors: {tally}")
    lines.append("")

    if snap["fired_on_read"]:
        lines.append("## Fired on read")
        for event in snap["fired_on_read"]:
            lines.append(f"- {event['actor'] or 'world'}: {event['text']}")
        lines.append("")

    lines.append("## Pending")
    if snap["pending"]:
        for event in snap["pending"]:
            when_text = event["at"] or f"when {event.get('when_text') or event.get('when')}"
            lines.append(f"- {event['id']} {event['actor'] or 'world'} — {when_text}: {event['text']}")
    else:
        lines.append("- Nothing pending.")
    lines.append("")

    lines.append("## Freeze audit")
    if snap["freeze"]:
        for item in snap["freeze"]:
            lines.append(
                f"- {item['name']}: {item['idle_breaks']} breaks untouched"
                + (f"; next was: {item['next']}" if item["next"] else "; no next action on record")
            )
    else:
        lines.append("- No ACTIVE actor has gone quiet.")
    lines.append("")

    lines.append("## Owed to the table")
    if snap["owed"]:
        for item in snap["owed"]:
            lines.append(f"- {item['id']} {item['actor']}: {item['what']}")
    else:
        lines.append("- Nothing owed.")
    lines.append("")

    if snap["unreviewed"]:
        lines.append("## Unreviewed (give each a state flag)")
        for name in snap["unreviewed"]:
            lines.append(f"- {name}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def tick_markdown(report: dict, note: str = "") -> str:
    head = f"## {report['label'] or 'scene break'} ({report['to']})"
    lines = [head]
    if note:
        lines.append(f"- {note}")
    if report["fired"]:
        for event in report["fired"]:
            lines.append(f"- **{event['actor'] or 'world'}**: {event['text']}")
    else:
        lines.append("- Nothing came due.")
    return "\n".join(lines) + "\n"


def append_ledger(path: Path, block: str) -> bool:
    """Append a tick block unless that exact block is already in the file."""
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    marker = block.strip().splitlines()[0]
    if marker and marker in existing:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        if existing and not existing.endswith("\n\n"):
            handle.write("\n" if existing.endswith("\n") else "\n\n")
        handle.write(block.strip() + "\n")
    return True

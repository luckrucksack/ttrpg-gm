"""Command line for the offscreen world engine.

Run from the repo root: `python3 -m worldengine status extremophilia`.
The GM calls these mid-session; every read is advance-on-read, so the world
catches up before it is described.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .clock import Clock, format_iso, parse_iso
from .engine import (
    add_convergence,
    append_ledger,
    freeze_audit,
    owed,
    pending,
    set_flag,
    settle_convergence,
    status,
    status_markdown,
    tick,
    tick_markdown,
    wrapup,
)
from .migrate import migrate_file
from .store import ACTOR_KINDS, ACTOR_STATES, Store, StoreError, new_event

SCOPED_STATES = ("WAITING-ON", "STILLED-BY")


def campaign_dir(name: str) -> Path:
    path = Path(name).expanduser()
    if path.is_absolute() or "/" in name:
        return path
    return Path("campaigns") / name


def _state_with_detail(state: str | None, detail: str | None) -> dict:
    if state and state not in ACTOR_STATES:
        raise StoreError(f"state must be one of {', '.join(ACTOR_STATES)}")
    if state in SCOPED_STATES and not detail:
        raise StoreError(f"{state} needs --detail naming the trigger or cause")
    payload: dict = {}
    if state:
        payload["state"] = state
    if detail is not None:
        payload["state_detail"] = detail
    return payload


def _load(name: str) -> Store:
    return Store.load(campaign_dir(name) / "engine.json")


def _print(text: str) -> None:
    sys.stdout.write(text if text.endswith("\n") else text + "\n")


# -- commands ----------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> int:
    directory = campaign_dir(args.campaign)
    target = directory / "engine.json"
    if target.exists() and not args.force:
        raise StoreError(f"{target} already exists; pass --force to overwrite")
    clock = None
    if args.clock:
        clock = format_iso(parse_iso(args.clock))
    store = Store.create(target, directory.name, clock, args.label or "")
    store.save()
    _print(f"initialized {target}" + (f" at {clock} ({store.clock.label})" if clock else ""))
    return 0


def cmd_clock(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    clock = store.clock
    if args.set:
        clock.at = parse_iso(args.set)
    if args.label is not None:
        clock.label = args.label
    store.set_clock(clock)
    store.save()
    _print(f"clock: {clock.describe()}")
    return 0


def cmd_tick(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    report = tick(store, by=args.by, to=args.to, label=args.label, note=args.note or "")
    store.save()
    if args.json:
        _print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    block = tick_markdown(report, args.note or "")
    if args.append_ledger:
        target = campaign_dir(args.campaign) / "offscreen-ledger.md"
        added = append_ledger(target, block)
        block += f"\n({'appended to ' + str(target) if added else 'already in ' + str(target)})\n"
    _print(block)
    if args.md:
        return 0
    frozen = freeze_audit(store)
    if frozen:
        _print("Freeze audit — resolve these before the next scene:")
        for item in frozen:
            _print(f"- {item['name']}: {item['idle_breaks']} breaks untouched")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    snap = status(store)
    if snap["fired_on_read"]:
        store.save()
    if args.json:
        _print(json.dumps(snap, indent=2, ensure_ascii=False, default=str))
    else:
        _print(status_markdown(store))
    return 0


def cmd_actor_add(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    if args.name in store.actors:
        raise StoreError(f"actor {args.name!r} already exists")
    if args.kind not in ACTOR_KINDS:
        raise StoreError(f"kind must be one of {', '.join(ACTOR_KINDS)}")
    _state_with_detail(args.state, args.detail)
    actor = store.actor(args.name, create=True)
    actor.update(
        {
            "kind": args.kind,
            "state": args.state or "ACTIVE",
            "state_detail": args.detail or "",
            "where": args.where or "",
            "wants": args.wants or "",
            "next": args.next or "",
            "last_tick": store.now_iso if store.clock.started else None,
            "last_tick_break": store.scene_breaks,
        }
    )
    store.save()
    _print(f"added {actor['name']} ({actor['kind']}, {actor['state']})")
    return 0


def cmd_actor_set(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    actor = store.actor(args.name)
    update = _state_with_detail(args.state, args.detail)
    for field in ("where", "wants", "next"):
        value = getattr(args, field)
        if value is not None:
            update[field] = value
    if not update:
        raise StoreError("nothing to set")
    actor.update(update)
    store.save()
    changed = ", ".join(f"{key}={value!r}" for key, value in update.items() if value)
    _print(f"{actor['name']}: {changed}")
    return 0


def cmd_actor_list(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    actors = [
        actor
        for actor in store.actors.values()
        if not args.state or actor["state"] == args.state
    ]
    if not actors:
        _print("no actors")
        return 0
    order = {state: index for index, state in enumerate(ACTOR_STATES)}
    actors.sort(key=lambda a: (order.get(a["state"], 99), a["name"]))
    for actor in actors:
        line = f"{actor['name']} [{actor['kind']}] {actor['state']}"
        if actor.get("state_detail"):
            line += f" ({actor['state_detail']})"
        if actor.get("where"):
            line += f" — at {actor['where']}"
        if actor.get("next"):
            line += f"; next: {actor['next']}"
        _print(line)
    return 0


def cmd_actor_reaction(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    actor = store.actor(args.name)
    actor.setdefault("reactions", []).append(
        {
            "on_flag": args.on_flag,
            "does": args.does,
            "after": args.after or "0s",
            "owed": bool(args.owed),
            "payoff": args.payoff or "",
            "fired_at": None,
        }
    )
    store.save()
    _print(f"{actor['name']}: on {args.on_flag} -> {args.does} (after {args.after or '0s'})")
    return 0


def cmd_event_add(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    if bool(args.at) == bool(args.when_flag):
        raise StoreError("give exactly one of --at or --when-flag")
    if not args.text.strip():
        raise StoreError("--text is required")
    if args.actor:
        store.actor(args.actor, create=args.create)
    when = {"flag": args.when_flag, "is": not args.when_false} if args.when_flag else None
    applied = {
        key: getattr(args, key)
        for key in ("state", "detail", "where", "next")
        if getattr(args, key)
    }
    if "detail" in applied:
        applied["state_detail"] = applied.pop("detail")
    if applied.get("state"):
        _state_with_detail(applied["state"], applied.get("state_detail"))
    event = new_event(
        actor=args.actor,
        kind="scheduled" if args.at else "semantic",
        text=args.text,
        at=format_iso(parse_iso(args.at)) if args.at else None,
        when=when,
        when_text=args.when_text or (f"{args.when_flag} is {not args.when_false}" if args.when_flag else ""),
        owed=bool(args.owed),
        payoff=args.payoff or "",
        applied=applied,
    )
    event["id"] = store.next_id("ev", store.events)
    event["created_at"] = store.now_iso if store.clock.started else None
    store.events.append(event)
    store.save()
    trigger = event["at"] or event["when_text"]
    _print(f"{event['id']} {event['actor'] or 'world'} — {trigger}: {event['text']}")
    return 0


def cmd_event_list(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    events = pending(store) if not args.all else store.events
    if not events:
        _print("no events")
        return 0
    for event in events:
        trigger = event["at"] or f"when {event.get('when_text') or event.get('when')}"
        _print(
            f"{event['id']} [{event['status']}] {event['actor'] or 'world'} — {trigger}: {event['text']}"
        )
    return 0


def cmd_event_cancel(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    for event in store.events:
        if event["id"] == args.id:
            if event["status"] != "pending":
                raise StoreError(f"{args.id} is already {event['status']}")
            event["status"] = "cancelled"
            store.save()
            _print(f"cancelled {args.id}")
            return 0
    raise StoreError(f"no event {args.id!r}")


def cmd_flag_set(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    scheduled = set_flag(store, args.name, value=not args.false, note=args.note or "")
    store.save()
    _print(f"flag {args.name} = {not args.false}")
    for event in scheduled:
        _print(f"  reaction queued: {event['id']} {event['actor']} at {event['at']}")
    return 0


def cmd_flag_list(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    if not store.flags:
        _print("no flags")
        return 0
    for name, flag in sorted(store.flags.items()):
        mark = "true" if flag.get("value") else "false"
        when = flag.get("at") or "unset time"
        note = f" — {flag['note']}" if flag.get("note") else ""
        _print(f"{name} = {mark} ({when}){note}")
    return 0


def cmd_converge_add(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    item = add_convergence(store, args.actor, args.what)
    store.save()
    _print(f"{item['id']} {item['actor']}: {item['what']}")
    return 0


def cmd_converge_list(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    items = store.convergence if args.all else owed(store)
    if not items:
        _print("nothing owed")
        return 0
    for item in items:
        _print(f"{item['id']} [{item['status']}] {item['actor']}: {item['what']}")
    return 0


def cmd_converge_settle(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    item = settle_convergence(store, args.id, args.outcome, args.note or "")
    store.save()
    _print(f"{item['id']} {item['status']}")
    return 0


def cmd_wrapup(args: argparse.Namespace) -> int:
    store = _load(args.campaign)
    report = wrapup(store)
    if args.json:
        _print(json.dumps(report, indent=2, ensure_ascii=False))
    elif report["ready"]:
        _print("Every thread is closed. Nothing owed.")
    else:
        _print("Open threads at wrap-up:")
        for actor in report["open_actors"]:
            detail = f" ({actor['state_detail']})" if actor["state_detail"] else ""
            _print(f"- {actor['name']}: {actor['state']}{detail}" + (f"; next was: {actor['next']}" if actor["next"] else ""))
        for item in report["owed"]:
            _print(f"- owed {item['id']} {item['actor']}: {item['what']}")
        for event in report["pending"]:
            _print(f"- queued {event['id']} {event['actor'] or 'world'}: {event['text']}")
    if args.strict and not report["ready"]:
        return 1
    return 0


def cmd_migrate(args: argparse.Namespace) -> int:
    directory = campaign_dir(args.campaign)
    ledger = Path(args.from_path).expanduser()
    if not ledger.exists():
        raise StoreError(f"no ledger at {ledger}")
    store, summary = migrate_file(directory, ledger, args.clock, args.force)
    _print(
        f"migrated {summary['entries']} entries in {summary['sections']} sections "
        f"({summary['first']} .. {summary['last']}); {summary['actors']} actors, all UNREVIEWED"
    )
    _print(f"state: {store.path}")
    return 0


# -- parser ------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worldengine",
        description="Offscreen world engine: in-game clock, event table, convergence queue.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create engine state for a campaign")
    init.add_argument("campaign")
    init.add_argument("--clock", help="ISO start time, e.g. 1995-06-12T13:00")
    init.add_argument("--label", help="fiction label, e.g. 'Day 1, afternoon'")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    status_cmd = sub.add_parser("status", help="advance-on-read snapshot")
    status_cmd.add_argument("campaign")
    status_cmd.add_argument("--json", action="store_true")
    status_cmd.set_defaults(func=cmd_status)

    clock = sub.add_parser("clock", help="show or set the in-game clock without ticking")
    clock.add_argument("campaign")
    clock.add_argument("--set", help="ISO time")
    clock.add_argument("--label")
    clock.set_defaults(func=cmd_clock)

    tick_cmd = sub.add_parser("tick", help="advance the clock one scene break and fire what is due")
    tick_cmd.add_argument("campaign")
    tick_cmd.add_argument("--by", help="duration: 30s, 15m, 2h, 1d 4h")
    tick_cmd.add_argument("--to", help="ISO time")
    tick_cmd.add_argument("--label", help="new fiction label")
    tick_cmd.add_argument("--note", help="one line of table narrative for this break")
    tick_cmd.add_argument("--md", action="store_true", help="print only the ledger block")
    tick_cmd.add_argument("--append-ledger", action="store_true", help="append the block to offscreen-ledger.md")
    tick_cmd.add_argument("--json", action="store_true")
    tick_cmd.set_defaults(func=cmd_tick)

    actor = sub.add_parser("actor", help="actors: NPCs, factions, creatures, places")
    actor_sub = actor.add_subparsers(dest="actor_command", required=True)
    actor_add = actor_sub.add_parser("add")
    actor_add.add_argument("campaign")
    actor_add.add_argument("name")
    actor_add.add_argument("--kind", default="npc", choices=ACTOR_KINDS)
    actor_add.add_argument("--state", choices=ACTOR_STATES)
    actor_add.add_argument("--detail")
    actor_add.add_argument("--where")
    actor_add.add_argument("--wants")
    actor_add.add_argument("--next")
    actor_add.set_defaults(func=cmd_actor_add)

    actor_set = actor_sub.add_parser("set")
    actor_set.add_argument("campaign")
    actor_set.add_argument("name")
    actor_set.add_argument("--state", choices=ACTOR_STATES)
    actor_set.add_argument("--detail")
    actor_set.add_argument("--where")
    actor_set.add_argument("--wants")
    actor_set.add_argument("--next")
    actor_set.set_defaults(func=cmd_actor_set)

    actor_list = actor_sub.add_parser("list")
    actor_list.add_argument("campaign")
    actor_list.add_argument("--state", choices=ACTOR_STATES)
    actor_list.set_defaults(func=cmd_actor_list)

    reaction = actor_sub.add_parser("reaction", help="standing rule: hears X -> does Z after D")
    reaction.add_argument("campaign")
    reaction.add_argument("name")
    reaction.add_argument("--on-flag", required=True)
    reaction.add_argument("--does", required=True)
    reaction.add_argument("--after", default="0s")
    reaction.add_argument("--owed", action="store_true")
    reaction.add_argument("--payoff")
    reaction.set_defaults(func=cmd_actor_reaction)

    event = sub.add_parser("event", help="event table entries")
    event_sub = event.add_subparsers(dest="event_command", required=True)
    event_add = event_sub.add_parser("add")
    event_add.add_argument("campaign")
    event_add.add_argument("--actor")
    event_add.add_argument("--create", action="store_true", help="create the actor if unknown")
    event_add.add_argument("--at", help="ISO due time")
    event_add.add_argument("--when-flag", help="fire when this flag is true")
    event_add.add_argument("--when-false", action="store_true", help="fire when the flag is false")
    event_add.add_argument("--when-text", help="human wording of the condition")
    event_add.add_argument("--text", required=True, help="what happens")
    event_add.add_argument("--owed", action="store_true", help="queue a pay-back at the table")
    event_add.add_argument("--payoff", help="how the player meets it")
    event_add.add_argument("--state", choices=ACTOR_STATES)
    event_add.add_argument("--detail")
    event_add.add_argument("--where")
    event_add.add_argument("--next")
    event_add.set_defaults(func=cmd_event_add)

    event_list = event_sub.add_parser("list")
    event_list.add_argument("campaign")
    event_list.add_argument("--all", action="store_true")
    event_list.set_defaults(func=cmd_event_list)

    event_cancel = event_sub.add_parser("cancel")
    event_cancel.add_argument("campaign")
    event_cancel.add_argument("id")
    event_cancel.set_defaults(func=cmd_event_cancel)

    flag = sub.add_parser("flag", help="evidence flags that semantic triggers read")
    flag_sub = flag.add_subparsers(dest="flag_command", required=True)
    flag_set = flag_sub.add_parser("set")
    flag_set.add_argument("campaign")
    flag_set.add_argument("name")
    flag_set.add_argument("--note")
    flag_set.add_argument("--false", action="store_true", help="record the flag as known-false")
    flag_set.set_defaults(func=cmd_flag_set)
    flag_list = flag_sub.add_parser("list")
    flag_list.add_argument("campaign")
    flag_list.set_defaults(func=cmd_flag_list)

    converge = sub.add_parser("converge", help="pay-backs owed to the table")
    converge_sub = converge.add_subparsers(dest="converge_command", required=True)
    converge_add = converge_sub.add_parser("add")
    converge_add.add_argument("campaign")
    converge_add.add_argument("--actor", required=True)
    converge_add.add_argument("--what", required=True)
    converge_add.set_defaults(func=cmd_converge_add)
    converge_list = converge_sub.add_parser("list")
    converge_list.add_argument("campaign")
    converge_list.add_argument("--all", action="store_true")
    converge_list.set_defaults(func=cmd_converge_list)
    for outcome in ("pay", "drop"):
        settle = converge_sub.add_parser(outcome)
        settle.add_argument("campaign")
        settle.add_argument("id")
        settle.add_argument("--note")
        settle.set_defaults(func=cmd_converge_settle, outcome="paid" if outcome == "pay" else "dropped")

    wrap = sub.add_parser("wrapup", help="campaign-end audit of open threads")
    wrap.add_argument("campaign")
    wrap.add_argument("--json", action="store_true")
    wrap.add_argument("--strict", action="store_true", help="exit 1 while threads remain open")
    wrap.set_defaults(func=cmd_wrapup)

    migration = sub.add_parser("migrate", help="import a hand-written ledger into engine state")
    migration.add_argument("campaign")
    migration.add_argument("--from", dest="from_path", required=True)
    migration.add_argument("--clock")
    migration.add_argument("--force", action="store_true")
    migration.set_defaults(func=cmd_migrate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (StoreError, ValueError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

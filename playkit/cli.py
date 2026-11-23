"""Command line: lint a scenario, inspect state, get the day's brief."""
from __future__ import annotations
import argparse, sys
from .model import load
from .lint import lint, ERROR
from .state import State
from . import runtime


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="playkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("lint", help="check a scenario declaration")
    a.add_argument("scenario")

    b = sub.add_parser("brief", help="what is live right now")
    b.add_argument("scenario")
    b.add_argument("--state", default="state.json")

    c = sub.add_parser("advance", help="move the clock")
    c.add_argument("--state", default="state.json")
    c.add_argument("--days", type=int, default=1)

    d = sub.add_parser("visit", help="record a node visited")
    d.add_argument("node")
    d.add_argument("--state", default="state.json")

    args = p.parse_args(argv)

    if args.cmd == "lint":
        scn = load(args.scenario)
        issues = lint(scn)
        for i in issues:
            print(i)
        errs = sum(1 for i in issues if i.severity == ERROR)
        print(f"\n{len(scn.nodes)} nodes, {len(scn.clues)} clues, "
              f"{len(scn.conclusions)} conclusions, {len(scn.ticks)} ticks: "
              f"{errs} error(s), {len(issues) - errs} warning(s)")
        return 1 if errs else 0

    if args.cmd == "brief":
        scn = load(args.scenario)
        st = State.load(args.state)
        if not st.scenario:
            st.scenario = scn.id
            for n in scn.entry_nodes():
                st.visited.add(n.id)
        print(runtime.brief(scn, st))
        return 0

    if args.cmd == "advance":
        st = State.load(args.state)
        st.advance(args.days)
        st.save(args.state)
        print(f"day {st.day}")
        return 0

    if args.cmd == "visit":
        st = State.load(args.state)
        st.visit(args.node)
        st.save(args.state)
        print(f"visited {args.node} on day {st.day}")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())

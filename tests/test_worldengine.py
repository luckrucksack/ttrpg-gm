"""Tests for the offscreen world engine. Run: python3 -m unittest discover -s tests"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from worldengine.clock import Clock, parse_duration, parse_iso  # noqa: E402
from worldengine.cli import main  # noqa: E402
from worldengine.engine import (  # noqa: E402
    add_convergence,
    append_ledger,
    evaluate,
    eval_condition,
    freeze_audit,
    set_flag,
    settle_convergence,
    status,
    tick,
    wrapup,
)
from worldengine.migrate import migrate, parse_ledger  # noqa: E402
from worldengine.store import Store, StoreError, new_event  # noqa: E402


def make_store(directory: Path, clock: str = "1995-06-12T13:00") -> Store:
    return Store.create(directory / "engine.json", "test", clock, "Day 1, afternoon")


def add_actor(store: Store, name: str, **fields) -> dict:
    actor = store.actor(name, create=True)
    actor.update({"state": "ACTIVE", **fields})
    return actor


def add_event(store: Store, **kwargs) -> dict:
    event = new_event(**kwargs)
    event["id"] = store.next_id("ev", store.events)
    event["created_at"] = store.now_iso
    store.events.append(event)
    return event


class ClockTests(unittest.TestCase):
    def test_durations(self):
        self.assertEqual(parse_duration("30s"), timedelta(seconds=30))
        self.assertEqual(parse_duration("15m"), timedelta(minutes=15))
        self.assertEqual(parse_duration("1d 4h"), timedelta(days=1, hours=4))
        self.assertEqual(parse_duration("3w"), timedelta(weeks=3))
        for bad in ("", "2", "h", "2x", "1h 30"):
            with self.assertRaises(ValueError):
                parse_duration(bad)

    def test_iso_and_describe(self):
        moment = parse_iso("1995-06-12T13:00")
        self.assertEqual(moment.hour, 13)
        self.assertEqual(parse_iso("1995-06-12T13:00:00Z").tzinfo, None)
        clock = Clock(moment, "Day 1")
        self.assertIn("Day 1", clock.describe())
        self.assertEqual(clock.advance(timedelta(hours=2)).hour, 15)

    def test_unstarted_clock_refuses_to_advance(self):
        clock = Clock(None, "")
        with self.assertRaises(ValueError):
            clock.advance(timedelta(hours=1))


class TriggerTests(unittest.TestCase):
    def test_condition_grammar(self):
        flags = {"a": {"value": True}, "b": {"value": False}}
        self.assertTrue(eval_condition({"flag": "a"}, flags))
        self.assertTrue(eval_condition({"flag": "b", "is": False}, flags))
        self.assertFalse(eval_condition({"flag": "missing"}, flags))
        self.assertTrue(eval_condition({"all": [{"flag": "a"}, {"flag": "b", "is": False}]}, flags))
        self.assertFalse(eval_condition({"any": [{"flag": "b"}, {"flag": "missing"}]}, flags))
        self.assertTrue(eval_condition({"not": {"flag": "b"}}, flags))
        with self.assertRaises(StoreError):
            eval_condition({"flags": "a"}, flags)

    def test_scheduled_fires_only_when_due(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = make_store(Path(tmp))
            actor = add_actor(store, "Oakley", where="Knoxville")
            add_event(
                store,
                actor="Oakley",
                kind="scheduled",
                text="Back from Knoxville.",
                at="1995-06-12T15:00",
                applied={"where": "the ridge"},
            )
            self.assertEqual(evaluate(store), [])
            report = tick(store, by="2h")
            self.assertEqual(len(report["fired"]), 1)
            self.assertEqual(actor["where"], "the ridge")
            self.assertEqual(actor["tick_count"], 1)

    def test_semantic_fires_on_flag_and_on_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = make_store(Path(tmp))
            add_actor(store, "The board")
            add_event(
                store,
                actor="The board",
                kind="semantic",
                text="Sets a watch at the reservoir.",
                when={"flag": "player_learned_water_source"},
                when_text="the player learns the water source",
                owed=True,
            )
            self.assertEqual(store.log, [])
            store.flags["player_learned_water_source"] = {"value": True}
            snap = status(store)  # advance-on-read, no tick
            self.assertEqual(len(snap["fired_on_read"]), 1)
            self.assertEqual(len(snap["owed"]), 1)
            self.assertEqual(snap["owed"][0]["actor"], "The board")

    def test_reaction_schedules_after_delay(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = make_store(Path(tmp))
            actor = add_actor(store, "Merle")
            actor["reactions"].append(
                {
                    "on_flag": "barn_burned",
                    "does": "Calls the sheriff.",
                    "after": "1h",
                    "fired_at": None,
                }
            )
            scheduled = set_flag(store, "barn_burned", True, "player lit it")
            self.assertEqual(len(scheduled), 1)
            self.assertEqual(scheduled[0]["at"], "1995-06-12T14:00")
            self.assertEqual(evaluate(store), [])
            tick(store, by="1h")
            self.assertEqual(actor["tick_count"], 1)
            self.assertEqual(actor["state"], "ACTIVE")

    def test_waiting_on_resolves_when_its_event_fires(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = make_store(Path(tmp))
            actor = add_actor(store, "Jane", state="WAITING-ON", state_detail="the deputy leaves")
            add_event(
                store,
                actor="Jane",
                kind="scheduled",
                text="The deputy is gone; she walks out.",
                at="1995-06-12T16:00",
            )
            tick(store, by="3h")
            self.assertEqual(actor["state"], "ACTIVE")
            self.assertEqual(actor["state_detail"], "")

    def test_cascade_settles(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = make_store(Path(tmp))
            for index in range(3):
                add_event(
                    store,
                    actor=None,
                    kind="semantic",
                    text=f"world beat {index}",
                    when={"flag": "go"},
                )
            set_flag(store, "go")
            self.assertEqual(len(evaluate(store)), 3)
            self.assertEqual(evaluate(store), [])


class FreezeTests(unittest.TestCase):
    def test_active_actor_goes_stale_after_threshold(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = make_store(Path(tmp))
            add_actor(store, "Derringer", next="waits for a report")
            add_actor(store, "Merle", state="STILLED-BY", state_detail="under guard")
            for _ in range(3):
                tick(store, by="1h")
            frozen = freeze_audit(store)
            self.assertEqual([item["name"] for item in frozen], ["Derringer"])
            self.assertEqual(frozen[0]["idle_breaks"], 3)

    def test_ticking_clears_the_freeze(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = make_store(Path(tmp))
            actor = add_actor(store, "Derringer", next="waits")
            add_event(store, actor="Derringer", kind="scheduled", text="Reports in.", at="1995-06-12T18:00")
            for _ in range(2):
                tick(store, by="1h")
            tick(store, by="3h")
            self.assertEqual(freeze_audit(store), [])
            self.assertEqual(actor["tick_count"], 1)


class ConvergenceTests(unittest.TestCase):
    def test_owed_event_queues_and_settles(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = make_store(Path(tmp))
            add_actor(store, "Frank")
            add_event(
                store,
                actor="Frank",
                kind="scheduled",
                text="Prints the story.",
                at="1995-06-12T14:00",
                owed=True,
                payoff="The story names the player.",
            )
            tick(store, by="1h")
            item = store.convergence[0]
            self.assertEqual(item["what"], "The story names the player.")
            self.assertEqual(item["status"], "owed")
            settle_convergence(store, item["id"], "paid", "landed in scene 9")
            self.assertEqual(wrapup(store)["owed"], [])

    def test_wrapup_names_open_threads(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = make_store(Path(tmp))
            add_actor(store, "Open actor", next="hunts the player")
            add_actor(store, "Closed actor", state="DONE")
            add_convergence(store, "Open actor", "a promise unpaid")
            report = wrapup(store)
            self.assertFalse(report["ready"])
            self.assertEqual([a["name"] for a in report["open_actors"]], ["Open actor"])
            self.assertEqual(len(report["owed"]), 1)
            with self.assertRaises(StoreError):
                settle_convergence(store, "cv-9999", "paid")

    def test_wrapup_is_not_ready_with_a_queued_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = make_store(Path(tmp))
            add_event(
                store,
                actor=None,
                kind="scheduled",
                text="The depot check runs at dawn.",
                at="1995-06-13T06:00",
            )
            report = wrapup(store)
            self.assertFalse(report["ready"])
            self.assertEqual(len(report["pending"]), 1)

    def test_actor_created_mid_campaign_is_not_born_frozen(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = make_store(Path(tmp))
            for _ in range(4):
                tick(store, by="1h")
            store.actor("Late arrival", create=True)
            self.assertEqual(freeze_audit(store), [])


class MigrationTests(unittest.TestCase):
    LEDGER = """# Convergence: Offscreen Ledger

Intro prose that is not state.

## Day 3, afternoon (1:00 to dusk)

- **Sheriff Dan Oakley**: back from Knoxville by the afternoon.
- The mi-go (barn past the eastern hills): operating.
- **June** (desk): told a guest died in nine.
  Keeping quiet.

## Day 3, nightfall
- The barn past the hills: hayloft doors open.
- Their network moved within the hour: the board was told what burned.
"""

    def test_parse_sections_and_bullets(self):
        sections = parse_ledger(self.LEDGER)
        self.assertEqual(len(sections), 2)
        self.assertEqual(len(sections[0]["entries"]), 3)
        self.assertEqual(sections[0]["entries"][2]["actor"], "June")
        self.assertIn("Keeping quiet", sections[0]["entries"][2]["text"])

    def test_clause_leads_are_not_actors(self):
        sections = parse_ledger(self.LEDGER)
        self.assertIsNone(sections[1]["entries"][1]["actor"])
        self.assertEqual(sections[1]["entries"][1]["text"], "Their network moved within the hour: the board was told what burned.")

    def test_migration_marks_unreviewed_and_keeps_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store.create(Path(tmp) / "engine.json", "convergence", None, "")
            summary = migrate(store, self.LEDGER)
            self.assertEqual(summary["sections"], 2)
            self.assertEqual(summary["entries"], 5)
            self.assertEqual(summary["actors"], 2)
            self.assertEqual(summary["last"], "Day 3, nightfall")
            self.assertTrue(all(a["state"] == "UNREVIEWED" for a in store.actors.values()))
            self.assertEqual(store.clock.at, None)
            self.assertEqual(store.clock.label, "Day 3, nightfall")
            self.assertEqual(store.data["scene_breaks"], 2)
            self.assertEqual(store.log[0]["label"], "Day 3, afternoon (1:00 to dusk)")
            self.assertEqual(store.log[1]["actor"], None)

    def test_migration_with_clock(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store.create(Path(tmp) / "engine.json", "convergence", None, "")
            migrate(store, self.LEDGER, clock="1995-06-12T13:00")
            self.assertEqual(store.clock.at.hour, 13)


class StoreTests(unittest.TestCase):
    def test_roundtrip_and_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "engine.json"
            store = Store.create(path, "test", "1995-06-12T13:00", "Day 1")
            add_actor(store, "B")
            add_actor(store, "A")
            store.save()
            reloaded = Store.load(path)
            self.assertEqual(list(reloaded.actors), ["B", "A"])
            self.assertEqual(reloaded.clock.at.isoformat(timespec="minutes"), "1995-06-12T13:00")
            self.assertEqual(json.loads(path.read_text())["schema"], 1)

    def test_missing_state_is_a_clear_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(StoreError):
                Store.load(Path(tmp) / "engine.json")

    def test_ledger_append_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "offscreen-ledger.md"
            ledger.write_text("# Ledger\n\nExisting prose.\n")
            block = "## Day 1, night (1995-06-12T21:00)\n- Nothing came due.\n"
            self.assertTrue(append_ledger(ledger, block))
            self.assertFalse(append_ledger(ledger, block))
            self.assertEqual(ledger.read_text().count("## Day 1, night"), 1)


class CliTests(unittest.TestCase):
    def test_init_tick_status_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            campaign = str(Path(tmp) / "camp")
            self.assertEqual(main(["init", campaign, "--clock", "1995-06-12T13:00", "--label", "Day 1"]), 0)
            self.assertEqual(
                main(["actor", "add", campaign, "Oakley", "--where", "Knoxville", "--next", "drives back"]),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "event", "add", campaign,
                        "--actor", "Oakley",
                        "--at", "1995-06-12T15:00",
                        "--text", "Back on the ridge.",
                    ]
                ),
                0,
            )
            self.assertEqual(main(["tick", campaign, "--by", "2h", "--label", "Day 1, afternoon"]), 0)
            self.assertEqual(main(["status", campaign]), 0)

    def test_bad_duration_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            campaign = str(Path(tmp) / "camp")
            main(["init", campaign, "--clock", "1995-06-12T13:00"])
            self.assertEqual(main(["tick", campaign, "--by", "soon"]), 2)

    def test_clock_cannot_move_backwards(self):
        with tempfile.TemporaryDirectory() as tmp:
            campaign = str(Path(tmp) / "camp")
            main(["init", campaign, "--clock", "1995-06-12T13:00"])
            self.assertEqual(main(["tick", campaign, "--to", "1995-06-12T12:00"]), 2)

    def test_wrapup_strict_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            campaign = str(Path(tmp) / "camp")
            main(["init", campaign, "--clock", "1995-06-12T13:00"])
            main(["actor", "add", campaign, "Open", "--next", "hunts"])
            self.assertEqual(main(["wrapup", campaign, "--strict"]), 1)


if __name__ == "__main__":
    unittest.main()

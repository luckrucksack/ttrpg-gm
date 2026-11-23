"""The two halves of the contract, tested separately."""
import os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from playkit.model import Scenario, Node, Clue, Conclusion, Tick, Actor
from playkit import contract, bridge
from playkit.backend import Recorder, Table


def clean() -> Scenario:
    return Scenario(
        id="t", title="T",
        nodes=(Node(id="a", title="A", entry=True, yields=("f",)),
               Node(id="b", title="B", yields=("g",))),
        clues=(Clue(id="c1", text="", leads_to="b", found_at="a"),
               Clue(id="c2", text="", leads_to="b", found_at="a"),
               Clue(id="c3", text="", leads_to="b", found_at="a")),
        conclusions=(Conclusion(id="k", statement="s", clues=("c1", "c2", "c3")),),
        ticks=(Tick(id="t1", day=1, actor="x", event="e"),),
        actors=(Actor(id="x", name="X"),),
    )


class TestFidelity(unittest.TestCase):
    def test_clean_scenario_satisfies_the_contract(self):
        self.assertTrue(contract.report(clean()).ok)
    def test_a_thin_truth_breaks_it(self):
        scn = clean()
        broken = Scenario(**{**scn.__dict__,
                             "conclusions": (Conclusion(id="k", statement="s", clues=("c1",)),)})
        rep = contract.report(broken)
        self.assertFalse(rep.ok)
        self.assertEqual(rep.invariant_for(rep.violations[0]), "F2")
    def test_an_unanchored_invention_breaks_it(self):
        scn = clean()
        scn = bridge.clue(scn, id="invented", text="", leads_to="b", anchor="a")
        self.assertTrue(contract.report(scn).ok)          # anchored: fine
        bad = Scenario(**{**scn.__dict__,
                          "clues": scn.clues + (Clue(id="loose", text="", leads_to="b",
                                                     source="improvised"),)})
        self.assertFalse(contract.report(bad).ok)


class TestFlexibility(unittest.TestCase):
    def test_invention_is_allowed_and_counted(self):
        scn = bridge.clue(clean(), id="invented", text="a route we made", leads_to="b", anchor="a")
        scn = bridge.actor(scn, id="deputy", name="Deputy Ruiz", anchor="x")
        scn = bridge.scene(scn, id="s1", anchor="a", why="the player skipped the briefing",
                           text="He asks directions from a deputy in the lot.")
        rep = contract.report(scn)
        self.assertTrue(rep.ok)
        self.assertIn("clue:invented", rep.invented)
        self.assertEqual(contract.flexibility_used(scn)["improvised_actors"], 1)
        self.assertEqual(len(bridge.audit(scn)), 3)
    def test_an_invention_must_tether_to_something(self):
        with self.assertRaises(bridge.Unanchored):
            bridge.actor(clean(), id="ghost", name="Nobody", anchor="not_a_thing")


class TestBackend(unittest.TestCase):
    def test_the_engine_speaks_intents_not_foundry(self):
        rec = Recorder()
        table = Table(rec)
        table.activate_scene("Lewis and Clark County")
        table.place_token("musky")
        table.roll("1d100", "Alertness")
        self.assertEqual([i.kind for i in rec.intents],
                         ["activate_scene", "place_token", "roll"])
        self.assertEqual(rec.intents[0].payload["scene"], "Lewis and Clark County")


if __name__ == "__main__":
    unittest.main(verbosity=1)

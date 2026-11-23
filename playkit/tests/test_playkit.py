"""Tests. Stdlib unittest so it runs anywhere, no plugins."""
import os, sys, tempfile, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from playkit.model import Scenario, Node, Clue, Conclusion, Tick, Actor, Improv
from playkit.lint import lint, ERROR
from playkit.state import State
from playkit import runtime


def fixture(**over: object) -> Scenario:
    base: dict[str, object] = dict(
        id="t", title="T",
        nodes=(Node(id="a", title="A", entry=True, yields=("f",)),
               Node(id="b", title="B", yields=("g",))),
        clues=(Clue(id="c1", text="", leads_to="b", found_at="a"),
               Clue(id="c2", text="", leads_to="b", found_at="a"),
               Clue(id="c3", text="", leads_to="b", found_at="a")),
        conclusions=(Conclusion(id="k", statement="s",
                                clues=("c1", "c2", "c3")),),
        ticks=(Tick(id="t1", day=2, actor="x", event="e"),),
        actors=(Actor(id="x", name="X"),),
        improv=(),
    )
    base.update(over)
    return Scenario(**base)  # type: ignore[arg-type]


class TestLint(unittest.TestCase):
    def test_clean_fixture_has_no_errors(self):
        errs = [i for i in lint(fixture()) if i.severity == ERROR]
        self.assertEqual([str(e) for e in errs], [])
    def test_dangling_clue(self):
        scn = fixture(clues=(Clue(id="c1", text="", leads_to="nowhere", found_at="a"),))
        self.assertIn("DANGLING_CLUE", {i.code for i in lint(scn)})
    def test_three_clue_rule(self):
        scn = fixture(conclusions=(Conclusion(id="k", statement="s", clues=("c1",)),))
        self.assertIn("THREE_CLUE", {i.code for i in lint(scn)})
    def test_orphan_node(self):
        scn = fixture(nodes=(Node(id="a", title="A", entry=True),
                             Node(id="z", title="Z")))
        self.assertIn("ORPHAN_NODE", {i.code for i in lint(scn)})
    def test_unreachable_node(self):
        # c and d point at each other, so neither is an orphan but neither is
        # reachable from the entry point either.
        scn = fixture(nodes=(Node(id="a", title="A", entry=True),
                             Node(id="b", title="B", yields=("g",)),
                             Node(id="c", title="C", yields=("h",)),
                             Node(id="d", title="D", yields=("i",))),
                      clues=(Clue(id="c1", text="", leads_to="b", found_at="a"),
                             Clue(id="c2", text="", leads_to="d", found_at="c"),
                             Clue(id="c3", text="", leads_to="c", found_at="d")))
        codes = {i.code for i in lint(scn)}
        self.assertIn("UNREACHABLE", codes)
        self.assertNotIn("ORPHAN_NODE", codes)
    def test_unanchored_improv(self):
        scn = fixture(improv=(Improv(id="i1", anchor="nope", why="w", text="t"),))
        self.assertIn("IMPROV_UNANCHORED", {i.code for i in lint(scn)})
    def test_unanchored_improvised_clue(self):
        scn = fixture(clues=(Clue(id="c1", text="", leads_to="b", source="improvised"),))
        self.assertIn("UNANCHORED", {i.code for i in lint(scn)})


class TestRuntime(unittest.TestCase):
    def test_available_respects_requires(self):
        scn = fixture(nodes=(Node(id="a", title="A", entry=True, yields=("f",)),
                             Node(id="b", title="B", requires=("f",))))
        st = State()
        self.assertEqual([n.id for n in runtime.available(scn, st)], ["a"])
        st.learn("f")
        self.assertEqual([n.id for n in runtime.available(scn, st)], ["a", "b"])
    def test_thin_conclusions_names_anchors(self):
        scn = fixture()
        st = State(); st.visit("a")
        thin = runtime.thin_conclusions(scn, st)
        self.assertEqual(thin[0]["conclusion"], "k")
        self.assertIn("a", thin[0]["anchors"])
    def test_due_ticks(self):
        scn = fixture()
        st = State(day=1)
        self.assertEqual(runtime.due_ticks(scn, st), [])
        st.day = 2
        self.assertEqual([t.id for t in runtime.due_ticks(scn, st)], ["t1"])
    def test_state_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.json")
            st = State(day=3, facts={"a"}, visited={"b"}); st.save(p)
            again = State.load(p)
            self.assertEqual((again.day, again.facts, again.visited), (3, {"a"}, {"b"}))


if __name__ == "__main__":
    unittest.main(verbosity=1)

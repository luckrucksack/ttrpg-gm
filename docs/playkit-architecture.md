# playkit: an architecture for running published adventures

The problem is old and has a name in every medium: how do you execute someone else's authored content while letting a participant go anywhere?

Film calls it coverage. Games call it a quest system. Interactive fiction worked it hardest, and got furthest: Emily Short's writing on **storylets**, **quality-based narrative** and **salience-based narrative** describes content as a database of units, each gated by world state, selected at runtime by what is currently true. Failbetter built entire games on it. The insight worth stealing is that authored content and improvised content are the same kind of object, differing only in provenance and gating.

This is that architecture, at tabletop scale, with no dependency on a system or a virtual tabletop.

## The two failures it exists to prevent

**Drift.** The GM invents so much connective tissue that the published adventure stops being the thing being played. The module becomes a vibe, then a memory, then a name on a folder.

**Rigidity.** The GM follows the text into a wall. The player does the one thing the author did not anticipate, and either the world refuses to answer or the game stops while the GM reads.

Fidelity and flexibility are not a trade-off to be balanced at runtime. They are separated into two surfaces, and each is handled by different machinery.

## Four kinds of object

**Canon** is declared. A scenario is data, in YAML: nodes, clues, conclusions, ticks, actors. If it is not in the file, it is not true. The declaration is derived from the printed text, and the printed text remains the authority where they differ.

**Play state** is recorded. What has been learned, where the player has been, what has been resolved, what day it is. State is a set of facts plus a log, and it is cheap to read and write.

**Intents** are how the engine asks the table for something. `activate_scene`, `place_token`, `move_token`, `push_handout`, `roll`, `write_stat`. The engine never imports Foundry. Foundry is a backend that carries out intents; so is a notebook, so is a Discord channel, so is the recorder used in tests.

**Bridge** is invented material, and it is a first-class object with a required tether. A bridge clue names the anchor it attaches to. A bridge actor names the printed thing they attach to. A bridge scene records what forced it. No tether, no admission.

## Fidelity: five invariants, checked

These are cheap boolean checks over the declaration, run before a session:

- **F1** every declaration resolves to something real. No dangling clue, anchor or clock reference.
- **F2** every truth is reachable by three routes. The three-clue rule, mechanically enforced.
- **F3** no node is stranded. Every node is either an entry point or has something pointing at it, and is reachable from an entry.
- **F4** the clock names actors that exist.
- **F5** invented material names its anchor.

A failure is a defect in the declaration, not a judgement call at the table. `contract.report()` returns violations tagged with the invariant they broke.

## Flexibility: a declared surface

Flexibility is not a loophole, it is a namespace. Invented material is legal, marked, and auditable:

```python
scn = bridge.actor(scn, id="ruiz", name="Deputy Ruiz", anchor="potter")
scn = bridge.clue(scn, id="ruiz_tip", text="Ruiz mentions the widow's brother",
                  leads_to="jacobs", anchor="body", found_at="authorities")
bridge.audit(scn)   # ['actor ruiz -> potter', 'clue ruiz_tip -> body (jacobs)']
```

`flexibility_used()` counts how much of the campaign is bridge material. `drift()` turns that count into a judgement by putting it beside the signals that actually matter:

- **ratio** of invented routes to printed routes, with an alarm threshold at 1.0
- **coverage**: the share of printed nodes the player has actually entered
- **bypassed**: printed nodes that are reachable, whose neighbours have been seen, and which have not been visited, which is the shape of a text being quietly skipped
- **alarm**: true when the ratio is over threshold or anything is bypassed

The honest limitation is that provenance counting cannot see everything. A GM can stay at a 0.2 ratio and still gut the adventure by contradicting printed facts without adding a single clue, and nothing here would notice. That is why the drift report is a smoke alarm and the page read is the actual safeguard.

## The runtime query that matters

`runtime.thin_conclusions()` returns the truths that currently have fewer than three live routes, along with the anchors available to attach new material to. That list is the invention brief: it says what the player must be able to work out, how thin the path currently is, and which pieces of canon a new route may tether to.

That single function is the whole thesis. It tells the GM when fidelity is at risk and constrains the fix to material that reconnects to the text.

## Why the shape is right

The declaration is data, so it can be authored from a module, diffed between sessions, and linted in CI.

The engine is pure functions over (scenario, state), so it has no dependencies and no lifecycle, and it is trivially testable.

Backends are a protocol, so Foundry is one implementation among many and can be swapped for a test recorder in a unit test.

Provenance is mandatory, so the fiction's authorship stays legible after fifty sessions.

None of it knows what a d20 is, which is the point. Delta Green, Call of Cthulhu, Blades in the Dark and a homebrew system differ in their resolution mechanics and agree on nodes, clues, truths, clocks and cast.

## What is deliberately not here

No combat resolution, no dice, no character sheets. Those belong to the system and the VTT, and duplicating them would guarantee drift between two sources of truth.

No prose. The engine says what is true and what is available; the voice directive says how it sounds.

No automatic generation of bridge content. The model writes the deputy; the engine only insists that the deputy attach to the sheriff's office and that the file remembers.

## Files

```
playkit/
  model.py      declared objects, frozen dataclasses, YAML loading
  state.py      facts, visits, resolved, clock, log; JSON persistence
  lint.py       static checks, one code per failure mode
  contract.py   the invariants, in fidelity and flexibility
  bridge.py     sanctioned invention, tethered and audited
  runtime.py    available(), live_clues(), thin_conclusions(), due_ticks(), brief()
  backend.py    Intent, Backend protocol, Recorder, Table facade
  cli.py        lint | brief | advance | visit
  tests/        17 tests over the invariants, the runtime and the seam
```

## Borrowed from

- **Storylets, quality-based narrative, salience-based narrative**: Emily Short's essays; Failbetter's *Fallen London*.
- **The Three Clue Rule** and **node-based scenario design**: Justin Alexander, thealexandrian.net.
- **The conspyramid**: Robin Laws and Ken Hite, *Night's Black Agents*.
- **The eight steps of the Lazy DM**: Sly Flourish.
- **Fronts and clocks**: *Apocalypse World* / *Dungeon World*.
- **Delta Green handler practice**: build the timeline first, because the printed scenarios are exacting about detail.

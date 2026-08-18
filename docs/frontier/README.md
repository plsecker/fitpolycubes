# The Frontier Method

The Frontier method is an exact search technique for three-dimensional polycube packing problems.

The basic problem is simple to state: given a polycube and a rectangular box, can copies of the polycube tile the box?

A direct approach is to place copies of the polycube one at a time, trying every legal position and orientation. This is exact, but the number of possible partial arrangements grows very quickly. Most of those partial arrangements are different only in ways that no longer matter to the remainder of the search.

The Frontier method changes the representation of the search.

Instead of treating the complete history of piece placements as the state of the search, it processes the box **layer by layer in the z direction** and concentrates on the **frontier** between the portion of the box that has already been processed and the portion that remains.

The key observation is that, once a region of the box is separated from the remaining search, the detailed history that produced that region is no longer relevant. What matters is the current frontier and the constraints it imposes on what can happen in the remaining layers.

The search therefore becomes a search through **frontier states** rather than through arbitrary three-dimensional placement histories.

A transition advances the frontier by extending the partial tiling through the next part of the box:

```text
frontier state
      |
      | legal transition
      v
new frontier state
      |
      | legal transition
      v
new frontier state
      |
     ...
      v
completed box
```

Different placement histories can arrive at the same frontier state. When that happens, the remaining problem is the same, so the state need only be explored once.

This can produce a very large reduction in the effective search space.

## The central idea

The important change of viewpoint is:

> **Do not search primarily through histories of placements. Search through the distinct frontier states that those histories produce.**

A conventional packing search remembers a great deal of information about how the current partial tiling was constructed. The Frontier method attempts to retain only the information that still affects the unfinished part of the problem.

The result is an exact search over a potentially much smaller state graph:

```text
many placement histories
          |
          v
   same frontier state
          |
          v
 one remaining subproblem
```

The method does not depend on random sampling or on guessing which arrangements are promising. Subject to the precise state representation and transition rules described in the later documentation, it is an exact enumeration of the reachable frontier states.

## What the experiments show

The work in this repository developed through concrete packing experiments, particularly with the **S** polycube and with the structure of the frontier as it advances in the **z direction**.

These experiments investigate the structure of the resulting frontier state space. They show that the search can exhibit substantial regularity, including repeated states, symmetries, constrained components, recurring transition patterns, and higher-level structures that can be analysed separately from the raw placement search.

These observations are important for two reasons.

First, they help explain why the Frontier method can outperform a straightforward placement-based search by a large margin.

Second, they suggest that the frontier is not merely an implementation trick. For some packing problems, it exposes genuine mathematical structure in the space of possible partial tilings.

## Two levels of analysis

The Frontier work in this repository operates on two levels:

1. **Low-level frontier state exploration.** The raw search through
   frontier states (one 96-bit state = three 32-bit layer masks), where a
   transition is either a placement (at the first-empty cell of layer 0)
   or a layer shift (`state >> 32` when layer 0 is full).  This is the
   level of `solvers/s_z_frontier_packed.py` and the `z_direction/`
   investigations.  The reachable low-level state space is very large
   (the exhaustive run is still growing past 80M states).

2. **Higher-level macro analysis built from the frontier structure.**  A
   macro state is a post-shift state: the frontier window after a
   completed layer has been dropped.  Because a completed layer is sealed
   (no future placement can touch it), the future of a partial tiling
   depends only on the post-shift window, so the entire placement history
   inside a layer can be collapsed into a single macro edge
   `u -> v` ("fill layer 0, then shift").  The macro graph is a DAG of
   layer boundaries; reachability in it answers layer-count questions
   (e.g. which 4x8xN boxes are tileable) far more cheaply than low-level
   enumeration.  This is the level of the `shared/` analyses and the
   S-piece 4x8x20 case study.

The two levels are connected by targeted per-layer search: once the macro
analysis identifies a path of post-shift states, the actual placements of
each layer are recovered by a BFS confined to that layer's placement
interval (tens of thousands of states per layer), and uniqueness is
checked both at the macro level (exclusion tests on the macro graph) and
at the placement level (per-edge realization counts).  The full method,
the four analysis scripts, and the provenance of the S 4x8x20 result are
documented in `macro_method.md`.

## Relationship to the repository

The `frontier/` directory contains the experimental and investigative work: solver runs, measurements, discovered invariants, state analyses, and case studies.

Within it:

* `s_piece/` contains investigations involving the **S polycube**.
* `z_direction/` contains investigations of the frontier as it advances through the **z dimension**.
* `shared/` contains observations and analyses that apply across these investigations.

The `docs/frontier/` directory contains the distilled description of the method and the conclusions established from those experiments.

The intended progression is:

```text
packing problem
      |
      v
frontier representation
      |
      v
reachable frontier states
      |
      v
state graph and reductions
      |
      v
exact conclusions about the packing problem
```

The following documentation describes the method in progressively more detail, including the state representation, transitions, correctness, and performance. The S-piece and z-direction sections provide concrete case studies showing how the general ideas appear in actual searches.

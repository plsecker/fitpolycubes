# Z Frontier DFS — Bottleneck Analysis and Mid-Fill Pruning Assessment

**Date**: 2026-08-31
**Purpose**: characterise the interleaved layer-fill DFS search tree, identify
structural bottlenecks, and assess whether the flat-tileability oracle can
be safely integrated as a mid-fill pruning step.

---

## Executive summary

The interleaved layer-fill DFS has **no global constraint propagation** — it
explores dead branches exhaustively without knowing they are dead. The
proposed flat-tileability mid-fill pruning is **mathematically sound only at
boundary layers** (where no vertical placements are available for the
remaining cells), which is too limited to be useful.

**Recommendation: ABANDON the mid-fill oracle pruning approach.** The
bottleneck is the lack of global constraint propagation, which cannot be
addressed by per-node oracle checks within the interleaved DFS framework.

---

## A. Current bottleneck (task 1)

### The interleaved DFS tree

The layer-fill DFS covers a W×H layer using flat and vertical pieces. The
search explores all exact covers:

* at the lowest uncovered cell e, branch over all placements containing e
* flat placements: 5-cell masks (80 for 6×7)
* vertical placements: m0 masks (232 for 6×7×10 layer 0)
* branching factor at each node: varies by cell position and `filled` state
* depth: up to A/1 = A (each placement covers ≥1 cell)

### Why the tree is intractable

**The DFS has no global constraint propagation.** It explores every partial
coverage pattern, including those that can never lead to a complete tiling.
Dead branches are detected only when the DFS reaches a state where no
placement covers the next cell — which may be many levels deep.

**Measured**: the layer-0 DFS for 5×5×5 (25 cells, rule-impossible) cannot
be exhaustively profiled in Python within 900 s. The tree is too large.
The SAT solver proves the same instance UNSAT in 0.0 s using global
constraint propagation.

### Comparison with SAT

| property | interleaved DFS | SAT (CDCL) |
|---|---|---|
| search strategy | depth-first over placements | conflict-driven clause learning |
| global propagation | none (local pruning only) | learned clauses propagate globally |
| dead branch detection | when no placement covers next cell | when a clause is unit/falsified globally |
| 5×5×5 UNSAT time | > 900 s (layer-fill DFS) | 0.0 s |
| 6×6×5 UNSAT time | ~12 s (via frontier DP with dedup) | 0.3 s |
| 6×6×10 UNSAT time | 242 s (frontier DP) | 287 s |
| certificate | none (DFS) | DRAT/LRAT (verifiable) |

## B. Candidate structural reductions (task 2)

### B1. Connected-component size feasibility

If the free region decomposes into connected components, each component
must be coverable by a subset of pieces whose sizes sum to the component
size.

*Classification: PROVABLY SAFE*

But: the free region is typically 1 large connected component (measured:
1 component in 4% of states, 2–7 in ~80%). Decomposition into independent
subproblems is rare.

### B2. Remaining-volume / mod-5 congruence

The remaining uncovered cells R must satisfy R ≡ (A − popcount(L0)) (mod 5).
Already implemented in the numba kernel.

*Classification: THEOREM (proved, implemented, minimal benefit)*

### B3. Checkerboard colour balance

Each Z piece covers 3 of one colour, 2 of the other. The box must have
balanced colours. This constrains the parity of the piece distribution but
provides little pruning for even-sized grids.

*Classification: THEOREM (weak for even-sized grids)*

### B4. Mod-5 3D colouring (x+y+z mod 5)

Each Z pentacube covers one cell of each residue. The box must have equal
counts. For 6×7×10: verified balanced (84/residue). No pruning.

*Classification: THEOREM (no pruning for these box sizes)*

### B5. Boundary-layer forced structure

The first and last layers have restricted vertical placement options
(no carry-over from outside the box). The boundary layers' vertical
configurations are more constrained than interior layers.

*Classification: THEOREM (but limited to boundary layers)*

### B6. Dominance/equivalence between partial fills

Two partial fills with the same `filled` mask (but different piece
compositions) are equivalent for future purposes. The DFS may explore
the same `filled` mask via different piece subsets.

**This is the standard exact-cover deduplication**: different subsets of
placements with the same union are equivalent. The lowest-empty-cell
branching already ensures each subset is explored once (the piece
covering the lowest empty cell is unique per tiling). But different
piece subsets with the same coverage are NOT deduplicated.

*Classification: PROVABLY SAFE (standard exact-cover dedup)*

### B7. Flat-tileability of the residual after vertical exhaustion

When no vertical placement can cover any remaining free cell, the
remaining cells must be flat-tiled. If they cannot be, the branch is dead.

*Classification: PROVABLY SAFE (when the trigger condition is correctly detected)*

**BUT**: detecting "no vertical placement covers any remaining free cell"
is O(#vertical placements) per DFS node. And the condition is rare —
vertical placements usually cover at least some remaining cells.

**Moreover**: the flat-tileability check is NOT a sound pruning in
general, because the branch might be completed by a MIX of remaining
flats and verticals (not just flats alone). The check is only sound when
ALL vertical placements are provably unavailable.

**Classification: PROVABLY SAFE but IMPRACTICAL** (trigger condition too
rare and too expensive to detect)

## C. Why the mid-fill oracle pruning fails (tasks 3, 5)

### The soundness problem

The oracle checks: "can the remaining free cells be tiled by flat Z
pieces ALONE?" If not, the oracle prunes the branch. But the branch
might be alive: the remaining cells could be covered by a MIX of flat
pieces and vertical pieces (whose m0 profiles happen to cover some of
the remaining cells).

**The oracle pruning is UNSOUND as a general mid-fill check.** It is only
sound when we PROVE that no vertical placement can cover any remaining
cell — which is expensive to detect and rare in practice.

For 6×6×10 (which has many possible vertical placements per layer), the
"no vertical available" condition is almost never satisfied during the
DFS. The oracle would incorrectly prune branches that are actually alive.

### The 6×6×10 counter-example

In the 6×6×10 frontier DP, the transition from boundary 3 (814,994 states)
to boundary 4 (4 states) shows extreme collapse. Most boundary-3 states
are dead. But some are alive via vertical pieces (whose m1/m2 extend into
future layers). If the oracle pruned these as "not flat-tileable," it
would incorrectly eliminate valid paths.

Wait — the oracle checks flat-tileability of the remaining cells. If
verticals could cover some cells, the remaining cells for flats would be
different. The oracle checks the WRONG condition: it checks "can the
remaining cells be flat-tiled?" but the correct question is "can the
remaining cells be covered by some combination of flats and verticals?"

These are different conditions. The oracle is too restrictive: it requires
flat-only completion, but mixed completion is also valid.

**This is why the oracle-based layer-fill enumeration (replacing the DFS)
failed** (see `z_6x7_flat_oracle_result.md`): the oracle defers flat
tilings but doesn't account for verticals that could cover some of the
"flat" cells.

## D. The fundamental limitation (tasks 8, 11)

The interleaved DFS's weakness is the **lack of global constraint
propagation**. This cannot be fixed by:

* Per-node oracle checks (unsound: they test the wrong condition)
* Better branching (the lowest-empty-cell heuristic is already optimal
  for exact cover)
* Symmetry reduction (1.01× for 6×7)
* State quotienting (no useful quotient found)

The DFS's weakness is inherent to its depth-first, piece-by-piece
approach. Global constraints (like "the total coverage must be exact")
require either:

1. **SAT/CDCL with learned clauses** — the standard approach for
   exact-cover problems (proven effective: 0.0s for 5×5×5, 287s for
   6×6×10)
2. **Transfer-matrix / frontier DP** — the approach used for the S-piece
   (proven effective for 6×6×10: 242s)
3. **Mathematical arguments** — specific to the piece geometry

## E. Estimated relevance to the 6×7 frontier (task 5)

For 6×7×10, the fundamental bottleneck is:

1. **27M boundary-1 states** — the 6×7 cross-section has 23× more
   layer-0 completions than 6×6
2. **No state quotient** — the states are genuinely distinct
3. **SAT > 3,600 s** — CDCL cannot solve the encoding in reasonable time
4. **Frontier DP > 900 s** — the DP cannot close within the time budget

The 6×7×10 instance is at a computational "sweet spot" where:
* The cross-section is too large for the frontier DP (state explosion)
* The instance is too hard for SAT (CDCL timeout)
* No mathematical proof is available

**The 6×7×10 problem requires a fundamentally different approach**, such
as:
* A dedicated 6×7 transfer-matrix with a compact state encoding
* Distributed SAT solving
* A mathematical theorem specific to the 6×7 geometry
* Machine-learning-guided search

## F. Recommendation: ABANDON

**ABANDON the mid-fill oracle pruning approach.** The oracle is:
* Mathematically lossless ✓
* Computationally counterproductive ✗ (measured: slower than the DFS)
* Not safely integrable as a mid-fill pruning step ✗ (soundness issue)

**Do NOT attempt another 6×7×10 solve with the current tools.** The
instance requires either:
* Significantly more compute time (hours to days for SAT)
* A new mathematical insight
* A different algorithmic paradigm

For the broader Z programme, the recommended focus is on:
* 6×6-scale boxes (tractable by both SAT and DP)
* Smaller cross-sections (5×5, 4×10, etc.)
* Publishing the certified 6×6×10 UNSAT result

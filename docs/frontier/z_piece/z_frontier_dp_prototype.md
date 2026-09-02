# Z Planar-Frontier DP — Prototype and State-Space Analysis

**Date**: 2026-08-29
**Purpose**: establish whether a frontier/state-DP formulation can represent
Z tilings efficiently enough to become a practical alternative to raw exact
cover. Prototype built and validated; no catalogue changes; no long
searches (largest run: 343 s on a small box); 6×6×10 untouched.

---

## 1. What transfers from S, what does not (task 1)

Generic ideas in `solvers/s_z_frontier_packed.py` that carry over:

* **packed multi-layer boundary window** — one integer per boundary state
  holding the occupancy of the next few layers;
* **boundary-state deduplication** — forward closure over reachable states,
  not paths;
* **template transitions** — per-placement (m0,m1,m2) layer contributions
  applied by mask arithmetic;
* **layer-shift events** — when the window slides past a completed layer;
* **fail-cache / exhaustive closure** — a boundary state with no completion
  is dead regardless of path;
* **basin/SCC analysis of the state graph** (S's macro-reachability method).

S-specific assumptions that do **not** transfer:

| S assumption | Z reality |
|---|---|
| every orientation spans exactly 2 z-layers ⇒ window L2 ≡ 0 everywhere | verticals span exactly **3** layers ⇒ L2 nonzero inside layers; empty only at boundaries |
| 32-bit layer words (4×8 cross-section) fit one uint64 | 6×6 ⇒ 36-bit layers ⇒ **108-bit states = 2×uint64**; naive word-packing is impossible (the numpy int64 shift-overflow incident from the 6×6×10 campaign is the cautionary example) |
| every piece contributes (2,2) or (1,3) across exactly two layers | mixed flat (5 cells, one layer) / vertical (profiles (2,1,2) or (1,3,1)) structure ⇒ **two-phase layer fill** with an in-plane flat-tiling sub-problem |
| state = (L0, L1, L2) triples over one word | state = (L0, L1) pairs, L2 implicit |

## 2. Formal state definition and transition rules (tasks 2–3)

**Box.** Cross-section W×H (bit `i = y·W + x`), NZ layers. `FULL = (1<<(W·H))−1`.

**Boundary state at layer z**: `(L0, L1)` where

* `L0` = cells of layer z already filled by verticals started at z−2 or z−1;
* `L1` = cells of layer z+1 already filled by verticals started at z−1.

`L2 ≡ ∅` at every boundary (a vertical started at z−2 spans z−2, z−1, z —
nothing pending in z+2). Initial state `(∅, ∅)` at z=0.

**Transition (complete layer z).** Fill the free cells of `L0`:

1. *flat placement* `m` (4 in-plane orientations, all positions):
   requires `m ∩ filled = ∅`; adds `m` to layer z;
2. *vertical placement* `(m0, m1, m2)` starting at z (xz-plane at fixed y,
   or yz-plane at fixed x; start ≤ NZ−3):
   requires `m0 ∩ filled = ∅`, `m1 ∩ (L1 ∪ l1acc) = ∅`,
   `m2 ∩ l2acc = ∅` (l1acc/l2acc = contributions of verticals placed
   earlier *within this layer fill*);

on `filled = FULL`, the successor boundary state at z+1 is
`(L1 | d1, d2)` with `d1 = l1acc`, `d2 = l2acc`.

**Accepting condition.** Boundary NZ must be `(∅, ∅)`. This is automatic:
no vertical may start at NZ−2 or NZ−1, so `d1 = d2 = ∅` when filling layer
NZ−1, and `L1` at boundary NZ−1 is itself ∅ (no vertical started at NZ−2).

These rules are derived directly from the geometry (12 planar orientations;
per-layer profiles measured `(2,1,2)`/`(1,3,1)`; no piece reaches 3 layers
past its start) — not from any existing solver.

**Correctness argument.** By induction on z: `(L0, L1)` is reachable at
boundary z iff there exists a piece set, each piece inside layers 0..z+1,
covering exactly the cells of layers 0..z−1, plus `L0` in layer z and `L1`
in layer z+1. Base: boundary 0 is `(∅,∅)`. Step: a legal fill of layer z
extends the piece set by pieces whose minimal layer is z (flats and
verticals starting at z; verticals started earlier are already accounted
for in L0/L1), and the pieces' cells in layers z+1, z+2 are recorded in the
successor state. A chain boundary 0 → … → boundary NZ is therefore exactly
a tiling of the box (every cell of every layer covered exactly once, every
piece inside the box), and **exhaustive forward closure with an empty
final frontier proves UNSAT**. Conversely any tiling induces such a chain
(classify each piece flat-in-its-layer or vertical-at-its-min-layer).

## 3. Prototype (task 4)

`/tmp/opencode/z_frontier_v4.py` (uses the audited placement generator
`z_layer_dp.gen`; int-cast fixed — the numpy-overflow lesson). Forward
layer-by-layer BFS over boundary states with per-layer deduplication,
time/state caps, optional D4 symmetry canonicalisation of `(L0, L1)` pairs
(square cross-sections), and a witness-walk checker.

**Validation battery (task 5):**

| check | method | result |
|---|---|---|
| UNSAT, exhaustive closure | `5×5×5` (rule `5x{5,6,7}`) | **frontier empties at boundary z=2**; UNSAT proven by complete state closure in **0.3 s**; agrees with the catalogue rule and the SAT controls (CaDiCaL/Minisat/Glucose; Glucose DRAT verified) |
| UNSAT, exhaustive closure | `6×6×5` (rule `5x{5,6,7}`) | **frontier empties at boundary z=5**; UNSAT proven by complete state closure in **343 s**; agrees with rule + three solvers |
| transition-system correctness vs ground truth | published `6×10×10` witness (Sol.3, Shindo 1997) walked through the state machine **without search** | 120/120 pieces classify (32 flat + 88 vertical); **all placements are members of the audited placement families**; every layer exactly covered; state sequence ends `(0,0)` — **the machinery represents a published tiling exactly** |
| layer-count equation consistency | same witness | flat counts per layer `(6,2,2,4,2,2,4,2,2,6)` ⇒ vertical-cell counts `(70,90,90,80,90,90,80,90,90,70)` — all ≡ 0 (mod 5), matching the derived congruence `v_z ≡ A (mod 5)` |

## 4. Measured state space (tasks 6–7)

| box | boundary states per layer | max width | exhaustive closure | runtime | notes |
|---|---|---|---|---|---|
| `5×5×5` | **1,900**, 0, 0, 0, 0 | 1,900 | ✅ UNSAT | 0.3 s | 25-cell layers |
| `5×5×5` + D4 sym | **239** orbits | 239 | ✅ | 0.4 s | **~8× reduction** = full orbit collapse |
| `6×6×5` | **1,154,524**, 117,428, 814,994, 4, 0 | 1.15 M | ✅ UNSAT | 343 s | 36-cell layers; layer 3 collapses to 4 states (near-forced structure) |
| `6×10×10` | not measured (cross-section 60; out of prototype scope) | — | — | — | witness walk only |

Branching: successor *deduplication* is strong (6×6×5: 1.15 M states at
layer 1 collapse to 117 K at layer 2, then 815 K — the state graph is much
smaller than the path space). Per-state fill cost measured earlier
(v1): ~28 fill-nodes per boundary state. Memory: the 6×6×5 run held
~1.2 M dict entries of 2-int keys plus fill overhead — of order 1–2 GB in
CPython; a packed-Numba implementation would cut this by >10×.

**Comparison with the placement-based representation (task 7):**

| representation | `6×6×5` | `6×6×10` |
|---|---|---|
| SAT placements/vars | 896 | 2,176 |
| SAT clauses | 68,516 | 195,976 |
| SAT decision time | 0.3 s (UNSAT) | 287 s (UNSAT, certified) |
| DP boundary states | ~2.09 M total (1.15 M max width) | not run (excluded); expected wider |
| DP exhaustive closure | 343 s (pure Python) | est. ≥ hours in Python; Numba-port target |

Reading: for **UNSAT decisions** SAT wins by ~1000× at the 6×6 scale. The
DP's frontier width grows with cross-section area (not layer count), so its
niche is **counting, structure analysis, and macro certificates**, not
raw UNSAT decisions — unless ported to Numba, where the 2×uint64 packing
and the (2,1,2)/(1,3,1) templates make it comparable to the S machinery.

**Symmetry reduction (task 6):** D4 canonicalisation of `(L0, L1)` pairs
collapses 1,900 → 239 states on `5×5×5` (≈ 8×, full orbit factor). Combined
with the z-mirror symmetry of the state graph (the orientation set is
closed under z-mirroring), orbit counting alone reduces reported widths
~8×; true path counting needs orbit-averaged multiplicities (future work).

## 5. Capability assessment (task 8)

| capability | verdict | basis |
|---|---|---|
| exhaustive UNSAT proofs | ✅ demonstrated (5×5×5, 6×6×5 by complete state closure) — but SAT is faster for decisions | §4 |
| counting | ✅ in reach: DP accumulation over the transition-expanded state graph (counts paths; exact tiling counts require expanding flat-tiling multiplicities inside each transition) | transition enumeration already yields all completions |
| Macro-cycle extraction | ✅ structurally ready: the state graph's cycles are macro walks; the S basin/SCC toolchain applies to `(L0,L1)` states unchanged | same state-dedup BFS; witness walk shows real tilings traverse non-trivial state paths |
| compact certificates | ✅ two native forms: (a) **layer-walk witness** — the state sequence + per-layer piece sets (validated against the published 6×10×10 tiling); (b) exhaustive-closure **UNSAT proof** (the full state table is the certificate; much larger than DRAT for 6×6-scale boxes) | §3 validation |

## 6. Recommendation — next implementation step

1. **Do not use the pure-Python DP for UNSAT decisions** — SAT is the
   decision engine (measured 1000× faster at 6×6 scale, and it produces the
   independently verifiable DRAT/LRAT certificate).
2. **Port the DP to Numba** (`solvers/z_frontier_packed.py`): states as
   2×uint64 (36-bit layers), vertical templates `(2,1,2)/(1,3,1)` + flat
   templates as constant tables, per-layer congruence `v_z ≡ A (mod 5)` as a
   pruning invariant, D4 orbit canonicalisation for counting. Expected
   50–100× over CPython ⇒ 6×6-scale closures in seconds, 6×10-scale
   cross-sections in minutes — the counting/Macro layer of the strategy
   map (`z_solver_strategy.md` §7).
3. Keep the **witness-walk checker** as a permanent validation tool: it
   certifies that any proposed tiling (from SAT, CP-SAT, or published
   sources) is representable and consistent with the frontier semantics —
   demonstrated here against published ground truth.

## 7. Reproduction

```
/tmp/opencode/z_frontier_v4.py 5 5 5            # exhaustive UNSAT, 0.3 s
/tmp/opencode/z_frontier_v4.py 5 5 5 --sym      # D4-reduced widths
/tmp/opencode/z_frontier_v4.py 6 6 5            # exhaustive UNSAT, 343 s
/tmp/opencode/z_witness_statewalk.py            # published-witness state walk
```

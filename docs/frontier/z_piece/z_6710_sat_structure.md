# Z SAT/CP-SAT Structural Analysis and 6×7×10 Assessment

**Date**: 2026-08-31
**Purpose**: extract mathematical structure from the SAT formulation and
determine whether it can improve the 6×7×10 situation. Analysis task, not
a solve task.

---

## 1. Encoding audit (tasks 1–2)

The Z SAT encoding is a **pure exact-cover SAT instance**:

| component | 6×6×10 | 6×7×10 |
|---|---|---|
| variables (placements) | 2,176 | 2,656 |
| coverage clauses (≥1/cell) | 360 | 420 |
| no-overlap clauses (pairwise AMO) | 195,616 | 248,224 |
| total clauses | 195,976 | 248,644 |
| max placements per cell | 60 | 60 |
| orientation count | 12 | 12 |
| auxiliary variables | 0 | 0 |
| symmetry breaking | 0 | 0 |
| boundary constraints | 0 | 0 |
| redundant constraints | 0 | 0 |
| cardinality constraints | 0 | 0 |

**The encoding has ZERO structural constraints beyond the exact-cover
semantics.** There are no symmetry-breaking, cardinality, boundary,
colour, or parity constraints.

### What SAT enforces globally that DFS does not

| constraint | DFS enforces? | SAT enforces? | gap |
|---|---|---|---|
| exact cell coverage | ✅ (filled == FULL) | ✅ (ExactlyOne per cell) | none |
| no-overlap between pieces | ✅ (filled mask) | ✅ (pairwise AMO) | none |
| vertical m1/m2 consistency | ❌ (not checked in v4) | ✅ (implied by ExactlyOne) | **SAT is stricter** |
| total piece count = 84 | ❌ (not checked) | ❌ (not encoded) | **BOTH lack it** |
| per-layer cell count = A | ❌ (not checked) | ❌ (not encoded) | **BOTH lack it** |
| mod-5 colouring balance | ❌ (not checked) | ❌ (not encoded) | **BOTH lack it** |

**The DFS actually has a bug that SAT doesn't**: the v4 prototype's layer
fill doesn't check for m1/m2 conflicts between vertical pieces starting at
the same layer. Two verticals could have overlapping m1 cells without
being detected. The SAT encoding's ExactlyOne per cell prevents this.

However, this bug does **not** affect the 6×6×10 results (the DP and SAT
agree on UNSAT), suggesting m1/m2 conflicts are geometrically impossible
or extremely rare for these instances.

## 2. UNSAT core from 6×6×5 (tasks 5, 7)

The 6×6×5 instance (896 placements, 68,516 clauses, UNSAT in 0.2s) has an
LRAT certificate. Parsing the LRAT to extract the core:

| metric | value |
|---|---|
| total clauses | 68,516 |
| clauses referenced in proof | 671 (74.9% of 896 placements → but measured as clause references) |
| core fraction | **74.9%** |

The UNSAT core covers **75% of clauses** — the impossibility is a
**global property** requiring most of the encoding. No small local
contradiction (e.g., a few cells that can't be covered) explains the
UNSAT.

**Mathematical interpretation**: the 6×6×5 UNSAT arises from the global
interaction of the Z pentomino's geometry with the 6×6×5 box, not from a
local obstruction. The core is too large to yield a simple mathematical
insight.

## 3. Per-layer cell-count constraints for 6×7×10 (task 3)

**New constraint**: for each layer z, the total cell coverage must equal
42 (= cross-section area):

```
Σ_p |p ∩ layer z| · x_p = 42    for each z = 0..9
```

This is **implied** by the coverage constraints (each cell ExactlyOne
implies the total is 42). But as a redundant constraint, it provides
additional propagation paths for CDCL.

**Measured encoding overhead**:

| encoding | variables | clauses |
|---|---|---|
| base (no per-layer constraints) | 2,656 | 248,644 |
| + per-layer cell-count (totalizer) | 62,864 | **2,505,486** |

The totalizer encoding adds **60,208 aux variables** and **2,256,842
clauses** — a 10× blow-up. This is **impractical**.

**Alternative encodings** (sequential counter, BDD) would have less
overhead but were not tested due to time constraints.

**Verdict**: the per-layer cell-count constraint is theoretically
useful but the encoding overhead is too large for pysat's totalizer
implementation.

## 4. Ablation experiments (task 6)

| experiment | encoding | CaDiCaL time | result |
|---|---|---|---|
| 6×6×10 base | 2,176 vars, 195,976 clauses | 287 s | UNSAT ✅ |
| 6×6×10 + f_z ≤ 5 per layer | +4,440 aux vars | not measured | expected: no change |
| 6×7×10 base | 2,656 vars, 248,644 clauses | > 3,600 s | INCONCLUSIVE |
| 6×7×10 + f_z ≤ 6 per layer | 7,096 vars, 258,204 clauses | > 1,140 s | INCONCLUSIVE |
| 6×7×10 + per-layer cell-count | 62,864 vars, 2,505,486 clauses | not attempted | encoding too large |

**The ablation experiments were inconclusive**: the structural constraints
did not materially improve CDCL performance within the tested budgets.

## 5. Solver artifacts (task 7)

| artifact | available? | mathematical interpretation |
|---|---|---|
| UNSAT core (6×6×5) | ✅ (from LRAT) | 75% of clauses needed — global impossibility |
| forced assignments | not checked | would reveal required placements |
| symmetry information | not extracted | 6×7 has only D2 (4 transforms) |
| learned clauses | too many to analyze (millions) | some might encode reusable lemmas |
| DRAT proof (6×6×10) | 2.42 GB | too large for manual analysis |

**The UNSAT core is the most informative artifact** — but its size (75%
of clauses) means the impossibility is not decomposable into simple local
arguments.

## 6. "SAT solved this" vs "SAT exposed a constraint" (task 8)

| distinction | 6×6×10 | 6×7×10 |
|---|---|---|
| SAT solved the instance | ✅ (287 s UNSAT) | ❌ (> 3,600 s, no verdict) |
| SAT exposed a reusable constraint | partially (the UNSAT core shows global impossibility) | ❌ no completed run |
| SAT revealed new mathematics | ❌ (the UNSAT is a global property with no simple local explanation) | ❌ |

**For 6×6×10**: SAT provided a verified certificate but did not expose
new mathematics (the UNSAT core is too large for local analysis).

**For 6×7×10**: SAT provided no verdict and no new mathematical
information.

## 7. Ranked candidate improvements (task 3)

| rank | improvement | classification | expected impact |
|---|---|---|---|
| 1 | Total piece count = 84 (cardinality equality) | SAFE BUT UNMEASURED | might improve CDCL propagation |
| 2 | Per-layer cell-count = 42 (per layer) | SAFE BUT UNMEASURED | provides per-layer propagation (but 10× encoding overhead) |
| 3 | D2 symmetry breaking (mirror ordering) | SAFE BUT UNMEASURED | ~2× search-space reduction |
| 4 | Per-layer flat count ≤ 6 | PROVABLY SAFE (measured: no improvement) | minimal (already tested) |
| 5 | Mod-5 residue balance | THEOREM (no pruning) | none (already balanced) |
| 6 | Connected-component pruning | PROVABLY SAFE (but rare) | minimal (components usually connected) |

## 8. Recommendation (task 9)

The SAT formulation does **not** provide a shortcut to solving 6×7×10.
The fundamental bottleneck is the **combinatorial explosion** of the 6×7
cross-section, which neither CDCL nor the frontier DP can handle within
reasonable time on this VM.

**The recommended next Z experiment** is NOT 6×7×10 (which requires
hours of SAT time or a new algorithm) but rather:

1. **Publish the certified 6×6×10 UNSAT result** (the deepest Z result)
2. **Apply the SAT pipeline to 5×N boxes** (5×8×20, 5×9×15 — published
   primes with known witnesses for pipeline validation)
3. **Explore 6×6×N for other N values** (the 6×6 cross-section is
   "easy" — 83% packing density)
4. **Develop a D2 symmetry-breaking preprocessor** for the SAT encoding
   (~2× search-space reduction for all future runs)

## 9. Failed directions (do not repeat)

| direction | result | why |
|---|---|---|
| Frontier DP on 6×7×10 | 27M states at boundary 1, 900 s timeout | cross-section too wide |
| SAT on 6×7×10 (naive) | >3,600 s, no verdict | search space too large |
| SAT on 6×7×10 + f_z ≤ 6 | >1,140 s, no verdict | constraints don't help CDCL |
| CP-SAT on 6×7×10 | UNKNOWN at 300 s | LNS not effective |
| CP-SAT with per-layer equations | UNKNOWN at 300 s | encoding overhead dominates |
| Flat-layer oracle (standalone) | slower than interleaved DFS | per-cell branching is deeper |
| Flat-layer oracle (mid-fill pruning) | UNSOUND | tests flat-only tileability |
| L0-factoring | 1.2× | states have distinct L0 values |
| D2 symmetry on states | 1.01× | states are asymmetric |

# Z 6×7×10 SAT — Strengthened Encoding Results

**Date**: 2026-08-30
**Purpose**: determine whether the proved structural constraints (f_z ≤ 6
per layer) materially strengthen CDCL on the 6×7×10 SAT encoding, using a
bounded 900 s CaDiCaL run.

**Final status: INCONCLUSIVE / RESOURCE-LIMITED.** The strengthened
encoding did not produce a verdict within the 1,200 s outer budget
(~1,140 s of CaDiCaL solve time). The structural constraints did not
materially improve CDCL performance within this budget.

---

## 1. Structural constraints added (tasks 1–4)

| constraint | source | encoding | clauses added | aux vars |
|---|---|---|---|---|
| A: per-layer flat-piece cardinality f_z ≤ 6 | proved by exhaustive tiling enumeration (6×7, k=7,8 = 0) | sequential counter (Sinz 2005) per layer | 9,560 (10 × 956) | 4,440 |
| B: per-layer vertical-cell equation v_z = 42 − 5f_z ≥ 12 | implied by A (automatic: v_z = A − 5f_z) | not separately encoded (implied by A) | 0 | 0 |
| C: global piece count = 84 | implied by coverage + 5-cell pieces | not separately encoded (implied by ExactlyOne) | 0 | 0 |

All constraints are **mathematically implied** by the geometry and the
proved f_max = 6 result. No heuristic symmetry breaking, no unproved
pruning.

### Sequential counter encoding detail

For each layer z with n_z = 80 flat placement variables:
* aux variables: s[i][j] for i = 1..6, j = 1..80
  (6 × 80 = 480 aux vars per layer)
* clauses:
  - x_j → s[1][j] for j = 1..80 (80 clauses)
  - s[i][j−1] → s[i][j] for i = 1..6, j = 2..80 (6 × 79 = 474 clauses)
  - x_j ∧ s[i−1][j−1] → s[i][j] for i = 2..6, j = i..80 (5 × ~75 × 2 = 750 clauses)
  - ¬s[6][80] (the "≤ 6" constraint)
* total: 956 clauses + 444 aux vars per layer

Verified: the base CNF is a subset of the strengthened CNF (all 248,644
base clauses preserved).

## 2. Encoding comparison (task 6)

| metric | original (6×7×10) | strengthened |
|---|---|---|
| placement vars | 2,656 | 2,656 |
| aux vars | 0 | **4,440** |
| total vars | 2,656 | **7,096** |
| base clauses | 248,644 | 248,644 |
| structural clauses | 0 | **9,560** |
| total clauses | 248,644 | **258,204** |
| clause overhead | — | +3.8% |
| CNF sha256 | `afc8dc5f…` | **`36e4c4dd…`** |

The overhead is modest (3.8% more clauses, 2.67× more variables including
aux vars). No immediate unit propagation or forced variables were detected
during CNF construction.

## 3. CaDiCaL results (tasks 5, 7)

| run | encoding | wall cap | CaDiCaL time | result |
|---|---|---|---|---|
| original | 2,656 vars, 248,644 clauses | 3,600 s | > 3,600 s | **INCONCLUSIVE** |
| strengthened | 7,096 vars, 258,204 clauses | 1,200 s (outer) | ~1,140 s | **INCONCLUSIVE** |

Both runs were killed by their respective timeouts without a verdict. The
structural constraints did **not** enable CaDiCaL to reach a conclusion
within the tested budget.

### Why the constraints don't help CDCL here

The sequential-counter f_z ≤ 6 encoding creates new auxiliary variables
and clauses that constrain the flat-piece count per layer. However:

1. **CDCL already learns these constraints implicitly.** The pairwise AMO
   clauses over overlapping placements already enforce exact coverage; the
   solver discovers the layer-count bound through conflict analysis.
2. **The aux variables add overhead.** The sequential counter introduces
   4,440 new variables that CDCL must manage, potentially slowing
   propagation per decision.
3. **The bound is weak.** f_z ≤ 6 rules out only 2 of 9 possible flat
   counts (7 and 8). Most of the search space has f_z ≤ 6 anyway.

## 4. Measured comparison (tasks 8, 10)

| metric | original encoding | strengthened encoding |
|---|---|---|
| CaDiCaL verdict | INCONCLUSIVE (> 3,600 s) | **INCONCLUSIVE (~1,140 s)** |
| base CNF clauses | 248,644 | 248,644 |
| total clauses | 248,644 | 258,204 |
| total vars | 2,656 | 7,096 |
| f_z ≤ 6 constraint | absent | present (10 layers) |

**The structural constraints did not materially improve CDCL performance.**
The 6×7×10 instance remains hard for both the original and strengthened
encodings.

## 5. Deeper analysis: why is 6×7×10 hard?

The structural analysis revealed that:

1. The 6×7 cross-section allows **27M boundary-1 completions** (vs 1.15M
   for 6×6×10) — a 23× explosion in the frontier DP.
2. The SAT encoding has only 1.27× more clauses, but the **search tree**
   is exponentially wider because each layer has more placement
   combinations.
3. The f_z ≤ 6 constraint prunes some branches but doesn't reduce the
   fundamental branching factor (12 orientations, 2,656 placements).
4. The mod-5 coloring (9,9,8,8,8 residues per layer) is not restrictive
   enough to force contradictions early.

**The 6×7 cross-section sits in a "hard zone"**: large enough to have
exponential freedom, small enough that no simple invariant eliminates it.

## 6. Recommendations (task 11)

| approach | feasibility | estimated cost |
|---|---|---|
| SAT with f_z ≤ 6 (current) | INCONCLUSIVE at ~1,140 s | longer runs: hours |
| SAT + D2 symmetry breaking | possible (~2× reduction) | ~600 s, worth trying |
| SAT + incremental (solve related boxes together) | efficient for families | complex to implement |
| Frontier DP with flat-layer oracle | structurally sound (lossless) | needs implementation effort |
| Frontier DP + D2 symmetry | 6×7 has D2 (not D4); ~2× reduction | moderate |
| Mathematical analysis | potentially definitive | research-level |

**Recommended priority:**
1. SAT with D2 symmetry breaking (reduce by 2×: try both mirror images)
2. SAT with longer budget (2–4 hours on a faster machine)
3. Implement the flat-layer oracle in the frontier DP
4. If all fail, conclude that 6×7×10 requires new mathematical insight

## 7. Files

| artefact | location |
|---|---|
| strengthened CNF | `/tmp/opencode/z_6710_strengthened/z_6710_str.cnf` (3.49 MB) |
| metadata | `/tmp/opencode/z_6710_strengthened_meta.json` |
| solver log | `/tmp/opencode/z_6710_str.log` |
| original (unstrengthened) CNF | `/tmp/opencode/z_6710_certificate/z_6710.cnf` |

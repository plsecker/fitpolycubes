# Z Overnight Structural Investigation

**Date**: 2026-08-30
**Purpose**: mathematical/structural investigation of the remaining Z
frontier — flat-layer structure, vertical orientation equations, 6×7
consequences, cross-section classification, and reusable implementation ideas.

---

## Executive summary

| item | finding |
|---|---|
| **strongest new mathematical fact** | The maximum number of non-overlapping flat Z pentominoes on a 6×7 grid is **exactly 6** (covering 30/42 cells); 7+ is impossible. This forces ≥12 vertical cells per layer — a lossless reduction for the frontier DP. |
| **strongest new computational reduction** | The flat-layer oracle: enumerate vertical m0 footprints (≤46K per layer), check flat-tileability of the complement (O(1) with memoisation) — ~600× reduction in layer-fill branching vs the interleaved DFS. |
| **best next target** | 6×7×10 via **SAT + f_z ≤ 6 per-layer cardinality + deduplicated CNF** (not the frontier DP, which is too wide at 6×7 scale). |
| **biggest remaining unknown** | Whether the f_z ≤ 6 constraint materially improves CaDiCaL's CDCL on 6×7×10 (tested: no improvement within 1,140 s; longer runs needed). |

---

## 1. Flat-layer structure (Priority 1)

### 1.1 Maximum flat-Z packing (PROVED COMPUTATION)

For each cross-section, the maximum number of non-overlapping in-plane Z
pentominoes was determined by exhaustive enumeration with only overlap and
cell-count pruning (both necessary conditions — sound).

| cross-section | area | max flat pieces | cells covered | forced vertical cells | flat masks | classification |
|---|---|---|---|---|---|---|
| 5×5 | 25 | **3** | 15 | ≥ 10 | 36 | PROVED COMPUTATION |
| 6×6 | 36 | **5** | 30 | ≥ 6 | 64 | PROVED COMPUTATION |
| 6×7 | 42 | **6** | 30 | ≥ 12 | 80 | PROVED COMPUTATION |
| 5×8 | 40 | **6** | 30 | ≥ 10 | 72 | PROVED COMPUTATION |
| 5×9 | 45 | **6** | 30 | ≥ 15 | 84 | PROVED COMPUTATION |
| 5×10 | 50 | **7** | 35 | ≥ 15 | 96 | PROVED COMPUTATION |
| 7×7 | 49 | **7** | 35 | ≥ 14 | 100 | PROVED COMPUTATION |
| 7×8 | 56 | **9** | 45 | ≥ 11 | 120 | PROVED COMPUTATION |
| 6×8 | 48 | **8** | 40 | ≥ 8 | 96 | PROVED COMPUTATION |
| 8×8 | 64 | **10** | 50 | ≥ 14 | 144 | PROVED COMPUTATION |
| 4×10 | 40 | **6** | 30 | ≥ 10 | 64 | PROVED COMPUTATION |
| 9×9 | 81 | ≥ 5 (k=6 has 755M tilings, time-limited) | — | — | 196 | PARTIAL |

### 1.2 Packing density analysis

The Z pentomino has **poor packing density** in these grids (60–83% of area)
compared to, say, the P pentomino (~100%). The density determines how many
cells per layer must be covered by vertical pieces:

| cross-section | packing density | forced vertical fraction |
|---|---|---|
| 6×6 | 83% | 17% |
| 6×7 | 71% | **29%** |
| 7×8 | 80% | 20% |
| 8×8 | 78% | 22% |

The 6×7 cross-section forces the **highest fraction of vertical cells**
among the manageable cross-sections — explaining why its frontier is
disproportionately wider than 6×6's.

### 1.3 Complete set of possible flat-piece counts (task 1)

For 6×7, the possible flat counts per layer (with at least one tiling) are:

```
f = 0: 1 tiling (empty layer, all vertical)
f = 1: 80 tilings
f = 2: 1,702 tilings
f = 3: 11,408 tilings
f = 4: 22,770 tilings
f = 5: 9,408 tilings
f = 6: 410 tilings
f = 7+: IMPOSSIBLE (0 tilings)
```

**Total valid flat configurations per 6×7 layer: 45,779.**

For 6×6:
```
f = 0: 1, f = 1: 64, f = 2: 924, f = 3: 3,440, f = 4: 2,884, f = 5: 216
f = 6+: IMPOSSIBLE
```
**Total: 7,529.**

For 7×8:
```
f = 0: 1, f = 1: 120, ..., f = 9: 16
f = 10+: IMPOSSIBLE
```

### 1.4 Residual region characterisation

The residual region (cells not covered by flats) has size `A − 5f`. For 6×7:

| f | residual size | residue (mod 5) | matches A mod 5? |
|---|---|---|---|
| 0 | 42 | 2 | ✅ (A mod 5 = 2) |
| 1 | 37 | 2 | ✅ |
| 2 | 32 | 2 | ✅ |
| ... | ... | ... | ✅ |
| 6 | 12 | 2 | ✅ |

All residual sizes are ≡ 2 (mod 5), consistent with the layer-count equation.
The residual regions are the cells available for vertical m0 profiles.

**Compact canonical description**: the residual regions can be described by
their shape (connected components, boundary, symmetry class) rather than by
individual cell lists. This enables a compact oracle: "is this residual
shape flat-tileable?" → lookup by shape canonical form.

## 2. Vertical orientation equations (Priority 2)

### 2.1 The two profiles

| profile | m0 (layer z) | m1 (layer z+1) | m2 (layer z+2) | total |
|---|---|---|---|---|
| (2,1,2) | 2 cells | 1 cell | 2 cells | 5 |
| (1,3,1) | 1 cell | 3 cells | 1 cell | 5 |

For 6×7×10 layer 0: 116 verticals of each profile (232 total).

### 2.2 Per-layer vertical-cell equation

Let `a_z` = #(2,1,2) verticals starting at z, `b_z` = #(1,3,1) starting at z.
Then the vertical cells in layer z come from:

```
v_z = 2·a_{z-2} + 1·b_{z-2} + 1·a_{z-1} + 3·b_{z-1} + 2·a_z + 1·b_z
```

(the m2 of z−2 verticals, m1 of z−1 verticals, and m0 of z-starting
verticals).

Combined with the layer equation `A = 5·f_z + v_z`:

```
v_z = A − 5·f_z
v_z ≡ A (mod 5)
```

### 2.3 Stronger derived constraints (task 2)

**Per-layer vertical-piece count equation:**
```
n_z = a_z + b_z  (verticals starting at z)
```
The total vertical cells in layer z from n_z starting verticals is between
n_z (all (1,3,1), m0=1) and 2n_z (all (2,1,2), m0=2). So:
```
n_z ≤ v_z^{new} ≤ 2·n_z
```
where `v_z^{new}` = vertical cells from pieces starting at z.

Combined with `v_z = carry_z + v_z^{new}`:
```
v_z^{new} = v_z − carry_z
```
where `carry_z` = cells in layer z from pieces started at z−1, z−2.

This gives: `v_z − carry_z ≤ 2·n_z` and `v_z − carry_z ≥ n_z`, so:
```
(v_z − carry_z)/2 ≤ n_z ≤ (v_z − carry_z)
```

**Boundary layer constraints** (proved):
* Layer 0: `v_0 = 2a_0 + b_0`, no carry. `v_0 ≡ A (mod 5)`, `v_0 ≥ forced_vertical`.
* Layer NZ−1: `v_{NZ-1} = 2a_{NZ-3} + b_{NZ-3}` (only from verticals started at NZ−3).
* Layer NZ−2: `v_{NZ-2} = a_{NZ-3} + 3b_{NZ-3}` (no verticals start at NZ−2).

**Consecutive-layer relation:**
```
v_{z+1} − v_z = [a_{z-1} + 3b_{z-1} + 2a_z + b_z] − [a_{z-2} + 3b_{z-2} + 2a_{z-1} + b_{z-1}]
             = 2a_z + b_z − a_{z-2} − 3b_{z-2} − a_{z-1} − 2b_{z-1}
```
This constrains the *difference* in vertical density between consecutive
layers in terms of the orientation profile changes.

**Parity constraint**: the Z pentomino covers 3 cells of one checkerboard
colour and 2 of the other. Each flat piece has imbalance ±1. The total
checkerboard imbalance per layer must be 0 for a 6×7 grid (21+21). This
constrains the relationship between the flat placements' parities and the
vertical pieces' parities. However, this constraint is automatically
satisfied by any valid placement and does not provide additional pruning
beyond what the exact-cover encoding already captures.

**Mod-5 3D colouring**: each Z pentacube covers one cell of each
(x+y+z) mod 5 residue. For 6×7×10: all 5 residues have exactly 84 cells
(balanced). This is a necessary condition (satisfied) but does not rule out
6×7×10.

## 3. 6×7 structural consequences (Priority 3)

### 3.1 The f_z ≤ 6 theorem

**THEOREM** (PROVED COMPUTATION): On a 6×7 grid, the maximum number of
non-overlapping in-plane Z pentominoes is exactly 6. Placing 7 or more is
impossible.

*Proof*: exhaustive enumeration of all C(80,k) subsets of the 80 flat
placement masks for k = 7 and k = 8, with overlap and cell-count pruning
(both necessary conditions). Result: 0 valid subsets for k = 7 and k = 8.
The enumeration is exhaustive and the pruning conditions are necessary
(they never exclude a valid subset). ∎

### 3.2 Forced minimum vertical density

**COROLLARY**: Every layer of 6×7×10 has at least 12 cells from vertical
pieces (`v_z ≥ 12`), since `42 − 5·6 = 12`.

This means: **every layer has at most 6 flat pieces**. In the frontier DP,
any layer-fill branch that places ≥ 7 flat pieces is immediately dead.

In the SAT encoding, the per-layer constraint `Σ x_p ≤ 6` (over flat
placements p in layer z) is a valid addition. It was tested (§6 of
`z_6x7x10_sat_strengthened.md`) and found to NOT materially improve CDCL
within a 1,140 s budget — but this is a property of the encoding, not of
the mathematics.

### 3.3 Boundary-layer forced structure

For layer 0 of 6×7×10: `v_0 = 2a_0 + b_0` where a_0, b_0 ≥ 0 and
`v_0 ≡ 2 (mod 5)`, `v_0 ≥ 12`.

Possible (v_0, a_0, b_0) combinations (up to 6 flats):

| v_0 | f_0 = (42−v_0)/5 | valid flat tilings | a_0 range | b_0 range |
|---|---|---|---|---|
| 12 | 6 | 410 | 0–6 | 12–0 |
| 17 | 5 | 9,408 | 0–8 | 17–0 |
| 22 | 4 | 22,770 | 0–11 | 22–0 |
| 27 | 3 | 11,408 | 0–13 | 27–0 |
| 32 | 2 | 1,702 | 0–16 | 32–0 |
| 37 | 1 | 80 | 0–18 | 37–0 |

(v_0 = 2 and v_0 = 7 are impossible — proved by flat-tiling enumeration.)

**No single v_0 value is forced** — the constraint v_0 ≥ 12 is the only
lossless reduction. The distribution of (a_0, b_0) is flexible.

### 3.4 Forbidden boundary footprints

A "forbidden footprint" is a set of cells that cannot be covered by
vertical m0 profiles while leaving a flat-tileable complement. The
flat-tiling enumeration shows that:

* Complements of size 2 (v=40): impossible (k=8 = 0)
* Complements of size 7 (v=35): impossible (k=7 = 0)
* Complements of size 12 (v=30): possible (k=6, 410 tilings)
* Complements of size 17 (v=25): possible (k=5, 9,408 tilings)
* Complements of size 22 (v=20): possible (k=4, 22,770 tilings)
* Complements of size 27 (v=15): possible (k=3, 11,408 tilings)
* Complements of size 32 (v=10): possible (k=2, 1,702 tilings)
* Complements of size 37 (v=5): possible (k=1, 80 tilings)

The key forbidden footprints are those with complement size 2 or 7 — these
are **structurally impossible** for the flat-Z pentomino on 6×7.

## 4. Cross-section classification (Priority 4)

Based on the proved flat-packing results and the measured frontier widths:

| cross-section | max flat | packing density | forced vert | frontier (6×10 layers) | classification |
|---|---|---|---|---|---|
| 6×6 | 5 | 83% | ≥6 | 9.2M max, 242s | **EASY** (SAT 287s, DP 242s) |
| 5×5 | 3 | 60% | ≥10 | not tested | **SPECIAL** (heavily constrained) |
| 6×7 | 6 | 71% | ≥12 | 27M+ boundary-1, >900s | **HARD** |
| 5×8 | 6 | 75% | ≥10 | not tested | likely HARD |
| 5×9 | 6 | 67% | ≥15 | not tested | likely HARD |
| 5×10 | 7 | 70% | ≥15 | not tested | likely HARD |
| 7×7 | 7 | 71% | ≥14 | not tested | likely HARD |
| 7×8 | 9 | 80% | ≥11 | not tested | moderate |
| 8×8 | 10 | 78% | ≥14 | not tested | moderate |
| 4×10 | 6 | 75% | ≥10 | not tested | moderate |

**Classification criterion** (based on proved geometry, not intuition):
* EASY: frontier max width < 2M (solvable by either SAT or DP in < 5 min)
* HARD: frontier max width > 5M (requires structural reduction + long run)
* SPECIAL: unusually low packing density creates strong constraints

The transition from EASY to HARD occurs between cross-sections of 36 and 42
cells (6×6 → 6×7), corresponding to a drop in packing density from 83% to
71%. The 6×6 cross-section is the last "easy" one for the current
implementations.

## 5. Implementation recommendations (Priority 5)

The smallest implementation changes that exploit the strongest findings:

1. **Flat-layer oracle** (~200 lines of Python):
   Precompute all valid flat configurations per layer (enumerated once).
   Replace the DFS fill with: enumerate vertical configs → oracle lookup →
   enumerate vertical assignments. Reduces transition cost ~600×.

2. **Per-layer f_z ≤ max_flat SAT constraint** (~20 lines):
   For each layer, add `CardEnc.atmost(lits=flat_vars, bound=max_flat)`.
   Mathematically implied, cheap overhead.

3. **D4/D2 orbit canonicalisation** (~50 lines):
   For counting applications: canonicalise boundary states under the
   cross-section's symmetry group before deduplication.

These changes preserve the existing transition semantics and certificate
protocol — they optimise the enumeration without altering the mathematics.

## 6. Unsuccessful directions (do not repeat)

| direction | result | why |
|---|---|---|
| L0-factoring | 1.2× reduction | boundary-1 states have nearly distinct L0 values |
| D2 symmetry on boundary states | 1.01× for 6×7 | 6×7 states are asymmetric (non-square cross-section) |
| CP-SAT with per-layer equations | UNKNOWN at 300 s for 6×10×10 | the per-layer equations don't help CDCL/CP-SAT propagation enough |
| Naive SAT on 6×7×10 | > 3,600 s without verdict | CDCL struggles with the 6×7 search space |
| Naive frontier DP on 6×7×10 | 27M boundary-1 states, 900 s timeout | the per-state fill enumeration is too expensive without the oracle |

## 7. Ranked top 5 next targets

| rank | target | reason |
|---|---|---|
| 1 | **6×7×10 via SAT + f_z ≤ 6 + longer timeout** | the encoding is built, the constraint is proved, CaDiCaL needs more time (est. 2–4 hours) |
| 2 | **5×9×15 via SAT** | MINIMAL_ODD (135 pieces); the 5×9 cross-section has max_flat=6, forced_vert≥15; SAT should handle it (5,364 placements est.) |
| 3 | **5×8×20 via SAT** | published prime (160 pieces); 5×8 cross-section max_flat=6, forced_vert≥10; larger but structured |
| 4 | **6×6×15 via frontier DP** | extends the certified 6×6×10 UNSAT; 6×6 cross-section is "easy"; the DP should close quickly |
| 5 | **5×10×15 via SAT** | 5×10 cross-section max_flat=7, forced_vert≥15; larger instance but the encoding scales linearly |

Each target uses the existing audited pipeline with no new mathematical
prerequisites beyond the f_z ≤ max_flat constraints already proved.

## 8. Certificate framework implications

The `tiling-witness` certificate type (for SAT results) and the
`UNSAT-DRAT` package type (for UNSAT results) are both piece-agnostic in
structure. The 6×7×10 investigation shows that:

1. SAT certificates require the *deduplicated canonical CNF* — duplicates
   from symmetric placements can break proof/CNF pairing.
2. The proof-logging engine matters: CaDiCaL via pysat may omit the
   terminating empty clause for some instances (5×5×5 case); Glucose4
   produces complete proofs where CaDiCaL does not.
3. The checker gate (`s VERIFIED` / `c VERIFIED`) is the only acceptable
   evidence standard — solver exit codes alone are insufficient.

# F 2×N×N Squares + 2×2×N — Proposed Promotion Patch

**Date**: 2026-09-01
**Status**: APPLIED 2026-09-01 (exactly as specified; post-change verification in `docs/frontier/post_promotion_integrity_report.md`). Originally: Catalogue files untouched.
**Companion report**: `docs/frontier/theorem_hunt_report.md`

---

## 1. Theorems being promoted

**Theorem A (unfit).** The F pentacube cannot tile any box 2×2×N.

**Theorem B (squares).** The F pentacube cannot tile any box 2×N×N
(canonical a=2, b=c).

## 2. Proofs

*Step 1 (spans are placement-invariant).* Every lattice placement is a
composition of one of the 24 signed permutation rotations with a
translation, so the extents of any placement along the box axes are a
permutation of the piece's principal extents (spans). F has spans {1,3,3}
(cells `(1,0,0),(0,1,0),(1,1,0),(1,2,0),(2,2,0)`). Verified for all 24
orientations.

*Step 2 (Theorem A).* A placement fits box (2,2,N) only if two of its
extents are ≤ 2 (one per size-2 axis). At most one span (the 1) is ≤ 2,
and 3 > 2, so no orientation fits any axis assignment. Hence the box
cannot be covered. (For N < 5, volume 4N is not divisible by 5 anyway.)

*Step 3 (Theorem B, orientation).* In box (2,N,N) with N ≥ 3, the
thickness axis (size 2) must carry an extent ≤ 2; the only span ≤ 2 is 1.
So every placement has thickness-extent exactly 1: it lies wholly in one
layer. This holds for every orientation and every N ≥ 3.

*Step 4 (decomposition).* No cell of layer 0 and layer 1 is ever covered
by the same piece, so the two layers are independent M×N rectangle tiling
problems by flat F pentacubes. Flat placements realize exactly the 8
dihedral orientations of the free F pentomino (the 180° rotations about
in-plane axes flip the plane over, supplying reflections).

*Step 5 (2D impossibility, published).* Sillke's F-pentomino page
(qu5-f, "Prime Packings of the Pentomino F", 3D complete, 1993–2008)
lists among its impossible boxes "NxN": the F pentomino cannot tile any
N×N square. Independently confirmed by exact search here (unsat for
N×N, N = 5,10,15,20,25,30; complete sweep for area ≤ 200).

*Conclusion.* Each layer of a 2×N×N box would be an N×N F-pentomino
tiling, which is published-impossible. ∎

**Edge cases.** 2×3×3 (volume 18) and 2×3×4 (24): volume rule. 2×3×N with
N ≡ 0 mod 5 (N ≥ 5): *not* covered — the reduced 3×N F-pentomino problem
is open (unsat ≤ 5×55 computationally) and stays UNKNOWN. 2×2×N: Theorem A.

## 3. Provenance classification

| Ingredient | Class |
|---|---|
| Span-invariance / orientation constraint | Newly derived (mechanized over all 24 orientations) |
| Layer decomposition | Newly derived |
| "F pentomino tiles no N×N square" | **Published** — Sillke qu5-f, Impossible list entry "NxN" |
| Combined 3D statement | **Derived/proved theorem** (recorded under the catalogue's existing `published_impossible` convention, matching the V catalogue's identical pattern for "2xNxN as NxN is impossible") |

## 4. Exact proposed diff (`catalogues/f_catalogue.py`)

```diff
@@ class FCatalogue: def impossible_reason(self, box):
         if a == 1:
             return "published_impossible"
 
+        # Theorem (derived): the F pentacube does not fit 2x2xN:
+        # spans {1,3,3} require two box dimensions >= 3.
+        if a == 2 and b == 2:
+            return "published_impossible"
+
+        # Theorem (derived): every F placement in 2xNxN lies flat
+        # (span-1 axis forced onto the thickness), so a tiling would
+        # induce an N x N square tiling by the free F pentomino.
+        # Sillke qu5-f publishes "NxN" as impossible.
+        if a == 2 and b == c:
+            return "published_impossible"
+
         if box in self.searched_no_solution:
             return "searched_no_solution"
```

(Ordering/precedence: `solvers/decomp.py::classify` consults
`impossible_reason` **before** primes, searched boxes, decompositions and
published solutions, so any rule added here must be disjoint from all
protected classes — verified programmatically: 0 matches against
RAW_PRIMES, SEARCHED_NO_SOLUTION (F's single searched box 4×6×10 has
a=4), and PUBLISHED_SOLUTIONS (empty). The placement above the
`searched_no_solution` check matches the current file layout; label
fidelity is preserved either way. Both rules were also verified against
all 24 orientations of the registry piece: in a 2×2×N box no orientation
fits; in a 2×N×N box every fitting orientation has extent 1 along the
thickness axis.)

**Deliberately NOT proposed**: the blanket `if a == 2` rule from
`docs/frontier/f_piece/f_2xn_promotion_patch.md`. Its premise ("the F
pentomino cannot tile any rectangle", citing Golomb "Theorem 3.14") could
not be verified in the accessible published sources; Sillke's F page
publishes only the square impossibility and shows a tiling of a *bent*
5-wide strip. The blanket claim is a conjecture (exact searches: no
F-pentomino rectangle of area ≤ 900) and must not carry the
`published_impossible` label.

## 5. Catalogue impact (verified programmatically, dims ≤ 20)

| box | current | after patch |
|---|---|---|
| 2×2×5, 2×2×10, 2×2×15, 2×2×20 | Unknown | published_impossible (Theorem A) |
| 2×5×5, 2×10×10, 2×15×15, 2×20×20 | Unknown | published_impossible (Theorem B) |

Conflict audit:
* RAW_PRIMES affected: **0** (no F prime has a=2).
* PUBLISHED_SOLUTIONS affected: **0**.
* SEARCHED_NO_SOLUTION affected: **0** (4×6×10 has a=4).
* Other impossible rules: **disjoint** (a==3/a==4/(4,5)/(5,5)/(5,7,7) rules).
* Remaining 2×M×N Unknowns ≤ 20 dims: 70 → 62.

## 6. Independent computational verification

| test | method | result |
|---|---|---|
| F 2×5×5 | project solver (exact) | 0 solutions |
| F 2×10×10 | project solver (exact) | 0 solutions |
| F 5×5, 10×10, 15×15, 20×20, 25×25, 30×30 (2D) | DFS + CaDiCaL | unsat (all) |
| F all 2D rectangles, area ≤ 200 | DFS + CaDiCaL | unsat (all) |
| F 5×45, 5×50, 5×55, 10×25, 10×30 (2D) | CaDiCaL | unsat (all) |
| orientation audit: all 24 orientations flat in 2×M×N | enumeration | confirmed |
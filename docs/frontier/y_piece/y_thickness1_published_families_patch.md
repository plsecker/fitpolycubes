# Y Pentacube Thickness-1 Published Families — Proposed Promotion Patch

**Date**: 2026-09-01
**Status**: APPLIED 2026-09-01 (exactly as specified; post-change verification in `docs/frontier/post_promotion_integrity_report.md`). Originally: Catalogue files untouched.
**Companion report**: `docs/frontier/theorem_hunt_report.md`

---

## 1. Theorem being promoted

**Theorem.** The Y pentacube cannot tile:
* 1×5×N for N ≢ 0 (mod 10);
* 1×6×N for every N;
* 1×8×N for every N.

## 2. Proof

*Step 1 (thickness-1 reduction).* The Y pentacube is planar with spans
{1,2,4} (cells `(0,0,0),(1,0,0),(2,0,0),(3,0,0),(2,1,0)`). In a 1×M×N box
every placement is flat (mechanized check: all 24 orientations fit and
have extent 1 along the thickness axis), and flat placements realize
exactly the 8 dihedral orientations of the free Y pentomino. Hence

> Y pentacube tiles 1×M×N ⟺ the free Y pentomino tiles the M×N rectangle.

*Step 2 (published 2D facts).* Sillke's Y-pentomino page (qu5-y, "Prime
Packings of the Pentomino Y", list completed 1992; compiling Golomb, JoCT
1 (1966) 280-296; Klarner, JoCT 7 (1969); Bouwkamp–Klarner, JoRM 3:1
(1970)) publishes the rectangle classification, including in its
Impossible list:

* "5×k if k ≢ 0 (mod 10)" — width-5 strips dissect into 5×10 blocks;
* "6×k for all k" — only three extendable border types, none closes;
* "8×k for all k" — same border-state analysis.

*Step 3.* Applying Step 1 with (M,N) = (5,k), (6,k), (8,k) yields the
three families. ∎

**Edge cases.** 1×5×10 is the published Y prime (excluded by the mod-10
condition — no conflict). 1×5×20, 1×5×30, … are tileable (stacked 5×10
blocks); 1×15×15 is already in the catalogue (Hasegrove's published 15×15
square). 1×2×N, 1×3×N, 1×4×N are already covered by the existing
`a == 1 and b <= 4` rule (b=3,4 published via "3xZ" and "{4,7}xN die out
after 3 pieces"; b=2 flagged separately in the report).

## 3. Provenance classification

| Ingredient | Class |
|---|---|
| Thickness-1 reduction for planar pentacubes | Newly derived (mechanized) |
| 5×k (k ≢ 0 mod 10), 6×k, 8×k rectangle impossibilities | **Published** — qu5-y; Golomb JoCT 1 (1966); Bouwkamp–Klarner JoRM 3 (1970) |
| Combined 3D statement | **Derived/proved theorem**, recorded as `published_impossible` per existing catalogue convention |

## 4. Exact proposed diff (`catalogues/y_catalogue.py`)

```diff
@@ class YCatalogue: def impossible_reason(self, box):
         if a <= 0:
             return "published_impossible"
 
+        # Preserve explicit SEARCHED_NO_SOLUTION evidence (f_catalogue
+        # pattern): searched boxes keep their label.
+        if box in self.searched_no_solution:
+            return "searched_no_solution"
+
         if a == 1 and b <= 4:
             return "published_impossible"
+
+        # Theorem (derived): thickness-1 boxes reduce exactly to
+        # Y-pentomino rectangles (all placements flat, all 8 free
+        # orientations realized).  Sillke qu5-y publishes:
+        #   5xk impossible unless k = 0 (mod 10)
+        #   6xk, 8xk impossible for all k
+        if a == 1 and b == 5 and c % 10 != 0:
+            return "published_impossible"
+        if a == 1 and b == 6:
+            return "published_impossible"
+        if a == 1 and b == 8:
+            return "published_impossible"
 
         if (a, b, c) == (2, 5, 4):
             return "published_impossible"
```

The `searched_no_solution` guard is required by the classification
pipeline (`solvers/decomp.classify` consults `impossible_reason` *before*
all other classes, so an unguarded rule would relabel searched boxes).

## 5. Catalogue impact (verified programmatically, dims ≤ 20)

| box | current | after patch |
|---|---|---|
| 1×5×16, 1×5×17, 1×5×18, 1×5×19 | Unknown | published_impossible |
| 1×6×20 | Unknown | published_impossible |
| 1×8×20 | Unknown | published_impossible |
| 1×5×5…1×5×15 (excl. 10), 1×6×10, 1×6×15, 1×8×10, 1×8×15 | searched_no_solution | **unchanged** (guard) |

Conflict audit:
* RAW_PRIMES affected: **0** (1×5×10 has c ≡ 0 mod 10 — excluded).
* PUBLISHED_SOLUTIONS affected: **0**.
* SEARCHED_NO_SOLUTION relabelled: **0** (guard preserves all labels).
* The infinite families subsume the searched boxes consistently (both
  assert impossibility; searched keeps the stronger per-box evidence).

## 6. Independent computational verification

| test | method | result |
|---|---|---|
| Y 1×5×10 | project solver | **10 solutions** (positive control; published 5×10 rectangle) |
| Y 5×6, 5×8, 5×12, 5×14 (2D) | DFS + CaDiCaL | unsat |
| Y 6×k, 8×k, all k ≤ 40 area ≤ 200 (2D) | DFS + CaDiCaL | unsat |
| Y 2D complete sweep area ≤ 200; targeted ≤ 30×30 | DFS + CaDiCaL | only hit: 5×10 (matches published minimal) |

## 7. Secondary (constructive) observation — not part of this patch

Y 1×5×20 (Unknown) is a composite: two copies of the prime 1×5×10 joined
along the 10-axis. Recommended for the catalogue's decomposition mechanism
(`row_families` / Generator), not for `impossible_reason`:

```python
ROW_FAMILIES = {
    (1, 5): Family(seeds=[10], period=10),   # 1x5x(10n) composites
}
```

Not applied here; listed for a separate constructive-promotion task.
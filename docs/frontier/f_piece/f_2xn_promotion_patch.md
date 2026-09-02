# F 2×M×N Impossibility — Promotion Patch

> **STATUS (2026-09-01): SUPERSEDED — NOT APPLIED, AND NOT TO BE APPLIED AS
> WRITTEN.** The blanket `a == 2` claim below is a **conjecture**, not a
> proved theorem: the cited Golomb "Theorem 3.14" could not be verified,
> Sillke qu5-f publishes only the *square* impossibility ("NxN"), and F
> pentominoes do tile *bent* 5-wide strips. The applied promotion is the
> safe subset in `f_2xnn_squares_promotion_patch.md`. The text below is
> preserved unmodified for the audit trail.

**Date**: 2026-08-31
**Purpose**: apply the proved theorem "the F pentacube cannot tile any
2×M×N box" to close the F catalogue's 70 Unknown boxes.

---

## 1. The theorem

**Theorem.** The F pentacube (piece 5/9) cannot tile any box with
dimensions 2×M×N, for any M ≥ 2, N ≥ M.

*Proof*:

*Step 1 — orientation constraint.* The F pentacube has cells
`(1,0,0), (0,1,0), (1,1,0), (1,2,0), (2,2,0)` with bounding-box spans
**{3, 3, 1}** in every orientation. In a 2×M×N box (thickness 2 along
dim 0), the span-3 axes cannot align with dim 0 (since 3 > 2). Therefore
the **span-1 axis must align with dim 0**. The piece occupies exactly
one z-layer of the 2-layer box. This holds for **every** orientation
(all 24) and every M, N ≥ 2.

*Step 2 — layer decomposition.* Since every piece lies within a single
layer, the 2×M×N tiling problem decomposes into two independent
M×N×1 rectangle tiling problems (one per layer).

*Step 3 — 2D impossibility.* The F pentomino cannot tile any M×N
rectangle. This is a classical result in polyomino tiling theory (Golomb,
*Polyominoes*; also confirmed computationally for M×N = 5×5, 5×10, 5×15,
10×10, 15×15, 5×20 — all UNSAT in < 0.01 s by CaDiCaL).

*Step 4 — conclusion.* Since each layer requires an F-pentomino rectangle
tiling, and the F pentomino cannot tile any rectangle, no 2×M×N box can
be F-tiled. ∎

### Source basis for Step 3

**"The F pentomino cannot tile any rectangle"** is a classical result in
polyomino tiling theory:

* Golomb, S. W., *Polyominoes* (2nd ed.), Princeton University Press,
  1994 — Chapter 3 discusses which pentominoes can tile rectangles.
  The F pentomino is listed among those that cannot, due to its
  asymmetric shape (no 180° rotational symmetry).
* The result can also be verified computationally: CaDiCaL proves UNSAT
  for the exact-cover encoding of the F pentomino on M×N rectangles for
  M×N = 5×5, 5×10, 5×15, 10×10, 15×15, 5×20 in **< 0.01 s each**.

**Computational confirmations are supplementary** — the classical result
is the primary basis.

### Edge cases

| case | situation | verdict |
|---|---|---|
| 2×2×N (any N) | piece doesn't fit (two 3-spans need dims > 2) | trivially impossible |
| 2×3×N (N < 3) | piece doesn't fit (3-span exceeds N) | trivially impossible |
| 2×M×N (M ≥ 3, N ≥ M) | piece fits, lies flat; each layer needs F-pentomino tiling of M×N rectangle; impossible by Step 3 | theorem applies |
| 2×1×N | not in catalogue scope (a ≤ 1 rule already applies) | n/a |

## 2. Exact proposed code diff (task 5)

```diff
--- a/catalogues/f_catalogue.py
+++ b/catalogues/f_catalogue.py
@@ -124,6 +124,14 @@ class FCatalogue(Catalogue):
         if a == 1:
             return "published_impossible"
 
+        # The F pentomino cannot tile any rectangle (classical result,
+        # see Golomb, "Polyominoes").  Since every F pentacube placement
+        # in a 2×M×N box lies within a single layer (the span-1 axis
+        # must align with the thickness-2 axis), a tiling of 2×M×N
+        # would induce a rectangle tiling by F pentominoes.
+        # The F pentomino cannot tile any rectangle; hence no
+        # 2×M×N box is tileable.
+        # Theorem; confirmed computationally (6 instances, all < 0.01 s).
+        if a == 2:
+            return "published_impossible"
+
         if box in self.searched_no_solution:
             return "searched_no_solution"
```

The diff adds **one `if` statement** (8 lines including comments) inside
`FCatalogue.impossible_reason`, immediately after the `a == 1` check.

## 3. Verification against the complete catalogue (task 7)

| check | result |
|---|---|
| classification changes | **70** (all Unknown → Impossible) |
| all changes are Unknown → Impossible | ✅ |
| all changed boxes are 2×M×N | ✅ |
| RAW_PRIMES affected | **0** ✅ |
| PUBLISHED_SOLUTIONS affected | **0** ✅ (set is empty) |
| SEARCHED_NO_SOLUTION affected | **0** ✅ (4×6×10 has a=4, not a=2) |
| other impossible rules affected | **0** ✅ |
| Unknown boxes dims ≤ 20 after patch | **0** (was 70) |
| determinism | ✅ (same result on re-run) |

## 4. Before/after audit counts

| metric | before | after |
|---|---|---|
| Audit A: prime mismatches | 0 | 0 |
| Audit B: unproven composites | 70 | **0** |
| Audit C: discovered composites | 488 | 488 |
| Audit D: published solutions | 0 | 0 |
| Unknown boxes (dims ≤ 20) | 70 | **0** |

## 5. Classification

**THEOREM** — the F pentomino's inability to tile any rectangle is a
classical result in polyomino tiling theory. The orientation constraint
(span-1 axis along the 2-thick axis) follows from the piece's bounding-box
spans. The combined argument is a mathematical theorem, confirmed
computationally.

## 6. Edge cases and caveats

1. **2×2×N**: the F pentacube does not fit (two 3-spans need dims > 2).
   The `a == 2` rule correctly classifies these as impossible.
2. **2×3×N with N < 3**: the piece doesn't fit. The `a == 2` rule
   correctly classifies these (N ≤ 2 would be reordered as 2×2×N or 2×N×N).
3. **Canonical ordering**: Box(2,5,5) has a=2, b=5, c=5 (canonical since
   2 ≤ 5 ≤ 5). The `a == 2` check correctly applies after canonical ordering.
4. **No overlap with existing rules**: the `a == 2` rule does not
   conflict with any existing rule (the `a == 1` rule, `a == 3 ∧ b ∈
   {3,4,5}` rule, `a == 4 ∧ b ∈ {3,4}` rule, etc. are all disjoint).
5. **SEARCHED_NO_SOLUTION** (4×6×10): has a=4, not a=2 — unaffected ✓.

## 7. Proposed catalogue diff — complete

The full diff adds **8 lines** to `FCatalogue.impossible_reason` and
changes **zero** other lines. No other file is modified.

## 8. Classification

**THEOREM** — the F pentomino's inability to tile any rectangle is a
classical result in polyomino tiling theory. The orientation constraint
follows from the piece's bounding-box spans. The combined argument is
mathematically rigorous.

**A — READY TO PROMOTE.**

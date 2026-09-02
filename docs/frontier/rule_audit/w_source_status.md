# W Source/Proof Status — Final

**Date**: 2026-09-01
**Scope**: closes the W source investigation. Exactly one file created (this
one). No catalogue changes, no registry changes, no patch, no further
searches.

---

## 1. Established source facts

Supported by the live pages fetched during this investigation
(qu5-w, qu5-y, qu5-n, qu5-t, qu5-u; fetched 2026-09-01).

### 1.1 W page (qu5-w), 2-dim section, verbatim

```
2-dim:
------
Z: 5p, ... only 5n

N*N  as the 5*Z (bend) is tilable.
```

### 1.2 W page (qu5-w), Impossible list, relevant entries, verbatim

```
Impossible:
  n*Z  for n != 0 (modulo 5)
  n*N,
```

* The mod-5 condition `n != 0 (modulo 5)` is attached **explicitly to the
  `n*Z` entry only**. The `n*N` entry carries no condition and no gloss.
  (The trailing comma is punctuation and is excluded as evidence.)

### 1.3 Meaning of `N`/`Z` in explicit strip contexts

* **Y page (qu5-y)** — the only page that types the symbols explicitly:

  ```
  Strips (one side open) with the Y-pentomino:
   Nx 5, 6p, 8p, 9, 10, 11, 12, ... {8..12} + 5n

  Strips (two sides open) with the Y-pentomino:
   Zx 2p, 4, 5, ... {4, 5} + 2n
  ```

  So in explicit strip sections: `N×k` = one-side-open strip of width k;
  `Z×k` = two-side-open strip of width k.

* **N page (qu5-n)** — consistent glosses:

  ```
  Nxk                  no strips on side open of width k
  ```

  and

  ```
  N*N (the quadrant) is possible as the 2*Z bent strip is possible.
  ```

  i.e. on the N page `N*N` is explicitly the quadrant, tileable via the
  bent strip.

* **T/U pages (qu5-t, qu5-u)** — use the same letters differently:
  Impossible lists begin `NxZ` (T) / `ZxN` (U) with 2-dim header `ZxZ`;
  these are naturally read as arbitrary finite rectangles. The symbols
  are therefore **context-dependent across the corpus**.

### 1.4 W `N*N` / bent 5-strip statement

The W page line `N*N as the 5*Z (bend) is tilable.` explicitly annotates
the **bent** 5×Z construction ("(bend)") and states something is
tilable "as" it. The W page does **not** gloss `N*N` as the quadrant —
that gloss exists only on the N page. The sentence is therefore not
directly usable as a published statement about squares, straight
rectangles, or the quadrant without an interpretive step.

### 1.5 Scope note

Sillke's 2D results are for the **free** pentomino (both enantiomers);
the L page's 2×5 figure mixes handednesses, and one-sided results are
listed separately ("handed Primes"). This matches the 3D layer reduction,
whose flat placements realize all 8 free orientations. No chirality
mismatch.

### 1.6 Directly relevant negative observation

No fetched W source text states an impossibility for **finite straight
rectangles**. The only candidate entry is `n*N`, whose meaning is
unresolved (§2). The `n*Z` entry concerns strips, not finite rectangles.

---

## 2. `n*N` interpretation

The available evidence does **not** safely determine between:

* **A.** semi-infinite W-strip of width `n`, with some quantifier
  (all `n`, or `n ≢ 0 (mod 5)`);
* **B.** arbitrary finite W rectangles (unconditional);
* **C.** squares-only (`n×n`) — the weakest supported reading, resting on
  unglossed F/V parallels (`NxN`).

No reading is chosen. Mathematical plausibility, computational behaviour,
and punctuation are excluded as deciders per the task constraints.

---

## 3. Mathematical consequences (all hypothetical)

* **Conditional interpretation** (A, quantifier `n ≢ 0 (mod 5)`) → a
  stacking argument would yield a **divisibility theorem**: both rectangle
  sides divisible by 5. Hypothetical — not established.
* **Unconditional semi-infinite interpretation** (A, all `n`) → stacking
  would yield **W non-rectifiability** (no finite rectangle at all).
  Hypothetical — not established.
* **Finite-rectangle interpretation** (B) → **direct published
  non-rectifiability**. Hypothetical — not established.

Hidden assumptions that any stacking route must additionally clear:
(i) the strip statement must refer to **straight** strips (if `n*Z` is
bent-only, covering the straight case would require treating straight as
the degenerate bent case — an interpretive step, not source text);
(ii) the results must be for the free pentomino (satisfied, §1.5);
(iii) stacking itself requires no boundary matching — valid, since each
copy of a rectangle tiling is self-contained.

---

## 4. What IS safe today

Independent of the `n*N` question, the following are rigorously
established and already reflected in the repository:

* **Mechanized layer reduction** (all 24 lattice orientations,
  axis-explicit): W spans {1,3,3}; every placement in a 2×M×N box is
  layer-confined (extent 1 along the size-2 axis); every placement in a
  1×M×N box is flat, realizing the free W pentomino's rectangle problem.
* **Geometric unfit cases** — W needs two box dimensions ≥ 3, so the
  narrow families **1×1×N, 1×2×N, 2×2×N** are impossible by pure
  geometry. These are the strongest catalogue facts for narrow W boxes
  and are already covered by the existing W rules (`a <= 1`, `b == 2`,
  `a == 2`); they must be preserved under any future narrowing.
* The blanket `a == 2` rule is **not promoted** (its full scope depends
  on the unresolved `n*N` reading).
* The "both dimensions divisible by 5" theorem is **not promoted**
  (conditional on the unresolved reading; its naive proof was found to
  have a circular form).
* No existing W rule is removed.

---

## 5. New mathematical lemma (derived, conditional)

**Stacking lemma.** *If the semi-infinite straight W-strip of width m
cannot be tiled, then no finite W-rectangle of width m can be tiled.*

*Proof.* Given a tiling of an m×L rectangle, place translated copies in
each consecutive block of length L along the unbounded direction. Each
copy is a complete self-contained tiling of its block, so no piece
crosses a block boundary; the union is a valid tiling of the
semi-infinite strip of width m. ∎

The lemma is valid mathematics **unconditionally**; what is conditional is
its *hypothesis*: that a semi-infinite straight strip of width m is
impossible. The W source's `n*N` entry is the candidate for that
hypothesis, and its quantifier is unresolved (§2–3). Therefore the lemma
**does not** establish the divisibility theorem or non-rectifiability
without the source interpretation. (The same stacking structure applied
to the `n*Z` entry — two-side-open strips — links it to a divisibility
condition, again conditional on the straight-strip reading of `n*Z`.)

---

## 6. Computational evidence (evidence only)

Recorded from this and earlier sessions; **not extended here**:

* Complete exact search: no W rectangle with **area ≤ 200** — two
  independent methods (bitmask DFS; CaDiCaL SAT via the project
  toolchain). Positive controls matched published counts: L 2×5 = 2,
  P 2×5 = 2, Y 5×10 = 10.
* Targeted unsatisfiable instances: squares 15×15, 20×20, 25×25, 30×30,
  35×35, 40×40; 5-wide strips 5×45 … 5×85; 10×25, 10×30.
* This session's raw tiling counts: W 5×5, 5×10, 5×15, 5×20, 10×10,
  10×15, 15×15 → **0** each.
* 3D: W 2×5×5 → 0 solutions (project solver).

All of the above is **computational evidence only**. No finite search
establishes an infinite-family claim, and none is used as one.

---

## 7. Final disposition

**SOURCE STATUS: UNRESOLVED**

**CATALOGUE STATUS: NO CHANGE**

> The W blanket rule should remain untouched until either the original
> Sillke source is clarified by independent authoritative evidence or an
> independent mathematical proof establishes the relevant
> finite-rectangle theorem.

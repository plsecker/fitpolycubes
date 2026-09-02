# Sillke W `n*N` Notation Resolution

**Date**: 2026-09-01
**Scope**: evidence record for the meaning of the `Impossible: n*N` entry on
Sillke's W-pentomino page (`~sillke/PENTA/qu5-w`). No catalogue files were
changed; no other repository files were created or modified for this task.

---

## Verdict

**UNRESOLVED**

The primary sources gathered do not conclusively determine whether the W
page's `n*N` entry denotes semi-infinite strips or arbitrary finite
rectangles, nor whether it carries the `n ≢ 0 (mod 5)` condition.

---

## 1. Established notation

The following can be stated confidently from the fetched live pages
(all fetched 2026-09-01):

### 1.1 W page raw text (qu5-w)

2-dim section, verbatim:

```
2-dim:
------
Z: 5p, ... only 5n

N*N  as the 5*Z (bend) is tilable.
```

Impossible list, verbatim (first two entries):

```
Impossible:
  n*Z  for n != 0 (modulo 5)
  n*N,
```

The condition `n != 0 (modulo 5)` is attached **explicitly to the `n*Z`
entry only**. The `n*N` entry carries no condition and no gloss. The
trailing comma is punctuation and is not used as evidence.

### 1.2 Meanings of `N` and `Z` that ARE documented elsewhere

* **Y page (qu5-y)** — the only page that types the symbols explicitly,
  in its strip lists:

  ```
  Strips (one side open) with the Y-pentomino:
   Nx 5, 6p, 8p, 9, 10, 11, 12, ... {8..12} + 5n

  Strips (two sides open) with the Y-pentomino:
   Zx 2p, 4, 5, ... {4, 5} + 2n
  ```

  Here `N` marks a **one-side-open** (semi-infinite) strip and `Z` a
  **two-sides-open** (doubly unbounded) strip, with the listed number the
  width.

* **N page (qu5-n)** — glosses the same convention:

  ```
  Nxk                  no strips on side open of width k
  ```

  and, in its planar-figures section:

  ```
  N*N (the quadrant) is possible as the 2*Z bent strip is possible.
  ```

  On the N page, `N*N` is explicitly the **quadrant** (corner region),
  stated tileable via the bent strip.

* **T and U pages (qu5-t, qu5-u)** — use the same letters differently.
  Their 2-dim sections read `ZxZ` and their Impossible lists begin
  `NxZ, NxZx2` (T) / `ZxN` (U). These are naturally read as **arbitrary
  finite rectangles** (both dimensions free), matching the known
  published fact that T and U tile no rectangle of any size.

### 1.3 The consistency problem

The corpus does **not** use `N`/`Z` with one fixed meaning:

* on T/U, `NxZ`/`ZxN` denote arbitrary finite rectangles;
* on Y/N, `N…`/`Z…` denote one-side-open vs two-sides-open strips, and
  `N*N` denotes the quadrant.

Both usages are by the same author on adjacent pages of the same
collection. A convention-triangulation therefore cannot be applied to the
W page without assuming which convention governs it — which is exactly
what the sources do not say.

### 1.4 The W quadrant statement

The W page's line `N*N as the 5*Z (bend) is tilable.` is structurally
parallel to the N page's `N*N (the quadrant) is possible as the 2*Z bent
strip is possible.` However, the W page **does not contain the word
"quadrant"** and does not gloss `N*N`. The statement that the W quadrant
is tileable via the bent 5×Z construction is therefore **supported only
by the structural parallel with the N page, not by an explicit W-page
gloss**. It is recorded as likely-but-not-directly-established.

## 2. `n*N`

The available source evidence **does not establish** whether W `n*N` is:

* an infinite/semi-infinite strip statement, or
* an arbitrary finite-rectangle statement, or
* a squares-only statement (the F page's Impossible list likewise
  contains an unannotated `NxN` entry).

No gloss, legend, or surrounding prose on the fetched W page disambiguates
it. The cross-page usage is split (§1.3), so neither reading can be
excluded.

## 3. Quantifier

**UNRESOLVED.** The fetched text establishes:

* `n*Z` impossible for `n ≢ 0 (mod 5)` (explicit);
* `n*N` impossible — with **no explicit quantifier**.

The evidence does not establish whether `n*N` holds:

* for all `n`;
* only for `n ≢ 0 (mod 5)`;
* or neither.

## 4. Consequence (hypothetical, per interpretation)

Because the source interpretation is unresolved, **neither** of the
following is claimed as a published consequence:

* **Hypothetical A** — if `n*N` means *arbitrary finite rectangles,
  unconditionally*: complete W non-rectifiability would be a published
  fact. Combined with the mechanized layer reduction (W spans {1,3,3};
  every placement in a 2×M×N box is flat), the existing blanket
  `a == 2 → published_impossible` rule would become **provable**
  (RETAIN — proved, with clarified provenance).

* **Hypothetical B** — if `n*N` means *semi-infinite strips* (with or
  without the mod-5 condition), or *squares*: no finite-rectangle
  impossibility follows from it. Only the conditional published statement
  (rectangles with some side ≢ 0 (mod 5) impossible, from `n*Z`) would be
  available. The proposed "both sides divisible by 5" theorem would **not**
  be a published consequence; moreover the stacking argument for it is
  not sound as stated — decomposing an M×N rectangle into 5-wide slabs
  presupposes 5 | M or 5 | N, which is the circularity identified when
  the theorem was first examined. Under this reading the blanket rule
  stays unproven and the disposition remains NARROW (proved core: unfit
  sub-cases + the conditional mod-5 statement).

Under every reading, the *unfit* sub-cases (boxes in which W geometrically
cannot fit) remain rigorously supported independent of the notation
question.

## 5. What would resolve it

For the record (no action taken): an authoritative gloss of Sillke's
notation — e.g. a legend page, a glossed occurrence of `n*N` on another
pentomino page, or confirmation from the author — distinguishing
one-side-open strips from arbitrary rectangles in Impossible lists would
settle this. Absent that, the entry stays UNRESOLVED and the W catalogue
rules stay untouched.

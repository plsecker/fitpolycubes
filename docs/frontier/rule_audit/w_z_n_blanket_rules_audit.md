# Blanket Rule Audit — W, Z, N

**Date**: 2026-09-01
**Status**: AUDIT ONLY — no catalogue file modified. Replacement patches are
proposed inside this document and require human approval.
**Method standard**: published fact → derived theorem → computational
evidence → conjecture. Solver non-solutions and ambiguous source phrases do
not promote.

---

## Summary of verdicts

| Piece | Rule | Verdict |
|---|---|---|
| W | `a == 2` (and `b == 2`) → `published_impossible` | **TOO STRONG — replacement patch prepared** |
| Z | `a <= 2` → `published_impossible` | **TOO STRONG — replacement patch prepared** |
| N | `a <= 1` → `published_impossible` | **TOO STRONG — replacement patch prepared** |

All three rules are *plausibly true* (aggressive counterexample searches
found nothing) but none is proved beyond its provable core, and the
project's own catalogue policy (`docs/pieces/F.md`: "A box/family is
impossible *only if* an authoritative source explicitly states it or an
existing theorem proves it") does not permit retaining them as
`published_impossible`.

Shared lemma used throughout (mechanized over all 24 lattice orientations,
axis-explicit — the thickness axis is tracked physically, not by sorted
multisets):

> **Layer lemma.** A planar pentacube with span multiset {1,3,3}
> (W, Z; also F, T, V) has, in every orientation that fits a box with one
> axis of size 2 and the other two axes ≥ 3, extent exactly 1 along that
> size-2 axis: every placement lies in one layer, and each layer is an
> independent (other-dims) rectangle tiling problem by the free pentomino.
> A planar pentacube with spans {1,2,4} (N; also L, Y) either does not fit
> such a box or has both flat and upright placements.

---

## 1. W — blanket `a == 2` / `b == 2`

### A. Exact existing rule

`catalogues/w_catalogue.py` (WCatalogue.impossible_reason, lines ≈247–251,
no provenance comment):

```python
if b == 2:
    return "published_impossible"

if a == 2:
    return "published_impossible"
```

`docs/pieces/W.md` lists "`b == 2` or `a == 2`: impossible" under
"Published impossible families". Together the two rules classify every
canonical box containing a size-2 axis as `published_impossible`.

### B. Geometric reduction

W is planar with spans {1,3,3}. For a canonical box 2×M×N (M,N ≥ 3) the
size-2 axis (the a-axis) must carry the span-1 axis (both other spans are
3 > 2), so every placement is flat; similarly for boxes with b = 2 (the
size-2 axis is the middle axis; the span-1 axis must align with it). Each
layer is an independent rectangle tiling problem for the free W pentomino.
Mechanized check: extents along the thickness axis = [1] only, for all 24
orientations and all axis assignments. Additional unfit sub-case: boxes
with two size-2 axes (2×2×N) — the piece needs two axes ≥ 3.

So: **W tiles 2×M×N (and a×2×c) ⟺ the free W pentomino tiles the
(other-two-dims) rectangle** — with the unfit 2×2×N / 1×2×N exceptions.

### C. Underlying 2D statement (qu5-w, live page fetched 2026-09-01)

* **Published impossibility**: "Impossible: `n*Z` for n ≠ 0 (mod 5)" —
  no W-pentomino rectangle has both sides ≠ 0 mod 5; and "`n*N`" —
  **squares are impossible**.
* **Published tiling examples (bent/infinite only)**: the 2-dim line
  "Z: 5p, ... only 5n" and "N*N as the 5*Z (bend) is tilable" refer to
  **bent** (staircase) 5-wide strips and contrast with the impossible
  squares. Bent-strip tileability is **not** straight-rectangle
  tileability and is not used as an ingredient here.
* **Published straight-rectangle status**: open. No 2d-complete stamp;
  the page itself is stamped "incomplete" (3D).
* **Derived consequence (this audit)**: any W-tileable 2×M×N box must have
  5 | M or 5 | N (published strip rule + layer lemma).
* **Computational evidence**: no W-pentomino rectangle of any area ≤ 200
  (complete, two independent methods); none in {15×15, 20×20, 25×25,
  30×30, 35×35, 40×40, 5×45…5×85, 10×25, 10×30}.

### D. Counterexample search

2D (the layer lemma makes this exhaustive for the 3D family): all
rectangles area ≤ 200 complete unsat; targeted up to 40×40 unsat; 5-wide
strips to 5×85 unsat. 3D solver: W 2×5×5 → 0 solutions. Positive controls
for the lift mechanism (published 2D tilings lifting to thickness-1 3D
boxes) verified on other pieces: L 1×2×5 = 2 solutions, P 1×2×5 = 2
solutions, Y 1×5×10 = 10 solutions — the mechanism works where a 2D
tiling exists. No W counterexample found. **A failed search is evidence
only.**

### E. Classification and replacement

**TOO STRONG — prepare replacement patch** (not applied). The blanket
covers boxes with 5 | (one of the other dims) — e.g. 2×5×N, 2×10×N — where
the published 2D record explicitly leaves the question open, and where a
future W straight-rectangle discovery (5-wide strips are the open class)
would falsify the rule.

Proposed replacement (identical provable core, open cases returned to
UNKNOWN):

```python
# W pentacube: spans {1,3,3}; any size-2 axis forces flat placements
# (mechanized), so a×2×c reduces to W-pentomino tiling (a×c).
# Published (Sillke qu5-w): W-pentomino rectangles with both sides
# != 0 (mod 5) are impossible ("n*Z for n != 0 (modulo 5)"); squares
# are impossible ("n*N").  Straight 5k-wide strips remain open.
if a == 2 or b == 2:
    others = [d for d in (a, b, c) if d != 2]
    if any(d < 3 for d in others):
        return "published_impossible"   # unfit: needs two axes >= 3
    if others[0] % 5 != 0 and others[1] % 5 != 0:
        return "published_impossible"   # published 2D strip rule
    return None                          # open: 5 | one side
```

Impact (dims ≤ 20, volume ≡ 0 mod 5): **70 boxes** `published_impossible →
UNKNOWN` (2×5×N, 2×10×N, … and the b==2 analogues); **0** boxes in the
other direction; **0** conflicts with RAW_PRIMES / PUBLISHED_SOLUTIONS /
SEARCHED_NO_SOLUTION (verified programmatically). The 1×2×N and 2×2×N
unfit boxes stay impossible.

---

## 2. Z — blanket `a <= 2`

### A. Exact existing rule

`catalogues/z_catalogue.py` (ZCatalogue.impossible_reason, line ≈229):

```python
if a <= 2:
    return "published_impossible"
```

`docs/pieces/Z.md` lists "`a <= 2`: impossible" under "Published
impossible families". This classifies **all** 1×M×N and 2×M×N boxes.

### B. Geometric reduction

Z is planar with spans {1,3,3}. Mechanized: in every orientation fitting
2×M×N (M,N ≥ 3) the extent along the size-2 axis is 1 — all placements
flat; each layer is a Z-pentomino rectangle problem. Same for 1×M×N
(all placements flat). Unfit sub-cases: 1×1×N, 1×2×N, 2×2×N (fewer than
two axes ≥ 3). So 1×M×N and 2×M×N ⟺ the free Z pentomino tiles the
(other-dims) rectangle — the reduction itself is a derived theorem.

### C. Underlying 2D statement

* **Published impossibility**: **none exists.** Sillke's qu5-z page has
  *no 2D section at all* (the Z pentacube's first 3D box was found by
  Shindo/Wolf only in 1997). The live Shirakawa Z page's 3D table starts
  at `3x[3-22]xN s:0` — there are **no 1× or 2× rows** to source the rule
  from.
* **Published tiling examples / bent strips**: none for the Z pentomino.
* **Derived consequences**: only volume/fitting conditions.
* **Computational evidence**: no Z-pentomino rectangle area ≤ 200
  (complete, two methods); none in targeted sets up to 40×40; 5×45–5×85
  and 10×25/30 unsat. Strong — but finite.

### D. Counterexample search

As above — no violation found anywhere; no published tiling exists to
lift as a positive control. **Evidence only, not proof.**

### E. Classification and replacement

**TOO STRONG — prepare replacement patch** (not applied). Unlike W, there
is not even a partial published 2D record to narrow to; the entire
thickness-1/2 family rests on computational evidence.

Proposed replacement:

```python
# Z pentacube: spans {1,3,3}; flat in 1- and 2-thick boxes (mechanized),
# reducing to Z-pentomino rectangles.  No published 2D result exists for
# the Z pentomino (Sillke qu5-z has no 2D section; Shirakawa's Z page
# starts at 3x[3-22]xN).  Only the unfit sub-cases are proved here.
if a <= 2:
    if sum(1 for d in (a, b, c) if d >= 3) < 2:
        return "published_impossible"   # unfit: 1x1xN, 1x2xN, 2x2xN
    return None                          # open: reduces to Z-pentomino
```

Impact (dims ≤ 20): **132 boxes** `published_impossible → UNKNOWN`
(1×3×N…, 2×3×N, 2×5×N…); 0 in the other direction; 0 conflicts. The
unfit sub-families (1×1×N, 1×2×N, 2×2×N) stay impossible.

**Note on cost/benefit**: this is the largest narrowing (132 boxes) and
the Z `a ≤ 2` rule may well be *true* — but "no solution found anywhere"
is not a published source, and the catalogue's own semantics
(`published_impossible`) would misstate the evidence. If the project
prefers to retain utility, the honest alternative is to keep the rule but
change its reason string to a non-published class — that requires a
catalogue-semantics decision and is out of scope here.

---

## 3. N — blanket `a <= 1`

### A. Exact existing rule

`catalogues/n_catalogue.py` (NCatalogue.impossible_reason, line ≈102):

```python
if a <= 1:
    return "published_impossible"
```

with the catalogue's own admission two rules later:

```python
# TODO: decode N no-strip impossibility rule
# TODO: decode Zx{3,5} impossibility rule
```

`docs/pieces/N.md` records that the rules "cannot be checked against the
current Shirakawa transcription". The blanket classifies all 1×M×N.

### B. Geometric reduction

N is planar with spans {1,2,4} and is chiral. Mechanized, axis-explicit:
in a 1×M×N box all 24 orientations fit and every placement is flat, and
flat placements realize all 8 dihedral orientations — so **N tiles
1×M×N ⟺ the free N pentomino tiles the M×N rectangle** (reflections
included, which matters: the N pentacube realizes both enantiomers).
Unfit sub-case: 1×1×N (spans {1,2,4} need two axes ≥ 2, one of them ≥ 4;
1×1×N provides only one usable axis).

Note this is a genuine *reduction to the free* pentomino: the 3D piece is
not one-sided in the layer.

### C. Underlying 2D statement (qu5-n, live page fetched 2026-09-01)

* **Published impossibility**: "`Zx{3,5}`" — 3- and 5-wide strips are
  impossible. This is the entire published finite-rectangle record.
* **Published tiling examples (bent/infinite)**: "N*N (the quadrant) is
  possible as the 2*Z bent strip is possible" — a **bent** 2-wide strip
  and the infinite **quadrant** (corner region). These are not straight
  rectangles and are not used as ingredients.
* **Published open question** (verbatim): "u*Z for u odd: 3 and 5
  impossible. ??? what is the smallest u possible ???" — the source
  itself treats even-width and larger odd-width strips as open.
* The Impossible-list entry "Nxk — no strips on side open of width k"
  concerns **one-side-open (semi-infinite) strips** and does not imply
  finite-rectangle impossibility.
* **Computational evidence**: no N-pentomino rectangle area ≤ 200
  (complete, two methods); squares 25×25–40×40 unsat; 5×45–5×55,
  10×25/30 unsat; **2×N straight strips unsat for every N ≤ 200** (so the
  bent-strip/quadrant results have produced no finite rectangle).

### D. Counterexample search

All of the above; no violation found. The quadrant/bent-strip results
make N the *most likely* of the three pieces to eventually yield a
finite rectangle (the source says the quadrant is tileable), so the
blanket rule carries genuine falsification risk, concentrated at
1×2×N and 1×N×N. **No counterexample found; evidence only.**

### E. Classification and replacement

**TOO STRONG — prepare replacement patch** (not applied).

Proposed replacement (keeps the published core; keeps all other existing
N rules untouched — `(2,2)`, `(2,3)`, `(3,3)`, `3×4×5`,
`3×5×{5,6,7,9,10,11}` are published in qu5-n's Impossible list):

```python
if a == 1:
    if b == 1:
        return "published_impossible"   # unfit: needs two axes >= 2
    if b in (3, 5):
        return "published_impossible"   # published: Zx{3,5} strips (qu5-n)
    return None                          # open: 1x2xN and 1xMxN, M >= 4
```

Impact (dims ≤ 20): **50 boxes** `published_impossible → UNKNOWN`
(1×2×N, 1×4×N, 1×6×N, 1×7×N, 1×8×N, …); 0 in the other direction;
0 conflicts. The catalogue's TODO comments should be resolved by this
change (the "Zx{3,5}" rule becomes explicitly encoded).

---

## 4. Cross-cutting observations

1. **The three rules share one failure mode**: a 2D strip impossibility
   (or its absence) was silently promoted to a 3D infinite-family claim.
   The F catalogue removed exactly such a rule on 2026-08 audits; these
   three are the remaining instances of the same pattern.
2. **All three blanket rules are *plausibly true*** — no counterexample
   exists up to substantial search limits (2D complete ≤ 200; squares to
   40×40; strips to 5×85 / 2×200) — but "plausible" is the conjecture
   tier, not the `published_impossible` tier.
3. **Any narrowing is a visible regression** in catalogue coverage
   (70 + 132 + 50 = 252 boxes ≤ 20 dims return to UNKNOWN). The patches
   above are prepared so the human can weigh mathematical hygiene against
   utility. A middle path exists for each piece: per-box
   `SEARCHED_NO_SOLUTION` entries with verified DRAT/LRAT certificates
   (the Z 6×6×10 precedent) for the most-wanted boxes, keeping the
   infinite-family question open.
4. **No existing classification is contradictory**: the narrowings touch
   only boxes currently labelled by the blanket rules themselves
   (0 conflicts with primes/searched/published — verified).
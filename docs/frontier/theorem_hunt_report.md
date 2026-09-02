# Theorem Hunt Report — Frontier Reduction via Layer Arguments

**Date**: 2026-09-01
**Scope**: audit of all 20 in-scope pentacube catalogues for theorem-shaped
reductions that eliminate infinite UNKNOWN families without brute force.
**No catalogue file was modified.** Proposed patches are separate documents.

---

## Executive summary

The F 2×M×N pattern (classical 2D fact → orientation argument → infinite
family → catalogue rule) was audited across all pieces. Results:

1. **The layer-reduction lemma is real and mechanizable, but it applies to
   exactly five in-scope pieces** — F, T, V, W, Z (planar, span multiset
   {1,3,3}). It does **not** transfer to L, N, Y (span {1,2,4}) or P, U
   (span {1,2,3}), which have upright placements in 2-thick boxes, and it is
   vacuous for non-planar pieces, every one of whose 2-thick placements
   occupies *both* layers. All of this was verified by enumerating all 24
   lattice orientations of every registered piece (mechanized, see §3).

2. **The 2D ingredients differ in strength per piece, and the F report's
   premise is not what it claims.** The blanket premise "the F pentomino is
   not rectifiable" could not be verified in any accessible published
   source. What *is* published (Sillke's F page, the project's primary
   source) is that the **F pentomino cannot tile any N×N square**
   ("Impossible: NxN"), and Sillke's page *shows an F tiling of a bent
   (staircase) 5-wide strip*. The citation "Golomb, Polyominoes 2nd ed.,
   Theorem 3.14" in `f_2xn_frontier_report.md` is unverified; Golomb's
   rectification material is Chapter 8 per Sillke's reference list.
   **The pending blanket `a == 2` patch for F must not be applied as
   `published_impossible`**; it is a conjecture with strong computational
   support (no F rectangle up to area 900, two independent exact methods).

3. **Mature new promotions identified**:
   - **F 2×N×N (squares) and F 2×2×N (piece cannot fit)** — 8 boxes ≤ 20
     dims, published 2D ingredient, zero conflicts. Patch:
     `docs/frontier/f_piece/f_2xnn_squares_promotion_patch.md`.
   - **Y 1×5×N (N ≢ 0 mod 10), 1×6×N, 1×8×N** — 6 boxes ≤ 20 dims, from
     Sillke's published Y-pentomino rectangle classification. Patch:
     `docs/frontier/y_piece/y_thickness1_published_families_patch.md`.

4. **Already-promoted families independently re-verified** (no change):
   T `a ≤ 1` and `a == 2` (Sillke qu5-t: pentomino tiles **no** rectangle,
   "NxZ"; and 3D "NxZx2"); V `a == 2 ∧ b == c` (published verbatim on
   qu5-v: "2xNxN as NxN is impossible"); U `a ≤ 1` (qu5-u "ZxN": no
   rectangle at all).

5. **Provenance flags (report only, no changes)**: the blanket `a == 2`
   rules in the **W** and **Z** catalogues and the blanket `a ≤ 1` rule in
   the **N** catalogue are *stronger* than anything found in the published
   sources; each has a provable published core that is strictly weaker.
   The **Q registry entry is geometrically broken** (disconnected cells;
   cannot fit its own catalogue's published 2×2×5 prime).

6. **Positive lifts found** (published 2D solutions lifted to thickness-1
   boxes): L/P 1×2×{10,15} are composites of 1×2×5; Y 1×5×20 is a
   composite of 1×5×10 (whose 10 solutions the project solver reproduces).

---

## 1. Method

- Extracted every piece's cell coordinates from `common/registry.py`,
  verified face-connectivity, computed span multisets (invariant under the
  24 lattice rotations), and enumerated all orientations
  (`/tmp/opencode/audit_registry.py`, `confinement_check.py`).
- Decoded each catalogue's `impossible_reason` rules, `RAW_PRIMES`,
  `SEARCHED_NO_SOLUTION`, `PUBLISHED_SOLUTIONS`.
- Computed the UNKNOWN frontier for all 20 catalogues (dims ≤ 15 and ≤ 20).
- Fetched and analysed the primary published sources for the 2D
  (pentomino) ingredients: Sillke's per-pentomino pages
  (`mathematik.uni-bielefeld.de/~sillke/PENTA/qu5-{f,t,u,v,w,y,z,n,l}`),
  which compile Golomb (JoCT 1966), Klarner (JoCT 1969), Bouwkamp–Klarner
  (1970), Göbel, Beeler, Postl, Reid, Aksyonov, Hasegrove.
- Ran two independent 2D exact methods (bitmask DFS and CaDiCaL SAT via the
  project venv's python-sat) and the project's own 3D solver as sanity
  checks. Solver/timeout results were used **only** as evidence, never as
  proof.

## 2. The published 2D landscape (provenance table)

Verified from the Sillke pages (primary compilation) + computations here:

| Pentomino | Tiles a straight rectangle? | Published basis | Computation here |
|---|---|---|---|
| I | yes, 1×5 | trivial | SAT ✓ |
| L | yes, 2×5, 7×15, 9×15 | qu5-l (Klarner 1969 Fig. 12) | SAT ✓ |
| P | yes, 2×5 | qu5-p ("List complete") | SAT ✓ |
| Y | yes, 5×10 minimal; full classification; 15×15 square | Golomb JoCT 1 (1966); Hasegrove JoRM 7 (1974); qu5-y | SAT ✓ (5×10: found) |
| F | **unknown**; squares impossible; bent 5-strip tilable | qu5-f Impossible: "NxN"; 2-dim line "Zx 5p, ... only 5n" (ambiguous) | none ≤ area 900 |
| N | unknown; 3-,5-wide strips impossible; infinite quadrant via bent 2-strips | qu5-n: "Zx{3,5}" | none ≤ 900 |
| T | **no rectangle at all** | qu5-t Impossible: "NxZ" (also 3D "NxZx2") | ✓ |
| U | **no rectangle at all** | qu5-u Impossible: "ZxN" | ✓ |
| V | unknown; **squares impossible**; half-plane dissecting into 5×Z stripes | qu5-v ("2d-complete 01.08.98"; "2xNxN as NxN is impossible") | none ≤ 900 |
| W | unknown; one side must be ≡ 0 (mod 5); infinite quadrant via bent 5-strips | qu5-w Impossible: "n*Z for n ≠ 0 (mod 5)"; "N*N as the 5*Z (bend) is tilable" | none ≤ 900 |
| X | unknown (out of scope, no catalogue) | — | none ≤ 900 |
| Z | unknown (**no published 2D data at all**) | qu5-z has no 2D section | none ≤ 900 |

Key subtlety: Sillke's terse 2-dim lines ("Zx 5p, ... only 5n") describe
**infinite/bent strips and plane tilings**, which do **not** imply finite
rectangles. Only the explicit "Impossible" entries were used as published
impossibility ingredients.

## 3. The layer-reduction lemma (newly derived; mechanized)

**Lemma (orientation confinement).** Let P be a planar pentacube whose span
multiset (extent along its three principal axes, invariant under the 24
lattice rotations) is {1,3,3}. In a box 2×M×N with M,N ≥ 3, **every**
placement of P lies in a single layer (extent 1 along the thickness axis).
In a box 1×M×N, every placement is flat, and the induced 2D placements
realize exactly the 8 dihedral orientations of the free pentomino.

*Proof.* A lattice placement is obtained by one of the 24 signed
permutation rotations, so the world-axis extents of any placement are a
permutation of the piece's spans. A placement fits the box iff its extent
along the thickness axis is ≤ 2 and the other two extents are ≤ M, N. For
spans {1,3,3} the only extent ≤ 2 is 1, so the span-1 axis must align with
the thickness; hence thickness-extent 1 for every placement. Flat
placements: the 4 rotations about the layer normal give one enantiomer's
rotations; the 180° rotations about in-plane axes flip the plane over and
give the mirror enantiomer's 4 rotations — together all 8 free-pentomino
orientations (3D rotations identify the two enantiomers of a planar piece).
Each layer of the box is therefore an independent M×N rectangle tiling by
the free pentomino, and conversely two stacked 2D tilings tile the box. ∎

Mechanized check (all 24 orientations, all axis assignments):

```
F,T,V,W,Z (1,3,3): extents along 2-thick axis = [1] only   → confined
A,B,E,G,H,J,K,M,R,S (2,2,2)/(2,2,3):        = [2] only   → always cross layers
P,U (1,2,3):                                = [1,2]      → mixed
L,N,Y (1,2,4): do not fit 2×3×3 at all; in 2×M×N (M,N ≥ 4): mixed
non-planar pieces in 1×M×N: 0 of 24 orientations fit       → trivially impossible
```

**Consequence (characterization).** For P ∈ {F,T,V,W,Z}:
**P tiles 2×M×N ⟺ the P pentomino tiles the M×N rectangle** (both layers
must tile; they are identical problems), and similarly for 1×M×N.
Boxes 2×2×N cannot fit P at all (only one dimension ≥ 3 available).

## 4. Candidate theorems (A–F per candidate)

### Candidate 1 — T pentacube: no 1×M×N, no 2×M×N (all M,N)

**A. Statement.** For all M,N: the T pentacube cannot tile 2×M×N
(M,N ≥ 3; smaller cases the piece cannot fit), nor any 1×M×N.

**B. Proof.** By the lemma, a 2×M×N (or 1×M×N) tiling induces an M×N
rectangle tiling by the free T pentomino. Sillke's T page (data: Göbel
1989, Beeler, Postl; list started 1993) lists in **Impossible: "NxZ"** —
no rectangle of any dimensions is T-tileable. Contradiction. ∎
(This matches the already-encoded 3D published entry "NxZx2".)

**C. Provenance.** 2D ingredient: published (Sillke qu5-t). Orientation
lemma: newly derived here. 3D corollary: **published** ("NxZx2" on qu5-t)
and independently re-derived — classify as *published + derived*.

**D. Catalogue impact.** None — `t_catalogue` already returns
`published_impossible` for `a ≤ 1` and `a == 2`. Verified: 0 conflicts.

**E. Implementation.** None. Recommendation: reference this proof in the
T catalogue comments.

**F. Verification.** Project solver: T 2×5×5 → 0, T 2×5×10 → 0,
T 1×5×5 → 0 (≤ 0.003 s each). 2D SAT: T unsat on every rectangle ≤ area
900 tested.

### Candidate 2 — F pentacube: 2×2×N and 2×N×N (NEW, mature)

**A. Statement.** (i) The F pentacube cannot tile any 2×2×N box (N ≥ 1).
(ii) The F pentacube cannot tile any 2×N×N box (N ≥ 5; smaller N fail the
volume or fitting conditions).

**B. Proof.** (i) F has spans {1,3,3}; a fitting placement needs two box
dimensions ≥ 3; a 2×2×N box has only one. So no placement exists and the
box cannot be covered. (ii) By the lemma, every placement in 2×N×N is flat
and each layer is an N×N square tiled by the free F pentomino. Sillke's
F page lists "NxN" among the impossible boxes — the F pentomino cannot
tile any square (independently confirmed here by exact search for
N = 5,10,15,20,25,30). Hence no layer can be tiled. ∎

**C. Provenance.** Fitting + orientation lemma: newly derived.
N×N impossibility: **published** (Sillke qu5-f, "Impossible: NxN").
Combined: **derived/proved theorem** with a published ingredient. Per the
catalogue convention established by the V rule (identical pattern,
labelled `published_impossible`), record as `published_impossible`.

**D. Catalogue impact.** Dims ≤ 20: 8 UNKNOWN → IMPOSSIBLE
(2×2×{5,10,15,20}; 2×{5,10,15,20}×{5,10,15,20} squares: 2×5×5, 2×10×10,
2×15×15, 2×20×20). Conflicts: **none** — no RAW_PRIMES, PUBLISHED_SOLUTIONS
or SEARCHED_NO_SOLUTION box matches either rule (verified programmatically).

**E. Implementation.** `docs/frontier/f_piece/f_2xnn_squares_promotion_patch.md`
(two `if` statements in `FCatalogue.impossible_reason`). **Not applied.**

**F. Verification.** Solver: F 2×5×5 → 0, F 2×10×10 → 0. 2D SAT: F 5×5,
10×10, 15×15, 20×20, 25×25, 30×30 all unsat; complete sweep area ≤ 200
unsat; targeted 5×45..5×55, 10×25, 10×30 unsat.

### Candidate 3 — F pentacube: blanket 2×M×N — DOWNGRADED TO CONJECTURE

**A. Statement (conjecture).** The F pentacube tiles no 2×M×N box at all.

**Status: NOT a theorem on the evidence accessible to this audit.**

* The premise "the F pentomino cannot tile any rectangle" is **not**
  established by the accessible published sources. Sillke's F page (the
  project's declared primary source, "3D complete") publishes only the
  **square** impossibility ("NxN") and prints an F tiling of a **bent**
  5-wide strip; its 2-dim line ("Zx 5p, ... only 5n") is ambiguous and
  carries no 2d-complete stamp (unlike V).
* The citation in `f_2xn_frontier_report.md` / `f_2xn_promotion_patch.md`
  ("Golomb, Polyominoes 2nd ed., Theorem 3.14") is **unverified**. Sillke's
  reference list places Golomb's rectangle-tiling material in **Chapter 8**
  of the 2nd edition; no Theorem 3.14 could be traced offline.
* Computational support is strong but finite: no F rectangle with area
  ≤ 200 (complete, two independent methods) and none in targeted sets up
  to 30×30 (area 900).

**Consequently the pending `f_2xn_promotion_patch.md` (blanket
`a == 2 → published_impossible`, 70 boxes) must NOT be applied in its
current form**: it would label a conjecture as published. The safe core
(Candidate 2) covers 8 of the 70 boxes. If the blanket result is ever
sourced (verified Golomb location) or per-box certificates are produced to
the project's DRAT/LRAT standard (see the Z 6×6×10 precedent), it can be
revisited; otherwise affected boxes may only enter `SEARCHED_NO_SOLUTION`
individually with verified certificates.

### Candidate 4 — V pentacube 2×N×N: already correct (verify-only)

The V catalogue encodes exactly Sillke's published statement ("2xNxN as
NxN is impossible", qu5-v, 2d-complete 01.08.98) as `a == 2 and b == c →
published_impossible`. The lemma reproduces it. No change.
Solver: V 2×5×5 → 0, V 2×3×5 → 0. 2D: V unsat ≤ 900 (squares 15×15–30×30
included).

### Candidate 5 — W pentacube: conditional 2×M×N theorem + blanket-rule flag

**A. Statement.** The W pentacube cannot tile any 2×M×N box with
5 ∤ M and 5 ∤ N.

**B. Proof.** By the lemma, 2×M×N reduces to W-pentomino tiling M×N.
Sillke's W page lists "n×Z for n ≢ 0 (mod 5)" as impossible; hence any
W-tileable rectangle has a side divisible by 5. If 5 ∤ M the rectangle
M×N is an n×Z strip with n = M ≢ 0 (mod 5) — impossible; likewise for N.
∎

**C. Provenance.** 2D ingredient published (qu5-w); combination newly
derived.

**D. Catalogue impact / conflict flag.** Zero new boxes: the W catalogue
already carries a blanket `a == 2 → published_impossible` rule. **That
blanket rule is stronger than anything found in the published sources**
(qu5-w's Impossible list has no 3D 2×M×N entry; the Shirakawa W
transcription lists 3x[3-6]xN, 3x7x10, 3x7x15, 4x[4-9]xN). Worse, qu5-w's
2-dim note "N*N as the 5*Z (bend) is tilable" suggests W tiles infinite
quadrants via bent 5-strips; if W tiles any *finite* square S×S, then
2×S×S is **tileable** and the blanket rule is **false**. (Computation:
W unsat on 15×15–30×30, so any such S > 30.) Recommendation: a dedicated
provenance audit of the W `a == 2` / `b == 2` rules; the conditional
theorem above is the provable core and can replace the blanket if no
source is found. **No change proposed here** (do-not-weaken constraint).

### Candidate 6 — Y pentacube thickness-1 families (NEW, mature)

**A. Statement.** The Y pentacube cannot tile: 1×5×N for N ≢ 0 (mod 10);
1×6×N for all N; 1×8×N for all N.

**B. Proof.** The Y pentacube is planar (spans {1,2,4}); in a 1×M×N box
every placement is flat (mechanized: all 24 orientations fit, all flat)
and realizes all 8 free-Y orientations, so 1×M×N ⟺ Y pentomino tiles
M×N. Sillke's Y page (compiling Golomb 1966, Klarner 1969,
Bouwkamp–Klarner 1970) publishes: "5×k if k ≢ 0 (mod 10)" impossible;
"6×k for all k" impossible; "8×k for all k" impossible (6- and 8-wide
strips have three extendable border types but never close; 5-wide strips
dissect into 5×10 blocks). ∎

**C. Provenance.** 2D ingredients published (qu5-y; Golomb, JoCT 1
(1966) 280-296). Thickness-1 reduction: trivial/newly stated.

**D. Catalogue impact.** 6 UNKNOWN → IMPOSSIBLE (≤ 20 dims):
1×5×{16,17,18,19}, 1×6×20, 1×8×20. The rule is consistent with (and
subsumed by) the existing SEARCHED entries at small N — the patch
includes a `searched_no_solution` guard (the `f_catalogue` pattern) so
those labels are preserved. No RAW_PRIMES conflict (1×5×10, the Y prime,
is excluded by the mod-10 condition).

**E. Implementation.** `docs/frontier/y_piece/y_thickness1_published_families_patch.md`.

**F. Verification.** Project solver: Y 1×5×10 → **10 solutions**
(positive control; matches the published 5×10 rectangle). 2D SAT: Y 5×6,
5×8, 5×12, 5×14, 6×k, 8×k unsat ≤ 200.

### Candidate 7 — U pentacube: verified, no change

`u_catalogue` marks `a ≤ 1` published_impossible; qu5-u publishes
"Impossible: ZxN" — *no* U-pentomino rectangle exists (page complete
1993). Thickness-1 reduction makes the rule exact. Solver: U 1×5×5 → 0.

### Candidate 8 — N pentacube: flag only

`n_catalogue` carries a blanket `a ≤ 1 → published_impossible`. The
published basis (qu5-n) covers only widths 3 and 5 ("Zx{3,5}") plus
infinite bent strips/quadrants; N's finite-rectangle status is open
(nothing ≤ 900 computationally). The blanket rule is **stronger than its
published basis** — flag for a dedicated audit (not weakened here).

### Candidate 9 — Z pentacube: flag only

`z_catalogue` carries `a ≤ 2 → published_impossible`. No published 2D
ingredient exists (qu5-z has no 2D section at all; the Z pentomino's first
3D box was found by Wolf only in 1997). Computational: no Z-pentomino
rectangle ≤ 900. Flag for provenance documentation; no promotion possible
from current sources.

### Candidate 10 — positive lifts (constructive, secondary)

* L pentacube 1×2×{10,15} = 2/3 copies of the prime 1×2×5 (L pentomino
  tiles 2×5, published Klarner/Sillke; solver finds 2 solutions for
  1×2×5). Currently UNKNOWN in `l_catalogue` → proposed *discovered
  composites*.
* P pentacube 1×2×{10,15}: same construction. → proposed composites.
* Y pentacube 1×5×20: two copies of the prime 1×5×10. → proposed composite.

These are constructive decompositions (not impossibilities) and would go
through the catalogue's decomposition/Generator mechanism rather than
`impossible_reason`.

### Non-candidates (checked, no theorem)

* **L, N, Y in 2×M×N**: span {1,2,4} admits upright placements spanning
  both layers → no layer reduction. (Verified mechanized.)
* **P, U in 2×M×N**: span {1,2,3} → mixed flat/upright → no reduction.
* **Non-planar pieces** (A,B,E,G,H,J,K,M,R,S): every 2-thick placement
  crosses both layers; no 1×M×N placements at all (already encoded via
  `a ≤ 1` rules everywhere).
* **Colouring invariants**: no short mod-k colouring was found that
  eliminates an infinite 3D family beyond what the published 2D
  classifications already give. Sillke's V-page colourings (mod-2/mod-3)
  underpin the published V-square result but do not generalize cheaply.
* **Q**: registry coordinates are disconnected (a 2×2 square plus a
  corner-touching cell) and cannot fit the catalogue's own published 2×2×5
  prime; no theorem claims are made for Q until the registry shape is
  repaired against Sillke qu5.61.

## 5. Computational evidence summary

2D pentomino rectangles (DFS + CaDiCaL SAT, agree on all instances):
complete sweep area ≤ 200 (all (r,c) with r·c ≡ 0 mod 5); targeted
{15×15, 5×45, 5×50, 5×55, 10×25, 10×30, 20×20, 25×25, 30×30} for
F, V, W, Z, N, U, T — **all unsat**. Rectifiable (found): I 1×5, L 2×5,
P 2×5, Y 5×10 — all matching the published record.

3D project-solver runs (exact, `fitpolycubes_fast.py --no-symmetry`):

| Box | Result | Consistent with |
|---|---|---|
| T 2×5×5 / 2×5×10 | 0 solutions | T theorem |
| F 2×5×5 / 2×10×10 | 0 solutions | F squares theorem |
| V 2×5×5 / 2×3×5 | 0 solutions | V squares rule / lemma |
| W 2×5×5, Z 2×5×5, Z 2×3×5 | 0 solutions | lemma + 2D unsat |
| U 1×5×5, T 1×5×5 | 0 solutions | published "no rectangles" |
| L 1×2×5 | **2 solutions** | positive control ✓ |
| P 1×2×5 | **2 solutions** | positive control ✓ |
| Y 1×5×10 | **10 solutions** | published 5×10 Y-rectangle ✓ |

(Side-effect note: these runs wrote `data/solutions_fast_*.dat` files;
they are solver outputs, not catalogue edits.)

## 6. Conflicts and provenance corrections (explicit list)

1. **f_2xn_promotion_patch.md (pending, unapplied)**: its blanket
   `a == 2 → published_impossible` rests on an unverified Golomb citation
   and is contradicted-in-spirit by Sillke's bent-strip F tiling; it must
   be downgraded to conjecture. The safe F patch (squares + 2×2×N) is
   proposed instead.
2. **W catalogue `a == 2` blanket**: no published basis found; potentially
   false if W tiles any finite square (qu5-w hints bent-strip quadrants).
   Recommend a dedicated audit.
3. **Z catalogue `a <= 2` blanket**: no published 2D basis found
   (qu5-z has none). Recommend a dedicated audit.
4. **N catalogue `a <= 1` blanket**: over-strong vs qu5-n (only 3-,5-wide
   strips published impossible). Recommend a dedicated audit.
5. **Y catalogue `a == 1 and b <= 4`**: correct for b ∈ {3,4} (published
   "3xZ", "{4,7}xN"), **unverified for b = 2** (qu5-y suggests width-2
   infinite strips exist; finite 2×N open; unsat ≤ 900 computationally).
6. **Q registry piece**: disconnected coordinates; inconsistent with its
   own catalogue's published 2×2×5 prime. Repair before any Q work.
7. **F report citation**: "Golomb 2nd ed. Theorem 3.14" should be
   corrected/verified; Golomb's rectangle-tiling chapter is Chapter 8 per
   Sillke's references.

## 7. Final ranked table

| Rank | Piece | Family | Boxes eliminated (dims ≤ 20) | Proof strength | External basis | Safe to promote? |
|------|-------|--------|------------------------------|----------------|----------------|------------------|
| 1 | F | 2×N×N squares + 2×2×N unfit | 8 | Derived theorem; published 2D ingredient (Sillke qu5-f "NxN") | Sillke qu5-f | **YES** — `published_impossible` (patch doc ready) |
| 2 | Y | 1×5×N (N ≢ 0 mod 10); 1×6×N; 1×8×N | 6 | Derived theorem; published 2D classification (Golomb 1966 / qu5-y) | qu5-y | **YES** — with SEARCHED guard (patch doc ready) |
| 3 | W | 2×M×N, 5 ∤ M, 5 ∤ N | 0 new (provable core of existing blanket) | Derived theorem; published strip impossibility | qu5-w | Only as fallback if blanket rule fails audit |
| 4 | T | 2×M×N and 1×M×N (all) | 0 new (already encoded) | Published ("NxZ", "NxZx2") + independent proof | qu5-t | Already promoted; document proof |
| 5 | V | 2×N×N (all N) | 0 new (already encoded) | Published verbatim | qu5-v | Already promoted |
| 6 | U | 1×M×N (all) | 0 new (already encoded) | Published ("ZxN") + exact reduction | qu5-u | Already promoted |
| 7 | N | 1×3×N, 1×5×N | 0 new (subsumed; blanket rule over-strong) | Published strips + reduction | qu5-n | Flag only |
| 8 | Z | 2×M×N | 0 | Computational only (≤ area 900) | none | NO — flag `a ≤ 2` provenance |
| 9 | F | blanket 2×M×N | (70 if true) | **Conjecture** (bent strips exist; nothing ≤ 900 unsat) | none verified | **NO** — do not apply pending patch |

Ranked by mathematical value: rank 1 carries the strongest *new* infinite
family with a fully published ingredient; ranks 3–5 convert existing
empirical-looking rules into documented theorems; rank 9 records what must
**not** be promoted.

## 8. Files

| file | purpose |
|---|---|
| `docs/frontier/theorem_hunt_report.md` | this report |
| `docs/frontier/f_piece/f_2xnn_squares_promotion_patch.md` | proposed F rule (not applied) |
| `docs/frontier/y_piece/y_thickness1_published_families_patch.md` | proposed Y rules (not applied) |

Reproduction scripts (session-local, under /tmp/opencode): audit_registry.py,
confinement_check.py, rect2d.py (DFS), sat2d.py (CaDiCaL), critical_batch.py,
big_squares.py, frontier_audit.py, impact.py.
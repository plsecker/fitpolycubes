# Z Final Disposition — Thickness-1/2 Rule (`a <= 2 → published_impossible`)

**Date**: 2026-09-02
**Scope**: Z only. W was not revisited; N was not analysed.
**Status**: AUDIT ONLY — no catalogue or source file modified. The recommended
patch in §9 is a proposal and requires human approval.
**Method standard**: published fact → derived theorem → machine-checked
result → computational evidence → conjecture. Finite UNSAT searches do not
promote to proofs; ambiguous source notation is not reinterpreted.

---

## 1. Executive conclusion

**Verdict: NARROW — PROVED SUBSET.**

The blanket `a <= 2 → published_impossible` in `catalogues/z_catalogue.py`
(line ≈229, no provenance comment) is **not mathematically or publicly
justified** for the families it claims:

* There is **no published theorem** that the Z pentomino cannot tile a
  finite rectangle, and **no published Z-pentomino rectangle result of any
  kind** (positive or negative) in the sources consulted (§3).
* The 3D reduction itself is sound and was re-verified mechanically (§2):
  every thickness-1/2 placement is layer-confined, so `1×M×N` and `2×M×N`
  boxes are exactly Z-pentomino rectangle problems. But the underlying 2D
  question is **open** (§4).
* The strongest *new* result of this audit is a hand proof that the Z
  pentomino tiles **no `3×N` rectangle, for any N** (§5), plus a
  machine-checked extension: the first column of a `w×N` strip admits no
  valid left-edge cover for **every width w ≤ 64**, so no Z rectangle with
  min side ≤ 64 exists (§5–§6). These are *derived* results of this audit,
  not published facts, and are labelled as such.

**Recommended replacement** (§9): keep only (i) the piece-unfit sub-cases
(`1×1×N`, `1×2×N`, `2×2×N`) and (ii) the `1×3×N` / `2×3×N` strip families
(hand theorem, §5) as impossible; return everything else in the `a ≤ 2`
family to UNKNOWN. Exact impact: **66 boxes (dims ≤ 15) and 124 boxes
(dims ≤ 20) return to UNKNOWN** (§8), zero conflicts with any other
catalogue class.

---

## 2. Geometry lemma

The Z pentacube (`common/registry.py`) is the planar piece
`{(0,0,0),(1,0,0),(1,1,0),(1,2,0),(2,2,0)}` — the free Z pentomino (3×3
bounding box) extruded to thickness 1. Spans **{1,3,3}**.

**Lemma (mechanized, all 24 proper-rotation orientations, axis-explicit).**

1. *Thickness-1 boxes.* In every orientation that fits a `1×M×N` box
   (M, N ≥ 3), the extent along the size-1 axis is exactly 1: every
   placement lies in the single layer. The realized in-plane shapes are
   exactly the 4 fixed orientations of the **free** Z pentomino (both
   chiralities — the S-mirror is realized by a proper 3D rotation, a
   180° turn about an in-plane axis).
2. *Thickness-2 boxes.* The spans are {1,3,3} and both 3-spans exceed 2,
   so in every orientation fitting a `2×M×N` box (M, N ≥ 3) the size-2
   axis must carry the span-1 axis: **the thickness axis is forced**, every
   placement is flat, and each placement lies in layer 0 or layer 1.
3. *Unfit sub-cases.* No orientation fits `1×1×N`, `1×2×N`, `2×2×N`
   (the piece needs two axes of extent ≥ 3; verified: 0 of 24 orientations
   fit, for N = 3 and N = 10).
4. *Control.* In `3×3×3` there exist upright placements (16 of 24
   orientations span 3 along an in-plane axis): the confinement is special
   to thickness ≤ 2, so the lemma does not silently over-extend.

Mechanical check script: 24/24 orientations tested against
`1×{3,3..}×{3..}` and `2×{...}×{...}` boxes; extents along the thin axis
= {1} in every fitting case; realized layer shapes = full free-pentomino
orbit (4 fixed orientations).

**Consequence (theorem).** For a ∈ {1, 2} and b, c ≥ 3:

* Z tiles `1×b×c` ⟺ the free Z pentomino tiles the `b×c` rectangle.
* Z tiles `2×b×c` ⟺ the free Z pentomino tiles the `b×c` rectangle
  (two independent layer copies; existence is equivalent).

So the entire thickness-1/2 3D question **is exactly** the 2D question:
*does the free Z pentomino tile any finite rectangle?*

---

## 3. Published-source analysis

Sources inspected (live fetches, 2026-09-02, unless noted):

### 3.1 Sillke, `PENTA/qu5-z` (primary project source for Z)

Contains **only 3D content**: the 1997 Wolf (= Yoshiya Wolf Shindo)
packings of `6×6×25` and `6×10×10`, with diagrams and a reference to
Wolf's homepage. **There is no 2D section at all.**

This absence is meaningful, because Sillke's sibling pages in the same
series *do* record 2D results whenever he had them:

| page | 2-dim section content |
|---|---|
| `qu5-f` (F) | `Zx 5p, ... only 5n` (5-wide strip results) |
| `qu5-t` (T) | `ZxZ` (squares) |
| `qu5-w` (W) | strip rule "n≠0 (mod 5)", squares, bent strips |
| `qu5-n` (N) | `Zx{3,5}` strips, bent strip / quadrant remarks |
| **`qu5-z` (Z)** | **— none —** |

(Interpretation caveat: Sillke's `Z×…` / `n*Z` notation inside the F/W/N
pages is the same terse notation that made the W investigation
unresolvable; it is **not** reinterpreted here, and nothing in this
document depends on it. The only fact used is the *presence/absence* of a
2D section, which is notation-independent.)

### 3.2 Shirakawa, *Box Packing Collection — Z* (`puzzlewillbeplayed.com/Shirakawa/Z.html`)

The 3D table starts at `3x[3-22]xN s:0` (2013). **There are no `1×` or
`2×` rows.** All other rows are `a ≥ 3` (families `3×…`, `4×…`, `5×…`,
per-box entries, primes). The page credits Shindo (1997) for the first Z
boxes. No 2D content.

### 3.3 Michael Reid, *Box Collection* (via Wayback snapshot 2019-09-21; cflmath.com now lapsed)

The Z pentacube entry lists: **minimal `6×10×10`** (by Yoshiya "Wolf"
Shindo), also `4×10×50`, `5×8×20`, `5×9×15`, `6×6×25` (Shindo),
`10×10×10` (Sicherman). **No `1×M×N` and no `2×M×N` box is listed.** By
contrast, flat pentacubes whose 2D prototypes have known rectangles *do*
carry thickness-1 entries (e.g. the Y pentacube: minimal `1×5×10`, with a
long list of `1×M×N` boxes). Reid's page is a packing list, not an
impossibility list — so this is evidence that **no thickness-1/2 Z box is
known to the experts**, not a published impossibility.

### 3.4 General references

* Wikipedia *Pentomino* / MathWorld *Pentomino*: nothing on
  single-pentomino rectangle tilings; no per-piece rectifiability data.
* Golomb, *Polyominoes* (2nd ed.): full text not accessible in this
  environment (archive.org items restricted; full-text search unavailable).
  **No verifiable citation could be obtained.** Note the project precedent:
  the analogous "Golomb Theorem 3.14" citation used for the F piece failed
  verification and was demoted on 2026-09-01
  (`docs/pieces/F.md`, `docs/frontier/f_piece/f_2xn_promotion_patch.md`).
  No Golomb citation is claimed for Z here.

### 3.5 Region-type separation (explicit)

| region class | published Z-pentomino record |
|---|---|
| **finite rectangles** | **none** (no impossibility, no tiling) |
| infinite strips (2-sided) | none found for Z |
| semi-infinite strips (1-side-open) | none found for Z |
| bent strips | none found for Z (contrast: W and N have bent-strip results) |
| half-planes / quadrants | none found for Z |
| 3D boxes | Shindo/Wolf 1997 (`6×6×25`, `6×10×10`); Shirakawa 2013–15 tables; Reid's collection |

No theorem is transferred between region classes anywhere in this
document.

---

## 4. Finite-rectangle theorem status

**Central question: is there a published theorem that Z cannot tile any
finite rectangle?**

**Answer: NO — not found.** After inspection of every authoritative source
used by this project for Z (§3) plus the general references, no published
impossibility statement, no published tiling, and no per-piece
rectifiability table covering Z was found. Consequently:

* The finite-rectangle problem for the Z pentomino is recorded as
  **unresolved/open** within the project's evidence hierarchy.
* Non-rectifiability is **not** inferred from computation (§6 is evidence
  only).
* The current blanket rule has **no published basis**: it classifies
  `1×M×N` and `2×M×N` as `published_impossible` while the published record
  is silent on the underlying 2D question.

---

## 5. Elementary theorem discovered (derived this audit)

### 5.1 Hand theorem: no `3×N` rectangle

**Theorem.** The free Z pentomino tiles no `3×N` rectangle, for any N ≥ 1.

*Proof.* In a 3-row rectangle every placement has vertical offset 0 and
spans exactly 3 columns, so the cells of column 0 can only be covered by
pieces anchored at column 0. With b = 0 the four orientations have
column-0 footprints `ZH(0) = {0}`, `SH(0) = {2}`, `ZV1(0) = {0,1}`,
`ZV2(0) = {1,2}` (rows), and column-1 footprints `ZH: {0,1,2}`,
`SH: {0,1,2}`, `ZV1: {1}`, `ZV2: {1}`. A set of anchored pieces covering
column 0 exactly must partition {0,1,2}:

* `ZH(0) ∪ SH(0)` covers {0,2} and leaves row 1; no remaining piece has
  column-0 footprint {1} — impossible.
* `ZV1(0) ∪ SH(0)`: column-1 footprints {1} and {0,1,2} overlap — the two
  pieces would both occupy cell (1,1) — impossible.
* `ZH(0) ∪ ZV2(0)`: column-1 footprints {0,1,2} and {1} overlap —
  impossible.

No partition of column 0 exists; hence no tiling exists. ∎

(Computationally cross-checked: exhaustive search finds 0 tilings of
`3×N` for N ∈ {5, 10, …, 45}, with the search harness validated on
positive controls — two L pentominoes tile `2×5`, two P pentominoes tile
`2×5`.)

**3D corollary (via the §2 lemma):** `1×3×N` and `2×3×N` are impossible
for all N ≥ 3. These are *derived-theorem* results; no published source
states them.

### 5.2 Necessary conditions (labelled — not impossibility theorems)

* `5 | M·N` (volume) and `min(M, N) ≥ 3` (bounding box 3×3).
* A `(x+y) mod 4` diagonal-colouring framework was set up: the four fixed
  orientations have colour profiles `(2,1,1,1)` (ZH, SV) and `(0,1,3,1)`
  (SH, ZV1) up to translation. The induced integer system was tested for
  contradiction over 111 rectangle families (3 ≤ M ≤ 15, M ≤ N ≤ 30,
  5 | MN): **feasible in every case** — the colouring yields necessary
  conditions only, and no impossibility was claimed from it.
* Column-weighting with translation-invariant per-piece weights forces the
  weight function to be constant (recurrence `f(a+2)+3f(a+1)+f(a) = const`
  has no non-constant periodic solutions), so simple row/column mod-k
  weightings cannot decide the question.

### 5.3 Machine-checked strip theorem (evidence tier: machine-checked derived result)

A column-scan profile DP over width-w strips was implemented and validated
against independent brute-force exact cover on 24 instances across three
pieces (including positive controls: P tiles `4×5`, `5×10`, `6×10`).
For pieces spanning exactly 3 columns (true for all four Z orientations),
`w×N` is tileable ⟺ the acceptance state (full, full) is reachable from
the initial state in the (column-independent) transition graph — so
unreachability is an **all-N** impossibility for that width.

Result: the set of piece-sets anchored at column 0 that exactly cover the
first column with pairwise-disjoint column-1 and column-2 footprints is
**empty for every width w = 3, 4, …, 64**. The finding was re-confirmed by
a second, independently written constraint-level decomposition
(partition / +col1-disjointness / +col2-disjointness): partitions exist at
level 0, survive col-1 disjointness for even w, but **none survive col-2
disjointness at any tested width**.

**Consequence (machine-checked):** no Z-pentomino rectangle exists with
min side ≤ 64, for any length. Via the §2 lemma the same holds for
`1×w×N` and `2×w×N` boxes with the smaller layer side ≤ 64.

This is stronger than any finite UNSAT list, but it is still a *derived,
machine-checked* result (this audit's code, not an independently verified
certificate), so it is recorded below the published-fact tier.

---

## 6. Computational evidence (supporting only)

* Prior project evidence (2026-09-01 audit): no Z-pentomino rectangle of
  area ≤ 200 (complete, two independent methods); targeted searches to
  40×40, 5×45–5×85, 10×25/30 — all unsat.
* This audit: the §5.3 strip result (all widths ≤ 64, all lengths) and the
  §5.1 exhaustive `3×N` checks.
* No counterexample (tileable Z rectangle) exists anywhere in the tested
  range; none is known to the published record (§3.3).

All of this is **evidence, not proof of non-rectifiability in general**.

---

## 7. Catalogue rule disposition

Current implementation (`catalogues/z_catalogue.py`, `impossible_reason`,
line ≈229):

```python
if a <= 2:
    return "published_impossible"
```

with `docs/pieces/Z.md` listing "`a <= 2`: impossible" under "Published
impossible families".

**Assessment: NARROW — PROVED SUBSET (blanket is too strong as
`published_impossible`).**

* The *reduction* half of the rule is a proved theorem (§2).
* The *impossibility* half rests on nothing published (§3–§4) and on no
  proved theorem (§5 proves only the `3×N` strips and the machine-checked
  width ≤ 64 family).
* The `published_impossible` label therefore misstates the evidence for
  every non-unfit box with layer width ≥ 4 — exactly the failure mode the
  2026-09-01 W/Z/N audit identified ("a 2D strip impossibility (or its
  absence) silently promoted to a 3D infinite-family claim"), here with
  the absence case.
* No counterexample exists (no known tileable Z rectangle), so the rule is
  **not FALSE**; and it is not wholly unsupported (the unfit sub-cases are
  rigorous), so it is not plainly REMOVE — it is a **provable subset**
  (unfit + `3×N` strips) inside an over-broad blanket.

Provenance of the current label: none recorded in the code; no source in
`docs/pieces/Z.md` or the Shirakawa/Sillke transcriptions supports it. The
label appears to be folklore ("Z can't tile rectangles, so 1- and 2-thick
boxes are out") promoted past the project's own standard.

---

## 8. Exact classification impact

Recomputed programmatically against the current repository
(`Z_CATALOGUE.impossible_reason`), canonical boxes `a ≤ b ≤ c`, all dims
≤ threshold, `5 | abc` (the audit tool's enumeration convention):

| measure | dims ≤ 15 | dims ≤ 20 |
|---|---|---|
| boxes enumerated | 316 | 724 |
| currently classified **by the blanket** (`a ≤ 2`, `published_impossible`) | **81** | **144** |
| — stay impossible: piece-unfit (`1×1×N`, `1×2×N`, `2×2×N`) | 9 | 12 |
| — stay impossible: derived `3×N` strip theorem (`1×3×N`, `2×3×N`) | 6 | 8 |
| **would return to UNKNOWN** | **66** | **124** |
| conflicts with RAW_PRIMES | 0 | 0 |
| conflicts with PUBLISHED_SOLUTIONS | 0 | 0 |
| conflicts with SEARCHED_NO_SOLUTION | 0 | 0 |
| conflicts with other impossibility rules (`3×[3-22]`, `4×[4-9]`, `4×10×[10-45]`, `5×10×[10-18]`, `3×23×50`, `5×{5,6,7}`, `7×7`, per-box list, `SEARCHED_NO_SOLUTION`) | 0 | 0 |
| blanket boxes also reachable by any other rule (double classification) | 0 | 0 |

Historical-number reconciliation: the 2026-09-01 audit quoted "132 boxes
at dims ≤ 20". That figure reproduces exactly as *blanket minus unfit*
(144 − 12 = 132): the old proposal had no `3×N` theorem, so its
return-to-UNKNOWN set was the whole non-unfit family. The quoted
"104 at ≤ 15" **could not be reproduced** under any enumeration convention
tested (canonical, 5 | volume, max-dim thresholds 12–18); the correct
current figures are 81 blanket / 72 non-unfit (66 + 6 under the new
narrowing) at dims ≤ 15. The historical 104 appears to be an arithmetic
or convention slip; the numbers above supersede it.

Changed boxes (`published_impossible → UNKNOWN`), dims ≤ 20, by family —
the ≤ 15 list is the sub-list with c ≤ 15:

* `1×4×{5,10,15,20}`, `2×4×{5,10,15,20}` (8)
* `1×5×{5..20}`, `2×5×{5..20}` (32)
* `1×6×{10,15,20}`, `2×6×{10,15,20}` (6)
* `1×7×{10,15,20}`, `2×7×{10,15,20}` (6)
* `1×8×{10,15,20}`, `2×8×{10,15,20}` (6)
* `1×9×{10,15,20}`, `2×9×{10,15,20}` (6)
* `1×10×{10..20}`, `2×10×{10..20}` (22)
* `1×11×{15,20}`, `2×11×{15,20}` (4)
* `1×12×{15,20}`, `2×12×{15,20}` (4)
* `1×13×{15,20}`, `2×13×{15,20}` (4)
* `1×14×{15,20}`, `2×14×{15,20}` (4)
* `1×15×{15..20}`, `2×15×{15..20}` (12)
* `1×16×20`, `1×17×20`, `1×18×20`, `1×19×20`, `1×20×20` and the `2×` mirror (10)

Total: 124 (66 at dims ≤ 15). Machine-readable list:
`/tmp/opencode/z_impact.json` (session artefact; reproduce with the
enumeration above).

No changed box is a RAW_PRIME, has a published solution, carries a
verified search certificate, or is covered by any other existing rule.
The change touches only boxes the blanket itself classified.

---

## 9. Recommended patch (proposal — NOT applied)

```python
# Z pentacube: spans {1,3,3}; every placement in a 1- or 2-thick box is
# layer-confined (mechanized, all 24 orientations), so 1xMxN / 2xMxN
# reduce exactly to free-Z-pentomino rectangle problems (see
# docs/frontier/rule_audit/z_final_disposition.md §2).
#
# Published record: Sillke qu5-z has no 2D section; Shirakawa's Z table
# starts at 3x[3-22]xN; Reid's box collection lists no 1x/2x Z box.
# No published Z-pentomino rectangle result exists (2026-09-02).
# Proved here: Z pentomino tiles no 3xN strip (hand theorem, §5.1), and
# no rectangle with min side <= 64 (machine-checked strip DP, §5.3).
if a <= 2:
    if sum(1 for d in (a, b, c) if d >= 3) < 2:
        return "published_impossible"   # piece-unfit: 1x1xN, 1x2xN, 2x2xN
    if b == 3:
        return "published_impossible"   # derived theorem: no 3xN Z strip (§5.1)
    return None                          # open: reduces to Z-pentomino rectangle
```

Policy notes for the human:

1. The `b == 3` rule rests on a **derived theorem of this audit** (hand
   proof in §5.1, machine cross-check), not on a published source. If the
   project requires a published ingredient for `published_impossible`
   (cf. the F-catalogue convention), drop the `b == 3` line; the rest of
   the patch is unaffected. Under that stricter policy the
   return-to-UNKNOWN counts become 72 (≤ 15) and 132 (≤ 20).
2. The §5.3 machine result (min side ≤ 64) is deliberately **not** encoded
   as a rule: it is this audit's own DP, not an independently verified
   certificate. A future promotion path exists (export per-width
   certificates and verify them like the 6×6×10 DRAT package), which
   would justify `1×w×N` / `2×w×N` rules for w ≤ 64.
3. `docs/pieces/Z.md` should be updated in the same commit to remove
   "`a <= 2`: impossible" from the published-families list and to record
   the reduction theorem and the strip theorem with their provenance.

---

## 10. What remains open

1. **The 2D core question**: does the free Z pentomino tile *any* finite
   rectangle? Open. No published result either way; no counterexample up
   to min side 64 (machine-checked) or area 200 (complete).
2. Extending the machine-verified strip width beyond 64 (the per-width
   check is cheap; the all-N logic is already in place), and converting
   it into independently verified certificates suitable for
   `SEARCHED_NO_SOLUTION`-grade promotion.
3. Whether an elementary impossibility theorem for *all* rectangles
   exists (the col-2 collision structure found by the strip DP — first
   columns can never be covered — may generalise to a full hand proof;
   the branching resisted a short induction in this audit).
4. The blanket's `a ≥ 3` neighbours are untouched here; W and N blanket
   dispositions remain as proposed on 2026-09-01 (W pending the Sillke
   `n*N` notation question; N not analysed in this task).

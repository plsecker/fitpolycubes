# Stage 5P — External Comparison against George Sicherman's Inverse/Diagonal (CK6) Pentacube Oddity Page

**Date:** 2026-09-08
**Status:** COMPLETE
**Source:** `https://sicherman.net/c5odd/c5nodd.html` — *Pentacube Oddities with Inverse/Diagonal
Symmetry*, **last revised 2026-09-05** (two days newer than the rev our 19-T fixture was built
from; re-read in full for this stage).
**Cached copy:** `data/ck6_reuse/sicherman_cache/c5odd/`
**Tool:** `tools/frontier/sicherman_c5nodd_compare.py`
**Raw evidence:** `data/ck6_reuse/stage5p_george_comparison.json`

---

## 1. What the page publishes

The page shows, **for each pentacube, one smallest-known oddity** with inverse/diagonal
(= CK6, or a supergroup) symmetry, as a 3-D drawing plus a strip of flat-coloured
cross-sections ("shown from top to bottom"). *"If you find a smaller solution, please write."*
Consequently **absence from the page is not evidence of absence** for any non-minimal figure —
only comparisons against the published minima are adjudicable from the page alone.

Transcribed rows (label + tile count, read at 7–8× zoom from the table images):

| table | rows (piece × tiles) |
|---|---|
| Achiral | X 1, P 5, Z 5, I 1, V 7, M 3, Q 7, L 11, U 7, Y 13, K 21, B 13, A 15, N 15, W 9, F 11, T 19 |
| Chiral, disallowing reflection | R 3, S 7, H 7, J 9, G 7, E 13 |
| Chiral, allowing reflection | R 3, S 7, H 7, J 9, E 11, G 7 |

Sister pages (also cached): square box (order 16, rev 2026-09-07), square (order 8, rev
2026-05-12), ternary/diagonal mirror (rev 2026-09-05). On all of them the I and X solutions are
stated to be trivial (the pieces themselves already have the symmetry).

## 2. Method

For every published figure that could match one of our Stage 5N catalogue entries at the same
(piece, tile count) — **R-3, P-5, Z-5** — we reconstructed the actual geometry from the
cross-section strips and compared it with our targets. Steps, all asserted in code:

1. **Strip parsing.** The table images have a white background, black 1 px cell borders and a
   flat palette (aqua/red/gold/green/purple/orange). Connected components of non-white pixels
   are the per-layer grids; the square lattice pitch is auto-detected and **validated against
   the black-border structure** (borders are drawn only where a filled cell faces an unfilled
   cell, a different colour, or the exterior) — this kills sub-cell pitch false positives.
2. **Offset recovery.** George's strip layout positions the grids decoratively, so when a
   layer's filled cells do not span the figure's full xy footprint, the per-layer offsets are
   lost by bbox-relative reading. They are recovered by constraint search (offsets in
   [−4,4]², anchored at the densest layer, consecutive-z footprints must intersect) subject
   to: figure face-connected, **CK6 ⊆ Sym** (re-derived from matrices), every 5-cell colour
   class congruent to our registry piece under proper rotations, and tileability by the piece.
3. **Handedness.** Any consistent reading convention differs from the true one by an O_h
   element; all page figures contain inversion (achiral), so every valid reading yields a
   congruent shape. The search returns all surviving readings; all readings found agree on one
   canonical form per figure.
4. **Comparison.** Full-O_h and proper-rotation canonical forms vs the Stage 5N catalogue ids;
   tiling orbits under Sym(target); George's published colouring mapped into our orbit set
   where his colours identify copies (he **reuses colours** on P-5/Z-5, so there the tiling
   extraction is skipped and only the shape is compared).

**Piece-lettering verification.** R, P, Z are confirmed *geometrically* (his figures tile by
our registry pieces and match our canonical forms). B and L were confirmed by high-zoom
thumbnail identification (B = 3-bar + side cube + top cube at the middle; L = 4-bar + end
cube) on top of the pre-existing odd-box reconciliation of the repo catalogue lettering
(`tools/verify_sicherman_odd_boxes.py`, B → (3,13,15), L → (3,5,5) PASS).

## 3. Geometry-level results

| George's figure | our shape | |Sym| | tilings (orbits) | verdict |
|---|---|---|---|---|
| R-3 (chd + cha, same figure) | **R-V15-S1** (`p24-4bb83e83ad90`) | 4 (exact CK6) | 2 (1 orbit), his colouring = our orbit 0 | **known shape + known tiling** |
| P-5 (ach) | **P-V25-S3** (`oh-69beb16fe99d`) | 12 (D3d) | 24 (2 orbits), 24 = our catalogue count | **known shape**; tiling count agrees exactly |
| Z-5 (ach) | **Z-V25-S1** (`oh-325afb95cf59`) | 8 | 4 (1 orbit), 4 = our catalogue count | **known shape + known tiling** |

Every reconstruction is independently validated: cell count = 5 × tiles, face-connectivity,
CK6 subgroup present, exact-cover tileable. Figures:

* George's **R-3** is the *same figure* as our R-V15-S1, and his published colouring is
  literally one of our two raw tilings (both tilings form a single orbit, so there is nothing
  beyond his figure at this (piece, count, class)).
* George's **P-5** is the 3×3×3 cube minus two body-diagonal corners (order 12) = our
  P-V25-S3, the highest-symmetry multi-tiling case of our catalogue (24 tilings, 2 orbits).
* George's **Z-5** is the 3×3×3 cube minus two opposite corners *of the middle layer*
  (order 8) = our Z-V25-S1.

## 4. Metadata-level results (all 52 catalogue shapes)

| category | count | shapes |
|---|---|---|
| known shape + known tiling | 4 | I-V5-S1, X-V5-S1 (trivial 1-tile = his trivial I/X entries), R-V15-S1, Z-V25-S1 |
| known shape | 1 | P-V25-S3 |
| related-but-distinct | 3 | P-V25-S1, P-V25-S2, Z-V25-S2 |
| **improvement over published minimum** | **16** | **B-V15-S1** and all 14 B-V25-*, L-V25-S1 |
| no match on page (minima-only caveat) | 28 | all non-trivial X and I figures |

### 4.1 Headline: B and L improvements

* **B-V15-S1: 3 B pentacubes, 15 cells, exact CK6, 2 tilings** — vs George's published B
  minimum of **13 tiles** (65 cells). Smaller by 10 tiles / 50 cells. All fourteen of our
  5-B constructions (including B-V25-S12 with its 10 tilings) are also below his minimum.
* **L-V25-S1: 5 L pentacubes, 25 cells** — vs George's published L minimum of **11 tiles**
  (55 cells). Smaller by 6 tiles / 30 cells.

These are exactly the "please write" cases the page solicits. They rest on: (a) Stage 5N/O
independent verification of our constructions (standalone auditor, dual checks), (b) the
lettering verification chain above, (c) the page's own semantics (one smallest-known figure
per piece). **Suggested action: write to George** with B-V15-S1, L-V25-S1 (and optionally
B-V25-S12) — witness coordinates and renders are in `data/ck6_reuse/`.

### 4.2 Consistency checks that passed

* His **T-19** minimum is fully consistent with our proven impossibility results for T at
  V = 15, 25, 35, 45 (an independent external corroboration of the Stage 2–4E negative
  results; our V=55 search continues separately).
* His R-3 appearing in *both* chiral tables (same figure) matches our R-V15-S1 being an
  achiral target tiled under proper rotations only.
* Our Stage 5L search independently rediscovered his P-5 and Z-5 minima (and their exact
  symmetry orders 12 and 8) — strong mutual validation of both catalogues.
* No shape in our catalogue contradicts anything on the page.

### 4.3 What the page cannot adjudicate

The 28 "no match" shapes are all non-trivial I/X constructions (3- and 5-copy oddities).
George's I and X entries are the trivial pieces themselves, and the page lists minima only,
so our non-trivial I/X figures are simply **not present on the page** — no novelty claim is
made from that. The same caveat covers our extra tilings of the known P-5/Z-5 shapes and the
extra non-congruent 5-P/5-Z shapes (P-V25-S1/S2, Z-V25-S2): same piece, same tile count,
same page class, but non-congruent to his published minima.

## 5. Tooling incident found and fixed during this stage

`common/oddity.py::placements_in_region` anchors orientations at **region cells**; for pieces
with orientations that do not contain their component-wise minimum corner (e.g. P), the
anchor can fall **outside** the region while every cell of the placement is inside — silently
dropping placements. This tool initially undercounted P-5 tilings (16 vs the true 24) because
of it; the tool now follows the repo's complete `all_covers` convention (enumerate over a
containing domain, then filter to the target).

**Impact assessment on prior results: none.** The large CK6 searches (Stages 2–4E, 5-series)
build their placement indices over the *full domain universe* (L1 ball), so every placement
anchor is in the enumeration region and the funnel is complete; the documented funnel counts
(V=25: 52,541/18,090/908; V=35: 9,003,562/6,229,218/56,889; V=45: 1,436,064/33,935/0) all
reproduce exactly. The trap only bites when anchoring directly at a small target's cells.
Recommend a docstring warning (or an assert) in `common/oddity.py` as a follow-up.

## 6. Reproduce

```bash
python3 tools/frontier/sicherman_c5nodd_compare.py      # ~1-2 min, low memory
```

Requires the cached images under `data/ck6_reuse/sicherman_cache/c5odd/` (fetched 2026-09-08;
if George updates the page, re-fetch `c5nodd.html`, `c5n-ach.png`, `c5n-chd.png`,
`c5n-cha.png` and re-check the strip band/x-range constants in `RECONSTRUCT`).

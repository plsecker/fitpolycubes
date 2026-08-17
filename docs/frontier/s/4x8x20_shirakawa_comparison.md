# 4x8x20 S Tiling vs. Shirakawa's Published Solution

Date: 2026-08-18
Status: **MATCH AFTER WHOLE-BOX SYMMETRY**

## Source

- URL: https://puzzlewillbeplayed.com/Shirakawa/html/5-15-20x8x4.html
  (page title: "Pentomino Box Packing : 128 5/15 (20×8×4)", discovered by
  Helmut Postl, 1998; listed in Shirakawa's collection as
  `128  4x8x20  1+  prime  1998 Postl`).
- The HTML page itself contains no tiling data; it embeds a single SVGZ
  object: `../svgz/5-15/5-15-4x8x20.svgz`
  (https://puzzlewillbeplayed.com/Shirakawa/svgz/5-15/5-15-4x8x20.svgz).

## How the published solution was extracted

1. Downloaded `5-15-4x8x20.svgz` (gzip; decompresses to
   `5-15-4x8x20.svg`, 63,572 bytes, "SVG creator for Polyomino Packing.
   2015 by ISHINO k16").
2. The SVG is a 2D projection of the box: 640 `<rect>` cells of 10×10 px,
   each carrying a fill color and an HTML comment `<!-- N -->` with the
   piece number N = 1..128. Cells sharing a piece number form one
   pentomino.
3. Layout of the drawing: 32 columns × 20 rows, with vertical gaps after
   columns 7, 16, 25 — i.e., 4 blocks of 8 columns × 20 rows. This is
   read as the 4×8×20 box with
   - block index (0..3) = x,
   - column within block (0..7) = y,
   - row (0..19) = z.
   (4 blocks × 8 columns × 20 rows = 640 cells = 4×8×20; this is the
   only assignment consistent with the block/column/row counts.)
4. Extraction validated:
   - 128 pieces, 5 cells each;
   - every piece is congruent to the S pentomino (all 128 pass the
     orientation check against the 24 orientations of S);
   - cells span exactly x ∈ [0,4), y ∈ [0,8), z ∈ [0,20);
   - 640 distinct cells — full coverage, no overlaps.
   Result saved to `/tmp/opencode/shirakawa/shirakawa_tiling.json`.

## Our 128 placements

From `docs/s_4x8x20_tiling_certificate.md` (reconstructed from the
verified 20-layer frontier cycle, `docs/s_4x8x20_frontier_cycle.md`):
128 placements in ordinary (x, y, z) coordinates, x ∈ [0,4), y ∈ [0,8),
z ∈ [0,20), each a valid S placement; 640 distinct cells; full coverage
(certificate PASS).

## Comparison

Both tilings were compared as multisets of 128 placements (each
placement = its set of 5 cells; pieces are unlabeled, so equality is
multiset equality of cell-sets). Allowed transformations: whole-box
symmetries only — since 4, 8, 20 are pairwise distinct, the only
legitimate box symmetries are the 8 axis reflections
(x → 3−x, y → 7−y, z → 19−z, any combination); no axis permutations and
no per-piece transformations.

Result of testing all 8 axis reflections:

| transform | matches our tiling? |
|---|---|
| identity | no |
| x → 3−x | **yes** |
| y → 7−y | **yes** |
| z → 19−z | **yes** |
| x → 3−x, y → 7−y | no |
| x → 3−x, z → 19−z | no |
| y → 7−y, z → 19−z | no |
| all three | **yes** |

The four matching transforms form the coset (1,0,0) + H where
H = {id, (x,y) flip, (x,z) flip, (y,z) flip}; both tilings are invariant
under H (verified directly for our tiling), which is why all four
transforms give the same match.

Placement-level verification under z → 19−z (and equivalently under each
of the other three): the 128 flipped Shirakawa placements are in exact
bijection with our 128 placements — multiset equality holds, with every
placement appearing exactly once on each side (no duplicate placements
in either tiling).

## Result

**MATCH AFTER WHOLE-BOX SYMMETRY**

The tiling published by Shirakawa (Postl 1998) is the SAME tiling as our
independently reconstructed unique 4x8x20 S tiling, up to a whole-box
reflection.

Required transformation (any one of the four equivalent ones):

- **z → 19−z** (flip along the 20-long axis) — the natural reading, since
  the SVG drawing lists rows top-to-bottom while our z increases upward;
- equivalently x → 3−x, y → 7−y, or all three flips together.

No translation is needed (a translation mapping the full box to itself
is the identity), and no axis permutation is legitimate because the box
dimensions 4, 8, 20 are pairwise distinct.

## Uncertainty and limitations

- The extraction depends on the drawing convention (block = x, column =
  y, row = z). This is forced by the counts (4 blocks × 8 columns × 20
  rows) and confirmed by the validation: all 128 pieces are S pentominoes
  and the 640 cells cover the box exactly once. Any other assignment of
  the three axes to block/column/row would fail the piece-shape check.
- The piece numbers in the SVG comments are arbitrary labels; the
  comparison is label-free (multiset of cell-sets), so labeling cannot
  affect the result.
- The "1+" in Shirakawa's listing was not interpreted as a solution
  count; the comparison is a direct placement-by-placement check.
- The match is not inferred from both being valid tilings: it is an
  exact 128-to-128 placement bijection after the reflection.

## Reproducibility

- Page: https://puzzlewillbeplayed.com/Shirakawa/html/5-15-20x8x4.html
- SVGZ: https://puzzlewillbeplayed.com/Shirakawa/svgz/5-15/5-15-4x8x20.svgz
- Extracted tiling: `/tmp/opencode/shirakawa/shirakawa_tiling.json`
- Comparison: ad-hoc script (parse SVG rects → 3D cells → validate S
  congruence → multiset comparison under the 8 axis reflections), run
  with `.venv/bin/python3`.
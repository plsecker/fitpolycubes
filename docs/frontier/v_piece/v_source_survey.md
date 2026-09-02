# V-Pentacube Source Survey

**Date**: 2026-08-26
**Status**: COMPLETE
**Purpose**: Establish ground truth for V-pentacube Macro methodology transfer.
**Method note**: every computational fact below was (re)computed for this survey
with the generic piece machinery (`tools/frontier/piece_utils.py`) from the
registry definition; nothing was carried over from S or T by assumption.

---

## 1. Piece Definition

**Canonical coordinates** (from `common/registry.py`, `PENTACUBES["V"]`):
```
V = [[0,0,0],[1,0,0],[2,0,0],[0,1,0],[0,2,0]]
```

The V-pentacube is a flat corner: two perpendicular arms of length 3 sharing
the corner cell — a planar L-shape occupying a 3×3 bounding box with the four
cells opposite the corner empty.

**Shirakawa piece number**: 6 (of 12 pentominoes)
**Kurnell number**: 13
**Shirakawa URL**: https://puzzlewillbeplayed.com/Shirakawa/V.html

---

## 2. Rotational Orientations

**Total unique orientations**: **12** (proper rotations, det=+1) — same count as S and T.

### Chirality

V is **achiral in 3D**: the mirror image lies *inside* the proper-rotation orbit
(verified computationally: orientations including reflections = 12 = proper-only
count; zero mirror images outside the orbit). This is the standard fact that
every planar pentacube is achiral (in-plane reflections lift to proper 3D
rotations), consistent with the W chirality correction in
`docs/frontier/macro_certificate_format.md` §8. No reflection convention is
needed anywhere in the V pipeline.

### Orientation classification by z-span

| z-span | Count | Layer occupancy patterns |
|--------|-------|--------------------------|
| 1 (flat) | 4 | [5,0,0] — all 5 cells in one layer |
| 3       | 8 | [3,1,1], [1,1,3] — exactly four each |

**No z-span=2 orientations exist.**

### Detailed orientation table (computed; see also data/frontier/v_piece/v_orientation_table.json)

| ID | z-span | Layer occ | Footprint | Cells (min-normalized) |
|----|--------|-----------|-----------|------------------------|
| O0 | 1 | [5,0,0] | 3×3 | [[0,2,0],[1,2,0],[2,0,0],[2,1,0],[2,2,0]] |
| O1 | 1 | [5,0,0] | 3×3 | [[0,0,0],[1,0,0],[2,0,0],[2,1,0],[2,2,0]] |
| O2 | 1 | [5,0,0] | 3×3 | [[0,0,0],[0,1,0],[0,2,0],[1,2,0],[2,2,0]] |
| O3 | 1 | [5,0,0] | 3×3 | [[0,0,0],[0,1,0],[0,2,0],[1,0,0],[2,0,0]] |
| O4 | 3 | [1,1,3] | 3×1 | [[0,0,2],[1,0,2],[2,0,0],[2,0,1],[2,0,2]] |
| O5 | 3 | [3,1,1] | 3×1 | [[0,0,0],[1,0,0],[2,0,0],[2,0,1],[2,0,2]] |
| O6 | 3 | [3,1,1] | 3×1 | [[0,0,0],[0,0,1],[0,0,2],[1,0,0],[2,0,0]] |
| O7 | 3 | [1,1,3] | 3×1 | [[0,0,0],[0,0,1],[0,0,2],[1,0,2],[2,0,2]] |
| O8 | 3 | [3,1,1] | 1×3 | [[0,0,0],[0,1,0],[0,2,0],[0,2,1],[0,2,2]] |
| O9 | 3 | [1,1,3] | 1×3 | [[0,0,0],[0,0,1],[0,0,2],[0,1,2],[0,2,2]] |
| O10 | 3 | [1,1,3] | 1×3 | [[0,0,2],[0,1,2],[0,2,0],[0,2,1],[0,2,2]] |
| O11 | 3 | [3,1,1] | 1×3 | [[0,0,0],[0,0,1],[0,0,2],[0,1,0],[0,2,0]] |

### Key structural facts (computed, not assumed)

1. **Flat orientations exist**: 4 of 12 have z-span=1 and fill a 3×3 corner
   region (5 of 9 cells of the bounding box). As with T, a single flat piece
   can complete layer-0 work without touching L1/L2 — this drives the
   generalized terminal-predecessor structure.

2. **No middle-heavy standing orientation**: all 8 standing orientations have
   profiles [3,1,1] or [1,1,3]; **[1,3,1] is impossible for V**. Geometric
   reason: when one arm stands vertically, the other arm lies entirely in the
   corner's layer, so the 3-cell layer always contains the corner and sits at
   an *end* of the z-range. This differs from T, whose standing orientations
   include [1,3,1] (stem centred). Consequence: a standing V never places
   cells in both L1 and L2 without also placing 3 cells in L0 *or* having its
   corner at the top — the slot-0 footprint of any standing template is
   either 3 cells or 1 cell.

3. **Standing footprint is a full 3-strip**: every standing orientation has
   x_span×y_span = 3×1 or 1×3. Standing Vs occupy entire length-3 rows or
   columns of the cross-section, anchored at a row/column end.

4. **Maximum template span**: 3 layers (z), 3 columns (x), 3 rows (y).

---

## 3. Legal Templates for Candidate Cross-Sections (computed, max_z=20 window)

| Cross-section | NCELLS | Concrete placements | Deduplicated templates |
|---------------|--------|---------------------|------------------------|
| 3×5           | 15     | 1,248               | **172**                |
| 4×5           | 20     | 2,064               | 296                    |
| 5×5           | 25     | 2,880               | **420**                |
| 3×10          | 30     | 3,088               | 432                    |
| 5×6           | 30     | 3,696               | 544                    |

These are an order of magnitude smaller than the S/T cross-sections that were
found tractable (e.g. T 3×7 completed in 0.4 s). The state width for 3×5 is
only 45 bits.

---

## 4. Published Catalogue (Shirakawa/Sillke)

Source pages:
- https://puzzlewillbeplayed.com/Shirakawa/V.html ("3D Complete. 4D Complete
  except for 4x5x5x5 and 5x5x5x5.")
- Sillke V-pentomino page (http://www.mathematik.uni-bielefeld.de/~sillke/PENTA/qu5-v)

### Prime boxes (`catalogues/v_catalogue.py`) — 27 canonical primes

| Family | Primes | Notes |
|--------|--------|-------|
| 3×5×N  | **6, 8** | **3×5×6 is the minimal prime** (Sillke 1993; published "3 solutions") |
| 3×7×N  | 20, 25, 30, 35 | |
| 3×9×N  | 10, 15 | |
| 3×10×N | 10, 11, 13 | |
| 3×11×N | 15 | |
| 3×13×N | 15 | |
| 4×5×N  | 6, 7, 8, 9, 10, 11 | six consecutive primes |
| 5×5×N  | 6, 9, 10, 11, 13, 14 | 5×5×9 = minimal odd box (verified exhaustively in-repo); 5×5×12 removed (see corrections) |
| 5×7×N  | 7, 9 | |

- Minimal prime overall: **3×5×6**
- Minimal odd prime (all dims odd): **5×5×9** (`MINIMAL_ODD` in catalogue;
  verified 2026-08-18: 1,120 raw Algorithm X solutions, 70 orbits under |G|=16)
- Minimal even prime (all dims even): none known (`MINIMAL_EVEN = None`)
  — consistent with the parity phenomena expected below.

### Impossible / corrected entries

Published impossible families:
- a ≤ 1; cubes (a=b=c); 2×N×N (reduces to impossible N×N front)
- 3×3×N: "dies out after 7 steps"
- 3×4×N: "dies out after 15 steps"
- 3×5×N with N odd

Published individual impossibles: 3×5×4, 3×5×10, 4×4×5, 4×5×5, 5×5×5,
5×5×7, 5×5×8, 3×7×10, 3×7×15.

Corrections recorded in `shirakawa/V.md`:
- Sillke claimed 5×5×12 prime — **not prime** (decomposes).
- Sillke claimed 3×3×3×15 impossible — **possible** (4D).

The 3×5 family gives unusually sharp Macro predictions (tested in Phases 6–8):
tileable z ∈ {6, 8} ∪ {even z ≥ 12}; 4 and 10 impossible; odd impossible.

---

## 5. Existing Repository Data (V)

### Placement files (repo root)

| File | Lines | Content |
|------|-------|---------|
| `placements_V_5x5x6.txt` | 697 | header "696", then 696 placements × 5 cell indices (index = x + 5·y + 25·z) |
| `placements_V_5x5x9.txt` | 1,165 | header "1164", then 1164 placements |

**Provenance (resolved during Phase 7)**: these are **complete placement
catalogues** — every legal V placement in the respective box (verified:
generate_placements gives exactly 696 / 1164) — *not* witness tilings. They
are search inputs, not evidence. True witnesses are the exhaustive solution
sets (`data/v_5x5x6_complete_solutions.json`, `data/v_5x5x9_*`).

### Certificates

- `data/v_5x5x6_certificate.json`: exhaustive-enumeration certificate
  (raw tiling evidence; **not** a Macro certificate).
- `data/frontier/certificates/v_5x5x6_solution01_macro_walk.json`:
  generic format-v1 Macro closed-walk certificate packed from solution #1 of
  the 5×5×6 enumeration; passes the isolated generic checker (Layer A C1–C7g).
  Already demonstrates non-T geometry handling of the certificate framework.

### Prior V Macro-related work (must be preserved, some conclusions superseded)

| Document | Status |
|----------|--------|
| `docs/frontier/v_5x5x6_macro_calibration.md` | Calibration: 80 macro return paths → 80 raw tilings → 9 symmetry orbits; matches published "9". Postscript: Algorithm X finds **144** raw solutions; interpretation given there ("first-empty-cell restriction misses some tilings") needs re-examination in Phase 4 — a macro walk under-determines its realizing fills, so walks→tilings is one-to-many and one-realization-per-path enumeration *undercounts* raw tilings without violating walk faithfulness |
| `docs/frontier/v_5x5_forward_exploration_results.md` | Forward exploration on 5×5 hit a compute wall (~9.1M states at depth 6); state 0 found at depth 6 (= 5×5×6 prime ✓); depth-9 unreachable by that method. Note: the "wall" there is an implementation/strategy wall (layer-by-layer forward sets), not a mathematical boundary |
| `docs/frontier/v_5x5_macro_analysis.md` | Earlier structural analysis |
| `docs/frontier/v_5x5x6_complete_verification.md`, `v_5x5x9_complete_symmetry_analysis.md`, symmetry audits | Exhaustive Algorithm X verification of the two smallest published primes |

### Existing V solver/catalogue code

- `catalogues/v_catalogue.py` — 27 canonical primes, impossibility rules.
- `solvers/v_5x5_*.py` — ~20 files: forward/bidirectional explorers,
  path counting, reconstruction, symmetry reduction, predecessor debugging,
  5×5×6/5×5×9 verification harnesses. These predate the generic
  `tools/frontier/macro_explorer.py` and hard-code the V geometry.

---

## 6. Available SVG Witnesses (External)

As with T, no inline SVG solutions are recorded for V in the repository's
Shirakawa transcription. Unlike T, however, the repo holds *native placement
data* (`placements_V_5x5x6.txt`, `placements_V_5x5x9.txt`) plus a fully
verified solution set for 5×5×6 (144 raw solutions in
`data/v_5x5x6_complete_solutions.json`). Physical-witness extraction can
therefore proceed from in-repo data rather than external SVG parsing.

---

## 7. Key Implications for Macro Transfer

1. **State depth**: max z-span = 3 ⇒ the existing 3-layer frontier window
   suffices. No generalization to >3 layers is needed (but this had to be
   checked, not assumed: V's standing geometry differs qualitatively from T's).

2. **Flat-orientation gate structure applies**: like T, V has flat orientations,
   so the generalized terminal-predecessor criterion (pred(0) states may have
   partially filled L0 with L1=L2=∅) is expected to apply rather than S's
   single-gate form. Whether pred(0) is a single class or multiple classes is
   a Phase 6/9 measurement.

3. **The [1,3,1]-free profile structure is genuinely new**: unlike T, no V
   placement ever has its 3-cell layer in the middle. This constrains which
   intermediate fill states are reachable and may make V's macro graphs
   structurally different (e.g. narrower transients, different out-degree
   distribution).

4. **Small cross-sections are exceptionally tractable**: 3×5 has only 172
   templates and a 45-bit state; a complete closure should be cheap. The
   natural first cross-section is 3×5 (published primes 3×5×6, 3×5×8;
   published impossibles 3×5×odd, ×4, ×10 give falsifiable predictions).

5. **Witness data exists natively**: third-geometry witness extraction can be
   validated against the in-repo verified 5×5×6 solutions without SVG parsing.

---

## 8. Provenance

| Source | Date | Contents |
|--------|------|----------|
| `common/registry.py` | Repository | V piece coordinates |
| `tools/frontier/piece_utils.py` + probe run 2026-08-26 | This survey | Orientation count, spans, profiles, achirality, template counts |
| `catalogues/v_catalogue.py` | Repository | 27 canonical primes, impossibility families |
| `shirakawa/V.md` | Feb 18, 2015 (fetched earlier) | Page summary, corrections |
| `docs/pieces/V.md` | 2026-08-25 | Catalogue audit incl. 5×5×6/5×5×9 verification history |
| `docs/frontier/v_5x5x6_macro_calibration.md` | 2026-08-21/25 | Prior macro calibration + Algorithm X correction |
| `docs/frontier/v_5x5_forward_exploration_results.md` | 2026-08-21 | Forward-exploration wall documentation |
| `placements_V_5x5x6.txt`, `placements_V_5x5x9.txt` | Repo root | Native placement witnesses |

# Q Piece Geometry Integrity Audit

**Date**: 2026-09-01
**Status**: DIAGNOSIS ONLY — registry not modified.
**Trigger**: theorem-hunt finding that registry-Q is disconnected and cannot
fit its own catalogue's published `2×2×5` prime.

---

## 1. Diagnosis (precise)

**The registry coordinates for piece `Q` are wrong.** They describe a
*disconnected* pseudo-piece (a 2×2 square plus a corner-touching cell) that
is not a pentacube at all. The catalogue (`catalogues/q_catalogue.py`) and
its documented published sources are **correct** and describe a different,
well-defined piece — Sillke's qu5.61 — whose true geometry is the
**2×2×2 block minus an L-triomino** (a 2×2 square with one cube stacked on
a corner). The registry definition must be corrected before any solver,
placement-generation, or theorem work touches Q.

There is no naming ambiguity: every available source identifies the same
piece via the same published data.

## 2. What the registry says today

`common/registry.py`:

```python
"Q": PieceInfo(
    letter="Q",
    coords=np.array([[0,0,0],[1,0,0],[0,1,0],[1,1,0],[2,2,0]]),
    catalogue_module="catalogues.q_catalogue",
    kurnell=61, shirakawa_url=".../Shirakawa/5-22.html", shirakawa_piece=22
),
```

Mechanical facts about these coordinates (verified by script):

| property | value |
|---|---|
| face-connectivity | **DISCONNECTED** — component {(0,0,0),(1,0,0),(0,1,0),(1,1,0)} plus isolated corner-touching cell (2,2,0) |
| bounding-box spans | (3, 3, 1) |
| distinct orientations | 12 |
| fits 2×2×5? | **NO** (two spans of 3 exceed both size-2 dimensions) |

A disconnected 5-cell "piece" is not a pentacube; pentacubes are
face-connected by definition. Independently, span (3,3,1) makes `2×2×5`
unreachable, while the catalogue — and both live published sources —
declare `2×2×5` the **prime minimal** box for this piece with published
solutions. Contradiction.

## 3. The authoritative sources (fetched live, 2026-09-01)

### 3.1 Sillke qu5.61 (`~sillke/PENTA/qu5.61`, "complete: 20.01.93")

The page opens with the piece's own height-map picture:

```
  1 2
  1 1
```

Interpreted as a 2×2 footprint with column heights, this is a 2×2 square
with a single second-layer cube on one corner — i.e. the 2×2×2 block minus
an L-triomino. (The *other* {2,2,2} pentacube would show two height-2
columns; see §4.)

Published content of qu5.61:

* **Complete list of prime boxes (# = 5):** `2x2x5, 2x3x5, 5x5x9, 5x7x7,
  3x7x25`.
* **Complete list of prime hyperboxes (# = 1):** `3x3x3x5`.
* **Impossible (with published proofs):**
  * (A) no `3×3×Z` strip (two sides open) — colored-cube counting:
    a 3×3×9 subblock needs ≥ 20 pieces (volume ≥ 100) inside a 3×3×11
    neighborhood (volume 99);
  * (B) `3×5×u` impossible for odd u — the Dist-2 face coloration forces a
    split into `2×3×5` blocks;
  * (C) `5×5×5`, `5×5×7`, `3×7×15` impossible — colored-cube counts
    (27/36/64) exceed piece counts (25/35/63).
* Credits: Göbel (CFF 33, 1994; coloration + 5×5×9), Postl (letter 1997;
  all prime boxes by hand).

### 3.2 Shirakawa 5-22 (live page, "Complete.", 2015)

Lists exactly: `2×2×5` (prime minimal, Sillke 1993), `2×3×5` (prime),
`3×7×25` (1+ prime), **`3×9×15` (1+ prime)**, `5×5×9` (1+ prime),
`5×7×7` (1+ prime), and 4D `3×3×3×5` (1+ prime) — all credited Sillke
1993. See §7 for the 3×9×15 discrepancy note.

### 3.3 Project record

`docs/pieces/Q.md` records the same six primes and the A/B/C rules and
states the catalogue was rebuilt "to the published Sillke rules" in the
2026-08-06 audit. `tools/verify_sicherman_odd_boxes.py` uses Q's odd box
(5,5,9) — a published-fact check, unaffected by the registry bug.

## 4. Identification of the true shape (exhaustive + computational)

There are exactly **48 connected 5-cell subsets of the 2×2×2 cube**, which
collapse under the 24 rotations into exactly **2 free pentacubes** with
span multiset {2,2,2} (verified by exhaustive enumeration):

* **Candidate 1 — "square + corner cell"** (= 2×2×2 minus an L-triomino):
  a 2×2 square in one layer plus one cube attached beneath/above a corner.
  Layers 4+1. This is Sillke's picture "1 2 / 1 1" (one height-2 column).
* **Candidate 2 — "staircase"** (this is registry piece **A**): an
  L-triomino in one layer plus a second-layer domino, with exactly one of
  the two domino cubes supported below. Layers 3+2, path graph P5.

Discriminating experiment (exact 3D enumeration over all 24 orientations,
`/tmp/opencode/q_identify.py`):

| shape | 2×2×5 raw tilings | 2×3×5 raw tilings |
|---|---|---|
| Candidate 2 (registry-A shape) | **0** | 0 |
| Candidate 1 (square + corner) | **16** | **64** |

The published prime `2×2×5` therefore **disqualifies Candidate 2 and
identifies Candidate 1 as qu5.61**. The raw counts are consistent with the
published solution counts (2 for 2×2×5, 10 for 2×3×5) once the box
symmetry groups (orders 16 and 8) and solution stabilizers are quotiented
(Burnside); the exact count convention is the sources' own.

Consistency check that the two pieces are genuinely distinct: Candidate 1
tiles 2×2×5; the A-shape does not; and `a_catalogue` (piece A,
Sillke qu5.37, Shirakawa 5-24) publishes entirely different primes
(4×9×15 minimal etc., live 5-24 page agrees). No collision.

## 5. Corrected coordinates (PROPOSED — NOT APPLIED)

```python
"Q": PieceInfo(
    letter="Q",
    coords=np.array([[0,0,0],[1,0,0],[0,1,0],[1,1,0],[0,0,1]]),
    ...
)
```

Properties of the corrected shape (verified):

| property | value |
|---|---|
| face-connected | yes |
| spans | (2, 2, 2) |
| chiral | no (achiral; 24 distinct orientations) |
| fits 2×2×5 | yes |
| tiles 2×2×5 | yes (prime minimal — smallest tileable box, volume 20) |

## 6. Verification of the corrected shape against ALL published qu5.61 data

Exact checks (DFS / CaDiCaL SAT over all 24 orientations):

| box | published claim | computed | verdict |
|---|---|---|---|
| 2×2×5 | prime minimal (tileable) | 16 raw tilings | ✓ |
| 2×3×5 | prime (tileable) | 64 raw tilings | ✓ |
| 3×3×5 | impossible (A-family) | 0 | ✓ |
| 3×3×6 | impossible (A-family) | 0 | ✓ |
| 3×3×9 | impossible (A-proof core) | 0 | ✓ |
| 3×5×5 (u odd) | impossible (B) | 0 | ✓ |
| 3×5×6 (u even) | tileable | 262144 raw tilings | ✓ |
| 5×5×5 | impossible (C) | 0 (SAT) | ✓ |
| 5×5×7 | impossible (C) | background DFS check running | (published ✓) |
| 3×7×15 | impossible (C) | background DFS check running | (published ✓) |
| 5×5×9 | prime (tileable) | not recomputed (45 pieces; published 1+) | published ✓ |

The identification is overdetermined: fitting `2×2×5` alone already
excludes every pentacube except the two {2,2,2} shapes, and the tiling
test separates them.

## 7. Which catalogue entries/results become suspect

**Catalogue data: nothing needs to change.** `q_catalogue`'s primes,
impossibility rules, MINIMAL_ODD, and empty searched/solution sets are
published facts about qu5.61 and are confirmed against the live sources.
After the registry fix they describe the piece the solvers will actually
use.

**Suspect if the registry is corrected: any solver-derived artifact that
used the broken coordinates.** A repository sweep found:

* no `data/solutions_q_*` or Q placement files;
* no invocation of Q in `tools/` or `verify_solvers.py`;
* no Q entries in `SEARCHED_NO_SOLUTION` or `PUBLISHED_SOLUTIONS`.

So the contamination set is **empty today**; the risk is entirely
forward-looking. Any future Q solver run with the current registry would
generate placements of a disconnected pseudo-piece and produce meaningless
results.

**Discrepancy note (no action required):** the live Shirakawa 5-22 page
lists `3×9×15` as a prime (1+, Sillke 1993), while qu5.61's "complete"
list (20.01.93) contains only five primes. Most likely Sillke's page was
not updated after finding 3×9×15 later in 1993. The catalogue follows
Shirakawa. Flagged for completeness; not a registry issue.

**Minor naming note:** the registry field `kurnell=61` actually stores
Sillke's qu5 numbering (61 = fixed-pentacube 61 in Sillke's LEX scheme),
not Kürnell's book numbering. Cosmetic.

## 8. Consequences for theorem hunting

The corrected Q has spans {2,2,2}: it has no span-1 axis, so in any
2×M×N box **every** placement occupies both layers (mechanized check),
and it cannot enter 1×M×N boxes at all. The F-style layer-reduction
theorem pattern therefore **cannot** apply to Q; its 2-thick boxes are a
genuinely 3-dimensional problem. (With the broken {3,3,1} coordinates the
opposite conclusion would have been drawn — a second reason the fix
matters.)

## 9. Recommended change (for a future task)

1. Replace Q's `coords` in `common/registry.py` with §5 (one line).
2. Re-run `tools/check_piece_registry.py` and the catalogue validators.
3. Re-run `tools/verify_sicherman_odd_boxes.py` (Q row uses published
   facts; should be unaffected).
4. Then (and only then) start solver work on Q, beginning with the
   published primes 2×2×5 / 2×3×5 as positive controls.
---

## ADDENDUM (2026-09-01): FIX APPLIED

§9 was executed the same day: `common/registry.py` Q coordinates replaced by
the §5 value (with an in-code provenance comment). Post-fix validation:
5 cubes, face-connected, spans (2,2,2), 24 orientations, distinct from A;
project solver on the corrected geometry: **2×2×5 = 16 raw tilings = 2
box-symmetry orbits = published count 2**, **2×3×5 = 64 raw = 10 orbits =
published 10** (the live 5-22 page's leading figures "4" and "6" are piece
counts, volume/5); negative controls 3×3×5, 3×3×9, 3×5×5, 3×5×7 → 0
solutions each (5×5×5 → 0 via SAT). Full-repository suite green; see
`docs/frontier/post_promotion_integrity_report.md`.

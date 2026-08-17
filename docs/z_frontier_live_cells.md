# Z-Frontier: Live Cells in Frontier Layers 0-3

Solver: `solvers/s_z_frontier_packed.py` (S pentacube, 4x8 box).
Piece definition: `common/registry.py`, S = (0,0,0), (1,0,0), (2,0,0),
(0,0,1), (2,1,0) (bounding box 3x2x2).

## Method

The template set is exactly the solver's `build_templates()` output:
every accepted template is anchored with its target cell at layer 0
(rel = 0) and all cells at rel in [0, 4). The next placement must
cover the first empty cell of layer 0, so the applicable templates are
`templates[first_empty(layer0)]`. The solver's discovery loop was not
run; only the template geometry was analyzed.

## 1. Maximum z-offset reachable, per frontier layer

| Layer | Max z-offset (rel) | Templates with a cell at this rel |
|---|---|---|
| 0 | 0 | 488 of 488 (the anchor cell) |
| 1 | 1 | 488 of 488 |
| 2 | 2 | 168 of 488 |
| 3 | 3 | 0 of 488 |

- The S pentacube's largest axis extent is 3, so a placement spans at
  most 3 z-levels; anchored at its bottom cell, the top cell is at
  rel = 2. No template ever contains a cell at rel = 3.
- Every template has at least one cell at rel = 1 (the anchor is never
  the top cell of an accepted placement).
- Every anchor position (all 32 cells of the 4x8 grid) has at least
  one template reaching rel = 2, so the max z-offset is 2 regardless
  of which cell is the first empty cell of layer 0.

## 2. Can every bit in layers 1-3 participate in a future placement?

Over all possible anchors (all possible first-empty cells):

| Layer | Positions touchable |
|---|---|
| 1 | 32 of 32 |
| 2 | 32 of 32 |
| 3 | 0 of 32 |

- Every (x, y) position in layers 1 and 2 is included in some template
  for some anchor: no position in layers 1-2 is excluded by geometry.
- No position in layer 3 is ever included in any template.
- For a fixed anchor (a given state), coverage is partial: the next
  placement can touch 6-14 of 32 positions in layer 1 and 3-9 of 32
  positions in layer 2, depending on the anchor. Cells not touchable
  by the next placement may still be touchable by later placements
  once the first-empty cell moves.

## 3. Provably dead bits

- **All 32 bits of layer 3 are provably dead.** No template contains a
  cell at rel = 3, so no placement can ever write a layer-3 bit and no
  placement can ever be blocked by one (the overlap check
  `state & template` never sees layer-3 bits). Shifts only move cells
  downward (rel decreases), so cells never enter layer 3 from below.
  The layer-3 word of the state is therefore always zero, and removing
  it from the state would not change any future completion.
- **No position in layers 1-2 is provably dead**: every (x, y) is
  included in some template at rel 1 and at rel 2 for some anchor, so
  each can participate in a future placement.

## Conclusion

- Max z-offset a future S placement can reach: 2 (layer 2). Layer 3 is
  unreachable.
- Layers 1-2: every bit position can participate (over all anchors);
  layer 3: no bit can ever participate.
- Provably dead: the entire layer-3 word (32 bits). No dead positions
  in layers 1-2.

This report is factual; no new state representation is proposed or
implemented.
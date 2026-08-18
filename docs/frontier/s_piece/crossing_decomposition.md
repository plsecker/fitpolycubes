# S-Frontier: Decomposition of the 100 Layer-1/2 Occupancies into Crossing Placements

Solver: `solvers/s_z_frontier_packed.py` (S pentacube, 4x8 box).
Sources: the 100 layer-shift records in
`docs/z_frontier_state_stats_1m.md` (lines 140-239), the template set
produced by the solver's own `build_templates()`, and the crossing-cell
analysis in `docs/s_frontier_crossing_piece_states.md`. No discovery
run was performed; only the template generation and the recorded
diagnostics were used.

## 1. Model

- **Templates (allowed pieces)**: the solver's `build_templates()`
  output. It contains 488 entries (one per anchor cell, deduplicated
  per anchor); the same packed template is generated for several
  anchor cells, so the distinct placements are **212**. A
  decomposition is a set of distinct placements, so the 212 distinct
  templates are the allowed pieces.
- **Occupancy**: for each layer-shift state, the occupied cells of
  layers 1-2 (8 cells in records 1-12; 13 cells in records 13-100),
  represented as (layer, cell) pairs because the same (x,y) position
  can be occupied at both z-levels.
- **Decomposition**: a set of templates whose layer-1/2 cells
  partition the occupancy (each occupancy cell covered exactly once).
- **Compatible**: additionally, the templates' layer-0 anchor cells
  (their rel-0 cells) are pairwise disjoint — each layer-0 cell can
  host at most one placement. This is the physical constraint of the
  solver: cells are occupied by at most one placement.
- Counting method: exact-cover backtracking (always choosing the
  remaining cell with the fewest usable templates), cross-checked by
  independent brute-force subset enumeration on sample records
  (records 1, 2, 13, 100 agree exactly).

## 2. Result

| Model | Unique (exactly 1) | Multiple (>1) | Zero |
|---|---|---|---|
| Compatible (anchor cells pairwise disjoint) | **100** | **0** | 0 |
| Weaker (only the layer-1/2 cells partitioned; anchors ignored) | 0 | 100 | 0 |

- **Every one of the 100 layer-shift states has exactly one compatible
  decomposition into crossing S placements.** No state has multiple
  compatible decompositions.
- In every state, the unique decomposition's anchor cells partition
  all 32 layer-0 cells (verified 100/100): the anchors are pairwise
  disjoint and their union is the full layer-0 grid.
- The unique decomposition uses 8 placements in records 1-12 and 9
  placements in records 13-100.
- If the anchor constraint is dropped (a weaker, non-compatible
  notion: only the layer-1/2 cells must be partitioned), every state
  has multiple decompositions, between 8 and 1,296 per state. Those
  decompositions share anchor cells, so they are not compatible with
  the state.

## 3. Examples: unique compatible decompositions

### Record 1 (layer 2 empty; 8 layer-1 cells; 8 placements)

Layer 1 cells: (0,0), (3,0), (0,3), (3,3), (1,4), (2,5), (1,6), (2,7).

| # | Anchor cells (layer 0) | Cells above the cut |
|---|---|---|
| 1 | (0,0), (1,0), (2,0), (2,1) | (1, (0,0)) |
| 2 | (2,2), (3,0), (3,1), (3,2) | (1, (3,0)) |
| 3 | (0,1), (0,2), (0,3), (1,1) | (1, (0,3)) |
| 4 | (1,2), (1,3), (2,3), (3,3) | (1, (3,3)) |
| 5 | (1,4), (2,4), (3,4), (3,5) | (1, (1,4)) |
| 6 | (0,6), (0,7), (1,7), (2,7) | (1, (2,7)) |
| 7 | (1,6), (2,6), (3,6), (3,7) | (1, (1,6)) |
| 8 | (0,4), (0,5), (1,5), (2,5) | (1, (2,5)) |

Each placement is the flat S orientation (4 anchor cells + 1 cell in
layer 1). The 8 x 4 = 32 anchor cells partition layer 0.

### Record 13 (first state with layer 2 occupied; 13 cells; 9 placements)

Layer 1 cells: (0,0), (3,0), (0,1), (1,3), (0,4), (3,4), (2,5), (0,7),
(3,7). Layer 2 cells: (0,0), (0,1), (1,3), (2,3).

| # | Anchor cells (layer 0) | Cells above the cut |
|---|---|---|
| 1 | (0,5), (0,6), (0,7), (1,5) | (1, (0,7)) |
| 2 | (1,3), (1,4) | (1, (1,3)), (2, (1,3)), (2, (2,3)) |
| 3 | (0,1), (1,1) | (1, (0,1)), (2, (0,0)), (2, (0,1)) |
| 4 | (1,6), (1,7), (2,7), (3,7) | (1, (3,7)) |
| 5 | (0,2), (0,3), (0,4), (1,2) | (1, (0,4)) |
| 6 | (0,0), (1,0), (2,0), (2,1) | (1, (0,0)) |
| 7 | (2,6), (3,4), (3,5), (3,6) | (1, (3,4)) |
| 8 | (2,2), (3,0), (3,1), (3,2) | (1, (3,0)) |
| 9 | (2,3), (2,4), (2,5), (3,3) | (1, (2,5)) |

Placements 2 and 3 are vertical S orientations (2 anchor cells, one
cell at rel 1 and two at rel 2); the other seven are flat (4 anchors +
1 cell). Anchors: 7 x 4 + 2 x 2 = 32 cells, partitioning layer 0.

### Record 100 (13 cells; 9 placements)

Layer 1 cells: (0,0), (3,0), (1,2), (0,3), (1,4), (3,4), (2,5), (0,7),
(3,7). Layer 2 cells: (1,2), (2,2), (1,4), (1,5).

| # | Anchor cells (layer 0) | Cells above the cut |
|---|---|---|
| 1 | (0,5), (0,6), (0,7), (1,5) | (1, (0,7)) |
| 2 | (1,6), (1,7), (2,7), (3,7) | (1, (3,7)) |
| 3 | (0,4), (1,4) | (1, (1,4)), (2, (1,4)), (2, (1,5)) |
| 4 | (1,2), (1,3) | (1, (1,2)), (2, (1,2)), (2, (2,2)) |
| 5 | (0,1), (0,2), (0,3), (1,1) | (1, (0,3)) |
| 6 | (0,0), (1,0), (2,0), (2,1) | (1, (0,0)) |
| 7 | (2,6), (3,4), (3,5), (3,6) | (1, (3,4)) |
| 8 | (2,2), (3,0), (3,1), (3,2) | (1, (3,0)) |
| 9 | (2,3), (2,4), (2,5), (3,3) | (1, (2,5)) |

Again 7 flat + 2 vertical placements; anchors partition layer 0.

## 4. Examples: multiple decompositions under the weaker model

Under the weaker model (anchors ignored), every state has several
decompositions. The first three found for records 1, 2 and 13 are
described below. All variants cover exactly the same layer-1/2 cells;
they differ only in which layer-0 anchor cells are assigned to each
placement. Every non-compatible variant has at least one pair of
placements sharing an anchor cell, so none of them is compatible with
the state.

### Record 1 (8 layer-1 cells; 144 weaker decompositions)

The compatible decomposition (Section 3) is one of the 144. The first
three variants found are:

- **v1**: anchor sets `(2,2),(3,0),(3,1),(3,2)`; `(0,0),(1,0),(2,0),(2,1)`;
  `(0,1),(0,2),(0,3),(1,1)`; `(1,2),(1,3),(2,3),(3,3)`;
  `(1,4),(1,5),(1,6),(2,4)`; `(2,5),(2,6),(2,7),(3,5)`;
  `(1,2),(1,3),(1,4),(2,2)`; `(2,3),(2,4),(2,5),(3,3)` — the last four
  placements overlap each other (e.g. (1,4) in placements 5 and 7,
  (2,5) in placements 6 and 8).
- **v2**: same as v1 except the last placement's anchors are
  `(0,4),(0,5),(1,5),(2,5)` (the compatible choice).
- **v3**: same as v1 except the last placement's anchors are
  `(1,7),(2,5),(2,6),(2,7)` — overlapping the compatible placement 7
  `(0,4),(0,5),(1,5),(2,5)` at (2,5) and placement 8
  `(0,6),(0,7),(1,7),(2,7)` at (2,7).

The layer-1 cell (2,5) is covered by a flat placement in every
variant; only the anchor choice differs.

### Record 2 (8 layer-1 cells; 16 weaker decompositions)

The compatible decomposition (Section 3) is variant 13 of the 16. The
first three variants found are:

- **v1**: anchor sets `(1,6),(1,7),(2,7),(3,7)`; `(2,2),(3,0),(3,1),(3,2)`;
  `(0,5),(0,6),(0,7),(1,5)`; `(0,0),(1,0),(2,0),(2,1)`;
  `(0,2),(0,3),(0,4),(1,2)`; `(1,3),(1,4),(2,4),(3,4)`;
  `(0,1),(0,2),(0,3),(1,1)`; `(1,2),(1,3),(2,3),(3,3)` — placements 5
  and 7 share (0,2),(0,3); placements 6 and 8 share (1,3).
- **v2**: same as v1 except the last placement's anchors are
  `(2,5),(3,3),(3,4),(3,5)` — overlapping placement 8
  `(1,2),(1,3),(2,3),(3,3)` at (3,3) and placement 6
  `(1,3),(1,4),(2,4),(3,4)` at (3,4).
- **v3**: same as v1 except the seventh placement's anchors are
  `(0,3),(1,3),(2,3),(2,4)` — overlapping placement 8
  `(1,2),(1,3),(2,3),(3,3)` at (1,3),(2,3).

### Record 13 (13 cells; 12 weaker decompositions)

The compatible decomposition (Section 3) is one of the 12. The first
three variants found are:

- **v1**: same as the compatible decomposition except the placement
  covering layer-1 cell (3,4) uses anchors `(1,3),(1,4),(2,4),(3,4)`
  instead of `(2,6),(3,4),(3,5),(3,6)` — overlapping the vertical
  placement `(1,3),(1,4)` at (1,3),(1,4).
- **v2**: same as the compatible decomposition except the placement
  covering layer-1 cell (2,5) uses anchors `(0,4),(0,5),(1,5),(2,5)`
  instead of `(2,3),(2,4),(2,5),(3,3)` — overlapping placement 5
  `(0,2),(0,3),(0,4),(1,2)` at (0,4) and placement 1
  `(0,5),(0,6),(0,7),(1,5)` at (0,5),(1,5).
- **v3**: same as the compatible decomposition except the placement
  covering layer-1 cell (2,5) uses anchors `(1,7),(2,5),(2,6),(2,7)`
  instead of `(2,3),(2,4),(2,5),(3,3)` — overlapping placement 4
  `(1,6),(1,7),(2,7),(3,7)` at (1,7),(2,7).

## 5. Why the compatible decomposition is unique

Two observations hold for all 100 states:

1. The layer-1/2 occupancy determines the placements' cells above the
   cut: the exact cover of the occupancy by template above-sets is
   unique once the anchor cells are required to be pairwise disjoint.
2. In every state the unique decomposition's anchor cells partition
   all 32 layer-0 cells (7 flat placements x 4 anchors + 2 vertical
   placements x 2 anchors = 32 in records 13-100; 8 x 4 = 32 in
   records 1-12). There is no unused layer-0 cell, so no alternative
   anchor assignment can exist without overlapping an existing anchor.

The weaker model shows the anchor constraint is the binding one:
without it, the same layer-1/2 cells admit 8-1,296 groupings, all of
which share anchor cells and are therefore not compatible with the
state.

## 6. Conclusion

- **100 of the 100 recorded layer-shift states have exactly one
  compatible decomposition** of their layer-1/2 occupancy into
  crossing S placements (the 212 distinct normalized templates).
- **0 states have multiple compatible decompositions.**
- The unique decomposition's anchor cells partition layer 0 in every
  state, which is what forces uniqueness.
- If the anchor cells are ignored, all 100 states have multiple
  decompositions (8-1,296 each), but those are not compatible with the
  state.

This document is descriptive only; no new solver or state
representation is proposed or implemented.
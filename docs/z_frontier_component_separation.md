# Z-Frontier: Separation of Non-Single Components

Source: the 100 layer-1 frontiers (states in
`docs/z_frontier_state_stats_1m.md`, lines 140-239). Component shapes
and numbering follow `docs/z_frontier_component_shapes.md`.

## Definition

Two non-single connected components (size >= 2) are separated if at
least one empty column AND at least one empty row lie strictly between
their occupied cells: the gap between their column ranges is >= 1 and
the gap between their row ranges is >= 1 (bounding-box gap in both
axes).

## Results

- Frontiers containing at least one separated non-single pair:
  **2 of 100**.
- Separated non-single pairs: **2 of 28** non-single pairs that occur
  across all frontiers.

| Record | Shapes | Component A (x-range, y-range) | Component B (x-range, y-range) | Column gap | Row gap |
|---|---|---|---|---|---|
| 15 | 2 + 3 | vertical domino, x0, y0-1 | horizontal domino, x2-3, y5 | 1 (column 1) | 3 (rows 2-4) |
| 24 | 2 + 7 | vertical domino, x0, y3-4 | L triomino, x2-3, y6-7 | 1 (column 1) | 1 (row 5) |

In both cases the separated components sit in the leftmost column and
in the rightmost columns of the 4-column grid, with the middle column
empty of both.

## Never-co-occur check

Neither separated pair uses component shapes that otherwise never
co-occur: both pairs (2 + 3 and 2 + 7) are among the co-occurring
pairs listed in `docs/z_frontier_component_relations.md` (2 + 3 in
8 records, 2 + 7 in 1 record). No new co-occurrence is introduced by
the separated pairs; the constraints document is not contradicted.
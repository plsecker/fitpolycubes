# S-Frontier: Crossing-Piece Cells in the 100 Layer-Shift States

Solver: `solvers/s_z_frontier_packed.py` (S pentacube, 4x8 box).
Sources: the 100 layer-shift records in
`docs/z_frontier_state_stats_1m.md` (lines 140-239), the 100
post-shift states in `docs/z_frontier_postshift_states.md`, the
template geometry in `docs/z_frontier_live_cells.md`, and the
sealed-layer argument in `docs/z_frontier_sealed_layer_invariant.md`.
No solver run was performed; all states below were decoded from the
recorded diagnostics.

## 1. Definitions

- **State**: one integer, three 32-bit layer masks — bits 0-31 =
  layer 0, bits 32-63 = layer 1, bits 64-95 = layer 2. Bit = x + 4y,
  x = column 0-3, y = row 0-7.
- **The current z-cut**: the plane between layer 0 and layer 1 — the
  plane the frontier advances across when a shift fires. When layer 0
  is full, the solver shifts (`state >> 32`): layer 0 is sealed and
  discarded, layers 1-2 survive into the new layers 0-1.
- **A placement crosses the cut** iff it has cells below the cut
  (layers <= 0, i.e. layer 0 or the sealed region) and cells above the
  cut (layers 1-2).
- Note: the sealed-layer invariant
  (`docs/z_frontier_sealed_layer_invariant.md`) guarantees no placement
  ever reaches into the sealed region from a future state, so no
  placement crosses the boundary between the sealed region and layer 0.
  The cut discussed here is the advancing plane between layer 0 and
  layer 1.

## 2. Why every occupied cell in layers 1-2 is a crossing cell

Two facts from the solver's template construction:

1. Every placement is anchored at `target = first_empty(layer0)`, and
   `make_shifted_template` rejects any cell with `rel < 0`. The anchor
   is therefore a minimum-z cell of the placement, in layer 0.
2. Every one of the 488 templates has cells at rel 0 **and** rel 1
   (`docs/z_frontier_live_cells.md`: "Every template has at least one
   cell at rel = 1 (the anchor is never the top cell of an accepted
   placement)"). The S pentacube is never flat, so no placement lies
   entirely in layer 0.

A cell in the current layer 1 was placed at rel 1 (0 shifts ago) or
rel 2 (1 shift ago); a cell in the current layer 2 was placed at rel 2
(0 shifts ago). In every case the placement has cells below the cut
(layer 0 at placement time, possibly since sealed) and cells above the
cut (layers 1-2). Hence:

> **Every occupied cell in layers 1-2 is necessarily part of a
> placement crossing the current z-cut.** There is no ambiguity for
> these cells; the occupancy alone identifies them.

A cell in the current layer 0, by contrast, could be an anchor (rel 0,
0 shifts ago — crossing), a rel-1 survivor (1 shift ago — crossing), or
a rel-2 survivor (2 shifts ago — its placement is entirely below the
cut, not crossing). Layer-0 cells are therefore ambiguous from
occupancy alone, but layer 0 is sealed at the shift, so their crossing
status never affects the next state.

## 3. The 100 layer-shift states, decoded

| Layer | Records 1-12 | Records 13-100 |
|---|---|---|
| 0 | full, 32 cells (shift trigger) | full, 32 cells (shift trigger) |
| 1 | 8 cells | 9 cells |
| 2 | 0 cells | 4 cells |
| Total occupied | 40 | 45 |

- Layer 0 is `0xFFFFFFFF` in all 100 states (the shift trigger).
- Layer 1 holds 8 cells in records 1-12 and 9 cells in records 13-100
  (consistent with `docs/z_frontier_shift_shapes.md`).
- Layer 2 is empty in records 1-12 and holds exactly 4 cells in
  records 13-100.
- The recorded post-shift states match `state >> 32` exactly for all
  100 records (verified): the post-shift state is precisely the
  layer-1 mask OR the layer-2 mask shifted up by 32 bits.

**Crossing cells per state**: the 8-12 occupied cells of layers 1-2
(8 for records 1-12; 13 for records 13-100) are necessarily crossing
cells and are exactly the cells that survive the shift. The 32 layer-0
cells could each be interpreted as part of a crossing placement, but
they are sealed.

## 4. Examples from the diagnostics

### Record 1 (layer 2 empty)

- Layer 1 = `0x42429009`, 8 cells:
  (0,0), (3,0), (0,3), (3,3), (1,4), (2,5), (1,6), (2,7).
- Layer 2 = 0.
- Post-shift state = `1111658505` = `0x42429009` — exactly these 8
  cells. All 8 are crossing cells; they become the new layer 0.

### Record 13 (first state with layer 2 occupied)

- Layer 1 = `0x90492019`, 9 cells:
  (0,0), (3,0), (0,1), (1,3), (0,4), (3,4), (2,5), (0,7), (3,7).
- Layer 2 = `0x6011`, 4 cells: (0,0), (0,1), (1,3), (2,3).
- Post-shift state = `105628551421977` = `0x601190492019` — the 9
  layer-1 cells become the new layer 0, the 4 layer-2 cells become the
  new layer 1. All 13 are crossing cells.

### Record 100

- Layer 1 = `0x904a1209`, 9 cells:
  (0,0), (3,0), (1,2), (0,3), (1,4), (3,4), (2,5), (0,7), (3,7).
- Layer 2 = `0x220600`, 4 cells: (1,2), (2,2), (1,4), (1,5).
- Post-shift state = `9576748698702345` = `0x220600904a1209`.

### Same (x,y) at two z-levels

In records 13-100, layer 1 and layer 2 share 2-4 (x,y) positions (61
of 88 records share exactly 3). Example, record 13: (0,0), (0,1),
(1,3) are occupied in both layer 1 and layer 2. This is consistent with
a vertical S placement occupying one column at rel 1 and rel 2: the
same (x,y) position can host two cells of one crossing placement. The
occupancy alone does not say whether the layer-1 and layer-2 cells at a
shared (x,y) belong to the same placement or to two different ones.

## 5. Smallest information needed to identify the crossing pieces

- **Cell level (the crossing cells)**: the occupancy masks of layers
  1-2 — already present in the state — identify the crossing cells
  exactly. No per-cell flags or piece labels are needed, because the
  anchoring rule (Section 2) makes every layer-1/2 cell a crossing
  cell with no ambiguity. This is the smallest information: zero extra
  bits beyond the state.
- **Layer-0 cells**: distinguishing crossing layer-0 cells (anchors,
  rel-1 survivors) from non-crossing ones (rel-2 survivors) would need
  one bit per layer-0 cell, but this is unnecessary — layer 0 is
  sealed at the shift and never affects the next state.
- **Piece level (complete 5-cell placements)**: identifying which
  cells belong to the same crossing placement (e.g. which layer-0 cell
  is the anchor of a given layer-1/2 cell, or whether the layer-1 and
  layer-2 cells at a shared (x,y) are one placement or two) is not
  determined by the occupancy; the smallest additional information
  would be piece labels or the placement history. The recorded
  diagnostics do not contain this, and it is not needed to identify
  the crossing cells.

## 6. Conclusion

In the 100 recorded layer-shift states, the occupied cells that could
be parts of S placements crossing the current z-cut are:

- all 8-12 occupied cells of layers 1-2 (necessarily crossing; they
  are exactly the cells that survive the shift into the post-shift
  state), and
- all 32 layer-0 cells (each could be interpreted as crossing, but the
  status is ambiguous and the layer is sealed).

The smallest information needed to identify the crossing cells is the
layer-1/2 occupancy already stored in the state; the post-shift
diagnostics confirm this by recording exactly those cells
(`post-shift = state >> 32`).

This document is descriptive only; no new state representation or
solver is proposed or implemented.
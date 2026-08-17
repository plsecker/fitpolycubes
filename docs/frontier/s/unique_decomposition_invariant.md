# S-Frontier: Conditions for the Unique Crossing-S Decomposition

Solver: `solvers/s_z_frontier_packed.py` (S pentacube, 4x8 box).
Sources: `docs/s_frontier_crossing_decomposition.md` (the 100-state
decomposition analysis), `docs/z_frontier_live_cells.md` (template
geometry), `docs/z_frontier_state_stats_1m.md` and
`docs/z_frontier_postshift_states.md` (the 1M diagnostics run), and
the solver code itself. No discovery run was performed; only
`build_templates()` (template geometry) and the recorded diagnostics
were used.

## 1. Setup and definitions

- **State**: one integer, three 32-bit layer masks (bits 0-31 = layer
  0, 32-63 = layer 1, 64-95 = layer 2). Layer 3 is not stored.
- **Templates**: the solver's `build_templates()` output, 488 raw
  entries deduplicated to **212 distinct** packed templates. Each
  template is anchored with its target cell at rel 0 (layer 0) and
  spans rel 0-2 (`make_shifted_template`, lines 108-140).
- **Pre-shift state**: a state with layer 0 completely filled
  (`current == WORD_MASK`, line 263); the solver then shifts
  (`state >> 32`).
- **Occupancy**: the layer-1/2 cells of a pre-shift state, as
  (layer, cell) pairs.
- **Decomposition**: a set of templates whose layer-1/2 cells
  partition the occupancy.
- **Compatible decomposition**: a decomposition whose layer-0 anchor
  cells are pairwise disjoint (each cell hosts at most one placement).
- **The claim (observed)**: each of the 100 sampled pre-shift states
  has exactly one compatible decomposition.

### Verified template geometry (from `build_templates()`)

The 212 distinct templates come in exactly three shapes:

| Shape | Anchors (rel 0) | Rel-1 cells | Rel-2 cells | Count |
|---|---|---|---|---|
| flat | 4 | 1 | 0 | 64 |
| vertical | 2 | 1 | 2 | 84 |
| standing | 1 | 4 | 0 | 64 |

Every template has at least one rel-1 cell; no template has a rel-2
cell count other than 0 or 2; no template reaches rel 3.

## 2. What is proven from the code and template definitions

**P1. Layer 3 is dead; the 3-layer model is complete.**
No template contains a cell at rel 3 (max rel 2 in all three shapes),
so no placement can ever write or be blocked by a layer-3 bit, and
shifts only move cells downward. The layer-3 word is always zero.
(This is the conclusion of `docs/z_frontier_live_cells.md`.)

**P2. Every placement anchored in layer 0 contributes at least one
cell to layer 1.** Every template has at least one rel-1 cell (the
anchor is never the top cell of an accepted placement).

**P3. In any pre-shift state, the layer-1/2 occupancy is exactly the
union of the above-cells of the placements made since the last shift,
and those placements' anchors partition layer 0.**
All placements are anchored at rel 0 = layer 0 of the current state
(`apply_template`, lines 185-192); the solver never overlaps
placements. Layer 0 is full at a pre-shift state, so every layer-0
cell is the anchor cell of exactly one placement since the last shift:
the anchors are pairwise disjoint and cover all 32 cells. The
layer-1/2 cells of the state are exactly the rel-1/rel-2 cells of
those placements.

**P4. The placement structure of the actual history is determined by
the occupancy cell counts (L1, L2).** From P3 and the shape table:
each vertical placement covers exactly 2 layer-2 cells, so
v = L2/2; the anchor and rel-1 bookkeeping then give
s = (4·L1 - L2 - 32)/15 standing placements and
f = (256 - 2·L1 - 7·L2)/30 flat placements. For the sampled shapes:
(8, 0) -> (v, f, s) = (0, 8, 0); (9, 4) -> (2, 7, 0). In particular,
for these shapes the actual history uses no standing placements and
its anchors partition layer 0.

**P5. First-empty-cell anchoring does not constrain the decomposition
count.** The first-empty rule (line 300: the next placement must cover
`first_empty(layer0)`) is a search-ordering rule. Any decomposition
whose anchors partition layer 0 is realizable in first-empty order:
order the placements by ascending minimum anchor cell; at each step
the first empty cell of layer 0 is exactly the next placement's
minimum anchor, and the placement does not overlap the state built so
far. Hence, given a pre-shift occupancy, the number of compatible
decompositions is a function of the occupancy and the template set
only; first-empty enters only through which states are reachable.

**P6 (verified computationally, geometric).** For the 100 sampled
occupancies, no standing (1,4,0) template fits the 8-cell occupancies
(records 1-12), and at most one fits 7 of the 13-cell occupancies.
For records 1-12 this forces the decomposition structure: all
candidates are flat (4,1,0) templates, so 8 placements cover the 8
layer-1 cells, and 8 x 4 = 32 pairwise-disjoint anchors partition
layer 0.

## 3. What is only observed in the 100-state sample

The following were verified by exact-cover search (MRV backtracking,
cross-checked by brute-force enumeration) on the 100 layer-shift
records of `docs/z_frontier_state_stats_1m.md` (lines 140-239), and
are NOT consequences of the code or template definitions alone:

- **O1. Uniqueness**: every one of the 100 sampled pre-shift states
  has exactly one compatible decomposition; none has multiple and none
  has zero.
- **O2. Anchor partition**: the unique decomposition's anchors
  partition all 32 layer-0 cells in 100/100 states. (For records 1-12
  this is forced by P6; for records 13-100 it is observed.)
- **O3. Shape usage**: the unique decompositions use only flat and
  vertical templates (8 flat for records 1-12; 7 flat + 2 vertical for
  records 13-100). Standing templates are never used, even though a
  standing candidate exists for 7 of the 13-cell states.
- **O4. Occupancy shapes**: records 1-12 have 8 layer-1 cells and no
  layer-2 cells; records 13-100 have 9 layer-1 and 4 layer-2 cells.
  These are the shapes of the sampled states, not of all reachable
  pre-shift states.
- **O5. Specific assignments**: which template covers which cell in
  each state.

The weaker model (anchors ignored) shows the anchor constraint is the
binding one: without it, all 100 occupancies admit 8-1,296
decompositions, all of which share anchor cells.

## 4. Which of the four candidate conditions are essential

| Condition | Essential? | Role |
|---|---|---|
| First-empty-cell anchoring | **No** | Search-ordering rule only (P5). Determines which states are reachable, hence which occupancies exist, but does not enter the decomposition count. Any anchor-partitioning decomposition is first-empty-realizable. |
| The S template set | **Yes** | The claim is conditional on the 212 distinct S templates and their three shapes (P3, P4, P6). The uniqueness is a property of this specific geometry; it does not transfer to other pieces. |
| Layer-0 completely filled before shifting | **Yes** | The claim is about pre-shift states. P3 (anchors partition layer 0) and P4 (structure forced by cell counts) rely on layer 0 being full. The claim does not extend to states with unfilled layer 0. |
| The 3-layer live frontier | **Yes (as the model)** | The decomposition is defined on layers 1-2 of the pre-shift state, and the 3-layer model is complete because layer 3 is provably dead (P1). The "3" is a consequence of the S geometry (max rel 2), not an independent condition. |

The exact conditions under which the observed uniqueness holds are:
a pre-shift state (layer 0 full), the S template set, the 3-layer
state model, and an occupancy of the sampled shapes. First-empty
anchoring is not among them.

## 5. What would still need to be tested to claim a general invariant

- **T1. All reachable pre-shift states.** The 1M diagnostics run
  recorded 2,451 layer shifts, all with distinct post-shift states
  (`docs/z_frontier_postshift_states.md`), hence 2,451 distinct
  pre-shift states. Only the first 100 were analyzed. Uniqueness must
  be checked for all 2,451.
- **T2. The full reachable set.** The 1M run was capped at 1,000,000
  states (`--max-states 1000000`); the reachable set may be larger, so
  the 2,451 pre-shift states are a prefix, not the whole population.
- **T3. Other occupancy shapes.** Whether reachable pre-shift states
  exist with (L1, L2) other than (8, 0) and (9, 4), and whether
  uniqueness holds for them. P4 predicts the history structure for any
  (L1, L2), but uniqueness of the reconstruction is separate.
- **T4. Standing templates.** Whether a standing (1,4,0) template can
  participate in a compatible decomposition of any reachable pre-shift
  state (7 sampled states have a standing candidate; none used it).
- **T5. Search-order independence.** Whether uniqueness persists for
  occupancies reachable under a different placement order (e.g.,
  without first-empty), to confirm P5 empirically.
- **T6. Other pieces.** Whether any analogue holds for other
  pentacubes; the S-specific geometry (three shapes, anchor counts)
  suggests the claim does not transfer.

## 6. Conclusion

- Proven from the code and template definitions: layer 3 is dead and
  the 3-layer model is complete (P1); every placement contributes a
  layer-1 cell (P2); in any pre-shift state the occupancy is the union
  of above-cells of placements whose anchors partition layer 0 (P3);
  the history's placement structure is determined by the cell counts
  (P4); first-empty anchoring does not constrain the decomposition
  count (P5); and for the sampled 8-cell occupancies the flat-only
  structure is forced (P6).
- Observed only in the 100-state sample: the uniqueness itself (O1),
  the anchor partition for the 13-cell states (O2), the flat/vertical
  shape usage (O3), the occupancy shapes (O4), and the specific
  assignments (O5).
- Essential conditions: the S template set, layer 0 completely filled
  before shifting, and the 3-layer live frontier (as the complete
  state model). First-empty-cell anchoring is not essential for the
  uniqueness; it only determines which states exist.
- To claim a general invariant, uniqueness must be tested on all
  reachable pre-shift states (at least the 2,451 recorded in the 1M
  run, and beyond the 1M cap), on any other occupancy shapes, and on
  search orders other than first-empty.

This document is descriptive only; no new solver or state
representation is proposed or implemented.
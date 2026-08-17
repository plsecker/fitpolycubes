# S-Frontier: Compatible Decomposition of All 2,451 Pre-Shift States

Solver: `solvers/s_z_frontier_packed.py` (S pentacube, 4x8 box).
States: all 2,451 pre-shift states recorded in
`docs/z_frontier_all_shift_states_1m.md` (the complete layer-shift
event list of the 1M diagnostics run).
Definition and template set: identical to
`docs/s_frontier_crossing_decomposition.md` — the 212 distinct
templates from the solver's `build_templates()`, a decomposition
partitions the layer-1/2 occupancy, and a compatible decomposition
additionally requires pairwise-disjoint layer-0 anchor cells.
Method: exact-cover search (MRV backtracking), the same as the
100-state analysis. No discovery run was performed; only
`build_templates()` (template geometry) and the recorded states were
used.

## 1. Classification

| Class | States |
|---|---|
| 0 compatible decompositions | **0** |
| exactly 1 compatible decomposition | **2,451** |
| >1 compatible decompositions | **0** |

- Minimum number of decompositions: **1**; maximum: **1**.
- Every one of the 2,451 pre-shift states has exactly one compatible
  decomposition. This extends the uniqueness observed for the first
  100 layer-shift records (O1 in
  `docs/s_frontier_unique_decomposition_invariant.md`) to the full
  shift population of the 1M run.
- The zero-decomposition class is empty, consistent with P3 of the
  invariant doc: the actual history of any pre-shift state is itself a
  compatible decomposition.

## 2. Occupancy-pattern distribution

Four (L1, L2) patterns occur; all 2,451 occupancies are pairwise
distinct (no two pre-shift states share the same layer-1/2 cell set).

| (L1, L2) | States | Record range | Unique decomposition structure | Placements |
|---|---|---|---|---|
| (8, 0) | 12 | 1-12 | 8 flat | 8 |
| (9, 4) | 404 | 13-416 | 2 vertical + 7 flat | 9 |
| (10, 8) | 1,862 | 429-2451 | 4 vertical + 6 flat | 10 |
| (16, 2) | 173 | 417-2340 | 1 vertical + 7 flat + 2 standing | 10 |

- The (8, 0) and (9, 4) patterns are exactly the two shapes seen in
  the 100-state sample (records 1-12 and 13-100).
- The (10, 8) and (16, 2) patterns are new: they appear only beyond
  the first 100 shift records.
- The (16, 2) and (10, 8) records are interleaved in discovery order
  (81 pattern changes between adjacent records; 40 transitions
  (16,2)->(10,8) and 39 (10,8)->(16,2)), so the record order is not
  grouped by pattern.

## 3. Standing-template usage

- **173 states use the (1-anchor, 4-rel-1) "standing" template** —
  exactly the 173 states of the (16, 2) pattern, each with **2
  standing placements** in its unique decomposition.
- This answers the open question T4 of the invariant doc: a standing
  template does participate in compatible decompositions of reachable
  pre-shift states (the 100-state sample contained no such state).
- The standing usage is exactly what the structural formula P4
  predicts for (16, 2): s = (4*16 - 2 - 32)/15 = 2.
- No state of the other three patterns uses a standing template.

## 4. Structural-rule checks (invariant doc)

| Rule | Checked on 2,451 states | Result |
|---|---|---|
| P4: structure determined by (L1, L2): v = L2/2, s = (4*L1 - L2 - 32)/15, f = (256 - 2*L1 - 7*L2)/30 | unique decomposition's (v, f, s) vs prediction | **0 mismatches** |
| O2: anchors partition all 32 layer-0 cells | anchor union size = 32 | **0 failures** (100%) |
| Observed shape rules: (8,0) -> 8 flat; (9,4) -> 2 vertical + 7 flat | per-pattern structure | **0 failures** |

- The P4 formula is confirmed for all four patterns, including the two
  new ones: (10, 8) -> (v, f, s) = (4, 6, 0); (16, 2) -> (1, 7, 2).
- In every state the unique decomposition's anchors partition layer 0
  (32 cells), extending O2 from the 100-state sample to all 2,451.
- No state contradicts the structural rules of
  `docs/s_frontier_unique_decomposition_invariant.md`.

## 5. Comparison with the 100-state sample

| Property | 100-state sample | All 2,451 states |
|---|---|---|
| Unique compatible decomposition | 100/100 | 2,451/2,451 |
| Anchor partition of layer 0 | 100/100 | 2,451/2,451 |
| Occupancy patterns | (8, 0), (9, 4) | (8, 0), (9, 4), (10, 8), (16, 2) |
| Standing-template usage | none | 173 states (all (16, 2)) |
| P4 structure mismatches | 0 | 0 |

## 6. Conclusion

- All 2,451 pre-shift states of the 1M run have exactly one compatible
  decomposition into the 212 distinct S crossing templates; none has
  zero and none has more than one.
- Four occupancy patterns occur: (8, 0) x 12, (9, 4) x 404,
  (10, 8) x 1,862, (16, 2) x 173; all occupancies are distinct.
- The standing (1, 4, 0) template is used, exactly in the 173 (16, 2)
  states (2 per state), as predicted by the structural formula.
- No state contradicts the structural rules of the invariant doc; the
  uniqueness, the anchor partition, and the P4 structure formula all
  hold for the full shift population.

This document is descriptive only; no new algorithm is proposed and no
solver code is modified.
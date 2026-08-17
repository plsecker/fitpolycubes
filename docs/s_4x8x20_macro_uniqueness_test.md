# S 4x8x20: Macro-Path Uniqueness Test (Exclusions E0 and E1)

Run: standalone analysis script (`/tmp/opencode/macro_exclusion_test.py`,
results in `/tmp/opencode/macro_exclusion_test_results.txt`).  The solver
(`solvers/s_z_frontier_packed.py`) is **not modified**; its pure functions
(`build_templates`, `apply_template`, `first_empty`, `layer_mask`,
`shift_state`, `WORD_MASK`) are reused with identical semantics, following
the established pattern of `docs/s_z_frontier_macro_reachability.md` and
`docs/s_z_frontier_length_analysis.md`.

**This test establishes macro-path uniqueness only, not full tiling
uniqueness.**  Surviving "macro paths" are distinct sequences of post-shift
states; placement-level alternatives *within* a layer (different templates
realizing the same macro edge) are deliberately not enumerated here.

## Method

* **First generation modeled exactly.**  The first-generation tree from
  the empty state `0` is complete: 3,162,387 states, cap not hit,
  331,765 distinct post-shift sources.  The verified edge `0 -> s*` with
  `s* = 6163195513375031274` is among them, and E0 is applied by removing
  `s*` from the allowed starting sources.
* **Macro graph.**  The standard capped closure built from the sources:
  15,000,991 macro states / 14,781,970 macro edges (15,000,000-state cap
  hit), DAG (Kahn: all nodes visited), max BFS distance 85.  Because the
  BFS processes nodes in non-decreasing distance order, the closure is
  complete through distance 19 — the region where the 20-layer question
  lives — so all verdicts below are **exact**, not capped.
* **Backward DP with edge deletions.**  `R(s)` = bitmask of macro
  distances `d` with `0` reachable from `s` in exactly `d` edges,
  computed over the Kahn reverse order; the excluded edge is skipped.
  A 20-layer return path exists iff some allowed first-gen source `s` has
  `19 in R(s)` (1 first-gen edge + 19 macro edges).
* **Exact path counting.**  Distinct 19-edge macro walks `s -> 0` are
  counted by an edge-exact DP restricted to the basin of `0` (the states
  with non-empty `R`; ≤ 226 states), so counting is cheap and exact.

## Scenarios tested

| # | Exclusion | Meaning |
|---|---|---|
| baseline | none | verified graph as stored/analyzed |
| E0 | forbid `0 -> 6163195513375031274` | verified first-generation edge |
| E1 | forbid `13835058072323104239 -> 3993075831` | verified macro edge (layer 3 of the N=20 path) |

## Results

| Scenario | Any path `0 -> 0` in exactly 20 completed layers? | Surviving sources | Surviving macro paths (19-edge walks `s -> 0`) |
|---|---|---|---|
| baseline | **yes** | 1 (`6163195513375031274`) | 1 |
| E0 | **no** | 0 | 0 |
| E1 | **no** | 0 | 0 |

Baseline cross-check: the single surviving source `s*` at distance 19
reproduces the stored length analysis exactly
(`sources_with_nonempty_R`: only `6163195513375031274` with `[19]`), and
the baseline basin is the documented 226 states.

### E0 detail (forbid first-gen edge `0 -> s*`)

* `s*` is excluded from the allowed starting sources; the macro graph
  itself is unchanged (basin still 226 states).
* **No first-gen source other than `s*` reaches `0` in 19 macro edges** —
  confirmed directly: 0 surviving sources, 0 surviving macro paths.

### E1 detail (forbid macro edge `13835058072323104239 -> 3993075831`)

* The edge is present in the macro graph (`e1_edge_present = True`).
* The edge is a **cut edge for the entire `s* -> 0` connection**: after
  removal, the basin shrinks from 226 to **224** states, and `s*` itself
  no longer reaches `0` at *any* distance (the only walk from `s*` to `0`
  of any length passes through this edge).
* 0 surviving sources, 0 surviving macro paths.

## Interpretation

* The verified 4x8x20 tiling is carried by a **single macro path**: the
  baseline shows exactly **1 distinct 19-edge macro walk**
  `s* -> ... -> 0` (not merely 1 source).
* **E0 and E1 both eliminate every 20-layer macro path**; there is no
  alternative macro-level route back to `0` in 20 completed layers in
  either case.
* This confirms macro-path uniqueness: no second 20-layer return path
  exists in the macro graph, and both exclusions are effective at killing
  the verified path.
* **Scope caveat**: this says nothing about placement-level alternatives
  within a layer.  A second *tiling* could in principle share the same
  macro path (same post-shift states) while differing in the placement
  choices that fill individual layers.  Enumerating those is explicitly
  out of scope for this test (see
  `docs/s_4x8x20_uniqueness_plan.md`, type-B freedom).

## Caveats

* The macro graph is the capped closure: state/edge counts are lower
  bounds.  All verdicts above are exact because they live at distance
  ≤ 19, where the closure is complete.
* `succ[0]` is truncated by the per-source intermediate cap (the closure
  processing of `0` itself hit the 1,000,000-intermediate cap, leaving
  `R(0) = [0]`), so through-0 cycles (N = 80, 100, …) are not visible.
  The 20-layer question is unaffected: it uses the complete first-gen
  edge set (331,765 sources) plus macro edges at distance ≤ 19.
* The test counts macro paths, not tilings; distinctness of tilings
  (placement sets) is not addressed here.

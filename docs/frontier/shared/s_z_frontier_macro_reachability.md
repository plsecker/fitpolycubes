# S Z-Frontier: Macro Reachability from the Empty State

Run: standalone analysis script (`/tmp/opencode/macro_reachability.py`) that
starts from the **empty 96-bit frontier state** (state `0`), explores all
legal placement sequences up to the first layer shift, then follows the
existing macro-transition logic to closure.

The solver itself is NOT modified and its discovery loop is not run; the
script reuses the solver's pure functions (`build_templates`,
`apply_template`, `first_empty`, `layer_mask`, `shift_state`, `WORD_MASK`)
with identical semantics.

## Method

A **macro node** is a post-shift state: the state immediately after a layer
shift (`post_shift_state = pre_shift_state >> 32`).

1. **First generation (from state 0).** Starting from the empty state, the
   script explores the placement tree exactly as the solver's `discover`
   loop does: repeatedly apply `templates[first_empty(layer0)]` to the
   current state; when `layer0 == WORD_MASK`, the shift successor
   `state >> 32` is recorded as a first-generation source and that path
   stops.  All intermediate (non-shift) states are discarded; only distinct
   post-shift states are kept.  Tree cap: 5,000,000 states (not hit).

2. **Macro closure.** From every reached post-shift state, the macro
   transition is iterated (each macro edge = fill one full layer, then
   shift) until no new post-shift states appear, with a closure cap of
   15,000,000 macro states.  The closure BFS processes nodes in
   non-decreasing distance order, so the distance-≤19 subgraph is complete
   even though the cap was hit (max BFS distance in the capped closure:
   85 ≥ 20).

3. **DAG check.** Kahn's algorithm (topological sort) on the capped
   closure; a cycle exists iff the sort visits fewer nodes than the graph
   has.

4. **Longest path.** Longest-path DP over the Kahn topological order
   (longest path in macro edges from any first-generation source to any
   macro state), plus the endpoints and sources attaining it.

5. **Tiling question (4x8xN, N = 1..20).** A complete 4x8xN tiling exists
   iff the empty state `0` is reachable as a post-shift state at macro
   distance exactly `N-1`: the first generation consumes layer 1, each
   macro edge consumes one further layer, and the only way to reach `0` is
   the immediate shift from a state with `layer0 == WORD_MASK` and layers
   1, 2 empty (the final layer of the tiling).  Distances are computed by
   an exact layer-BFS over the capped closure for distances 0..20.

**Per-source safety limit**: `MAX_INTERMEDIATE = 1,000,000` distinct
non-shift states explored per source; **no source hit the limit**.

## First generation (from state 0)

| Metric | Value |
|---|---|
| Placement-tree states explored | 3,162,387 |
| Tree cap (5,000,000) hit | no |
| First-generation post-shift sources | 331,765 |
| Elapsed | 4.2 s |

The empty state branches into 331,765 distinct post-shift states at the
first layer shift — far more than the 2,451 post-shift states recorded by
the 1M-state solver run used in the earlier macro-graph analysis.

## Macro closure (capped)

| Metric | Value |
|---|---|
| Macro states (capped) | 15,000,991 |
| Macro edges (capped) | 14,781,970 |
| Closure cap (15,000,000) hit | **yes** |
| Total intermediate states explored | 374,388,610 |
| Max BFS distance in capped closure | 85 |
| Distance-≤19 subgraph complete | yes |
| Closure elapsed | 668.0 s |

The closure cap **was hit**: the reachable macro state space from the empty
state is larger than 15,000,991 states, so the state/edge counts above are
**lower bounds** on the true closure.  (An earlier 2,000,000-cap run also
hit its cap at 2,004,846 states, confirming the space is large.)

## DAG check

Kahn's algorithm on the capped closure: **is_dag = True** — the
topological sort visited all 15,000,991 of 15,000,991 nodes (48.4 s), so
the capped closure contains no directed cycle.  This is consistent with the
earlier complete closure of the 2,451 recorded sources (31,113 states,
0 nontrivial SCCs).  Strictly, the DAG verdict here is proven for the
capped prefix; the full empty-state closure was not computed (infeasible
within memory/time).

## Longest path (capped)

| Metric | Value |
|---|---|
| Longest path (macro edges, capped) | 94 |
| Endpoints attaining the longest path | 8 |
| Sources starting longest paths | 1 |

Longest-path source: `6163195513375031274`.

Endpoints (post-shift states at longest-path distance 94):

```
47854251521522430
47888203237997310
309676149166391184
309678412614156192
525850369616289348
918827784608774004
9819066548199716724
10019438384180403780
```

Because the closure is capped, 94 is a **lower bound** on the true longest
path.  A further lower bound follows from the catalogue: 4x8x130 is a
prime (Shirakawa 2014), so `0` is reachable at macro distance 129, i.e.
the true longest path is at least **129** edges.

## Tiling question (4x8xN, N = 1..20)

Empty state `0` is in the macro states: **yes**.  Distances at which `0` is
reachable (checked 0..20): **[19]** — exactly one distance, so exactly one
tileable height in range.

| N | 32N/5 integer (cell-count check) | 0 reachable in N-1 edges | 4x8xN tileable |
|---|---|---|---|
| 1 | no | no | no |
| 2 | no | no | no |
| 3 | no | no | no |
| 4 | no | no | no |
| 5 | yes | no | no |
| 6 | no | no | no |
| 7 | no | no | no |
| 8 | no | no | no |
| 9 | no | no | no |
| 10 | yes | no | no |
| 11 | no | no | no |
| 12 | no | no | no |
| 13 | no | no | no |
| 14 | no | no | no |
| 15 | yes | no | no |
| 16 | no | no | no |
| 17 | no | no | no |
| 18 | no | no | no |
| 19 | no | no | no |
| 20 | yes | yes | **YES** |

Only **4x8x20** is tileable among N = 1..20.  The cell-count check (32N
cells must be divisible by 5) passes for N = 5, 10, 15, 20, but the
reachability check rules out 5, 10, 15.

## Verification against the catalogue

* **4x8x20 = YES** matches `catalogues/s_catalogue.py`: `Box(4, 8, 20)`
  is a 1+ prime (Postl 1998).
* **4x8x10 = no** matches the catalogue's `4x8x{10,30,50,70,90,110}: 0`
  (Shirakawa 2014) and the empirical C++ exact-cover result in
  `docs/s_4x8x10_baseline.md` (0 solutions).
* **4x8x5 and 4x8x15 = no** are new results (not listed in the catalogue);
  they are consistent with the catalogue's pattern that the only tileable
  heights in range are multiples of 20.
* The tiling verdicts are **exact** (not capped): the closure BFS is
  complete through distance 19 (max BFS distance 85 ≥ 20), and the
  distance-≤19 subgraph is where all N = 1..20 verdicts live.
* An earlier 2,000,000-cap run gave the identical tiling table (0
  reachable only at distance 19), cross-checking the result.

## Caveats

* Macro state/edge counts and the longest path (94) are **lower bounds**:
  the closure cap of 15,000,000 was hit.
* The DAG verdict is proven for the capped closure; the full closure was
  not computed (memory/time infeasible on this machine: 11 GB RAM).
* The longest path is at least 129 (catalogue consequence, 4x8x130 prime),
  so the capped value 94 is known to be far from the true value.
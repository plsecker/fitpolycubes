# Z-Frontier Growth: 100k vs 1M State Cap

Comparison of the two diagnostics runs of
`solvers/s_z_frontier_packed.py --diagnostics`
(S, 4x8): `--max-states 100000` → `docs/z_frontier_state_stats.md`
and `--max-states 1000000` → `docs/z_frontier_state_stats_1m.md`.

Duplicate rate = duplicate transitions / processed states;
shift rate = layer shifts / processed states.

## Comparison

| Metric | 100k run | 1M run | Growth (×) |
|---|---|---|---|
| State count | 100,001 | 1,000,000 | 10.0 |
| Processed states | 29,086 | 409,873 | 14.1 |
| Duplicate transitions | 21 | 353 | 16.8 |
| Duplicate rate | 0.072% | 0.086% | ~1.2 |
| Layer shifts | 4 | 2,451 | 612.8 |
| Shift rate | 0.014% | 0.598% | ~43 |
| Branching states (out-degree > 1) | 23,396 | 267,139 | 11.4 |
| Maximum out-degree | 11 | 11 | 1.0 |

## What changes from 100k to 1M

Raising the cap tenfold explores 14.1× as many processed states
(29,086 → 409,873), so the search reaches substantially deeper layers
of the frontier rather than just more states at the same depth. The
most dramatic change is layer shifts: 4 → 2,451 (612.8×), and the
shift rate jumps from 0.014% to 0.598% of processed states, because
states with a full top layer (`WORD_MASK`) that trigger a shift become
common only deeper in the tree. Duplicate transitions also grow
super-linearly (21 → 353, 16.8×), although the duplicate rate stays
nearly flat (0.072% → 0.086%). Branching states grow 11.4× but their
share of processed states falls from 80.4% to 65.2%, with degree-1
states (which include the shifts) rising from third to second place in
the out-degree histogram. Maximum out-degree stays 11, since it is
bounded by the placement set at a single cell and is independent of
search depth.

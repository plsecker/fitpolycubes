# S 4x8x10 Z-Frontier Result

Solver: `solvers/s_z_frontier_packed.py --max-states 5000000`
(96-bit 3-layer packed state, Python `set[int]` seen).

| Metric | Value |
|---|---|
| States | 5,000,001 |
| Processed | 4,155,167 |
| Duplicate states | 8,417 |
| Layer shifts | 324,466 |
| Branching states | 1,232,921 |
| Max out-degree | 11 |
| Elapsed | 62.3 s |
| Peak RSS | 393 MB |

Termination: **hit the state limit** (5,000,000) — the reachable state
space is not exhausted; 844,834 states remained queued. Peak RSS
cross-checked via `/proc` VmHWM polling (393 MB, agrees with the
solver's `ru_maxrss` report).

Context: the 4x8x10 box itself has no S tiling (see
`docs/s_4x8x10_baseline.md`); this run explores the 4x8 z-frontier
state space, which exceeds 5M states.
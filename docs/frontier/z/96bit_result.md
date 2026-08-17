# Z-Frontier: 96-bit State Run (1M states)

## Change

`solvers/s_z_frontier_packed.py` was modified to drop the dead fourth
frontier layer:

- `LAYERS = 4` -> `LAYERS = 3`; the packed state is now 3 x 32 bits
  (layer 0 = bits 0-31, layer 1 = bits 32-63, layer 2 = bits 64-95,
  no layer 3).
- `shift_state` is unchanged (`state >> 32`).
- Template generation/application is semantically unchanged: no S
  placement template ever contains a cell at rel = 3 (max z-offset is
  2, see `docs/z_frontier_live_cells.md`), so the `rel >= LAYERS`
  rejection in `make_shifted_template` rejects nothing new and the
  template set is identical (488 templates, 3944 concrete placements).
- First-empty-cell rule, BFS behaviour and diagnostics are unchanged.
- Docstrings updated to describe the 96-bit state.

## Runs

Both runs: `solvers/s_z_frontier_packed.py --diagnostics
--max-states 1000000` (same invocation as the baseline
`docs/z_frontier_state_stats_1m.md`).

| Metric | Baseline (128-bit) | 96-bit |
|---|---|---|
| States | 1,000,000 | 1,000,000 |
| Processed | 409,873 | 409,873 |
| Duplicate states | 353 | 353 |
| Layer shifts | 2,451 | 2,451 |
| Branching states | 267,139 | 267,139 |
| Maximum out-degree | 11 | 11 |
| Elapsed | 1.226 s | 1.292 s |
| Peak RSS | 111 MB | 111 MB |

Baseline metrics match `docs/z_frontier_state_stats_1m.md` exactly
(states 1,000,000; processed 409,873; duplicates 353; shifts 2,451;
branching 267,139; max out-degree 11). Elapsed time and peak RSS are
not recorded in that document; the baseline values above are from a
fresh run of the unmodified solver.

## Timing note

The exploration is short (~1.2 s), so elapsed time is noisy. Repeated
runs: 128-bit 1.226-1.315 s; 96-bit 1.171-1.292 s. The two versions
overlap completely; there is no measurable timing difference. Peak RSS
is 111 MB in every run (dominated by the 1M-entry `seen` set, not by
the 32-bit reduction per state).

## Conclusion

The 96-bit state is semantically identical to the 128-bit state (the
fourth layer was always zero): every reported metric is unchanged, and
elapsed time and peak RSS are unchanged within noise.
# Phase 2 Benchmark Cases

Baseline benchmark set for Phase 2 (solver speedup work). The goal is a small,
fixed set of solver runs that can be re-executed before/after solver changes to
measure wall-clock improvement. All cases use the hybrid solver
(`solvers/fitpolycubes_hybrid.py`) with the same worker count.

## How to run

From the repository root, using the project venv:

```bash
.venv/bin/python solvers/fitpolycubes_hybrid.py <piece> --box <dims> --workers 4 --heartbeat
```

Output is written to `data/solutions_hybrid_<piece>_<dims>.dat` (see
`solver_output_path` in `solvers/fitpolycubes_hybrid.py`). Record wall-clock
time and the number of solutions found for each run.

## Cases

### 1. Easy: N 5x5x5 (known solution)

```bash
.venv/bin/python solvers/fitpolycubes_hybrid.py n --box 5 5 5 --workers 4 --heartbeat
```

- **Status**: prime box, 4 published solutions (Postl 1998; see `docs/pieces/N.md`).
- **Baseline**: solved in ~16 s after the "speedups" commit (`bb5911f`, 2026-05-19).
  Latest evidence: `data/SOLUTION_FOUND` (2026-08-12 11:36:14) → first solution
  written to `data/solutions_hybrid_n_5x5x5.dat` (88 KB).
- **Expected**: finds all 4 solutions quickly. Good smoke test for regressions.

### 2. Moderate: Y 2x5x10 (known solutions, larger search)

```bash
.venv/bin/python solvers/fitpolycubes_hybrid.py y --box 2 5 10 --workers 4 --heartbeat
```

- **Status**: not a catalogue prime (solver experiment box), but known solvable —
  `data/solutions_hybrid_y_2x5x10.dat` (617 KB) exists from 2026-07-09.
- **Verification**: reduce with
  `solvers/reduce_solutions.py data/solutions_hybrid_y_2x5x10.dat --reflections`
  (matches the tracked `reduce` run config).
- **Expected**: completes in minutes; solution count should match the existing
  file's count after reduction.

### 3. Difficult: S 4x8x130 (prime, no solution found yet)

```bash
.venv/bin/python solvers/fitpolycubes_hybrid.py s --box 4 8 130 --workers 4 --heartbeat
```

- **Status**: one-sided page prime ("1+ prime", added in the S audit; see
  `docs/pieces/S.md` line 31). The existing output file
  `data/solutions_hybrid_s_4x8x130.dat` is **0 bytes** (2026-08-11) — the solver
  has not found a solution yet.
- **Expected**: long-running. This is the case Phase 2 speedups should crack;
  any improvement in time-to-first-solution is the headline metric.

### Alternative heavy case: P 1x5x24 (large output)

```bash
.venv/bin/python solvers/fitpolycubes_hybrid.py p --box 1 5 24 --workers 4 --heartbeat
```

- **Status**: `data/solutions_hybrid_p_1x5x24.dat` is 54 MB (2026-07-23) —
  large solution count. Useful for stress-testing the writer path and
  solution I/O, not for quick timing comparisons.

## Notes

- Use a fixed `--workers` count (4 matches the tracked `solve` run config) so
  timings are comparable across runs.
- `--heartbeat` prints progress every 10 s; keep it on for long cases.
- Do not commit `data/solutions_hybrid_*.dat` outputs; they are solver
  artifacts (only `data/solutions_n_5by5by5.dat` and
  `data/solutions_y_5by5by5.dat` are tracked today).
# TW1-32 Hardened Solver Benchmark Harness

Fail-closed paired benchmark runner for the Fit-Polycubes campaign.
Default modes never start a solver. Real execution requires `--execute`
plus a passing host gate.

Reviewed and hardened from TW1-31 (`fad611b1…`): adds mid-campaign host
protection, `/usr/bin/time -v` peak-RSS capture, and 10 new self-tests
(33 total). TW1-31 originals preserved untouched in `../tw31/`.

## Files

| File | Purpose |
|---|---|
| `bench_runner.py` | The harness (stdlib only) |
| `test_bench_runner.py` | 23 self-tests, stubs + fakes only |
| `benchmark_manifest.json` | Pinned TW1-29 baseline/candidate config |
| `README.md` | This file |
| `tw31_report.md` / `progress.txt` | Task report |

## Quick start (safe)

```bash
python3 bench_runner.py --help
python3 bench_runner.py --manifest benchmark_manifest.json --run-dir run1 preflight
python3 bench_runner.py --manifest benchmark_manifest.json --run-dir run1 evidence
python3 bench_runner.py --manifest benchmark_manifest.json --run-dir run1 dry-run
python3 test_bench_runner.py   # 23 self-tests, no real solver
```

## Real benchmark (operator opt-in, quiet host only)

```bash
# 1. Review the manifest hashes and commands (dry-run above).
# 2. Run when the desktop is quiescent:
python3 bench_runner.py --manifest benchmark_manifest.json --run-dir run1 run --execute
# 3. Analyze:
python3 bench_runner.py --manifest benchmark_manifest.json --run-dir run1 analyze
```

`run --execute` performs preflight → evidence check → 75 s host gate →
10 sequential runs (20 s inter-pair health check before each new pair;
`/usr/bin/time -v` peak-RSS capture) → `runs.csv` + `pairs.csv` +
`analysis.json`.
Without `--execute` it exits 2 without starting anything.

## Safety properties

- Expected SHA256 hashes are pinned in the manifest; any mismatch aborts
  before a solver starts (exit 3). The manifest is never regenerated
  from files found on disk.
- Instrumented builds (gprof/ASan/UBSan/gcov/invariant markers) are
  rejected from release comparisons. `__gmon_start__` alone is NOT
  treated as instrumentation (normal glibc symbol).
- Host gate: ≥75 s `/proc/stat`-delta observation, idle >85%, 1-min
  load <4.0 throughout, no memory pressure/sustained swap. Failure
  writes `readiness.json`/`readiness.txt` and exits 4 with zero
  subprocesses launched.
- Correctness evidence is bound to exact binary hashes; a changed
  binary invalidates reuse (exit 5).
- Explicit argv arrays (no shell), separate stdout/stderr logs,
  internal vs external timings in separate CSV columns (csv module,
  schemas defined up front in `RUN_CSV_FIELDS` / `PAIR_CSV_FIELDS`).
- Journal (`journal.jsonl`, atomic appends) tracks
  PLANNED/RUNNING/COMPLETED/FAILED/INTERRUPTED/HOST_STOPPED per run ID;
  ambiguous states refuse automatic continuation; interrupted runs never
  enter statistics; missing pairs stay missing.
- Mid-campaign protection: a 20 s health check (same thresholds) runs
  before each new pair; on failure completed rows are preserved,
  `host_stop.json` records the stop reason, and no further solver is
  started. A running solver always finishes before the next check.
- Peak RSS via `/usr/bin/time -v` prefix (solver argv/binary unchanged);
  falls back gracefully when unavailable (field left empty, never
  invented). Internal, external, and RSS fields stay distinct.
- Results go to a new run directory; non-empty run dirs are refused.
  Raw logs are never overwritten.

## Exit codes

0 ok · 2 bad config/usage · 3 preflight · 4 host BLOCKED ·
5 evidence · 6 execution error.

## Schemas

Raw runs CSV: `RUN_CSV_FIELDS` in `bench_runner.py` (27 columns:
run/pair/order/impl identity, paths+hashes, argv JSON, UTC start/end,
exit status, nodes/solutions/dead ends, internal time + throughput,
external time, peak RSS, pre/post host JSON, log paths, status,
warning). Pair CSV: `PAIR_CSV_FIELDS` (9 columns incl. ratio and
reduction percent). Manifest: workload, node_cap, search_options,
expected_argv_tail, baseline/candidate (label, paths, hashes),
placement, compiler/flags, expected_counters, correctness_evidence
(binary hashes + log refs with hashes), readiness thresholds,
pair_order.

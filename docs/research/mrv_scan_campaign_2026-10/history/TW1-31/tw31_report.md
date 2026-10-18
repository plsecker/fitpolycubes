# TW1-31 — Reproducible Benchmark Harness: REPORT

**Outcome: TOOLING READY FOR REVIEW**

Date: 2026-10-17 NZDT. No solver code modified; no binaries rebuilt;
no real solver process launched; no worktrees or prior artifacts changed;
no commit/merge/deploy.

## 1. What was built (`/tmp/pentacube-bench/tw31/`)

- `bench_runner.py` (~700 lines, stdlib only): preflight (existence +
  exact SHA256 + argv match + instrumentation scan + fresh-run-dir
  guard), ≥75 s epoch-verified host gate (`/proc/stat` deltas, load,
  MemAvailable, pressure, swap deltas, competing procs), evidence
  binding (binary-hash match + evidence-log hashes), dry-run printer,
  sequential paired executor (explicit argv, separate logs, journal,
  Ctrl-C safe), CSV writers (csv module, fixed schemas), analyzer
  (ratios, reductions, medians, ranges), distinct exit codes 0/2/3/4/5/6.
- `test_bench_runner.py`: 23 self-tests, stubs + deterministic fakes.
- `benchmark_manifest.json`: pinned TW1-29 pair config (see §4).
- `README.md`: operator guide. `tw31_report.md` (this file),
  `progress.txt`.

## 2. Failures it prevents (mapped to campaign history)

- Loaded-host comparisons (TW1-20/21–26/29/30): genuine ≥75 s gate,
  BLOCKED exit 4 with zero subprocesses, per-pair load logging.
- Wrong-binary timings (TW1-20's misattributed −7.86% table): pinned
  full hashes verified before execution; evidence bound to binary hash.
- Uncertain provenance: manifest records compiler/flags, log paths and
  log hashes; preflight re-verifies every file.
- Malformed CSVs (TW1-29's shifted-column incident): schemas defined
  first, csv.DictWriter/DictReader, column-count test.
- Internal/external confusion: separate fields end to end; parser test.
- Overwritten profiling output: per-run-ID log files in a fresh run dir;
  non-empty run dirs refused.
- Benchmarking unverified binaries: evidence gate (exit 5) unless an
  explicit fresh-validation mode succeeds (not yet implemented —
  see §5).
- Wasted readiness-only tasks: one tool covers preflight → gate →
  evidence → dry-run → execute → analyze with reviewable manifest.

## 3. Self-tests proved (23/23 pass, no real solver)

Hash pass/mismatch-before-exec; missing binary/placement stop;
invalid manifest rejected; failed gate launches zero subprocesses
(marker-file proof); passing fixture advances; dry-run prints without
executing; `run` without `--execute` exits 2 with no runs.csv; stubs
strictly sequential (single-flight guard); non-zero exit captured with
stop-after-failure; interruption marked INTERRUPTED and excluded from
stats; ambiguous journal refuses restart; CSV column counts + quoting;
timing-field separation; reduction math on synthetic data (10%/−10% →
median 0%); missing pairs never fabricated; hash change invalidates
evidence; prior report cannot authorize a different binary;
instrumented binary rejected; fixtures confined to temp dirs.
Time/metric/launcher injection used throughout (no 75 s waits in tests).

Live verification (safe modes only): `--help`, `preflight` (5 files ok),
`evidence` (8 logs ok), `dry-run` (10 correct commands printed),
`run` without `--execute` → exit 2, no runs.csv. `pgrep` confirms no
solver process launched during this task.

## 4. Recovered configuration (all independently re-hashed)

- Baseline source `tw18/solver_coalesced.cpp`: `a4fdcf12…93278` ✓
- Candidate source `tw29/solver_mrv_scan.cpp`: `274c3796…bfb418` ✓
- Baseline binary `tw29/solver_baseline`: `79dff337…c95ebc47` ✓
- Candidate binary `tw29/solver_mrv_scan`: `f7f9b3f8…36715715` ✓
  (retrieved from TW1-29 report, verified against the actual file)
- W placements: `a7a421cd…` ✓ (V `dc22870d…`, KSSref `9786dd43…` also ✓)
- CLI: `<binary> W 5 7 9 <placements_W> 2500000 --connectivity
  --symmetry --region-prune=propagate` (reconciled against TW1-29 W log
  header + counters: 2500040/0/1136291, prop 564316/forced 1525974)
- Expected counters V 70033/18/34236, KSSref 10000068, W 2500040 +
  4884-line forced traces (both `67985dba…`, byte-identical) recorded
  with per-log hashes in the manifest.
- Pair order baseline,candidate / candidate,baseline ×5; gate
  idle >85%, load <4.0, 75 s; compiler g++ 13.3.0, flags
  `-Ofast -march=native -flto -std=c++17 -pthread`.

## 5. Unknowns / limitations

- Fresh-correctness mode (build + run V/KSSref/W + compare) is specified
  in the manifest structure but not implemented: the harness reuses
  pinned evidence only. A changed binary is refused, never validated.
- Between-pair idle checks are specified as short observations; the
  executor records pre/post host snapshots per run but does not yet
  auto-stop on mid-campaign degradation (operator judges from logs).
- `/usr/bin/time -v` peak-RSS capture is not wired into the default
  launcher (peak_rss parsed from stderr when present, else empty).
- No KSSref/V benchmark modes (W-only manifest); no parallel-mode guard
  beyond argv pinning.

## 6. Operator launch procedure (future quiet host)

1. `cd /tmp/pentacube-bench/tw31` and review `benchmark_manifest.json`
   hashes against TW1-29 records.
2. `python3 bench_runner.py --manifest benchmark_manifest.json --run-dir run_mrv1 preflight`
3. `... evidence` then `... dry-run`; confirm the 10 commands.
4. When the desktop is quiescent:
   `... --run-dir run_mrv1 run --execute` (gate runs first; BLOCKED
   exits 4 with no solvers started if the host is loaded).
5. `... --run-dir run_mrv1 analyze`; decide per the ≥2% hypothesis.

## 7. Artifacts and hashes

- `bench_runner.py` — see verification command below
- `test_bench_runner.py` — see below
- `benchmark_manifest.json` — see below
- `README.md` — see below
- `tw31_report.md` — see below
- `progress.txt` — see below

No MRV performance claim is made; the hypothesis remains untested.

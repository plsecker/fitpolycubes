# TW1-32 — Harness Safety Review and Hardening: REPORT

**Outcome: READY FOR CONTROLLED BENCHMARK**

Date: 2026-10-17 NZDT. No solver code modified; no solver executed;
no binaries rebuilt; TW1-31 originals preserved; no commit/merge/deploy.

## 1. Verification baseline

TW1-31 hashes confirmed before editing (all match the TW1-31 report):
`bench_runner.py fad611b1…`, `test_bench_runner.py 3c7c15fb…`,
`benchmark_manifest.json 5ec37e56…`, `README.md 9d0f0d65…`,
`tw31_report.md f7de4c46…`. Existing suite: 23/23 pass.

## 2. Safety audit (all 1009 lines read)

Enforced for real (not test-only): pinned full-SHA256 preflight with
fail-before-exec; argv-tail cross-check; instrumentation-marker scan
(with documented `__gmon_start__` exclusion); explicit `--execute`
opt-in; argv arrays, no shell; separate stdout/stderr logs; fresh-run-dir
refusal; atomic journal with ambiguous-state refusal; INTERRUPTED never
trusted for timing; incomplete pairs never fabricated; evidence bound to
exact binary hashes + evidence-log hashes; internal/external timings in
separate fields.

Gaps found and fixed: (a) dead `vals` loop in `read_pressure` (removed —
was shadowing the real regex parse); (b) thresholds duplicated between
initial gate and (missing) inter-pair logic — now single-sourced via
`gate_thresholds()`; (c) no mid-campaign protection; (d) peak RSS parsed
but never produced; (e) `execute_plan` had no host-stop path.

## 3. Changes (tw31 → tw32)

- `read_pressure`: removed dead pre-loop; single regex parse.
- `gate_thresholds(manifest)`: one source for idle/load/pressure/swap
  limits, used by both the 75 s gate and inter-pair checks.
- `inter_pair_health_check()`: 20 s documented observation (5 s
  samples), same thresholds, never touches other processes.
- `execute_plan(..., inter_pair_check=...)`: check runs before each new
  pair (never before pair 1, never concurrently — a running solver
  finishes first); on failure writes `host_stop.json`, journals
  `HOST_STOPPED`, preserves completed rows, starts no further solver.
- `timev_launcher()`: `/usr/bin/time -v` prefix for peak-RSS capture;
  solver argv/binary identity unchanged (time only prefixes); graceful
  fallback to `default_launcher` when absent (field empty, never
  invented). Wired into `cmd_run` via `use_time_v` manifest flag (true).
- Manifest: added `inter_pair_observation_s: 20`, `use_time_v: true`.
- Tests: 10 new cases (23 → 33), all stub/fake/marker based.
- README: documents new behaviour and TW1-31 provenance.

## 4. Self-tests: 33/33 pass, no real solver

New coverage: deterioration after a completed run prevents the next
launch (2 rows kept, `host_stop.json` with `before_pair: 2`);
stop reason recorded; incomplete pair stays incomplete across restart
(`HOST_STOPPED` in journal, 1 complete pair only); no stats fabricated
for incomplete pairs (0 pairs, null median); completed records survive
interruption with provenance; RSS/timing fields distinct + time-v
parse/fallback; hash mismatch still blocks; default/dry-run never
execute; `--execute` still required; inter-pair thresholds identical
to initial gate.

Live safe-mode verification against the real manifest: preflight 5/5
ok, evidence 8/8 ok, dry-run prints the 10 correct commands,
`run` without `--execute` exits 2 with no runs.csv. Process check
confirms no solver launched (one transient pgrep self-match ruled out
by PID inspection).

## 5. Remaining limitations (not blockers)

No fresh-correctness mode (changed binary refused, not validated);
no automatic mid-campaign abort of an already-running solver (by
design — it finishes, then the next launch is refused); W-only
manifest; RSS empty if `/usr/bin/time` absent.

## 6. Artifacts (`/tmp/pentacube-bench/tw32/`)

- `bench_runner.py`, `test_bench_runner.py`, `benchmark_manifest.json`,
  `README.md`, `tw31 self-test/test output/dry-run` provenance noted,
  `selftest_output.txt`, `dryrun_example.txt`
- `tw32_report.md` (this report), `progress.txt`

The MRV-scan hypothesis remains untested; no performance claim made.
Next: operator reviews the manifest and runs `run --execute` on a
quiet host.

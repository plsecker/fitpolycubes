# TW1-39 Future Workload Diagnostic — Operator README

## When to use

After the TW1-32/33 harness readiness gate PASSES on a quiet host, the
operator may optionally collect MRV workload-exposure counters BEFORE
running the five paired release benchmarks. This is diagnostic context
only — it never replaces the paired benchmark.

## How

```bash
cd /tmp/pentacube-bench/tw39
./run_workload_diagnostic.sh /tmp/pentacube-bench/tw39_workload_run1
```

The script: verifies the diagnostic source/binary/placement hashes,
refuses an existing output dir, runs the INSTRUMENTED binary once on
W 5x7x9 (2.5M cap, propagate, single-threaded), captures exit status
and the `MRV-DIAG` stderr line into the fresh output dir.

## Rules

- NEVER compare the diagnostic binary's elapsed time against release
  builds (extra packed pass + counters per MRV call).
- NEVER include diagnostic timings in `benchmark_results.csv`.
- The `MRV-DIAG` counters measure workload exposure (how often early
  exits trigger, how many columns are skipped, how many pushes are
  discarded) — not speedup.
- High `avoided_tail` + high `discarded_pushes` STRENGTHENS the ≥2%
  hypothesis (more exposure); near-zero values WEAKEN it. Either way,
  the five-pair benchmark decides.

## Counter meanings

See `counter_definitions.json` for exact per-counter definitions.

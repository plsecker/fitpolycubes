# TW1-40 — MRV-Scan Workload Diagnostic: REPORT

**Outcome: WORTH RELEASE BENCHMARK** (prioritisation only — no
performance claim; the ≥2% hypothesis still requires the paired
release benchmark)

Date: 2026-10-17 NZDT. One bounded instrumented run only. No release
benchmark, no source/binary modification, all priors preserved.

## 1. Diagnostic verification — PASS

All hashes independently verified: baseline source `a4fdcf12…93278`,
candidate source `274c3796…bfb418`, instrumented source `f337984a…`,
instrumented binary `07ab1f93…` (MRV-DIAG marker present, 18 counter
refs in source), W placements `a7a421cd…`, TW1-39 script `33366394…`
+ counter definitions read. Nothing rebuilt or modified.

## 2. Memory-safety gate — PASS (CPU idle explicitly not a criterion)

14:28:46–14:29:17 NZDT: no competing solvers; MemAvailable 3254 MB
(≥256 MB); pressure 0.00/0.00; 30 s swap deltas 5/0 (occupancy without
activity — correctly not failed). Swap ~100% occupied but inactive.

## 3. Bounded run — SUCCESS

Wrapper `run_bounded_diagnostic.sh` (dry-run refused without
`--execute`; hash preflight; fresh-dir refusal; 180 s timeout).
Single run 14:29:39–14:29:40 NZDT, exit 0, swap deltas 0/0:
W 5×7×9, cap 250000 → stopped at **250037 nodes** (cap means
stop-after-exceed, consistent with TW1-27's 2500040), 0 solutions,
114203 dead ends, prop 57917 (forced 156628). INSTRUMENTED elapsed
1.39 s is overhead-inclusive and never used for comparison.

## 4. Counters (exact TW1-39 definitions)

- MRV calls: **227239**; visited: **32890203** (mean 144.7/call)
- Zero-hit calls: **33526 (14.75%)**; no-zero calls: 193713
- Mean first-zero position: **63.6** (0-based visit index)
- Avoided tail: **2820977** active-column visits (mean 12.4/call)
- Exit histogram [v=1..6,7+]: [0,1564,1380,676,748,878,441,**27839**] —
  83% of exits skip 6+ columns; bucket-0 empty (a zero is never the
  very first active column visited)
- Discarded degree-1 pushes: **179841**; authoritative forced: 210457
- Max visits one call: 315
- Consistency: calls == zero+nozero ✓; hist sums to zero_calls ✓

## 5. Interpretation (exposure, not speedup)

Zero-degree states are common (1 in 7 MRV calls) and exits skip real
work (mean 12.4 columns, 2.8M total over 250k nodes ≈ 8.6% of visited
columns). The removed push path fires ~180k times. Both TW1-29
mechanisms have substantial workload exposure — but per-call savings
are small (a predictable branch + mostly-untaken stores), so this
supports exposure, not a runtime percentage. The ≥2% hypothesis is
neither proven nor weakened beyond "the optimisation actually engages
on real search states."

## 6. Decision

**WORTH RELEASE BENCHMARK.** Meaningful avoided visits (2.8M) and
removed insertions (180k) at 250k nodes; scale ~10× to the 2.5M-cap
benchmark workload. Preserve the candidate for the next controlled
release comparison when the host qualifies. No adoption/rejection on
operation counts.

## 7. Artifacts (`/tmp/pentacube-bench/tw40/`)

- `run_bounded_diagnostic.sh`, `diag_run1/` (stdout, stderr with
  MRV-DIAG line, run_record.txt), `diagnostic_results.json`,
  `tw40_report.md`, `progress.txt`

# TW1-29 — MRV-Scan Optimisation: REPORT

**Outcome: RETAIN AS EXPERIMENTAL (correctness passes; performance
unmeasured — host gate failed, no benchmarks run)**

Date: 2026-10-17 NZDT. Host: philip-VirtualBox, 8 logical CPUs.
No worktrees modified; TW1-15–TW1-28 artifacts preserved; no
commit/merge/deploy.

## 1. Baseline and prior evidence — verified

- TW1-28 report/progress read. TW1-27 CSV inspected: 10 data rows, all
  five pairs favour the coalesced baseline (pair reductions −31.39%,
  −22.62%, −57.63%, −36.72%, −52.52%). ActiveX timings not used as a
  baseline for anything here.
- Canonical baseline `/tmp/pentacube-bench/tw18/solver_coalesced.cpp`
  hashes to `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278`
  — matches expected. Isolated work dir `/tmp/pentacube-bench/tw29/`.

## 2. MRV audit (actual source, not report alone)

`choose_best_column` (lines 553–595), sole packed-scan caller (line 566);
`PackedActiveCols::for_each` visits set bits in strictly ascending column
order (ctz per word, words ascending) — the existing lowest-index
tie-break. `one_deg_set` is incrementally maintained by
`mrv_update_one_deg` on every degree transition and rollback.

Execution trace per propagate-enabled node:
1. `prop_forced.clear()` (line 1452).
2. Scan pushes degree-1 columns into `forced_out` (lines 572–574).
3. Lines 587–592 `clear()` those pushes, then re-collect from
   `one_deg_set` — the scan's pushes are always discarded. The
   `one_deg_set` collection is authoritative; the scan pushes have no
   side effects (plain `push_back`, no other readers — `prop_forced`
   read only at 1463/1513–1519, after the re-collection).
4. Caller checks `best_col == -1 || min_rows == 0` (line 1466) and
   returns (dead end) **before** touching `prop_forced` — so on a
   degree-0 node, `forced_out` contents are never consumed. Early exit
   cannot leave `forced_out` observably incomplete.
5. `deg_out` is always `g_deg.data()` itself and the write
   `deg_out[c] = g_deg[c]` is a self-copy no-op; partial writes from
   early exit are harmless (verified: no other `deg_out` caller passes
   a distinct buffer; colour-prune callers at 1394/1427 pass nullptr).

Both changes proven safe; no STOP condition triggered. The reported
redundancy is present in the source exactly as described.

## 3. Candidate

`/tmp/pentacube-bench/tw29/solver_mrv_scan.cpp`
SHA256: `274c3796c00658e1e4eee4b56304c86a7a470e05bd8f3aa3bef6e6be85bfb418`

Exact change (diff in `mrv_scan.diff`, 39 lines):
1. Added `PackedActiveCols::for_each_until` — ascending iteration with
   early stop when the functor returns true (mirrors `for_each` order).
2. `choose_best_column` uses `for_each_until`, returning true at the
   first degree-0 column (unbeatable minimum; ascending order keeps the
   lowest-index degree-0 column = original tie-break winner).
3. Removed the scan's degree-1 `forced_out` pushes (always discarded);
   single authoritative collection from `one_deg_set` retained unchanged.

No new data structures, heaps, buckets, propagation algorithms, or
ActiveX code. Original untouched.

Builds (same compiler/flags): `g++ -Ofast -march=native -flto
-std=c++17 -pthread`; `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0`.
- Baseline binary: `79dff337875560de88f2501a602e8aeebabc26220a61197204adf910c95ebc47`
  (reproduces the known verified hash exactly)
- Candidate binary: `f7f9b3f86d45e520b06097e0b9fcefbe08dbedf05608cc956f06d3d073476715`
- Logs: `build_baseline.log`, `build_candidate.log` (only the standard
  lto-wrapper serial-compilation note).

## 4. Correctness — PASS (all three + forced trace)

Identical CLI (`--connectivity --symmetry --region-prune=propagate`,
single-threaded), exit 0/0 throughout:

- V 5×5×6 exhaustive: 70033 nodes / 18 sol / 34236 dead / prop 14452
  (forced 42099) — full diff excl. timing IDENTICAL (matches the
  70033/18/34236 reference).
- KSSref 5×5×5 cap 10M: 10000068 nodes / 0 sol / 6335178 dead / prop
  1297394 (forced 2464552) — IDENTICAL (matches the 10000068 reference).
- W 5×7×9 cap 2.5M: 2500040 nodes / 0 sol / 1136291 dead / prop 564316
  (forced 1525974) — IDENTICAL (matches the 2500040 reference).
- `DEBUG_COMPARE=1` V 5000-cap forced trace: 4884 `D` lines IDENTICAL.

Logs: `correct_{V,KSS,W}_{baseline,candidate}.log/.err`,
`forced_{baseline,candidate}.txt`.

## 5. Host readiness — FAIL (82 s epoch-verified observation)

Window 10:44:45–10:46:07 NZDT (16 × 5 s /proc/stat deltas, 82 s):
- Idle %: 49.5, 48.2, 55.7, 48.7, 49.1, 66.2, 67.3, 58.8, 45.6, 52.1,
  51.6, 71.8, 76.3, 75.3, 71.7, 72.3 → **average 60.6%** (gate >85%: FAIL)
- 1-min load 6.14–11.63, **every sample >4.0** (gate: FAIL)
- MemAvailable ~3.3–3.6 GB; memory some-pressure avg60 0.08–0.37
  (no significant pressure); swap-in 12–47 pages per 5 s window
  (~380 total, 0 swap-out) — light but sustained swap-in traffic
- No competing solver/benchmark processes (PASS)
- Load drivers: firefox content procs (~10–12% CPU each), opencode
  sidecar 16.2%, OpenWork renderer 8.2% — heavy desktop load, materially
  worse than the TW1-27 gate window.

Per protocol: **stopped before benchmarking.** No performance runs were
performed; the ≥2% hypothesis is untested, not falsified.

## 6. Analysis / decision

**RETAIN AS EXPERIMENTAL.** Correctness passes fully (three workloads +
forced trace identical), the change is minimal and provably
semantics-preserving, but performance could not be measured under
controlled conditions — a 2% effect is unresolvable at 60% idle with
1-min load 6–11. No complexity was added that needs justifying, so this
is not a REJECT; it is an unmeasured candidate awaiting a quiet host.
No runtime heuristic added.

## 7. Artifacts (`/tmp/pentacube-bench/tw29/`)

- `tw29_report.md` — this report
- `progress.txt` — short progress record
- `benchmark_results.csv` — header only (no benchmark rows; none run)
- `solver_mrv_scan.cpp` — candidate source
- `mrv_scan.diff` — exact 39-line diff
- `solver_baseline`, `solver_mrv_scan` — release binaries
- `build_baseline.log`, `build_candidate.log`
- `correct_{V,KSS,W}_{baseline,candidate}.log/.err`
- `forced_{baseline,candidate}.txt`

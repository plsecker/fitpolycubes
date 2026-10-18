# TW1-16: Coalesced Degree-Delta KSSref Replication Report

**Date:** 2026-10-16 (NZDT)
**Experiment:** Replicate KSSref 5×5×5 performance improvement from TW1-15
**Status:** COMPLETE

---

## 1. Pre-Run Identity Verification

### 1.1 TW1-15 Report Review

Read `/tmp/pentacube-bench/coalesced-degree-delta/coalesced_degree_delta_report.md` and `progress.txt`.

**TW1-15 recorded single-run KSSref timings:**
- TW1-13 uninstrumented: 55.4671 s (internal)
- Coalesced candidate: 40.7254 s (internal)
- Reported speedup: 26.6%

**TW1-15 provenance limitations (carried forward):**
- Source-to-binary mapping: **UNVERIFIED** (no build log retained)
- Build flags: inferred as `g++ -Ofast -std=c++17 -pthread` from `progress.txt`
- KSSref benchmark: single run only, no repeated measurements

### 1.2 Independently Verified File Hashes

Computed by `sha256sum` immediately before benchmarking:

| File | SHA256 |
|---|---|
| `solver_tw13_uninstrumented` | `4e2ff001cd69e6a7bfdebde86b90d0ec1a8dc9bc7115cad6a28ba4018e6e310d` |
| `solver_coalesced` | `214b4de314f63dd5240ef178be7b4851ccd2e2b43137c29e4ea0dedf23df3180` |
| `placements_KSSref_5x5x5.txt` | `9786dd438861f4668cc4b7f8f179d2b2e844426681d17c44d7375e901b1de291` |

All match the TW1-15 report values.

### 1.3 Active Job Check

No `solver_tw13` or `solver_coalesced` processes were running at benchmark start.

### 1.4 CLI Arguments

Identical to TW1-15 correctness test:
```
./solver KSSref 5 5 5 placements_KSSref_5x5x5.txt 10000000 --connectivity --region-prune=colour --region-prune=propagate --symmetry
```

---

## 2. Benchmark Execution

Five paired repetitions, alternating order, sequential execution:

| Pair | Order | Implementation | Internal (s) | Wall (s) | Nodes | Solutions | Dead Ends | Exit |
|---|---|---|---|---|---|---|---|---|
| 1 | first | tw13 | 46.6545 | 46.70 | 10,000,070 | 0 | 6,335,406 | 0 |
| 1 | second | coalesced | 44.7976 | 44.82 | 10,000,070 | 0 | 6,335,406 | 0 |
| 2 | first | coalesced | 45.0919 | 45.11 | 10,000,070 | 0 | 6,335,406 | 0 |
| 2 | second | tw13 | 46.1335 | 46.18 | 10,000,070 | 0 | 6,335,406 | 0 |
| 3 | first | tw13 | 46.7090 | 46.73 | 10,000,070 | 0 | 6,335,406 | 0 |
| 3 | second | coalesced | 44.9005 | 44.91 | 10,000,070 | 0 | 6,335,406 | 0 |
| 4 | first | coalesced | 43.4870 | 43.50 | 10,000,070 | 0 | 6,335,406 | 0 |
| 4 | second | tw13 | 47.0476 | 47.07 | 10,000,070 | 0 | 6,335,406 | 0 |
| 5 | first | tw13 | 45.8255 | 45.84 | 10,000,070 | 0 | 6,335,406 | 0 |
| 5 | second | coalesced | 45.4808 | 45.50 | 10,000,070 | 0 | 6,335,406 | 0 |

**Counter verification:** All 10 runs produced identical deterministic counters (nodes, solutions, dead ends). No discrepancies.

**Log paths:** `/tmp/pentacube-bench/coalesced-degree-delta/tw16/KSS_bench_p{1-5}_{tw13,coalesced}.log`

---

## 3. Analysis

### 3.1 Paired Runtime Ratios (Internal Time)

| Pair | TW1-13 (s) | Coalesced (s) | Ratio (C/T) | Reduction (%) |
|---|---|---|---|---|
| 1 | 46.6545 | 44.7976 | 0.9602 | 3.98 |
| 2 | 46.1335 | 45.0919 | 0.9774 | 2.26 |
| 3 | 46.7090 | 44.9005 | 0.9613 | 3.87 |
| 4 | 47.0476 | 43.4870 | 0.9243 | 7.57 |
| 5 | 45.8255 | 45.4808 | 0.9925 | 0.75 |

### 3.2 Aggregate Statistics (Internal Time)

| Statistic | TW1-13 | Coalesced |
|---|---|---|
| Median | 46.6545 s | 44.9005 s |
| Mean | 46.4740 s | 44.7516 s |
| Std Dev | 0.4882 s | 0.7535 s |
| Min | 45.8255 s | 43.4870 s |
| Max | 47.0476 s | 45.4808 s |

### 3.3 Paired Summary

| Metric | Value |
|---|---|
| Median paired ratio (coalesced/tw13) | 0.9613 |
| **Median paired reduction** | **3.87%** |
| Mean paired reduction | 3.69% |
| All pairs show improvement? | Yes (5/5) |
| Smallest improvement | 0.75% (Pair 5) |
| Largest improvement | 7.57% (Pair 4) |

### 3.4 External Wall-Clock Comparison

| Statistic | TW1-13 | Coalesced |
|---|---|---|
| Median | 46.70 s | 44.91 s |
| Mean | 46.50 s | 44.77 s |

Median wall-clock reduction: **3.89%**

### 3.5 Comparison with TW1-15 Single Run

| Source | TW1-13 | Coalesced | Reduction |
|---|---|---|---|
| TW1-15 (single run) | 55.47 s | 40.73 s | 26.6% |
| TW1-16 (median, 5 pairs) | 46.65 s | 44.90 s | 3.87% |

The TW1-15 single-run result (26.6% faster) **does not reproduce** at that magnitude. The TW1-15 run was taken under high system load (load average 3.14 → 9.11), which likely penalized the TW1-13 run disproportionately. The TW1-16 replication under more stable conditions shows a consistent but modest 3.9% improvement.

### 3.6 Environmental Notes

- All runs completed at ~99% CPU utilization (single-threaded).
- Minor page faults were consistent across runs (264–280 minor, 0 major after warmup).
- Context switches varied (167–985 involuntary), suggesting some OS scheduling noise.
- No obvious environmental interference detected.

---

## 4. Verdict

### RETAIN AS EXPERIMENTAL

**Evidence Summary:**

| Criterion | Result |
|---|---|
| Correctness (all 10 runs) | PASS — identical counters |
| Binary identity verified | PASS — SHA256 matches TW1-15 |
| Placement identity verified | PASS — SHA256 confirmed |
| Paired improvement (5/5) | PASS — all pairs show coalesced faster |
| Median reduction | 3.87% (internal), 3.89% (wall) |
| TW1-15 magnitude reproduced | NO — 26.6% → 3.9% |

**Rationale:**

The coalesced degree-delta optimization consistently outperforms TW1-13 on the KSSref 5×5×5 workload, but the improvement is **modest (3.9%)** rather than the dramatic 26.6% observed in the single TW1-15 run. The TW1-15 result was likely inflated by environmental noise (high system load during the TW1-13 run).

The optimization is correct, safe, and delivers a small but consistent benefit on this workload. It remains an experimental candidate — the improvement is real but not large enough to justify unconditional adoption without further validation on additional workloads.

---

## 5. Limitations

1. **Source-to-binary provenance: UNVERIFIED.** No build log retained. Binary hashes match TW1-15 report, but compilation provenance is not independently verified.
2. **Build flags: inferred** as `g++ -Ofast -std=c++17 -pthread` from TW1-15 `progress.txt`.
3. **Only 5 repetitions.** Small sample size; no statistical significance testing performed.
4. **Single workload.** Only KSSref 5×5×5 tested. Results may not generalize.
5. **Load averages not systematically recorded.** Environmental conditions were not fully instrumented.
6. **No parallel/threaded benchmark.** All tests single-threaded.

---

## 6. Artifact Paths

| Artifact | Path |
|---|---|
| Report | `/tmp/pentacube-bench/coalesced-degree-delta/tw16/tw16_report.md` |
| Benchmark CSV | `/tmp/pentacube-bench/coalesced-degree-delta/tw16/benchmark_results.csv` |
| Progress | `/tmp/pentacube-bench/coalesced-degree-delta/tw16/progress.txt` |
| Raw Logs | `/tmp/pentacube-bench/coalesced-degree-delta/tw16/KSS_bench_p*.log` |
| TW1-15 Report | `/tmp/pentacube-bench/coalesced-degree-delta/coalesced_degree_delta_report.md` (unchanged) |
| TW1-15 Progress | `/tmp/pentacube-bench/coalesced-degree-delta/progress.txt` (unchanged) |
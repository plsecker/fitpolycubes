# Coalesced Degree-Delta: Final Provenance Audit & Report

**Date:** 2026-10-16 (NZDT)  
**Experiment:** TW1-15 — Coalesced Degree-Delta Optimization  
**Status:** COMPLETE

---

## 1. Source & Binary Identity

### Source Files
| Implementation | File | SHA256 |
|---|---|---|
| TW1-13 (Uninstrumented) | `solver_tw13_uninstrumented.cpp` | `9289644a9c968182f14c734fa96ac83a4612ffd93bc822cacea376e24130443c` |
| Coalesced Candidate | `solver_coalesced.cpp` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` |
| Reference (std::set) | `solver_reference.cpp` | `65e9e2c42c7b58a2ba7cd6501132e9ef300bbabcdc93fe4d1aadbe4512f6738e` |

### Release Binaries
| Implementation | Binary | SHA256 |
|---|---|---|
| TW1-13 | `solver_tw13_uninstrumented` | `4e2ff001cd69e6a7bfdebde86b90d0ec1a8dc9bc7115cad6a28ba4018e6e310d` |
| Coalesced | `solver_coalesced` | `214b4de314f63dd5240ef178be7b4851ccd2e2b43137c29e4ea0dedf23df3180` |
| Reference | `solver_reference` | `61647ab64deb5be29e9e44336fe9c9e800bce2891f19e8151b1e8367b90035a8` |

### Patch Verification
- **Patch File:** `coalesced_degree_delta.patch`
- **Verification Command:** `patch --dry-run -R -p0 < coalesced_degree_delta.patch` (target: `solver_coalesced.cpp`)
- **Exit Status:** `0` (PASS)
- **Result:** The patch reverses cleanly. The candidate source is a direct, single-diff derivative of the uninstrumented TW1-13 source.

### Source Content Audit
- The diff introduces exactly four structural changes:
  1. `DegreeDeltaScratch` struct + `thread_local g_degree_delta_scratch`
  2. `g_degree_delta_scratch.init(num_cols)` in `compute_degrees()`
  3. `apply_row_removals_coalesced()` function
  4. Call-site swap in `gen_tasks_rec()` (loop → coalesced call)
- No new profiling counters, debug prints, or instrumentation macros were added. Pre-existing guarded debug code (`DEBUG_COMPARE`, `SYM_DEBUG`, `PROP_DEBUG`) matches the uninstrumented baseline.
- **Conclusion:** The candidate contains only the intended coalescing logic. No unintended debug/profiling instrumentation detected.

---

## 2. Release-Binary Provenance

| Property | Status |
|---|---|
| Compiler | `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` (confirmed via binary `.comment` section) |
| Intended Flags | `g++ -Ofast -std=c++17 -pthread` (recorded in `progress.txt`) |
| Build Log Retained | **NO** |
| Source-to-Binary Mapping | **UNVERIFIED** |

**Provenance Note:** Binary SHA256s match the self-reported hashes in the precise benchmark logs (runs 11–15), and the patch reverse-dry-run confirms the source relationship. However, no build log, Makefile, or compilation transcript is retained. The exact flags and compilation environment cannot be independently verified. **Source-to-binary provenance is marked UNVERIFIED.**

---

## 3. Semantic Audit of Coalesced Logic

### `apply_row_removals_coalesced()` vs. Original Loop
- **Original:** Iterates `deactivated_rows`, calling `apply_row_removal()` per row. Each call updates `g_deg` and `one_deg_set` immediately. Intermediate degree/set states are technically observable between iterations.
- **Coalesced:** Accumulates all decrements in `DegreeDeltaScratch` (epoch-stamped, O(1) per column). After accumulation, iterates `touched_cols`, computes net `new_deg`, pushes a single `(col, -decrement)` trail entry, updates `g_deg`, and calls `mrv_update_one_deg(col, old_deg, new_deg, true)`.

### Intermediate State Observation
- **No intermediate degree/set states are observable** before the coalesced transaction commits. The scratch array is isolated; `g_deg` and `one_deg_set` are untouched until the commit phase.
- `mrv_update_one_deg()` handles net transitions correctly:
  - `2 → 0`: No set change (correct: never in set, ends out)
  - `3 → 1`: Inserts (correct: crosses threshold into degree-1)
  - `1 → 0`: Erases (correct: leaves degree-1)
  - `2 → 1`: Inserts (correct)
- **Conclusion:** The coalesced transaction produces the same final `g_deg` and `one_deg_set` state as the sequential loop, with no observable intermediate states. Semantically equivalent for search correctness.

---

## 4. Coalescing Instrumentation Results

### V Workload (`V_profile_v2.log`)
| Metric | Value |
|---|---|
| Row-removal transactions | 366,906 |
| Total decrement events | 29,785,099 |
| Unique affected columns | 10,344,644 |
| Avoided repeated updates | 19,440,455 |
| **Avoided-update ratio** | **65.27%** |
| Degree-trail pushes (coalesced) | 10,344,644 |
| Row-removal `one_deg_set` inserts | 597,094 |
| Row-removal `one_deg_set` erases | 220,950 |
| Max decrements/transaction | 396 |
| Max touched columns/transaction | 85 |
| Histogram overflow | 0 |

### KSSref Workload (`KSS_profile_v2.log`)
| Metric | Value |
|---|---|
| Row-removal transactions | 10,000,069 |
| Total decrement events | 1,593,796,088 |
| Unique affected columns | 204,271,191 |
| Avoided repeated updates | 1,389,524,897 |
| **Avoided-update ratio** | **87.18%** |
| Degree-trail pushes (coalesced) | 204,271,191 |
| Row-removal `one_deg_set` inserts | 17,210,204 |
| Row-removal `one_deg_set` erases | 10,396,254 |
| Max decrements/transaction | 1,911 |
| Max touched columns/transaction | 111 |
| Histogram overflow | 0 |

**Scratch Array Cost:** `seen_epoch` (uint32), `pending_delta` (int), `touched_cols` (dynamic). ~3.6 KB/thread for V, ~3.0 KB/thread for KSSref. Epoch mechanism avoids O(num_cols) clears; only `touched_cols` is cleared per transaction.

---

## 5. Correctness Results

| Test | Implementation | Nodes | Solutions | Dead Ends | Exit |
|---|---|---|---|---|---|
| V Exhaustive | reference | 366,907 | 144 | 131,833 | 0 |
| V Exhaustive | tw13 | 366,907 | 144 | 131,833 | 0 |
| V Exhaustive | coalesced | 366,907 | 144 | 131,833 | 0 |
| KSSref 10M Cap | reference | 10,000,070 | 0 | 6,335,406 | 0 |
| KSSref 10M Cap | tw13 | 10,000,070 | 0 | 6,335,406 | 0 |
| KSSref 10M Cap | coalesced | 10,000,070 | 0 | 6,335,406 | 0 |

- **Forced Placement Comparison (KSS 1000-cap):** `DEBUG_COMPARE` + `DEBUG_FORCED_CONTENT` logs show byte-identical `D`/`FC` sequences for tw13 and coalesced.
- **ASAN + DEG_TRAIL_DEBUG:** V (366,906 checks), KSS 1000-cap (1,056 checks). Zero failures.
- **Conclusion:** PASS. All implementations produce identical deterministic counters and search trees.

---

## 6. V Benchmark Results (5 Paired Repetitions)

**Setup:** V 5×5×6, exhaustive, 696 placements, identical search settings, alternating execution order.

| Run | reference (s) | tw13 (s) | coalesced (s) |
|---|---|---|---|
| 1 | 1.621520 | 1.484440 | 0.939072 |
| 2 | 0.935747 | 0.739685 | 0.828838 |
| 3 | 0.908937 | 0.802899 | 0.755540 |
| 4 | 0.848419 | 0.731382 | 0.782398 |
| 5 | 0.941532 | 0.763150 | 0.744224 |

**Summary (Solver-Internal Time):**
| Statistic | reference | tw13 | coalesced |
|---|---|---|---|
| Median | 0.908937 | 0.763150 | 0.782398 |
| Mean | 0.931151 | 0.784311 | 0.810014 |
| Std Dev | 0.2798 | 0.2129 | 0.0731 |

**Paired Ratios (coalesced / tw13):**
- Run 1: 0.632
- Run 2: 1.121
- Run 3: 0.941
- Run 4: 1.070
- Run 5: 0.975
- **Median Ratio:** 0.975 (coalesced is 2.5% slower than tw13 at median)
- **Mean Ratio:** 0.988

**Interpretation:** On the V workload, coalescing provides no measurable performance gain. The scratch array overhead and epoch management roughly cancel the benefit of avoiding 65% of repeated updates. Variance is lower for coalesced (std dev 0.073 vs 0.213 for tw13), indicating more consistent performance.

---

## 7. KSSref Performance (Single Run, 10M Cap)

| Implementation | Internal Time (s) | NPS |
|---|---|---|
| tw13 | 55.4671 | 180,288 |
| coalesced | 40.7254 | 245,549 |

**Speedup:** `1 - (40.7254 / 55.4671) = 26.6%` faster for coalesced.

**Note:** This is a single-run comparison. System load varied (3.14 → 9.11). No repeated KSS benchmark exists. The result is promising but not statistically validated.

---

## 8. Explicit Limitations

1. **Source-to-Binary Provenance: UNVERIFIED.** No build log retained. Hashes are self-reported in benchmark logs. Patch verification confirms source relationship, not compilation.
2. **Build Flags:** Inferred from `progress.txt` as `g++ -Ofast -std=c++17 -pthread`. Not independently confirmed.
3. **KSS Benchmark:** Single run only. No repeated measurements, confidence intervals, or statistical testing.
4. **Environmental Noise:** Load averages ranged from 1.21 to 9.11 during V benchmark. Run 1 shows cold-cache effects (~1.6s reference).
5. **Reference Confounding:** `solver_reference` uses `std::set<int>` for `one_deg_set`. Comparisons against it conflate data-structure differences with coalescing effects.
6. **No Parallel/Threaded Benchmark:** All tests single-threaded.

---

## 9. Verdict

### RETAIN AS EXPERIMENTAL

**Evidence Summary:**
- ✅ Correctness: PASS (V exhaustive, KSS 10M cap, forced-placement identity, ASAN + trail debug)
- ✅ Patch Verification: PASS (clean reverse dry-run, no unintended instrumentation)
- ⚠️ V Benchmark: NEUTRAL (coalesced is 2.5% slower at median; lower variance)
- ⚠️ KSS Benchmark: +26.6% faster (single run, unvalidated)
- ⚠️ Provenance: UNVERIFIED (no build log)

**Rationale:** The coalesced degree-delta optimization is correct, safe, and provably equivalent in final state. On small workloads (V), overhead cancels gains. On larger, denser workloads (KSSref), it delivers meaningful speedup by eliminating 87% of redundant degree updates. The optimization is not a universal win but shows workload-dependent value. It should be retained as an experimental option, potentially gated by runtime heuristics (e.g., average deactivated rows per transaction, placement density, or column count). Not ready for unconditional adoption.

---

## 10. Artifact Paths

| Artifact | Path |
|---|---|
| Final Report | `/tmp/pentacube-bench/coalesced-degree-delta/coalesced_degree_delta_report.md` |
| V Benchmark Audit CSV | `/tmp/pentacube-bench/coalesced-degree-delta/V_benchmark_audit.csv` |
| Patch | `/tmp/pentacube-bench/coalesced-degree-delta/coalesced_degree_delta.patch` |
| Progress Log | `/tmp/pentacube-bench/coalesced-degree-delta/progress.txt` |
| Source Files | `/tmp/pentacube-bench/coalesced-degree-delta/solver_*.cpp` |
| Release Binaries | `/tmp/pentacube-bench/coalesced-degree-delta/solver_{tw13_uninstrumented,coalesced,reference}` |
| Benchmark Logs | `/tmp/pentacube-bench/coalesced-degree-delta/V_bench_r*.log`, `V_precise_r*.log` |
| Correctness Logs | `/tmp/pentacube-bench/coalesced-degree-delta/correctness_*.log` |
| Profile Logs | `/tmp/pentacube-bench/coalesced-degree-delta/*_profile*.log` |
| Sanitizer Logs | `/tmp/pentacube-bench/coalesced-degree-delta/sanitizer_*.log` |
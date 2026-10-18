# TW1-17: Source-Matched Profiling and Next Optimisation Selection

**Date:** 2026-10-16 (NZDT)
**Status:** COMPLETE

---

## 1. Provenance Audit — Existing Profiles

### 1.1 degree-hotpath-profile

| Property | Value |
|---|---|
| Source | `/tmp/pentacube-bench/degree-hotpath-profile/solver_linear_mrv.cpp` |
| Binary | `solver_linear_mrv_degprofile` (SHA256: `0756036f...`) |
| Workloads | V 5×5×6 (exhaustive), W 5×7×9 (2.5M cap) |
| Method | Custom event counters (thread-local uint64_t) |
| **Classification** | **APPLICABLE to TW1-13** — event counts valid |

Source is TW1-13 with degree maintenance instrumentation added. Event counts (273M degree changes on W, 79.7M apply_row_removal calls, 16.3M one_deg_set removes) are reliable. No CPU cycle attribution.

### 1.2 post-packed-one-deg-profile

| Property | Value |
|---|---|
| Source | `/tmp/pentacube-bench/post-packed-one-deg-profile/solver_candidate_a.cpp` |
| Binary | `solver_candidate_a_instrumented` |
| Workloads | V 5×5×6, W 5×7×9 (2.5M cap) |
| Method | Custom event counters |
| **Classification** | **APPLICABLE to TW1-13** — event counts valid |

Source is TW1-13 (PackedOneDegSet) with instrumentation. Event counts (661M column inspections on W, 292/call, 44.9% active fraction) are reliable. No CPU cycle attribution.

### 1.3 mrv-selection-profile

| Property | Value |
|---|---|
| Source | `/tmp/pentacube-bench/mrv-selection-profile/solver_linear_mrv.cpp` (SHA256: `2e5a19cf...`) |
| Binary | `solver_linear_mrv_profile` (SHA256: `d6faf8a8...`) |
| Workloads | P 1×4×5, V 5×5×6, W 5×7×9 (2.5M cap) |
| Method | Custom event counters + histogram |
| **Classification** | **APPLICABLE to TW1-13** — event counts valid |

Source is TW1-13 with MRV scan instrumentation. Event counts (661M column inspections on W, 292 avg inspections/call, 44.9% active fraction) are reliable. No CPU cycle attribution.

### 1.4 mrv-validation (heap-based MRV)

| Property | Value |
|---|---|
| Source | `/tmp/pentacube-bench/mrv-validation/solver_current.cpp` (SHA256: `384adc60...`) |
| Binary | `solver_current_gprof` (SHA256: `71c716ee...`) |
| Workload | W 5×7×9 (2.5M cap) |
| Method | gprof (-pg) |
| **Classification** | **REJECTED / UNRELATED** — heap-based MRV, not linear-MRV |

This profile measured the rejected heap-based MRV experiment. Its findings (heap maintenance dominating at 72.8%) do not apply to the current linear-MRV implementation.

### 1.5 Summary

Existing profiles provide reliable **event counts** but no **CPU cycle attribution** for the current TW1-13 or coalesced implementations. Fresh profiling is required.

---

## 2. TW1-16 Replication Validation

### 2.1 Artifact Verification

| Artifact | Path | SHA256 |
|---|---|---|
| Report | `/tmp/pentacube-bench/coalesced-degree-delta/tw16/tw16_report.md` | `d753d1f0...` |
| CSV | `/tmp/pentacube-bench/coalesced-degree-delta/tw16/benchmark_results.csv` | `b2c576da...` |

### 2.2 CSV vs. Log Validation

All 10 rows in the CSV validated against raw log files:
- All internal times match exactly (within 0.001s)
- All wall times match exactly (within 0.01s)
- All node counts, solutions, and dead ends match exactly
- All 10 log files exist and are readable

### 2.3 Paired Ratios (Verified)

| Pair | TW1-13 (s) | Coalesced (s) | Ratio | Reduction |
|---|---|---|---|---|
| 1 | 46.6545 | 44.7976 | 0.9602 | 3.98% |
| 2 | 46.1335 | 45.0919 | 0.9774 | 2.26% |
| 3 | 46.7090 | 44.9005 | 0.9613 | 3.87% |
| 4 | 47.0476 | 43.4870 | 0.9243 | 7.57% |
| 5 | 45.8255 | 45.4808 | 0.9925 | 0.75% |

**Median reduction: 3.87%** (internal time)
**Mean reduction: 3.69%** (internal time)

All 5 pairs show coalesced faster. No discrepancies found.

---

## 3. Fresh Profiling — TW1-13 and Coalesced on W 5×7×9

### 3.1 Build Environment

| Property | Value |
|---|---|
| Compiler | `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| Build flags | `-pg -O2 -std=c++17 -pthread` |
| Build directory | `/tmp/pentacube-bench/tw17/` |
| perf availability | **BLOCKED** — `perf_event_paranoid=4` |
| Profiling method | gprof (-pg instrumentation) |

### 3.2 Source and Binary Identity

| File | SHA256 |
|---|---|
| `solver_tw13.cpp` (copy of TW1-13) | `9289644a9c968182f14c734fa96ac83a4612ffd93bc822cacea376e24130443c` |
| `solver_coalesced.cpp` (copy of coalesced) | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` |
| `solver_tw13_profile` | `010eb00af2e7d4c8609fb221a3389a690dd6f1ff74b913c17c7aaeace7a4a2dc` |
| `solver_coalesced_profile` | `7bba61575d899ea18debbdda5c67940f8a0d86e40ce47b0a2a3379507513db47` |

Source hashes match the originals exactly.

### 3.3 Workload and Arguments

```
./solver W 5 7 9 placements_W_5x7x9.txt 2500000 --connectivity --region-prune=colour --region-prune=propagate --symmetry
```

Placement file SHA256: `a7a421cde69049fcfa7fd7ee8aa71a82a4ad4c7bfc9631c04ab035d663f8b045`

### 3.4 Run Results

| Implementation | Internal (s) | Wall (s) | Nodes | Solutions | Dead Ends | Exit |
|---|---|---|---|---|---|---|
| TW1-13 | 23.1522 | 23.20 | 2,500,040 | 0 | 1,136,291 | 0 |
| Coalesced | 18.7369 | 18.79 | 2,500,040 | 0 | 1,136,291 | 0 |

**Counter verification:** Identical nodes, solutions, dead ends, connectivity checks (4,766,031), propagation rejections (564,316), and rejection depth histograms.

**Coalesced speedup on W:** 19.1% faster (18.74s vs 23.15s).

### 3.5 gprof Flat Profile — TW1-13 (gmon_tw13.out)

| % Time | Self (s) | Calls | Function |
|---|---|---|---|
| 60.1% | 8.15 | 4.82M | `frame_dummy` (gprof instrumentation) |
| 12.6% | 1.71 | — | `search` (recursive) |
| 10.6% | 1.43 | 957K | `Propagator::run` |
| 7.7% | 1.04 | 79.7M | `apply_row_removal` |
| 3.2% | 0.44 | 2.27M | `choose_best_column` |
| 2.9% | 0.39 | 572M | `mrv_update_one_deg` |
| 1.4% | 0.19 | 11.2M | `vector::emplace_back` |
| 1.3% | 0.17 | 2.50M | `rollback_deg_changes` |

### 3.6 gprof Flat Profile — Coalesced (gmon_coalesced.out)

| % Time | Self (s) | Calls | Function |
|---|---|---|---|
| 54.1% | 8.26 | 4.82M | `frame_dummy` (gprof instrumentation) |
| 30.2% | 4.61 | — | `search` (recursive) |
| 10.8% | 1.65 | 957K | `Propagator::run` |
| 3.7% | 0.56 | 2.27M | `choose_best_column` |
| 0.8% | 0.12 | 193M | `mrv_update_one_deg` |
| 0.3% | 0.04 | 2.50M | `rollback_deg_changes` |

### 3.7 Profile Interpretation

**gprof limitations:** The `-pg` instrumentation adds ~54-60% overhead (frame_dummy). The remaining ~40-46% reflects real work but with distorted attribution due to instrumentation in frequently-called small functions.

**Profile discrepancy resolved:** The initial gprof run read the wrong gmon.out file (from the coalesced run). The fresh profiles with separate gmon.out files show:
- `choose_best_column`: 0.44s (TW1-13) vs 0.56s (coalesced) — similar, not the 0.02s vs 0.52s discrepancy
- `Propagator::run`: 1.43s (TW1-13) vs 1.65s (coalesced) — similar, appears in both profiles because both implementations have the Propagator
- `apply_row_removal`: 1.04s (TW1-13) vs ~0s (coalesced) — eliminated by coalescing (replaced by `apply_row_removals_coalesced`)
- `mrv_update_one_deg`: 0.39s (TW1-13) vs 0.12s (coalesced) — reduced by coalescing (193M calls vs 572M calls)

**The dominant measured costs in the current linear-MRV implementation:**
- Propagator::run: ~1.5s (10.6-10.8% of profiled time), 957K calls
- choose_best_column: ~0.5s (3.2-3.7% of profiled time), 2.27M calls
- apply_row_removal: 1.04s (TW1-13 only), 79.7M calls — eliminated by coalescing
- mrv_update_one_deg: 0.39s (TW1-13) / 0.12s (coalesced), 572M / 193M calls

---

## 4. Next Optimisation Selection

### 4.1 Eliminated Candidates

The following are excluded per task constraints or prior experiments:
- Incremental MRV / packed active-column enumeration — already implemented (TW1-7/TW1-8)
- Bucket MRV — excluded by task constraints
- Packed one_deg_set — already implemented (TW1-7)
- Heap-based MRV — rejected (TW1-11, 5.86× slower on V)
- Inlining `mrv_update_one_deg()` — not distinct enough from degree-delta coalescing
- Trail-SoA — excluded by task constraints
- Degree-delta coalescing — already implemented (TW1-15/TW1-16)
- Empty-forced-list propagation guard — already exists in source

### 4.2 Proposed Optimisation: Propagator Row-Overlap Precomputation

**Measured bottleneck:** `Propagator::run` is the second-largest hotspot at ~1.5s (10.6-10.8% of profiled time) with 957K calls. The inner loop performs a triple-nested CSR traversal: for each forced cell, find the unique surviving row, kill overlapping rows, and decrement degrees of uncovered cells.

**Current behaviour:**
```cpp
// For each cell in killed row r:
for (int j = Y.indptr[r]; j < Y.indptr[r + 1]; ++j) {
    const int e = Y.data[j];
    covered[e] = g;
    // For each row covering cell e:
    for (int k2 = X.indptr[e]; k2 < X.indptr[e + 1]; ++k2) {
        const int r2 = X.data[k2];
        if (r2 == r || kill[r2] == g || !active_rows[r2]) continue;
        kill[r2] = g;
        // For each cell in killed row r2:
        for (int jj = Y.indptr[r2]; jj < Y.indptr[r2 + 1]; ++jj) {
            const int u = Y.data[jj];
            if (covered[u] == g) continue;
            if (--deg[u] == 0) return true;  // starved
            if (deg[u] == 1) q[tail++] = u;
        }
    }
}
```

This triple-nested loop involves random memory accesses to `X.data`, `Y.data`, `active_rows`, `kill`, `covered`, and `deg`. The CSR traversal pattern is cache-unfriendly.

**Proposed change:** Pre-compute a **row overlap graph** at initialization time. For each pair of rows that share at least one cell, store the overlap in an adjacency list. The Propagator's inner loop would then traverse the overlap graph directly, replacing the triple-nested CSR traversal with a simpler graph traversal.

**Why this should reduce cost:**
- Eliminates the triple-nested CSR traversal in the Propagator's inner loop
- Replaces random memory accesses to `X.data` and `Y.data` with sequential adjacency list traversal
- Improves cache locality by pre-computing the overlap graph
- Reduces the number of memory accesses per killed row

**Correctness invariants:**
- The overlap graph must be complete: every pair of overlapping rows must be connected
- The Propagator must still check `active_rows` and `kill` arrays to avoid processing inactive or already-killed rows
- The degree decrements must still be applied correctly

**Risks:**
- Pre-computation time and memory overhead for the overlap graph
- The overlap graph may be large for dense problems (up to O(R²) edges for R rows)
- The graph traversal must still check `active_rows` and `kill` arrays

**Falsifiable hypothesis:** The pre-computed overlap graph reduces W 5×7×9 (2.5M cap) internal runtime by ≥5% compared to TW1-13, without changing deterministic counters.

**Correctness tests:**
1. V 5×5×6 exhaustive: identical nodes/solutions/dead-ends
2. KSSref 5×5×5 (10M cap): identical counters
3. `DEBUG_DEG=1` validation passes
4. `DEBUG_COMPARE` forced-placement sequences match TW1-13

**Benchmark protocol:**
1. 5 paired repetitions on W 5×7×9 (2.5M cap), alternating order
2. 5 paired repetitions on V 5×5×6 (exhaustive)
3. Same placement files, same search settings, same binaries except the candidate

---

## 5. Limitations

1. **Source-to-binary provenance: UNVERIFIED.** No build log for release binaries.
2. **gprof limitations:** `-pg` instrumentation adds ~54-60% overhead. Attribution of small functions is unreliable. Event-count profiles provide complementary data but no cycle attribution.
3. **perf unavailable:** `perf_event_paranoid=4` blocks hardware sampling. No cycle-accurate profiling possible.
4. **Single workload profiled:** Only W 5×7×9 (2.5M cap) profiled. V and KSSref not profiled with gprof.
5. **No parallel profiling:** Only single-threaded execution profiled.

---

## 6. Artifact Paths

| Artifact | Path |
|---|---|
| Report | `/tmp/pentacube-bench/tw17/tw17_report.md` |
| Progress | `/tmp/pentacube-bench/tw17/progress.txt` |
| TW1-13 profiling source | `/tmp/pentacube-bench/tw17/solver_tw13.cpp` |
| Coalesced profiling source | `/tmp/pentacube-bench/tw17/solver_coalesced.cpp` |
| TW1-13 profiling binary | `/tmp/pentacube-bench/tw17/solver_tw13_profile` |
| Coalesced profiling binary | `/tmp/pentacube-bench/tw17/solver_coalesced_profile` |
| TW1-13 profile log | `/tmp/pentacube-bench/tw17/tw13_w5x7x9_profile2.log` |
| Coalesced profile log | `/tmp/pentacube-bench/tw17/coalesced_w5x7x9_profile2.log` |
| TW1-13 gmon.out | `/tmp/pentacube-bench/tw17/gmon_tw13.out` |
| Coalesced gmon.out | `/tmp/pentacube-bench/tw17/gmon_coalesced.out` |

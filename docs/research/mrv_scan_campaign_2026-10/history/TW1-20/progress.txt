# TW1-20: Dynamic Active-Row Index for Propagation — REJECTED

**Date:** 2026-10-16 (NZDT)
**Status:** COMPLETE — REJECTED

---

## 1. Baseline Verification

| Item | Path | SHA256 |
|---|---|---|
| Coalesced source | `/tmp/pentacube-bench/tw18/solver_coalesced.cpp` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` |
| Copy in TW1-20 | `/tmp/pentacube-bench/tw20/solver_coalesced.cpp` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` |

Hash matches. Source identity confirmed.

### 1.1 Build

| Property | Value |
|---|---|
| Compiler | `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| Build command | `g++ -Ofast -march=native -flto -std=c++17 -pthread solver_coalesced.cpp -o solver_baseline` |
| Build output | `lto-wrapper: warning: using serial compilation of 2 LTRANS jobs` |
| Baseline binary | `solver_baseline` (SHA256: `79dff337875560de88f2501a602e8aeebabc26220a61197204adf910c95ebc47`) |

---

## 2. Row-and-Cell Representation Audit

### 2.1 CSR Structures

**X CSR (cell → rows):** `X.indptr[c]..X.indptr[c+1]` lists all placement rows covering cell `c`. Built by `build_x_csr()` — iterates all placements, for each cell in the placement appends the row index. Rows are stored in placement-order (row 0 first, then row 1, etc.).

**Y CSR (row → cells):** `Y.indptr[r]..Y.indptr[r+1]` lists the 5 cells of placement row `r`. Fixed size: exactly 5 entries per row.

### 2.2 Propagator Traversal

The Propagator's conflict scan (lines 819–838) uses the X CSR:
```cpp
for (int j = Y.indptr[r]; j < Y.indptr[r + 1]; ++j) {  // cells in placed row
    const int e = Y.data[j];
    covered[e] = g;
    for (int k2 = X.indptr[e]; k2 < X.indptr[e + 1]; ++k2) {  // rows covering cell e
        const int r2 = X.data[k2];
        if (r2 == r || kill[r2] == g || !active_rows[r2]) continue;
        kill[r2] = g;
        // ... decrement degrees of cells in r2
    }
}
```

**Ordering:** Rows are visited in the order they appear in `X.data`, which is placement-order (row 0, 1, 2, ...). This is deterministic.

**Duplicate handling:** The `kill[r2] == g` check prevents processing the same row twice within one Propagator run. A row may appear in `X.data` for multiple cells of the placed row — the kill stamp catches duplicates.

### 2.3 active_rows Changes

**During placement (lines 1586–1593):** For each column `c` covered by the placed row, scan `X.data` for all rows covering `c`. If `active_rows[other]` is true, set it to 0 and record in `deactivated_rows`.

**During rollback (lines 1661–1663):** Restore `active_rows[q] = 1` for each row in `deactivated_rows`.

**During propagation:** The Propagator reads `active_rows` but does NOT modify it. It uses the `kill` stamp array to track rows killed during the current run.

**Key observation:** `active_rows` is modified by the search loop (placement/rollback), not by the Propagator. The Propagator only reads it.

### 2.4 Code Paths That Must Maintain a New Index

Any dynamic active-row index must be updated:
1. **Placement** (line 1586–1593): When rows are deactivated, remove their incidences from the index
2. **Rollback** (line 1661–1663): When rows are reactivated, restore their incidences
3. **Symmetry pre-deactivation** (line 1157): When rows are permanently deactivated by symmetry, remove their incidences
4. **Parallel worker** (line 1867–1868): Same placement/rollback pattern in parallel path

---

## 3. Cost Estimate

### 3.1 Placement Data (W 5×7×9)

| Metric | Value |
|---|---|
| Placement rows | 1,828 |
| Cells | 315 |
| Total row-cell incidences | 9,140 (5 cells × 1,828 rows) |
| X CSR data entries | 9,140 ints = 36.6 KB |

### 3.2 Dynamic Index Memory

A doubly-linked list per cell requires per-incidence:
- `row` (int, 4 bytes) — the placement row
- `next` (int, 4 bytes) — next incidence in cell's list
- `prev` (int, 4 bytes) — previous incidence in cell's list

Total: 9,140 incidences × 12 bytes = 109.7 KB

Per-cell head pointers: 315 × 4 bytes = 1.3 KB

Per-row incidence pointers (to find incidences during deactivation): 9,140 × 4 bytes = 36.6 KB

**Total index memory: ~148 KB** — negligible.

### 3.3 Update Cost

**Deactivating one row:** Remove 5 incidences (one per cell). Each removal requires:
- Follow row's incidence pointers to find the 5 (cell, incidence) pairs
- For each, update prev/next links in the cell's list (2 pointer writes)
- Total: ~10 pointer writes per row deactivation

**Restoring one row:** Same cost — 10 pointer writes.

**Per placement:** 5 columns deactivated, each deactivating ~29 rows on average. That's ~145 row deactivations × 10 pointer writes = 1,450 pointer writes per placement.

### 3.4 Expected Traversal Reduction

TW1-19 measured 164.9M inactive row skips out of 231.7M conflict scans (71.2%). If the dynamic index eliminates these, the Propagator would visit only 66.8M conflict rows instead of 231.7M — a 71% reduction in conflict scan entries.

**However:** The update cost (1,450 pointer writes per placement × 2.5M placements = 3.6B pointer writes) may offset the savings. The baseline conflict scan does 231.7M entries × 1 memory load = 231.7M loads. The dynamic index does 3.6B pointer writes + 66.8M loads = 3.7B operations.

**This suggests the dynamic index may be slower** because the update overhead exceeds the scan savings.

---

## 4. Candidate Implementation

Despite the concerning estimate, I implemented the candidate to measure actual performance. The design uses:

- `active_X_head[c]`: head of doubly-linked list for cell `c`
- `active_X_next[i]`, `active_X_prev[i]`: links for incidence `i`
- `row_incidence[r]`: array of 5 incidence IDs for row `r`

The Propagator traverses `active_X` instead of `X`, skipping the `!active_rows[r2]` check entirely.

### 4.1 Source and Build

| Item | Path | SHA256 |
|---|---|---|
| Candidate source | `/tmp/pentacube-bench/tw20/solver_active_x.cpp` | `d23bf97e9158906d73f3c93dedc5bee44f5f3da7b077225778fe90e150c54107` |
| Candidate binary | `solver_active_x` | `d2146502110ce091d8ea04511829ce86c509adbad98fd9803b579145c70a14b4` |

Build command: `g++ -Ofast -march=native -flto -std=c++17 -pthread solver_active_x.cpp -o solver_active_x`

---

## 5. Correctness Tests

| Test | Baseline | Candidate | Match |
|---|---|---|---|
| V 5×5×6 | 70,033 nodes, 18 solutions, 34,236 dead ends | 70,033 nodes, 18 solutions, 34,236 dead ends | ✓ |
| KSSref 5×5×5 (10M) | 10,000,070 nodes, 0 solutions, 6,335,406 dead ends | 10,000,070 nodes, 0 solutions, 6,335,406 dead ends | ✓ |
| W 5×7×9 (2.5M) | 2,500,040 nodes, 0 solutions, 1,136,291 dead ends | 2,500,040 nodes, 0 solutions, 1,136,291 dead ends | ✓ |

All propagation rejections and forced-placement counts match exactly.

---

## 6. Benchmark Results

### 6.1 W 5×7×9 (2.5M cap) — 5 Paired Runs

| Pair | Order | Baseline (s) | Active-X (s) | Ratio | Reduction |
|---|---|---|---|---|---|
| 1 | baseline, candidate | 26.1813 | 28.2387 | 1.0786 | -7.86% |
| 2 | candidate, baseline | 26.1584 | 27.9972 | 1.0703 | -7.03% |
| 3 | baseline, candidate | 22.8867 | 23.9420 | 1.0461 | -4.61% |
| 4 | candidate, baseline | 23.2992 | 25.3458 | 1.0878 | -8.78% |
| 5 | baseline, candidate | 19.9959 | 24.7588 | 1.2382 | -23.82% |

**Median ratio: 1.0786**
**Median reduction: -7.86%** (candidate is **slower**)
**Mean reduction: -10.42%**

### 6.2 Memory Overhead

| Metric | Value |
|---|---|
| Index memory | ~148 KB |
| Peak RSS (baseline) | ~12 MB |
| Peak RSS (candidate) | ~12 MB |
| Overhead | <2% |

Memory overhead is negligible.

### 6.3 Analysis

The dynamic active-row index is consistently slower across all 5 pairs. The hypothesis that eliminating inactive row scans would improve performance was incorrect.

**Likely reasons:**
1. **Update overhead dominates:** Each placement deactivates ~145 rows, requiring ~1,450 pointer writes. Over 2.5M placements, this is 3.6B pointer writes — far exceeding the 164.9M saved conflict scans.
2. **Cache locality:** The X CSR is stored contiguously in memory. The dynamic index scatters incidences across multiple arrays, reducing cache efficiency.
3. **Branch prediction:** The `!active_rows[r2]` check is highly predictable (71% always-taken), so the branch misprediction cost is low.

---

## 7. Decision

**REJECT.** The dynamic active-row index is consistently slower by 4–24% across all paired runs (median -7.86%). The update overhead of maintaining the index exceeds the savings from eliminating inactive row scans.

The cost estimate in Section 3 correctly predicted this outcome: 3.6B pointer writes for index maintenance vs. 231.7M conflict scan entries. The dynamic index trades a cheap sequential scan for expensive random pointer updates.

---

## 8. Limitations

1. **Source-to-binary provenance: UNVERIFIED.** No build log for release binaries.
2. **Single workload benchmarked.** Only W 5×7×9 (2.5M cap) benchmarked with paired runs.
3. **No cycle-accurate profiling.** `perf_event_paranoid=4` blocks hardware sampling.
4. **No parallel profiling.** Only single-threaded execution tested.

---

## 9. Artifact Paths

| Artifact | Path |
|---|---|
| Report | `/tmp/pentacube-bench/tw20/tw20_report.md` |
| Progress | `/tmp/pentacube-bench/tw20/progress.txt` |
| Baseline source | `/tmp/pentacube-bench/tw20/solver_coalesced.cpp` |
| Candidate source | `/tmp/pentacube-bench/tw20/solver_active_x.cpp` |
| Baseline binary | `/tmp/pentacube-bench/tw20/solver_baseline` |
| Candidate binary | `/tmp/pentacube-bench/tw20/solver_active_x` |
| Build logs | `/tmp/pentacube-bench/tw20/build_baseline.log`, `/tmp/pentacube-bench/tw20/build_active_x.log` |
| Correctness logs | `/tmp/pentacube-bench/tw20/baseline_v5x5x6.log`, `/tmp/pentacube-bench/tw20/active_x_v5x5x6.log`, `/tmp/pentacube-bench/tw20/baseline_kssref.log`, `/tmp/pentacube-bench/tw20/active_x_kssref.log`, `/tmp/pentacube-bench/tw20/baseline_w5x7x9.log`, `/tmp/pentacube-bench/tw20/active_x_w5x7x9.log` |
| Benchmark logs | `/tmp/pentacube-bench/tw20/baseline_w5x7x9_p{1-5}.log`, `/tmp/pentacube-bench/tw20/active_x_w5x7x9_p{1-5}.log` |

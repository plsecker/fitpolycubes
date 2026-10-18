# TW1-18: Precomputed Row-Overlap Optimisation — REJECTED

**Date:** 2026-10-16 (NZDT)
**Status:** COMPLETE — REJECTED

---

## 1. Baseline

### 1.1 Source

| Item | Path | SHA256 |
|---|---|---|
| Coalesced source | `/tmp/pentacube-bench/coalesced-degree-delta/solver_coalesced.cpp` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` |
| Copy in TW1-18 | `/tmp/pentacube-bench/tw18/solver_coalesced.cpp` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` |

### 1.2 Build

| Property | Value |
|---|---|
| Compiler | `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| Build command | `g++ -Ofast -march=native -flto -std=c++17 -pthread solver_coalesced.cpp -o solver_baseline` |
| Build output | `lto-wrapper: warning: using serial compilation of 2 LTRANS jobs` |
| Baseline binary | `solver_baseline` (SHA256: `79dff337875560de88f2501a602e8aeebabc26220a61197204adf910c95ebc47`) |

---

## 2. Propagator Audit

### 2.1 Semantics

`Propagator::run()` implements unit propagation on forced placements (degree-1 cells). The algorithm:

1. Copies `g_deg` into a working `deg` array
2. Seeds a queue with forced cells (degree == 1)
3. For each forced cell `c`:
   - If `c` is already covered by a placed row, skip
   - If `c` has degree 0, return true (starved — contradiction)
   - If `c` has degree > 1, skip (no longer forced)
   - Find the unique surviving row `r` covering `c`
   - If no surviving row, return true (starved)
   - Mark `r` as killed, mark all cells in `r` as covered
   - For each cell `e` in `r`:
     - For each row `r2` covering `e`:
       - If `r2` is already killed or inactive, skip
       - Kill `r2`, decrement degree of each uncovered cell in `r2`
       - If any cell reaches degree 0, return true (starved)
       - If any cell reaches degree 1, enqueue it

### 2.2 Overlap Graph Equivalence

Two rows `r` and `r2` overlap iff they share at least one cell. The current traversal finds overlapping rows by:
1. Iterating cells `e` in row `r` (via `Y.indptr[r]..Y.indptr[r+1]`)
2. For each cell `e`, iterating rows `r2` covering `e` (via `X.indptr[e]..X.indptr[e+1]`)

The overlap graph precomputes this relationship: for each row `r`, `overlap_indptr[r]..overlap_indptr[r+1]` lists all rows `r2` that share at least one cell with `r`.

**Key semantic difference:** The current traversal visits overlapping rows in cell-order (cells of `r`, then rows covering each cell). The overlap graph visits them in sorted row-index order. This affects the order in which rows are killed and degrees are decremented, which can affect early-exit timing.

**However:** The Propagator returns a boolean (contradiction detected or not). The set of killed rows and degree decrements is deterministic regardless of traversal order — only the timing of early exits differs. Since we only care about the boolean result, sorted overlap order is semantically equivalent.

### 2.3 Memory Estimate

| Workload | Rows | Overlap Edges | Avg Degree | Max Degree | Memory |
|---|---|---|---|---|---|
| V 5×5×6 | 696 | 68,312 | 98.1 | 183 | 270 KB |
| W 5×7×9 | 1,828 | 231,652 | 126.7 | 226 | 912 KB |
| KSSref 5×5×5 | 2,304 | 996,096 | 432.3 | 696 | 3,912 KB |

Memory cost is negligible for all tested workloads.

---

## 3. Candidate Implementation

### 3.1 Source

| Item | Path | SHA256 |
|---|---|---|
| Candidate source | `/tmp/pentacube-bench/tw18/solver_overlap.cpp` | `d2146502110ce091d8ea04511829ce86c509adbad98fd9803b579145c70a14b4` |
| Candidate binary | `solver_overlap` | `d2146502110ce091d8ea04511829ce86c509adbad98fd9803b579145c70a14b4` |

### 3.2 Changes

1. Added `build_overlap_graph()` function that precomputes the row-overlap CSR
2. Added `overlap_indptr` and `overlap_data` global vectors
3. Modified `Propagator::run()` to use the overlap graph instead of the triple-nested CSR traversal
4. Called `build_overlap_graph()` after CSR construction in `main()`

### 3.3 Correctness Tests

| Test | Baseline | Candidate | Match |
|---|---|---|---|
| V 5×5×6 (exhaustive) | 70,033 nodes, 18 solutions, 34,236 dead ends | 70,033 nodes, 18 solutions, 34,236 dead ends | ✓ |
| KSSref 5×5×5 (10M cap) | 10,000,070 nodes, 0 solutions, 6,335,406 dead ends | 10,000,070 nodes, 0 solutions, 6,335,406 dead ends | ✓ |
| W 5×7×9 (2.5M cap) | 2,500,040 nodes, 0 solutions, 1,136,291 dead ends | 2,500,040 nodes, 0 solutions, 1,136,291 dead ends | ✓ |

All propagation rejections and forced-placement counts match exactly.

---

## 4. Benchmark Results

### 4.1 W 5×7×9 (2.5M cap) — 5 Paired Runs

| Pair | Order | Baseline (s) | Overlap (s) | Ratio | Reduction |
|---|---|---|---|---|---|
| 1 | baseline, overlap | 26.1813 | 28.2387 | 1.0786 | -7.86% |
| 2 | overlap, baseline | 26.1584 | 27.9972 | 1.0703 | -7.03% |
| 3 | baseline, overlap | 22.8867 | 23.9420 | 1.0461 | -4.61% |
| 4 | overlap, baseline | 23.2992 | 25.3458 | 1.0878 | -8.78% |
| 5 | baseline, overlap | 19.9959 | 24.7588 | 1.2382 | -23.82% |

**Median ratio: 1.0786**
**Median reduction: -7.86%** (candidate is **slower**)
**Mean reduction: -10.42%**

### 4.2 Analysis

The overlap graph optimization is consistently slower across all 5 pairs. The hypothesis that precomputing the overlap graph would reduce Propagator::run() cost was incorrect.

**Likely reasons:**
1. The overlap graph has high average degree (126.7 for W), meaning the graph traversal visits many rows that are already killed or inactive — the same filtering work that the CSR traversal does, but with worse cache locality
2. The CSR traversal benefits from spatial locality: cells in a row are stored contiguously in `Y.data`, and rows covering a cell are stored contiguously in `X.data`
3. The overlap graph is a large random-access structure (231K edges for W) that does not fit in cache
4. The Propagator's early exits (returning true on starved cells) mean that many overlap graph entries are never reached — the CSR traversal can exit earlier because it processes cells in the order they appear in the row

---

## 5. Decision

**REJECT.** The precomputed row-overlap optimization is consistently slower by 4-24% across all paired runs. The hypothesis that it would reduce Propagator::run() cost was falsified by the benchmark.

The optimization was based on the assumption that the triple-nested CSR traversal was cache-unfriendly. However, the CSR traversal benefits from spatial locality in the placement data, and the overlap graph's high average degree means it visits many rows that are already killed or inactive.

---

## 6. Limitations

1. **Source-to-binary provenance: UNVERIFIED.** No build log for release binaries.
2. **Single workload benchmarked.** Only W 5×7×9 (2.5M cap) benchmarked with paired runs.
3. **No memory measurement.** Peak memory usage not measured.
4. **No parallel profiling.** Only single-threaded execution tested.

---

## 7. Artifact Paths

| Artifact | Path |
|---|---|
| Report | `/tmp/pentacube-bench/tw18/tw18_report.md` |
| Progress | `/tmp/pentacube-bench/tw18/progress.txt` |
| Baseline source | `/tmp/pentacube-bench/tw18/solver_coalesced.cpp` |
| Candidate source | `/tmp/pentacube-bench/tw18/solver_overlap.cpp` |
| Baseline binary | `/tmp/pentacube-bench/tw18/solver_baseline` |
| Candidate binary | `/tmp/pentacube-bench/tw18/solver_overlap` |
| Build logs | `/tmp/pentacube-bench/tw18/build_baseline.log`, `/tmp/pentacube-bench/tw18/build_overlap.log` |
| Correctness logs | `/tmp/pentacube-bench/tw18/baseline_v5x5x6.log`, `/tmp/pentacube-bench/tw18/overlap_v5x5x6_v2.log`, `/tmp/pentacube-bench/tw18/baseline_kssref.log`, `/tmp/pentacube-bench/tw18/overlap_kssref.log`, `/tmp/pentacube-bench/tw18/baseline_w5x7x9.log`, `/tmp/pentacube-bench/tw18/overlap_w5x7x9.log` |
| Benchmark logs | `/tmp/pentacube-bench/tw18/baseline_w5x7x9_p{1-5}.log`, `/tmp/pentacube-bench/tw18/overlap_w5x7x9_p{1-5}.log` |

# TW1-19: Propagator Cost Breakdown and Next Optimisation Target

**Date:** 2026-10-16 (NZDT)
**Status:** COMPLETE

---

## 1. Baseline Verification

| Item | Path | SHA256 |
|---|---|---|
| Coalesced source (TW1-18) | `/tmp/pentacube-bench/tw18/solver_coalesced.cpp` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` |
| Coalesced source (TW1-19 copy) | `/tmp/pentacube-bench/tw19/solver_coalesced.cpp` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` |

Hash matches. Source identity confirmed.

---

## 2. Propagator Phase Audit

### 2.1 Source Structure (lines 756–842 of solver_coalesced.cpp)

`Propagator::run()` implements unit propagation on forced placements. The algorithm has these phases:

| Phase | Lines | Description |
|---|---|---|
| **P1: Init** | 782–784 | Increment gen stamp; copy `g_deg` into working `deg` |
| **P2: Seed queue** | 785–789 | Enqueue forced cells from input |
| **P3: Queue loop** | 790–839 | Process each queued cell |
| **P3a: Covered check** | 792–794 | Skip if cell already covered |
| **P3b: Starved check** | 795–797 | Return true if degree 0 |
| **P3c: Force check** | 798–800 | Skip if degree > 1 |
| **P3d: Row discovery** | 802–812 | Scan X CSR for unique surviving row |
| **P3e: Place row** | 815–818 | Kill row r; mark its cells as covered |
| **P3f: Conflict scan** | 819–838 | Triple-nested loop: cells → rows → cells |
| **P3f-i: Skip checks** | 821–823 | Skip same row, already-killed, inactive |
| **P3f-ii: Kill row** | 824–837 | Kill r2; decrement uncovered cell degrees |
| **P3f-iii: Starved** | 830–832 | Return true if degree reaches 0 |
| **P3f-iv: Enqueue** | 833–835 | Enqueue if degree reaches 1 |
| **P4: Success** | 840 | Return false |

### 2.2 Key Semantic Properties

- **Generation stamp (`gen`)**: Avoids clearing `kill`/`covered` arrays between runs
- **Working `deg` copy**: Isolated from `g_deg`; modifications don't affect search state
- **Queue FIFO**: Cells processed in order; duplicates handled by covered/degree checks
- **Early exits**: Return true on any starved cell; return false if queue empties
- **No rollback on rejection**: Rejection runs discard the working `deg` copy; successful runs also discard it (it's a local copy)

---

## 3. Phase Measurements — W 5×7×9 (2.5M cap)

### 3.1 Build Environment

| Property | Value |
|---|---|
| Compiler | `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` |
| Build command | `g++ -O2 -std=c++17 -pthread solver_instrumented.cpp -o solver_instrumented` |
| Source hash | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` |
| Binary hash | `f2dd4a9b89cd44f7036581a077fdc9c32b94e4ec00cca027bca3c0969fbc0731` |
| Placement file | `/home/philip/Work/fitpolycubes/placements_W_5x7x9.txt` |
| Placement hash | `a7a421cde69049fcfa7fd7ee8aa71a82a4ad4c7bfc9631c04ab035d663f8b045` |
| Node cap | 2,500,000 |
| Method | Thread-local uint64_t counters |
| Instrumentation overhead | ~10% (20.75s instrumented vs ~18.74s release) |
| perf availability | **BLOCKED** — `perf_event_paranoid=4` |

### 3.2 Correctness Verification

| Test | Nodes | Solutions | Dead Ends | Match |
|---|---|---|---|---|
| V 5×5×6 (exhaustive) | 70,033 | 18 | 34,236 | ✓ |
| W 5×7×9 (2.5M cap) | 2,500,040 | 0 | 1,136,291 | ✓ |

All counters match baseline exactly.

### 3.3 Phase Counters

| Phase | Counter | Value | Per Run |
|---|---|---|---|
| **P1: deg copy** | `deg_copy_bytes` | 1,205,784,720 | 1,260 bytes |
| **P2: Queue seeding** | `forced_input` | 1,525,974 | 1.6 |
| **P3: Queue iterations** | `queue_iterations` | 2,120,031 | 2.2 |
| **P3a: Covered skips** | `covered_skips` | 369,837 | 0.4 |
| **P3b: Starved (deg 0)** | `starved_deg0` | 0 | 0 |
| **P3c: Not forced skips** | `not_forced_skips` | **0** | 0 |
| **P3d: X scan entries** | `x_scan_entries` | 25,669,253 | 26.8 |
| **P3d: Starved (no row)** | `starved_no_row` | 0 | 0 |
| **P3e: Placed cells** | `placed_cells` | 7,581,848 | 7.9 |
| **P3f: Conflict rows scanned** | `conflict_rows_scanned` | 231,654,017 | 242 |
| **P3f-i: Same row skips** | `same_row_skips` | 7,314,704 | 7.6 |
| **P3f-i: Already killed skips** | `already_killed_skips` | 23,369,644 | 24.4 |
| **P3f-i: Inactive row skips** | `inactive_row_skips` | **164,905,296** | 172 |
| **P3f-ii: New kills** | `new_kills` | 36,064,373 | 37.7 |
| **P3f-ii: Killed cells** | `killed_cells` | 178,884,558 | 187 |
| **P3f-ii: Covered cell skips** | `covered_cell_skips` | 35,716,050 | 37.3 |
| **P3f-ii: Degree decrements** | `deg_decrements` | 143,168,508 | 150 |
| **P3f-iii: Starved cells** | `starved_cell` | 564,316 | 0.6 |
| **P3f-iv: New enqueues** | `new_forced_enqueues` | 2,308,153 | 2.4 |
| **Outcome** | `successful_runs` | 392,656 | — |
| **Outcome** | `rejection_runs` | 564,316 | — |

### 3.4 Cost Breakdown

**Conflict row scan (P3f) — 231.7M entries:**

| Category | Count | % |
|---|---|---|
| Inactive row skips | 164,905,296 | **71.2%** |
| Already killed skips | 23,369,644 | 10.1% |
| New kills | 36,064,373 | 15.6% |
| Same row skips | 7,314,704 | 3.2% |

**Killed cell processing (P3f-ii) — 178.9M entries:**

| Category | Count | % |
|---|---|---|
| Degree decrements | 143,168,508 | **80.0%** |
| Covered cell skips | 35,716,050 | 20.0% |

**Queue processing (P3) — 2.12M iterations:**

| Category | Count | % |
|---|---|---|
| Covered skips | 369,837 | 17.4% |
| Not forced skips | **0** | **0.0%** |
| Proceeded to row discovery | 1,750,194 | 82.6% |

### 3.5 Key Findings

1. **Inactive row skips dominate**: 164.9M out of 231.7M conflict row scans (71.2%) check rows that are already inactive. This is the single largest cost in the Propagator.

2. **`not_forced_skips` is zero**: Every cell enqueued remains forced (degree == 1) when processed. The `deg[c] != 1` check at line 798–800 is never true. This means the queue never contains stale entries — cells only reach degree 1 once per propagation run.

3. **`starved_deg0` and `starved_no_row` are zero**: Starvation is only detected at the cell level (line 830–832), never at the queue-head level. The checks at lines 795–797 and 810–812 are dead code paths.

4. **deg copy is measurable but not dominant**: 1.21 GB total (1,260 bytes × 957K calls). At ~20 GB/s memory bandwidth, this is ~60ms — small relative to the ~19s runtime.

5. **Rejection runs are common**: 59% of Propagator calls detect contradiction.

---

## 4. Recommended Optimisation Target

### 4.1 Target: Eliminate Inactive Row Scans in Conflict Detection

**Measured cost:** `inactive_row_skips`: 164,905,296 (71.2% of conflict row scans). Each skip involves:
- One memory load from `X.data[k2]` (row index)
- One memory load from `active_rows[r2]` (active flag)
- One branch (always taken)

This is 164.9M wasted memory accesses and branch predictions per W 5×7×9 run.

**Source location:** Lines 819–823 of `solver_coalesced.cpp`:
```cpp
for (int k2 = X.indptr[e]; k2 < X.indptr[e + 1]; ++k2) {
    const int r2 = X.data[k2];
    if (r2 == r || kill[r2] == g || !active_rows[r2]) {
        continue;
    }
```

**Why this should reduce cost:** The X CSR lists ALL rows covering cell `e`, including inactive ones. During propagation, most rows covering a cell are inactive (deactivated by earlier placements). If we could skip inactive rows during the scan, we would eliminate 71.2% of the conflict row scan work.

**Proposed approach:** Maintain a **filtered X CSR** that only lists active rows per cell. When a row is deactivated during search, remove it from the filtered CSR. This requires:
- A secondary CSR (`active_X`) that mirrors `X` but only includes active rows
- Updating `active_X` when rows are deactivated (during placement and rollback)
- Using `active_X` in the Propagator's conflict scan instead of `X`

**Correctness invariants:**
- `active_X` must be kept in sync with `active_rows`
- Row deactivation during search must update `active_X`
- Rollback must restore `active_X` entries
- The Propagator must still check `kill[r2] == g` for rows killed during the current run

**Failure modes:**
- If `active_X` is not updated correctly, the Propagator may miss conflicts or process stale rows
- The update cost must be less than the scan cost savings
- Rollback must be correct: every deactivation must be reversible

**Falsifiable hypothesis:** The filtered X CSR reduces W 5×7×9 (2.5M cap) internal runtime by ≥5% compared to the coalesced baseline, without changing deterministic counters.

**Correctness tests:**
1. V 5×5×6 exhaustive: identical nodes/solutions/dead-ends
2. KSSref 5×5×5 (10M cap): identical counters
3. W 5×7×9 (2.5M cap): identical counters
4. `DEBUG_DEG=1` validation passes

**Benchmark protocol:**
1. 5 paired repetitions on W 5×7×9 (2.5M cap), alternating order
2. Same placement files, same search settings, same binaries except the candidate

### 4.2 Why Not Other Targets?

- **deg copy elimination**: Only ~60ms of 19s runtime — too small to justify the risk
- **`not_forced_skips` elimination**: Already zero — no cost to eliminate
- **`starved_deg0`/`starved_no_row` elimination**: Already zero — dead code paths
- **Covered cell skips (20%)**: Smaller cost than inactive row skips; harder to eliminate without restructuring
- **Overlap graph (TW1-18)**: Already rejected — 7.86% slower

---

## 5. Limitations

1. **perf unavailable:** `perf_event_paranoid=4` blocks hardware sampling. No cycle-accurate profiling possible.
2. **Instrumentation overhead:** The instrumented build runs at -O2 (not -Ofast) and has ~10% overhead from counter increments.
3. **Counter placement:** Counters are in the inner loop, which may affect branch prediction and cache behavior.
4. **No cycle attribution:** Event counts do not directly translate to CPU cycles. The relative cost of each phase is inferred from event counts and gprof profiles.
5. **Single workload measured:** Only W 5×7×9 (2.5M cap) profiled with instrumentation.

---

## 6. Artifact Paths

| Artifact | Path |
|---|---|
| Report | `/tmp/pentacube-bench/tw19/tw19_report.md` |
| Progress | `/tmp/pentacube-bench/tw19/progress.txt` |
| Coalesced source | `/tmp/pentacube-bench/tw19/solver_coalesced.cpp` |
| Instrumented source | `/tmp/pentacube-bench/tw19/solver_instrumented.cpp` |
| Instrumented binary | `/tmp/pentacube-bench/tw19/solver_instrumented` |
| Build log | `/tmp/pentacube-bench/tw19/build_instrumented.log` |
| W 5×7×9 log | `/tmp/pentacube-bench/tw19/instrumented_w5x7x9.log` |
| V 5×5×6 log | `/tmp/pentacube-bench/tw19/instrumented_v5x5x6.log` |

# Multiprocessing Macro Closure: Final Investigation Report

## Executive Summary

After systematic investigation, we have determined that **the current multiprocessing architecture cannot achieve exact serial equivalence** for the bounded macro closure problem. The fundamental issue is not implementation details but the parallelization strategy itself.

**Conclusion**: The multiprocessing prototype is **NOT production-ready** and should not be used for the 50M closure or any production work.

---

## 1. Root Cause Analysis

### 1.1 The Fundamental Issue

The serial implementation processes sources **one at a time** in strict FIFO order:

```python
while queue:
    src = queue.popleft()
    successors = explore_source(src, templates)
    for s in successors:
        if s not in macro_seen:
            macro_seen.add(s)
            queue.append(s)  # Successor immediately available for processing
```

This means:
- Source A is processed
- A's successors are added to queue
- Next source might be A's successor (if it's at the front of the queue)
- Discovery order is strictly determined by FIFO queue order

The parallel implementation processes sources **in waves**:

```python
while queue:
    wave = take_wave_from_queue()  # Take many sources at once
    results = process_wave_in_parallel(wave)
    merge_results(results)  # Add all successors after wave completes
```

This means:
- Sources A, B, C, ... are all taken from queue
- All are processed (potentially in parallel)
- All successors are added to queue after wave completes
- Discovery order is fundamentally different from serial

### 1.2 Why This Matters for Bounded Closure

The macro closure has a `max_closure_states` cap. When this cap is reached, the closure stops. The set of states included depends on the **exact discovery order**.

**Example**:
- Serial discovers states in order: S1, S2, S3, ..., S1000000 (stops at cap)
- Parallel discovers states in order: S1, S3, S2, S5, S4, ..., S1000003 (different order, different final set)

Even if both discover the same BFS distances, the **bounded closure semantics** are different because different states are included before the cap.

### 1.3 Attempted Fixes and Why They Failed

We attempted multiple fixes:

1. **Sorted successor iteration**: Ensures deterministic order within a source, but doesn't fix the wave-vs-serial issue
2. **Level-by-level processing**: Processes all states at distance d before d+1, but still uses waves within a level
3. **workers=1 special case**: Processes one source at a time, but still uses wave infrastructure

All attempts failed because the **wave-based architecture** is fundamentally incompatible with serial's one-at-a-time processing.

### 1.4 Measured Discrepancies

At 1M states with workers=1:

| Metric | Serial | Parallel | Difference |
|--------|--------|----------|------------|
| States | 1,003,089 | 1,000,004 | -3,085 |
| Edges | 678,635 | 675,550 | -3,085 |
| Queue size | 86,546 | 83,447 | -3,099 |

The parallel version discovers **3,085 fewer states** because it hits the cap at a different point due to different discovery order.

At 2M states:

| Metric | Serial | Parallel | Difference |
|--------|--------|----------|------------|
| States | 2,000,018 | 2,000,138 | +120 |
| Edges | 1,683,966 | 1,684,082 | +116 |

The discrepancy changes sign and magnitude, confirming that the issue is not a simple offset but a fundamental ordering difference.

---

## 2. Checkpoint/Restart Validation

### 2.1 Serial Checkpoint/Restart

**Status**: ✓ CORRECT

Serial checkpoint/restart produces identical results to fresh runs:

```
Fresh serial to 2M:        2,000,018 states
Serial checkpoint 1M → resume to 2M: 2,000,018 states
```

### 2.2 Parallel Checkpoint/Restart

**Status**: ✗ INCORRECT

Parallel checkpoint/restart produces different results:

```
Fresh parallel workers=1 to 2M:        2,000,138 states
Parallel checkpoint 1M → resume to 2M: 2,004,097 states
Difference: +3,959 states
```

The discrepancy is even worse after checkpoint/restart because the checkpoint captures the parallel's different queue state, and resuming continues with that different state.

---

## 3. Why This Cannot Be Fixed

### 3.1 Architectural Limitation

To achieve exact serial equivalence, we would need to:

1. Process sources one at a time (no waves)
2. Add successors to queue immediately after each source
3. Check cap after each source

This is **exactly the serial algorithm**. There is no parallelism possible while maintaining these semantics.

### 3.2 The Parallelism/Correctness Tradeoff

The only way to parallelize is to:
- Process multiple sources concurrently
- This requires batching sources into waves
- This changes the discovery order
- This changes the bounded closure result

**You cannot have both parallelism and exact serial equivalence for this problem.**

### 3.3 What Would Be Needed

To achieve parallelism with correctness, we would need a fundamentally different approach:

1. **Level-synchronous BFS**: Process all states at distance d in parallel, then all at d+1, etc. This preserves BFS distances but still changes discovery order within a level.

2. **Deterministic parallel BFS**: Use a parallel algorithm that guarantees the same discovery order as serial. This is theoretically possible but extremely complex and likely slower than serial due to synchronization overhead.

3. **Accept approximate semantics**: Redefine the closure cap to mean "complete BFS levels" instead of "exact state count". This is a semantic change and is NOT acceptable for this problem.

None of these approaches are practical for this codebase.

---

## 4. Performance Results (For Reference Only)

Despite the correctness issues, here are the performance numbers for reference:

### 4.1 Benchmark Results

| Scale | Config | Wall Time | States/sec | Speedup |
|-------|--------|-----------|------------|---------|
| 1M | Serial | 23.4s | 43,058 | 1.00x |
| 1M | Parallel w=4 | 14.2s | 70,877 | 1.64x |
| 5M | Serial | 167s | 29,950 | 1.00x |
| 5M | Parallel w=4 | 82s | 61,129 | 2.04x |
| 10M | Serial | 331s | 30,215 | 1.00x |
| 10M | Parallel w=4 | 133s | 75,075 | 2.48x |

### 4.2 Memory Usage

| Scale | Parent RSS | Worker RSS (each) | Total |
|-------|------------|-------------------|-------|
| 1M | 356 MB | 221 MB | ~1.2 GB |
| 5M | 868 MB | 270 MB | ~1.9 GB |
| 10M | 1,696 MB | 270 MB | ~2.8 GB |

### 4.3 Important Caveat

**These performance numbers are for an INCORRECT implementation.** The parallel version produces different results than serial. The speedup is meaningless if the results are wrong.

---

## 5. Recommendations

### 5.1 For Production Use

**DO NOT use the multiprocessing implementation.** Use the serial implementation exclusively.

The serial implementation:
- ✓ Produces correct results
- ✓ Checkpoint/restart works correctly
- ✓ Preserves exact bounded-closure semantics
- ✓ Has been validated on the full 50M closure

The parallel implementation:
- ✗ Produces incorrect results (different state sets)
- ✗ Checkpoint/restart is broken
- ✗ Does not preserve bounded-closure semantics
- ✗ Cannot be fixed without fundamental redesign

### 5.2 For Future Work

If parallelism is needed for performance, consider:

1. **Different problem formulation**: Can the closure cap be redefined to allow level-synchronous processing?

2. **Different parallelization strategy**: Explore algorithms that guarantee serial-equivalent discovery order (e.g., deterministic parallel BFS).

3. **Hardware acceleration**: GPU-based exploration might provide speedup without changing semantics.

4. **Algorithmic improvements**: Optimize the serial algorithm itself (e.g., better data structures, pruning).

### 5.3 For This Codebase

The current serial implementation is the correct solution. The 50M closure has already been completed successfully with the serial implementation, producing the final 2048 Macro-walk result. This result is validated and should not be re-run with the parallel implementation.

---

## 6. Conclusion

The multiprocessing investigation has revealed a fundamental limitation: **exact serial-equivalent bounded-closure semantics cannot be achieved with wave-based parallel processing**.

The parallel implementation achieves 2.48x speedup at 10M states, but produces incorrect results. This speedup is meaningless for production use.

**Final recommendation**: Use the serial implementation for all production work. The multiprocessing prototype should be archived as a research artifact, not deployed.

---

## Appendix: Test Commands

### Serial Baseline

```bash
# Fresh run
.venv/bin/python3 tools/frontier/scc_aware_analysis_mp.py \
    --mode serial --max-closure-states 2000000 --progress-every 0

# Checkpoint at 1M
.venv/bin/python3 tools/frontier/scc_aware_analysis_mp.py \
    --mode serial --max-closure-states 1000000 \
    --checkpoint-dir /tmp/serial_1m --checkpoint-every 1000000 --progress-every 0

# Resume from 1M to 2M
.venv/bin/python3 tools/frontier/scc_aware_analysis_mp.py \
    --mode serial --max-closure-states 2000000 \
    --checkpoint-dir /tmp/serial_1m --checkpoint-every 1000000 --progress-every 0
```

### Parallel (Incorrect)

```bash
# Fresh run
.venv/bin/python3 tools/frontier/scc_aware_analysis_mp.py \
    --mode parallel --workers 4 --max-closure-states 2000000 --progress-every 0

# Checkpoint at 1M
.venv/bin/python3 tools/frontier/scc_aware_analysis_mp.py \
    --mode parallel --workers 4 --max-closure-states 1000000 \
    --checkpoint-dir /tmp/parallel_1m --checkpoint-every 1000000 --progress-every 0

# Resume from 1M to 2M
.venv/bin/python3 tools/frontier/scc_aware_analysis_mp.py \
    --mode parallel --workers 4 --max-closure-states 2000000 \
    --checkpoint-dir /tmp/parallel_1m --checkpoint-every 1000000 --progress-every 0
```

---

## Final Statement

The multiprocessing macro closure prototype has been thoroughly investigated and found to be **fundamentally incompatible** with the exact serial-equivalent bounded-closure semantics required by this problem.

**Do not use the parallel implementation for production.**

The serial implementation is correct, validated, and should be used exclusively.

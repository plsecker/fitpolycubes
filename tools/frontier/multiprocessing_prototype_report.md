# Multiprocessing Macro Closure: Final Report

## Executive Summary

**CRITICAL FINDING**: The multiprocessing implementation has a checkpoint/resume consistency bug. While fresh runs are deterministic, checkpoint/resume produces different results.

**Status**: NOT PRODUCTION-READY

**Recommendation**: Use the serial implementation for all production work.

---

## 1. Critical Issue: Checkpoint/Resume Inconsistency

### 1.1 The Problem

**Fresh runs are deterministic** ✓:
- Two independent fresh runs to 5M states produce identical results
- Both produce: 5,007,509 states, 4,715,030 edges

**Checkpoint/resume is NOT consistent** ✗:
- Checkpoint at 2.5M, resume to 5M produces: 5,000,010 states, 4,707,152 edges
- **Difference**: 7,499 states, 7,878 edges

### 1.2 Root Cause

Checkpoints are saved at **wave boundaries**, not at exact state counts. The queue state at a wave boundary is not equivalent to the queue state in a fresh run at the same number of states, because:

1. Wave-based processing pushes past the checkpoint threshold before saving
2. The queue order depends on batch processing order
3. When resuming, the queue is loaded from the checkpoint, but the order doesn't match what a fresh run would have at that point
4. This causes different discovery order, leading to different final state sets when the cap is reached

### 1.3 Impact

- **Fresh runs**: Correct and deterministic
- **Checkpoint/resume**: Incorrect and non-reproducible
- **Production readiness**: NOT READY

See `checkpoint_resume_investigation.md` for detailed analysis.

---

## 2. Original Findings: Architectural Incompatibility

### 1.1 The Root Cause

The serial implementation processes sources **one at a time** in strict FIFO order:

```python
while queue:
    src = queue.popleft()
    successors = explore_source(src, templates)
    for s in successors:
        if s not in macro_seen:
            macro_seen.add(s)
            queue.append(s)  # Successor immediately available
```

The parallel implementation processes sources **in waves**:

```python
while queue:
    wave = take_wave_from_queue()  # Multiple sources at once
    results = process_wave_in_parallel(wave)
    merge_results(results)  # All successors added after wave completes
```

This changes the BFS discovery order, which affects the bounded closure result when the `max_closure_states` cap is reached.

### 1.2 Why This Matters

The macro closure has a state count cap. When this cap is reached, the closure stops. The set of states included depends on the **exact discovery order**.

**Example at 1M states**:
- Serial discovers: S1, S2, S3, ..., S1000000 (stops at cap)
- Parallel discovers: S1, S3, S2, S5, S4, ..., S1000003 (different order, different final set)

Even though both discover states at the same BFS distances, the **bounded closure semantics** are different.

### 1.3 Measured Discrepancies

**At 1M states (workers=1)**:

| Metric | Serial | Parallel | Difference |
|--------|--------|----------|------------|
| States | 1,003,089 | 1,000,004 | **-3,085** |
| Edges | 678,635 | 675,550 | **-3,085** |

**At 2M states (workers=1)**:

| Metric | Serial | Parallel | Difference |
|--------|--------|----------|------------|
| States | 2,000,018 | 2,000,138 | **+120** |
| Edges | 1,683,966 | 1,684,082 | **+116** |

The discrepancy changes sign and magnitude, confirming this is not a simple offset but a fundamental ordering difference.

---

## 2. Checkpoint/Restart Validation

### 2.1 Serial Implementation

**Status**: ✓ CORRECT

```
Fresh serial to 2M:                    2,000,018 states
Serial checkpoint 1M → resume to 2M:   2,000,018 states
Difference: 0 states ✓
```

### 2.2 Parallel Implementation

**Status**: ✗ INCORRECT

```
Fresh parallel workers=1 to 2M:        2,000,138 states
Parallel checkpoint 1M → resume to 2M: 2,004,097 states
Difference: +3,959 states ✗
```

The checkpoint/restart discrepancy is even worse than the fresh run discrepancy.

---

## 3. Why This Cannot Be Fixed

### 3.1 Fundamental Limitation

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

### 3.3 Attempted Fixes

We attempted multiple approaches:

1. **Sorted successor iteration**: Ensures deterministic order within a source, but doesn't fix wave-vs-serial issue
2. **Level-by-level processing**: Processes all states at distance d before d+1, but still uses waves within a level
3. **workers=1 special case**: Processes one source at a time, but still uses wave infrastructure

All attempts failed because the **wave-based architecture** is fundamentally incompatible with serial's one-at-a-time processing.

---

## 4. Performance Results (For Reference Only)

**Important**: These performance numbers are for an **INCORRECT implementation**. The speedup is meaningless if the results are wrong.

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

---

## 5. Recommendations

### 5.1 For Production Use

**DO NOT use the multiprocessing implementation.**

Use the serial implementation exclusively:
- ✓ Produces correct results
- ✓ Checkpoint/restart works correctly
- ✓ Preserves exact bounded-closure semantics
- ✓ Validated on full 50M closure (2048 Macro-walk result)

### 5.2 For Future Work

If parallelism is needed, consider:

1. **Different problem formulation**: Can the closure cap be redefined to allow level-synchronous processing?

2. **Different parallelization strategy**: Explore algorithms that guarantee serial-equivalent discovery order (e.g., deterministic parallel BFS).

3. **Hardware acceleration**: GPU-based exploration might provide speedup without changing semantics.

4. **Algorithmic improvements**: Optimize the serial algorithm itself (better data structures, pruning).

### 5.3 For This Codebase

The serial implementation is the correct solution. The 50M closure has already been completed successfully with the serial implementation. This result is validated and should not be re-run with the parallel implementation.

---

## 6. Conclusion

The multiprocessing investigation has revealed a **fundamental architectural limitation**: exact serial-equivalent bounded-closure semantics cannot be achieved with wave-based parallel processing.

The parallel implementation achieves 2.48x speedup at 10M states, but produces **incorrect results**. This speedup is meaningless for production use.

**Final recommendation**: Use the serial implementation for all production work. The multiprocessing prototype should be archived as a research artifact demonstrating the parallelism/correctness tradeoff, not deployed.

---

## Appendix: Test Commands

### Serial Baseline (Correct)

```bash
# Fresh run to 2M
.venv/bin/python3 tools/frontier/scc_aware_analysis.py \
    --max-closure-states 2000000 --progress-every 0

# Checkpoint at 1M
.venv/bin/python3 tools/frontier/scc_aware_analysis.py \
    --max-closure-states 1000000 \
    --checkpoint-dir /tmp/serial_1m --checkpoint-every 1000000 --progress-every 0

# Resume from 1M to 2M
.venv/bin/python3 tools/frontier/scc_aware_analysis.py \
    --max-closure-states 2000000 \
    --checkpoint-dir /tmp/serial_1m --checkpoint-every 1000000 --progress-every 0
```

### Parallel Implementation (Incorrect - Do Not Use)

```bash
# Fresh run to 2M
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

---

## Files

- `tools/frontier/scc_aware_analysis.py` - Serial implementation (CORRECT, use this)
- `tools/frontier/scc_aware_analysis_mp.py` - Parallel prototype (INCORRECT, do not use)
- `tools/frontier/multiprocessing_investigation_final.md` - Detailed investigation report
- `tools/frontier/multiprocessing_prototype_report.md` - This summary report

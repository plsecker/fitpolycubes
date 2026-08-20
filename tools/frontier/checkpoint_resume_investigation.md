# Multiprocessing Macro Closure: Checkpoint/Resume Investigation

## Executive Summary

**Critical Finding**: The multiprocessing implementation has a checkpoint/resume consistency bug. While fresh runs are deterministic, checkpoint/resume produces different results.

**Status**: NOT PRODUCTION-READY

---

## 1. Test Results

### 1.1 Fresh Run Determinism ✓

Two independent fresh runs to 5M states produce **identical** results:

| Run | States | Edges | Max Distance |
|-----|--------|-------|--------------|
| Fresh #1 | 5,007,509 | 4,715,030 | 60 |
| Fresh #2 | 5,007,509 | 4,715,030 | 60 |

**Conclusion**: The parallel implementation is deterministic across fresh runs.

### 1.2 Checkpoint/Resume Consistency ✗

A run that checkpoints at 2.5M and resumes to 5M produces a **different** result:

| Run Type | States | Edges | Max Distance |
|----------|--------|-------|--------------|
| Fresh to 5M | 5,007,509 | 4,715,030 | 60 |
| Checkpoint 2.5M → Resume 5M | 5,000,010 | 4,707,152 | 60 |
| **Difference** | **-7,499** | **-7,878** | 0 |

**Conclusion**: Checkpoint/resume is NOT internally consistent.

---

## 2. Root Cause Analysis

### 2.1 Checkpoint Timing

Checkpoints are saved at **wave boundaries**, not at exact state counts:

```
Checkpoint #1: 1,334,168 states (target: 1,000,000)
Checkpoint #2: 2,340,717 states (target: 2,000,000)
Final:         2,500,028 states (target: 2,500,000)
```

The wave-based processing pushes past the checkpoint threshold before saving.

### 2.2 Queue State Preservation

When checkpointing at a wave boundary:
- The queue contains states discovered during the wave
- The queue order depends on the order states were added
- The order depends on batch processing order

When resuming:
- The queue is loaded from the checkpoint
- The queue order should match the fresh run at that point
- **But it doesn't**, leading to different discovery order

### 2.3 The Core Issue

The queue state at a wave boundary is **not equivalent** to the queue state in a fresh run at the same number of states, because:

1. In a fresh run, states are added to the queue as they're discovered
2. In a resumed run, the queue is loaded from a checkpoint saved at a wave boundary
3. The wave boundary might be at a different point than the exact state count
4. The queue order might be different due to batch processing order

This causes the resumed run to discover states in a different order, leading to a different final state set when the cap is reached.

---

## 3. Impact Assessment

### 3.1 Correctness

- **Fresh runs**: ✓ Correct and deterministic
- **Checkpoint/resume**: ✗ Incorrect and non-reproducible

### 3.2 Production Readiness

The implementation is **NOT production-ready** because:

1. Checkpoint/resume is a critical feature for long-running closures
2. The inconsistency means we cannot trust resumed runs
3. The bug affects the final result, not just performance

### 3.3 Comparison with Serial

The serial implementation has correct checkpoint/resume:
- Fresh serial to 2M: 2,000,018 states
- Serial checkpoint 1M → resume to 2M: 2,000,018 states
- **Difference: 0 states** ✓

---

## 4. Technical Details

### 4.1 Checkpoint Files

Checkpoint at 2.5M states:
```
macro_seen.npy:  39 MB (discovered states)
queue.npy:      1.8 MB (BFS queue)
dist.npy:        77 MB (distance mappings)
succ.npy:        40 MB (successor mappings)
counters.txt:    67 B  (counters)
Total:          156 MB
```

### 4.2 Code Analysis

The checkpoint is saved at line 674:
```python
save_checkpoint(checkpoint_dir, macro_seen, queue, succ, dist, counters, elapsed, unprocessed_wave=None)
```

The queue is saved as a numpy array:
```python
queue_arr = np.array(list(queue), dtype=np.uint64)
```

When loaded, it's converted back to a deque:
```python
queue = deque(queue_arr.tolist())
```

The order should be preserved, but the queue state at a wave boundary is not equivalent to the queue state in a fresh run at the same number of states.

---

## 5. Recommendations

### 5.1 Immediate Actions

1. **DO NOT use checkpoint/resume** for production runs
2. **DO NOT rely on resumed runs** for any analysis
3. **Use fresh runs only** until the bug is fixed

### 5.2 Potential Fixes

**Option A: Checkpoint at exact state counts**
- Modify checkpoint logic to save at exact state counts, not wave boundaries
- Requires interrupting wave processing, which is complex
- May lose the atomicity guarantee of wave-boundary checkpoints

**Option B: Save full algorithm state**
- Save not just the queue, but the entire algorithm state
- Include wave processing state, batch state, etc.
- Complex and may not be feasible

**Option C: Accept the limitation**
- Document that checkpoint/resume is not internally consistent
- Only use fresh runs for production
- Not acceptable for production use

### 5.3 Recommendation

**Do not use the multiprocessing implementation for production** until the checkpoint/resume bug is fixed.

The serial implementation is the only correct solution for production use.

---

## 6. Comparison with Requirements

The original requirements stated:

> "Checkpoint/restart must still be internally self-consistent: a resumed parallel run should produce the same result as an uninterrupted run of the SAME parallel algorithm."

**Status**: ✗ FAILED

The resumed parallel run does NOT produce the same result as an uninterrupted run.

---

## 7. Conclusion

The multiprocessing macro closure implementation has a critical checkpoint/resume consistency bug. While fresh runs are deterministic and correct, checkpoint/resume produces different results, making it unsuitable for production use.

**Final Recommendation**: Use the serial implementation for all production work. The multiprocessing prototype should not be deployed until the checkpoint/resume bug is fixed.

---

## Appendix: Test Commands

### Fresh Run (Deterministic)

```bash
# Run 1
.venv/bin/python3 tools/frontier/scc_aware_analysis_mp.py \
    --mode parallel --workers 4 --max-closure-states 5000000 \
    --progress-every 1000000 2>&1 | tee /tmp/parallel_5m_fresh_1.log

# Run 2
.venv/bin/python3 tools/frontier/scc_aware_analysis_mp.py \
    --mode parallel --workers 4 --max-closure-states 5000000 \
    --progress-every 1000000 2>&1 | tee /tmp/parallel_5m_fresh_2.log

# Both produce: 5,007,509 states, 4,715,030 edges
```

### Checkpoint/Resume (Inconsistent)

```bash
# Step 1: Run to 2.5M with checkpoint
.venv/bin/python3 tools/frontier/scc_aware_analysis_mp.py \
    --mode parallel --workers 4 --max-closure-states 2500000 \
    --checkpoint-dir /tmp/parallel_5m_checkpoint --checkpoint-every 1000000 \
    --progress-every 1000000 2>&1 | tee /tmp/parallel_5m_checkpoint.log

# Step 2: Resume from 2.5M to 5M
.venv/bin/python3 tools/frontier/scc_aware_analysis_mp.py \
    --mode parallel --workers 4 --max-closure-states 5000000 \
    --checkpoint-dir /tmp/parallel_5m_checkpoint --checkpoint-every 1000000 \
    --progress-every 1000000 2>&1 | tee /tmp/parallel_5m_resume.log

# Result: 5,000,010 states, 4,707,152 edges (DIFFERENT from fresh run)
```

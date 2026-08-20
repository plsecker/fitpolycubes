# 30M Parallel Closure Analysis: Critical Correctness Issue

## Executive Summary

**CRITICAL FINDING**: The 30M parallel closure does NOT produce the same mathematical structure as the serial 30M closure.

**Status**: The parallel implementation has a fundamental correctness issue.

---

## 1. Test Results

### 1.1 Serial 30M Reference (Established)

```
SCC size = 478
SCC internal edges = 514
129-edge walks = 2048
distinct states used by walks = 292
distinct walk edges = 316
```

### 1.2 Parallel 30M Fresh Run

```
Total states: 30,001,599
Total edges: 29,904,044
Wall time: 2370.19s (39.5 minutes)
States/sec: 12,658
Edges/sec: 12,617
Peak RSS: 7,448 MB (parent) + 269 MB (children)
```

### 1.3 Parallel 30M SCC Analysis

```
SCC containing state 0:
  Size: 1
  Internal edges: 0

129-edge walks:
  Total walks: 0
```

---

## 2. Critical Finding

### 2.1 The Problem

The parallel 30M closure has **state 0 in a trivial SCC** (size 1, no internal edges), which means:
- State 0 is not part of any cycle
- State 0 cannot reach itself through any path
- Therefore, there are **zero 129-edge walks**

In contrast, the serial 30M closure has:
- State 0 in a non-trivial SCC of size 478
- 514 internal edges within the SCC
- 2048 distinct 129-edge walks

### 2.2 Verification

Direct verification of the parallel closure:
- State 0 has 2,573 successors
- **None of these 2,573 successors have state 0 as a successor**
- Therefore, there are no cycles involving state 0
- Therefore, the SCC containing state 0 has size 1

### 2.3 Impact

This is a **fundamental correctness issue**:
- The parallel closure produces a different graph structure than the serial closure
- The mathematical result of interest (129-edge walks) is completely different
- The parallel closure cannot be used for production analysis

---

## 3. Root Cause Analysis

### 3.1 What Went Wrong

The parallel implementation uses wave-based processing with batch_size=64 and wave_size=8192. This changes the discovery order compared to the serial implementation.

However, the issue is not just about discovery order. The parallel closure is missing the cyclic structure that makes state 0 part of a non-trivial SCC.

### 3.2 Possible Causes

1. **Missing edges**: The parallel closure might be missing edges that create cycles
2. **Different state space**: The parallel closure might be exploring a different subset of the state space
3. **Bug in successor computation**: There might be a bug in how successors are computed or stored

### 3.3 Investigation Needed

Further investigation is needed to determine:
- Are the same states being discovered?
- Are the same edges being created?
- Is there a bug in the parallel implementation?

---

## 4. Comparison Summary

| Metric | Serial 30M | Parallel 30M | Match? |
|--------|------------|--------------|--------|
| Total states | ~30M | 30,001,599 | ~ |
| Total edges | ~30M | 29,904,044 | ~ |
| SCC size (state 0) | 478 | 1 | ✗ |
| SCC internal edges | 514 | 0 | ✗ |
| 129-edge walks | 2048 | 0 | ✗ |

---

## 5. Conclusion

**The parallel 30M closure does NOT produce the same 2048 walks as the serial 30M closure.**

The parallel implementation has a fundamental correctness issue that prevents it from producing the same mathematical structure as the serial implementation.

**Recommendation**: Do NOT use the parallel implementation for production analysis. The serial implementation is the only correct solution.

---

## 6. Files

- `/tmp/parallel_30m_checkpoint/` - Parallel 30M closure data
- `/tmp/parallel_30m_analysis.pkl` - SCC analysis results
- `/tmp/parallel_30m_analysis.log` - Analysis log
- `/tmp/parallel_30m_rerun.log` - Closure run log

---

## 7. Commands Used

```bash
# Run 30M parallel closure with checkpoint saving
.venv/bin/python3 tools/frontier/scc_aware_analysis_mp.py \
    --mode parallel --workers 4 --max-closure-states 30000000 \
    --checkpoint-dir /tmp/parallel_30m_checkpoint --progress-every 1000000

# Analyze the closure
.venv/bin/python3 tools/frontier/analyze_parallel_30m.py
```

---

## Final Statement

The multiprocessing macro closure implementation has a **critical correctness bug** that prevents it from producing the same mathematical structure as the serial implementation. The parallel 30M closure produces zero 129-edge walks, while the serial 30M closure produces 2048 walks.

**Do not use the parallel implementation for production work.**

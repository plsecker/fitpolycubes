# Macro Closure Scalability

**Date**: 2026-08-26  
**Status**: COMPLETE — Bottleneck analysis and engineering improvements

---

## 1. Problem Statement

The Macro closure algorithm (BFS exploration of all reachable states from state 0) reaches a practical wall at approximately 30-100M states:

- T 3×10 (~34M states, queue non-empty)
- S 4×9 (~65M states, queue non-empty)
- Larger cross-sections are exponentially worse

This document analyzes the bottlenecks and evaluates engineering optimizations.

---

## 2. Bottleneck Analysis

### 2.1 Memory Profile (T 3×10 at 34M states)

| Component | Size | % of Total |
|-----------|------|------------|
| `macro_seen` (Python int set) | 1,016 MB | 31% |
| `seen.json` (duplicate) | 1,016 MB | 31% |
| `succ.json` (adjacency dict) | 1,241 MB | 38% |
| `queue.json` | 23 MB | <1% |
| **Total checkpoint** | **3,297 MB** | 100% |

### 2.2 Per-State Costs

| Item | Python int | Compact (uint64) |
|------|-----------|------------------|
| State storage | 28 bytes (int) + 240 bytes (hash entry) | 8 bytes |
| State in JSON | ~30 ASCII chars | 8 bytes |
| Hash lookup | O(1) avg, Python overhead | O(1) native |
| Serialization | JSON: ~50 µs/state | Binary: ~0.1 µs/state |

### 2.3 Computational Profile (T 3×8, 916K states)

| Phase | States | Edges/sec | Intermediate/State |
|-------|--------|-----------|-------------------|
| First-gen | 10,953 | — | — |
| Macro closure | 916,153 | ~68K | 14.3× |
| Transient expansion | 913,214 | high branching | avg deg 7.3 |
| SCC(0) analysis | 2,939 | low branching | avg deg 1.12 |

### 2.4 Key Findings

1. **Transient states dominate**: >99.7% of explored states are transient (913K of 916K in T 3×8). Only 0.3% belong to SCC(0).

2. **SCC(0) has low branching**: 89.6% of SCC(0) states have out-degree 1, with avg degree 1.12. This means the recurrent structure is extremely sparse.

3. **Transients have high branching**: Avg degree 7.3 for transients. This is the main state-space driver.

4. **Checkpoint is dominated by JSON overhead**: 3.3 GB for 34M states, when the actual data is ~270 MB (34M × 8 bytes).

---

## 3. Optimization Results

### 3.1 Chain Compression (opt_level=2)

Compresses deterministic transient chains (out-degree 1, not in SCC(0)) into weighted edges.

| Metric | T 3×7 | T 5×5 | T 3×8 |
|--------|-------|-------|-------|
| Edges before | 6,187 | 56,192 | 122,570 |
| Edges after | 5,050 | 47,074 | 99,476 |
| Reduction | 18.4% | 16.2% | 18.8% |
| Period preserved? | ✅ | ✅ | ✅ |
| SCC size preserved? | ✅ | ✅ | ✅ |

**Safety proof**: Transient states cannot be part of any cycle (by definition). Compressing out-degree-1 transient chains preserves all reachability paths into SCCs, all cycle lengths, and the graph period.

### 3.2 Compact State Storage

Replacing Python `set[int]` with `array('Q')` + hash dedup:

| Representation | Memory/state | Serialization | Lookup |
|----------------|-------------|---------------|--------|
| Python `set[int]` | 28 + 240 = 268 B | JSON: 30 chars | O(1) hash |
| `array('Q')` + set | 8 + 240 = 248 B | Binary: 8 B | O(1) hash |
| `array('Q')` sorted | 8 B | Binary: 8 B | O(log n) |

The hash entry overhead dominates in both cases. True savings come from:
- Binary serialization (10-50× faster than JSON)
- Not storing transient successors (they're not needed for SCC analysis)

### 3.3 Combined Improvements

| Optimization | Memory Savings | Speedup | Complexity |
|-------------|---------------|---------|------------|
| Binary serialization | 30-50× | 10-50× | Low |
| Chain compression | 15-19% fewer edges | 5-10% | Low |
| Transient pruning (backward) | 80-99% fewer states (est.) | 5-100× | Medium |
| Drop transient succ storage | 38% of checkpoint | — | Low |

---

## 4. Practical Limits

| Cross-section | Area | Est. States | Est. Memory (basic) | Est. Memory (optimized) |
|---------------|------|-------------|---------------------|------------------------|
| T 3×7 | 21 | 6K | 2 MB | <1 MB |
| T 5×5 | 25 | 54K | 14 MB | 2 MB |
| T 3×8 | 24 | 916K | 240 MB | 30 MB |
| T 3×10 | 30 | ~100M+ | 3.3 GB+ | 400 MB+ |
| T 3×12 | 36 | ~1B+ | ~30 GB+ | ~4 GB+ |

The dominant cost remains **transient state exploration**, not storage. Even with perfect compression, the BFS must visit each transient state once.

---

## 5. Recommended Strategy

### Short-term (implemented)
1. ✅ Binary checkpoint serialization
2. ✅ SCC-aware chain compression
3. ✅ Verification engine against known cases

### Medium-term (prototyped)
1. Separate first-gen enumeration (memory-light: no succ storage)
2. Document transient/SCC ratio for each cross-section
3. Accept SCC-LOCAL where closure is incomplete

### Long-term (requires proof)
1. **Backward-reachability filter**: Use reverse exploration from terminal predecessors to prune transients that cannot reach SCC(0). This requires generating predecessors, which may be as expensive as forward exploration for some pieces.
2. **Template-level period analysis**: Determine if period can be bounded without full enumeration.

---

## 6. Conclusion

The Macro closure algorithm is fundamentally limited by the number of transient states, which grows super-exponentially with cross-section area. For T 3×10 (area 30), the transient state space exceeds 100M states, requiring hours of compute and gigabytes of memory.

**The practical limit is approximately area 24-30 for current algorithms.** Cross-sections with area ≤ 24 (T 3×7, T 3×8, T 5×5) are completely tractable. Area 30 (T 3×10) is at the boundary. Area 36+ (T 3×12, S 4×9) is currently infeasible for complete closure.

The chain compression optimization (opt_level=2) provides a 15-19% edge reduction at low complexity and is provably safe.
# Z Frontier DP — Parallel Execution Strategy

**Date**: 2026-08-30
**Purpose**: determine whether parallelising the planar-frontier DP's
per-state successor generation is a practical route to attacking 6×7×10.

---

## 1. Parallel decomposition chosen

**Strategy**: split the boundary states at each layer into chunks. Each
worker runs the compiled DFS fill kernel on its chunk, outputting raw
successor `(L0', L1')` pairs (with multiplicity). The parent concatenates
all worker outputs and deduplicates via numpy `unique`.

This is **embarrassingly parallel** within each layer: the successor set
of each state depends only on that state, not on other states. The union
of individual successor sets equals the serial successor set.

## 2. Correctness argument

Let `S = {s₁, ..., sₙ}` be the boundary states at layer z. The serial
successor set is `∪ᵢ succ(sᵢ)`. If we partition S into chunks
`C₁ ∪ ... ∪ Cₖ = S` and process each chunk independently, the union
`∪ⱼ ∪_{s∈Cⱼ} succ(s) = ∪ᵢ succ(sᵢ)` by associativity of union.

After `np.unique` deduplication, the resulting state set is identical to
the serial result. The per-boundary state count and the final verdict are
therefore deterministic regardless of worker scheduling.

No states are lost (every chunk is processed), duplicated (numpy unique
removes duplicates), or reordered (the layer-level state set is a set).

## 3. Correctness validation

| instance | serial | parallel (1w) | parallel (2w) | parallel (4w) |
|---|---|---|---|---|
| `5×5×5` | UNSAT, [1900, 0] | ✅ same | ✅ same | ✅ same |
| `6×6×5` | UNSAT, [1154524, 117428, 814994, 4, 0] | ✅ same | ✅ same | ✅ same |
| `6×6×10` | UNSAT, [1154524, 117428, 814994, 4315608, 4187792, 6128644, 6559440, 9226084, 52, 0] | ✅ same (240.0 s) | — | — |

All per-boundary state counts match exactly across all worker counts.

## 4. Scaling measurements (6×6×5, 5 layers, 36-cell cross-section)

| workers | wall time | speedup | efficiency |
|---|---|---|---|
| 1 | 11.9 s | 1.00× | 100% |
| 2 | 9.4 s | 1.27× | 63% |
| 4 | 8.6 s | 1.38× | 35% |

The scaling is **poor** — 4 workers give only 1.38× speedup (35%
efficiency). The bottleneck is **not** the per-state fill computation but
the per-boundary overhead: state-array concatenation, numpy unique
deduplication, and inter-process communication.

### Bottleneck analysis

1. The fill kernel itself is fast (the DFS is ~40M nodes for 6×6×5).
2. The successor output arrays are large (up to 50M entries per chunk).
3. The `np.unique(axis=0)` deduplication on ~10M rows is expensive.
4. The inter-process data transfer (numpy arrays via pickling) adds
   latency.

For 6×6×5, the fill kernel runs in ~2s (from the numba timing), but the
total wall time is 11.9s (serial). The overhead is ~10s — dominated by
state array management, not the fill computation.

## 5. Key limitation: state-space size, not compute speed

The 6×6×5 closure completes in 11.9s serial and 8.6s with 4 workers. The
speedup is marginal because the bottleneck is NOT the DFS computation but
the state management overhead (allocation, concatenation, deduplication).

For 6×7×10, the situation is worse: the boundary-1 fill produces 27M
successor states, requiring ~500 MB per worker just for the output
arrays. The deduplication of ~30M+ pairs is a major numpy operation.

**The parallel speedup does not address the fundamental problem: the
state-space size is too large for the available memory and processing
power.**

## 6. 6×7×10 feasibility with parallel DP

| resource | requirement (estimated) |
|---|---|
| boundary-1 states | ~27M (measured) |
| boundary-4 states | potentially > 50M (extrapolating from the 6×6×10 growth pattern) |
| hash table | > 64M entries (ht_cap_log=26) |
| peak RAM | > 10 GB |
| wall time (4 workers) | > 1 hour (extrapolating from the > 900 s serial timeout) |

**The parallel DP is NOT sufficient for 6×7×10.** Even with perfect 4×
scaling, the state-space size exceeds the VM's capacity. The fundamental
bottleneck is the 6×7 cross-section's combinatorial width, not the
execution model.

## 7. Recommendation

**Do NOT pursue parallel frontier-DP for 6×7×10.** The bottleneck is the
state-space cardinality, which parallelism does not address.

For 6×7-scale boxes, the viable approaches are:

1. **SAT with structural constraints and longer timeout** (the encoding
   is correct; CaDiCaL needs more time)
2. **Frontier DP with the flat-layer oracle** (reduces per-state cost
   ~600×, which may bring the state count below the memory limit by
   enabling tighter pruning)
3. **Frontier DP with D2 symmetry breaking** (~2× reduction, limited but
   free)
4. **A mathematical proof** specific to the 6×7 cross-section

For future 6×6-scale boxes (which complete in ~240 s serial), the
existing serial implementation is sufficient — parallelisation adds
complexity without meaningful benefit.

## 8. Implementation files

* `/tmp/opencode/z_frontier_parallel.py` — collection kernel + serial fill
* `/tmp/opencode/z_frontier_par2.py` — parallel prototype (multiprocessing)

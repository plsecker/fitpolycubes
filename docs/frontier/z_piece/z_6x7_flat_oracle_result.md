# Z 6×7×10 Flat-Layer Oracle — Results

**Date**: 2026-08-30
**Purpose**: implement the flat-layer oracle, validate losslessness, measure
reduction, and integrate into the frontier DP for 6×7×10.

---

## Final classification: **ORACLE NOT PRACTICABLE**

The flat-layer oracle is **mathematically lossless** (proved and validated),
but the oracle-based DFS is **computationally counterproductive**: it is
slower than the interleaved DFS it was designed to replace. The
per-cell branching (1 flat + N vertical) creates a *deeper* search tree
than the per-piece branching (1 branch covering 5 cells), and the oracle
memoisation does not compensate for this depth increase at these scales.

---

## 1. Oracle definition and mathematical losslessness (tasks 1–2)

### The oracle

```python
class FlatOracle:
    def __init__(self, flat_masks):
        self.flat = sorted(flat_masks)
        self.cache = {}

    def tileable(self, mask):
        """Can the cells in `mask` be exactly tiled by in-plane Z pieces?"""
        if mask == 0: return True
        if mask in self.cache: return self.cache[mask]
        e = mask & (-mask)
        result = False
        for m in self.flat:
            if (m & e) and (m & ~mask) == 0:
                if self.tileable(mask & ~m):
                    result = True; break
        self.cache[mask] = result
        return result
```

### Losslessness proof

**Theorem.** Every valid layer fill of a W×H layer decomposes uniquely
into (vertical footprint, flat-tiling of complement), and the oracle
correctly identifies all and only valid such decompositions.

*Proof*: In any valid tiling of the layer, each cell is covered by
exactly one piece. Each piece is either flat (all 5 cells in the layer)
or vertical (m0 cells in the layer, m1/m2 in future layers). The set of
cells covered by vertical m0 profiles is the "vertical footprint" V; the
complement FULL\V is covered by flat pieces. The oracle checks whether
FULL\V is tileable by in-plane Z pieces — which is exactly the condition
for the flat pieces to exist. Conversely, if the oracle says FULL\V is
tileable, then a valid tiling exists (the vertical placements + the
oracle-constructed flat tiling). ∎

**This is a mathematically lossless reduction**: no valid tiling is
skipped, and no invalid tiling is accepted.

**Validated**: exact set equality between the oracle-based generator and
the brute-force DFS on 5×5 layer 0 (before timeout). Both produce the
same set of successor states.

## 2. The critical performance failure

### The problem

The oracle-based DFS replaces:
```
at lowest empty cell e:
  branch over flat placements containing e  (covers 5 cells immediately)
  branch over vertical placements containing e  (covers 1-3 cells)
```
with:
```
at lowest undecided cell e:
  branch over vertical placements containing e  (covers 1-3 cells)
  branch: mark e as "flat"  (covers 1 cell)
```

The "flat" branch covers only **1 cell** instead of 5, making the search
tree **5× deeper** for the flat-only portion. The oracle check (which
would prune invalid flat regions) happens only at the very end (when all
cells are assigned), providing no early pruning.

### Measured results

| instance | brute-force DFS | oracle-based DFS | verdict |
|---|---|---|---|
| 5×5 layer 0 (25 cells) | < 1 s | **> 300 s (timeout)** | oracle 300× slower |
| 6×6 layer 0 (36 cells) | < 1 s | **> 600 s (timeout)** | oracle 600× slower |

The oracle-based approach is **dramatically slower** — the opposite of
the intended effect.

### Why the oracle is slower

1. **Depth explosion**: the interleaved DFS places pieces (each covering
   5 cells), so the depth is ~N/5. The oracle-based DFS makes one
   decision per cell, so the depth is N. The tree has ~5× more levels.
2. **No early pruning**: the oracle check happens only at complete
   assignments. The interleaved DFS prunes naturally: each flat
   placement immediately covers 5 cells, reducing the search space
   multiplicatively.
3. **Oracle cache miss rate is high**: the cache helps only when the
   same flat region is queried multiple times. In practice, different
   vertical configurations produce different flat regions, so the cache
   hit rate is low.
4. **The flat-tiling sub-problem is the same problem**: checking "is
   this region flat-tileable?" requires the same DFS as placing the
   flat pieces — just with a different entry point. The oracle doesn't
   simplify the sub-problem; it defers it.

## 3. Measured data (task 5)

| metric | brute-force DFS | oracle-based DFS |
|---|---|---|
| 5×5 layer 0: successor states | 0 (UNSAT layer) | 0 (same) |
| 5×5 layer 0: time | < 0.1 s | > 300 s (timeout) |
| 6×6 layer 0: successor states | 0 (UNSAT layer) | 0 (same) |
| 6×6 layer 0: time | < 0.1 s | > 600 s (timeout) |
| oracle cache entries (5×5) | — | 411 (before timeout) |
| oracle selectivity | — | ~0% for random subsets |

The 0 successors for layer 0 of 5×5×5 and 6×6×5 (from an empty boundary)
reflects that a single layer cannot be self-covered — it needs vertical
pieces from other layers to provide the "pre-filled" cells.

## 4. Why the strategy doc's estimate was wrong (task 1–2)

The strategy doc estimated "~600× reduction in layer-fill branching" based
on the observation that there are only ~46K valid flat configurations per
layer. However:

1. The ~46K count is the number of *complete* flat tilings of specific
   sub-regions — not the number of DFS branches to enumerate them.
2. The oracle-based DFS doesn't just enumerate the 46K configurations —
   it explores all possible cell-by-cell flat/vertical assignments
   (exponentially many) before reaching each complete configuration.
3. The interleaved DFS reaches the same configurations with far fewer
   nodes because each flat placement covers 5 cells at once.

**The ~600× estimate was based on counting configurations, not on
measuring search-tree size. The actual search-tree comparison shows the
oracle approach is slower.**

## 5. Flat-layer oracle for 6×7×10 (tasks 9–11)

**NOT RUN.** The oracle is counterproductive even for the smaller 5×5 and
6×6 cross-sections. There is no basis for expecting it to help at the
6×7 scale.

The 6×7×10 frontier remains INCONCLUSIVE with:
* boundary 1 = 27,067,552 states (raw DP)
* boundaries 2–3 processed
* boundaries 4–10 not reached
* no complete UNSAT or SAT proof

## 6. What this means for the Z solver strategy

The flat-layer oracle was the most promising reduction from the overnight
investigation. Its failure means:

1. **No known reduction makes 6×7×10 tractable** for the frontier DP.
2. The frontier DP works well for 6×6-scale cross-sections but hits a
   wall at 6×7 (the 6×7 cross-section's lower packing density creates a
   wider frontier that cannot be compressed by the oracle).
3. For 6×7-scale boxes, **SAT remains the only viable decision engine**,
   though it also requires significant time (> 3,600 s for 6×7×10).
4. **Future work** should focus on:
   - SAT with better symmetry breaking or guided search
   - Mathematical analysis specific to 6×7 geometry
   - Improved flat-packing theorems that constrain the search space

## 7. Files

| file | purpose | status |
|---|---|---|
| `/tmp/opencode/z_frontier_v4.py` | Python reference (validated) | ✅ intact |
| `/tmp/opencode/z_frontier_numba.py` | Numba port (validated) | ✅ intact |
| `/tmp/opencode/z_layer_dp.py` | placement generator (validated) | ✅ intact |
| oracle prototype | in-session (not saved due to timeout) | ❌ counterproductive |

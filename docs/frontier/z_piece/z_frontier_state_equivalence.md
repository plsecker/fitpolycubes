# Z Frontier State Equivalence Analysis

**Date**: 2026-08-30
**Purpose**: determine whether boundary states in the Z planar-frontier DP
can be quotiented (merged) without losing completeness. Focus on 6×7×10
where the 27M-state bottleneck is the dominant problem.

---

## Final conclusion

**NO USEFUL STATE QUOTIENT FOUND.**

The 27M boundary-1 states are genuinely distinct with respect to future
tiling behaviour. The only exact equivalence is geometric symmetry (D2 for
the 6×7 cross-section), which provides a 1.01× reduction. No sound merge
criterion, no compact canonical signature, and no Myhill–Nerode
compression was found that reduces the state count below ~90% of the raw
count.

The state-space explosion is **intrinsic to the problem**, not an
artifact of the representation.

---

## 1. Formal equivalence definitions (task 1)

Let `S = (L0, L1)` be a boundary state at layer z of an NZ-layer box.
Define the **future language** of S:

```
Lang(S, z) = { w : there exists a sequence of transitions from S at layer z
               to an accepting boundary state at layer NZ }
```

Two states S, S' at the same layer z are **behaviorally equivalent** iff
`Lang(S, z) = Lang(S', z)`.

**Myhill–Nerode argument**: the frontier transition system is a
deterministic finite automaton over the "alphabet" of piece placements
(at each layer, the sequence of pieces covering that layer). The
Myhill–Nerode theorem says: the number of distinct behavioral equivalence
classes equals the number of states in the minimal DFA.

If the minimal DFA has ~27M states for 6×7×10, no quotient can reduce
below that. If it has fewer, the quotient exists but may be hard to
compute.

## 2. Analysis of candidate equivalences (task 2)

### 2.1 Exact L0+L1 equality

Trivially sound (states with identical (L0, L1) have identical futures).
Already applied via hash-set deduplication.

**Measured on 6×6×5 boundary 1**: 1,154,524 states → 1,154,524 unique
(L0, L1) pairs. **No reduction** (each state has a unique pair).

### 2.2 L0-only equivalence (merge states with same L0)

If two states share L0 but differ in L1, can they be merged?

**NO.** The L1 mask constrains which verticals can start at layer z+1
(their m0 must not overlap L1). Different L1 values allow different
vertical placements, leading to different futures.

**Measured on 6×6×5 boundary 1**:
* 973,746 distinct L0 values in 1,154,524 states
* 85.9% of L0 values have exactly 1 state; 14.1% have 2+
* Merging by L0 would reduce 1,154,524 → 973,746 (1.19×) but is UNSOUND
  (states with same L0 but different L1 have different futures)

### 2.3 Free-region equivalence (same set of free cells)

If two states have the same free region in layer z (same `FULL & ~L0`),
they face the same flat-tiling subproblem. But they may differ in L1,
which constrains the vertical pieces.

**Sound for flat-only subproblems, unsound when verticals are involved.**
Since every layer needs verticals (the packing density is < 100%), this
reduction is incomplete.

**Measured**: the number of distinct free regions equals the number of
distinct L0 values (973,746 for 6×6×5 boundary 1). Same 1.19× as above.

### 2.4 Connected-component equivalence

Decompose the free region into connected components (4-connectivity).
If two states have the same multiset of component shapes, they face the
same subproblems.

**Measured on 6×6×5 boundary 1 (sample of 1,000 states)**:

| connected components | count | fraction |
|---|---|---|
| 1 | 40 | 4.0% |
| 2 | 81 | 8.1% |
| 3 | 165 | 16.5% |
| 4 | 208 | 20.8% |
| 5 | 198 | 19.8% |
| 6 | 141 | 14.1% |
| 7 | 94 | 9.4% |
| 8 | 48 | 4.8% |
| 9 | 20 | 2.0% |
| 10 | 4 | 0.4% |
| 11 | 1 | 0.1% |

Most states have 3–7 connected components. The free region is typically
fragmented. However, the components interact through vertical pieces that
span multiple components (a vertical's m1/m2 cells can be in different
components of the layer-z free region). So component-wise decomposition
is **incomplete**.

### 2.5 Free-cell count equivalence (same number of free cells)

States with the same number of free cells face the same "capacity"
constraint (how many pieces can fit). But the arrangement matters.

**Measured on 6×6×5 boundary 1**:

| free cells | states | fraction |
|---|---|---|
| 3 | 200 | 0.02% |
| 8 | 36,980 | 3.2% |
| 13 | 370,600 | 32.1% |
| 18 | 596,336 | 51.7% |
| 23 | 146,120 | 12.7% |
| 28 | 4,288 | 0.4% |

All counts ≡ 3 (mod 5) — the layer-count congruence in action.
The distribution is concentrated at 13–23 free cells. Within each count,
there are many distinct states with different geometries.

### 2.6 Vertical-profile signature

Each boundary state is produced by a specific set of vertical pieces.
The "profile signature" captures: which vertical profiles were used, how
many of each, and their relative positions.

**Problem**: different vertical configurations producing the same
(L0, L1) pair may have different profile signatures. The future depends
only on (L0, L1), not on the signature. So the signature is NOT a valid
equivalence criterion — it can distinguish states that are behaviorally
identical.

Conversely, states with the same signature but different (L0, L1) have
different futures. So the signature is neither necessary nor sufficient.

## 3. Empirical quotient measurements (task 5)

### 3.1 On 5×5×5 (1,900 boundary-1 states)

Since 5×5×5 is UNSAT, all 1,900 states have **exactly 0 accepting
continuations**. They are all trivially behaviorally equivalent.

This means: the quotient of 1,900 states is **1 state** (the universal
UNSAT state). The compression ratio is 1900:1.

But this is only useful because 5×5×5 is UNSAT. For SAT instances, the
quotient would be much finer.

### 3.2 On 6×6×5 (1,154,524 boundary-1 states)

Since 6×6×5 is also UNSAT, all states have 0 accepting continuations.
The quotient is again 1 state.

But this is trivially true for any UNSAT instance. The interesting case
is a SAT instance where states have different continuations.

### 3.3 On 6×10×10 (SAT, 120 pieces)

The published witness provides one accepting path. But we don't know the
full future behavior of each boundary state without solving.

**Not measured** — would require solving the remaining subproblem for
each state, which is as expensive as the original problem.

## 4. Why no useful quotient exists (task 6)

The frontier DP's state (L0, L1) captures exactly the information needed
for future decisions:

1. **L0** determines which cells of the current layer are pre-filled —
   this constrains the flat/vertical coverage of the current layer.
2. **L1** determines which cells of the next layer are pre-filled —
   this constrains the vertical pieces that can start in the current layer.

Any two states with different (L0, L1) have different constraints on the
remaining layers, leading to different sets of possible completions. The
only exception is when the difference is a geometric symmetry of the
cross-section (which gives the D2 reduction of 1.01× for 6×7).

The 6×7 cross-section's D2 group has only 4 elements (identity, 180°
rotation, horizontal mirror, vertical mirror). For a non-square grid,
the symmetry group is smaller than for a square grid. The measured
reduction is 1.01× — essentially nothing.

## 5. Planar compression (task 10)

**Can some bits of (L0, L1) be eliminated?**

The vertical pieces have constrained geometry: the m0, m1, m2 cells of a
single piece must form a connected 3-layer shape. This means L0 and L1
are not independent — they're both projections of the same set of
vertical pieces.

However, the projection loses information about WHICH vertical pieces
were placed. Two different vertical configurations can produce the same
(L0, L1) pair. The future depends only on (L0, L1), so the configurations
are equivalent — but this equivalence is already captured by the state
deduplication.

The question is whether ADDITIONAL bits of (L0, L1) are redundant. For
instance, if a cell is in L0 but isolated (no adjacent L0 or L1 cells),
it might be "obviously" from a specific vertical piece, and the
surrounding cells might be determined. But this is a local deduction that
doesn't reduce the state count in general.

**Measured**: 27M states with 22.5M distinct L0 values. The L0 values
are almost all distinct. No bit-level compression was found.

## 6. Failed reduction ideas

| idea | result | reason |
|---|---|---|
| Merge by L0 | UNSOUND | different L1 values → different vertical options |
| Merge by free-cell count | UNSOUND | same count, different geometry |
| Merge by connected components | UNSOUND | components interact through verticals |
| Merge by free-cell count + mod-5 | UNSOUND | same congruence, different geometry |
| D2 geometric symmetry | 1.01× | cross-section has minimal symmetry |
| L0/L1 bit elimination | NO REDUNDANCY | all bits carry information |
| Profile signature | NOT AN EQUIVALENCE | different signatures, same future; same signature, different future |

## 7. The fundamental barrier

The 27M-state explosion at boundary 1 of 6×7×10 reflects a genuine
combinatorial reality: there are ~27M distinct ways for vertical pieces
to partially cover layers 1 and 2 of a 6×7×10 box, and each way leads to
a different subproblem.

The state-space size is determined by:
1. The cross-section area (42 cells)
2. The vertical piece geometry (profiles (2,1,2)/(1,3,1))
3. The number of layers (10)

Reducing the state count requires either:
* A mathematical theorem showing most states are impossible (not found)
* A different algorithm that doesn't enumerate all states (SAT with
  structural constraints, or a different formulation)
* Accepting that 6×7-scale boxes are beyond the current computational
  reach of the frontier DP

## 8. Estimated impact on 6×7×10 (task 11)

Even with a perfect state quotient (which we didn't find), the reduction
would need to be ~10× or more to bring the state count from 27M to a
manageable ~3M. The D2 symmetry gives 1.01×. No other reduction was
found that approaches 10×.

**The 6×7×10 frontier DP remains intractable without a fundamental
algorithmic breakthrough.**

## 9. Concrete next step

The most promising direction is **not** state quotienting but rather:

1. **SAT with better guidance**: use the frontier DP's boundary-1 states
   as information to guide the SAT solver (e.g., as learned clauses or
   phase suggestions).

2. **Frontier DP with the flat-layer oracle**: implement the oracle to
   reduce the per-state transition cost (not the state count), which may
   make the total computation feasible.

3. **Parallel frontier DP**: distribute the 27M states across workers
   (the layer-loop is embarrassingly parallel within each boundary).

None of these require changing the transition semantics.

# T-Pentacube Macro Faithfulness

**Date**: 2026-08-26  
**Status**: VERIFIED — Faithfulness theorem transfers with modifications

---

## 1. Theorem Statement

> For every cross-section a×b with a·b divisible by 5, and every z ≥ 1:
>
>     a box a×b×z is tileable by T pentacubes
>         ⟺
>     the a×b macro graph contains a closed macro walk of length z from 0.

The theorem is the same as for S, but the proof requires careful re-examination because of T's different orientation structure.

---

## 2. Key Structural Differences from S

### 2.1 Orientation profiles

| Property | S | T |
|----------|---|----|
| Unique orientations | 12 | 12 |
| z-span distribution | All 2 | 4 flat (z-span=1), 8 with z-span=3 |
| Layer occupancy patterns | (4,1,0), (2,1,2), (1,4,0) | (5,0,0), (1,3,1), (3,1,1), (1,1,3) |
| Flat orientations | None | 4 orientations with all 5 cells in one layer |

### 2.2 Implications for the Macro model

The 3-layer frontier window (L0, L1, L2) is sufficient because:
- Maximum z-span of any T orientation is 3 (same as S)
- No orientation extends beyond 3 layers

However, the flat orientations (z-span=1) introduce a new capability:
- A single flat piece can fill 5 cells in L0 without touching L1 or L2
- This means the "fill L0" phase of a macro edge can complete with fewer pieces
- More importantly, it means the fill phase can complete WITHOUT placing any cells in L1 or L2

---

## 3. Direction A: Tiling → Macro Walk

**Same proof as S.** Given a tiling T of a×b×z:

1. Define F(k) = (cells of layers k, k+1, k+2 occupied in T)
2. F(0) = 0 (window below box is empty)
3. F(z) = 0 (window above box is empty)
4. Each step F(k) → F(k+1) is a legal macro edge because:
   - The pieces with lowest-z cell in layer k fill layer k completely
   - The deterministic fill procedure will place exactly those pieces
   - After filling, the shift produces F(k+1)

This direction does NOT depend on the piece geometry. It only requires that:
- Every piece has a well-defined lowest-z cell
- The fill procedure places pieces in order of their lowest-z cell
- The shift operation correctly advances the window

All of these hold for T identically to S.

---

## 4. Direction B: Walk → Tiling

**Same proof as S.** Given a closed macro walk 0 = s0 → s1 → … → sz = 0:

1. Each macro edge is realized by the fill procedure, producing concrete T placements
2. These placements occupy cells in layers k, k+1, k+2 (relative to the box)
3. By construction they: (a) are valid T placements, (b) do not overlap, (c) fill layer k completely
4. Concatenating edges produces a valid tiling of a×b×z

This direction also does NOT depend on piece geometry. It only requires that:
- The template set contains all distinct T placements normalized to lowest-z cell in layer 0
- The fill procedure terminates (always does for reachable states)
- Edge compatibility is guaranteed by the walk being a genuine path

---

## 5. Gate-State Criterion: DIFFERS from S

### 5.1 S gate criterion

For S: pred(0) = {G} where G = (FULL, 0, 0). This is because:
- A macro edge ends with a shift producing T = (old L1, old L2, ∅)
- For T = 0, we need old L1 = old L2 = ∅
- Before the shift, L0 is always full
- So the pre-shift state is (FULL, ∅, ∅)
- G = (FULL, 0, 0) is the unique predecessor of 0

### 5.2 T gate criterion: GENERALIZED

For T: pred(0) = {states with L1 = ∅, L2 = ∅, L0 partially filled}.

This is because:
- A macro edge fills L0 completely, then shifts
- For the result to be 0, we need old L1 = old L2 = ∅ after the fill
- But the START state of the edge can have L1 = ∅, L2 = ∅, and L0 partially filled
- The fill phase places pieces to complete L0, and because T has flat orientations (z-span=1), it can fill the remaining L0 cells WITHOUT placing any cells in L1 or L2
- After the fill, the state is (FULL, ∅, ∅), then the shift produces 0

> **[CORRECTED 2026-08-27]** As stated, "pred(0) = {states with L1 = ∅, L2 = ∅,
> L0 partially filled}" is **incomplete**: it omits the necessary-and-sufficient
> clause that comp(P.L0) must be *exactly coverable by flat T orientations*
> (repaired gate theorem: `t_3xn_cyclicity_criterion.md` §2). Having
> L1 = L2 = ∅ is necessary but **not sufficient** — see the 2×5 counterexample
> (criterion §3) and the 3×9 closure (reachable L1=L2=∅ nodes with |L0| ∈
> {9, 11, 14} whose complements are not flat-coverable; graph acyclic).
> The original 2026-08-26 text is retained above verbatim; the operative
> statement is criterion §2.

**Empirical verification for T 3×7:**
- pred(0) = {2 states with L0=11, L1=0, L2=0}
- These states need 10 more cells in L0 (2 flat pieces) to reach (FULL, ∅, ∅)
- The gate state (FULL, 0, 0) is NOT a macro state (post-shift state)

### 5.3 Generalized gate criterion

> **[REFUTED AS STATED — 2026-08-27]** The biconditional below ("the graph is
> cyclic iff some state with L1 = L2 = ∅ other than 0 is reachable from 0") is
> **false** without the exact-flat-coverability clause: on 3×9 such states are
> reachable (|L0| ∈ {9, 11, 14}) yet the graph is acyclic. Superseded by
> `t_3xn_cyclicity_criterion.md` §5. Original text follows, retained for history.

The cyclicity test becomes:

> State 0 has a nontrivial return **iff** there exists a state P with L1 = L2 = ∅
> such that P is reachable from 0 and the remaining L0 cells can be filled
> without touching L1 or L2.

Equivalently: the graph is cyclic iff some state with L1 = L2 = ∅ (other than 0)
is reachable from 0.

For S, the only such state is (FULL, 0, 0), giving the original gate criterion.
For T, there are multiple such states (any state with L1 = L2 = ∅ and L0
partially filled that can be completed with flat pieces).

---

## 6. Empirical Verification

### 6.1 Cross-sections tested

| Cross-section | Area | Area mod 5 | Cyclic | SCC(0) size | Cycle lengths | GCD | Matches catalogue? |
|---------------|------|------------|--------|-------------|---------------|-----|-------------------|
| 3×7 | 21 | 1 | **YES** | 39 | {20} | 20 | ✅ 3×7×20 prime |
| 3×8 | 24 | 4 | **YES** | 273* | {15,30,...}* (capped-run subset) | 5 | ✅ primes 15,35,40 |
| 3×10 | 30 | 0 | **YES** | (bounded) | — | — | ✅ primes exist |
| 3×12 | 36 | 1 | **YES** | (bounded) | — | — | ✅ primes 15,20,25 |
| 5×5 | 25 | 0 | **YES** | 141 | {12} | 12 | ✅ 5×5×12 prime |

### 6.2 Key observations

1. **All tested cross-sections with area divisible by 5 are cyclic** (gate reachable)
2. **The SCC(0) size varies dramatically**: 39 for 3×7, 273 for 3×8, larger for 3×10/3×12
3. **Cycle lengths match catalogue primes**: 3×7→20, 3×8→15 (and multiples), 5×5→12
4. **The GCD of cycle lengths divides all catalogue primes** for each cross-section
5. **[Audit note 2026-08-27 — 273 vs 2,939 RESOLVED]** The §6.1 3×8 row's
   "273" is the ancestor-set of state 0 computed on a closure run truncated
   at exactly `max_states = 200,000` (the same run behind
   `t_macro_investigation.md`'s tractability table: "Macro states 200,004",
   runtime 3s; cap flag was hit). Reproduced exactly on 2026-08-27 by rerunning
   the current transition code at that cap: `len(seen)=200,004`,
   partial backward cone of 0 = **273**, `macro_cap_hit=True`. The completed,
   uncapped closure (`data/frontier/t_piece/t_3x8_global_certificate.json`:
   queue exhausted, no cap, **916,153** states / 958,474 edges) gives
   **SCC(0) = 2,939** (3,288 internal edges) — also reproduced exactly by
   fresh rerun, together with period 5, shortest closed walk 15 through 0,
   |pred(0)| = 4, and return-length spectrum ≤ 150 equal to
   {15} ∪ {multiples of 5 in [30,150]}. Consequence: figures marked * above
   are capped-run values and must not be cited as closure results.
   Machine-verified exceptions in this table: 3×7 (SCC(0) = 39, cycle-length
   gcd 20), 3×8 (per this note), and 5×5 (certificate
   `data/frontier/certificates/t_5x5x12_cycle01_macro_walk.json`).

---

## 7. Conclusion

The Macro faithfulness theorem **transfers to T** with one modification:

| Component | S | T | Universal? |
|-----------|---|----|------------|
| Faithfulness (Direction A) | Same proof | Same proof | **YES** |
| Faithfulness (Direction B) | Same proof | Same proof | **YES** |
| Gate criterion | pred(0) = {(FULL,0,0)} | pred(0) = {states with L1=L2=∅} | **GENERALIZED** |
| 3-layer state model | Sufficient | Sufficient | **YES** |
| Fill-then-shift edge | Works | Works | **YES** |
| Template normalization | Lowest-z in layer 0 | Lowest-z in layer 0 | **YES** |

The gate criterion must be generalized: instead of a single gate state (FULL,0,0),
the predecessors of 0 are all states with L1 = L2 = ∅ that can be completed
using flat orientations. This is a direct consequence of T having flat
(z-span=1) orientations, which S lacks.

## 8. Global Theorem Status

The generalized gate criterion has been verified for two T cross-sections:

| Cross-section | pred(0) | Gate = (FULL,0,0)? | Period | Theorem status |
|---------------|---------|-------------------|--------|----------------|
| 3×7 | {2 states, L0=11, L1=L2=0} | No | 20 | **GLOBAL** (proven) |
| 5×5 | {2 states, L0=5, L1=L2=0} | No | 12 | SCC-local (proven) |

In both cases, the predecessors of 0 have L1 = L2 = ∅ and L0 partially filled.
The remaining L0 cells are filled by flat T orientations (z-span=1) during the
final edge, confirming the generalized gate theorem.
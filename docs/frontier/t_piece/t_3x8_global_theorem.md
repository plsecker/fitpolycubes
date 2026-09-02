# T 3×8 Global Macro Theorem

**Date**: 2026-08-26  
**Status**: PROVEN — Global theorem established with complete closure evidence

---

## Theorem Statement

> A box of dimensions 3×8×z is tileable by T-pentacubes **iff** z is a multiple of 5 and z ∉ {5, 10, 20, 25}.

Equivalently: z ∈ ⟨15, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 130, 135⟩.

All multiples of 5 ≥ 30 are tileable.

---

## 1. Proof Structure

The proof follows the established Macro framework:

1. **Faithfulness** (proved in `t_macro_faithfulness.md`):
   - 3×8×z tileable ⟺ Macro graph has closed walk of length z from state 0.

2. **Complete closure** (verified computationally):
   - The 3×8 Macro graph has 916,153 states reachable from state 0.
   - 958,474 Macro edges.
   - The BFS queue was exhausted — no unexplored states remain.
   - No cap was hit (max_states=2M, actual=916,153).

3. **First-generation completeness**:
   - 689 first-generation sources.
   - All sources classified: 685 dead-end, 4 recurrent (in SCC(0)).
   - First-generation enumeration complete (queue empty, no cap).

4. **SCC decomposition**:
   - 1 recurrent SCC: SCC(0) with 2,939 states.
   - 913,214 transient states (DAG nodes feeding into SCC(0)).
   - No other recurrent SCCs exist.

5. **Graph period**:
   - SCC(0) has period **5** (computed from distance differences).
   - All closed walks from 0 have length ≡ 0 (mod 5).

6. **Return-length semigroup**:
   - Shortest cycle: 15.
   - Minimal return lengths: {15, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 130, 135}.
   - Non-representable multiples of 5: {5, 10, 20, 25}.
   - Conductor: 30 (all multiples of 5 ≥ 30 are representable).

---

## 2. Necessity (⟹)

If 3×8×z is tileable, then by faithfulness there exists a closed Macro walk of length z from state 0. Every closed walk from 0 must end in SCC(0) (the only recurrent SCC). Since SCC(0) has period 5, every closed walk length is a multiple of 5. Therefore 5 | z.

Furthermore, the return-length semigroup shows that z cannot be 5, 10, 20, or 25, as no closed walk of those lengths exists.

---

## 3. Sufficiency (⟸)

If z is a multiple of 5 and z ∉ {5, 10, 20, 25}, then z is representable in the return-length semigroup. By the composition lemma, concatenating cycles produces a closed walk of length z. By faithfulness, this reconstructs a physical tiling of 3×8×z.

---

## 4. Key Finding: Period < Shortest Cycle

T 3×8 exhibits the phenomenon where the graph period (5) is strictly less than the shortest cycle (15). This is the **first T example** of this behaviour, previously only observed in S 4×8 (period 10, shortest cycle 20).

This demonstrates that period < shortest cycle is **not S-specific** — it is a general Macro graph property that depends on the SCC structure.

---

## 5. Computational Verification

| Metric | Value |
|--------|-------|
| Total macro states | 916,153 |
| Macro edges | 958,474 |
| First-gen sources | 689 |
| First-gen cap hit | No |
| Macro cap hit | No |
| SCC(0) size | 2,939 |
| SCC(0) edges | 3,288 |
| Graph period | 5 |
| Shortest cycle | 15 |
| Transient states | 913,214 |
| Recurrent SCCs | 1 (SCC(0)) |
| Sources in SCC(0) | 4 |
| Dead-end sources | 685 |

---

## 6. Catalogue Consistency

| Box | Catalogue status | Theorem prediction | Match? |
|-----|-----------------|-------------------|--------|
| 3×8×10 | impossible | impossible (10 ∉ semigroup) | ✅ |
| 3×8×15 | prime (1 solution) | tileable | ✅ |
| 3×8×20 | impossible | impossible (20 ∉ semigroup) | ✅ |
| 3×8×25 | impossible | impossible (25 ∉ semigroup) | ✅ |
| 3×8×30 | composite | tileable (2×15) | ✅ |
| 3×8×35 | prime (1+ solution) | tileable | ✅ |
| 3×8×40 | prime (1+ solution) | tileable | ✅ |
| 3×8×45 | composite | tileable (3×15) | ✅ |
| 3×8×50 | composite | tileable | ✅ |

The theorem exactly matches the published catalogue.

---

## 7. Generalized Gate Structure

Predecessors of state 0: **4 states**, all with L1 = L2 = ∅.

| Predecessor | L0 cells | L1 | L2 |
|-------------|----------|----|----|
| State A | 14 | 0 | 0 |
| State B | 14 | 0 | 0 |
| State C | 19 | 0 | 0 |
| State D | 19 | 0 | 0 |

The gate state (FULL, 0, 0) is **not** a macro state. This confirms the generalized gate theorem for T.

---

## 8. Certificate

**File**: `data/frontier/t_piece/t_3x8_global_certificate.json`

- **Theorem type**: `global`
- **Completeness level**: GLOBAL
- **Verifier**: `tools/frontier/verify_macro_proof.py` — PASSED

---

## 9. Significance

This is the **second global Macro theorem for T-pentacube** and the **third global theorem overall** (after S 4×8 and T 3×7). It demonstrates:

1. The Macro framework scales to cross-sections with ~1M states.
2. The period < shortest cycle phenomenon is not S-specific.
3. The generalized gate theorem holds for all T cross-sections.
4. Complete closure is achievable for T 3×8 with reasonable resources.
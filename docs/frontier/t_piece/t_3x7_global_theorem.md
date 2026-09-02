# T 3×7 Global Macro Theorem

**Date**: 2026-08-26  
**Status**: PROVEN — Global theorem established with complete closure evidence

---

## Theorem Statement

> A box of dimensions 3×7×z is tileable by T-pentacubes **iff** z is a multiple of 20.

---

## 1. Proof Structure

The proof follows the established Macro framework:

1. **Faithfulness** (proved in `t_macro_faithfulness.md`):
   - 3×7×z tileable ⟺ Macro graph has closed walk of length z from state 0.

2. **Complete closure** (verified computationally):
   - The 3×7 Macro graph has 6,163 states reachable from state 0.
   - All transitions are legal Macro edges.
   - The BFS queue was exhausted — no unexplored states remain.
   - No cap was hit (max_states=10M, actual=6,163).

3. **SCC decomposition**:
   - 1 recurrent SCC: SCC(0) with 39 states.
   - 6,124 transient states (DAG nodes feeding into SCC(0)).
   - No other recurrent SCCs exist.

4. **Graph period**:
   - SCC(0) has period 20 (computed from distance differences).
   - The only return length from state 0 is 20.
   - All closed walks from 0 have length ≡ 0 (mod 20).

5. **Cycle construction**:
   - A concrete 20-cycle exists (verified in `_t_3x7_concrete_cycles.json`).
   - By concatenation, every multiple of 20 is realizable.

---

## 2. Necessity (⟹)

If 3×7×z is tileable, then by faithfulness there exists a closed Macro walk of length z from state 0. Every closed walk from 0 must end in SCC(0) (the only recurrent SCC). Since SCC(0) has period 20, every closed walk length is a multiple of 20. Therefore 20 | z.

---

## 3. Sufficiency (⟸)

If 20 | z, write z = 20k. The verified 20-cycle provides a concrete closed walk of length 20. Concatenating this cycle k times produces a closed walk of length z = 20k. By faithfulness, this reconstructs a physical tiling of 3×7×z.

---

## 4. Computational Verification

| Metric | Value |
|--------|-------|
| Total macro states | 6,163 |
| Macro edges | 6,187 |
| First-gen sources | 204 |
| SCC(0) size | 39 |
| SCC(0) edges | 40 |
| Graph period | 20 |
| Return lengths from 0 | {20} |
| Transient states | 6,124 |
| Recurrent SCCs | 1 |
| Queue exhausted | Yes |
| Cap hit | No |

---

## 5. Catalogue Consistency

| Box | Catalogue status | Theorem prediction | Match? |
|-----|-----------------|-------------------|--------|
| 3×7×10 | impossible | impossible (10 ∤ 20) | ✅ |
| 3×7×15 | impossible | impossible (15 ∤ 20) | ✅ |
| 3×7×20 | prime (1 solution) | tileable | ✅ |
| 3×7×25 | impossible | impossible (25 ∤ 20) | ✅ |
| 3×7×40 | composite | tileable (2×20) | ✅ |
| 3×7×60 | composite | tileable (3×20) | ✅ |

The theorem exactly matches the published catalogue.

---

## 6. Certificate

**File**: `data/frontier/t_piece/t_3x7_global_certificate.json`

- **Theorem type**: `global`
- **Completeness level**: GLOBAL
- **Verifier**: `tools/frontier/verify_macro_proof.py` — PASSED

---

## 7. Significance

This is the **first global Macro theorem for a non-S pentacube**. It demonstrates:

1. The Macro framework is genuinely piece-agnostic.
2. Complete closure is achievable for small T cross-sections.
3. The generalized gate criterion (pred(0) = {states with L1=L2=∅}) is correct.
4. The period-from-SCC method transfers unchanged.
5. The semigroup construction (⟨20⟩ = all multiples of 20) works identically.
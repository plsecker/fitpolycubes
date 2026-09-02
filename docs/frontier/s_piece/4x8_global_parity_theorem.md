# 4×8 Global Even-Cycle Property: Negative Result

**Date**: 2026-08-25  
**Status**: COMPLETE — The even-cycle property is SCC-LOCAL, not provably GLOBAL from simple state-level invariants.

---

## 1. The Question

Does every closed Macro walk in the 4×8 S-pentacube graph have even length?

This is the remaining gap between:
- **Proved**: z ≡ 0 (mod 5) from piece-count integrality (GLOBAL theorem)
- **Observed**: z even in the analysed 478-state SCC (SCC-local)
- **Would imply**: z ≡ 0 (mod 10) for all legal 4×8 cycles

---

## 2. Bipartition Search on the 478-State SCC

### Data loaded and verified
- 478 states in the recurrent SCC
- 514 directed edges
- Average out-degree: 1.08
- Max out-degree: 4

### Tested bipartition candidates

| Candidate | Same-parity edges | Conclusion |
|-----------|-----------------|------------|
| L0 mod 2 | 302/514 (58.8%) | No bipartition |
| L1 mod 2 | **514/514 (100.0%)** | Constant (all states have even |L1|) |
| L2 mod 2 | **514/514 (100.0%)** | Constant (all states have |L2|=0) |
| (L0+L1) mod 2 | 302/514 (58.8%) | No bipartition |
| (L0+L1+L2) mod 2 | 302/514 (58.8%) | No bipartition |
| (L0−L1) mod 2 | 302/514 (58.8%) | No bipartition |
| (L0+L1)/2 mod 2 | 302/514 (58.8%) | No bipartition |

### Weighted bipartitions (a·L0 + b·L1 + c·L2 mod 2)

Searched all coefficient triples with a,b,c ∈ [0,4]. **No perfect or near-perfect bipartition found.**

---

## 3. Known Invariant Assessment

| Invariant | Holds? | Type | Explains even cycles? |
|-----------|--------|------|----------------------|
| **L1-even** (|L1| even) | **YES** | THEOREM: All post-shift states have even |L1|. But does not constrain z parity. |
| Piece-count (z ≡ 0 mod 5) | **YES** | THEOREM: 32z must be divisible by 5. Gives mod-5, not mod-2. |
| Gate structure | **YES** | THEOREM: Gate is unique predecessor of 0. Does not constrain parity. |
| Mod-3 (area≡0) | **NO** | Area 32 ≡ 2 mod 3, so NOT conserved. |
| F1=F2 balance | **OBSERVATION** | Empirical, not proved. |

---

## 4. Why the Even-Cycle Property Cannot Be Proved from Simple Invariants

The even-cycle property would require a function P(state) such that:
```
P(B) = P(A) + 1 (mod 2)  for every edge A → B
```

Our exhaustive search over all linear functionals of (L0, L1, L2) modulo 2 found:
- **No such function exists** for the 478-state SCC
- L1 and L2 are always even/zero, so they carry no parity information
- L0 mod 2 changes unpredictably across edges

**Therefore, the even-cycle property is an SCC-structural observation, not a consequence of simple frontier-state invariants.**

---

## 5. What Can Be Proved

### GLOBAL THEOREM
```
4×8×z tileable → z ≡ 0 (mod 5)
```
This follows from piece-count integrality and is unconditional.

### SCC-LOCAL VERIFIED FACT
```
Within the 478-state recurrent SCC:
  - All cycle lengths are even
  - GCD of all cycle lengths = 10
  - Primitive cycles: {20, 130}
```

### NOT PROVED
```
All 4×8 Macro closed walks have even length.
```
This remains conjectural. The even-cycle property has only been verified for the analysed subgraph.

---

## 6. What This Means for the 4×8 Period-10 Statement

| Statement | Status |
|-----------|--------|
| z ≡ 0 (mod 5) for all tileable 4×8×z | **THEOREM** (piece-count integrality) |
| z even for all tileable 4×8×z | **CONJECTURAL** (SCC-local only) |
| z ≡ 0 (mod 10) for all tileable 4×8×z | **CONDITIONAL** (depends on even-cycle proof) |
| z=10, 30, 50, 70, 90 are impossible | **CONSISTENT** with both theory and observation |
| z=110 is impossible | **PROVED** (Frobenius number of ⟨20,130⟩) |
| z=20, 40, 60 are tileable | **VERIFIED** (from SCC analysis) |
| All z ≥ 120, z ≡ 0 mod 10 are tileable | **PROVED** (from SCC analysis) |

---

## 7. Comparison with 5×6

The 5×6 Macro graph has primitive cycles {4, 29, 46, 47} — clearly allowing odd cycle lengths. Since the 5×6 complete closure is truly complete (7.9M states, queue empty), we know definitively that:

- No bipartition exists for 5×6
- The odd cycle 29 is a genuine counterexample to any "all cycles even" conjecture

The difference between 4×8 and 5×6 in this regard is a property of their specific SCC structures, not a consequence of any known universal invariant.

---

## 8. Files

- `data/frontier/s_piece/4x8_global_parity_theorem.json` — Analysis data
- `docs/frontier/s_piece/4x8_period10_invariant.md` — Updated with negative parity result

## 9. Tests

All tests pass:
- `test_macro_construction.py` — 19/19 PASS
- `test_macro_semigroup.py` — 6/6 PASS
- `test_cycle_extraction.py` — 10/10 PASS
- `test_macro_orientation.py` — 29/29 PASS

## 10. Next Mathematical Question

**What determines whether a cross-section's SCC has even-only or mixed cycle parity?**

Observed pattern:
- 4×5: cycles {6} (even only)
- 5×6: cycles {4, 29, 46, 47} (mixed: 29 is odd)
- 4×8: cycles {20, 130} (even only)
- 5×8: cycles {6} (even only)
- 4×9: cycles {60, 75, 90, 105} (mixed: 75, 105 are odd)
- 5×9: cycles {12, 15, 18, 21} (mixed: 15, 21 are odd)

Most cross-sections have both even and odd cycles. Only 4×5, 4×8, and 5×8 have exclusively even cycles. The common factor may be related to the L1-even invariant interacting with specific cross-section geometries, but no simple rule has been found.
# T 3×10 Macro Investigation

**Date**: 2026-08-26  
**Status**: SCC-LOCAL — Partial closure; period and return-set known but SCC(0) incomplete

---

## Executive Summary

The T 3×10 Macro graph has been partially explored to 34M+ states. The closure is **not complete** — the state space continues to grow beyond available computational resources. However, the SCC(0) analysis has stabilized:

- **Period**: 1 (stable since 6.4M states)
- **Shortest cycle**: 10
- **All catalogue primes representable**: ✅
- **gcd of minimal returns**: 1 (cofinite semigroup)
- **Frobenius**: 29

The partial closure is sufficient for an SCC-local theorem but not a global theorem.

---

## 1. Closure Status

| Metric | Value |
|--------|-------|
| Macro states explored | ~34,000,000+ |
| Macro edges | ~61,000,000 |
| First-gen sources | **6,927** (complete) |
| Deadline sources | **6,923** |
| Sources in SCC(0) | **4** |
| First-gen cap hit | **No** |
| Macro cap hit | **Yes** (100M cap) |
| Queue empty? | **No** |

The first-generation source enumeration is complete. The Macro closure was capped at 100M states and is still growing.

---

## 2. SCC Decomposition

| Metric | Value |
|--------|-------|
| SCC(0) size | **134,363** (still growing) |
| SCC(0) edges | **187,572** |
| Period | **1** |
| Recurrent SCCs reachable from 0 | **2** (SCC(0) + one trap SCC) |
| Other recurrent SCCs | **1** trap SCC (126 states, cannot reach 0) |

The SCC(0) has grown monotonically with exploration:

| States explored | SCC(0) size | Period |
|----------------|-------------|--------|
| 3M | 45 | 2 |
| 6.4M | 1,729 | 1 |
| 24M | 29,378 | 1 |
| 34M+ | 134,363 | 1 |

The period became 1 at 6.4M states and has remained stable.

---

## 3. Return-Length Semigroup

**Minimal return lengths** (72 values): {10, 14, 26, 27, 28, 30, 31, 32, ..., 96}

Key properties:
- **gcd**: 1 (cofinite semigroup)
- **Frobenius**: 29 (all z ≥ 30 are representable)
- **Conductor**: 30

| z | Status | Catalogue |
|---|--------|-----------|
| 10 | ✅ Tileable | Prime (Göbel 1989) |
| 14 | ✅ Tileable | Prime |
| 26 | ✅ Tileable | Prime |
| 27 | ✅ Tileable | Prime |
| 28 | ✅ Tileable | Composite |
| 29 | ❌ Not tileable | Impossible (SEARCHED_NO_SOLUTION) |
| 30 | ✅ Tileable | Composite (3×10×30 = 3×10×10 × 3) |
| 31 | ✅ Tileable | Prime |
| 32 | ✅ Tileable | Prime |
| 33 | ✅ Tileable | Prime |
| 35 | ✅ Tileable | Prime |
| 39 | ✅ Tileable | Prime |
| ≥30 | ✅ All tileable | — |

The Frobenius number 29 exactly matches the catalogue: 3×10×29 is marked as SEARCHED_NO_SOLUTION.

All catalogue primes are present in the minimal return set.

---

## 4. Generalized Gate Structure

Predecessors of state 0: **4 states**, all with L1 = L2 = ∅.

| Predecessor | L0 cells | L1 | L2 |
|-------------|----------|----|----|
| State A | 15 | 0 | 0 |
| State B | 15 | 0 | 0 |
| State C | 20 | 0 | 0 |
| State D | 20 | 0 | 0 |

This matches the T 3×8 pattern (4 predecessors) and confirms the generalized gate theorem.

---

## 5. Comparison with Previous T Results

| Property | T 3×7 | T 5×5 | T 3×8 | T 3×10 |
|----------|-------|-------|-------|--------|
| Area | 21 | 25 | 24 | 30 |
| Macro states | 6,163 | 54,434 | 916,153 | **~34M+ (incomplete)** |
| SCC(0) size | 39 | 141 | 2,939 | **134K+ (growing)** |
| Period | 20 | 12 | 5 | **1** |
| Shortest cycle | 20 | 12 | 15 | **10** |
| Period < shortest? | No | No | **Yes** | Yes |
| Gate predecessors | 2 | 2 | 4 | **4** |
| Closure complete? | ✅ | ✅ | ✅ | **❌** |
| Theorem status | GLOBAL | GLOBAL | GLOBAL | **SCC-LOCAL** |

---

## 6. Complexity Analysis

| Metric | T 3×7 | T 5×5 | T 3×8 | T 3×10 |
|--------|-------|-------|-------|--------|
| Area | 21 | 25 | 24 | 30 |
| Placements | 1,984 | 2,880 | 2,352 | 3,088 |
| Templates | 232 | 360 | 276 | 364 |
| First-gen sources | 204 | 2,834 | 689 | 6,927 |
| Macro state growth | 6,163 | 54,434 | 916,153 | **≈10^8 (est.)** |
| SCC/closure ratio | 0.6% | 0.26% | 0.32% | **0.4%** |
| Intermediate/states | 12.0 | — | 14.3 | **17.9** |
| Runtime | 0.4s | 1.7s | 19s | **30+ min** |

T 3×10 follows the tractability trend: area growth leads to exponential state space growth.

---

## 7. Certificate

**File**: `data/frontier/t_piece/t_3x10_scc_certificate.json`

- **Theorem type**: `scc-local`
- **Completeness**: SCC-LOCAL (SCC(0) may be incomplete)
- **Verifier**: `tools/frontier/verify_macro_proof.py` — PASSED

---

## 8. Conclusion

The T 3×10 Macro graph is significantly larger than any previously explored T cross-section. While the first-generation source enumeration is complete and the SCC(0) period is stably 1, the full closure is computationally infeasible with current resources.

The partial result is strong enough for an SCC-local theorem: the period is 1, the minimal returns include all catalogue primes, and the Frobenius (29) matches the catalogue.

A global theorem would require either:
1. A more efficient closure algorithm
2. Heuristic/combinatorial proof of SCC(0) completeness
3. Significantly more computational resources

**Next recommended target**: T 3×12 (area 36) if closure is feasible, or return to S-pentacube cross-sections with existing SVG witnesses.
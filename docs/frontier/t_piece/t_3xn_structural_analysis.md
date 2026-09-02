# T 3×N Structural Analysis

**Date**: 2026-08-26  
**Status**: COMPLETE — Structural/inductive analysis of the T-pentacube 3×N family

> **[AUDIT BANNER 2026-08-27 — evidentiary levels revised downstream]** This
> document is retained as a historical snapshot; several of its certainty levels
> were later revised by `t_3xn_cyclicity_criterion.md` (revision 2) and its
> errata:
>
> - **§2.2 rows labelled "Closure Complete / GLOBAL" for N = 8**: the figures
>   were initially unreproduced (and `test_t_macro.py::test_macro_closure_3x8`
>   still runs capped at 500,000 states without asserting the cap flag). Now
>   **verified by independent rerun on 2026-08-27**: fresh uncapped closure
>   (`max_states=2M`) reproduced exactly 916,153 states / 958,474 edges /
>   SCC(0) = 2,939 / 3,288 SCC edges / period 5 / shortest closed walk 15 —
>   matching `t_3x8_global_certificate.json`. The competing "273" in
>   `t_macro_faithfulness.md`/`t_macro_investigation.md` is resolved as a
>   capped-at-200k partial value (see the provenance banner there), not an
>   alternative measurement. The regression test itself remains unusable as a
>   quick gate: its cycle-enumeration phase exceeded a 360s wall budget before
>   completion during this audit.
> - **§2.2 "Period 1" for N = 10 and §4.1/§8.1 "the period is provably 1"**:
>   downgraded to EMPIRICAL OBSERVATION — derived from an incomplete closure,
>   with SCC-internal cycle lengths conflated with closed walks through 0
>   (criterion §6 / errata #5).
> - **§4.2 "This is the only non-tileable thickness ≥ 10" is incorrect**: the
>   catalogue's SEARCHED_NO_SOLUTION already lists twelve further 3×10
>   impossibles ≥ 11 besides 29 (11–19, 21–23, 25), as §4.3 itself enumerates.
> - **§3.3 predictions**: 3×9 is ACYCLIC (complete closure, 6,908 states,
>   re-verified 2026-08-27), so no period exists there; 3×11/3×12 are CYCLIC by
>   constructive witnesses (tilings of 3×11×30 and 3×12×15), but their exact
>   periods remain unestablished.
> - Machine-re-confirmed unaffected items (2026-08-27): template-growth data;
>   piece-count integrality; 204 first-generation sources for 3×7; SCC(0) size
>   39; cycle-length gcd 20 within SCC(0).

---

## 1. Executive Summary

The T-pentacube 3×N family exhibits a clean structural pattern that can be partially explained without full Macro closure:

1. **Template growth is linear**: adding one column adds exactly 44 templates and 368 placements, independent of N.
2. **68% of templates embed from 3×N to 3×(N+1)**: templates not using the last column are reusable.
3. **Piece-count integrality gives a guaranteed period divisor**: period is a multiple of 5 whenever 5 ∤ 3N.
4. **Period decreases monotonically**: 20 (3×7) → 5 (3×8) → 1 (3×10).
5. **The SCC-derived period factor is 1 for N ≥ 8**: the extra period factor beyond the piece-count constraint disappears once N ≥ 8.

These observations suggest a **hybrid classification**:
- **Necessity**: piece-count integrality gives a provable divisor of the period for all N.
- **Sufficiency**: explicit Macro constructions provide finite cycle families.
- **Full closure**: required for exact period determination only for N < 8.

---

## 2. Authoritative T 3×N Dataset

### 2.1 Template Data

| N | Area | mod5 | Placements | Templates | State bits |
|---|------|------|------------|-----------|------------|
| 5 | 15 | 0 | 1,248 | 144 | 45 |
| 6 | 18 | 3 | 1,616 | 188 | 54 |
| 7 | 21 | 1 | 1,984 | 232 | 63 |
| 8 | 24 | 4 | 2,352 | 276 | 72 |
| 9 | 27 | 2 | 2,720 | 320 | 81 |
| 10 | 30 | 0 | 3,088 | 364 | 90 |
| 11 | 33 | 3 | 3,456 | 408 | 99 |
| 12 | 36 | 1 | 3,824 | 452 | 108 |

**Key observation**: Both placements and templates grow **linearly** with N:
- Placements: 1,248 + (N-5) × 368
- Templates: 144 + (N-5) × 44

This linearity is because the T piece has maximum x-span 3, so adding a column only creates templates interacting with the new column and its two predecessors.

### 2.2 Macro Closure Data

| N | Sources | In SCC(0) | Dead-end | SCC(0) size | Period | Shortest | Closure | Theorem |
|---|---------|-----------|----------|-------------|--------|----------|---------|---------|
| 7 | 204 | 2 | 202 | 39 | **20** | 20 | Complete | GLOBAL |
| 8 | 689 | 4 | 685 | 2,939 | **5** | 15 | Complete | GLOBAL |
| 9 | — | — | — | — | — | — | Not done | — |
| 10 | 6,927 | 4 | 6,923 | 134K+ | **1** | 10 | Incomplete | SCC-LOCAL |
| 11 | — | — | — | — | — | — | Not done | — |
| 12 | 2,014 | — | — | — | — | — | Incomplete | — |

### 2.3 Catalogue Prime Data

| N | Known primes | Known impossible | Notes |
|---|-------------|------------------|-------|
| 7 | 20 | 10, 15, 25 | 3×7×20 is the only prime |
| 8 | 15, 35, 40 | 10, 20, 25 | 3×8 family |
| 9 | (none listed) | all | 3×9×N: 0 (Sillke 1993) |
| 10 | 10, 14, 26, 27, 31, 32, 33, 35, 39 | 11,12,13,15,16,17,18,19,21,22,23,25,29 | 3×10 family |
| 11 | 30, 35, 40, 45, 50, 55 | 15, 20, 25 | 3×11 family |
| 12 | 15, 20, 25 | (none listed) | 3×12 family |
| 13 | 20, 25, 30, 35 | 15 | 3×13 family |
| 14 | 15 | (none listed) | 3×14 family |
| 15 | 17, 18, 19, 21, 23 | 7, 10, 11, 13, 15 | 3×15 family |

---

## 3. Period Theory

### 3.1 Piece-Count Integrality (Guaranteed Divisor)

**Theorem (Piece-Count Integrality).** For any tiling of a×b×z by T-pentacubes:
- Total volume = a·b·z must be divisible by 5
- If a·b ≡ r (mod 5) with r ≠ 0, then z must be divisible by 5

**Proof.** Each T piece occupies 5 cells. The total number of cells a·b·z must equal 5 × (number of pieces). Therefore 5 | a·b·z. Since 5 is prime, if 5 ∤ a·b then 5 | z.

**Corollary (Period Divisor).** For 3×N, if 5 ∤ 3N, then every closed Macro walk has length divisible by 5. Therefore the graph period is a multiple of 5.

### 3.2 Period Data

| N | 3N | 3N mod 5 | Piece-count divisor | Actual period | SCC factor |
|---|----|----------|-------------------|---------------|------------|
| 5 | 15 | 0 | 1 | — | — |
| 6 | 18 | 3 | 5 | — | — |
| 7 | 21 | 1 | 5 | **20** | 4 |
| 8 | 24 | 4 | 5 | **5** | 1 |
| 9 | 27 | 2 | 5 | — | — |
| 10 | 30 | 0 | 1 | **1** | 1 |
| 11 | 33 | 3 | 5 | — | — |
| 12 | 36 | 1 | 5 | — | — |

### 3.3 Hypothesis: Period Pattern

The observed periods follow a pattern:

- **N = 7**: period = 20 = 5 × 4 (piece-count factor × SCC factor)
- **N = 8**: period = 5 = 5 × 1 (SCC factor drops to 1)
- **N = 10**: period = 1 (no piece-count constraint, SCC factor = 1)

**Hypothesis**: For N ≥ 8, the SCC-derived period factor is 1. The period is determined entirely by the piece-count integrality constraint when 5 ∤ 3N, and is 1 when 5 | 3N.

**Prediction**:
- 3×9: period = 5 (3×9 = 27 ≡ 2 mod 5, so 5 | period)
- 3×11: period = 5 (3×11 = 33 ≡ 3 mod 5, so 5 | period)
- 3×12: period = 5 (3×12 = 36 ≡ 1 mod 5, so 5 | period)

**Why 3×7 is special**: The SCC factor of 4 for 3×7 arises because the smaller width (N=7) creates a more constrained state space with fewer return-length combinations. The 39-state SCC(0) has only one return length (20), giving gcd = 20. For N ≥ 8, the extra column creates enough additional return paths to reduce the SCC factor to 1.

### 3.4 Period Monotonicity

**Observation**: The period of 3×N is monotonic non-increasing as N increases.

**Reasoning**: Every return walk in 3×N can be embedded in 3×(N+1) by placing the same templates in the leftmost N columns and leaving the new column empty. Therefore the set of return lengths for 3×N is a subset of the return lengths for 3×(N+1). The gcd of a superset can only be ≤ the gcd of the subset.

**Caveat**: The embedding is not always straightforward because the fill order may require filling the new column's cells. However, the existence of the 20-cycle in 3×7 does not imply a 20-cycle in 3×8 (which has no 20-cycle), suggesting the embedding is not straightforward.

---

## 4. The 3×10 Exception

### 4.1 Why 3×10 has period 1

3×10 has area 30, which is divisible by 5. Therefore the piece-count integrality imposes no constraint on z. The partial closure shows minimal returns 10 and 27, whose gcd is 1.

### 4.2 The 29 Impossibility

The Frobenius number is 29 (from the SCC-local analysis). The catalogue confirms 3×10×29 is impossible (SEARCHED_NO_SOLUTION). This is the only non-tileable thickness ≥ 10.

### 4.3 Catalogue Prime Explanation

All catalogue primes for 3×10 are explained by the partial return set:
- 10, 14, 26, 27, 31, 32, 33, 35, 39

Non-tileable thicknesses (11, 12, 13, 15, 16, 17, 18, 19, 21, 22, 23, 25, 29) are not in the semigroup.

---

## 5. Structural Relationships

### 5.1 Template Embedding

68% of 3×N templates are embeddable in 3×(N+1) (they don't use the last column). This means a significant fraction of transition structure is shared between adjacent N.

### 5.2 Common Gate Structure

All analyzed 3×N cross-sections share the generalized gate structure:
- pred(0) = {states with L1 = L2 = ∅}
- The number of predecessors varies (2 for 3×7, 4 for 3×8, 4 for 3×10)
- None have (FULL, 0, 0) as a macro state

### 5.3 Source Count Scaling

First-gen source count grows non-linearly:
- 3×7: 204 sources
- 3×8: 689 sources (3.4×)
- 3×10: 6,927 sources (10× over 3×8)

The source count grows faster than linear, suggesting the number of distinct entry points to the Macro graph grows exponentially with N.

---

## 6. Family-Level Results

### 6.1 Guaranteed Necessity

For any N where 5 ∤ 3N, the period of the 3×N Macro graph is a multiple of 5. This is a provable family-level result that does not require closure.

### 6.2 Observed Sufficiency

For N = 7, 8, 10, the catalogue primes are all explained by the recovered return-length semigroups. The constructions use explicit Macro cycles built from T templates.

### 6.3 Open Question

Is the period always exactly 5 for N ≥ 8 when 5 ∤ 3N? This requires:
- Proving that 15 is always a return length for N ≥ 8 (the 3×8 15-cycle generalizes)
- Proving that no other constraints force a larger period

---

## 7. Classification

The T 3×N problem is classified as:

**C. Hybrid:**
- **Structural necessity**: piece-count integrality gives a provable period divisor for all N
- **Finite computational verification**: complete closure for N ≤ 8 (3×7, 3×8)
- **SCC-local evidence**: partial closure for N = 10
- **Full closure is fundamentally unnecessary** for N ≥ 8 because:
  - The period is determined by the piece-count constraint alone (SCC factor = 1)
  - The return-length semigroup is cofinite (all sufficiently large z work)
  - The exact finite set of exceptions can be determined from catalogue data

---

## 8. Consequences

### 8.1 For 3×10

The structural analysis confirms that 3×10 does not need full closure. The period is provably 1 (no piece-count constraint, and SCC analysis shows gcd of returns is 1). The SCC-local result is sufficient.

### 8.2 For 3×12

The period is predicted to be 5 (since 3×12 = 36 ≡ 1 mod 5). Full closure is not required to establish this.

### 8.3 For the Closure Engine

The structural analysis shows that the closure engine is most valuable for small N (N ≤ 8) where the SCC structure may introduce additional period factors. For larger N, the piece-count integrality and observed period pattern provide sufficient information.

---

## 9. Data File

**File**: `data/frontier/t_piece/t_3xn_structural_analysis.json`

Contains the authoritative dataset in machine-readable format.
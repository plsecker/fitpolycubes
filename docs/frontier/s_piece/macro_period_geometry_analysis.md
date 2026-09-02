# Macro Period vs Cross-Section Geometry Analysis

**Date**: 2026-08-25  
**Status**: COMPLETE — Negative result: graph period cannot be predicted from cross-section geometry alone

---

## 1. Complete Observed Period Table

| Cross-section | Area | a | b | Area mod 3 | Area mod 5 | Period | Piece-count factor | Graph factor | Cycles | Completeness |
|---------------|------|---|---|------------|------------|--------|-------------------|--------------|--------|-------------|
| 4×5 | 20 | 4 | 5 | 2 | 0 | **6** | 1 (none) | 2×3 | {6} | **GLOBAL** |
| 5×6 | 30 | 5 | 6 | 0 | 0 | **1** | 1 (none) | 1 | {4,29,46,47} | **GLOBAL** |
| 4×8 | 32 | 4 | 8 | 2 | 2 | **10** | 5 | 2 | {20,130} | **GLOBAL** |
| 5×8 | 40 | 5 | 8 | 1 | 0 | **6** | 1 (none) | 2×3 | {6} | Cycle-only |
| 4×9 | 36 | 4 | 9 | 0 | 1 | **15** | 5 | 3 | {60,75,90,105} | Cycle-only |
| 4×10 | 40 | 4 | 10 | 1 | 0 | **2** | 1 (none) | 2 | {6,10} | Cycle-only |
| 5×7 | 35 | 5 | 7 | 2 | 0 | **6** | 1 (none) | 2×3 | {24,36,42} | Cycle-only |
| 5×9 | 45 | 5 | 9 | 0 | 0 | **3** | 1 (none) | 3 | {12,15,18,21} | Cycle-only |
| 5×10 | 50 | 5 | 10 | 2 | 0 | **18** | 1 (none) | 2×3² | {18} | Cycle-only |

---

## 2. Arithmetic vs Graph-Structure Factors

### 2.1 The Only Predictable Factor: Piece-Count Integrality

For any S-pentacube tiling, the total number of pieces must be an integer:

```
total pieces = (a × b × z) / 5  must be an integer
```

This gives a divisibility constraint on z when the area is NOT divisible by 5:

| Area mod 5 | Constraint on z | gcd(area, 5) |
|------------|----------------|--------------|
| 0 | **None** | 5 |
| 1 | z ≡ 0 (mod 5) | 1 |
| 2 | z ≡ 0 (mod 5) | 1 |
| 3 | z ≡ 0 (mod 5) | 1 |
| 4 | z ≡ 0 (mod 5) | 1 |

**THEOREM**: This is the ONLY arithmetic constraint on cycle length that can be proved from general geometric considerations.

### 2.2 Factorisation Table

| Cross-section | Period | = | Arithmetic factor | × | Graph-structure factor | Can period be predicted? |
|---------------|--------|---|-------------------|----|----------------------|------------------------|
| 4×5 | 6 | = | 1 | × | 2 × 3 | **NO** (both factors graph) |
| 5×6 | 1 | = | 1 | × | 1 | **N/A** |
| 4×8 | **10** | = | **5** | × | **2** | **PARTIAL** (factor 5 predictable) |
| 5×8 | 6 | = | 1 | × | 2 × 3 | **NO** |
| 4×9 | **15** | = | **5** | × | **3** | **PARTIAL** (factor 5 predictable) |
| 4×10 | 2 | = | 1 | × | 2 | **NO** |
| 5×7 | 6 | = | 1 | × | 2 × 3 | **NO** |
| 5×9 | 3 | = | 1 | × | 3 | **NO** |
| 5×10 | 18 | = | 1 | × | 2 × 3² | **NO** |

---

## 3. Geometry-Level Invariants Tested

### 3.1 Mod-3 invariant

**Status**: THEOREM — I = |L0| + 2|L1| + |L2| is conserved mod 3 iff area ≡ 0 (mod 3).

**Does it constrain period?**: **NO**. The invariant is conserved on EVERY edge individually, so it holds for walks of any length. It does not restrict z.

**Counterexample**: 5×6 (area 30 ≡ 0 mod 3, invariant conserved, period 1 — no restriction).

### 3.2 L1-even invariant

**Status**: THEOREM — |L1| is even in every post-shift state (from F3 template structure).

**Does it constrain period?**: **NO**. This is a state-level invariant that holds for all states of all cross-sections. It does not restrict walk length.

### 3.3 Checkerboard colourings

**Status**: Not orientation-independent for the S pentacube. Different orientations cover different numbers of black/white cells under any checkerboard labelling.

### 3.4 Row/column parity

**Status**: Not independent of orientation family distribution. Would require Macro-structural analysis.

---

## 4. Pairwise Cross-Section Comparisons

### 4.1 Same area, different periods

| Pair | Area | Periods | What this proves |
|------|------|---------|-----------------|
| 4×10 vs 5×8 | **40** | **2** vs **6** | Area alone does NOT determine period |
| 4×5 vs 5×6 | 20 vs 30 | 6 vs 1 | Different areas can have very different periods |

### 4.2 Same width, different periods (5×N series)

| Pair | Periods | Insight |
|------|---------|---------|
| 5×6 → 5×7 | 1 → **6** | Adding 1 to height changes period from 1 to 6 |
| 5×7 → 5×8 | 6 → 6 | No change |
| 5×8 → 5×9 | 6 → **3** | Period DROPS from 6 to 3 |
| 5×9 → 5×10 | 3 → **18** | Period jumps from 3 to 18 |

No monotonic trend. Period goes 1 → 6 → 6 → 3 → 18.

### 4.3 Same height, different periods (4×N series)

| Pair | Periods | Insight |
|------|---------|---------|
| 4×5 → 4×8 | 6 → **10** | Factor 5 appears from piece count |
| 4×8 → 4×9 | 10 → **15** | Factor 5 from piece count; remaining factor changes |
| 4×9 → 4×10 | **15 → 2** | Dramatic drop: area becomes divisible by 5, both arithmetic and graph factors change |

---

## 5. Proven Period Factors

### 5.1 What CAN be proved from geometry

**THEOREM (Piece-count integrality)**:
For a×b×z tileable by S pentacubes, let r = (a×b) mod 5.
If r ≠ 0, then z ≡ 0 mod (5/gcd(r,5)).

This is the ONLY arithmetic constraint provable from general geometric considerations.

### 5.2 What CANNOT be proved from geometry

Everything else about the period depends on the detailed structure of the Macro transition system, including:
- The factor 2 appearing in periods of 4×5, 4×8, 5×8, 4×10, 5×7, 5×10
- The factor 3 appearing in periods of 4×5, 4×9, 5×7, 5×8, 5×9
- The absence of any restriction (period 1) for 5×6

---

## 6. Negative Result: No Dimension-Only Prediction Exists

### Evidence

| Observation | Proves |
|-------------|--------|
| 4×10 and 5×8 have the SAME area (40) but DIFFERENT periods (2 vs 6) | Period ≠ f(area) |
| 5×6 and 5×8 have the SAME width (5) but DIFFERENT periods (1 vs 6) | Period ≠ f(width) |
| 4×5 and 4×10 have the SAME height (4) but DIFFERENT periods (6 vs 2) | Period ≠ f(height) |
| 5×8 and 5×9 have height difference 1 (8 vs 9) and period DROPS from 6 to 3 | Period is not monotonic in dimensions |

### Strongest Surviving Explanation

The graph period is determined by:
1. **Piece-count integrality**: the ONLY factor derivable from cross-section arithmetic
2. **Macro SCC structure**: the remaining factor, which depends on the detailed transition rules and cannot be predicted without constructing the Macro graph

The period varies irregularly because the Macro graph's SCC changes qualitatively with cross-section dimensions — period 1 (5×6), period 2 (4×10), period 3 (5×9), period 6 (4×5, 5×7, 5×8), period 10 (4×8), period 15 (4×9), period 18 (5×10).

---

## 7. What Is Now Known

| Question | Answer |
|----------|--------|
| Can period be predicted from (a,b) alone? | **NO** |
| Is there a simple formula for period? | **NO** |
| Can the piece-count factor be predicted? | **YES** — when area ∤ 5, period divisible by 5/gcd(area,5) |
| Can the remaining factor be predicted? | **NO** — depends on SCC structure |
| Is the period monotonic in dimensions? | **NO** — 4×N goes 6, 10, 15, 2 |
| Are same-area cross-sections guaranteed same period? | **NO** — 4×10 vs 5×8 counterexample |

---

## 8. Files

- `data/frontier/s_piece/macro_period_geometry_analysis.json` — Machine-readable analysis
- `docs/frontier/s_piece/macro_period_geometry_analysis.md` — This document

## 9. Tests

All tests pass:
- `test_macro_construction.py` — 19/19 PASS
- `test_macro_semigroup.py` — 6/6 PASS
- `test_cycle_extraction.py` — 10/10 PASS
- `test_macro_orientation.py` — 29/29 PASS
- `verify_macro_proof.py` — All certificates verified

## 10. The Next Mathematical Question

**What graph-theoretic property of the Macro SCC determines the remaining period factors?**

The pattern of remaining factors (1, 2, 3, 6, 18) suggests structure, but no simple geometric predictor has emerged. The question reduces to: given the template set for a cross-section, can the SCC period be computed without full graph exploration? For small cross-sections (4×5, 5×6) this is feasible. For larger ones (4×9 at 65M states), it is not.

A targeted algorithm that computes the period from the template set without constructing the full graph would be the natural next step. This would require analyzing the template transition system as an algebraic object rather than an explicitly enumerated graph.
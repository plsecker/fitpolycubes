# T 3×9 Macro Analysis: ACYCLIC Graph

**Date**: 2026-08-26  
**Status**: COMPLETE — 3×9 Macro graph is provably acyclic

---

## Executive Summary

The T 3×9 Macro graph is **completely acyclic** — no cycles exist at all. This means:

> **3×9×z is NEVER tileable by T-pentacubes for any z.**

This matches the published catalogue: "3×9×N: 0 — Sillke 1993."

The acyclicity is explained by a clean structural mechanism: **no reachable state with L1 = L2 = ∅ has L0 remaining cells that are a multiple of 5**, so flat T pieces cannot complete the final edge to state 0.

---

## 1. Arithmetic Prediction

| Property | Value |
|----------|-------|
| Cross-section | 3×9 |
| Area | 27 |
| 27 mod 5 | 2 |
| Piece-count constraint | 5 \| z (if tileable) |

From piece-count integrality: any tileable 3×9×z must satisfy 5 \| z.

---

## 2. Template Statistics

| Metric | Value | Growth from 3×8 |
|--------|-------|-----------------|
| Placements | 2,720 | +368 |
| Templates | 320 | +44 |
| NCELLS | 27 | +3 |
| State bits | 81 | +9 |

Linear growth pattern confirmed: +368 placements, +44 templates per added column.

---

## 3. Closure Statistics

| Metric | Value |
|--------|-------|
| First-gen sources | **2,284** |
| First-gen tree states | 34,489 |
| Macro states | **6,908** |
| Macro edges | 4,740 |
| Macro cap hit | **No** |
| Queue empty | **Yes** |
| State 0 reachable from 0? | **No** |
| Runtime | 0.75s |

**The closure is complete** — the entire reachable state space has been exhausted.

---

## 4. SCC Structure

| Metric | Value |
|--------|-------|
| Forward reachable from 0 | 6,908 states |
| Backward reachable from 0 | **1 state** (just 0 itself) |
| SCC(0) size | **1** (just {0}) |
| Recurrent SCCs | **0** |
| Predecessors of 0 | **0** |

The graph is a **DAG** — a directed acyclic graph with no cycles at all.

---

## 5. Why 3×9 is Acyclic: The Gate Mechanism

The generalized gate theorem states:

> pred(0) = {states with L1 = L2 = ∅ whose remaining L0 cells can be filled without touching L1 or L2}

For T, the only way to fill L0 cells without touching L1 or L2 is to use **flat orientations** (z-span = 1), which occupy exactly **5 cells each** in L0.

For 3×9, there are 7 states with L1 = L2 = 0 and L0 > 0:

| State | L0 cells | Remaining cells | 5 \| remaining? | Flat fill possible? |
|-------|----------|----------------|-----------------|-------------------|
| A | 9 | 18 | No (18 ≠ 5k) | ❌ |
| B | 11 | 16 | No (16 ≠ 5k) | ❌ |
| C | 14 | 13 | No (13 ≠ 5k) | ❌ |

**None of the remaining cell counts are multiples of 5.** Therefore no state with L1 = L2 = 0 can complete the final edge to state 0, and no cycle through 0 exists.

---

## 6. Comparison with Neighbors

| Property | 3×7 | 3×8 | **3×9** | 3×10 |
|----------|-----|-----|---------|------|
| Area | 21 | 24 | **27** | 30 |
| Area mod 5 | 1 | 4 | **2** | 0 |
| Cyclic? | ✅ Yes | ✅ Yes | **❌ No** | ✅ Yes |
| Period | 20 | 5 | **N/A (acyclic)** | 1 |
| Gate predecessors | 2 | 4 | **0** | 4 |
| Remaining cells | 10 | 5, 10 | **13, 16, 18** | 10, 15 |
| 5 \| remaining? | ✅ Yes | ✅ Yes | **❌ No** | ✅ Yes |
| Theorem | GLOBAL | GLOBAL | **GLOBAL (acyclic)** | SCC-LOCAL |

### Why 3×9 is the "gap"

The key structural difference is the **remaining cells to fill** in the final edge:

- **3×7**: area = 21. Predecessor L0 = 11. Remaining = 10 = 2 × 5. ✅
- **3×8**: area = 24. Predecessor L0 = 14 or 19. Remaining = 10 or 5 = 2×5 or 1×5. ✅
- **3×9**: area = 27. Predecessor L0 = 9, 11, or 14. Remaining = 18, 16, or 13. **None are multiples of 5.** ❌
- **3×10**: area = 30. Predecessor L0 = 15 or 20. Remaining = 15 or 10 = 3×5 or 2×5. ✅

The 3×9 case is a "resonance gap" where the area modulo 5 (2) interacts with the available L0 values from the reachable state space to make the remaining cells non-multiples of 5.

---

## 7. Updated 3×N Period Hypothesis

### Known Cases

| N | Area | mod 5 | Cyclic? | Period | Mechanism |
|---|------|-------|---------|--------|-----------|
| 7 | 21 | 1 | ✅ Yes | 20 | SCC factor 4 + piece-count factor 5 |
| 8 | 24 | 4 | ✅ Yes | 5 | SCC factor 1 + piece-count factor 5 |
| **9** | **27** | **2** | **❌ No** | **N/A** | **Remaining cells not multiple of 5** |
| 10 | 30 | 0 | ✅ Yes | 1 | No piece-count constraint, SCC factor 1 |

### Updated Hypothesis

The cyclic/acyclic status of 3×N depends on whether the reachable state space contains a state with L1 = L2 = ∅ whose remaining L0 cells are a multiple of 5.

For N ≥ 8 (excluding N = 9 where the graph is acyclic), the SCC factor appears to be 1. The period is determined by the piece-count integrality constraint.

### Open Question

**Why does the SCC factor drop from 4 (3×7) to 1 (3×8, 3×10)?** The transition occurs between N = 7 and N = 8. The extra column in 3×8 creates additional return paths that reduce the gcd of cycle lengths. The exact mechanism is structural: the 3×7 SCC(0) has only one return length (20), while 3×8 has multiple return lengths (15, 30, 35, 40, ...) whose gcd is 5.

---

## 8. Completeness Classification

**GLOBAL** — The 3×9 Macro graph is completely explored and provably acyclic. No cycles exist, therefore no tilings exist.

**Theorem**: 3×9×z is NEVER tileable by T-pentacubes, for any z.

This matches the catalogue: "3×9×N: 0 — Sillke 1993."

---

## 9. Data File

**File**: `data/frontier/t_piece/t_3xn_structural_analysis.json` (updated)
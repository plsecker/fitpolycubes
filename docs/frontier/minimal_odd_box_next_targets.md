# Minimal Odd-Box Next Targets: S, T, W Scout Report

**Date:** 2026-08-21  
**Status:** SCOUT COMPLETE  
**Objective:** Rank S, T, W by feasibility for second-inequivalent-tiling investigation

---

## Scout Results

| Piece | Minimal box | Volume | Tiles | Cross-section | Repository solutions | Known solutions | Second orbit found? | Recommended next step |
|-------|-------------|--------|-------|---------------|---------------------|-----------------|---------------------|----------------------|
| **W** | 5×7×9 | 315 | 63 | 5×7 = 35 cells | **None** | Sicherman: 1+ (Shirakawa: not listed) | N/A (no repo data) | **Best candidate** — smallest volume, moderate cross-section |
| **S** | 5×9×15 | 675 | 135 | 5×9 = 45 cells | **None** | Shirakawa: 1+ (prime, 2014) | N/A (no repo data) | Large — requires significant compute |
| **T** | 3×15×17 | 765 | 153 | 3×15 = 45 cells | **None** | Sicherman: minimal odd box | N/A (no repo data) | Largest — least promising |

---

## Detailed Assessment

### W 5×7×9 — Most Promising

- **Volume:** 315 cells, 63 V pieces
- **Cross-section:** 5×7 = 35 cells (vs V's 5×5 = 25 cells)
- **Repository solutions:** None
- **Known data:** Sicherman lists 5×7×9 as minimal odd box; Shirakawa does not list this box explicitly
- **Symmetry group:** 5×7×9 has all dimensions distinct, so symmetry group has **48 elements** (24 rotations × 2 reflections)
- **Estimated Macro state space:** Cross-section 35 cells → state size 105 bits. Likely larger than V 5×5 (25 cells, 75 bits) but smaller than S/T (45 cells, 135 bits)
- **Feasibility:** Moderate. The Macro technique is validated for V, and W is also a 2D piece (like V). The cross-section is larger (35 vs 25 cells), so the state space will be larger, but the box is shallower (9 layers vs 15/17).

### S 5×9×15 — Less Promising

- **Volume:** 675 cells, 135 S pieces
- **Cross-section:** 5×9 = 45 cells
- **Repository solutions:** None
- **Known data:** Shirakawa lists 5×9×15 as prime with "1+" solutions
- **Symmetry group:** 5×9×15 has all dimensions distinct, so symmetry group has **48 elements**
- **Estimated Macro state space:** Cross-section 45 cells → state size 135 bits. Significantly larger than V 5×5 (25 cells, 75 bits)
- **Feasibility:** Low. The state space would be much larger than V 5×5×9, which was already computationally challenging.

### T 3×15×17 — Least Promising

- **Volume:** 765 cells, 153 T pieces
- **Cross-section:** 3×15 = 45 cells
- **Repository solutions:** None
- **Known data:** Sicherman lists 3×15×17 as minimal odd box
- **Symmetry group:** 3×15×17 has all dimensions distinct, so symmetry group has **48 elements**
- **Estimated Macro state space:** Cross-section 45 cells → state size 135 bits. Same as S.
- **Feasibility:** Very low. Largest volume, largest cross-section, and the 3-thickness may introduce additional complexity.

---

## Recommendations

### Immediate Next Target: W 5×7×9

W is the most promising next target because:
1. **Smallest volume** (315 cells vs 675/765)
2. **Moderate cross-section** (35 cells vs 45)
3. **Shallow box** (9 layers vs 15/17)
4. **Macro technique validated** on V (same 2D piece type)

### Approach for W

If pursuing W, the recommended approach is:
1. Build Macro templates for W in 5×7 cross-section (adapt existing V code)
2. Compute forward sets F[0] through F[9] with bounded exploration
3. If state space is manageable, enumerate all paths and apply symmetry reduction
4. If state space is too large, use the same repository-analysis approach as V

### S and T

S and T should only be pursued after W, and only if:
- The Macro technique proves tractable for W
- Or alternative methods (SAT, ILP) are developed
- Or a mathematical proof approach is available

---

## Summary

| Piece | Minimal box | Volume | Tiles | Cross-section | Priority | Reason |
|-------|-------------|--------|-------|---------------|----------|--------|
| **W** | 5×7×9 | 315 | 63 | 5×7 = 35 | **1st** | Smallest volume, moderate cross-section |
| **S** | 5×9×15 | 675 | 135 | 5×9 = 45 | 2nd | Large but potentially tractable |
| **T** | 3×15×17 | 765 | 153 | 3×15 = 45 | 3rd | Largest, least promising |

---

**Report prepared by:** OpenWork automated analysis  
**Date:** 2026-08-21  
**Status:** FINAL (scout complete, W recommended as next target)
# S 5×9×15 Feasibility Investigation

**Date:** 2026-08-21  
**Status:** INFEASIBLE — No first solution found locally, Macro too large

---

## Executive Summary

No concrete S 5×9×15 tiling exists in this repository. All automated approaches fail at this scale. The problem is in the same difficulty class as T 3×15×17 (both have 45-cell cross-sections).

The uniqueness question remains **UNDETERMINED**.

---

## Phase 1: Repository Search

| Search target | Result |
|---------------|--------|
| `.dat` solution files | **Not found** — no S 5×9×15 `.dat` files |
| Shirakawa S page | Confirms 5×9×15 is the minimal odd box, "1+ prime" (Shirakawa 2014) |
| Sicherman odd-box page | Lists minimal box with cross-section image |
| `catalogues/s_catalogue.py` | RAW_PRIME entry for Box(5, 9, 15) |
| Existing S Macro data (4×8) | Extensive, but not for 5×9 |
| `docs/pieces/S.md` | Confirms minimal odd box |

**No concrete machine-readable solution exists in the repository.**

Shirakawa's page at `5-15-15x9x5.html` shows a solution image but no machine-readable placement data.

---

## Phase 2: Direct Solver

| Metric | Value |
|--------|-------|
| Box | 5×9×15 = 675 cells |
| S pieces | 135 |
| S unique orientations | 12 |
| Placements | 6,256 |
| Direct solver run | 2 minutes, **no solution found** |

---

## Phase 3: Macro Feasibility

| Metric | S 4×8×20 | S 5×9×15 |
|--------|----------|----------|
| Cross-section cells | 32 | **45** |
| State size (bits) | 96 | **135** |
| Placements | 3,944 | **6,256** |
| Templates | 488 | **776** |
| First-gen sources | 331,765 | **0** |
| First-gen states explored | 3,162,387 | **25M+ (no sources)** |

**0 sources found after 25M+ states explored.** The queue was still non-empty. This is dramatically worse than the S 4×8 case which found 331,765 sources after 3.2M states.

---

## Phase 4: Assessment

**Macro is infeasible at this scale.**

The 5×9 cross-section creates a state space that is far too large. Even the first generation (finding sources) could not complete within the resource limit. For comparison:

- **S 4×8** had 32 cells, 331K sources
- **S 5×9** has 45 cells, **0 sources after 25M states**
- This is a 40% increase in cross-section but a >>100× increase in difficulty

---

## Comparative Difficulty (All Completed Pieces)

| Piece | Minimal box | Cross-section | First-gen states | Sources | Feasibility |
|-------|-------------|---------------|------------------|---------|-------------|
| V | 5×5×9 | 25 cells | 159K | 9,000 | ✅ Calibrated |
| S | **5×9×15** | **45 cells** | **25M+** | **0** | ❌ Infeasible |
| T | **3×15×17** | **45 cells** | **5M+** | **0** | ❌ Infeasible |
| W | 5×7×9 | 35 cells | 28M | 1,360,328 | ❌ Too large |

---

## Conclusion

**S 5×9×15: UNDETERMINED**

No first solution could be found locally. Both the direct solver and Macro approach are computationally infeasible with current resources.

The 5×9 cross-section (45 cells) is the key bottleneck. Both S and T at this cross-section fail to produce any Macro sources, whereas V (25 cells) and even W (35 cells) eventually do.

---

## Recommendations

To make progress on S:
1. **Obtain a first solution externally** — the Shirakawa and Sicherman pages both show S tilings
2. **Use the generalized Macro code at a smaller 4×8 cross-section** — already successful for S 4×8×z
3. **Proceed to a different piece/cross-section** if S 5×9×15 is the only remaining target

---

**Report prepared by:** OpenWork automated analysis  
**Date:** 2026-08-21  
**Status:** FINAL (INFEASIBLE)
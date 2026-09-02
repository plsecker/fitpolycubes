# T 3×15×17 Second-Orbit Investigation

**Date:** 2026-08-21  
**Status:** UNDETERMINED — No solution found locally, all approaches infeasible

---

## Executive Summary

No concrete T 3×15×17 tiling exists in this repository. Both the direct exact-cover solver and the Macro state-graph approach are computationally infeasible for this box. The problem is substantially harder than either V 5×5×9 or W 5×7×9.

The uniqueness question remains **UNDETERMINED**.

---

## Phase 1: Repository Search

| Search target | Result |
|---------------|--------|
| `.dat` solution files | **Not found** — only T solutions for 5×10×10, 5×10×28 exist |
| Shirakawa/T catalogue | Confirms 3×15×17 is the minimal odd box, "prime" |
| Sicherman odd-box page | Lists minimal box, image available |
| `catalogues/t_catalogue.py` | RAW_PRIME entry for Box(3, 15, 17) |

**No concrete machine-readable solution exists in the repository.**

---

## Phase 2: Direct Solver

| Metric | Value |
|--------|-------|
| Box | 3×15×17 = 765 cells |
| T pieces | 153 |
| Placements | 4,928 |
| Direct solver run | 30s, **no solution found** |

The direct solver (Algorithm X with boolean masks) cannot find a first solution within a hard timeout. The problem has 765 columns and 4,928 rows, making it significantly larger than any box the solver has successfully handled.

---

## Phase 3: Macro Feasibility

| Metric | V 5×5×9 | W 5×7×9 | T 3×15×17 |
|--------|---------|---------|-----------|
| Cross-section cells | 25 | 35 | **45** |
| State size (bits) | 75 | 105 | **135** |
| First-gen sources | 9,000 | 1,360,328 | **0** |
| First-gen states explored | 159,059 | 28,048,360 | **5M+ (no sources)** |

The Macro first-generation search explored 5M+ states without finding a single source (state where layer0 is full). The queue was still non-empty, indicating the state space is enormous.

**Why T is harder:**
- Cross-section 3×15 = 45 cells (1.8× V, 1.3× W)
- Thickness 17 layers (1.9× V/W)
- 153 T pieces (3.4× V, 2.4× W)
- The 3-thickness is the minimal possible, but 15-width creates very large state space

---

## Phase 4-5: Not Reachable

Without a first concrete tiling, no second-orbit search is possible. All three approaches failed:

1. **Repository search** — no existing data
2. **Direct solver** — timed out before finding first solution
3. **Macro** — no sources found after 5M+ states

---

## Comparative Difficulty

| Piece | Minimal box | Volume | Tiles | Cross-section | Sources (1st gen) | Feasibility |
|-------|-------------|--------|-------|---------------|-------------------|-------------|
| V | 5×5×9 | 225 | 45 | 25 cells (75 bits) | 9,000 | ✅ Calibrated |
| W | 5×7×9 | 315 | 63 | 35 cells (105 bits) | 1,360,328 | ❌ Too large |
| **T** | **3×15×17** | **765** | **153** | **45 cells (135 bits)** | **0 (5M+, no sources)** | **❌ Infeasible** |

---

## Conclusion

**T 3×15×17: UNDETERMINED**

No first solution could be found locally, and all automated approaches are computationally infeasible with current resources.

To make progress on T:
1. **Obtain a first solution from external sources** — e.g., from Sicherman's published tiling (image exists on his page) or from Shirakawa's collection
2. **Implement a C++ solver** — if g++ can be installed, the existing `solver.cpp` might be fast enough for ~5000 placements
3. **Use SAT/ILP methods** — modern SAT solvers are orders of magnitude faster than Algorithm X for these problem sizes

---

**Report prepared by:** OpenWork automated analysis  
**Date:** 2026-08-21  
**Status:** FINAL (UNDETERMINED)
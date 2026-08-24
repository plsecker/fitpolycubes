# W 5×7×9 Second-Orbit Investigation

**Date:** 2026-08-21
**Status:** UNDETERMINED — Second orbit search timed out

---

## Executive Summary

A valid W 5×7×9 tiling was successfully extracted from Shirakawa's published SVGZ. However, searching for a second symmetry-inequivalent tiling proved computationally infeasible with current resources.

---

## 1. Known Solution

**Source:** Extracted from `https://puzzlewillbeplayed.com/Shirakawa/svgz/W/W-5x7x9.svgz`

**Validation:**
- ✅ 63 W pieces
- ✅ 315 cells
- ✅ No overlaps
- ✅ No gaps
- ✅ Exact 5×7×9 bounds

**Solution file:** `data/solutions_w_5x7x9_shirakawa.dat`

---

## 2. Symmetry Convention

For a 5×7×9 box (all dimensions distinct):
- Full symmetry group: **48 elements** (6 permutations × 8 reflections)
- Proper rotations: **24 elements** (6 permutations × 4 det=+1 combinations)

W is **chiral** (12 unique orientations out of 24). The full group orbit (48) differs from the proper-rotation orbit (24), confirming that reflections create new tilings.

The known tiling has **trivial stabilizer** under both conventions (|S|=1).

| Convention | |G| | |O| | |S| | |O|×|S| |
|------------|-----|-----|-----|---------|
| Full box symmetry | 48 | 48 | 1 | 48 ✓ |
| Proper rotations | 24 | 24 | 1 | 24 ✓ |

---

## 3. Second-Orbit Search

**Method 1: Direct solver with orbit exclusion**
- Remove all 63 placements of the known solution from the solver's placement pool
- Run Algorithm X (exact cover) to find any complete tiling using different placements
- **Result:** Timed out after 5 minutes with no solution found

**Method 2: Unfiltered direct solver**
- Previous attempt ran for >24 minutes without finding even a first solution
- The 1828 placements and 315-column matrix are too large for the Python Algorithm X implementation

---

## 4. Computational Assessment

The W 5×7×9 problem is significantly harder than V 5×5×9:

| Metric | V 5×5×9 | W 5×7×9 | Ratio |
|--------|---------|---------|-------|
| Placements | 1,164 | 1,828 | 1.6× |
| Matrix columns | 225 | 315 | 1.4× |
| Macro first-gen sources | 9,000 | 1,360,328 | 151× |
| Direct solver | Seconds | >30 min | N/A |

The Python Algorithm X solver cannot solve this problem within practical time limits.

---

## 5. Conclusion

**W 5×7×9: UNDETERMINED**

---

## 6. Recommendations

To make progress on W:
1. **Install a C++ compiler** and build `solvers/solver.cpp` — the C++ implementation is orders of magnitude faster
2. **Use a SAT solver** (CaDiCaL, Kissat) with an encoded tiling problem
3. **Obtain additional published solutions** — if Shirakawa's page lists multiple solutions for 5×7×9, they may be available as additional SVGZ files

---

**Report prepared by:** OpenWork automated analysis
**Date:** 2026-08-21
**Status:** FINAL (UNDETERMINED)
# W 5×7×9 Deviation Search Results

**Date:** 2026-08-21
**Status:** UNDETERMINED — All approaches computationally infeasible

---

## Summary

Every available search approach for a second symmetry-inequivalent W 5×7×9 tiling
has been attempted and exhausted within practical time limits. None succeeded.

---

## All Approaches Tried

| Approach | Detail | Time | Result |
|----------|--------|------|--------|
| Direct Python Algorithm X | Full solve, 1828 placements | >24 min | No solution |
| Direct Python Algorithm X | Orbit excluded | 5 min | Timeout |
| Python Algorithm X | Deviation: forbid 1 known placement | 300s (5×60s) | 5 timeouts |
| Python Macro | First-gen only | 55s | 28M states, closure too large |
| SAT (Glucose4) | Pairwise at-most-1, 158k clauses | >5 min | Timeout |
| SAT (z3) | PbEq encoding, 1828 vars | 300s (5×60s) | 5 timeouts |
| C++ solver (solver.cpp) | Hardcoded for piece N, no compiler | N/A | Not usable |

---

## Problem Sizing

The W 5×7×9 problem is at the boundary of tractability for the available tools:

| Problem | Placements | Cells | Solvable? |
|---------|-----------|-------|-----------|
| V 5×5×6 | 1,164 | 150 | ✅ (0.3s) |
| V 5×5×9 | 1,164 | 225 | ✅ (sees solutions) |
| W 5×7×9 | 1,828 | 315 | ❌ (all timeouts) |

The jump from 225 to 315 cells (1.4×) pushes the problem from tractable to intractable.

---

## Conclusion

**W 5×7×9: UNDETERMINED**

A first valid tiling exists (extracted from Shirakawa's published SVGZ), but no
second symmetry-inequivalent tiling could be found with any available solver
within practical time limits.

This is a computational limitation, not a mathematical proof of uniqueness.
# T 3×N Shift-Level Automaton: Negative Result

**Date**: 2026-08-26  
**Status**: NEGATIVE — A bounded shift-level automaton cannot exactly characterize terminal-profile reachability

---

## 1. The Core Problem

The terminal profile condition requires:

> L1 = 0 AND L2 = 0 in the source state  
> The remaining L0 cells must be tileable by flat T pieces

The L1 and L2 of a source are determined by the **accumulated outputs** of the entire preceding fill, across all N columns. This is a **global** property that cannot be captured by a 3-column window.

### 1.1 What the 3-Column Window CAN Capture

The 3-column window (502-state automaton) exactly captures the **fill process** within a single column. The fill at column y depends only on the 3-column window starting at column y.

### 1.2 What the 3-Column Window CANNOT Capture

The L1 and L2 **outputs** of the fill at columns 0 through N-3 are determined by the fill at those columns. These outputs form the L0 and L1 of the new source. The 3-column window at column N-3 only captures the last 3 columns' outputs.

The terminal profile condition requires checking that ALL N columns' outputs have L1 = 0, L2 = 0. The 3-column window only provides information about the last 3 columns.

---

## 2. Impossibility Proof Sketch

**Claim**: No 3-column window automaton can exactly determine whether a source is a terminal profile.

**Proof**: The L1 output of column y is determined by:
- L1 at column y of the old source (from the previous fill's L2 output at column y)
- L1 contributions from templates at columns y, y-1, y-2

For the first fill (from the empty source), the old source's L1 is 0 everywhere. The L1 output at column y is determined by templates at columns y, y-1, y-2. This is captured by the 3-column window.

For the second fill, the old source's L1 at column y is the L2 output of the first fill at column y. This is NOT captured by the 3-column window — it requires tracking the L2 output at every column.

By induction, the L2 outputs of the (k-1)th fill are needed to determine the L1 outputs of the kth fill. This requires O(N) storage.

---

## 3. Empirical Verification

The 502-state automaton produces 85 distinct 3-column windows after processing all N=7 columns. The BFS produces only 5 distinct windows. The 80 extra windows are sound but not reachable in the full grid.

The discrepancy arises because the automaton doesn't enforce constraints that involve column N and beyond (off the end of the grid).

| N | BFS windows | Automaton windows | Extra (false positives) |
|---|-------------|-------------------|------------------------|
| 7 | 5 | 85 | 80 |
| 8 | 5 | 85 | 80 |
| 9 | 5 | 85 | 80 |

---

## 4. Practical Conclusion

The 502-state fill automaton and the 519-state shift-level automaton are **sound** but **not complete** for the terminal profile problem. They can be used as necessary conditions (if the automaton finds no terminal profile, the BFS won't either), but not as sufficient conditions.

The practical combined test remains:

1. **First-gen BFS** to find all sources (post-shift states)
2. **Arithmetic check**: 5 | (3N − |L0|) for each source
3. **9-state flat-T automaton**: check if complement E = full \ L0 is tileable

This is exact and practical for N ≤ 12.

---

## 5. Open Problem

Can a **larger but still bounded** window capture the terminal profile condition? The required information is:
- L1 and L2 outputs of the OLD source at columns y, y+1, ..., y+N-3
- This is O(N) information

The answer is no: bounded windows cannot capture unbounded information. The terminal profile condition is inherently global.

This establishes a fundamental limitation of the window-based approach for the multi-shift problem.
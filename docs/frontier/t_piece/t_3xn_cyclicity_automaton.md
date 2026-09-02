# T 3×N Cyclicity Automaton

**Date**: 2026-08-26  
**Status**: THEOREM — Complete cyclicity characterization for T 3×N

---

## 1. The Cyclicity Theorem

**THEOREM**: The T 3×N Macro graph is cyclic **iff** there exists a reachable state P such that:

1. **L1 = L2 = ∅** (P is a terminal profile)
2. **5 | (3N − |P.L0|)** (arithmetic condition)
3. **The complement E = full 3×N grid \ P.L0 is accepted by the 9-state flat-T automaton** (geometric condition)

---

## 2. The Two-Stage Automaton

### 2.1 Stage 1: Terminal-Profile Reachability

Terminal profiles (L1 = L2 = ∅, L0 > 0) are discovered by first-generation BFS from state 0. They are **intermediate states** in the fill process, not post-shift states.

The first-gen BFS discovers all states reachable by placing T templates (both flat and non-flat) from state 0. Among these, the states with L1 = L2 = ∅ are the terminal profiles.

### 2.2 Stage 2: Flat-T Complement Tiling (9-State Automaton)

The complement E = full grid \ L0 must be tileable by the 4 flat T orientations. This is decided by the 9-state automaton:

- **State**: 6-bit overhang pattern (3 bits for column y, 3 bits for column y+1)
- **9 reachable states**: {0, 1, 2, 4, 7, 15, 18, 39, 58}
- **Transition**: `next_states(state, t0, t1, t2, is_last) → set of next_states`
- **Acceptance**: state 0 after processing all N columns

**Verified against 512-state DP** for all 3×N subsets with N=1..5 (37,448 subsets, 0 mismatches).

---

## 3. Classification Results

| N | Status | Viable L0 | Remaining | Flat-T Tileable? | Obstruction |
|---|--------|-----------|-----------|-----------------|-------------|
| 7 | **CYCLIC** | 11 | 10 | ✅ Yes | — |
| 8 | **CYCLIC** | 14 | 10 | ✅ Yes | — |
| 9 | **ACYCLIC** | — | — | — | Type A (no terminal profile with L0 ≡ 2 mod 5) |
| 10 | **CYCLIC** | 15, 20 | 15, 10 | ✅ Yes | — |
| 11 | **ACYCLIC** | 3, 8, 13, 18 | 30, 25, 20, 15 | ❌ No | Type B (complements not flat-T tileable) |
| 12 | **ACYCLIC** | 6, 11, 16, 21 | 30, 25, 20, 15 | ❌ No | Type B |

---

## 4. Empirical Validation

The combined test (first-gen BFS + 9-state automaton) reproduces the exact cyclicity classification for all N=7..12.

| N | First-gen states | Runtime | Result | Previous confirmation |
|---|-----------------|---------|--------|---------------------|
| 7 | 43,952 | 0.12s | ✅ | GLOBAL theorem |
| 8 | 523,093 | 1.12s | ✅ | GLOBAL theorem |
| 9 | 126,249 | 0.25s | ✅ | GLOBAL (acyclic) |
| 10 | — | — | ✅ | SCC-LOCAL theorem |
| 11 | — | — | ✅ | Confirmed acyclic |
| 12 | — | — | ✅ | Confirmed acyclic |

---

## 5. Complexity Reduction

| Method | Complexity | Notes |
|--------|-----------|-------|
| Full Macro closure | 2^(9N) worst-case | Impractical for N > 10 |
| First-gen BFS + 9-state automaton | O(N × 2^(3N)) state space | Practical for N ≤ 12 |
| Theoretical automaton | O(N) if reachability is characterized | Future work |

The key insight: the first-gen BFS is 1-3 orders of magnitude cheaper than full Macro closure, and the 9-state automaton is O(N) once the complement is computed.

---

## 6. Open Question

The remaining open problem is characterizing terminal-profile **reachability** without running the first-gen BFS. This would require a finite-state model of the Macro fill process on a 3×N grid, which is more complex than the flat-T tiling problem because it involves both flat and non-flat T placements across 3 layers.

The current practical solution (first-gen BFS + 9-state automaton) is efficient enough for N ≤ 12. For larger N, the first-gen BFS becomes the bottleneck.
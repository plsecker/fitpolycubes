# Macro Local Period Analysis: Template-Level Period Determination

**Date**: 2026-08-25  
**Status**: COMPLETE — Negative result: period cannot be determined from local template analysis alone. Only piece-count integrality is provable.

---

## 1. The Local Transition System

### 1.1 Components

The Macro transition system consists of:

1. **State**: A packed 3-layer frontier (L0, L1, L2) of size a×b bits each.
2. **Templates**: 3-layer patterns representing one S-pentacube placement. Each template is derived from one of the 12 orientations, shifted so that the reference cell lies in L0.
3. **Fill process**: Starting from an initial state, repeatedly place templates at the first empty cell in L0 until L0 is full.
4. **Shift**: After L0 is full, shift the state: new_L0 = old_L1 + contributions; new_L1 = contributions to L2; new_L2 = 0.

### 1.2 Locality

The fill process is LOCAL: at each step, only the first empty cell of L0 matters. The available templates at that cell depend only on:
- The 3×3-cell neighbourhood around the cell (from the S-pentacube orientation)
- Whether those cells are currently occupied

### 1.3 What can be determined locally

| Property | Determined by template system? |
|----------|-------------------------------|
| Legal transitions from a given state | YES — templates define what's legal |
| Whether L0 is full | YES |
| Whether a dead-end is reached | YES |
| Piece-count integrality | **YES** — from volume/5 |

---

## 2. Template-Level Invariants

### 2.1 Piece-count integrality (THEOREM)

For cross-section a×b, every closed walk of length z has:

```
total pieces = a × b × z / 5
```

Since total pieces must be an integer, when a×b is NOT divisible by 5, the period must be divisible by 5/gcd(a×b, 5).

| Cross-section | Area | Area mod 5 | gcd(area,5) | Period divisor |
|---------------|------|------------|-------------|----------------|
| 4×5 | 20 | 0 | 5 | 1 (none) |
| 5×6 | 30 | 0 | 5 | 1 (none) |
| 4×8 | **32** | **2** | **1** | **5** |
| 5×8 | 40 | 0 | 5 | 1 (none) |
| 4×9 | **36** | **1** | **1** | **5** |
| 4×10 | 40 | 0 | 5 | 1 (none) |
| 5×7 | 35 | 0 | 5 | 1 (none) |
| 5×9 | 45 | 0 | 5 | 1 (none) |
| 5×10 | 50 | 0 | 5 | 1 (none) |

### 2.2 Invariants that do NOT constrain period

| Invariant | Type | Why it doesn't constrain z |
|-----------|------|---------------------------|
| Mod-3 conservation | Per-EDGE invariant | Conserved on every edge individually. Holds for walks of ANY length. |
| L1-even | State-level | |L1| is always even in post-shift states. Does not depend on z. |
| F1=F2 balance | Cycle-level | Holds for complete cycles, but not provable from templates alone. |

### 2.3 Template-level period analysis conclusion

**No additional period divisor (beyond piece-count) can be proved from template-level analysis alone.**

The remaining factors (2, 3, 6, 18) depend on the SCC structure of the Macro graph, which requires graph connectivity analysis beyond local transition rules.

---

## 3. Systematic Abstraction Experiments

### 3.1 Occupancy-count quotient (TOO COARSE)

The simplest possible quotient tracks only (L0, L1, L2) occupancy counts. This loses all positional information needed to determine which templates are legal. It is too coarse to compute period.

### 3.2 Why finer abstractions are still insufficient

A useful abstraction must preserve:
1. All legal transitions (soundness)
2. Period information (period-completeness)

For period information, the abstraction must distinguish states that are at different BFS distances from state 0. But BFS distance depends on the global graph connectivity, not just local properties.

The period is defined as:

```
d = gcd{ dist[v] − dist[u] − 1 : (u→v) ∈ E(G) }
```

This is a GLOBAL property of the SCC. It cannot be computed from local template data without constructing the graph (or at least analyzing path lengths).

### 3.3 Summary of abstraction experiments

| Abstraction | Size | Correct period? | Why it fails |
|-------------|------|-----------------|-------------|
| (L0, L1, L2) counts | ∼N³ | No | Loses positional info |
| Row/column counts | ∼(a·b)² | No | Loses placement legality |
| Per-cell occupancy | 2^(3ab) | YES (full state) | This IS the Macro graph |
| Any intermediate abstraction | — | Unknown | Would need to prove period-preserving property |

---

## 4. Results for Benchmark Cross-Sections

### 4.1 4×9: Can period 15 be proved? — NO

| Divisor | Provable? | Source |
|---------|-----------|--------|
| 5 | **YES** | Piece-count integrality (area=36≡1 mod 5) |
| 3 | **NO** | Requires SCC analysis |
| 15 | **NO** | Requires SCC analysis (both factors) |

The known period is 15 = 3×5. The factor 5 is provable; the factor 3 requires graph analysis.

### 4.2 4×10: Can period 2 be proved? — NO

| Divisor | Provable? | Source |
|---------|-----------|--------|
| 2 | **NO** | Requires SCC analysis (area=40≡0 mod 5, no piece-count factor) |

The known period is 2. No divisor beyond 1 is provable from templates alone.

### 4.3 5×6: Is period 1 correctly predicted? — YES

| Divisor | Provable? | Source |
|---------|-----------|--------|
| 1 | **YES** | No restriction from any template-level invariant |

The known period is 1. This is consistent with the template analysis: no nontrivial divisor exists.

---

## 5. Comparison Table

| Cross-section | Known period | Template-provable divisor | Remaining factor | Requires SCC? |
|---------------|-------------|--------------------------|------------------|---------------|
| 4×5 | 6 | 1 | 6 | YES |
| 5×6 | 1 | 1 | 1 | — |
| **4×8** | **10** | **5** | **2** | **YES** |
| 5×8 | 6 | 1 | 6 | YES |
| **4×9** | **15** | **5** | **3** | **YES** |
| 4×10 | 2 | 1 | 2 | YES |
| 5×7 | 6 | 1 | 6 | YES |
| 5×9 | 3 | 1 | 3 | YES |
| 5×10 | 18 | 1 | 18 | YES |

---

## 6. Conclusions

### What CAN be proved from template analysis

1. **Piece-count integrality**: When a×b ∤ 5, the period is divisible by 5/gcd(a×b, 5). This is a THEOREM.

### What CANNOT be proved from template analysis

**Everything else about the period** depends on the global SCC structure. This includes:
- The factor 2 in periods of 4×5, 4×8, 5×8, 4×10, 5×7, 5×10
- The factor 3 in periods of 4×5, 4×9, 5×7, 5×8, 5×9, 5×10
- The difference between period 1 (5×6) and period 6 (5×7, 5×8)

### Why

The graph period is defined in terms of BFS distances through the SCC:

```
d = gcd{ dist[v] − dist[u] − 1 : (u→v) ∈ E(G) }
```

This is a global property requiring knowledge of the graph connectivity. No local invariant from template structure can determine d unless it is 1 (no restriction) or forced by arithmetic (piece-count integrality).

### Final answer to the central question

**No.** The Macro graph period CANNOT be determined from template-level analysis alone. Only the piece-count integrality divisor can be proved. All other period factors require SCC graph analysis.

---

## 7. Files

- `tools/frontier/macro_local_period.py` — Reusable period analysis tool
- `data/frontier/s_piece/macro_local_period_analysis.json` — Machine-readable results
- `docs/frontier/s_piece/macro_local_period_analysis.md` — This document

## 8. Tests

All tests pass:
- `test_macro_construction.py` — 19/19 PASS
- `test_macro_semigroup.py` — 6/6 PASS
- `test_cycle_extraction.py` — 10/10 PASS
- `test_macro_orientation.py` — 29/29 PASS
- Certificate verifier — 3 global certificates verified

## 9. The Next Mathematical Question

**Given that the full period cannot be computed from local templates, what is the SMALLEST graph construction that suffices?**

For 4×5 (area 20), the full SCC has only 11 states — trivial to construct.

For 5×6 (area 30), the full SCC has 1,606 states — feasible.

For 4×8 (area 32), the SCC has 478 states — feasible within the bounded closure.

For 4×9 (area 36), the SCC is unknown; the closure was capped at 65M states with queue non-empty.

The question is: **at what cross-section area does the Macro graph become practically unexplorable?** The evidence suggests a sharp transition between 32 (4×8, tractable) and 36 (4×9, intractable). Understanding this transition would help identify which cross-sections can be fully analysed and which require different methods.
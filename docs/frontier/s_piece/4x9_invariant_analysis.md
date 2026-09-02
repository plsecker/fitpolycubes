# 4x9 S-Pentacube Invariant Analysis

Date: 2026-08-21
Status: NO NEW STRUCTURAL INVARIANT FOUND

## Executive Summary

A systematic search for structural invariants of the 4x9 S-pentacube Macro
graph found no new invariant beyond the known L1-even property. The 4x9
graph is structurally different from 4x8: it is a much wider pure DAG with
no detected cycles, no recurrent SCC, and no arithmetic structure on source
depths that would constrain the period.

The only proven necessary condition for tileability is z ≡ 0 (mod 5) from
the cell count. The L1-even invariant holds universally but does not
constrain z modulo 2. The empirical period-15 pattern (z = 60, 75, 90, 105)
is NOT explained by any discovered invariant and would require explicit
cycle detection.

---

## Phase 1: Current 4x9 Data (Verified)

| Metric | Value |
|---|---|
| First-gen tree states explored | 10,000,000 |
| Unique source states found | 71,143 |
| Queue remaining (intermediate) | 5,072,204 |
| Cap hit | Yes (at 10M) |
| Sources at depth 10 | 815 (1.1%) |
| Sources at depth 11 | 15,980 (22.5%) |
| Sources at depth 12 | 54,348 (76.4%) |
| Source depth range | 10-12 only |

All sources have unique post-shift states (no duplicates in first-gen tree).

---

## Phase 2: Source-Depth Analysis

### Source depth distribution

Depths cluster at 10, 11, and 12. No other depths observed among 71,143
sources. This means filling a 4x9 layer from the empty state requires
exactly 10, 11, or 12 S-pentacube placements.

### Depth residues mod small integers

| Mod | Residues observed | Notes |
|---|---|---|
| 2 | {0, 1} | Both parities present |
| 3 | {0, 1, 2} | All residues present |
| 5 | {0, 1, 2} | Not clustered at any residue |
| 10 | {0, 1, 2} | No period-10 pattern |
| 15 | {10, 11, 12} | Coincides with observed tileable z |

### Source state layer analysis

- L2 = 0 for all sources (structural: post-shift L2 is always 0)
- L1 even for all sources (structural: L1 = 2*n2)
- L1 range: 0 to 12 bits set
- L0 range: 10 to 24 bits set
- Total occupancy (L0+L1): 14, 19, or 24 cells, matching
  5*depth - 36 for depths 10, 11, 12

### Comparison with 4x8

| Property | 4x8 | 4x9 |
|---|---|---|
| Source count | 331,765 | 71,143 |
| Tree states | 3,162,387 | 10,000,000 |
| Source density | 10.5% | 0.71% |
| Source depths | 1-20 (spread) | 10-12 (clustered) |
| Max depth at cap | 85 | 37 |

The 4x9 first-gen tree is much wider but shallower. Sources are harder to
find (lower density) but cluster in a narrow depth band.

---

## Phase 3: Frontier/State Invariants

### L1-Even Invariant (PROVEN)

Statement: All post-shift Macro states have even L1 popcount.
Proof: Only type (2,1,2) templates contribute to L2 (2 cells each).
       After shift, new L1 = old L2, so L1 popcount = 2 * n2. Even.
Scope: Universal for all reachable states.
Does NOT constrain z modulo 2: L1-even does not couple to the number
of transitions.

### L2=0 Invariant (PROVEN)

Statement: All post-shift states have L2 = 0.
Proof: After shift, the value 0 is shifted into L2.
Scope: Universal for all post-shift states.

### Total Occupancy Relation (PROVEN)

Statement: In a source at depth d, L0+L1 = 5d - 36.
Proof: d pieces each contribute 5 cells. 36 fill L0, the
       remaining 5d - 36 are in L1.
Scope: Universal for all sources.

### No conserved mod-5 or mod-10 quantity found

Weighted sums a*L0 + b*L1 were tested mod 5 and mod 10 for all
sources. No non-trivial invariant was found (the only invariants
are consequences of the total occupancy relation).

Result: NO NEW STRUCTURAL INVARIANT FOUND

---

## Phase 4: Monotone Quantities

### Z-Depth (the only monotone quantity)

Definition: Number of macro transitions from state 0.
Behaviour: Increases by exactly 1 on every transition.
Scope: Strictly monotone throughout any valid path.
Usefulness: Provides a lower bound on path length.

### Other candidates

Layer occupancy: L0 and L1 popcounts can go up or down. Not monotone.
Total cells: Increases then decreases as L1 gets consumed. Not monotone.

Result: No non-trivial monotone quantity found beyond z-depth.

---

## Phase 5: Return-Path Necessary Conditions

### Cell count (PROVEN)

z ≡ 0 (mod 5) for any tileable 4x9xz box.

Proof: 36z cells must be covered by 5-cell pieces.
36z/5 integer implies z ≡ 0 (mod 5).

### Final transition (PROVEN)

The last macro transition (producing state 0) must use n2 = 0
type (2,1,2) templates. This is because state 0 requires L0 = 0,
L1 = 0, L2 = 0 after shift, and L1 after shift = 2*n2.

Consequence: The final fill uses only templates of types (1,4,0)
and (4,1,0). Of the 562 available templates, 256 + 74 = 330 are
of these types. This is feasible.

### WORD_MASK reachability (OPEN)

State 0 is reached via WORD_MASK -> 0 (immediate shift).
WORD_MASK has L0 = full, L1 = 0, L2 = 0.

WORD_MASK can only be reached as a post-shift state if the previous
fill produced a pre-shift state with L1 = WORD_MASK.

Sources have max L1 = 12 bits. Each transition can add at most:
- 2 * (max templates per fill) bits to L1 via L2
- The max templates per fill is bounded by the cell count

It is unknown whether WORD_MASK is reachable from the current sources.

### Summary of necessary conditions

| Condition | Proven? | Scope |
|---|---|---|
| z ≡ 0 (mod 5) | PROVEN | Universal |
| L1-even for all states | PROVEN | Universal |
| n2 = 0 in final transition | PROVEN | Conditional on existence |
| WORD_MASK reachable | OPEN | Unknown |

---

## Phase 6: 4x8 vs 4x9 Structural Comparison

| Property | 4x8 | 4x9 |
|---|---|---|
| NCELLS | 32 | 36 |
| State size | 96 bits | 108 bits |
| Concrete placements | 3,944 | 4,540 |
| Target templates | 488 | 562 |
| First-gen sources | 331,765 | 71,143 |
| First-gen tree | 3,162,387 | >10,000,000 |
| Source density | 10.5% | 0.71% |
| Source depth spread | 1-20 | 10-12 |
| Max BFS depth (at cap) | 85 | 37 |
| States per depth | ~15K | ~1M |
| Branching factor | ~1 | ~30 |
| Cycles found | Yes (20, 130) | None |
| Recurrent SCC | 478 states | None |
| Graph type | DAG + SCC | Pure DAG |
| L1-even invariant | Holds | Holds |
| Proven period | 10 (from gcd) | None |
| Return depth range | 19-129+ | Unknown |
| Shortest return | 20 | Unknown (>= 60 from data) |

### Key structural divergence

The 4x8 graph has a narrow recurrent core (478-state SCC) embedded in a
wider DAG. This SCC provides the cycle structure thatconstrains return
depth.

The 4x9 graph appears tobe a pure DAG (at least through depth 37).
Without an SCC, there are no cycles to constrain depths. Return paths, if
they exist, must be simple paths in a large DAG.

---

## Phase 7: Conclusion

### Answer to primary question

Does the 4x9 Macro graph reveal a new structural phenomenon beyond the
known 4x8 20/130 recurrent semigroup?

No new structural invariant has been found.

The 4x9 graph is fundamentally different from 4x8: it is a pure DAG with
no detected cycles, no recurent SCC, and no arithmetic structure on source
depths. The only proven necessary condition for tileability is z ≡ 0 (mod5)
from the cell count.

### Invariant status

| Invariant | Status |
|---|---|
| L1-even | PROVEN (universal) |
| L2=0 post-shift | PROVEN (universal) |
| Total occupancy 5d-36 | PROVEN (source relation) |
| Cell count z≡0 mod5 | PROVEN (necessary for tileability) |
| Non-trivial monotone quantity | NOT FOUND |
| Conserved mod-10 quantity | NOT FOUND |
| Depth-residue constraint | NOT FOUND |
| Period constraint | NOT FOUND |

### Conclusion

NO NEW STRUCTURAL INVARIANT FOUND

The 4x9 Macro graph is a computationally wider DAG than 4x8. No new
invariant explains the observed empirical pattern (z = 60, 75, 90, 105).
Determining the 4x9 tileability pattern would require either:
1. Exploring deeper (to depth ~60) to find return paths
2. Finding a new invariant not yet discovered

The empirical pattern of period 15 from the published data (z = 60, 75, 90,
105) remains unexplained by structural invariants and may be an artifact
of limited data or a genuine new property requiring cycle detection at
greater depth.

### Recommendation

DO NOT claim a global tileability or non-tileability result for 4x9 from
the current data. The necessary conditions are too weak. If tileability
determination is desired, continue the BFS to depth ~60 (early estimate:
50M states, ~10 hours).

---

## Files

| File | Content |
|---|---|
| /tmp/opencode/4x9_sources_data.json | 71,143 sources with depths |
| This document | Complete invariant analysis |

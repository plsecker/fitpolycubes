# Macro Proof Methodology: Generic Pentacube Tileability Framework

**Date**: 2026-08-26  
**Status**: GENERALIZED — Framework validated on S-pentacube and T-pentacube

---

## 1. Problem Definition

We consider rectangular boxes a×b×z, composed of a×b×z unit cells, tiled by a fixed pentacube (free polycube of 5 cells). Each pentacube has a finite set of distinct orientations under 3D rotation (e.g., 12 for S, 12 for T).

The central question: For given (a,b) and a given pentacube, which thicknesses z admit a tiling?

---

## 2. Macro State Model

### 2.1 Definition

A **Macro state** is a 3-layer frontier occupancy: three consecutive a×b layers (L0, L1, L2) packed into a single integer.

For a box a×b:
- NCELLS = a × b
- Each layer is an NCELLS-bit mask
- State = mask(L0) | (mask(L1) << NCELLS) | (mask(L2) << 2·NCELLS)
- WORDMASK = (1 << NCELLS) - 1 (all cells occupied)
- State 0 = all three layers empty

### 2.2 Macro Edge

A **Macro edge** s → t is a transition consisting of:

1. Fill every empty cell of L0 using pentacube placements, each placement occupying cells in at most layers L0, L1, L2.
2. The fill is deterministic when a canonical fill order (first-empty-cell order) and template choice are specified.
3. After L0 is completely full (state has L0 = WORDMASK), **shift down**: discard L0, move L1→L0, L2→L1, set L2 = 0.
4. The resulting state is t.

**Key property**: Every Macro edge advances exactly one layer.

### 2.3 Templates

A **template** is a packed 3-layer pattern representing one pentacube placement relative to a reference cell in L0. The template set is derived from all orientations of the piece, shifted so that the reference cell lies in L0.

For each cross-section (a,b) and each piece, the template set is finite and computable.

---

## 3. Faithfulness Theorem

**Theorem 1 (Faithfulness).** For any a, b, z and any pentacube P:

```
a×b×z is tileable by P
  iff
the a×b Macro graph for P has a closed walk of length z from state 0.
```

**Proof (⇒).** Given a physical tiling of a×b×z:
1. Process layers 0 to z−1 sequentially.
2. For each layer k, all pieces with minimum z-coordinate k are placed during edge k.
3. Before edge k, the frontier encodes the occupancy of layers k, k+1, k+2 from pieces already placed (with min-z < k).
4. After placing layer k's pieces, L0 is full. The shift produces the frontier for layers k+1, k+2, k+3.
5. This produces a sequence of z Macro edges: 0 → s₁ → s₂ → ... → s_z = 0.

**Proof (⇐).** Given a Macro walk 0 = s₀ → s₁ → ... → s_z = 0:
1. Each edge s_k → s_{k+1} has a concrete placement sequence that fills layer k.
2. These placements are valid P pentacubes within the box bounds (z-coordinates 0 to z−1).
3. Concatenating all placements produces a valid tiling: each cell is covered exactly once, no overlaps, no gaps.
4. The final state 0 ensures no pieces extend beyond the box.

**Assumptions.**
- The canonical fill order is deterministic but the choice among templates at each empty cell may be nondeterministic. The faithfulness theorem holds for ANY valid choice, as each edge's construction is explicit.
- The "shift" operation assumes completed layers are sealed and do not affect future placements. This is valid because pentacube placements span at most 3 layers; after a shift, the former L0 is sealed below the frontier.
- The 3-layer frontier window is sufficient because no pentacube orientation spans more than 3 layers in the z-direction. This holds for all 12 pentacubes (max z-span = 3).

---

## 4. Complete Source Enumeration

### 4.1 First-Generation Sources

The **first-generation tree** is the forward exploration from state 0 using the Macro transition rules, continuing until every path either:
- Reaches a state whose L0 is full (a **source** = successor after shift); or
- Dead-ends (no valid template can fill the remaining empty cells).

A **first-generation source** is a state s such that 0 → ... → s is a Macro path and s's predecessor had L0 full.

### 4.2 Source Completeness

**Definition.** The first-generation enumeration is **complete** when every state reachable from 0 via a single-edge path (fill+shift) has been discovered.

**Theorem 2 (Source Completeness).** If the first-generation tree is enumerated exhaustively (queue empty), then every possible entry point to the Macro graph from state 0 is known.

*Proof.* By construction: the BFS from state 0 explores every legal template choice at every reachable frontier state until no unexplored states remain. Any state reachable from 0 by one Macro edge (fill one layer + shift) must be reachable in this BFS, because the BFS explores exactly those transitions.

### 4.3 Source Classification

Each source can be classified as:
- **Dead-end**: no outgoing Macro edges (no valid template sequence can fill its L0).
- **Recurrent**: has at least one outgoing Macro edge.

---

## 5. SCC Decomposition

### 5.1 Strongly Connected Components

A **strongly connected component (SCC)** of the Macro graph is a maximal set of states where every state is reachable from every other.

The SCC decomposition partitions the state space into:
- **Recurrent SCCs**: SCCs that are not terminal (have outgoing edges within the SCC).
- **Transient states**: states that eventually reach an SCC but cannot be reached back.

### 5.2 Recurrent SCC Containing State 0

The Macro graph's recurrent behaviour relevant to tilings is the SCC containing state 0, denoted **SCC(0)**. This SCC contains all states that:
1. Are reachable from state 0 (can appear in a Macro walk); AND
2. Can reach state 0 (can return to complete a tiling).

### 5.3 SCC Completeness

**Definition.** The SCC decomposition is **recurrently complete** when every source that is not dead-end belongs to a known SCC, and the union of those SCCs contains all states reachable from 0 that have outgoing edges.

**Theorem 3 (SCC Completeness from Sources).** If:
1. The first-generation sources are completely enumerated (Theorem 2); AND
2. The Macro closure from all sources is fully explored (queue empty); AND
3. Every source is classified as dead-end or assigned to an SCC;

then the resulting SCC decomposition is complete for all states reachable from 0.

---

## 5a. Generalized Gate Theorem

### 5a.1 The Gate State in S

For the S-pentacube, every orientation has z-span = 2. This means that during the fill phase of a Macro edge, every placement touches at least L0 and L1. Consequently, the only way to reach a state with L1 = L2 = ∅ after the fill is to start with L1 = L2 = ∅ and fill L0 completely using pieces that do not touch L1 or L2. Since S has no flat orientations (z-span = 1), this is impossible unless L0 is already full. Therefore:

```
For S: pred(0) = {(FULL, 0, 0)}
```

The state (FULL, 0, 0) is called the **gate state** G. The cyclicity test reduces to: G is reachable from 0.

### 5a.2 The Generalized Gate Criterion

For a general pentacope, the predecessor set of state 0 depends on the piece's orientation z-span distribution. A Macro edge ends with a shift: T = (old L1, old L2, ∅). For T = 0, we need old L1 = old L2 = ∅. The pre-shift state always has L0 full. Therefore:

```
pred(0) = {states reachable from 0 with L1 = L2 = ∅
           whose remaining L0 cells can be filled without touching L1 or L2}
```

This set depends on whether the piece has **flat orientations** (z-span = 1) that can fill L0 cells without occupying L1 or L2.

**Theorem 3a (Generalized Gate).** For any pentacube P:

- If P has no flat orientations (all orientations have z-span ≥ 2), then pred(0) = {(FULL, 0, 0)}.
- If P has flat orientations (z-span = 1), then pred(0) = {states with L1 = L2 = ∅ that are reachable from 0}.

*Proof.* The shift operation always produces T = (old L1, old L2, ∅). For T = 0, we require old L1 = old L2 = ∅. The fill phase starts from some state S and produces (FULL, L1', L2'). For L1' = L2' = ∅, every placement in the fill phase must avoid L1 and L2. This is only possible if the piece has orientations with z-span = 1 (flat orientations). If no such orientations exist, the only way to have L1' = L2' = ∅ is to start with L0 already full, i.e., S = (FULL, 0, 0).

### 5a.3 Empirical Verification

| Piece | Cross-section | Flat orientations? | pred(0) | Gate = (FULL,0,0)? |
|-------|---------------|-------------------|---------|-------------------|
| S | 4×5 | No | {(FULL,0,0)} | Yes |
| S | 5×6 | No | {(FULL,0,0)} | Yes |
| S | 4×8 | No | {(FULL,0,0)} | Yes |
| T | 3×7 | Yes (4 of 12) | {2 states with L1=L2=∅} | No |
| T | 5×5 | Yes (4 of 12) | {2 states with L1=L2=∅} | No |

### 5a.4 Computational Consequences

The generalized gate criterion changes the cyclicity test from:

> Is (FULL, 0, 0) reachable from 0?

to:

> Is any state with L1 = L2 = ∅ (other than 0) reachable from 0?

This is a simple check: during the first-generation BFS, record any state where L1 = L2 = 0 and L0 is not empty. If such a state exists, the graph is cyclic.

---

## 6. Graph Period Theorem

### 6.1 Graph Period

**Definition.** For a strongly connected directed graph G, the **period d** is:

```
d = gcd{ length(γ) : γ is a closed walk in G }
```

Equivalently, d is the gcd of all differences dist[v] − dist[u] − 1 over edges u→v, where dist is a BFS distance from an arbitrary root.

**Theorem 4 (Period from Distance).** For any strongly connected graph G:

```
d = gcd{ dist[v] − dist[u] − 1 : (u→v) ∈ E(G) }
```

where dist is computed from any BFS spanning tree rooted at any vertex.

*Proof.* The BFS distance labels each vertex with its distance from the root modulo d. Any edge u→v changes this label by exactly 1 (in the underlying undirected sense). The gcd of the deviations from the expected ±1 gives the period.

### 6.2 Global Period from SCC

**Theorem 5 (Global Period).** Let G be the set of all states reachable from state 0 in the Macro graph. Let SCC₁, SCC₂, ..., SCCₖ be the recurrent SCCs in G, with periods d₁, d₂, ..., dₖ. Then:

Every closed walk from state 0 has length divisible by D = lcm(d₁, ..., dₖ).

*Proof.* Any closed walk from 0 eventually enters some recurrent SCC (possibly after transients). Within that SCC, the walk's length from first entry to exit must be divisible by that SCC's period. The total walk length includes the transient segment plus the cycle segment. The transient segment's length is fixed by the path chosen; the cycle segment's length must be divisible by dᵢ.

For the case where there is exactly one recurrent SCC reachable from 0 that can also reach 0 (SCC(0)), the global period is simply the period of SCC(0).

**Corollary (4×8 case).** For 4×8, SCC(0) has period 10. All 331,765 first-gen sources either dead-end (331,761) or enter SCC(0) (4). There is no other recurrent SCC reachable from 0. Therefore every closed walk from 0 has length ≡ 0 (mod 10).

---

## 7. Primitive Cycle Certificates

### 7.1 Cycle Extraction

Given a physical tiling of a×b×z, a Macro cycle can be extracted by:
1. Processing the tiling layer by layer.
2. Recording the Macro state before each layer fill.
3. Verifying each transition is a legal Macro edge.
4. Confirming the sequence starts and ends at state 0.

### 7.2 Irreducibility

A Macro cycle is **irreducible** if no proper subsequence of its edges forms a closed walk from 0 to 0. Equivalently, no state (other than 0) repeats within the cycle.

### 7.3 Primitive Cycles

A **primitive cycle** is an irreducible closed walk from 0 to 0 that is not a concatenation of shorter such walks.

### 7.4 Cycle Certificate

A **cycle certificate** contains:
- Cross-section (a,b)
- Cycle length z
- Full Macro state sequence
- Edge placement data (concrete coordinates for each piece, relative to the edge's layer)
- Verification hash for each transition
- Irreducibility proof (state non-repetition)

---

## 8. Semigroup Sufficiency Theorem

### 8.1 Numerical Semigroup

Given positive integers c₁, ..., cₖ, the **numerical semigroup** is:

```
⟨c₁, ..., cₖ⟩ = { Σ nᵢ·cᵢ : nᵢ ≥ 0 }
```

### 8.2 Composition Lemma

**Lemma 6 (Cycle Composition).** If Macro cycles of lengths c₁, ..., cₖ exist from state 0, then every z ∈ ⟨c₁, ..., cₖ⟩ is realisable as a closed Macro walk.

*Proof.* Each cycle begins and ends at state 0. Concatenating cycles places the second cycle's pieces in the next z layers (offset by the first cycle's thickness). Since the frontier is empty (state 0) at the junction, the two cycles operate on disjoint layer ranges and cannot interfere. By induction, any concatenation of cycles is valid.

### 8.3 Sufficiency Theorem

**Theorem 7 (Semigroup Sufficiency).** Given verified Macro cycles of lengths c₁, ..., cₖ, every thickness z in the numerical semigroup ⟨c₁, ..., cₖ⟩ admits a physical tiling.

*Proof.* By Lemma 6, each such z has a closed Macro walk. By the Faithfulness Theorem (Theorem 1), each closed walk corresponds to a physical tiling.

### 8.4 Generator Status

Three notions of "generator" must be distinguished:

| Notion | Meaning | How determined |
|--------|---------|----------------|
| **Recovered cycle** | A cycle extracted from a physical witness | SVG/solver extraction |
| **Primitive cycle** | An irreducible cycle | State non-repetition check |
| **Semigroup generator** | A length not generated by others | Arithmetic check |
| **Globally primitive** | Cannot be decomposed using ANY cycles | Requires complete SCC analysis |

---

## 9. Numerical Semigroup Analysis

For a given semigroup S = ⟨c₁, ..., cₖ⟩:

| Property | Definition |
|----------|------------|
| GCD | gcd(c₁, ..., cₖ) |
| Frobenius number | Largest integer NOT in S (if GCD = 1) |
| Conductor | Smallest n such that all m ≥ n are in S |
| Apéry set | Ap(S, m) = {min s ∈ S : s ≡ r (mod m)} for each r |

For GCD > 1, the semigroup only contains multiples of the GCD. The analysis can be scaled by dividing through by the GCD to obtain a "scaled semigroup" with GCD = 1.

---

## 10. Proof Certificate Format

### 10.1 Top-Level Structure

```json
{
  "certificate_version": "1.0",
  "theorem_type": "global | scc-local | cycle-only",
  "cross_section": {"a": 4, "b": 8},
  "piece_hash": "...",
  "source_enumeration": {
    "complete": true,
    "total_sources": 331765,
    "dead_end_sources": 331761,
    "recurrent_sources": 4,
    "scc_id": "SCC(0)",
    "scc_size": 478
  },
  "scc_period": {
    "computed": true,
    "period": 10,
    "states_in_bfs": 478,
    "edges_checked": 514,
    "gcd_of_deltas": 10,
    "period_classes": 10
  },
  "primitive_cycles": [...],
  "semigroup": {...},
  "tileability_claim": "..."
}
```

### 10.2 Completeness Levels

| Level | Meaning |
|-------|---------|
| `global` | Full theorem: necessary and sufficient conditions proven |
| `scc-local` | Period and cycles verified for SCC; globality unproven |
| `cycle-only` | Recovered cycles verified; no SCC analysis |
| `catalogue` | External catalogue source (not independently verified) |

---

## 11. Independent Verification

A certificate verifier must independently check:

1. **Source count**: matches the expected source-set size.
2. **Transition legality**: each edge in a cycle certificate is a valid Macro transition.
3. **SCC period**: can be recomputed from the SCC adjacency data.
4. **Semigroup arithmetic**: Frobenius and conductor are correctly computed.
5. **Claim consistency**: the theorem type matches the evidence level.

The verifier does NOT need to rerun the original Macro closure. It only checks the certificate's internal consistency and matches the stated completeness level.

---

## 12. Worked Examples

### 12.1 4×5: Complete Theorem

- Sources: Complete (queue empty)
- SCC(0): 11 states
- Period: 6
- Primitive cycles: {6}
- Semigroup: ⟨6⟩
- **Theorem**: Only 4×5×6 is tileable

### 12.2 5×6: Complete Theorem

- Sources: Complete (queue empty)
- SCC(0): 1,606 states
- Period: 1 (no nontrivial restriction)
- Primitive cycles: {4, 29, 46, 47}
- Semigroup: ⟨4, 29, 46, 47⟩, Frobenius 43, Conductor 44
- **Theorem**: All z ≥ 44 tileable; z ∈ {4, 8, 12, ..., 43} classified individually

### 12.3 4×8: Global Theorem

- Sources: Complete (331,765)
- SCC(0): 478 states
- Period: 10
- Primitive cycles: {20, 130}
- Semigroup: ⟨20, 130⟩, Frobenius 110, Conductor 120
- **Theorem**: z ∈ ⟨20, 130⟩ exactly the tileable set

### 12.4 4×9: SCC-Local Result

- Sources: Bounded (10M cap)
- SCC: Not fully explored
- Recovered cycles: {60, 75, 90, 105} from SVG
- Semigroup: ⟨60, 75, 90, 105⟩, Frobenius 45, Conductor 60
- **Status**: Cycle-only (not global theorem; SCC unproven)

### 12.5 T 3×7: Global Theorem (First Non-S)

- Piece: T (12 orientations, 4 flat)
- Sources: Complete (204 sources, queue empty)
- SCC(0): 39 states, 40 edges
- Period: 20 (computed from distance differences)
- Primitive cycles: {20}
- Semigroup: ⟨20⟩
- Gate: Generalized (pred(0) = {2 states with L1=L2=∅})
- **Theorem**: 3×7×z tileable iff 20 | z
- **Significance**: First global Macro theorem for a non-S pentacube

### 12.6 T 5×5: Global Theorem

- Piece: T
- Sources: Complete (2,834 sources, queue empty)
- SCC(0): 141 states, 168 edges
- Period: 12
- Primitive cycles: {12}
- Semigroup: ⟨12⟩
- Gate: Generalized (pred(0) = {2 states with L1=L2=∅})
- **Theorem**: 5×5×z tileable iff 12 | z

### 12.7 T 3×8: Global Theorem (Period < Shortest Cycle)

- Piece: T
- Sources: Complete (689 sources, queue empty)
- SCC(0): 2,939 states, 3,288 edges
- Period: **5** (period < shortest cycle 15)
- Primitive cycles: {15, 30, 35, 40, 45, ...}
- Semigroup: ⟨15, 30, 35, 40, ...⟩, Frobenius 25, Conductor 30
- Gate: Generalized (pred(0) = {4 states with L1=L2=∅})
- **Theorem**: 3×8×z tileable iff z ∈ ⟨cycle semigroup⟩; all z ≥ 30 tileable
- **Significance**: First T example of period < shortest cycle, matching S 4×8

### 12.8 T 3×10: SCC-Local Result

- Piece: T
- Sources: Complete (6,927 sources, queue empty)
- SCC(0): ~134K+ states (incomplete closure)
- Period: **1** (stable)
- Minimal returns: {10, 14, 26, 27, 28, 30, 31, ..., 96}
- Semigroup: cofinite, Frobenius 29, Conductor 30
- Gate: Generalized (pred(0) = {4 states with L1=L2=∅})
- **Status**: SCC-LOCAL (forward closure incomplete; SCC(0) may be incomplete)

---

## 13. Failure Modes and Limitations

| Issue | Consequence |
|-------|-------------|
| First-gen tree capped | Source completeness unproven; period may not be global |
| SCC closure capped | Recurrent SCC may be incomplete; additional cycles possible |
| No SCC data | Period unknown; only cycle-length gcd available |
| Catalogue-only evidence | No Macro verification; relies on external accuracy |
| Bounded closure queue not empty | Future computation may reveal new states/cycles |

---

## 14. Summary of Levels

| Level | First-gen complete? | SCC complete? | Period computed? | Cycles verified? |
|-------|--------------------|---------------|------------------|------------------|
| GLOBAL THEOREM | ✓ | ✓ | ✓ | ✓ |
| SCC-LOCAL | ✗ | ✓ (within bound) | ✓ | ✓ |
| CYCLE-ONLY | ✗ | ✗ | ✗ | ✓ |
| CATALOGUE REFERENCE | ✗ | ✗ | ✗ | ✗ |

---

## 15. Files

- This document: `docs/frontier/macro_proof_methodology.md`
- Certificate verifier: `tools/frontier/verify_macro_proof.py`
- Generic Macro explorer: `tools/frontier/macro_explorer.py`
- Generic piece utilities: `tools/frontier/piece_utils.py`
- S-pentacube certificate data: `data/frontier/s_piece/certificates/`
- T-pentacube certificate data: `data/frontier/t_piece/`

## 16. Tests

All existing tests pass:
- `test_macro_construction.py` — 19/19 PASS
- `test_macro_semigroup.py` — 6/6 PASS
- `test_cycle_extraction.py` — 10/10 PASS
- `test_macro_orientation.py` — 29/29 PASS
- `test_t_macro.py` — 15/15 PASS (T-specific tests)
- `verify_macro_proof.py` — S 5×6 global certificate, T 3×7 global certificate

---

## 17. The Remaining Question

**What determines whether a cross-section's Macro graph has a global period > 1?**

The answer is known for the five proven cases:
- S 4×5: period 6 (from SCC structure)
- S 5×6: period 1 (no restriction)
- S 4×8: period 10 (piece-count → factor 5; SCC → factor 2)
- T 3×7: period 20 (complete closure, single recurrent SCC)
- T 5×5: period 12 (complete closure, single recurrent SCC)

For the remaining cross-sections (4×9, 4×10, 5×7, 5×8, 5×9, 5×10, T 3×8, T 3×10, T 3×12), the period is inferred from recovered cycles but not proven from complete graph analysis. The outstanding mathematical question is: can the period be predicted from the cross-section dimensions and piece geometry alone, without full graph enumeration?

**What is the most important remaining question for T?**

The T-pentacube has been fully characterized for two cross-sections (3×7 and 5×5). The most important remaining question is:

> **Can the T 3×8 Macro graph be completely closed?**

T 3×8 has area 24, SCC(0) of 273 states, and cycle lengths including 15, 30, 35, 40, ... with GCD 5. The closure was bounded at 200K states. If the closure can be completed, it would yield a third global T theorem and test whether the methodology scales to larger cross-sections within the same piece.

A secondary question:

> **Does T have any cross-section where the period is not simply the minimal cycle length?**

For both T 3×7 and T 5×5, the period equals the minimal cycle length (20 and 12 respectively). This contrasts with S 4×8 where the period (10) differs from the minimal cycle length (20). Understanding when period ≠ minimal cycle length is an open question.
---

## 18. V-Pentacube Addendum (2026-08-26)

The framework's third validation, documented fully in
`docs/frontier/v_piece/`. Summary of what the V port adds to the *generic*
methodology (S/T sections above are unchanged):

1. **State-depth check formalized.** The 3-layer window is now justified per
   piece by a measured max-z-span census (`v_orientation_table.json`), not by
   analogy. For V: 4 flat + 8 span-3 orientations, no span-2, and — new among
   tested pieces — **no middle-heavy [1,3,1] standing profile**.

2. **Walk↛tiling injectivity refuted on real data.** Replaying all 144
   exhaustive V 5×5×6 tilings shows tiling→walk is many-to-one (144 → 80
   walks). Macro walk counts must never be reported as raw-tiling counts.
   This resolves the historical "Macro misses tilings" calibration puzzle as a
   realization-counting artifact.

3. **Mixed gate structure.** pred(0) for V 3×5 contains both the classic S-style
   gate (FULL,∅,∅) and four flat-completion partial predecessors. The
   generalized terminal-predecessor criterion (§5a) remains correct; its
   instantiation differs per piece.

4. **Exact-walk-length post-analysis promoted to standard step.** Layered BFS
   inside SCC(0) gives the exact achievable set {z : closed walk of length z
   through 0} up to any bound; with faithfulness this yields family-wide
   classifications. First result: **3×5×z tileable ⟺ z ∈ {6,8} ∪ {even ≥ 12}**
   — GLOBAL THEOREM status for the whole 3×5 family, reproducing both published
   primes (6, 8) and all three published impossibility rules (odd, ×4, ×10)
   from one computation.

5. **Period < shortest cycle now proven at complete-closure strength in two
   families.** V 3×5: period 2 < shortest cycle 6. Side result of the same
   benchmark run: the **T 3×8 closure completed** (916,153 states, previously
   bounded at 200K), proving T-period 5 < shortest cycle 15 — answering §17's
   secondary question affirmatively.

6. **Certificate claims enforced mechanically.** The V port adds a claim-level
   verifier (GLOBAL / SCC-LOCAL / VERIFIED CYCLE / CATALOGUE ONLY) plus a
   rejection suite; unjustified GLOBAL claims and structured tileability
   assertions contradicted by exact-length evidence are rejected by test
   (§10–11 machinery extended in `tools/frontier/v_piece/v_claim_verifier.py`).

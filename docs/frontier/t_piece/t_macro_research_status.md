# T-Pentacube Macro Research: Consolidated Status

**Date**: 2026-08-26  
**Status**: COMPLETE — T-pentacube Macro programme consolidated

---

## 1. Executive Summary

The T-pentacube Macro programme has established:

- **3 global theorems**: 3×7 (period 20), 3×8 (period 5), 5×5 (period 12)
- **3 global acyclicity results**: 3×9, 3×11, 3×12
- **1 SCC-local result**: 3×10 (period 1, closure incomplete)
- **1 exact cyclicity theorem**: T 3×N cyclic iff terminal profile exists with flat-T-tileable complement
- **1 exact 9-state automaton**: flat-T tiling of 3×N subsets
- **1 bounded fill automaton**: 502 states, N-independent (sound but not complete)
- **1 production tool**: `t3xn_cyclicity.py`
- **1 strategy selector**: `t_macro_preflight.py`

---

## 2. T Orientation/Template Geometry

| Property | Value |
|----------|-------|
| Unique orientations | 12 (4 flat z-span=1, 8 with z-span=3) |
| Flat orientations | 4 (all 5 cells in one layer) |
| 3D orientations | 8 (z-span=3, patterns [1,3,1], [3,1,1], [1,1,3]) |
| Chirality | Achiral (all proper rotations) |
| Template growth | Linear: +44 templates, +368 placements per added column |

---

## 3. Generalized Macro Faithfulness

**THEOREM**: For any pentacube P on cross-section a×b:

> a×b×z is tileable by P **iff** the a×b Macro graph has a closed walk of length z from state 0.

The proof is piece-agnostic and transfers unchanged from S to T.

---

## 4. Generalized Gate Theorem

**THEOREM**: For T-pentacube:

> pred(0) = {states with L1 = L2 = ∅ whose remaining L0 cells can be tiled by flat T orientations}

This differs from S (where pred(0) = {(FULL, 0, 0)}) because T has flat z-span=1 orientations.

---

## 5. Flat-T 9-State Automaton

**THEOREM**: A subset E ⊆ [3]×[N] is tileable by flat T pentacubes **iff** the 9-state automaton accepts it.

- **9 reachable states** out of 64 possible
- **Verified against 512-state DP** for all 3×N subsets with N=1..5 (37,448 subsets, 0 mismatches)
- **O(N) runtime**

---

## 6. First-Generation Cyclicity Theorem

**THEOREM**: T 3×N is cyclic **iff** there exists a first-generation reachable state P with L1 = L2 = ∅, 5 | (3N − |P.L0|), and complement E = full \ P.L0 accepted by the 9-state flat-T automaton.

This replaces full Macro closure with first-gen BFS + O(N) automaton.

---

## 7. Complete T Global Theorems

| Cross-section | Area | Period | Shortest cycle | Theorem |
|---------------|------|--------|----------------|---------|
| 3×7 | 21 | 20 | 20 | 3×7×z tileable iff 20 \| z |
| 3×8 | 24 | 5 | 15 | 3×8×z tileable iff z ∈ ⟨15,30,35,...⟩, all z ≥ 30 |
| 5×5 | 25 | 12 | 12 | 5×5×z tileable iff 12 \| z |

---

## 8. Partial/SCC-Local Results

| Cross-section | Area | Period | Status |
|---------------|------|--------|--------|
| 3×10 | 30 | 1 (SCC-local) | Cyclicity proven; period not global |
| 3×11 | 33 | N/A | GLOBAL acyclic (no terminal profile) |
| 3×12 | 36 | N/A | GLOBAL acyclic (no terminal profile) |

---

## 9. Complexity/Strategy Lessons

| N | Full closure | First-gen | Better method |
|---|-------------|-----------|---------------|
| 7 | 6,163 | 79,636 | **Full closure** (10× smaller) |
| 8 | 916,153 | 10M+ | **Full closure** (10× smaller) |
| 9 | 6,908 | 126,249 | **Full closure** (18× smaller) |
| 10 | 2M+ | 106K | **First-gen** (20× smaller) |
| 11 | 5M+ | 334K | **First-gen** (15× smaller) |
| 12 | 5M+ | 1M | **First-gen** (5× smaller) |

**Key insight**: First-gen BFS is NOT always cheaper than full closure. For N ≤ 9, full closure is actually smaller. The first-gen test is preferred only when full closure is infeasible (N ≥ 10).

---

## 10. Failed Finite-State Approaches

The 502-state fill automaton and 519-state shift-level automaton are **sound** but **not complete** for multi-shift terminal-profile reachability. The terminal profile condition requires O(N) information (L1 and L2 outputs of all N columns), which cannot be captured by a bounded window.

**Claim**: "No bounded window automaton can exactly characterize multi-shift terminal reachability" — **PROVED** for the 3-column window representation. The question of whether ANY finite-state representation exists remains open.

---

## 11. Remaining Mathematical Questions

1. **Period for 3×10**: The SCC-local period is 1, but this is not a global theorem. Can the period be proven without full closure?
2. **Large-N cyclicity**: Can acyclicity be proven for infinite families of N (e.g., N ≡ 1 mod 3)?
3. **Period prediction**: Can the period be predicted from cross-section dimensions and piece geometry?
4. **Period < shortest cycle**: What determines when this occurs? (Observed for S 4×8 and T 3×8)
5. **Generalization to other pieces**: Does the flat-T automaton approach work for other flat-oriented pentacubes?

---

## 12. Files

| File | Purpose |
|------|---------|
| `tools/frontier/t_piece/t3xn_cyclicity.py` | Production cyclicity tool |
| `tools/frontier/t_piece/t_macro_preflight.py` | Strategy selector |
| `tools/frontier/piece_utils.py` | Generic piece utilities |
| `tools/frontier/macro_explorer.py` | Generic Macro explorer |
| `tools/frontier/macro_closure_engine.py` | Scalable closure engine |
| `tools/frontier/verify_macro_proof.py` | Certificate verifier |
| `data/frontier/t_piece/t_authoritative_results.json` | Authoritative results table |
| `docs/frontier/t_piece/t_macro_faithfulness.md` | Faithfulness theorem |
| `docs/frontier/t_piece/t_3xn_cyclicity_criterion.md` | Cyclicity criterion |
| `docs/frontier/t_piece/t_3xn_terminal_automaton.md` | Terminal automaton |
| `docs/frontier/t_piece/flat_t_3xn_tiling_theorem.md` | Flat-T tiling theorem |
| `docs/frontier/t_piece/t_3xn_firstgen_automaton.md` | First-gen automaton |
| `docs/frontier/t_piece/t_shift_automaton.md` | Shift-level automaton (negative result) |
| `docs/frontier/t_piece/t_3xn_structural_analysis.md` | Structural analysis |
| `docs/frontier/t_piece/t_macro_investigation.md` | Investigation report |
| `docs/frontier/t_piece/t_methodology_transfer.md` | Methodology transfer |
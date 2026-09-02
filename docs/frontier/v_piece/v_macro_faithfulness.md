# V-Pentacube Macro Faithfulness

**Date**: 2026-08-26
**Status**: VERIFIED — faithfulness theorem transfers unchanged; gate structure
is a new mixed form; historical 80-vs-144 calibration discrepancy resolved as
a one-to-many realization effect, not an unfaithfulness.

---

## 1. State Depth (Phase 3): the 3-layer window suffices

**Claim.** Three frontier layers are sufficient for an exact Macro
representation of V on any cross-section.

**Proof.**
1. Computed orientation census
   (`data/frontier/v_piece/v_orientation_table.json`): every V orientation has
   z-span ≤ 3 (4 orientations span 1 layer, 8 span exactly 3; none spans 2).
2. A template is normalized so its lowest cell sits on window layer 0; its
   cells therefore land on layers 0..z_span−1 ⊆ {0,1,2}.
3. Hence the fill phase never writes outside the 3-layer window, and after a
   shift every still-relevant occupancy lies inside the new window.
4. No assumption about S or T profiles was used — only the computed max
   z-span of V itself. ∎

Remark (deliberate check, not inheritance): V *could* have required more
layers if any orientation had z-span > 3; the survey measured z-span ≤ 3
directly from the geometry. The T/S three-layer model transfers because of
this measurement, not by analogy.

---

## 2. Theorem Statement

> For every cross-section a×b and every z ≥ 1:
>
>     a×b×z is tileable by V pentacubes
>         ⟺
>     the a×b Macro graph has a closed walk of length z from state 0.

---

## 3. Direction A: Tiling → Walk (verified constructively on real data)

Given a tiling 𝒯 of a×b×z define the frontier state before layer k:

    s_k = (occupancy of layers k, k+1, k+2 restricted to pieces with bottom < k)

so s_0 = 0 and s_z = 0. Each step s_k → s_{k+1} is a macro edge:

*The pieces of 𝒯 with bottom exactly k partition layer k.* Place them in
increasing order of their lowest cell id. At each step the current first-empty
cell c is covered by some not-yet-placed piece P; P's template is disjoint
from the occupancy (all its cells are disjoint from all other pieces' cells in
the genuine tiling). Applying P restores the invariant; when layer 0 is full
the shifted occupancy equals s_{k+1}. The BFS in the explorer discovers every
such completion, so the edge exists. Only generic properties were used: each
piece has a well-defined bottom, templates cover all normalized placements,
fill explores all first-empty-cell choices.

### Empirical verification (third geometry, exhaustive data)

All **144** raw solutions of the exhaustively verified 5×5×6 box
(`data/v_5x5x6_complete_solutions.json`) were independently revalidated
(bounds/congruence/disjointness/exact coverage) and replayed
(`tools/frontier/v_piece/v_faithfulness_replay_5x5x6.py`):

| Check | Result |
|---|---|
| Independent tiling revalidation | 144/144 valid |
| Constructive first-empty replay produces the induced walk | 144/144 |
| Induced transitions are edges of the true macro graph | 144/144 |
| Distinct induced walks | **80** |
| Realizations per walk | 1 or 2 (e.g. 2,2,2,…; Σ = 144) |

### Resolution of the historical 80-vs-144 discrepancy

`docs/frontier/v_5x5x6_macro_calibration.md` reported 80 Macro return paths vs
Algorithm X's 144 raw tilings and conjectured that "the first-empty-cell
placement restriction misses some tilings". The replay above shows that
interpretation is **incorrect**: every tiling induces a legal walk (nothing is
missed). The map *tiling → walk* is simply **many-to-one**: two tilings can
fill each layer in different orders/placements while producing identical
frontier states, and the Macro graph intentionally abstracts exactly that away.
The earlier reconstruction enumerated one realization per walk, hence 80.
Faithfulness is intact; only the raw-count semantics differed. (Orbit counts
agreed all along: both give 9 symmetry orbits.)

---

## 4. Direction B: Walk → Tiling

Same argument as S/T, no V-specific content: realizing each edge of a closed
walk 0 = s_0 → … → s_z = 0 with any concrete fill (which the template set
provides) yields placements that (a) are congruent to V, (b) are pairwise
disjoint, (c) complete layer k of edge k, hence tile the box exactly. The
certificate machinery (Layer A checker) validates such realizations by pure
set arithmetic.

---

## 5. Terminal / Gate Structure (Phases 9 data, stated here for the theorem)

Measured on the complete 3×5 closure (`v_3x5_closure_analysis.json`):

    pred(0) = 5 states, ALL with L1 = L2 = ∅:
      - four states with L0 popcount 10  (exactly one flat V missing)
      - the classic gate G = (FULL, ∅, ∅)

This is a **mixed structure, new among S/T/V**:

| Piece | pred(0) form | Classic gate reachable? |
|-------|--------------|------------------------|
| S     | {(FULL,∅,∅)} only | yes (it is the unique predecessor) |
| T     | partial states only | no — (FULL,0,0) is not even a macro state on tested sections |
| V 3×5 | partial states **and** (FULL,∅,∅) | yes |

Both facts trace to V's flat orientations (as with T, partial predecessors can
be completed without touching L1/L2) *and* to the reachability of a full-layer
boundary with empty upper window (as with S but unlike tested T sections).

**Generalized terminal-predecessor criterion (piece-specific instantiation):**

> The graph is cyclic ⟺ some state P ≠ 0 with L1 = L2 = ∅ is reachable from 0
> whose remaining L0 cells can be covered by flat (z-span-1) placements alone.

For V 3×5 the remaining-L0 count of each partial predecessor is 5 ≡ 0 mod 5 —
covered by exactly one flat V. (The mod-5 coincidence is a corollary of flat
V being a 5-cell layer piece here; it is *not* proposed as a general test —
see the certificate format's field taxonomy.)

---

## 6. Consequences

1. **Cyclicity**: V 3×5 admits closed walks (state 0 reachable; 220
   first-generation sources; SCC(0) size 243).
2. **Global classification (3×5)**: combining faithfulness with the exact
   walk-length computation
   (`data/frontier/v_piece/v_3x5_exact_walk_lengths.json`):
   3×5×z tileable ⟺ z ∈ {6,8} ∪ {even z ≥ 12} — reproducing the published
   primes (6, 8) and published impossibilities (odd, ×4, ×10) in one object.
   Status: **GLOBAL THEOREM** for the 3×5 family (proof: faithfulness +
   exact bounded BFS + eventual periodicity with conductor 11, period 2).
3. **Period < shortest cycle** occurs for V as well (period 2, shortest
   simple cycle 6) — third geometry exhibiting the phenomenon.

---

## 7. Component Status Table

| Component | S | T | V | Universal? |
|-----------|---|---|---|------------|
| Direction A proof | same | same | same (verified on 144 tilings) | **YES** |
| Direction B proof | same | same | same | **YES** |
| 3-layer state depth | ✓ | ✓ | ✓ (measured, not assumed) | YES for z-span≤3 pieces |
| Fill-then-shift edge | ✓ | ✓ | ✓ | **YES** |
| Template normalization | bottom cell → L0 | same | same | **YES** |
| Gate = single (FULL,∅,∅) | yes | no | **partly** (mixed) | NO — piece-specific |
| Flat-completion terminal class | n/a | yes | yes | piece-specific |
| Classic gate present | yes | no | **yes** | piece-specific |
| Walk↛tiling injectivity | — | — | **refuted** (many-to-one) | NEVER assumed |

# T 3×N Cyclicity Criterion — Revised

**Date**: 2026-08-26 (revision 2)
**Supersedes**: the 2026-08-26 revision of this document and its companion JSON,
both of which contained false acyclicity claims for 3×11 and 3×12.
**Audit provenance**: an independent audit on 2026-08-26 refuted the superseded
version constructively (CP-SAT tilings of the published prime boxes 3×12×15 and
3×11×30, whose induced Macro walks close at state 0 with every edge legal under
the repository transition). See §9 (Errata) and §10 (Artifacts).

---

## 0. Status labels used in this document

| Label | Meaning |
|-------|---------|
| **THEOREM** | Deductively proved from the Macro model definition; no computational input needed beyond finite checks of orientation profiles. |
| **PROVED COMPUTATION** | Established by a completed, uncapped, deterministic computation or by an explicitly stored, independently re-verifiable construction (e.g., a tiling certificate whose induced walk is checked edge-by-edge against the repository transition code). |
| **EMPIRICAL OBSERVATION** | Observed in searches that may have been capped, partial, or semantically ambiguous; not relied upon. |
| **CONJECTURE** | Plausible, unproven, no counterexample known. |
| **REFUTED CLAIM** | A specific earlier claim shown false, with the counterexample cited. |

---

## 1. The Macro model (fixed vocabulary)

Cross-section a×b, NCELLS = a·b. A **state** packs three layer masks
(L0, L1, L2). A **template** is a concrete piece placement normalized so that
its bottom-layer cells lie in slot 0, registered under every bottom cell it
covers. A **fill** from state s repeatedly takes the lowest-index empty slot-0
cell and branches over all templates anchored there; whenever slot 0 becomes
full, the result (FULL, A, B) yields the post-shift state **(A, B, ∅)**. A
**Macro edge** is u → v iff v is a post-shift state of some fill from u. The
**Macro graph** has as nodes exactly the post-shift states reachable from 0 =
(∅,∅,∅); consequently every node has L2 = ∅.

Two immediate consequences used throughout:

* (Monotonicity) Fill never removes cells: the final state of a fill contains
  the initial state.
* (Shift shape) Every node has the form (X, Y, ∅).

Faithfulness (tileable box a×b×z ⟺ closed Macro walk of length z through 0)
is proved in `t_macro_faithfulness.md` and is exercised constructively by the
witness certificates of §10. **THEOREM** (unchanged).

---

## 2. The gate theorem (preserved)

> A state P is a predecessor of 0 (i.e., P → 0 is a Macro edge) **iff**
> P has L1 = L2 = ∅ **and** the complement of P.L0 in the layer
> (a·b − |P.L0| cells) is **exactly coverable by flat T orientations**
> (z-span = 1 placements lying wholly in slot 0).

**Proof.** (⇒) If P → 0, the fill from P ends at (FULL, ∅, ∅). By monotonicity
P.L1 = ∅ (and P.L2 = ∅ always holds for nodes). Every template applied during
the fill must avoid slots 1 and 2 entirely. The T orientation profile set is
{(5,0,0) ×4, (1,3,1) ×4, (3,1,1) ×2, (1,1,3) ×2}; every non-flat profile meets
slot 1, so only the four flat orientations were usable, and they covered
exactly the complement of P.L0. (⇐) Given such P and an exact flat cover of
its complement, the fill procedure realizes it: branching on the lowest empty
cell is complete for exact cover (the lowest uncovered cell must be covered by
some piece of the cover, and templates[c] enumerates every placement whose
bottom contains c). No cell lands outside slot 0, so the fill ends at
(FULL, ∅, ∅), whose shift is 0. ∎ **THEOREM**

Degenerate cases: P with P.L0 = FULL (empty complement) is vacuously covered
(the empty set of pieces) and shifts directly to 0. P = 0 itself is a
predecessor of 0 iff the whole layer admits an exact flat-T cover (a rectangle
tiling by T pentominoes; none exists for the volume-viable 3-wide layers,
3×5 / 3×10 / 3×15, re-verified computationally on 2026-08-27 — the original
"tested sizes" were otherwise unstated) — consistent with the classical result
that the T pentomino tiles no rectangle. **PROVED COMPUTATION** for tested sizes.

---

## 3. Divisibility is necessary only

Since each flat orientation covers exactly 5 cells, every predecessor of 0
satisfies 5 ∣ (a·b − |P.L0|). **THEOREM** (necessity).

The superseded version claimed the converse — that 5 ∣ (a·b − |P.L0|) together
with L1 = L2 = ∅ suffices for P → 0. **REFUTED CLAIM.** Counterexample:
cross-section 2×5 (NCELLS = 10). No flat T placement fits (every flat
orientation has bounding box 3×3), so no subset of size ≡ 0 (mod 5) is
flat-coverable; the full Macro graph has no node with a predecessor edge to 0
(indeed no complete fill exists at all: two pieces would have to tile the layer
flat, impossible). Yet P = 0 is reachable with 5 ∣ (10 − |L0|). Exact
coverability, not divisibility, is the operative condition.

---

## 4. Predecessors of 0 occur at depth ≥ 2 (and possibly arbitrarily deep); first-generation BFS is not sufficient

A node (X, Y, ∅) with Y ≠ ∅ can be the ancestor of a node (X′, ∅, ∅): a single
fill that avoids the parent's slot 2 (using span ≤ 2 pieces, i.e. profiles
(5,0,0)/(1,3,1)/(3,1,1)) produces spill (X′, ∅) regardless of the parent's own
Y. Depth caveat: depth ≥ 2 is demonstrated (3×7); that the depth is unbounded is
plausible by the mechanism above but not proved — no invariant bounds it, and
no arbitrarily deep predecessor has been constructed.

**Demonstration on 3×7 (smallest cyclic case):** generation-1 fills from 0
produce 204 sources, and **none** of them has Y = ∅ (L1-empty). Nevertheless
the completed closure contains exactly two predecessors of 0 (both |L0| = 11,
both L1 = L2 = ∅). Both therefore sit at depth ≥ 2. Any search restricted to
first-generation states finds no candidate at all — on the very cross-section
where cyclicity was first established. **REFUTED CLAIM**: "First-gen BFS
sufficiency for T — THEOREM". It was never proved, and it is false.

What first-gen *does* provide soundly: a pool of depth-1 candidates, and hence
a sound *one-sided* witness rule (§8).

---

## 5. Corrected cyclicity criterion and decision procedure

> **Criterion.** The T a×b Macro graph is cyclic (admits a closed walk through
> 0) **iff** some reachable node P satisfies the gate theorem of §2: L1 = L2 = ∅
> and comp(P.L0) exactly flat-coverable. **THEOREM** (immediate from §2 plus
> the definition of a closed walk: the last edge into 0 departs from a
> predecessor of 0, and conversely).

> **Decision procedure.** Breadth-first Macro closure from 0 with early exit:
> return CYCLIC as soon as a node meeting the §2 conditions is found
> (constructively — build the actual flat cover); return ACYCLIC only when the
> queue empties with no cap hit. **PROVED COMPUTATION** methodology; correct by
> §2 + §5. There is **no** known cheaper complete test (see §8).

Cost honesty: the procedure costs what full closure costs. The superseded
document's first-generation cost table (§5.2 there) is retired: first-gen size
says nothing about completeness for this question.

---

## 6. Reclassified 3×N results

Independent computations performed for this revision: complete Macro closures
for 3×7 (6,163 states) and 3×9 (6,908 states), agreeing exactly with the
repository's completed runs; CP-SAT tilings of five published prime boxes with
edge-by-edge walk validation against the repository transition
(`tools/frontier/validate_t_macro_walk.py`; see §10). Catalogue files were not
modified.

| Cross-section | Cyclic? | Status | Evidence |
|---|---|---|---|
| 3×7 | **YES** | PROVED COMPUTATION | Complete closure 6,163 states (this audit + repo agree); pred(0) = {two nodes, \|L0\|=11}, both at depth ≥ 2; SCC(0) = 39 with cycle set {20}; constructive tiling of catalogue prime 3×7×20 (validated witness). Period-20 claim consistent with sole catalogue prime 20. |
| 3×8 | **YES** | PROVED COMPUTATION (cyclicity) | Constructive tiling of catalogue prime 3×8×15 (validated witness; final pred \|L0\|=14, remaining 10 flat-covered). Full-closure period/gcd data remain EMPIRICAL OBSERVATION: the repo closure for 3×8 has not been independently reproduced uncapped, and `test_macro_closure_3x8` runs capped (max_states = 500 000) without asserting the cap flag — flagged in §9. |
| 3×9 | **NO** | PROVED COMPUTATION (acyclicity) | Independent complete closure: 6,908 states, no predecessor of 0; reachable L1=L2=∅ nodes have \|L0\| ∈ {9, 11, 14} with complements {18, 16, 13}, none divisible by 5 (gate-necessity suffices). Consistent with Sillke 1993 ("3×9×N = 0") and with t_catalogue's impossible_reason rule, which publishes the whole 3×9 family as impossible (re-verified by full closure reproduction, 2026-08-27). |
| 3×10 | **YES** | PROVED COMPUTATION (cyclicity) | Constructive tiling of catalogue prime 3×10×14 (validated witness; final pred \|L0\|=15, remaining 15 flat-covered). The earlier "period 1 / minimal returns {10, 27}" statements are downgraded to EMPIRICAL OBSERVATION: the underlying closure is incomplete and unreproduced, and SCC-internal cycle lengths were conflated with closed walks through 0. Audit correction (2026-08-27): the previously cited "catalogue searched-no-solution entry for Box(3,10,10)" does not exist — `t_catalogue.py` has listed Box(3,10,10) in RAW_PRIMES since its creation and never in SEARCHED_NO_SOLUTION — so the former inference that those returns "cannot have been closed walks through 0" is withdrawn as unsupported; if anything, the published prime 3×10×10 is *consistent* with a length-10 closed walk through 0 under the faithfulness theorem. The downgrade itself stands on the incompleteness/non-reproduction grounds. (see §7). |
| 3×11 | **YES** | PROVED COMPUTATION | Constructive tiling of catalogue prime 3×11×30 (validated witness; walk length 30 closes at 0; final pred \|L0\|=28, remaining 5 flat-covered). Superseded ACYCLIC claim **REFUTED**; superseded "reachable L1=L2=∅ values = {5}" **REFUTED** (28 witnessed). Agrees with catalogue primes 30–55 and with Sillke/Shirakawa data. |
| 3×12 | **YES** | PROVED COMPUTATION | Constructive tiling of catalogue prime 3×12×15 (validated witness; walk length 15 closes at 0; final pred \|L0\|=21, remaining 15 flat-covered). Superseded ACYCLIC claim **REFUTED**; superseded "{5}" claim **REFUTED** (21 witnessed). |
| 5×5 | YES | PROVED COMPUTATION (cyclicity) | Constructive self-contained Macro-walk certificate `data/frontier/certificates/t_5x5x12_cycle01_macro_walk.json` (closed walk of length 12 through 0; packed from the existing complete-closure artifact's primitive cycle, verified by both Layer-A checkers + C++ verifier + `validate_t_macro_walk.py`, gate clause realized at the terminal edge — see `t_5x5x12_macro_walk_certificate.md`). Underlying closure data: repo run of 54,434 states (`queue_exhausted=true`, `cap_hit=false`); catalogue prime 5×5×12 consistent. |

Unchanged valid results retained from the superseded version: orientation
profile facts (§2), the 3×7 and 3×9 closures and their derived quantities, the
piece-count integrality theorem (if 5 ∤ a·b then every cycle length is divisible
by 5 — THEOREM, elementary), and the S-pentacube contrast, which survives only
as an EMPIRICAL OBSERVATION about first-generation scans (the inference drawn
there — that S needs full closure — remains plausible but was never a
characterization of pred_S(0)).

---

## 7. Reconciliation with the catalogue and sibling documents

Every prior conclusion inconsistent with published tileable boxes is resolved
as follows (no catalogue truth table was modified):

1. **t_catalogue.py RAW_PRIMES** lists 3×11×{30,35,40,45,50,55} and
   3×12×{15,20,25}. Under the faithfulness theorem these imply CYCLIC for both
   cross-sections. The superseded criterion claimed ACYCLIC — a direct
   contradiction resolved by abandoning the claim (REFUTED) and by the
   constructive witnesses above.
2. **t_3xn_structural_analysis.md §2.2** records closures for N = 9 and N = 11
   as "Not done" and N = 12 as "Incomplete", while the superseded JSON labelled
   3×9 and 3×11 "closure complete". Both same-day documents cannot be right;
   the structural document's account is the accurate one. This revision marks
   3×9 acyclicity as proved via a fresh completed closure and withdraws all
   unsupported "closure complete" labels.
3. **t_macro_faithfulness.md §6.1** already listed 3×12 as "YES" cyclic — again
   contradicting the superserved criterion. That row was correct.
4. **t_macro_faithfulness.md §5.2/§5.3** states pred(0) = "{states with
   L1 = L2 = ∅}", omitting the exact-flat-coverability clause. As stated it is
   too loose (see §3 counterexample style); the precise statement is §2 here.
   Flagged; that document is not edited in this repair.
5. **Structural analysis §3.2/§4.1 period semantics**: "period" values mix gcds
   of SCC-internal cycle lengths with closed-walk-through-0 lengths. Only the
   latter witness box tilings. All period/gcd assertions except 3×7's {20}
   (confirmed by completed closure) are downgraded to EMPIRICAL OBSERVATION.

---

## 8. Is a corrected cheap test possible?

* **Sound witness rule (cheap, incomplete).** During any bounded search, if a
  reachable node P with L1 = L2 = ∅ is found and comp(P.L0) is *constructively*
  flat-covered, return CYCLIC. Sound by §2; often hits early (all five
  witnesses here were found this way, via tilings). Never sufficient for
  ACYCLIC.
* **Per-node filter (cheap, weak).** 5 ∤ (a·b − |P.L0|) rules out P as a
  predecessor. Useful only inside an exhaustive sweep; concludes nothing alone
  (divisibility is not sufficient, §3).
* **No cheap complete test.** Concluding ACYCLIC requires exhausting all
  reachable nodes, i.e. closure; predecessors occur at arbitrary depth (§4),
  and no invariant currently bounds that depth. Any claim that first-gen (or
  any fixed-depth) truncation decides the question is refused by default.
  CONJECTURE (open): some residual-set or congruence invariant might prune the
  search space substantially for 3-wide strips; no such invariant is currently
  proved, and none is assumed here.

---

## 9. Errata against the superseded revision

1. **False**: "A state P is a predecessor of 0 iff P has L1 = L2 = ∅ and R is
   divisible by 5." Sufficiency removed; divisibility is necessary only
   (counterexample 2×5; general gap between arithmetic and coverability).
   Replaced by the §2 gate theorem with the exact-cover clause.
2. **False**: "First-gen BFS sufficiency for T — THEOREM." No proof existed;
   false in general; demonstrably inadequate even on 3×7 (zero depth-1
   L1=L2=∅ sources among 204; two predecessors exist at depth ≥ 2). §5.1's
   algorithm additionally returned CYCLIC on divisibility alone (unsound) and
   excluded P = 0 (boundary incompleteness when 5 ∣ ab).
3. **False**: 3×11 and 3×12 classified ACYCLIC with pred_of_0_count = 0.
   Refuted constructively (3×11×30, 3×12×15 witnesses); contradicted
   t_catalogue RAW_PRIMES, t_3xn_structural_analysis §2.3, and
   t_macro_faithfulness §6.1.
4. **Unsupported**: "Reachable L0 values = {5}" for 3×11 and 3×12 (real
   reachable values include 28 and 21 respectively); "CONFIRMED (state 0 not
   reachable, closure complete)" for 3×11 contradicts the structural
   document's "Not done".
5. **Downgraded**: all period/gcd/semigroup assertions except 3×7 cycle {20};
   the 3×10 "period 1" statement is semantically conflated (SCC-internal
   cycles vs closed walks through 0) and conflicts with the catalogue's
   3×10×10 impossibility if read as walks through 0.
6. **Flagged (not edited)**: `test_macro_closure_3x8` runs a capped closure
   (500 000 states) and does not assert the cap flag; its runtime makes it
   unusable as a quick regression gate. 3×8 cyclicity should rest on the
   constructive witness instead.
7. **Retained**: gate theorem (with clause restored), 3×7/3×9 closures,
   piece-count integrality, orientation-profile facts, S comparison as
   observation only.
8. **Corrected (2026-08-27 audit)**: §6's 3×10 caveat had cited a
   "catalogue searched-no-solution entry for Box(3,10,10)" that
   `t_catalogue.py` never contained — Box(3,10,10) has been in RAW_PRIMES
   since the catalogue was created and appears nowhere in SEARCHED_NO_SOLUTION.
   The inference drawn from it ("those returns therefore cannot have been
   closed walks through 0") is withdrawn as unsupported; the EMPIRICAL
   OBSERVATION downgrade stands on its remaining grounds (incomplete,
   unreproduced closure; conflated semantics). The 3×9 row's "consistent with
   t_catalogue SEARCHED_NO_SOLUTION" citation was likewise corrected to the
   impossible_reason published-impossible rule. Also in this audit: §4's
   heading was softened from "arbitrary depth" to "depth ≥ 2, possibly
   arbitrarily deep" (unboundedness is not proved); §2's degenerate-case
   "tested sizes" were made explicit (3×5, 3×10, 3×15 — all whole-layer flat-T
   covers absent) and the machine-readable twin was updated in step. Full
   verification log: the 3×7 closure figures (6,163 states; preds of 0 =
   two nodes |L0| = 11 at depth ≥ 2; SCC(0) = 39 with cycle-length gcd 20),
   the 2×5 counterexample, and a fresh complete 3×9 closure (6,908 states,
   no predecessor of 0, reachable L1=L2=∅ |L0| values {9, 11, 14}) were all
   reproduced by rerun on 2026-08-27.
9. **3×8 discrepancy resolved (2026-08-27 audit)**: "SCC(0) = 273"
   (`t_macro_faithfulness.md` §6.1, `t_macro_investigation.md`) vs
   "SCC(0) = 2,939" (`t_3xn_structural_analysis.md` §2.2) is not a
   metric conflict: both are ancestor-sets of state 0 under the same
   transition; 273 was computed on a closure truncated at exactly
   max_states = 200,000 (cap hit), 2,939 on the completed uncapped
   closure of 916,153 states. Both values reproduced exactly by rerun
   (2026-08-27); full independent verification in the corrected
   documents and `t_3x8_global_certificate.json`. This does not affect
   the cyclicity verdict above, which rests on the constructive witness.

## 10. Artifacts and reproduction

Machine-checkable witnesses (each validated: disjoint exact cover; shapes
against proper-rotation orientation set; induced walk closes at 0; **every
edge legal under the repository transition**; final predecessor satisfies §2
constructively):

| Box | File | Final pred \|L0\| / remaining |
|---|---|---|
| 3×7×20 | `data/frontier/t_piece/t_3x7x20_cpsat_tiling.json` | 11 / 10 |
| 3×8×15 | `data/frontier/t_piece/t_3x8x15_cpsat_tiling.json` | 14 / 10 |
| 3×10×14 | `data/frontier/t_piece/t_3x10x14_cpsat_tiling.json` | 15 / 15 |
| 3×11×30 | `data/frontier/t_piece/t_3x11x30_cpsat_tiling.json` | 28 / 5 |
| 3×12×15 | `data/frontier/t_piece/t_3x12x15_cpsat_tiling.json` | 21 / 15 |

Reproduce:

```
python3 tools/frontier/validate_t_macro_walk.py data/frontier/t_piece/t_3x*_cpsat_tiling.json
python3 tools/frontier/test_t_macro.py        # orientation/closure/SCC tests
```

**Certificate format v2 (2026-08-26 validation pass).** Each witness JSON now
also embeds `conventions` (cell indexing, state packing, piece geometry,
proper-rotation rule), the explicit walk states, and per-edge fill placements
in window coordinates. This makes the certificates checkable by
`tools/frontier/check_macro_certificate_independent.py`, which imports
**nothing from this repository**: edge legality is verified by direct set
arithmetic against the declared conventions, shapes by signed-permutation-
matrix congruence, and the box tiling is reconstructed from the fills and
cross-checked against the stored placements. Run it isolated:

```
cd /tmp && python3 -I <repo>/tools/frontier/check_macro_certificate_independent.py \
    <repo>/data/frontier/t_piece/t_3x*_cpsat_tiling.json
```

Circularity note: `validate_t_macro_walk.py` checks edges against the
repository's own template machinery (`piece_utils.build_templates`, shared
with `macro_explorer.py`), so it establishes *consistency with the repository
implementation* but not full independence; the v2 certificates plus the
independent checker close that gap. All five witnesses pass both checkers;
mutation tests (shifted fill cell, flipped walk bit, corrupted placement) are
rejected.

Solver: OR-Tools CP-SAT 9.15.6755 (2026-08-26). Independent closures in this
repair: 3×7 → 6,163 states (cyclic, preds {11,11}); 3×9 → 6,908 states
(acyclic). Machine-readable summary: `data/frontier/t_piece/
t_3xn_cyclicity_criterion.json` (revision 2).

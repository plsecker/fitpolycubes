# V-Pentacube Macro Investigation

**Date**: 2026-08-26
**Status**: COMPLETE for first cross-section (3×5); GLOBAL classification obtained
**Companion documents**: `v_source_survey.md`, `v_macro_faithfulness.md`,
`v_methodology_transfer.md`, `data/frontier/v_piece/v_macro_results.json`

Claim-level conventions used throughout (mandatory labels):

* **GLOBAL THEOREM** — proven for the whole family (all z) on a cross-section.
* **GLOBAL CYCLICITY** — closed walks exist for the cross-section, periods unproven.
* **SCC-LOCAL** — proven only within the explored recurrent component.
* **VERIFIED CYCLE** — concrete realized walk, validated end-to-end.
* **CATALOGUE FACT** — published/recorded result, not re-proven here.
* **HYPOTHESIS** — conjecture, explicitly unproven.

---

## 1. Geometry summary (Phase 1–2)

V is the flat corner pentacube `[[0,0,0],[1,0,0],[2,0,0],[0,1,0],[0,2,0]]`.

| Property | Value |
|---|---|
| Unique orientations (proper rotations) | 12 |
| Chirality | achiral (mirror ⊂ orbit) |
| z-span distribution | 4 × span-1 (flat), 8 × span-3 |
| Layer profiles | [5,0,0] ×4, [3,1,1] ×4, [1,1,3] ×4 |
| Middle-heavy [1,3,1] | **impossible** (corner layer always carries the 3-arm) |
| Standing footprints | 3×1 / 1×3 strips only |
| Templates | 172 @ 3×5 · 296 @ 4×5 · 420 @ 5×5 · 432 @ 3×10 |

Orientation infrastructure was exercised through the generic
`tools/frontier/piece_utils.py`; nothing V-specific was added to generic code
(`data/frontier/v_piece/v_orientation_table.json`, tests in
`tools/frontier/test_v_macro.py`).

## 2. Macro state depth (Phase 3)

Measured max z-span = 3 ⇒ the standard 3-layer frontier window is exact for V.
The sufficiency proof is in `v_macro_faithfulness.md` §1. The transfer rests on
a measurement, not on S/T analogy.

## 3. Faithfulness (Phase 4)

Faithfulness transfers unchanged. New quantitative content:

* All **144** raw solutions of the exhaustively verified 5×5×6 box were
  independently revalidated and replayed under the first-empty-cell discipline:
  144/144 induce legal walks; 144/144 transitions confirmed as true macro-graph
  edges (`tools/frontier/v_piece/v_faithfulness_replay_5x5x6.py`).
* The 144 tilings collapse onto exactly **80 distinct walks** — precisely the
  count reported by the superseded 2026-08-21 calibration. Its interpretation
  ("first-empty-cell restriction misses tilings") is thereby **refuted**: the
  tiling→walk map is many-to-one by design; the old reconstruction took one
  realization per walk.

## 4. First cross-section choice (Phase 5)

**Chosen: 3×5** (area 15 — the smallest area that can hold any pentacube layer
work). Rationale:

* published minimal prime **3×5×6** (Sillke 1993, "3 solutions") — CATALOGUE FACT;
* second prime **3×5×8**, and sharp impossibilities (odd; ×4; ×10) give
  falsifiable predictions;
* template/state counts tiny (172 templates, 45-bit states) ⇒ complete closure
  guaranteed cheap.

Deliberately NOT chosen: 5×9 or other large published primes merely because
data exists (the 5×5 forward exploration already documented a strategy wall at
~9M states — an implementation wall, not a mathematical boundary).

## 5. Complete closure (Phase 6)

Run: generic `macro_explorer.py --piece V --a 3 --b 5`, no cap hit ⇒
**first-generation completeness holds** (BFS exhausted).

| Quantity | Value |
|---|---|
| Concrete placements / templates | 1,248 / 172 |
| First-generation sources | **220** |
| First-gen tree states | 1,126 |
| Macro states | **4,543** |
| Macro edges | **5,494** |
| Total intermediate fill states | 58,243 |
| Closure runtime | **0.28 s** |

SCC topology (Tarjan over the full reachable graph):

| Quantity | Value |
|---|---|
| SCCs total | 4,241 |
| Cyclic SCCs | **13** — one main + twelve 6-state islands |
| Main SCC(0) | 243 states, 362 internal edges |
| Transient states | 4,228 |
| Sink states (no continuation) | 3,186 ≈ 70% of all states |
| Island structure | pure deterministic 6-cycles, three isomorphism types |
| Out-degrees in SCC(0) | {1:178, 2:44, 4:16, 6:4, 8:1} |

## 6. Terminal/gate structure (Phases 4/9)

pred(0) = **5 states**, all with L1=L2=∅:

* 4 partial states with L0-popcount 10 — remaining 5 cells covered by exactly
  one flat V (flat-completion class, T-style);
* the classic gate (FULL,∅,∅) — S-style, present AND a predecessor here.

V therefore instantiates **both** known terminal classes simultaneously
("mixed gate"). The generalized cyclicity criterion applies:

> cyclic ⟺ some reachable state P ≠ 0 with L1=L2=∅ has flat-coverable remainder.

A T-analogous cheap test remains available (flat-completability of L1=L2=∅
states); it was not needed since the full closure costs 0.28 s.

## 7. Physical witnesses and extraction (Phase 7)

Provenance finding: repo-root `placements_V_5x5x6.txt` (696 lines) and
`placements_V_5x5x9.txt` (1164 lines) are **complete placement catalogues**
(every legal placement in the box), not witness tilings. True witnesses:

* `data/v_5x5x6_complete_solutions.json` — 144 verified raw tilings; all 80
  induced length-6 witness walks extracted to
  `data/frontier/v_piece/v_5x5x6_witness_walks.json` (none passes the classic
  gate state mid-walk);
* **new Direction-B realizations** produced here, fully validated:
  * 3×5×6 — 18 pieces, certificate
    `data/frontier/v_piece/v_3x5x6_macro_cycle_certificate.json`;
  * 3×5×8 — 24 pieces, certificate
    `data/frontier/v_piece/v_3x5x8_macro_cycle_certificate.json`;

Both pass the isolated generic Layer-A checker (C1–C7g). Comparison
witness-vs-macro: every witness-induced 5×5×6 walk is a genuine macro-graph
cycle (verified during replay); conversely the macro-discovered primitives {6,8}
realize boxes whose existence the catalogue records. Status: **VERIFIED CYCLE**
for each certificate; catalogue agreement noted separately.

## 8. Period analysis (Phase 8)

Exact method: closed walks through 0 never leave SCC(0) (condensation is a
DAG); layered BFS inside SCC(0) yields the exact achievable set up to any bound
(`tools/frontier/v_piece/v_exact_walk_lengths.py`).

**Result (bound 240):**

> 3×5×z tileable ⟺ z ∈ {6, 8} ∪ { even z ≥ 12 }

* period d = 2 (BFS-delta = achievable-gcd agree);
* shortest simple cycle 6; primitive cycle lengths {6, 8};
* semigroup ⟨6,8⟩ misses exactly one even ≥ 6, namely **10**;
* conductor 11: every even ≥ 12 achievable.

Cross-piece status table (complete closures only):

| Case | Period | Shortest cycle | Primitives | Semigroup | period < shortest? |
|------|--------|----------------|------------|-----------|--------------------|
| S 4×5 | 6 | 6 | {6} | ⟨6⟩ | no |
| T 3×7 | 20 | 20 | {20} | ⟨20⟩ | no |
| T 5×5 | 12 | 12 | {12} | ⟨12⟩ | no |
| **T 3×8** (re-run 2026-08-26, complete at 916,153 states) | **5** | **15** | {15,35,…} | gcd 5 | **YES** |
| **V 3×5** | **2** | **6** | {6,8} | ⟨6,8⟩, gcd 2 | **YES** |

Side result: today's higher-limit run **completed the T 3×8 closure** that had
been capped at 200K states, upgrading "T 3×8 period inferred" to proven
(period 5) and answering the open question recorded in
`docs/frontier/macro_proof_methodology.md` §10 (period ≠ shortest cycle does
occur for T). S 4×8 keeps its documented GLOBAL period-10 theorem (period 10 <
shortest recovered cycle 20).

**Status: GLOBAL THEOREM for the 3×5 family** — faithfulness (mathematics) +
complete closure + exact bounded BFS + eventual periodicity. It reproduces,
from a single object: primes 6, 8 (CATALOGUE FACTS, now re-proven);
impossibilities odd / ×4 / ×10 (published impossibility rules, now theorems).

## 9. Certificate framework (Phase 10)

* Two V certificates packed in generic format v1 (with pinned
  `semantics_id`); both **Layer-A VALID** under the stdlib-only isolated
  checker. The 3×5×6 certificate terminates via the flat-completion class
  (remaining = 5); the 3×5×8 via the classic gate (remaining = 0) — both
  documented terminal classes exercised.
* Claim verifier `tools/frontier/v_piece/v_claim_verifier.py` (Layers B/C)
  classifies CATALOGUE ONLY < VERIFIED CYCLE < SCC-LOCAL < GLOBAL and checks
  structured tileability claims against the exact achievable set.
* Negative suite `test_v_certificate_rejection.py`: moved fill cell, flipped
  state bit, duplicated placement, wrong geometry, bare GLOBAL overclaim, and a
  GLOBAL claim asserting tileable z=10 are ALL rejected; positive controls
  pass. An unjustified GLOBAL claim cannot survive.

## 10. Complexity benchmark (Phase 12)

Selectors run unmodified against V 3×5:

| Selector | Prediction | Actual |
|---|---|---|
| S-area-calibrated `macro_preflight.py` | tractability SMALL; full_closure; ~1,500 sources; ~1,500 macro states; SCC ≈ 11 | SMALL/full_closure correct; sources **220** (7× lower); states **4,543** (3× higher); SCC(0) **243** (22× higher) |
| T-family selector `t_macro_preflight.py --piece V` | "unknown" (no V calibration) | — |

Assessment (per task instruction, not tuned): strategy selection transferred;
the state-count model did not. Area alone is not a portable complexity feature:
at comparable template density (≈11.5 templates/cell) the recurrent core varies
by an order of magnitude across pieces (T 3×7: 39 vs V 3×5: 243). Candidate
general feature for a future model: template density plus flat-orientation
fraction and standing-footprint shape (full-strip vs interior attachment).
Recorded as HYPOTHESIS.

## 11. First genuinely V-specific phenomena (Phase 13)

Ranked:

1. **Mixed gate structure** (both classic gate and flat partial predecessors in
   pred(0)). S showed gate-only, T partial-only; V shows both simultaneously.
   Geometric root: V has flat orientations (→ partial class, like T) *and*
   admits full-layer boundaries with empty upper window as reachable states
   (→ classic gate, unlike tested T sections). Status: measured fact on 3×5;
   HYPOTHESIS that this persists on larger V sections.
2. **Recurrent escape-basin islands at minimal scale**: twelve additional
   6-cycle SCCs beside the main component — deterministic infinite filling
   patterns that can never close a box. S/T small sections had exactly ONE
   cyclic SCC each. Correlate: 70% of all V macro states are sinks.
3. **No middle-heavy standing orientation** ([1,3,1]-free profile census): a
   standing V always puts its 3-cell arm-layer at a z-end — constrains
   intermediate fill states in a way neither S nor T exhibits.
4. **Semigroup gap above the primes**: achievable = {6,8} ∪ evens≥12 leaves the
   published-impossible 10 as an isolated gap — the smallest cross-section where
   the semigroup structure (not just parity/period) carries a nontrivial
   impossibility.

## 12. Test coverage (Phase 15 detail)

17/17 tests in `tools/frontier/test_v_macro.py` (orientation infra, templates,
closure completeness, exact achievable set, period<shortest, mixed gate,
islands, Layer-A certificates, rejection suite). S and T suites re-run clean;
all repository certificates re-verified — see final report section below.

## 13. Best next steps

1. **V 5×5** next cross-section: published primes {6,9,10,11,13,14}; odd prime
   9 predicts **period 1** there — a direct contrast with 3×5's period 2 within
   the same piece. Closure cost unknown; first-gen source count must be measured
   before committing (5×5 forward sets reached ~9M states at depth 6 under the
   old layer-by-layer strategy; the closure engine's strategy differs).
2. Then **V 4×5** (six consecutive published primes 6–11 — richest semigroup
   candidate).
3. Methodological: add flat-fraction/template-density features to the preflight
   model; extend the exact-walk-length tool into the standard post-closure step
   for every future closure.

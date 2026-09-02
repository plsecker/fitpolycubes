# Pre-Promotion Integrity Report

**Date**: 2026-09-01
**Scope**: Q geometry integrity; W/Z/N blanket-rule audit; safe F and Y
promotion packages; patch safety audit.
**No catalogue file was modified in this task.** All changes exist as
proposed patch documents for human review.

---

## Executive summary

**Definitely safe (patch documents ready, zero conflicts, fully verified):**

1. **F 2×N×N + 2×2×N** (`docs/frontier/f_piece/f_2xnn_squares_promotion_patch.md`)
   — 8 boxes UNKNOWN → published_impossible at dims ≤ 20. Every ingredient
   re-verified this session: orientation confinement mechanized over all 24
   orientations; published ingredient confirmed on the live Sillke qu5-f
   page ("Impossible: NxN"); zero overlap with RAW_PRIMES,
   PUBLISHED_SOLUTIONS, SEARCHED_NO_SOLUTION; repository validators pass.
   The unsafe blanket F 2×M×N claim remains **not promoted** (and its
   pending patch document should be marked superseded).

2. **Y thickness-1 published families** (`docs/frontier/y_piece/y_thickness1_published_families_patch.md`)
   — 1×5×N (N ≢ 0 mod 10), 1×6×N, 1×8×N: 6 boxes UNKNOWN →
   published_impossible at dims ≤ 20, 14 searched boxes preserved by an
   explicit guard, zero prime/published-solution conflicts. The published
   wordings were re-checked against the live qu5-y page; the 1×5×10
   solver result (10 solutions) serves as sanity, not proof.

**Suspicious (this audit):**

3. **Q registry geometry is broken** — the registered coordinates are a
   disconnected pseudo-piece incompatible with the catalogue's own
   published 2×2×5 prime. Diagnosis is exact (§ below); corrected
   coordinates are proposed but **not applied**. No existing solver
   artifact is contaminated (verified by repository sweep), so the fix is
   low-risk and should happen before any Q solver work.

4. **W, Z, N blanket impossibility rules are stronger than their
   published evidence** (`docs/frontier/rule_audit/w_z_n_blanket_rules_audit.md`).
   All three are plausibly true — aggressive counterexample searches found
   nothing up to substantial limits — but none is proved beyond a
   strictly smaller core. Replacement patches prepared; applying them
   narrows coverage (70 + 132 + 50 = 252 boxes ≤ 20 dims return to
   UNKNOWN) and is a human decision.

**Must wait:**

5. The blanket F 2×M×N conjecture; W/V/F/Z straight-rectangle questions
   (5-wide strips remain the open class for W/V/F; squares are published-
   impossible for F/V/W but nothing is proved for Z); N finite rectangles
   (bent-strip/quadrant results exist, no finite rectangle known);
   verified-DRAT per-box certificates for any SEARCHED_NO_SOLUTION
   additions in the narrowed families.

---

## Q diagnosis

Full document: `docs/frontier/q_piece/q_geometry_integrity_audit.md`.

* **Exact problem**: `common/registry.py` defines Q as
  `[(0,0,0),(1,0,0),(0,1,0),(1,1,0),(2,2,0)]` — face-**disconnected**
  (a 2×2 square plus a corner-touching cell), spans (3,3,1), 12
  orientations, **cannot fit 2×2×5**. A disconnected set is not a
  pentacube, and the span data contradicts the catalogue's published
  prime-minimal box.
* **What the piece really is** (three independent confirmations): Sillke's
  qu5.61 page opens with the height-map picture `1 2 / 1 1` — a 2×2 square
  with one cube stacked on a corner; exhaustive enumeration shows exactly
  two free pentacubes have spans {2,2,2}, and only the square+corner shape
  tiles 2×2×5 (16 raw tilings; the other candidate — which is registry
  piece A — tiles 0); the corrected shape matches **every** published
  qu5.61 constraint checked (2×2×5 ✓, 2×3×5 ✓, 3×3×{5,6,9} unsat ✓,
  3×5×5 unsat ✓, 3×5×6 SAT ✓, 5×5×5 unsat ✓; 5×5×7 and 3×7×15 corroboration
  running at audit time — published rule C stands regardless).
* **Corrected coordinates (proposed, not applied)**:
  `[[0,0,0],[1,0,0],[0,1,0],[1,1,0],[0,0,1]]` — connected, spans (2,2,2),
  achiral, 24 orientations.
* **Suspect set**: empty today (no Q solver data, no Q invocations in
  tools; catalogue entries are published facts about qu5.61 and remain
  valid). Risk is entirely forward-looking.
* **Side notes**: qu5.61's "complete" list has five primes while the live
  Shirakawa 5-22 page lists six (adds 3×9×15, credited Sillke 1993) —
  page-staleness, flagged not changed; the registry's `kurnell` field
  actually stores Sillke's qu5 numbering; the corrected {2,2,2} spans mean
  the F-style layer theorem **cannot** apply to Q (with the broken spans
  the opposite would have been concluded).

## W / Z / N rule audit

Full document: `docs/frontier/rule_audit/w_z_n_blanket_rules_audit.md`.
Common method: axis-explicit layer reduction (mechanized), strict
separation of published facts / published bent-strip results / derived
consequences / computational evidence, and aggressive counterexample
searches. Searches found **no** violation of any blanket rule (2D
complete ≤ area 200 by two independent methods; squares to 40×40; 5-wide
strips to 5×85; N 2-strips to 2×200; 3D solver zero-solutions on
representative boxes; positive lift controls on L/P/Y all pass) — but a
failed search is evidence only.

### W — `a == 2` / `b == 2` → **TOO STRONG**

* Published: strips with a side ≢ 0 (mod 5) impossible; squares impossible
  ("n*N" — re-read this session; the "N*N ... bend is tilable" line is a
  contrast with the bent strip, not a square construction). Straight
  5k-wide strips: **open** (no 2d-complete stamp; page marked incomplete).
* Provable core: size-2-axis boxes unfit when another dim < 3; otherwise
  impossible iff both other dims ≢ 0 (mod 5).
* Replacement patch prepared (in the audit doc): 70 boxes IMP→UNKNOWN
  (2×5×N, 2×10×N, …), 0 conflicts, unfit sub-cases retained.

### Z — `a <= 2` → **TOO STRONG**

* Published: **nothing** — qu5-z has no 2D section; the live Shirakawa Z
  page starts at 3×[3-22]×N with no 1×/2× rows.
* Provable core: unfit sub-cases only (1×1×N, 1×2×N, 2×2×N).
* Replacement patch prepared: 132 boxes IMP→UNKNOWN, 0 conflicts.
  Utility trade-off flagged; honest alternative (relabeling rather than
  narrowing) needs a catalogue-semantics decision.

### N — `a <= 1` → **TOO STRONG**

* Published: "Zx{3,5}" strips impossible — that is all. The catalogue's
  own TODO comments admit the rules were never decoded. "N*N (the
  quadrant) is possible" via bent 2-strips — infinite regions, not finite
  rectangles; "no strips (one side open) of width k" concerns semi-
  infinite strips.
* Provable core: 1×1×N unfit; 1×3×N, 1×5×N published.
* Replacement patch prepared: 50 boxes IMP→UNKNOWN (1×2×N, 1×4×N,
  1×6×N, 1×7×N, 1×8×N, …), 0 conflicts; all other existing N rules kept
  (they are published in qu5-n's Impossible list).

## F — safe promotion status

* Patch document: `docs/frontier/f_piece/f_2xnn_squares_promotion_patch.md`
  (re-validated this session; precedence section strengthened).
* Content: two rules — `a == 2 ∧ b == 2` (unfit: spans {1,3,3} need two
  axes ≥ 3) and `a == 2 ∧ b == c` (published F-square impossibility +
  mechanized layer confinement).
* Verification this session: all 24 orientations checked (axis-explicit);
  2D ingredient confirmed on the live qu5-f page; F squares unsat by exact
  search through 40×40; project solver: F 2×5×5 and F 2×10×10 → 0
  solutions; classify-pipeline precedence checked (impossible_reason is
  consulted first — zero matches against protected classes);
  `validate_catalogue.py F` PASSED; `audit_catalogue.py F`: prime
  mismatches 0, unproven composites 39 (the 2×M×N unknowns — 8 of which
  this patch resolves), published solutions 0.
* Impact: 8 boxes UNKNOWN → published_impossible at dims ≤ 20
  (2×2×{5,10,15,20}; 2×{5,10,15,20}×{5,10,15,20}); 62 of the 70 former
  blanket targets remain honestly UNKNOWN.
* The unsafe blanket patch (`f_2xn_promotion_patch.md`) must **not** be
  applied; recommended to mark it superseded by this document.

## Y — promotion status

* Patch document: `docs/frontier/y_piece/y_thickness1_published_families_patch.md`
  (re-validated).
* Content: `1×5×N` with N ≢ 0 (mod 10), `1×6×N`, `1×8×N` →
  published_impossible, with an explicit `searched_no_solution` guard
  (required because `classify` consults impossible_reason first — an
  unguarded rule would relabel 14 searched boxes).
* Published wordings verified verbatim on live qu5-y: "5xk if k <> 0
  (modulo 10)", "6xk for all k", "8xk for all k" (Impossible list;
  rectangle context confirmed by the page's own 5×N/6×N/8×N strip
  analyses). The thickness-1 reduction is mechanized (all 24 orientations
  flat in 1×M×N; all 8 free-Y orientations realized).
* Sanity (not proof): Y 1×5×10 → 10 solutions (project solver), matching
  the published 5×10 Y-rectangle; 2D SAT corroborates each family
  (5×{12,14,16,18,22,24}, 6×k to 6×30, 8×k to 8×30 all unsat).
* Impact: 6 boxes UNKNOWN → published_impossible at dims ≤ 20
  (1×5×{16,17,18,19}, 1×6×20, 1×8×20); 14 searched boxes keep their
  labels; 0 conflicts; `validate_catalogue.py Y` PASSED;
  `audit_catalogue.py Y`: prime mismatches 0, unproven composites 0.
* Secondary (separate task): 1×5×{20,30,…} are constructive composites of
  the prime 1×5×10 (proposed `ROW_FAMILIES` entry in the patch doc).

## Patch safety audit (all four patches)

| check | F patch | Y patch | W replacement | Z replacement | N replacement |
|---|---|---|---|---|---|
| boxes changed (dims ≤ 20) | 8 | 6 | 70 | 132 | 50 |
| direction | UNKNOWN→IMP | UNKNOWN→IMP | IMP→UNKNOWN | IMP→UNKNOWN | IMP→UNKNOWN |
| RAW_PRIMES touched | 0 | 0 | 0 | 0 | 0 |
| PUBLISHED_SOLUTIONS touched | 0 | 0 | 0 | 0 | 0 |
| SEARCHED_NO_SOLUTION touched | 0 | 0 (guard) | 0 | 0 | 0 |
| contradictory-rule overlap | 0 | 0 | 0 | 0 | 0 |
| validator | PASSED | PASSED | PASSED | PASSED | PASSED |
| auditor prime-mismatches | 0 | 0 | — | 0 | 0 |

(`audit_catalogue.py` was run for F, Y, N and Z; W's auditor was not run
to completion — its validator PASSED and its data is untouched by any
proposed change except the narrowing documented above.)

**No patch has been applied.** `git status` confirms catalogue mtimes are
unchanged from before this task.

## Recommended action order

| Item | Status | Evidence | Catalogue impact | Patch ready? | Action |
| ---- | ------ | -------- | ---------------: | ------------ | ------ |
| F 2×N×N + 2×2×N promotion | proved (published ingredient + mechanized lemma) | live qu5-f "NxN"; 2D unsat ≤ 40×40; solver 0-solutions; 0 conflicts | 8 boxes UNKNOWN→IMP, dims ≤ 20 | **Yes** | Apply after human review; mark blanket F patch superseded |
| Y thickness-1 families promotion | proved (published ingredient + exact reduction) | live qu5-y impossible list; solver 1×5×10 = 10 sols (sanity); 0 conflicts | 6 boxes UNKNOWN→IMP; 14 searched preserved | **Yes** | Apply after human review |
| Q registry correction | diagnosed; corrected coords proposed | disconnected registry shape; live qu5.61 + Shirakawa 5-22; tiling identification (16 vs 0 raw tilings of 2×2×5) | none today (no Q artifacts) | **Yes** (1-line registry fix) | Fix registry, re-run check_piece_registry + validators, then Q solver work with 2×2×5/2×3×5 positive controls |
| W blanket narrowing | TOO STRONG (unproven beyond core) | qu5-w published strip rule; no straight rectangles ≤ 40×40 | 70 boxes IMP→UNKNOWN | **Yes** (in rule-audit doc) | Human decision: apply narrowing, or relabel, or retain with documented caveat |
| N blanket narrowing | TOO STRONG (published core = 3-,5-wide only) | qu5-n "Zx{3,5}"; catalogue TODOs; unsat ≤ 2×200 | 50 boxes IMP→UNKNOWN | **Yes** (in rule-audit doc) | Human decision (as above) |
| Z blanket narrowing | TOO STRONG (no published 2D basis at all) | qu5-z has no 2D data; Z page starts at 3× | 132 boxes IMP→UNKNOWN | **Yes** (in rule-audit doc) | Human decision (as above); largest coverage regression |
| Blanket F 2×M×N | conjecture | no F rectangle ≤ area 900 (2 methods); bent-strip tiling exists; no published source | (70 if ever proved) | No — do not promote | Hold; revisit only with verified Golomb location or DRAT certificates |
| W/Z/N straight-rectangle questions | open | searches exhausted to stated limits only | — | — | Optional: DRAT-certificate SEARCHED entries for wanted boxes (Z 6×6×10 precedent) |
| qu5.61 vs Shirakawa 3×9×15 discrepancy | noted | qu5.61 complete list (5 primes) vs live 5-22 (6 primes) | none (catalogue follows Shirakawa) | — | Optional: ask/source-check; no catalogue change |

## Discipline record

* Published fact → derived theorem → computational evidence → conjecture
  was maintained throughout; every promotion above sits in the first two
  tiers, and everything else was left open or explicitly labelled
  conjecture.
* The three TOO STRONG verdicts follow the project's own policy precedent
  (the F `a == 2` empirical rule removal recorded in `docs/pieces/F.md`).
* Nothing was weakened silently: every narrowing exists only as a
  proposed diff with exact before/after box counts.

---

## ADDENDUM (2026-09-01, later same day)

The three evidence-backed changes recommended above were **applied** exactly
as specified, followed by a full re-audit (see
`docs/frontier/post_promotion_integrity_report.md`):

1. F promotion applied (8 boxes UNKNOWN → published_impossible).
2. Y promotion applied with the SEARCHED guard (6 boxes UNKNOWN →
   published_impossible; 48 searched boxes now carry their label through
   `classify`, moving 39 previously-unlabeled entries out of the search
   database's unproved list: 199 → 160).
3. Q registry corrected to the square+corner shape; project-solver positive
   controls 2×2×5 = 16 raw (2 box-symmetry orbits = published 2) and
   2×3×5 = 64 raw (10 orbits = published 10) — note the live Shirakawa
   page's leading numbers (4, 6) are *piece counts*, and the published
   *solution* counts are 2 and 10; negative controls 3×3×{5,9}, 3×5×{5,7}
   all zero (5×5×5 zero via SAT).

One parsing correction to the body of this report: the earlier reading of
the 5-22 page as "2×2×5: 4 solutions, 2×3×5: 6 solutions" conflated piece
counts with solution counts. The orbit verification above supersedes it.

The W/Z/N blanket rules remain flagged TOO STRONG and were **not** touched.

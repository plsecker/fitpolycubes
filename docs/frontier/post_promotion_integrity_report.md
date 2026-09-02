# Post-Promotion Integrity Report

**Date**: 2026-09-01
**Scope**: application of the three evidence-backed changes (F promotion,
Y promotion, Q geometry correction) and the complete post-change audit.
**Constraints honoured**: W/Z/N blanket rules untouched; the blanket F
2×M×N conjecture not promoted; no new mathematical claims; all
published/primes/searched evidence preserved.

---

## 1. Applied changes (exact diffs)

Three files changed; full diffs are in git (`git diff` isolates each —
all three files were clean before this task).

### 1.1 `catalogues/f_catalogue.py` (+12 lines)

```diff
@@ class FCatalogue: def impossible_reason(self, box):
         # Historical note: An empirical rule for a == 2 ... (unchanged)
 
+        # Theorem (derived): the F pentacube does not fit 2x2xN:
+        # spans {1,3,3} require two box dimensions >= 3.
+        if a == 2 and b == 2:
+            return "published_impossible"
+
+        # Theorem (derived): every F placement in 2xNxN lies flat
+        # (span-1 axis forced onto the thickness), so a tiling would
+        # induce an N x N square tiling by the free F pentomino.
+        # Sillke qu5-f publishes "NxN" as impossible.
+        if a == 2 and b == c:
+            return "published_impossible"
+
         if box in self.searched_no_solution:
             return "searched_no_solution"
```

### 1.2 `catalogues/y_catalogue.py` (+19 lines)

```diff
         if a <= 0:
             return "published_impossible"
 
+        # Preserve explicit SEARCHED_NO_SOLUTION evidence (f_catalogue
+        # pattern): searched boxes keep their label.  Required because
+        # solvers.decomp.classify consults impossible_reason before all
+        # other classification stages.
+        if box in self.searched_no_solution:
+            return "searched_no_solution"
+
         if a == 1 and b <= 4:
             return "published_impossible"
 
+        # Theorem (derived): thickness-1 boxes reduce exactly to
+        # Y-pentomino rectangles (all placements flat, all 8 free
+        # orientations realized).  Sillke qu5-y publishes:
+        #   5xk impossible unless k = 0 (mod 10)
+        #   6xk, 8xk impossible for all k
+        if a == 1 and b == 5 and c % 10 != 0:
+            return "published_impossible"
+        if a == 1 and b == 6:
+            return "published_impossible"
+        if a == 1 and b == 8:
+            return "published_impossible"
```

### 1.3 `common/registry.py` (Q geometry, +7/−1 lines)

```diff
     "Q": PieceInfo(
         letter="Q",
-        coords=np.array([[0,0,0],[1,0,0],[0,1,0],[1,1,0],[2,2,0]]),
+        # Corrected 2026-09-01 (geometry-integrity audit, ...): the
+        # previous coordinates were face-disconnected and could not fit
+        # the catalogue's published 2x2x5 prime.  The corrected shape is
+        # Sillke qu5.61 (Shirakawa 5-22): a 2x2 square with one cube
+        # stacked on a corner, i.e. the 2x2x2 block minus an L-triomino.
+        coords=np.array([[0,0,0],[1,0,0],[0,1,0],[1,1,0],[0,0,1]]),
```

The pre-change registry state is exactly the git `HEAD` version of
`common/registry.py` (the file was clean before the edit); the old
coordinates are additionally preserved verbatim in the in-code comment,
in `docs/frontier/q_piece/q_geometry_integrity_audit.md`, and in
`docs/pieces/Q.md`.

## 2. Classification changes (full-diff verified)

A snapshot of all 14,480 classifications (20 catalogues, canonical boxes
dims ≤ 20, volume ≡ 0 mod 5) was taken before and after the changes and
diffed:

* **Exactly 14 classifications changed; nothing else moved.**
* **F: 8** — 2×2×{5,10,15,20}, 2×5×5, 2×10×10, 2×15×15, 2×20×20, all
  `UNKNOWN → published_impossible`.
* **Y: 6** — 1×5×{16,17,18,19}, 1×6×20, 1×8×20, all
  `UNKNOWN → published_impossible`.
* **Q: 0 classification changes** (expected: its catalogue is published
  data about qu5.61 and was already correct).
* No RAW_PRIMES, PUBLISHED_SOLUTIONS or SEARCHED_NO_SOLUTION member
  changed label in any catalogue; no unrelated impossibility rule fired
  (catalogues other than F/Y are bit-identical in the snapshot).

Y SEARCHED guard behaviour (verified at the classify level):
`impossible_reason` now returns `searched_no_solution` for the searched
boxes (e.g. 1×5×5, 1×6×10, 1×8×15), the prime 1×5×10 is untouched
(rule excluded by the mod-10 condition), and all 48 searched boxes keep
their searched status.

## 3. Q correction — evidence and validation

**Old geometry** `[(0,0,0),(1,0,0),(0,1,0),(1,1,0),(2,2,0)]`:
face-disconnected, spans (3,3,1), cannot fit 2×2×5.
**Corrected geometry** `[(0,0,0),(1,0,0),(0,1,0),(1,1,0),(0,0,1)]`:
Sillke qu5.61 / Shirakawa 5-22 — the 2×2 square with one cube stacked on
a corner. Evidence chain: Sillke's own height-map picture ("1 2 / 1 1");
exhaustive enumeration (48 connected 5-subsets of the 2×2×2 cube →
exactly 2 free pentacubes with spans {2,2,2}); tiling discrimination
(square+corner tiles 2×2×5, the other candidate — registry piece A —
does not, 16 vs 0 raw tilings).

Post-fix geometry checks (all pass): 5 cubes; face-connected; spans
{2,2,2}; 24 distinct orientations (achiral, trivial stabilizer); distinct
from A; all 24 orientation images are connected 5-cell sets; layer
structure 4+1 as expected.

**Positive controls (project solver, post-fix):**

| box | raw solutions | box-symmetry orbits | published |
|---|---:|---:|---:|
| 2×2×5 | **16** | **2** | 2 ✓ |
| 2×3×5 | **64** | **10** | 10 ✓ |

**Count-semantics note (explicit, superseding the earlier misreading):**
on the live Shirakawa 5-22 page the leading numbers ("4", "6") are
**piece counts** (volume/5: 20/5 = 4, 30/5 = 6), and the published
*solution* counts are **2** and **10**. The raw-orientation counts of the
project solver (16, 64) differ from the published counts by the box
symmetry quotient (groups of order 16 and 8; Burnside orbit counts
computed directly = 2 and 10, matching exactly). Raw and canonical counts
were not silently equated.

**Negative controls (project solver; 5×5×5 via CaDiCaL SAT):**

| box | published basis | result |
|---|---|---|
| 3×3×5 | qu5.61 rule (A) family | 0 ✓ |
| 3×3×9 | rule (A) proof core | 0 ✓ |
| 3×5×5 (u odd) | rule (B) | 0 ✓ |
| 3×5×7 (u odd) | rule (B) | 0 ✓ |
| 5×5×5 | rule (C) | 0 ✓ (SAT) |

(5×5×7 / 3×7×15 rule-C corroborations were still running in the
background at report time; they are published results and are not
load-bearing here.)

## 4. Q blast-radius audit

* `data/`: the only Q files are the six created by **this session's**
  post-fix controls (`solutions_fast_q_*.dat`, timestamps 11:11–11:13).
  **Zero pre-existing Q solver artifacts** — independently reconfirmed.
* Hard-coded old-Q coordinates: none (the single grep hit,
  `tools/frontier/test_v_macro.py`, is a commented "W shape" 2D test with
  different cells).
* Registry consumers: `catalogues/registry.py` (module wiring,
  geometry-independent) and `tools/verify_sicherman_odd_boxes.py` (uses
  Q's published 5×5×9 odd-box fact — geometry-independent). No
  orientation caches, solver tests, documented placements, or published
  solution records depend on the old geometry.
* `shirakawa/G.md` carries a historical audit note that it once contained
  a mislabeled copy of the 5-22 (Q) transcription; the note records that
  the 5-22 data "lives under Q" — consistent with today's fix, no action.
* Conclusion: **nothing existing became invalid**; the correction removes
  a forward-looking hazard only.

## 5. Regression results (before → after)

| check | before | after | verdict |
|---|---|---|---|
| classification snapshot (14,480 boxes, 20 catalogues) | baseline | exactly 14 intended changes | ✓ |
| `validate_catalogue.py` — all 20 pieces | (F/Y/W/Z/N PASS spot-checked) | **20/20 PASSED** | ✓ |
| `audit_catalogue.py F` | A0 B39 C157 D0 | A0 **B33** C157 D0 | ✓ (B: −6 = the six ≤15 boxes promoted) |
| `audit_catalogue.py Y` | A0 B0 C238 D0 | A0 B0 C238 D0 | ✓ |
| `audit_catalogue.py Q` | n/a (geometry broken) | A0 B42 C257 D0; NOTABLE 5×5×9 minimal-odd ✓ | ✓ |
| `check_repo.py` | all ✓, status OK, 199 unproved | all ✓, status OK, **160 unproved** | ✓ (Δ39 = Y searched entries now labeled by the guard — intended) |
| `check_piece_registry.py` | passed (4 known module warnings: I, X, B, G) | passed (same warnings) | ✓ |
| solver smoke F 2×5×5 | 0 | 0 | ✓ |
| solver smoke L 1×2×5 | 2 | 2 | ✓ |
| solver smoke Y 1×5×10 | 10 | 10 | ✓ |
| solver smoke T 2×5×5 | 0 | 0 | ✓ |
| Q positive 2×2×5 / 2×3×5 | (impossible with old geometry) | 16 / 64 raw (2 / 10 orbits = published) | ✓ |
| Q negative 3×3×5, 3×3×9, 3×5×5, 3×5×7, 5×5×5 | — | all 0 | ✓ |

The only unexpected-looking movement — the search database's unproved
count 199 → 160 — was investigated and is exactly the Y
`searched_no_solution` guard labelling all 48 Y searched boxes through
`classify` (39 of them were previously unlabeled). This is the guard's
intended provenance improvement, not a regression.

## 6. Per-piece change table

| Piece | Change | Before | After | Unexpected effects |
| ----- | ------------------- | -----: | ----: | ------------------ |
| F | theorem promotion (2×2×N unfit + 2×N×N squares) | 39 unproved composites ≤15; 8 UNKNOWN 2×-boxes ≤20 | 33 unproved composites ≤15; 0 UNKNOWN among the 8 | none |
| Y | theorem promotion (1×5×N mod-10, 1×6×N, 1×8×N) | 0 unproved composites; 6 UNKNOWN thickness-1 boxes ≤20 | 0 unproved composites; 0 UNKNOWN among the 6; 48 searched boxes labeled through classify | search-db unproved 199→160 (intended guard effect) |
| Q | geometry correction | disconnected pseudo-piece, spans (3,3,1), 2×2×5 unreachable | connected qu5.61 shape, spans (2,2,2), 2×2×5 = 2 orbits (published), all published rules reproduced | none (no pre-existing Q artifacts) |

## 7. Provenance updates made

* `docs/pieces/F.md` — audit-history entry: applied promotion is a
  **derived theorem** using the **published** F-square impossibility
  (qu5-f "NxN"); blanket 2×M×N recorded as unapplied conjecture.
* `docs/pieces/Y.md` — audit-history entry: applied families carry
  published provenance (Golomb 1966; Bouwkamp–Klarner 1970; qu5-y); guard
  side-effect documented.
* `docs/pieces/Q.md` — audit-history entry: registry correction is the
  resolution of the geometry-integrity issue, with the evidence chain.
* `docs/frontier/f_piece/f_2xn_promotion_patch.md` — **STATUS banner
  added** (superseded/conjecture, not applied); historical text preserved
  unmodified.
* `docs/frontier/f_piece/f_2xnn_squares_promotion_patch.md` and
  `docs/frontier/y_piece/y_thickness1_published_families_patch.md` —
  status updated to APPLIED (pointer to this report).
* `docs/frontier/pre_promotion_integrity_report.md` — addendum recording
  the application and the piece-count/solution-count parsing correction.
* `docs/frontier/q_piece/q_geometry_integrity_audit.md` — addendum: fix
  applied, with the validation summary.
* The W/Z/N rule audit (`docs/frontier/rule_audit/w_z_n_blanket_rules_audit.md`)
  stands unchanged: the three blanket rules remain flagged **TOO STRONG**
  and were not modified.

## 8. Remaining concerns

1. **W blanket `a == 2` / `b == 2`** — TOO STRONG (provable core: both
   other dims ≢ 0 mod 5; squares published-impossible; straight 5k-wide
   strips open). Unmodified per task constraints.
2. **Z blanket `a <= 2`** — TOO STRONG (no published 2D basis at all;
   provable core = unfit sub-cases 1×1×N, 1×2×N, 2×2×N). Unmodified.
3. **N blanket `a <= 1`** — TOO STRONG (published core = 1×3×N, 1×5×N;
   quadrant/bent-strip results are not finite rectangles). Unmodified.
4. **Blanket F 2×M×N** — conjecture; its patch document now carries a
   SUPERSEDED banner; 62 boxes ≤ 20 dims remain honestly UNKNOWN.
5. **Y `a == 1 and b <= 4`** — correct for b ∈ {3,4} (published), but the
   b = 2 sub-case (1×2×N) has no published impossibility basis (qu5-y
   says width-2 *bent* strips exist; finite 2×N unsat ≤ 2×200
   computationally). Flagged in the rule audit; untouched here.
6. **qu5.61 vs Shirakawa 5-22 prime-list discrepancy** — qu5.61's
   "complete" list has five primes; the live 5-22 page adds 3×9×15
   (credited Sillke 1993). Likely page staleness; flagged, no change.
7. **Registry field naming** — `kurnell=61` stores Sillke's qu5 (LEX)
   numbering, not Kürnell's book numbering. Cosmetic.
8. **Working tree hygiene** — the repository carries pre-existing
   uncommitted modifications from earlier sessions (`catalogues/w_catalogue.py`,
   `catalogues/z_catalogue.py`, `common/polycube_utils.py`,
   `solvers/solver.cpp`, docs). They predate this task and were not
   touched; committing them (separating this task's three changes) would
   improve auditability.

## 9. Recommended next action

With the repository clean and all three changes verified, the single most
valuable next investigation is:

**Determine whether the W pentomino tiles any straight 5×N strip.**

Rationale: (i) the W catalogue's retained blanket `a == 2` rule asserts
*every* 2×M×N box impossible, and by the mechanized layer reduction this
is equivalent to "the W pentomino tiles no rectangle at all" — yet
Sillke's W page hints that width-5 strips are the one open class ("Z:
5p, ... only 5n"); (ii) a single W 5×N hit would **falsify** a currently
retained `published_impossible` family — a correctness issue, not merely
hygiene — and immediately yield new tileable 2×5×N boxes; (iii) strips
are the most tractable infinite family and the repository already has
frontier/transfer-matrix machinery suited to them; (iv) the same study
would settle the analogous open classes for F/V/Z (also {1,3,3} pieces
whose 2-thick fate reduces to the same 2D question). The Z-pentomino 2D
status (no published data at all) is the natural follow-up.
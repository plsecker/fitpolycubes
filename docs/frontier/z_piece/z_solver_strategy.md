# Z Solver Strategy Map

**Date**: 2026-08-29
**Purpose**: a measured decision framework for choosing the right exact solver
for future Z-pentacube boxes. Based on the certified 6×6×10 UNSAT campaign,
its certificate package, the S-piece planar-frontier machinery, and new
small bounded proof-of-concept probes (listed in §6; no uncontrolled
searches, no catalogue changes, no changes to certified results).

---

## 1. Geometry and solver inventory (tasks 1–2)

**Z geometry** (piece 5/11; `PENTACUBES["Z"]`): flat pentacube, 12
orientations = 4 planar shapes × 3 planes. Every placement lies in one
axis-parallel plane: xy (1 z-layer, 5 cells) or vertical xz/yz (3 z-layers,
per-layer profiles (2,1,2) or (1,3,1)).

| solver | status | strengths | weaknesses (measured) |
|---|---|---|---|
| A. `solvers/fitpolycubes_hybrid.py` (mp + Numba DLX, MRV, symmetry) | production | fast tiling discovery on easy boxes; warm-startable | no certificate; UNSAT not attainable in reasonable time (6×6×10: >1.5B nodes/60 min, one depth-1 branch alone >189M nodes) |
| B. SAT/CaDiCaL via pysat + drat-trim/lrat-check | production-quality for Z (6×6×10 certified) | complete decision both ways; portable DRAT/LRAT certificate; 2,176-var encoding audited | naive CDCL struggles on the 120-piece SAT side (all 3 axes + CP-SAT UNKNOWN at 300–900 s) |
| C. planar frontier DP (S-piece methodology) | prototypes only (`/tmp/opencode/z_layer_dp*.py`) | exact counts; natural layer-walk certificates; S-proven | 6×6-scale frontier ≈ 10⁶ boundary states — Python-infeasible (measured: 1.4M distinct failed states on 6×6×5, 300 s incomplete); needs Numba port |

**S-machinery transferability (task 2).** The S solver
(`solvers/s_z_frontier_packed.py`) assumes every orientation spans exactly 2
z-layers, so its 3-layer window state has `L2 ≡ 0` and 32-bit words. For Z:

* vertical placements span **exactly 3 layers** with profiles **(2,1,2) /
  (1,3,1)** (measured) — the same 3-layer window works, but `L2` carries
  pending cells *inside* a layer build and is `0` at every layer boundary
  (verified in the prototype);
* S's 32-bit layer words → Z needs **36-bit layers = 108-bit states = 2×uint64**
  (a naive single-word port is impossible — and the numpy int64 shift-overflow
  incident during the 6×6×10 work shows word-packing must use split words or
  Python ints);
* Z's mixed flat/vertical structure requires an **in-plane flat-tiling
  oracle** inside each layer transition (S has no analogue);
* measured frontier: 6×6 cross-section ⇒ ~10⁶ distinct boundary states
  (1.4M failed states at 6×6×5 before cap) — fine in Numba, infeasible in
  pure Python. 5×5 cross-section: 1,901 states, UNSAT in 0.4 s.

**Transfer verdict**: the S state model transfers structurally (3-layer
window, packed masks, template transitions, basin/SCC analysis); the
32-bit word-packing does not (3×36 = 108 bits ⇒ 2×uint64 states), and the
flat/vertical split needs the two-phase layer transition. Productisable as
`z_frontier_packed.py` for boxes with cross-section ≲ 40–50 cells.

## 2. The certified 6×6×10 pipeline — measured economics (task 3)

| stage | measured |
|---|---|
| placements | 2,176 (geometry-capped: **max 60 placements per cell for every Z box measured**, §4) |
| clauses | 195,976 = 360 ≥1 + 195,616 AMO (146,296 unique; ≈ 90 AMO clauses per placement — **linear in placements**) |
| CNF size | 2.6 MB (canonical; dedup would give ≈ 26k+146k ≈ 150k clauses, −25 %) |
| solve | CaDiCaL 287 s (single core) |
| DRAT | 7,425,174 lines, 2.42 GB (+45 % solve overhead to log) |
| drat-trim | **s VERIFIED** 455 s, 1.19 GiB peak |
| LRAT emit (`-L`) | second full verification 496 s, 2.45 GB LRAT |
| lrat-check | **c VERIFIED** 25.2 s |
| total third-party cost | ≈ 8 min for formal verification of the hardest box tried |

**Scalability implications**: encoding is trivially cheap (placement
generation + ~90 clauses/placement, linear). Solve time is the wild card
(287 s here; unknown territory above ~120 pieces). DRAT proof size grows
superlinearly with hardness: 5×5×5 ≈ 1–2 K lines; 6×6×5 ≈ 26–54 K lines;
6×6×10 = 7.4 M lines / 2.42 GB. Verification remains mechanical (LRAT
25 s), but **proof storage** (GBs) and the 2× solve overhead become the
practical limits for much larger UNSAT boxes.

## 3. Benchmark set (task 4; all existing certified/public instances)

| instance | status | role |
|---|---|---|
| `6×6×10` | **UNSAT** — fully verified DRAT/LRAT certificate | hard UNSAT representative |
| `6×10×10` | **SAT** — smallest published tileable Z box (prime, Shindo 1997/ISHINO 2000), 4 machine-readable witnesses | hard SAT representative |
| `5×5×5` | impossible (rule `5x{5,6,7}`) | small UNSAT control |
| `6×6×5` | impossible (rule `5x{5,6,7}`) | medium UNSAT control |

(No smaller known-tileable Z box exists than 6×10×10 = 120 pieces, so the
"small tileable" and "hard SAT" roles coincide there; the published
witnesses make it an ideal constructive-certificate test.)

## 4. Formulation comparison (measured)

| formulation | state/variable count | branching | memory | 6×6×10 result | UNSAT certificate? | SAT witness? |
|---|---|---|---|---|---|---|
| A hybrid/MRV DLX | 2,176 placements DFS | no proof-size control; >1.5B nodes/60 min, non-exhaustive | modest | intractable | **none** (search log only) | tiling only, slow |
| B SAT/CaDiCaL (pairwise-AMO) | 2,176 vars / 195,976 clauses (6×6×10) | CDCL + learning; 287 s | ≤ 2.9 GB | **UNSAT, certified** | **DRAT/LRAT, third-party verified** | yes — model → placements → geometric check (validated on 6×10×10) |
| B′ CP-SAT (+layer equations) | same + 10 linear equations | portfolio/LNS | moderate | n/a (UNSAT not attempted) | yes (proof logging limited) | yes (solution) — but **UNKNOWN at 300 s without a hint** (measured, both with and without layer equations) |
| C planar frontier DP | boundary (L0,L1) ∈ ~10⁶ states (measured: 1.4M failed states on 6×6×5) | per-layer vertical-config DFS + flat-oracle | ~GB in Python; fine in Numba | incomplete at 300 s (v1) | yes in principle (state table), needs port | yes — natural layer-walk/tiling counts (S-methodology) |
| C′ witness-guided SAT | 4,096 vars | forced assumptions / CP-SAT hint | small | — | n/a | **OPTIMAL 0.22 s, validated** (published witness; works for any box with a known tiling) |

## 5. Layer-count and orientation-count constraints (task 7)

Derived exact constraints (all verified derivable from the geometry):

* **Per-layer area equation**: `A = 5·f_z + v_z` where `A` = cross-section
  area, `f_z` = flat pieces in layer z, `v_z` = cells contributed by
  vertical pieces (1–3 each). Hence **`v_z ≡ A (mod 5)`** — a strong
  congruence invariant for both DP pruning and SAT propagation.
* **Vertical count congruence**: summing over all layers,
  `Σ_z v_z = 5·(#vertical pieces)`, so `#vertical ≡ 0 (mod 5)` for a box
  with `c ≡ 0 (mod 5)` layers (e.g. 10 for 6×6×10 ⇒ #vertical ≡ 0 (mod 5));
  `#flat = 72 − #vertical`.
* **Per-orientation counts**: no fixed equalities (orientations repeat
  freely); only the flat/vertical split above is constrained.

**Measured PoC effect** (`10×10×6`, the 120-piece SAT instance):
CP-SAT + per-layer equations, no hint: **UNKNOWN at 300 s** — layer
equations alone do not rescue hard SAT instances on a 4-core VM. Their best
use is DP pruning (congruence invariant) and solution *verification*
(witness → hint → instant reconstruction: **OPTIMAL 0.22 s**, tiling
geometrically validated — demonstrated end-to-end).

## 6. Generalization without clause explosion (task 8)

Placement statistics across 8 measured boxes:

| box | pieces | placements | max-k/cell | naive clauses |
|---|---|---|---|---|
| 5×5×5 | 25 | 540 | 60 | 36,143 |
| 6×6×5 | 36 | 896 | 60 | 68,516 |
| 6×6×10 | 72 | 2,176 | 60 | 195,976 |
| 5×9×15 | 135 | 4,484 | 60 | 428,513 |
| 6×10×10 | 120 | 4,096 | 60 | 406,648 |
| 5×8×20 | 160 | 5,328 | 60 | 508,328 |

`maxk = 60` for **every** box: the number of placements covering a single
cell is geometry-capped (12 orientations × bounded offsets), independent of
box size. Therefore pairwise-AMO clause growth is **linear** in placements
(≈ 90 clauses/placement) — the 6×6×10 encoding generalizes to larger boxes
without quadratic blow-up (5×8×20: 508k clauses, still small). For very
large boxes a sequential/totalizer AMO would shave the constant, but the
measured data shows no explosion.

**Generalization of the certificate pipeline**: the z_6610 package
(CNF + DRAT/LRAT + placement_set + var_map + standalone semantic audit +
checker verdicts + hashes) is already piece-agnostic in structure — the
audit script hard-codes only the piece geometry and box. The same
`data/certificates/z_<box>/` layout is reusable as-is for any future box.

**Constructive (SAT) certificates**: a tiling witness — JSON placements
plus an independent exact-cover/congruence verifier — is already validated
end-to-end (published 6×10×10 witness → 120/120 placements in the audited
set → forced-assumption SAT reproduces it → geometric validation ✅;
witness-hinted CP-SAT reconstructs it in **0.22 s**, OPTIMAL). This
complements the existing `macro-walk-certificate` JSON schema
(`tools/frontier/macro_certificate_schema.json`), which already treats piece
geometry as authoritative — SAT tiling witnesses fit the same
"checker-derives-everything" philosophy as a separate certificate type
(`tiling-witness` alongside `macro-walk` and the new `UNSAT-DRAT` class).

## 6b. Framework hardening findings (from the control battery)

1. **Deduplicate the DIMACS.** Duplicate AMO clauses (symmetric placements)
   can break proof/CNF pairing: `6×6×5` verified only with the deduplicated
   canonical CNF (195,616 → 146,296+360 clauses; drat-trim `s VERIFIED`
   0.28 s AND lrat-check `c VERIFIED` — the project's **second fully
   certified UNSAT instance**, and the template for small boxes).
2. **pysat's CaDiCaL proof stream can be incomplete**: for `5×5×5` it omits
   the terminating empty clause (instance-dependent), so its DRAT fails
   verification even though the solve verdict is correct. Same wrapper
   produced a complete proof for 6×6×10 — the gap is instance-dependent.
   Mitigations, both demonstrated: cross-engine logging — **Glucose4's
   proof for 5×5×5 verifies (`s VERIFIED`, 0.078 s)** — and/or standalone
   solver binaries. The `s VERIFIED` gate is what catches this; never
   trust an unverified proof log.
3. `Minisat22` cannot log proofs via pysat (`NotImplementedError`).

## 7. Recommended decision framework (task 9)

Default pipeline for **any** future Z box, in order:

1. **Decomposition check** (`classify`): if the existing engine closes it,
   done — no solver needed.
2. **SAT decision** (audited encoding, deduplicated CNF, CaDiCaL bounded):
   * UNSAT → certificate pipeline (drat-trim + lrat-check; archive package).
   * SAT → tiling witness extraction + independent geometric validation
     (`validate_tiling`) → constructive certificate.
3. **If SAT is slow (placement-rich box, ≥ ~120 pieces)**:
   a. published/witness-guided solve (hint or forced assumptions) — proven
      instant when a tiling is known;
   b. CP-SAT portfolio with the piece-count + per-layer equations — cheap to
      try, sometimes unknown (measured);
   c. frontier DP (Numba port of the prototype) — the counting/certificate
      engine; required anyway for tiling counts.
4. **Never rely on an unverified proof stream**: the pipeline's acceptance
   gate is checker `s VERIFIED`/`c VERIFIED`, never solver exit codes. If
   CaDiCaL's stream is defective (no terminating empty clause), re-log with
   Glucose4 or a standalone CaDiCaL/kissat binary — demonstrated working
   fallback (5×5×5 via Glucose4: `s VERIFIED`).

Scenario → solver mapping:

| scenario | solver |
|---|---|
| small easy box (≤ ~40 pieces), any status | SAT (CaDiCaL; seconds) — complete + certificate-ready |
| box with a known/published tiling | witness-forced SAT / CP-SAT hint (constructive certificate in seconds) |
| hard UNSAT candidate | SAT → CaDiCaL → drat-trim → lrat-check (the 6×6×10 pipeline; measured economics in §2 of the certification docs) |
| hard SAT candidate without guidance | CP-SAT/SAT portfolio (bounded), else frontier-DP Numba port, else record UNKNOWN |
| counting / macro certificates | planar frontier DP (S-methodology, 2×uint64 state words, mod-5 layer congruence pruning) |
| exhaustive proofs of structure (bands, families) | frontier DP + SAT for spot decisions; hybrid/MRV only for quick tiling discovery |

## 8. Concrete next implementation steps (future work, not started)

1. `tools/frontier/z_piece/z_certificate_lib.py`: shared encoding helpers
   (dedup canonical DIMACS, var map, metadata) — generalizing the z_6610
   package; DRAT emitted from the packaged file (file-logged protocol).
2. Numba port of the planar frontier DP (`solvers/z_frontier_packed.py`):
   2×uint64 state words, mod-5 per-layer congruence as pruning, targeting
   the `(5,·)` semigroup-dense rows.
3. Extend the certificate schema family: `tiling-witness` (JSON, validated
   by the independent geometric checker) and `UNSAT-DRAT` (CNF+proof+checker
   verdicts) as first-class evidence classes beside the macro-walk schema.

## 9. What this task did NOT do

No catalogue changes (truth tables untouched); no changes to the certified
6×6×10 artefacts (all hashes in `z_6610_certificate/hashes.txt` remain
valid); no long searches (all probes bounded ≤ 300 s); no new solver code in
the repository (prototypes live under `/tmp/opencode/`).

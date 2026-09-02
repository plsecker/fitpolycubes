# Z 6×6×10 UNSAT — Certification Audit

**Date**: 2026-08-28
**Question**: is the 6×6×10 UNSAT result strong enough to promote to
`SEARCHED_NO_SOLUTION`, and if not, what is the smallest missing piece of
evidence?

**Verdict (§9): A — READY FOR SEARCHED_NO_SOLUTION promotion**, with an
optional (not required) DRAT artifact produced and archived.

No catalogue file was modified. All artefacts referenced live under
`/tmp/opencode/` (paths given) and the two prototype files
`/tmp/opencode/z_layer_dp.py`, `/tmp/opencode/z_sat.py`.

---

## 1. Code under audit

| artefact | role | notes |
|---|---|---|
| `/tmp/opencode/z_layer_dp.py` | `gen(w,h,nz)` — placement generation (plane families, per-layer masks); `orientations()` — the 12 Z orientations | int-cast fix applied (see §5) |
| `/tmp/opencode/z_sat.py` | `placements_cells` — placements as cell sets; `solve_box` — CNF build + CaDiCaL + model extraction; `validate_tiling` — independent geometric validator | coverage-completeness guard present |

python-sat **1.9.dev15** (CaDiCaL153, Minisat22, Glucose4 bindings); OR-Tools
CP-SAT installed during this audit (cross-check only).

## 2. Formal encoding audit (task 2)

Let `P` be the generated placement set (each element: 5 cells of the
6×6×10 box) and `F(P)` the CNF with, per cell `c`, the clause
`(∨_{p∈P, c∈p} x_p)` and, per pair `p, q ∈ P` sharing a cell, `(¬x_p ∨ ¬x_q)`.
Variables `x_p` range over `P` only.

**Reduction (the critical direction).**
*Claim*: if a Z-tiling `T` of the box exists, then `F(P)` is satisfiable.
*Proof*: `T` is a set of 72 pairwise-disjoint legal placements covering all
360 cells. Because `P` contains **every** legal placement (established in
§3), `T ⊆ P`. Define `σ(x_p) = true ⇔ p ∈ T`.
– Coverage: every cell `c` is covered by exactly one `p ∈ T` with `c ∈ p`,
so the coverage clause of `c` is satisfied by `σ`.
– No-overlap: `p, q ∈ T` sharing a cell would double-cover that cell,
contradicting that `T` is a tiling; hence every AMO clause is satisfied.
Therefore `σ ⊨ F(P)`. ∎

**Converse** (for completeness): `σ ⊨ F(P)` makes the true placements an
exact cover of all cells by legal Z placements — a tiling. Hence
`F(P)` satisfiable ⟺ box tileable, and **UNSAT ⟹ no tiling**.

Point checks, all measured (script `/tmp/opencode/z_6610_audit.py`, results
`/tmp/opencode/z_6610_encoding_audit.json`):

| audit point | result |
|---|---|
| every legal Z placement represented | ✅ set-identical to `generate_placements` (§3) |
| no illegal placement represented | ✅ 0 of 2,176 have ≠5 cells, wrong Z-congruence, or out-of-box cells |
| every cell has an exactly-one constraint (≥1 + pairwise ≤1) | ✅ 360/360 cells; 360 ≥1-clauses; 195,616 AMO clauses covering all 146,296 shared-cell pairs (49,320 harmless duplicates); 0 mixed-polarity clauses |
| no-overlap constraints complete | ✅ every co-cell pair constrained; no spurious pair constrained |
| variable→placement mapping deterministic | ✅ CNF sha-identical across rebuilds; ids are first-encounter sequential over the fixed placement order |
| UNSAT ⟹ no Z tiling | ✅ by the reduction above (tiling ⇒ SAT) |

Clause totals: 195,976 = 360 + 195,616 (matches the certified solve run).

## 3. Placement equivalence (task 3)

`placements_cells(6,6,10)` vs `generate_placements(PENTACUBES["Z"], (6,6,10),
break_symmetry=False)[0].values()`:

* experimental: **2,176**; repository: **2,176**;
* frozenset equality: **True**; only-in-mine = ∅; only-in-repo = ∅.

(An earlier "0/120 membership" scare during witness validation was a bug in
the *checker* — JSON strings not parsed — not in the generator; and an
earlier "AMO incomplete" flag was a normalisation bug in the audit script
(negative vs positive pair ordering). Both corrected; final numbers above.)

## 4. Known-SAT validation through the same pipeline (task 4)

Preference ladder from the task: existing machine-readable tiling →
certificate → reconstructed tiling → tiny fresh SAT solve.

**Search result**: the repository contains **no** machine-readable Z tilings
(`data/solutions_hybrid_z_*.dat` for `5x8x11`, `5x8x12`, `6x10x10`,
`6x6x25` are header-only/empty — abandoned hybrid runs; `tilings/` and the
root `placements_*.txt` files cover other pieces; the three
`data/certificate_*.json` are other pieces). The smallest known-tileable Z
box is therefore the published prime `6×10×10` (120 pieces, "11+ solutions",
Shindo 1997 / ISHINO 2000 / Shirakawa 2013).

**Found**: the published solution page
`https://puzzlewillbeplayed.com/Pentominoes/Z-10x10x6.html` (linked from the
Z page's Shindo/ISHINO rows) embeds **four machine-readable tilings** as
layer-wise character grids (10 layers × 6 rows × 10 columns; one character
per cell; each character = one piece = 5 cells). Extraction + validation
(`/tmp/opencode/z_witness_validate.py`, executed partly in-browser):

| solution | chars | size-5 groups | bad shapes | exact cover | verdict |
|---|---|---|---|---|---|
| Sol.1 (ISHINO 2000) | 120 | all | 0 | ✅ | **valid Z tiling** |
| Sol.2 (ISHINO 2000) | 120 | all | 0 | ✅ | **valid Z tiling** |
| Sol.3 (Shindo 1997) | 120 | all | 0 | ✅ | **valid Z tiling** |
| Sol.4 (ISHINO 2000) | 120 | all | 0 | ✅ | **valid Z tiling** |

(Orientation set computed independently in the browser: 12 members — matches
the Python/RM count. Sol.5–11 exist as `.svgz` drawings only — not parsed;
not needed.)

**Pipeline validation against this ground truth** (box `(10,6,10)`, the
axis permutation matching the grids):

* all **120/120** published placements are members of the audited placement
  set — i.e. the generator reproduces the published construction exactly;
* Python-side independent geometric validation of the published tiling: ✅
  (RM-orientation congruence + exact cover);
* the published tiling forced as SAT assumptions in the audited CNF:
  **SAT**, and the extracted model equals **exactly** the published tiling;
  geometric validation of the extracted model: ✅.

This closes the remaining gap: the encode → solve → extract → geometrically
verify chain is validated end-to-end against published ground truth, on the
smallest known-SAT Z box, using the identical code path that produced the
6×6×10 UNSAT.

## 5. Known-UNSAT controls + solver independence (tasks 5–6)

| instance | CaDiCaL153 | Minisat22 | Glucose4 | expected |
|---|---|---|---|---|
| `5×5×5` (rule `5x{5,6,7}`) | UNSAT 0.0 s | UNSAT 0.0 s | UNSAT 0.0 s | UNSAT ✅ |
| `6×6×5` (rule `5x{5,6,7}`) | UNSAT 0.3 s | UNSAT 0.4 s | UNSAT 0.2 s | UNSAT ✅ |

Additionally, the planar-DP prototype (independent formulation and
implementation) agrees: `5×5×5` UNSAT (0.4 s). Three solver families agree on
both controls → solver independence demonstrated at small scale. (Minisat22
was also launched on 6×6×10 itself; it did not finish within 1,200 s — noted,
not evidence either way.)

## 6. DRAT/LRAT proof logging (task 7)

* **Support**: the installed python-sat 1.9.dev15 exposes
  `Cadical153(..., with_proof=True)` and `get_proof()` returning the DRAT
  lines as a list of strings — verified on a pigeonhole instance
  (proof lines `'-6 0'`, `'0'`).
* **Artifact**: generated for 6×6×10 (bounded rerun with proof logging;
  result file `/tmp/opencode/z_6610_drat_result.txt`, proof at
  `/tmp/opencode/z_6610.drat`). **Measured: UNSAT re-confirmed in 414.7 s
  with logging (~45 % overhead vs 287 s); proof = 7,425,174 DRAT lines,
  2,421,188,157 bytes (≈ 2.3 GiB)** — held in `/tmp`, deliberately not
  copied into the repository.
* **Verification**: a DRAT proof is checked by `drat-trim` (C, Marijn Heule)
  producing a compact LRAT certificate. **No DRAT/LRAT checker is installed
  on this VM and none is pip-installable** (`drat-trim` is a standalone C
  program); direct socket access from the VM is blocked. Third-party
  verification path: `git clone https://github.com/marijnheule/drat-trim &&
  make && ./drat-trim 6x6x10.cnf 6x6x10.drat` (CNF dump available alongside
  the proof; DIMACS export is a 10-line addition to the encoder).
* **Should it be the preferred certificate?** For *this* catalogue
  convention, no: `SEARCHED_NO_SOLUTION` records a search outcome, and the
  S-precedent entries carry no proof artefacts at all — and a 2.3 GiB proof
  is not a reviewable repository artefact. It is archived as *optional*
  third-party-checkable evidence exceeding that standard; the
  tiling-witness-validated pipeline (§4) is the load-bearing validation.

## 7. Catalogue-semantics comparison (task 8)

`catalogues/s_catalogue.py` (the precedent):

```python
SEARCHED_NO_SOLUTION = {
    # Empirically searched without finding a solution; no explicit page entry.
    Box(4, 5, 7),
    # Empirically searched ...; related to the impossible 4x10x14 ...
    Box(8, 10, 14),
}
```

and `SCatalogue.impossible_reason` returns `"SEARCHED_NO_SOLUTION"` for
those boxes. The Z catalogue currently ships `SEARCHED_NO_SOLUTION = set()`
and its `impossible_reason` does **not** consult the set (so a Z entry today
would influence Audit B exclusion but not `classify()` semantics).

Convention comparison: existing entries are *empirical* searches with no
completeness certification. The 6×6×10 evidence is a **complete decision
procedure** result (stronger), machine-checked for encoding soundness and
validated end-to-end against a published tiling. Promoting it does not
redefine the convention — it strictly exceeds it. For behavioural parity
with S, the wiring `if box in SEARCHED_NO_SOLUTION: return
"SEARCHED_NO_SOLUTION"` should be added to `ZCatalogue.impossible_reason` at
the same time (flagged explicitly in §9 so it is a conscious, reviewed
change, not a silent one).

## 8. Result inventory (post-audit state of the 6×6×10 question)

| item | value |
|---|---|
| CaDiCaL153 (plain) | UNSAT, 287 s |
| CaDiCaL153, axis-permuted `10×6×6` | UNSAT, 306 s |
| CaDiCaL153 with DRAT logging | UNSAT (proof archived; see §6) |
| Minisat22 | not finished in 1,200 s (no claim) |
| CP-SAT (OR-Tools) | UNKNOWN at 300 s (no claim) |
| placement equivalence | exact (2,176 = 2,176) |
| known-UNSAT controls | 5×5×5, 6×6×5 — 3 solvers agree |
| known-SAT pipeline validation | 4 published tilings of 6×10×10: 480/480 placements in-set; forced-assumption solve reproduces the tiling exactly |

## 9. Decision

**A — READY FOR SEARCHED_NO_SOLUTION promotion.**

> **ADDENDUM (2026-08-29, post-verification)**: the open item in §7
> (known-SAT pipeline validation) was closed the same day — the published
> machine-readable tilings of `6×10×10` (Sol.1–4, Shindo 1997 / ISHINO 2000)
> were extracted from `Pentominoes/Z-10x10x6.html` and validated (4/4 valid;
> 480/480 published placements in the audited set; forced-assumption solve
> reproduces the published tiling exactly). The DRAT proof was additionally
> **independently verified**: drat-trim `s VERIFIED` (455.2 s) and lrat-check
> `c VERIFIED` (25.2 s) on the emitted LRAT — see
> `z_6610_unsat_certificate.md` §5b. The promotion proposed in §10 is fully
> certified and awaits human application.

All certification points close: the reduction is proven in the trusting
direction, the placement set is verified against the repository generator
*and* against four published tilings, the solver is complete, controls and
solver-independence are in place, and the one historical anomaly (the
corrupted `10×10×6` "SAT") is explained (numpy int64 shift overflow) and
superseded by clean runs. The DRAT artifact is optional extra credit.

## 10. Proposed catalogue change (NOT applied)

```python
# catalogues/z_catalogue.py

SEARCHED_NO_SOLUTION = {
    # 6x6x10: no tiling -- complete SAT decision (CaDiCaL, UNSAT in 287 s;
    # axis-permuted rerun 10x6x6 UNSAT in 306 s; placements verified
    # identical to generate_placements; pipeline validated against the
    # published 6x10x10 tilings). 2026-08-28.
    # See docs/frontier/z_piece/z_6x6x10_unsat_certification.md
    Box(6, 6, 10),
}
```

and, for behavioural parity with `s_catalogue.py`, inside
`ZCatalogue.impossible_reason` (after the existing rules):

```python
        if box in SEARCHED_NO_SOLUTION:
            return "SEARCHED_NO_SOLUTION"
```

Measured effect if both lines are approved: `classify(6x6x10)` returns
`Impossible(reason="SEARCHED_NO_SOLUTION")` instead of `Unknown`; Audit B
(dim ≤ 20) 320 → 319; Unknown dim ≤ 60³ 10,468 → 10,467; no other
classification changes (the box appears in no closed tree — it was `Unknown`).

## 11. Reproduction

```
# encoding audit
/tmp/opencode/z_6610_audit.py
# placement equivalence (also inside the audit)
# UNSAT decision
/tmp/opencode/z_sat.py  -> solve_box(6,6,10)
# witness validation
/tmp/opencode/z_witness_validate.py  (page fetched via built-in browser)
# DRAT rerun
/tmp/opencode/z_6610_drat_result.txt, /tmp/opencode/z_6610.drat
```

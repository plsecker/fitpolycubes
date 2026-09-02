# T 5×5×12 Macro-Walk Certificate — Selection, Recovery, Verification

**Date**: 2026-08-27
**Artifact**: `data/frontier/certificates/t_5x5x12_cycle01_macro_walk.json`
**Format**: `fitpolycubes.macro-walk` v1, semantics pinned
`fitpolycubes.macro-walk/semantics-1`
**Packer**: `tools/frontier/t_piece/pack_t_5x5x12_walk.py`

---

## 1. Result selected and why

**Selected result**: *The T-pentacube Macro graph on cross-section 5×5 is
cyclic; equivalently (faithfulness theorem) T tiles the box 5×5×12.*

This row appears as the closing row of the reclassification table in
`t_3xn_cyclicity_criterion.md` §6 — the document produced by the recent
repair audit of the T 3×N cyclicity analysis. It was chosen because it was
the **only remaining non-self-supported row of that repaired table**, and the
best-supported uncertified T result in the repository:

| Evidence type | Status before this work |
|---|---|
| Repository code output | Complete closure artifact (54,434 states, `queue_exhausted=true`, `cap_hit=false`) recorded in `data/frontier/t_piece/t_5x5_certificate.json` / `t_5x5_global_certificate.json`; criterion doc cites it loosely ("completes in tests with 0 reachable") |
| Catalogue data | `Box(5,5,12)` sole 5×5 prime in `catalogues/t_catalogue.py RAW_PRIMES`; `impossible_reason` marks `(5,5,c%12≠0)` published-impossible |
| Self-contained Macro-walk certificate | **none** — the five packed T witnesses cover only the 3-wide primes (3×7×20, 3×8×15, 3×10×14, 3×11×30, 3×12×15); `data/frontier/certificates/` held no T file at all |

Candidates considered and rejected:

* 3×9 acyclicity — not certifiable by a walk certificate (certificates prove
  existence, never absence).
* Catalogue-only 3-wide primes N ≥ 13 (e.g. 3×13×20) — no placements exist
  anywhere in the repository; a witness would require a fresh CP-SAT solve,
  i.e. a new search, which this task excludes unless necessary. Not needed.
* Box(3,10,10) — carries a doc/catalogue tension (`RAW_PRIMES` lists it while
  criterion §6/§7 reads it as searched-no-solution); touching it risks
  entangling truth-table questions explicitly out of scope here.

## 2. Smallest constructive witness

A closed Macro walk of length 12 through state 0 on cross-section 5×5 (one
fill per layer ⇒ exactly a tiling of 5×5×12 by 60 T pentacubes). Anything
smaller cannot establish cross-section 5×5 cyclicity, since walk length must
equal box height z.

## 3. Witness recovery — no new search

The existing artifact `data/frontier/t_piece/t_5x5_certificate.json`
(`primitive_cycles[0]`, identical content to
`tools/frontier/_t_5x5_concrete_cycles.json`) already stores the primitive
12-cycle **with per-edge concrete placements in window coordinates**
(`concrete_placements`, dz ∈ {0,1,2}). The packer re-derived everything from
those raw fills:

* all 12 edges: shapes congruent to the declared T geometry under det=+1
  rotations; pairwise disjoint; disjoint from source occupancy; slot-0
  completion;
* shift(source + fill) reproduces every stored path id exactly under the
  pinned packing `l0 | l1<<25`, `cell_id = x + 5y`;
* lifted union = exact disjoint cover of 5×5×12 (60 pieces, 300 cells);
* terminal predecessor walk[11]: L1 = ∅, |L0| = 5, remaining 20 cells covered
  exactly by the final edge's four all-slot-0 flat-T pieces.

Nothing was copied unverified into the certificate; the packer refuses to emit
on any inconsistency.

## 4. Verification (Layer A generic + Layer B piece-specific + schema)

| Checker | Role | Result |
|---|---|---|
| `tools/frontier/macro_certificate_generic_checker.py`, run isolated (`python3 -I`, cwd `/tmp`) | Layer A, C1–C7g | VALID |
| `tools/frontier/check_macro_certificate_independent.py` (T-era independent checker, legacy alias keys) | Layer A | INDEPENDENTLY VALID |
| `tools/frontier/macro_certificate_verifier.cpp` (C++17, stdlib only), built via `python3 -m ziglang c++` | second implementation per format spec §7 | LAYER-A VALID |
| `tools/frontier/validate_t_macro_walk.py` | repository-specific: registry orientation set, Direction-A re-extraction from raw tiling, repo-transition edge legality, exhaustive flat exact-cover gate check | VALID |
| `tools/frontier/macro_certificate_schema.json` (jsonschema Draft7, `$id` self-resolved) | structural schema | SCHEMA VALID |

Negative controls (P7 fail-closed), mutated copies rejected by the isolated
generic checker: shifted fill cell, flipped walk-state bit, duplicated
placement (edge fill and alias), wrong `semantics_id`, corrupted geometry,
dz=3 out-of-window cell, lying `terminal` block, wrong box z. All exit≠0.

## 5. What the certificate proves

1. There exists a closed Macro walk of length 12 through state 0 for the T
   pentacube on cross-section 5×5 — machine-checked from the file alone by
   three mutually independent implementations.
2. By the faithfulness theorem (external mathematics,
   `t_macro_faithfulness.md`): **T tiles 5×5×12**, and the 5×5 cross-section
   is cyclic (the repaired criterion's gate theorem route; its constructive
   clause is realized at the terminal edge).
3. Constructively: the tileability is exhibited, not just counted out.

## 6. What it does NOT prove

* **Minimality**: not that z = 12 is the smallest tileable height for T on
  5×5 — that remains catalogue-level published data.
* No uniqueness/counting claim, no period characterization beyond the
  exhibited length, no claim about other cross-sections, no pred(0)
  completeness for 5×5, no new acyclicity statement anywhere.
* The closure counts (54,434 states etc.) are cited provenance, not
  re-established by the certificate.
* Catalogue truth tables were **not modified**; the 5×5 row's status label
  stays "PROVED COMPUTATION (cyclicity)" — only its evidence pointer changed.

## 7. Evidentiary delta

Before: supported primarily by *repository code output* (a closure run whose
record in prose was vague) plus *catalogue consistency*. After: same claim
rests on a self-contained, third-party-checkable object verified by four
independent code paths with clean mutation-rejection behavior — matching the
evidentiary standard of the five 3-wide T witnesses produced during the
repair audit. Every row of the reclassification table in
`t_3xn_cyclicity_criterion.md` §6 now has a self-contained constructive
witness for its CYCLIC entries.

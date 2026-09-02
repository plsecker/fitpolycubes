# Pentacube Macro-Walk Certificate Format

**Date**: 2026-08-26
**Status**: FORMAT SPECIFICATION v1 (generic) — supersedes the ad-hoc "v2"
T-witness layout as the project-wide certificate format. The five existing
T witnesses remain valid and are readable by the generic checker via the
documented key aliases.
**Revision 2026-06-26a→2026-08-26a**: formal protocol audit applied; semantics
now pinned via `conventions.semantics_id`; Layer-A checker hardened
(see §9). All eleven certificates re-validated.
**Origin**: extracted from the validated T 3×N cyclicity-certificate work
(see `docs/frontier/t_piece/t_3xn_cyclicity_criterion.md`, §10).

---

## 1. Purpose and scope

A Macro-walk certificate is a self-contained evidence object demonstrating that
a named pentacube admits a closed walk through state 0 of the Macro graph on a
given cross-section — equivalently (by the faithfulness theorem, which is
*mathematics*, not part of the certificate) that an a×b×z box is tileable.

Goals: reusable across all pentacubes; verifiable by a checker that imports
nothing from this repository; explicit separation between what is machine-
checked, what is piece-specific verification, and what is mathematical claim.

Non-goals: no new theory; no catalogue integration; no solver.

## 2. Field taxonomy: generic vs piece-specific

| Field / routine | Class | Notes |
|---|---|---|
| `box` dimensions | generic | any cross-section |
| `piece.geometry` | generic *as data* | the certificate carries it; checker never hardcodes |
| orientation convention (proper rotations, det=+1) | generic | chiral pieces supported naturally |
| cell indexing `x + a*y`, state packing `l0 \| l1<<N` | generic | declared in-cert |
| `edge_fills` (window-coordinate placements) | generic | the heart of the evidence |
| Macro shift/fill semantics | generic | set-arithmetic definable from conventions alone |
| walk closure `s_0 = s_z = 0` | generic | |
| tiling reconstruction ≡ stored tiling | generic | |
| terminal-predecessor structural facts (popcounts, final-edge slot-0 property, complement coverage) | generic *observations* | computed and reported, never interpreted |
| gate theorem instantiation ("preds of 0 are exactly …") | **piece-specific** | T: L1=L2=∅ + flat coverability; S: single gate state; each piece needs its own statement + proof |
| mod-5 divisibility of terminal complement | **piece-specific corollary** | follows from T's flat 5-cell orientations; false as a general test |
| flatness *as a geometric fact* (`all dz == 0`) | generic observation | its *significance* is piece-specific |

## 3. Layer separation

**Layer A — generic Macro-walk verification.** Pure semantics from the
certificate's own conventions: geometry congruence under proper rotations,
disjointness, slot-0 completion, shift arithmetic, closure, reconstruction.
Implemented once in `tools/frontier/check_macro_certificate_independent.py`
(T-era, legacy keys) and `tools/frontier/macro_certificate_generic_checker.py`
(generic, stdlib-only). No repository imports permitted here.

**Layer B — piece-specific gate/predecessor verification.** For each piece P,
a separate small verifier (or argument) establishes that the terminal facts
reported by Layer A instantiate P's gate theorem — e.g. for T: "terminal node
has L1=L2=∅ and complement exactly covered by final-edge pieces ⇒ that edge is
P→0 and the theorem's sufficient condition is realized". B consumes A's
output; it may import repository code; it is per-piece by nature.

**Layer C — mathematical claims.** Prose objects inside the certificate
(`claims[]`) with status labels (THEOREM / PROVED COMPUTATION / EMPIRICAL
OBSERVATION / CONJECTURE / REFUTED CLAIM), statements, and pointers to
documents or checkers. **Never evaluated by Layer A code.**

## 4. Schema (summary)

Normative machine-readable version: `tools/frontier/macro_certificate_schema.json`.

```jsonc
{
  "format": "fitpolycubes.macro-walk",
  "format_version": 1,
  "piece": {
    "name": "V",                          // label only; NOT trusted by checkers
    "geometry": [[0,0,0], "... 5 cells"], // authoritative shape
    "cell_count": 5
  },
  "conventions": {
    "semantics_id": "fitpolycubes.macro-walk/semantics-1",   // REQUIRED, pins semantics
    "cell_id": "x + a*y, 0 <= x < a, 0 <= y < b",
    "state_packing": "l0 | (l1 << NCELLS); slot 2 always empty",
    "rotations": "proper only (signed permutation matrices, det=+1)",
    "window_coords": "edge k pieces relative to layer k: (x,y,dz), dz∈{0,1,2}",
    "edge_legality_definition": "<full prose definition>"
  },
  "box": {"a": 5, "b": 5, "z": 6},
  "walk":      [{"step": 0, "l0": 0, "l1": 0, "hex": "0x0"}, "... z+1 states"],
  "edge_fills": ["[ [ [x,y,dz]×5 ] × pieces_k ] for k = 0..z-1"],
  "box_tiling": ["[ [x,y,z]×5 ] × (abz/5)   (alias accepted: 'placements')"],
  "terminal": {                            // OPTIONAL, generic facts only
    "predecessor_state_index": "z-1",
    "l0_popcount": 22, "remaining_cells": 3,
    "final_edge_all_slot0": true,
    "final_edge_covers_complement": true
  },
  "provenance": {"generator": "...", "date": "...", "solver": "..."}, // unverified
  "claims": [                              // OPTIONAL, Layer C, never machine-checked
    {"id": "C1", "statement": "...", "status": "THEOREM", "evidence": ["docs/..."]}
  ]
}
```

## 5. Independent verification principles

- **P1 Self-containedness.** Every semantic input (geometry, indexing,
  packing, rotation rule, edge definition) is inside the file. The checker
  reads no registry, no catalogue, no explorer.
- **P2 Semantics from declarations.** Orientation images are derived at check
  time from `piece.geometry`; the checker asserts nothing about how many
  orientations exist.
- **P3 Edges by set arithmetic.** Legality of u→v is checked directly against
  the stored fill: congruence, pairwise/state disjointness, slot-0 completion,
  shift equality. No search, no templates.
- **P4 Redundant consistency.** The box tiling must be independently exact and
  must equal the reconstruction from edge fills (two routes to the same fact).
- **P5 Observations ≠ claims.** Terminal facts are reported as observations;
  interpreting them requires Layer B/C. The generic checker prints this
  boundary explicitly.
- **P6 Isolation.** The generic checker runs under `python3 -I` from outside
  the repo tree; CI should do exactly that.
- **P7 Negative-testability.** Mutated certificates (moved fill cell, flipped
  state bit, duplicated placement) must fail. Checkers ship with no mutation
  tests themselves, but acceptance requires them (done for T; repeat for any
  new checker).
- **P8 Semantics pinning.** The certificate must declare
  `conventions.semantics_id = "fitpolycubes.macro-walk/semantics-1"`. A
  checker implements exactly that pinned semantics and refuses anything else;
  the human-readable `conventions` prose is a restatement, never parsed.
- **P9 Fail closed.** Malformed input (wrong types, degenerate boxes,
  non-connected geometry, out-of-window cells) produces an explicit FAIL, not
  an exception or silent acceptance. JSON booleans never pass as integers.

## 6. Meaningful certificate vs replay log

A **mathematically meaningful** certificate supports all of C1–C7 below by a
third party using only the file:

- C1 volume/piece-count sanity vs `cell_count`;
- C2 stored tiling: bounds, congruence, exact disjoint cover;
- C3 walk endpoints and length;
- C4 every edge legal by set arithmetic;
- C5 recomputed walk equals stored walk, closes at 0;
- C6 fills reconstruct exactly the stored tiling;
- C7g terminal predecessor facts (structural; constructive when
  `final_edge_covers_complement` holds).

A **replay log** records states or paths without the data needed to re-derive
them: e.g. `tools/frontier/_*_concrete_cycles.json` store cycle paths/edges as
state ids only — they demonstrate nothing to an outsider and must not be cited
as evidence. Upgrading a replay log to a certificate requires recovering the
realizing fills (a genuine computation), not a format conversion.

Existing artifact classification: the five T witnesses (format v2) satisfy
C1–C7g meaningfully; `_t_3x7_concrete_cycles.json` and siblings are replay
logs; `data/v_5x5x6_certificate.json` / `w_5x7x9_certificate.json` contain raw
tilings (strong evidence for tileability) but are not Macro certificates until
packed with walks/fills — demonstrated for one V solution alongside this spec.

## 7. Circularity rules

The generic checker must not depend on: `common/registry`, catalogue modules,
`common/polycube_utils.generate_placements`, `tools/frontier/piece_utils`,
any macro explorer/transition implementation. Compliance is operational:
run isolated (`python3 -I`, cwd outside the repo). Producers/convertisers MAY
use repository code — they are on the trusted side of the boundary.

A second, independent implementation exists:
`tools/frontier/macro_certificate_verifier.cpp` (C++17, stdlib only; build:
`python3 -m ziglang c++ -std=c++17 -O2 -o mcv <file>.cpp` or any g++/clang).
Cross-implementation results and the two defects it exposed (one per
implementation) are recorded in
`docs/frontier/certificate_interop_report.md`. Third parties should treat
agreement of BOTH checkers as the current confidence bar for Layer A.

## 8. Formal protocol audit (2026-08-26a)

### 9.1 Trust boundary — what Layer A establishes from the file alone

> There exists a 5-cell, face-connected integer polycube G (the declared
> geometry) and sequences of states (s_0,…,s_z) and placement sets
> (F_0,…,F_{z−1}) such that s_0 = s_z = ∅; each F_k consists of pairwise-
> disjoint placements, each congruent to G under a det=+1 signed permutation,
> disjoint from the occupied cells of s_k, with all cells inside the box
> window, jointly completing slot k of s_k; and shift(s_k ∪ F_k) = s_{k+1}.
> The lifted union of all F_k is exactly an a×b×z disjoint cover.

Consequently Layer A proves **existence** of a closed Macro walk under the
pinned semantics for the *declared* piece. Tileability follows only via the
faithfulness theorem, which is external mathematics, not part of Layer A.
Everything else — catalogue status, minimality, solution counting, gate
characterizations — is outside the boundary.

### 9.2 Formerly implicit assumptions, now explicit

| Assumption | Status |
|---|---|
| coordinate indexing `x + a·y`; packing `l0 \| l1<<N` | pinned by `semantics_id`; prose decorative |
| orientation enumeration = exactly the 24 det=+1 monomial matrices | built into checker; group completeness structural |
| handedness | identity of the piece **is its geometry**, never its `name` or `chiral` flag; declaring mirrored geometry certifies the mirrored piece |
| window height 3 (`dz ∈ {0,1,2}`) | pinned; max pentacube z-span is 5 for I upright — certificates using taller spans are out of scope and refused by bounds check |
| degenerate boxes (`a,b,z ≥ 1`) | enforced (previously crashed on z=0) |
| empty fills / already-full slot 0 | legal, handled vacuously |
| stored walk is **one witness**, not canonical | certificates prove existence only; no uniqueness/counting claim |
| geometry must be distinct + face-connected | now checked directly (was incidental via congruence) |
| fill cells in-bounds before bit-indexing | now checked at C4 (bit-aliasing via out-of-range x/y previously rejected only accidentally/transitively; negative indices crashed) |
| dual tiling keys | conflict now refused |
| big integers | masks need >64 bits for NCELLS ≥ 33; third parties must use bigint or byte-array masks |

### 9.3 Field classification

| Class | Fields |
|---|---|
| mathematically necessary | `piece.geometry`, `piece.cell_count`, `box`, `walk[].l0/l1`, `edge_fills`, `conventions.semantics_id` |
| needed only for reconstruction cross-check | `box_tiling`/`placements` (derivable from fills; kept as an independent second route) |
| informational/provenance | `piece.name`, `chiral`, notes, `provenance`, `claims[]`, `hex` |
| redundant (validated when present) | `walk[].step` (must equal position), `terminal` block (derived facts) |
| dangerous if trusted | `name`, `chiral`, prose conventions, `provenance`, `claims` — all ignored by Layer A; semantics pinned via id |

Smallest sufficient certificate: geometry + cell_count + box + walk(l0,l1) +
edge_fills + `semantics_id`. Everything else is convenience or evidence
hydration, retained for auditability.

### 9.4 Adversarial battery results (hardened checker, isolated runs)

Rejected cleanly: wrong/missing `semantics_id`; z=0 box; disconnected or
duplicate-cell geometry; whole-piece out-of-window translation; negative
coordinates; conflicting dual tiling keys; scrambled step labels;
cell_count mismatch; omitted/duplicated edge; declared mirror geometry of a
chiral piece (S); altered walk state; shifted fill cell; duplicated placement;
corrupted geometry. Accepted correctly: proper-rotation repacks (S, W);
declaring mirror geometry of an **achiral** piece (W) — same orientation set.
Pre-fix findings that motivated the hardening: convention prose silently
ignored; z=0 crash; dual-key silent preference; step field unvalidated;
out-of-bounds fills caught only accidentally or by crash.

### 9.5 Status

**READY FOR THIRD-PARTY VERIFICATION** within the documented scope: existence
of closed Macro walks (hence tileability witnesses) for declared pieces and
boxes, verifiable with stdlib-only tooling from the certificate alone.
Explicitly out of scope: exhaustiveness, minimality, periods, gate theorems,
solution counts.

## 9. Demonstrations (what they show and do not)

Demonstrated with real data:

- **T** — five witnesses (3×7×20, 3×8×15, 3×10×14, 3×11×30, 3×12×15), packed
  in generic v1 form; all pass Layer A under the isolated generic checker.
- **V** — `data/frontier/certificates/v_5x5x6_solution01_macro_walk.json`,
  packed from solution #1 of the existing exhaustive V 5×5×6 enumeration;
  passes C1–C7g. Non-T geometry and orientation structure.
- **I** — `i_1x5x3_synthetic_macro_walk.json`, hand-built trivial self-loop;
  degenerate-case smoke test only.
- **W (orientation-machinery demonstration; achiral — see correction below)** —
  `w_5x7x9_solution01_macro_walk.json` packs solution #1 of the existing
  exhaustive W 5×7×9 enumeration (63 pieces, 9-edge closed walk); passes
  Layer A isolated. A second file,
  `w_5x7x9_solution01_rot90_macro_walk.json`, applies the genuine proper
  rotation (x,y,z) → (−y+b−1, x, z), transposing the cross-section to 7×5;
  it also passes — a positive control confirming that congruent rotations are
  accepted while nothing about the piece is hardcoded.

**Chirality finding (correction).** W was expected to be the first genuinely
chiral demonstration; computation shows otherwise. The mirror image of the
embedded W geometry lies *inside* its proper-rotation orbit: the explicit
det=+1 map (x,y,z) → (−x, y, −z) (180° rotation about y) realizes the
x-reflection. This is the standard fact that **every planar pentacube is
achiral in 3D** (in-plane reflections lift to proper rotations), consistent
with Sicherman nomenclature reserving primed mirror twins for nonplanar
pieces (E,S,J,R,H,G). Earlier frontier notes describing W as "chiral (12
orientations)" conflated pentomino-plane handedness with pentacube handedness;
the correct statement is that W has 12 distinct orientations and is achiral.
The certificate files record `"chiral": false` with this note.

The orientation machinery handles genuine chirality correctly by construction:
for the S pentacube the proper-rotation orbit has size 12 and the mirror image
is **not** a member, so any certificate whose placements use mirrored S pieces
fails check C2 ("not congruent to embedded geometry") — the same mechanism as
the verified geometry→T / geometry→S negative controls.

**S — genuinely chiral demonstration (2026-08-26 validation pass).**
`data/frontier/certificates/s_4x5x6_solution01_macro_walk.json` packs the
existing verified 24-piece S tiling of 4×5×6
(`data/frontier/s_4x5x6_tiling.txt`, verification documented in
`docs/frontier/s_piece/4x5_scc_structure.md`) into generic v1 form and passes
Layer A under the isolated checker (`python3 -I`, C1–C7g, including a
degenerate empty final fill). Chirality is established explicitly for the
embedded geometry: proper-rotation orbit size **12**, x-mirror image **not in
the orbit**. Controls, all as expected: a full-certificate proper-rotation
repack (cross-section transposed to 5×4,
`s_4x5x6_solution01_rot90_macro_walk.json`) is **accepted**; declaring the
mirror geometry instead of S is **rejected** at C2 (true-S placements are not
congruent to the mirror's orientation set); unrelated geometries (T, W),
corrupted geometry, shifted fill cell, altered walk state and duplicated
placement are all rejected. The one control that could not be constructed —
mirroring a single placement in place — had no collision-free instance in this
tiling; its rejection mechanism is covered by the declared-geometry mutation.
No S-specific Layer-B theorem is claimed by the certificate; existing S gate
discussion remains in `docs/frontier/t_piece/t_macro_faithfulness.md` §5.1 and
the s_piece analyses.

- **T (5×5 cross-section, 2026-08-27)** —
  `t_5x5x12_cycle01_macro_walk.json` packs the length-12 primitive cycle of
  the existing complete T 5×5 closure artifact (`t_5x5_certificate.json`) into
  generic v1 form and passes Layer A under all three independent checkers plus
  `validate_t_macro_walk.py` (which re-extracts the walk from the raw tiling
  against the repository transition and checks the repaired gate clause).
  Gives the last non-self-supported row of the repaired cyclicity table
  (`t_3xn_cyclicity_criterion.md` §6) a self-contained constructive witness.
  Details: `docs/frontier/t_piece/t_5x5x12_macro_walk_certificate.md`.

Not demonstrated here: packing further existing tilings; Layer-B verifiers
for pieces other than T; any *new* exhaustive claims. None of these are
provided by this specification.

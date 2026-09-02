# Z 6x6x10 UNSAT Certificate Package

**Claim.** The 6x6x10 box cannot be tiled by the Z pentacube (piece 5/11).
This package contains the complete machine-checkable evidence: a DIMACS CNF
encoding of the exact-cover problem, a DRAT proof of unsatisfiability
produced by CaDiCaL, an LRAT certificate produced by drat-trim, TWO
independent checker verdicts (drat-trim AND lrat-check, both
`s VERIFIED`), an independent semantic audit script for the encoding, and
full provenance.

Claim status: **VERIFIED — both standard checkers accept the proof.**

## Package contents

| file | sha256 (see hashes.txt) | size |
|---|---|---|
| z_6610.cnf | 034899621ba6f091a6ee1f80df88934d0b812bc9bda1023df6b8d66c9c3d719d | 2.6 MB |
| z_6610.drat | a208875f62747d3dead8e4e297d2c4c563c103ca074f95dfe39dd1bb15fa4239 | 2.42 GB (7,425,174 DRAT lines) |
| z_6610.lrat | f0f70f6cc3d921a87a227294c702ebb241759325085857fe437c80cca610481a | 2.45 GB (LRAT, emitted by drat-trim -L) |
| placement_set.json | a21aec07b4f43bdff08b46ddbc6b11f2e213484fdb9eb47ca88b571ea486dbb7 | 124 KB (2,176 placements) |
| var_map.json | f9975e371cd25312c9565b8bb984f508c8489716500424d8ff2bb66a4e18dee2 | variable id -> placement |
| metadata.json | 00156cc9547767552c5c64db9982dd3ba572dfe301d4167937ecd12593dfdab1 | provenance + runs (see note) |
| z_6610_verify_encoding.py | 1f2c2e8b4927e6470992c1ac34ed15afa7ce29270796494a0807a0ef2b2417f6 | independent semantic audit |
| solve_command.py | 201f5f5e55fb115f26662f1c5e5aefb7dea6dd6a28e9b24e7ccdcb355d907168 | exact certified-run script |
| README.md | 5be5a55d13168df0... (this file; sha in hashes.txt) | verification guide |

z_6610.drat and z_6610.lrat are .gitignore'd inside this directory (2.42 GB
+ 2.45 GB); their sha256s pin them for transfer. metadata.json records the
file hashes as of its own writing; hashes.txt is authoritative for the
final files.

## Problem semantics (what the CNF encodes)

Variables x_1..x_2176: one per legal placement of the Z pentacube (piece
cells (0,0,0),(1,0,0),(1,1,0),(1,2,0),(2,2,0) -- provenance
PENTACUBES["Z"]) in the 6x6x10 box, under all 12 orientations. Clauses:

* per box cell (360 cells): OR x_p over the placements covering it -- at
  least one piece covers every cell;
* per pair of placements sharing a cell: -x_p OR -x_q -- no overlaps.

Hence satisfying assignments <-> exact tilings of the 6x6x10 box by 72 Z
pentacubes, and UNSAT <=> no tiling exists.

## Verification record (2026-08-28/29, this VM)

| checker | version/commit | build | command | result | runtime | peak RSS |
|---|---|---|---|---|---|---|
| drat-trim | marijnheule/drat-trim commit 2e3b2dc0ecf938addbd779d42877b6ed69d9a985 (2024-11-25) | zig cc 0.16.0, -std=c99 -D_DEFAULT_SOURCE -O2 | ./drat-trim z_6610.cnf z_6610.drat | **s VERIFIED** (145,987/195,976 clauses in core; 2,059,922/3,730,947 lemmas in core; 0 RAT lemmas; 232,102,828 resolution steps) | 455.2 s (wall 7:35) | 1.19 GiB |
| drat-trim -L (LRAT emission) | same binary | same | ./drat-trim z_6610.cnf z_6610.drat -L z_6610.lrat | **s VERIFIED** | 496.4 s | 2.79 GiB |
| lrat-check | same repo/commit | zig cc 0.16.0, -std=c99 -D_DEFAULT_SOURCE -DLONGTYPE -O2 | ./lrat-check z_6610.cnf z_6610.lrat | **c VERIFIED** (Added clauses = 2,255,898; Deleted = 2,255,775; Max live = 195,976) | 25.2 s | small |

All three runs exited 0. No warnings that weaken the result were printed
(the checker logs are archived at /tmp/opencode/z_6610_drattrim_result.txt
and /tmp/opencode/z_6610_drattrim_lrat_result.txt).

## How to re-verify (third party)

### Step 1 -- semantic audit of the encoding (fast, pure Python, no repo code)

python3 z_6610_verify_encoding.py .

Expected final line: ENCODING AUDIT: ALL CHECKS PASSED.

### Step 2 -- independent re-decision with any complete SAT solver

kissat z_6610.cnf            # expect: s UNSATIFIABLE

### Step 3 -- verify the DRAT proof (formal certificate check)

git clone https://github.com/marijnheule/drat-trim && cd drat-trim && make
./drat-trim z_6610.cnf z_6610.drat
#    expected output: s VERIFIED   (~8 min, ~3 GB RAM)

### Step 3b -- verify the LRAT certificate (fast, if you have z_6610.lrat)

make lrat-check              # (Makefile builds it with -DLONGTYPE)
./lrat-check z_6610.cnf z_6610.lrat
#    expected output: c VERIFIED   (~25 s)

### Step 4 -- provenance check

sha256sum -c hashes.txt
python3 -c "import json; m=json.load(open('metadata.json')); print(m['runs'])"

## Provenance summary

* Placement generation: placements_cells(6,6,10) -- verified set-identical
  to the repository's trusted common/polycube_utils.generate_placements
  (2,176 = 2,176, frozenset equality, zero differences).
* Clause construction: per cell >=1 over covering placements; per
  shared-cell pair an AMO clause; no other clauses; 0 mixed-polarity.
* Solver: CaDiCaL as bundled in python-sat 1.9.dev15 (default options).
* Encoding-pipeline validation: the published machine-readable tilings of
  the smallest known-SAT Z box (6x10x10; Shindo 1997, ISHINO 2000) were
  extracted from puzzlewillbeplayed.com/Pentominoes/Z-10x10x6.html: 4/4
  solutions are geometrically valid Z tilings; all 480 published piece
  placements are members of the audited placement set; forcing them as SAT
  assumptions reproduces the published tiling exactly through the same
  encode->solve->extract->verify chain.
* Known-UNSAT controls: 5x5x5, 6x6x5 (catalogue rule 5x{5,6,7}) -- UNSAT
  under three solver families (CaDiCaL153, Minisat22, Glucose4), and under
  the independent planar-DP prototype.

## Notes

* z_6610.drat is a DRAT (deletion-resolution asymmetric tautology) proof:
  every line is a learned clause admitting RUP (reverse unit propagation)
  w.r.t. the current formula, or a clause deletion. z_6610.lrat is the
  equivalent LRAT certificate emitted by drat-trim (-L): each line references
  input/lemma ids and explicit resolution pivots, checkable by lrat-check
  without the original solving engine.
* The encoding is monotone-safe: it contains only coverage and no-overlap
  clauses, both satisfied by any genuine tiling. Given the verified complete
  placement set, a spurious UNSAT is impossible; the only way the claim
  could fail is a solver or checker defect, which the two independent
  checkers (drat-trim and lrat-check) and the optional Step-2 re-solve would
  expose.

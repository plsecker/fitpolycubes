# Z 4x11x15 UNSAT Certificate Package

**Claim.** The 4x11x15 box cannot be tiled by the Z pentacube (piece 5/11).
This package contains the complete machine-checkable evidence: a canonical
deduplicated DIMACS CNF encoding of the exact-cover problem, the native
binary-DRAT proof produced by CaDiCaL 1.5.3, an independent drat-trim
verdict (`s VERIFIED`), an independent standalone semantic audit, and full
provenance.

Claim status: **VERIFIED — solver UNSAT + independent checker `s VERIFIED`
+ semantic audit `ALL CHECKS PASSED`.**

## Package contents

| file | sha256 (hashes.txt) | size |
|---|---|---|
| z_4x11x15.cnf | ecb549acd394ce9d...44c16 | 3.67 MB (4096 vars, 265000 clauses) |
| z_4x11x15_native2.drat | 64c7bef652f67f19...d3ea2 | **3.61 GB binary DRAT** (gitignored locally, pinned by hash) |
| z_4x11x15_native2.drat.sha256 | — | pinned proof hash |
| placement_set.json | f13eda45b40ed158...db8729 | 4096 placements, independent cross-check PASS |
| var_map.json | c362b89ac8a3f03f...361e0 | variable id -> placement (canonical order) |
| z_4x11x15_cadical.out | c263a00d13f2ca4f...0c14c | solver log: conflicts 8,771,150; decisions 19,726,489; propagations 1.90G; 2117.5 s; exit 20 (UNSAT) |
| z_4x11x15_drattrim.out | c678e7af1601c77a...e579 | checker log: `s VERIFIED`, 647,547,908 resolution steps |
| metadata.json | a781aa421d976d45...2ef74 | full run history incl. the earlier encodings |
| verify_encoding.py | 984a74c731478f00...be69 | standalone semantic audit (no repo imports) |
| solve_command.py | see hashes.txt | exact certified commands |

z_4x11x15_native2.drat is .gitignore'd inside this directory (3.61 GB);
its sha256 is pinned here and in metadata.json for transfer/re-verification.

## Problem semantics (what the CNF encodes)

Variables x_1..x_4096: one per legal placement of the Z pentacube (cells
(0,0,0),(1,0,0),(1,1,0),(1,2,0),(2,2,0); 12 proper-rotation orientations)
in the 4x11x15 box. Clauses:

* per box cell (660 cells): OR x_p over the placements covering it — at
  least one piece covers every cell;
* per pair of placements sharing a cell: -x_p OR -x_q — no overlaps
  (264,340 distinct pairs; duplicates from pairs sharing two cells are
  removed by the canonical deduplication).

Hence satisfying assignments <-> exact tilings of 4x11x15 by 132 Z
pentacubes, and UNSAT <=> no tiling exists.

## Verification record (2026-09-04)

| step | engine | command | result | runtime |
|---|---|---|---|---|
| solve | native CaDiCaL 1.5.3 | `cadical z_4x11x15.cnf z_4x11x15_native2.drat` | `s UNSATISFIABLE` (exit 20) | 2117.5 s |
| check | drat-trim (same build as the certified 6x6x10 package) | `drat-trim z_4x11x15.cnf z_4x11x15_native2.drat` | **`s VERIFIED`** — 258,206/265,000 clauses in core; 4,859,533/11,822,097 lemmas in core; 0 RAT lemmas; 647,547,908 resolution steps | 2458.2 s |
| semantic audit | standalone Python | `python3 verify_encoding.py .` | **ALL CHECKS PASSED** | ~1 min |

metadata.json also records the earlier, superseded runs on the
non-deduplicated 356,020-clause encoding (native CaDiCaL UNSAT 2349.6 s;
drat-trim `s VERIFIED` 2591.0 s) and the initial proof-less pysat run
(1865.2 s).  This package supersedes those artefacts; they are retained as
corroboration only.

## How to re-verify (third party)

### Step 1 — semantic audit of the encoding (fast, pure Python, no repo code)

    python3 verify_encoding.py .

Expected final line: ENCODING AUDIT: ALL CHECKS PASSED.

### Step 2 — verify the DRAT proof (formal certificate check)

    git clone https://github.com/marijnheule/drat-trim && cd drat-trim && make
    ./drat-trim z_4x11x15.cnf z_4x11x15_native2.drat
    #    expected output: s VERIFIED   (~41 min, ~3 GB RAM)

### Step 3 — optional independent re-decision with any complete SAT solver

    kissat z_4x11x15.cnf            # expect: s UNSATISFIABLE

### Step 4 — provenance check

    sha256sum -c hashes.txt         # (the .drat line must be added back if
                                    #  the proof was fetched separately)
    cat z_4x11x15_native2.drat.sha256

## Notes

* The encoding is the certified plain ALO+AMO recipe of the Z 6x6x10
  package with canonical clause deduplication, and NO symmetry-breaking
  predicates of any kind (symmetry clauses are a new proof obligation; the
  H 5x5x6 pair-scheme bug showed they can silently destroy solution orbits).
* Placement set cross-checked: repo `generate_placements` vs an independent
  first-principles regeneration — set-identical (4096 = 4096).
* The pysat 1.9.dev15 proof-capture path drops the final conflict on proofs
  past ~2^24 lines (documented in metadata); the native CaDiCaL route used
  here bypasses it and is the recommended proof path.
* Catalogue: Z 4x11x15 is recorded as SEARCHED_NO_SOLUTION with this
  package as provenance.

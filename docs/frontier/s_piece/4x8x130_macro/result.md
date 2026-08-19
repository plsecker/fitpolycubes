# S Pentacube 4×8×130: Macro Investigation — Authoritative Result

Status: **complete** (documentation/artifact preservation)
Branch: `frontier-solutions`
Date: 2026-08-20

This document is the authoritative write-up of the S-pentacube 4×8×130
Macro investigation: the 30,000,015-state Macro closure, the 2048
reconstructed 129-edge Macro walks, the low-level realization analysis
(2048 actual tilings), and the exact match against Shirakawa's published
solution (walk 311, identity symmetry).

All figures below are exact for the 30,000,015-state Macro closure.
Scope caveats are stated in [Section I](#i-scope--caveat).

---

## A. Motivation

### A.1 The published solution

Toshihiro Shirakawa (2014) published an S-pentacube tiling of the
4×8×130 box (832 S pentacubes, 4160 unit cubes) at

    https://puzzlewillbeplayed.com/Shirakawa/html/5-15-130x8x4.html

The page contains a single SVGZ diagram and no textual construction or
uniqueness claim (see [Section H](#h-shirakawa-comparison)).

### A.2 Why the Macro method

The low-level exhaustive frontier search for S in 4×8 boxes grows
enormously with box length.  The low-level run for 4×8×20
(`frontier_compact_pure_268m/`, compact pure frontier explorer) reached

    264,035,192 states
    4.0 GB on disk
    9,917,983 layer shifts
    still incomplete (280M capacity, run stopped)

and could not answer even the 4×8×20 question exhaustively.  The Macro
method collapses each completed z-slice into a single graph edge, turning
"reach 0 in exactly N layers" into reachability in a much smaller graph
of post-shift states.  For 4×8×20 the Macro closure (15M states) was
computed in ~11–13 minutes and answered the question exactly.

### A.3 The earlier 4×8×20 success

The 4×8×20 Macro investigation (see `docs/frontier/s_piece/4x8x20_*.md`)
established:

- the Macro graph of post-shift states;
- the **20-cycle**: a closed Macro walk `0 -> s* -> … -> WORD_MASK -> 0`
  of exactly 20 layers, with `s* = 6163195513375031274`;
- macro-path uniqueness for the 20-layer return (1 surviving source,
  1 surviving 19-edge walk) — at the coarse level.

The dramatic performance advantage: the 4×8×20 question lives at
distance ≤ 19, where the capped 15M closure is complete; the low-level
space at the same depth was still growing past 80M states.

---

## B. Exact Macro definitions

### B.1 Low-level state (unchanged, reused verbatim)

From `solvers/s_z_frontier_packed.py` (not modified):

- Box: 4 (x) × 8 (y) × N (z); `X_SIZE = 4`, `Y_SIZE = 8`, `NCELLS = 32`.
- A low-level state is one Python int with three 32-bit layer masks:
  bits 0–31 = layer 0, bits 32–63 = layer 1, bits 64–95 = layer 2.
- Bit `x + 4y` of a mask is cell (x, y), x ∈ [0,4), y ∈ [0,8).
- `WORD_MASK = 0xffffffff`; `layer_mask(s, i) = (s >> 32i) & WORD_MASK`.
- `first_empty(mask)` = lowest set bit position of `~mask` (first empty
  cell of a layer).
- `apply_template(state, t)` = `state | t` if `state & t == 0` else None.
- `shift_state(s) = s >> 32` (drop layer 0, shift layers 1,2 down).
- Templates: `build_templates()` from `PENTACUBES["S"]` =
  `{(0,0,0),(1,0,0),(2,0,0),(0,0,1),(2,1,0)}`; 3944 concrete placements,
  488 target templates (one list per anchor cell).

### B.2 MacroState

A **MacroState** is the **post-shift projection** of a low-level state:
the 96-bit window content after a completed layer has been shifted out.
Equivalently: the state `v` such that some pre-shift state
`p = WORD_MASK | (L0(v) << 32) | (L1(v) << 64)` shifts to `v`.

All low-level states sharing the same post-shift projection have
identical futures (the completed layer is sealed), so the Macro graph is
the quotient of the low-level graph by this projection.

### B.3 MacroEdge

A **MacroEdge** `u -> v` is:

1. start from post-shift state `u`;
2. repeatedly apply S placements at `first_empty(layer0(u))` until
   layer 0 == `WORD_MASK` (pre-shift state `p`);
3. shift: `v = p >> 32`.

For a given pre-shift state the placement sequence is deterministic
(first-empty cell + template order).

### B.4 z-slice / layer semantics

- Layer 0 of a state = the z-slice currently being filled.
- Layers 1, 2 = the next two slices' occupancy contributed by pieces
  anchored in the current/previous slice.
- After the fill, `shift_state` drops layer 0 (the completed slice) and
  the next slice becomes layer 0.

### B.5 Why one MacroEdge advances exactly one z-unit

The shift drops exactly one 32-bit layer mask = one 4×8 slice = one
z-unit.  A MacroEdge therefore always advances the frontier by exactly
one z-slice, and a tiling of the 4×8×N box corresponds to a Macro walk
of exactly N edges from 0 back to 0 (first edge fills slice 0, edge i
fills slice i+1).

---

## C. 4×8×20 result

- Macro closure: 15,000,991 states / 14,781,970 edges (15M cap hit),
  computed in ~11–13 minutes (~668–713 s per run).
- The 20-cycle: `0 -> s* -> … -> WORD_MASK -> 0`, 20 post-shift states,
  closed walk of 20 layers in the true Macro graph.  The 20 post-shift
  states (in order, starting after 0):

      6163195513375031274   (s*)
      13835058072323104239
      3993075831
      55840897340952456
      9838132153049676753
      2089671021646321023
      13523993509333176
      54046496222498049
      3430478137537398
      2691607028413209
      4934612199136503
      612490719515897646
      16285016559841080657
      217229141722890951
      6729013160573166
      2297949969
      1224979683048584328
      17294878168733286543
      4294967295            (WORD_MASK)
      0

- Contrast with low-level: the exhaustive low-level run reached
  264,035,192 states (4.0 GB) and was still incomplete; the Macro
  closure answered the distance-≤19 question exactly in minutes.
- Every edge of the 20-cycle has exactly 1 low-level placement
  realization (see `docs/frontier/results/macro_edge_realizations_results.txt`).

---

## D. 4×8×130 investigation

### D.1 Progression

1. **15M closure** (earlier runs): 15,000,991 MacroStates; the basin of
   0 (states with a path to 0) had **226 states**; the 20-cycle was
   fully inside it.
2. **Complete succ[0]**: the checkpoint's `succ[0]` was truncated by the
   first-generation cap; it was recomputed completely with
   `explore_source(0, templates, MAX_INTERMEDIATE_0 = 4_000_000)`:
   **331,765 first-generation sources** (the full first-generation tree
   from 0 has 3,162,387 states).
3. **226-state SCC discovery**: with complete `succ[0]`, Tarjan found
   the SCC containing 0 (226 states at 15M).
4. **Extension to 30,000,015 MacroStates**: the closure was re-run to
   the 30M cap (run log: `logs/macro_30m_run.log`,
   `logs/macro_30m_reported.log`).
5. **Final SCC structure** (30M): see D.2.

### D.2 Exact 30M figures

    macro_states            = 30,000,015
    num_sccs                = 29,999,520
    num_nontrivial_sccs     = 3

Nontrivial SCC sizes:

    10
    10
    478

The **478-state SCC** (the recurrent core):

    contains 0
    contains s*  (6163195513375031274)
    contains WORD_MASK (4294967295)

First generation:

    331,765 sources

Relevant entry points (first-generation sources inside the SCC) and
their SCC-internal distances to 0:

    6163195513375031274      distance 19   (s*, the 20-cycle start)
    17293822637554016271     distance 129  (the 130-solution entry; R = {59, 129})
    17293950180903112719     distance 39
    17306770486483095567     distance 39

Important distances:

    19     (s* -> 0)
    39     (two other entry points)
    59     (the other distance in R[entry])
    129    (the 4x8x130 solution distance)

### D.3 The 130 solution

    source      = 17293822637554016271
    entry       = 17293822637554016271
    DAG distance = 0
    SCC distance = 129
    total       = 129

`num_achievable_combinations = 1` at the coarse level
(source, entry point, DAG distance, SCC distance) — see Section E.

---

## E. Correction of the earlier "unique" claim

**Important.**  The earlier result

    num_achievable_combinations = 1

was **only** uniqueness at the coarse level:

    (source, entry point, DAG distance, SCC distance)

It was **NOT** uniqueness of the Macro walk.

The full reconstruction (`tools/frontier/reconstruct_130_path.py`,
exact DP over the SCC) found:

    2048 distinct 129-edge Macro walks

from

    17293822637554016271

to

    0

inside the 478-state SCC.  The earlier "unique combination" statement
is superseded by this document.

---

## F. Macro-walk structure

### F.1 Walk family

    2048 walks
    all walks are simple paths
    130 distinct MacroStates per walk
    no repeated states
    no cycles as subpaths
    none contains the known 20-cycle as a contiguous subpath

Across all walks:

    292 of 478 SCC states used
    316 of 514 SCC edges used
    317 distinct Macro edges including the first edge 0 -> ENTRY

### F.2 Observed branch structure

The reconstructed walk (walk 0) shows this R-set / branch shape
(129−k ∈ R[M_k] at step k):

    M0–M9:    2 branches
    M10–M25:  3 branches
    M26–M79:  1 branch
    M80–M119: 2 branches
    M120–M129: 1 branch

Walk 311 (Shirakawa's walk, see Section H) has branch points at
M0 (2 successors), M19 (4), M25, M32, M42, M47, M78, M82, M92, M105,
M106, M119 (2 each), and M129 = 0 (4); it is a shortest path to 0 from
M26 onward.

---

## G. Low-level realization result

The generalized realization analysis
(`tools/frontier/macro_edge_realizations_130.py`, same enumeration rules
as `macro_edge_realizations.py`: first-empty-cell, templates, monotone
fill, exact end state `p_target = WORD_MASK | L0(b)<<32 | L1(b)<<64`)
found:

    all 317 distinct edges have exactly 1 placement realization
    (exhaustive, no caps hit)

Therefore:

    2048 Macro walks
      ↕  (bijection: each walk's edges each have a unique realization)
    2048 actual tilings

with no hidden multiplicity on the used edges.

Full-tile certificate (walk 0, and independently the walk-311 tiling):

    832 S-pentacubes
    4160 cells
    exact 4x8x130 coverage
    CERTIFICATE: PASS

---

## H. Shirakawa comparison

### H.1 Exact source

    https://puzzlewillbeplayed.com/Shirakawa/html/5-15-130x8x4.html

Page title: "Pentomino Box Packing : 832 5/15 (130×8×4)", "Discovered
by 白川俊博 (Toshihiro Shirakawa) (2014)".  The page contains:

    832 5/15 pentomino/pentacube pieces
    one SVGZ diagram (5-15-4x8x130.svgz)
    4160 colored cells (10x10 px rects)
    piece identifiers 1..832 (HTML comments on the cells)
    no textual uniqueness claim
    no coordinates, no construction description

### H.2 Exact conversion

The SVG is 4 panels × 8 columns × 130 rows (panels at SVG columns
27–34, 18–25, 9–16, 0–7).  Canonical coordinates:

    x = panel index (0..3)
    y = column within panel (0..7)
    z = row (0..129)

Verified by shape analysis:

    proper rotations of S succeed (all 832 pieces)
    mirror chirality Z fails (all 832)
    the convention is uniquely selected by shape verification
    (exactly one of the 16 axis-orientation combinations passes)

### H.3 Decisive result

    Shirakawa's published tiling is exactly one of our 2048 tilings

    walk  = 311
    symmetry = identity
    no rotation / reflection / translation required

The tiling is not invariant under any 180° box rotation, so identity is
the unique matching symmetry.  (Improper symmetries cannot match: they
map S to Z.)

### H.4 Independent cross-check

The MacroState sequence derived **directly** from Shirakawa's 832-piece
placement data (state after slice s = packed
`slice s+1 ∩ (P_{s-1} ∪ P_s)`, `slice s+2 ∩ P_s`, where P_s = pieces
whose lowest cell lies in slice s) reproduces **walk 311 exactly** —
130 states, all distinct, all in the 478-state SCC.  This is an
independent validation of both our realization machinery and the
correspondence.

---

## I. Scope / caveat

- **2048 is exact for the 30,000,015-state Macro closure.**  It is NOT
  claimed to be the globally proven number of all 4×8×130 tilings.
- The closure was capped at 30M states, and the recurrent SCC grew from
  226 states (15M closure) to 478 states (30M closure).  A larger
  closure could in principle reveal additional Macro walks/tilings.
- Shirakawa's source page makes **no uniqueness claim**.
- The 2048 count is exact for the data we have; the global tiling count
  remains open.

---

## Artifacts

All result artifacts are retained in `results/` (see `README.md` for
the file list and how to reproduce every number in this document).
The 30M checkpoint (~943 MB) is NOT in Git; see `checkpoint.md` for its
location, exact format, and checksums.
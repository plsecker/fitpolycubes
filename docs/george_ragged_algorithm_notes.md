# George's ragged algorithm — repository reference notes

Scope: locate every reference in this repository to the five terms
(ragged configurations, diagonal planes, end configurations, solid
diagonal, finite-state automaton), quote the exact local wording, and
identify which existing solver concept each reference corresponds to.
No interpretation beyond the quoted text is offered.

Searched: `experiments/frontier/archive/`, `solvers/`, `docs/`,
`shirakawa/`, `ksystem.pdf`.

Preliminary note on "George": every "George" hit in this repository is
an attribution to George Sicherman for pentacube nomenclature or tiling
results (e.g. `docs/pieces/J.md`, `docs/pieces/S.md`, `docs/pieces/M.md`,
`docs/pieces/G.md`, `catalogues/s_catalogue.py`). No George-authored
algorithm text exists in the repo. `ksystem.pdf` is Michael Reid,
"Klarner Systems and Tiling Boxes with Polyominoes", J. Combin. Theory
Ser. A 111 (2005) 89–105; it contains none of the five terms.
`shirakawa/` transcriptions contain none of the five terms either.

---

## 1. "ragged" / ragged configurations

| File:line | Exact wording | Corresponding solver concept |
|---|---|---|
| `experiments/frontier/archive/s_frontier_ragged.py:3` | "Ragged-frontier / diagonal-sweep prototype for the S pentacube" | Ragged-frontier prototype; frontier swept diagonal by diagonal |
| `s_frontier_ragged.py:23-24` | "The current diagonal's mask may already contain cells beyond the cursor: those are the "ragged" part of the frontier." | Definition of the ragged part: occupied cells beyond the cursor in the current diagonal |
| `s_frontier_ragged.py:251` | "Advance the ragged cursor over already-occupied cells." | Cursor advance over occupied cells |
| `s_frontier_ragged.py:457` | "Interior ragged states: " | Interior state count report |
| `s_frontier_ragged.py:491` | "Ragged diagonal-frontier automaton " | Automaton experiment name |
| `s_frontier_ragged.py:554` | "Starting ragged-frontier exploration " | Run banner |
| `s_frontier_ragged.py:559` | "automaton.run()" | Automaton runner |
| `s_frontier_ragged_v2.py:3` | "Corrected ragged-frontier prototype for the S pentacube in a 4x8 prism." | Corrected ragged-frontier prototype |
| `s_frontier_ragged_v2.py:279` | "Advance the ragged cursor through occupied cells." | Cursor advance |
| `s_frontier_ragged_v2.py:444` | "# plane, preserving the ragged boundary." | Ragged boundary preserved across plane shift |
| `s_frontier_ragged_v2.py:572` | "Starting corrected ragged-frontier exploration..." | Run banner |
| `s_frontier_ragged_fixed.py:3` | "Ragged diagonal-frontier automaton prototype for S in a 4x8 prism." | Ragged automaton prototype |
| `s_frontier_ragged_fixed.py:8-9` | "Absolute diagonal/z is NOT stored: this is intended to model the translation-invariant interior." | Translation-invariant interior state |
| `s_ragged_profile.py:3` | "Ragged profile / finite-state prototype for S in 4x8." | Ragged profile prototype |
| `s_ragged_profile.py:15-16` | "Thus a flat z-frontier corresponds to a ragged surface when viewed in planes perpendicular to (1,1,1).  This is the "ragged configuration"" | The ragged configuration as a flat z-frontier seen in (1,1,1)-perpendicular planes |
| `s_ragged_profile.py:395` | "Discover the normalized ragged profile automaton " | Normalized ragged profile automaton |
| `s_ragged_profile.py:531` | "\nExample ragged state:" | Example state printout |
| `s_ragged_profile2.py:3` | "Profile the normalized ragged frontier automaton for S in 4x8." | Normalized ragged frontier automaton |
| `s_frontier_profile.py:3` | "Interior ragged-profile automaton for S in a 4x8 prism." | Interior ragged-profile automaton |
| `s_frontier_profile.py:98` | "The placement can be used as a transition from a ragged frontier only" | Placement-as-transition condition |
| `s_frontier_profile.py:144` | "translations into unique ragged-profile transition templates." | Transition template normalization |
| `s_frontier_profile.py:281` | "BFS over normalized ragged profiles." | BFS over normalized profiles |
| `s_frontier_profile.py:463` | "Generating S ragged-profile templates..." | Template generation banner |
| `s_diagonal_frontier_exposed.py:25` | "the same exposed ragged boundary." | Exposed ragged boundary in the finite-box diagonal DP |
| `s_interior_automaton2.py:16` | "do different histories converge to the same ragged frontier?" | Automaton question: convergence of histories to a ragged frontier |

## 2. "diagonal planes"

| File:line | Exact wording | Corresponding solver concept |
|---|---|---|
| `s_diagonal_frontier_dp.py:3` | "Finite-box diagonal sweep / frontier-DP prototype for S in 4x8xN." | Finite-box diagonal sweep DP |
| `s_diagonal_frontier_dp.py:9` | "within each diagonal plane, a fixed deterministic (u,v) order" | Deterministic per-plane cell order |
| `s_diagonal_frontier_dp.py:12-13` | "(current absolute diagonal d, cursor within diagonal d," | State: absolute diagonal + cursor |
| `s_diagonal_frontier_dp.py:16-17` | "Only the current + next four diagonal planes are retained because an S pentacube has solid-diagonal span at most 4." | 5-plane window; span bound |
| `s_diagonal_frontier_dp.py:20` | "* find the earliest unresolved cell in the current diagonal;" | Earliest-unresolved-cell rule |
| `s_diagonal_frontier_dp.py:29` | "state translationally invariant / automaton-like." | Translation-invariant state goal |
| `s_diagonal_frontier_dp.py:108-110` | "For every actual diagonal d, return:" | Per-diagonal plane geometry |
| `s_diagonal_frontier_dp.py:140` | "Within each actual diagonal plane, order cells by (u,v)." | (u,v) ordering |
| `s_diagonal_frontier_dp.py:271` | "When the current diagonal has no unresolved cells, shift one plane." | Plane shift rule |
| `s_diagonal_frontier_dp.py:638` | "Finite-box diagonal frontier DP " | Experiment name |
| `s_diagonal_frontier_exposed.py:3` | "Finite-box diagonal frontier DP for S in 4x8xN." | Finite-box diagonal frontier DP |
| `s_diagonal_frontier_exposed.py:7-8` | "the unprocessed side of the diagonal cut." | Diagonal cut / processed side |
| `s_diagonal_frontier_exposed.py:20-21` | "(current absolute diagonal d, cursor within that diagonal," | State: absolute diagonal + cursor |
| `s_diagonal_frontier_exposed.py:113` | "Deterministic order of cells within each solid-diagonal plane." | Per-plane deterministic order |
| `s_diagonal_frontier_exposed.py:162` | "Placement exceeds supported diagonal span" | Span bound error |
| `s_diagonal_frontier_exposed.py:281` | "# Current diagonal is fully resolved." | Diagonal resolution check |
| `s_diagonal_frontier_exposed.py:316` | "# On the current diagonal, bits before cursor are behind the cut." | Bits behind the cut |
| `s_frontier_ragged_v2.py:7` | "the current diagonal. Its target cell may lie on relative diagonal 0..4" | Relative diagonal range |
| `s_frontier_ragged_v2.py:13` | "and translate the signature so that the target cell is on frontier diagonal 0." | Signature normalization |
| `s_frontier_ragged_v2.py:18` | "Absolute diagonal/z is intentionally absent from the interior state." | Translation-invariant interior |
| `s_frontier_ragged_v2.py:42` | "# Current + four future diagonal planes." | 5-plane window |
| `s_frontier_ragged_v2.py:52` | "# masks[0] is the placement's minimum diagonal." | Minimum-diagonal mask |
| `s_frontier_ragged_v2.py:58` | "# Placement translated so that its target cell is on diagonal 0." | Normalization |
| `s_frontier_ragged_v2.py:119` | "frontier diagonal 0." | Frontier diagonal 0 |
| `s_frontier_ragged_v2.py:153` | "S placement exceeds supported diagonal span" | Span bound error |
| `s_frontier_ragged_v2.py:187-188` | "For every target cell in the current diagonal, generate candidates for every relative diagonal on which that cell could occur." | Candidate generation |
| `s_frontier_ragged_v2.py:281` | "When the cursor reaches the end of the current diagonal, the diagonal" | Cursor end-of-diagonal rule |
| `inspect_s_diagonal.py:3` | "Geometry inspector for an S pentacube under a solid-diagonal sweep." | Geometry inspector |
| `inspect_s_diagonal.py:40` | "def solid_diagonal_coords(" | (d,u,v) coordinate function |
| `inspect_s_diagonal.py:62` | "def group_box_by_diagonal(" | Box cells grouped by d |
| `inspect_s_diagonal.py:72` | "d, u, v = solid_diagonal_coords(x, y, z)" | Coordinate conversion |
| `inspect_s_diagonal.py:90` | "f"{len(grouped)} solid-diagonal planes\n"" | Plane count report |
| `s_frontier_interior.py:5-6` | "this models the MIDDLE of a long prism, where every diagonal cross-section is the same 4x8 set of 32 cells." | Interior diagonal cross-section |
| `s_frontier_interior.py:11-15` | "A state is five 32-bit diagonal masks: mask[0] = current frontier diagonal ... mask[4] = furthest diagonal affected by an S placement" | 5-mask state |
| `s_frontier_interior.py:18` | "diagonal and continue." | Shift rule |
| `s_frontier_interior.py:228` | "# In the infinite interior, every diagonal has all 32 cells." | Interior plane mask |
| `s_frontier_automaton.py:8` | "In the middle of a long 4x8xN prism, diagonal planes are identical." | Identical interior planes |
| `s_frontier_automaton.py:14-17` | "mask[0] = current diagonal ... mask[4] = furthest diagonal touched by an S placement" | 5-mask state |
| `s_frontier_automaton.py:19` | "When mask[0] is full, the frontier shifts by one diagonal." | Shift rule |
| `s_frontier_automaton.py:23` | "diagonal is zero; therefore it describes a possible interior transition." | Normalized signature |
| `s_interior_automaton2.py:8-11` | "the solid-diagonal cross-section becomes constant in the middle.  We identify one such stable diagonal plane, use its (u,v) cells as the fixed 2D cross-section, and represent a frontier only by the occupancy of cells in the next few diagonal planes." | Stable interior plane as fixed cross-section |
| `s_interior_automaton2.py:98` | "Find the longest run of identical diagonal-plane shapes and return" | Stable-plane detection |
| `s_interior_automaton2.py:124` | "raise RuntimeError("No diagonal plane run found")" | No-stable-plane error |
| `s_interior_automaton3.py:5-10` | "d = x+y+z ... the lattice cross-section repeats with period 3 in d, not period 1.  There are three interior plane phases." | 3-periodic plane phases |
| `s_interior_automaton3.py:14` | "represents the frontier as five consecutive phase-aware plane masks;" | Phase-aware masks |
| `s_interior_automaton3.py:15` | "keeps the phase (d mod 3) in the state;" | Phase in state |
| `inspect_diagonal_bitsets.py:12` | "For a fixed finite box, each solid-diagonal plane d has a finite set of valid (u,v) points." | Plane bitset encoding |
| `inspect_diagonal_bitsets.py:18` | "* builds the actual cross-section of every diagonal plane;" | Cross-section builder |
| `inspect_s_slices.py:125` | "Solid-diagonal span: d={min_d}..{max_d} (span {span})" | Placement span report |
| `frontier_s.py:2` | "Experimental diagonal-frontier solver for S in 4x8xN boxes." | Diagonal-frontier solver |
| `frontier_s.py:239` | "Max diagonal reached: " | Max-diagonal report |
| `frontier_s_diagnostic.py:3` | "Experimental diagonal-frontier solver for S in 4x8xN boxes." | Instrumented diagonal-frontier solver |
| `frontier_s_diagnostic.py:9` | "- current/max diagonal" | Progress instrumentation |
| `frontier_s_diagnostic.py:410` | "Max diagonal reached: " | Max-diagonal report |
| `docs/z_frontier_first_shift_geometry.md:128` | "State 1: a diagonal chain in rows 4-7 — (1,4), (2,5), (1,6), (2,7)." | Observed diagonal chain in the z-frontier first-shift states |

## 3. "end configurations"

Only one hit in the entire repository:

| File:line | Exact wording | Corresponding solver concept |
|---|---|---|
| `solvers/s_z_frontier.py:12` | "Finite-box start/end caps are not yet included." | The z-frontier automaton models only the interior; finite-box start/end caps are a known missing piece |

Related (same idea, different wording): the interior experiments state
that they deliberately exclude finite-box end effects —
`s_frontier_interior.py:5-6` ("models the MIDDLE of a long prism"),
`s_frontier_automaton.py:5` ("deliberately an INTERIOR automaton
experiment"), `s_interior_automaton2.py:6` ("This deliberately removes
the finite-box end effects."), `s_frontier_automaton.py:26-27` ("the
next stage is to connect the start/end boundary regions to this graph.").

## 4. "solid diagonal"

| File:line | Exact wording | Corresponding solver concept |
|---|---|---|
| `s_diagonal_frontier_dp.py:17` | "an S pentacube has solid-diagonal span at most 4." | Span bound justifying the 5-plane window |
| `s_diagonal_frontier_exposed.py:113` | "Deterministic order of cells within each solid-diagonal plane." | Per-plane order |
| `inspect_s_diagonal.py:3` | "Geometry inspector for an S pentacube under a solid-diagonal sweep." | Solid-diagonal sweep geometry |
| `inspect_s_diagonal.py:40` | "def solid_diagonal_coords(" | (d,u,v) = (x+y+z, x-y, y-z) |
| `inspect_s_diagonal.py:90` | "f"{len(grouped)} solid-diagonal planes\n"" | Plane count |
| `inspect_s_diagonal.py:204` | "Solid-diagonal coordinate system:\n d = x + y + z\n u = x - y\n v = y - z" | Coordinate system definition |
| `s_ragged_profile.py:11` | "Equivalently, the next unfilled solid-diagonal level is:" | Ragged profile as unfilled solid-diagonal levels |
| `s_frontier_profile.py:96` | "We normalize by the minimum solid-diagonal d=x+y+z." | Normalization by minimum d |
| `s_interior_automaton2.py:8` | "the solid-diagonal cross-section becomes constant in the middle." | Stable interior cross-section |
| `s_interior_automaton2.py:462` | "Finding stable solid-diagonal cross-section..." | Banner |
| `s_interior_automaton3.py:3` | "Interior solid-diagonal automaton for S in 4x8xN." | Interior solid-diagonal automaton |
| `inspect_diagonal_bitsets.py:3` | "Solid-diagonal slice-bitset explorer for the S pentacube in a 4x8xN box." | Slice-bitset explorer |
| `inspect_diagonal_bitsets.py:12` | "For a fixed finite box, each solid-diagonal plane d has a finite set of valid (u,v) points." | Plane bitset encoding |
| `inspect_diagonal_bitsets.py:355` | "Solid-diagonal planes: {len(shapes)}" | Plane count report |
| `inspect_s_slices.py:125` | "Solid-diagonal span: d={min_d}..{max_d} (span {span})" | Placement span report |

## 5. "finite-state" / automaton

| File:line | Exact wording | Corresponding solver concept |
|---|---|---|
| `docs/OPENWORK_FRONTIER_TASK.md:6` | "Build engineering infrastructure around the experimental S 4x8 frontier/automaton work." | Task framing: frontier/automaton work |
| `docs/OPENWORK_FRONTIER_TASK.md:30` | "Do not "fix" the automaton by inventing new geometry or state definitions." | Constraint: don't alter the automaton model |
| `solvers/s_z_frontier.py:368` | "Discover the interior z-frontier automaton for S in 4x8." | z-frontier automaton |
| `solvers/s_z_frontier.py:408` | "\nStarting z-frontier automaton..." | Run banner |
| `s_frontier_ragged.py:117` | "work for the automaton experiment; this one is easy to inspect." | Cell-order choice for the automaton experiment |
| `s_frontier_ragged.py:337` | "For the interior automaton experiment, reaching a repeated state is" | Repeated-state handling |
| `s_frontier_ragged.py:491` | "Ragged diagonal-frontier automaton " | Experiment name |
| `s_frontier_ragged.py:547` | "automaton = RaggedAutomaton(" | Automaton class |
| `s_frontier_ragged.py:559` | "automaton.run()" | Runner |
| `s_frontier_ragged_v2.py:576` | "automaton = RaggedAutomaton(" | Automaton class |
| `s_frontier_ragged_fixed.py:3` | "Ragged diagonal-frontier automaton prototype for S in a 4x8 prism." | Ragged automaton prototype |
| `s_frontier_ragged_fixed.py:552` | "automaton = RaggedAutomaton(" | Automaton class |
| `s_frontier_interior.py:3` | "Interior finite-state experiment for the S pentacube in a 4x8 prism." | Interior finite-state experiment |
| `s_frontier_interior.py:9` | "That is the translationally invariant automaton idea we want to test." | Translationally invariant automaton idea |
| `s_frontier_automaton.py:3` | "Discover the finite-state frontier automaton for S in a 4x8 prism." | Finite-state frontier automaton |
| `s_frontier_automaton.py:5` | "This is deliberately an INTERIOR automaton experiment." | Interior-only scope |
| `s_frontier_automaton.py:9-10` | "Translating a frontier one diagonal along z should not create a new state." | Translation invariance |
| `s_frontier_automaton.py:364` | "Discover the interior frontier automaton " | Banner |
| `s_ragged_profile.py:3` | "Ragged profile / finite-state prototype for S in 4x8." | Ragged profile finite-state prototype |
| `s_ragged_profile.py:24` | "the finite automaton state; the amount subtracted is the transition's" | Finite automaton state / transition normalization |
| `s_ragged_profile.py:27` | "This is an INTERIOR automaton experiment.  Absolute N is not part of the" | Interior scope; no absolute N |
| `s_ragged_profile.py:306` | "Discover the reachable normalized profile automaton." | Reachable normalized profile automaton |
| `s_ragged_profile.py:395` | "Discover the normalized ragged profile automaton " | Banner |
| `s_ragged_profile2.py:3` | "Profile the normalized ragged frontier automaton for S in 4x8." | Normalized ragged frontier automaton |
| `s_ragged_profile2.py:9` | "It also measures the OUT-DEGREE of each state.  A real automaton should" | Out-degree measurement |
| `s_ragged_profile2.py:438` | "\nDiscovering automaton..." | Banner |
| `s_frontier_profile.py:3` | "Interior ragged-profile automaton for S in a 4x8 prism." | Interior ragged-profile automaton |
| `s_frontier_profile.py:21` | "That gives us an actual finite-state automaton candidate." | Finite-state automaton candidate |
| `s_frontier_profile.py:281-283` | "BFS over normalized ragged profiles. ... This is the actual automaton discovery experiment." | Automaton discovery experiment |
| `s_frontier_profile.py:440` | "Discover the interior ragged-profile automaton " | Banner |
| `s_frontier_profile.py:497` | "\nStarting normalized ragged-profile BFS..." | Banner |
| `s_interior_automaton2.py:3` | "Discover the translation-invariant INTERIOR frontier automaton for S in" | Translation-invariant interior automaton |
| `s_interior_automaton2.py:15` | "The purpose is to answer the automaton question:" | Automaton question |
| `s_interior_automaton2.py:16-17` | "do different histories converge to the same ragged frontier? do those states contain cycles/SCCs?" | Convergence / SCC question |
| `s_interior_automaton3.py:3` | "Interior solid-diagonal automaton for S in 4x8xN." | Interior solid-diagonal automaton |
| `s_interior_automaton3.py:16-17` | "explores the translation-invariant interior graph; reports branching and SCC structure." | Interior graph exploration |
| `s_interior_automaton3.py:19` | "It is still an automaton experiment, not the finite-box solver." | Scope statement |
| `s_interior_automaton3.py:521` | "Starting 3-phase interior automaton " | Banner |

---

## Summary

- **Ragged configurations**: the frontier is not flat; cells beyond the
  cursor in the current diagonal are the "ragged" part
  (`s_frontier_ragged.py:23-24`), and a flat z-frontier appears as a
  ragged surface in (1,1,1)-perpendicular planes
  (`s_ragged_profile.py:15-16`). Implemented in the ragged-frontier
  prototypes and ragged-profile automata.
- **Diagonal planes**: the sweep direction d = x+y+z with per-plane
  (u,v) cell order; implemented in the diagonal-frontier DPs
  (`s_diagonal_frontier_dp.py`, `s_diagonal_frontier_exposed.py`) and
  the interior 5-mask automata.
- **End configurations**: mentioned exactly once
  (`solvers/s_z_frontier.py:12`); the interior experiments deliberately
  exclude finite-box start/end caps.
- **Solid diagonal**: the (d,u,v) coordinate system and the span bound
  "solid-diagonal span at most 4" (`s_diagonal_frontier_dp.py:17`).
- **Finite-state automaton**: the translation-invariant interior
  automaton experiments (ragged-profile, z-frontier, diagonal,
  solid-diagonal variants) plus the infrastructure constraint in
  `docs/OPENWORK_FRONTIER_TASK.md`.
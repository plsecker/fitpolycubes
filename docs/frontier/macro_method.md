# The Frontier Macro Method: how the S 4x8x20 result was obtained

Date: 2026-08-18
Status: analysis/documentation of the existing macro-analysis pipeline (no
solver changes; the S 4x8x20 result is treated as established).

This document reconstructs, from the actual scripts and documents, exactly
how the macro analysis was performed and how it produced the S 4x8x20
result.  All numbers are quoted from the scripts' own output files and the
documented runs.

## 1. Terminology (reconciled from code and docs)

| Term | Meaning (as used in the code) |
|---|---|
| low-level frontier state | one Python int, three 32-bit layer masks: bits 0–31 = layer 0, 32–63 = layer 1, 64–95 = layer 2; bit `x + 4y` of a mask = cell (x, y), x ∈ [0,4), y ∈ [0,8). Layer 3 is never reached by S templates and is not stored (`solvers/s_z_frontier_packed.py`). |
| pre-shift state | a state with `layer0 == WORD_MASK` (0xffffffff): the current layer is completely filled. |
| shift | `shift_state(s) = s >> 32`: drop the completed layer 0, re-index layers 1, 2 as 0, 1. |
| post-shift state | the state immediately after a shift; **this is what a macro state is**. |
| first generation | the placement tree from the empty state 0 up to each path's first shift; its leaves are the first-generation sources (distinct post-shift states). |
| macro edge `u -> v` | from post-shift state `u`: apply S placements at `first_empty(layer0)` until layer 0 is full (pre-shift `p`), then shift: `v = p >> 32`. One macro edge = one completed layer. |
| placement interval of `u` | all states reachable from `u` by placements only (no shift), i.e. the states explored by `explore_source(u)`. |
| macro closure | all macro states reachable from the first-generation sources by macro edges. |
| capped closure | the closure truncated at the 15,000,000-state safety cap. |
| R(s) | bitmask of exact macro distances `d` such that the empty state 0 is reachable from `s` in exactly `d` macro edges. |
| basin of 0 | the states with non-empty R (can reach 0); 226 states. |

## 2. The low-level frontier model (unchanged, reused verbatim)

All four scripts import the pure functions of `solvers/s_z_frontier_packed.py`
(`build_templates`, `apply_template`, `first_empty`, `layer_mask`,
`shift_state`, `WORD_MASK`) and never modify the solver or run its
`discover` loop.

- Templates: `build_templates()` generates all concrete S placements in the
  4x8x20 box (`generate_placements(PENTACUBES["S"], (4, 8, 20),
  break_symmetry=False)`): **3,944 concrete placements**, collapsed to
  **488 target templates** keyed by anchor cell (the cell that must be the
  `first_empty` cell of layer 0).  Each template is a packed 96-bit
  occupancy with its anchor occurrence on layer 0.
- Transition: at a non-pre-shift state, the anchor is
  `first_empty(layer0)`; every `templates[anchor]` is tried;
  `apply_template(state, t) = state | t` if disjoint, else None.
- The transition is deterministic given the state (first-empty cell +
  template order), so the set of successors is a function of the state
  alone.

## 3. What defines a macro state, and why the compression is valid

A macro state is **not** merely a deduplicated low-level state.  It is the
**post-shift projection** of a low-level state: the 96-bit window content
after the completed layer has been dropped by the shift (`state >> 32`).
The completed layer (layer 0 of the pre-shift state) is full and sealed —
no future placement can touch it, because placements only ever add cells
inside the current 3-layer window and the window only advances in z (the
sealed-layer invariant of `docs/frontier/z_direction/`).  The future
evolution of a partial tiling therefore depends only on the current window
content, i.e. on the post-shift state; the history of how the layer was
filled is irrelevant.

Consequences, all used by the pipeline:

- All low-level states that share the same post-shift projection have
  identical futures; the macro graph is the quotient of the low-level
  graph that keeps only the layer-boundary (post-shift) states.
- Each macro edge `u -> v` collapses an entire placement interval into a
  single edge; the intermediate states are discarded after the successors
  are computed.
- The macro graph is a DAG (verified by Kahn's algorithm on the capped
  closure: all 15,000,991 nodes visited, `is_dag=True`).

## 4. The pipeline: four scripts

All four scripts live in `/tmp/opencode/` (analysis artifacts, not part of
the repo), hard-code `REPO_ROOT = /home/philip/Work/fitpolycubes`, and
write machine-readable results to `/tmp/opencode/*_results.txt`.

### 4.1 `macro_reachability.py` — tileability (N = 1..20)

- **Input**: nothing but the solver's pure functions (templates built from
  scratch).
- **Strategy**: (1) first generation from 0; (2) macro closure BFS from the
  sources; (3) Kahn DAG check; (4) longest-path DP; (5) layer-BFS over the
  closure for distances 0..20 to answer "is 0 reachable in exactly N-1
  macro edges?".
- **Stopping conditions / caps** (reported if hit):
  - `MAX_FIRSTGEN_STATES = 5,000,000` (first-gen tree) — **not hit**;
  - `MAX_INTERMEDIATE = 1,000,000` (per-source interval) — hit for 0's
    interval (3,162,387 states), truncating `succ[0]`;
  - `MAX_CLOSURE_STATES = 15,000,000` (macro closure) — **hit**.
- **Results** (`/tmp/opencode/macro_reachability_results.txt`):
  - first-gen: 3,162,387 tree states, 331,765 sources, 4.2 s;
  - closure: 15,000,991 macro states, 14,781,970 macro edges,
    374,388,610 total intermediate states, 668.0 s, max BFS distance 85,
    `complete_through_19=True` (the closure BFS processes nodes in
    non-decreasing distance order, so the distance-≤19 subgraph is
    complete even though the cap was hit);
  - Kahn: `is_dag=True`, 48.4 s; longest path 94 edges, 8 endpoints,
    1 source (`6163195513375031274`);
  - tiling table N = 1..20: `zero_distances=[19]`, so **N = 20 is the only
    tileable height** (`tiling_N20=True (div=True, reach=True)`; N = 5,
    10, 15 pass the cell-count check 32N/5 but are not reachable).
- **Role**: establishes **where tileability was established** — 4x8x20 is
  tileable (and every other N ≤ 20 is not) at the macro level.

### 4.2 `macro_length_analysis.py` — exact reachable lengths and the N=20 path

- **Input**: recomputes the same capped closure (first generation +
  `macro_closure` + Kahn) — it does not read stored results.
- **Strategy**: backward DP over the Kahn reverse order:
  `R(u) = { d+1 : d in R(v), v in succ(u) }`, `R(0) = {0}`; then
  reachable N from the sources; then `reconstruct_path(s, d, succ, R)`
  for the shortest N=20 path and `firstgen_path_to_source(s20)` for the
  first-generation segment.
- **Completeness limit**: `COMPLETENESS_D = 85` — any path of length ≤ 85
  from a first-gen source stays within distance-≤84 states, all fully
  processed, so R(s) is exact for d ≤ 85 (N ≤ 86).
- **Results** (`/tmp/opencode/macro_length_analysis_results.txt`):
  - firstgen 5.6 s; closure 648.2 s; Kahn 77.0 s; backward DP 4.7 s;
  - `reachable_d_exact=[19, 39, 59]` → `reachable_N=[20, 40, 60]`;
    `r0=[0]` (the 20-cycle through 0 is not visible: `succ[0]` is
    truncated by the per-source intermediate cap);
  - basin of 0: 226 states, `R_size_distribution={1: 226}` (every basin
    state reaches 0 at exactly one distance), max remaining distance 59;
  - only 4 of 331,765 sources reach 0:
    `6163195513375031274` (d=19), `17293950180903112719` (39),
    `17306770486483095567` (39), `17293822637554016271` (59);
  - `n20_source=6163195513375031274`, `n20_path` = the 20 post-shift
    states (steps 0..19, ending `4294967295` (WORD_MASK) then 0),
    `n20_p0=0x558811aa57ffffeaffffffff`, `n20_firstgen_placements=14`;
  - terminal structure: exactly one state has an edge to 0 — WORD_MASK
    (immediate shift), so the final pre-shift state is unique for every
    reachable length; N=40 and N=60 paths are non-decomposing (no
    intermediate visit to 0).
- **Role**: establishes **where the 20-layer path was established** — the
  N=20 chain `0 -> [14 placements] -> p0 -> s* -> (19 macro edges) -> 0`,
  with the unique source and the exact post-shift/pre-shift state list.

### 4.3 `extract_20layer_path.py` — the actual 128 placements

- **Input**: `PATH_STATES` (the 20 post-shift states, hard-coded verbatim
  from the length-analysis doc) and `P0` (hard-coded).
- **Strategy**: reconstruction only, no new exhaustive search.  For each
  edge `u -> v`, the unique pre-shift state is
  `p = WORD_MASK | (L0(v) << 32) | (L1(v) << 64)` (identity
  `p >> 32 == v`); `placements_to_state(u, p, templates)` runs a targeted
  BFS confined to that layer's placement interval (at most ~40K states)
  and returns the first placement sequence reaching `p`.  Layer 1:
  `placements_to_state(0, P0)`.
- **Verification**: every segment re-simulated with the solver's own
  `apply_template` (never None), `p >> 32 == v` for all 19 macro edges,
  and the full chain `0 -> ... -> 0` simulated end to end returns exactly
  0: `ALL CHECKS PASSED: True`.
- **Results** (`/tmp/opencode/s_4x8x20_frontier_cycle_full.txt` +
  `s_4x8x20_frontier_cycle_results.txt`): `total_placements=128`,
  `firstgen_placements=14`, per-layer counts
  `14, 4, 4, 8, 8, 6, 4, 6, 8, 6, 8, 6, 6, 6, 8, 4, 6, 8, 8, 0`
  (layer 20 is an immediate shift, zero placements), `final_state=0`.
  The 128 placements in ordinary (x, y, z) coordinates are the verified
  tiling of `docs/frontier/s_piece/4x8x20_tiling_certificate.md`
  (640 distinct cubes, full 4x8x20 coverage, PASS).
- **Role**: establishes **where the actual 128 placements were
  extracted** — the tiling itself, from the macro path, by targeted
  per-layer search.

### 4.4 `macro_exclusion_test.py` — macro-path uniqueness (E0, E1)

- **Input**: hard-coded `S_STAR = 6163195513375031274`,
  `E1_U = 13835058072323104239`, `E1_V = 3993075831`; recomputes the
  first generation (asserts `not fg_hit`, `S_STAR in sources`) and the
  capped closure (712.7 s) + Kahn (62.3 s).
- **Strategy**: `backward_dp(order, succ, skip_edges)` with edge
  deletions; E0 removes `s*` from the allowed starting sources (the
  first-gen edge `0 -> s*` is forbidden); E1 removes the macro edge
  `(E1_U, E1_V)`.  `count_macro_paths` counts distinct 19-edge macro
  walks `s -> 0` by an edge-exact DP restricted to the basin (≤ 226
  states).
- **Results** (`/tmp/opencode/macro_exclusion_test_results.txt`):
  - baseline: 1 surviving source (`s*`), 1 surviving macro path;
  - E0: 0 surviving sources, 0 paths;
  - E1: edge present (`e1_edge_present=True`), it is a **cut edge** for
    the whole `s* -> 0` connection (basin 226 → 224), 0 surviving
    sources, 0 paths.
- **Role**: establishes **where uniqueness was tested** — macro-path
  uniqueness (exactly one 19-edge macro walk `s* -> 0`; both exclusions
  kill every 20-layer macro path).  Placement-level uniqueness was
  completed separately by `/tmp/opencode/macro_edge_realizations.py`
  (all 20 edge counts = 1, product = 1), documented in
  `docs/frontier/s_piece/4x8x20_macro_edge_realizations.md`.

## 5. How the 4x8x20 result flows through the pipeline

```
low-level frontier states (96-bit, 3 layer masks)
   |  first generation: placement tree from 0, stop at first shift
   v
331,765 first-generation sources (post-shift states)
   |  macro closure: fill layer + shift, to closure (capped 15M)
   v
macro graph: 15,000,991 nodes / 14,781,970 edges, DAG
   |  backward DP R(s) over Kahn order (exact for d <= 85)
   v
reachability: 0 reachable at distance 19 from exactly one source
   |  reconstruct_path + firstgen_path_to_source
   v
N=20 chain: 0 -> [14 placements] -> p0 -> s* -> 19 macro edges -> 0
   |  targeted per-layer BFS (extract_20layer_path.py)
   v
128 placements = the verified 4x8x20 tiling (certificate PASS)
   |  exclusion tests (E0, E1) + per-edge realization counts
   v
uniqueness: 1 macro path, 1 placement realization per edge -> unique tiling
```

Provenance summary:

| Result | Established by | Evidence |
|---|---|---|
| 4x8x20 tileable (only N ≤ 20) | `macro_reachability.py` | `zero_distances=[19]`, `tiling_N20=True` |
| 20-layer path (states + p0) | `macro_length_analysis.py` | `n20_path`, `n20_p0`, `n20_firstgen_placements=14` |
| 128 placements (the tiling) | `extract_20layer_path.py` | `total_placements=128`, `all_checks_passed=True`; certificate PASS |
| macro-path uniqueness | `macro_exclusion_test.py` | baseline 1 path; E0/E1 → 0 |
| tiling uniqueness | `macro_edge_realizations.py` | 20 edge counts = 1, product = 1 |

## 6. Relationship between the three levels of search

- **Low-level exhaustive Frontier state graph** (`discover` in
  `s_z_frontier_packed.py`): all states reachable from 0 by placements and
  shifts.  It is enormous: the 5M-state run (`/tmp/opencode/frontier_5m.log`)
  reached 5,000,001 states with 324,466 layer shifts and 49,247,845
  transitions generated in 62 s (393 MB peak RSS), and the exhaustive
  run currently in progress (`solvers/s_z_frontier_compact_pure.py
  --exhaustive --resume`, checkpoint dir `frontier_compact_pure_80m`,
  80M-state cap) is still running — the low-level space exceeds 80M
  states.
- **Macro graph**: nodes = post-shift states only; edges = one completed
  layer each.  Building it explored 374,388,610 intermediate states in
  total but retained only 15,000,991 macro states (≈25x compression), and
  the graph is complete through distance 19 — exactly the region the
  4x8x20 question lives in — despite the cap.
- **Targeted per-layer search**: for a fixed macro edge `u -> v`, a BFS
  confined to `u`'s placement interval (tens of thousands of states per
  layer).  Used by `extract_20layer_path.py` to recover the actual
  placements and by `macro_edge_realizations.py` to count all placement
  sequences per edge.

## 7. Memory behaviour (distinguishing the four categories)

- **Actual OOM / MemoryError / SIGKILL events**: none.  No such record
  exists in any script, log, or results file.
- **Deliberate state caps** (all reported, all runs completed):
  - `MAX_FIRSTGEN_STATES = 5,000,000` — not hit (3,162,387 states);
  - `MAX_INTERMEDIATE = 1,000,000` per source — hit for 0's interval
    (3,162,387 states), which truncates `succ[0]` and hides the 20-cycle
    through 0 (N = 80, 100, … not visible);
  - `MAX_CLOSURE_STATES = 15,000,000` — hit at 15,000,991 states in every
    closure run (668.0 s / 648.2 s / 712.7 s).
- **Estimated memory requirements**: the closure construction is the
  expensive step — `docs/frontier/s_piece/4x8x20_uniqueness_plan.md`
  estimates "≈ 11 min, ≈ 11 GB — the expensive step" on the 11 GB RAM
  machine; `docs/frontier/shared/s_z_frontier_macro_reachability.md`
  states the full uncapped closure was "not computed (memory/time
  infeasible on this machine: 11 GB RAM)".  The cap exists precisely
  because the full closure would exceed memory/time.
- **Successful completed runs**: all four scripts completed and wrote
  their results files; the verdicts are exact because they live at
  distance ≤ 19, where the capped closure is complete (max BFS distance
  85 ≥ 20).

## 8. Why the macro method was dramatically more effective

The 4x8x20 question is: "does some first-generation source reach the empty
state 0 in exactly 19 macro edges?"  In the low-level graph this is a
depth-20-layers reachability question, and the low-level space grows
enormously with depth: 5M states had completed only ~324K layer shifts,
and the exhaustive run is still growing past 80M states.  The macro graph
collapses each layer into a single edge, turning the question into
reachability in a 15M-node DAG — computed in ~11 minutes, exactly for
distance ≤ 19.  The per-layer targeted search then recovers the actual
placements at a cost of tens of thousands of states per layer, and the
basin-based DP makes the uniqueness tests cheap (226 states).  The
compression is valid because the completed layer is sealed: the future
depends only on the post-shift window, not on how the layer was filled.

## 9. Hard-coded assumptions and dimensions

- Box: 4 (x) × 8 (y) × 20 (z) — `X_SIZE = 4`, `Y_SIZE = 8` in
  `s_z_frontier_packed.py`; templates generated in the 4x8x20 box.
- `extract_20layer_path.py`: `PATH_STATES` (20 states) and `P0` hard-coded
  from the length-analysis doc.
- `macro_exclusion_test.py`: `S_STAR`, `E1_U`, `E1_V` hard-coded from the
  verified path.
- `macro_length_analysis.py`: `COMPLETENESS_D = 85`.
- All scripts: `REPO_ROOT = /home/philip/Work/fitpolycubes`, results in
  `/tmp/opencode/`.
- Precursor: `macro_graph.py` built the macro graph from the 2,451
  post-shift states of the 1M-state solver run (31,113 closure states,
  28,927 edges, no nontrivial SCCs, 9.7 s) — superseded by the
  empty-state analysis of `macro_reachability.py` (331,765 sources).

## 10. Caveats (as documented)

- The macro state/edge counts are lower bounds (closure cap hit).
- `succ[0]` is truncated (per-source intermediate cap), hiding through-0
  cycles; the 20-layer question is unaffected (complete first-gen edge
  set + macro edges at distance ≤ 19).
- R(s) is exact for d ≤ 85 (N ≤ 86); no partial (d > 85) reachable
  lengths were found.
- The exclusion test counts macro paths, not tilings; placement-level
  uniqueness was established separately (product of per-edge counts = 1).

## 11. Orientation Selection

The Macro technique can be applied with any of the three box dimensions
as the longitudinal (thickness) direction. The choice dramatically
affects the state-space size.

**Heuristic**: Choose the orientation with the smallest cross-section area.
This is an empirical rule supported by measurements on the S-pentacube
4×5×6 box, where the three orientations produced state spaces differing
by 3,000×.

See `docs/frontier/s_piece/macro_orientation_heuristic.md` for details
and `tools/frontier/macro_orientation.py` for the implementation.
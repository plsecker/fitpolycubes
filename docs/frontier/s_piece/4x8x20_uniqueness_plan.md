# S 4x8x20: Uniqueness Plan — Enumerating a Second Tiling

Scope: determine what it takes to find a *second* distinct 4x8x20 tiling
with the current frontier representation
(`solvers/s_z_frontier_packed.py`), and how the search can be forced to
avoid the verified tiling of `docs/s_4x8x20_tiling_certificate.md`.

Constraints honored: no code is modified; no search is implemented or run;
all claims below rest on the already-verified analyses
(`docs/s_z_frontier_macro_reachability.md`,
`docs/s_z_frontier_length_analysis.md`, and the stored results in
`/tmp/opencode/macro_*_results.txt`).

## 1. Where choices occur in the frontier representation

The representation is a layered decision tree:

* **Atomic decision.** In a state whose layer-0 mask is not full, the
  anchor is forced — `first_empty(layer0)` — and the choice is which
  template from `templates[anchor]` is applied (`build_templates` yields
  488 target templates; observed branching up to 11 alternatives per
  state, most states fewer).
* **Layer fill.** Repeated choices fill layer 0; when `layer0 ==
  WORD_MASK` the shift `state >> 32` is **forced** (no choice).
* **A tiling is one leaf of this tree**: 128 atomic choices forming a
  20-layer closed walk `0 -> source -> … -> 0`.

The verified tiling's 128 choices, grouped by layer:

| Layer | Placements | Layer | Placements | Layer | Placements |
|---|---|---|---|---|---|
| 1 (first gen) | 14 | 7 | 4 | 13 | 6 |
| 2 | 4 | 8 | 6 | 14 | 6 |
| 3 | 4 | 9 | 8 | 15 | 8 |
| 4 | 8 | 10 | 6 | 16 | 4 |
| 5 | 8 | 11 | 8 | 17 | 6 |
| 6 | 6 | 12 | 6 | 18 | 8 |
| | | 19 | 8 | 20 (forced shift) | 0 |

Each placement is recorded in the certificate as its anchor (the
first-empty cell) plus 5 cells; the anchor+template pair uniquely
identifies the decision.  Example decision point: layer 2, step 1, anchor
`(0,0)`, cells `(0,0,0)(0,1,0)(0,0,1)(0,0,2)(1,0,2)` (relative coords).

## 2. What is structurally forced (cannot vary)

Three exact facts (from the stored analyses; exact because every relevant
state lies at BFS distance ≤ 19 from the source set, and the closure is
complete through distance 19, max 85):

1. **The first-generation source is unique.** Any 4x8x20 tiling begins
   `0 -> (14 placements) -> p0 -> shift -> s*` with
   `s* = 6163195513375031274`; it is the **only** one of the 331,765
   first-gen sources (first-gen tree complete: 3,162,387 states, no cap
   hit) reaching `0` in exactly 19 macro edges.  The search therefore
   **cannot avoid the tiling by choosing a different source** — there is
   none.
2. **The final edge is unique.** Every path to `0` ends with
   `WORD_MASK -> 0` (the only in-edge of `0`; `WORD_MASK` the only state
   with an edge to `0`).
3. **Macro-edge targets are determined by their post-shift state.** For a
   macro edge `u -> v`, the pre-shift state is uniquely
   `p = WORD_MASK | (L0(v) << 32) | (L1(v) << 64)`; only the placement
   *path* within a layer is free, not the layer's final occupancy.

Additionally the basin of `0` is tiny (226 states, all with `|R(s)| = 1`:
every basin state reaches `0` at exactly one remaining distance), so
"second tiling" freedom cannot come from distance choices.

**Corollary.** A second distinct tiling can differ from the verified one
only in exactly two ways:

* **(A) a different macro walk** `s* -> … -> 0` of 19 edges (a different
  sequence of post-shift states), or
* **(B) a different placement-level realization of the same macro walk**
  (same post-shift states; a different atomic choice inside one or more
  layers, e.g. different template at the same anchor, ending at the same
  pre-shift `p(v)`).

## 3. How to force the search to avoid the verified tiling

Because fact 1 pins the source, *excluding any single decision of the
verified tiling eliminates it entirely*; the re-run then answers whether
any other tiling survives.  Three granularities:

| # | Exclusion | Meaning | Effect |
|---|---|---|---|
| E0 | first-gen segment `0 -> s*` (equivalently: forbid `p0`) | drop all paths `0 -> p0` | kills verified tiling; forces a different source if one existed |
| E1 | one macro edge of the walk, e.g. layer 3: `u = 13835058072323104239 -> v = 3993075831` | forbid that transition | kills verified tiling at macro level |
| E2 | one placement, e.g. layer 2 step 1, anchor `(0,0)`, cells `(0,0,0)(0,1,0)(0,0,1)(0,0,2)(1,0,2)` | forbid that atomic choice | finest-grained; forbids the exact leaf |

All three are *edge deletions* and can be applied as a forbidden-transition
set in the `apply_template` / macro-step loop.  E2 is the only one that
also rules out the verified tiling's own realization while still allowing
any alternative realization of the same macro walk (type B).

**Verdict procedure** (per exclusion): recompute `R(s)` = set of remaining
macro distances to `0` with the excluded edges removed; if no first-gen
source has `19 in R(s)`, no second tiling of that granularity exists; if
one does, enumerate the walk(s) and reconstruct as a certificate (reuse
`/tmp/opencode/reconstruct_tiling_certificate.py` for the placement-level
checks).

## 4. Required computation (not performed here)

* **(A) macro-level**: count distinct 19-edge walks `s* -> 0`.  All states
  involved lie in the 226-state basin, so this needs only the out-edges of
  the basin states: either re-materialize the capped closure (15,000,991
  nodes / 14,781,970 edges; ≈ 11 min, ≈ 11 GB — the expensive step, and
  the only one that touches the full state space) or a targeted expansion
  of the 226 basin states' intervals (cheap).  Then a path-count DP over
  the basin: exact, seconds.
* **(B) placement-level**: for each macro edge `u -> v` of the verified
  walk, enumerate **all** placement paths from `u` to the unique pre-shift
  `p(v)` — the same targeted per-layer BFS the reconstruction
  (`/tmp/opencode/extract_20layer_path.py`) already does, but kept
  complete instead of stopping at the first path.  Intervals are small
  (tens of thousands of states per layer), so this is cheap.  The number
  of type-B tilings is the product of per-edge path counts along each
  macro walk.
* **Exclusion re-runs**: patch the backward DP with edge deletions (no
  closure rebuild needed); ≈ seconds each.

Total tilings of 4x8x20 = Σ over macro walks of Π over edges of (placement
paths per edge), deduped by placement *set* (a tiling is a set of 128
placements; the deterministic fill order may realize a set in only one
way, but dedupe by set anyway for safety).

## 5. Completeness caveats

* **Per-source intermediate cap (1,000,000)**: the stored closure is exact
  for post-shift states and macro edges at BFS distance ≤ 19, which is all
  that (A) needs; but *intermediate* (non-shift) states inside a layer are
  discarded by the closure construction, so type-B counting **cannot** be
  read off the stored closure — it requires the per-layer targeted BFS of
  §4 (B).  `succ[0]` truncation only hides through-0 cycles (N = 80, 100,
  …) and does not affect the N = 20 verdict.
* **Exactness of "unique source"**: rests on the distance-≤85 completeness
  of the closure (max BFS distance 85 ≥ 20); documented and consistent
  across the capped runs.
* **Distinctness definition**: two enumeration results are distinct iff
  their placement sets differ (certificate-style).  Macro walks of type
  (A) and layer paths of type (B) that agree as sets are the same tiling.

## 6. Expected outcomes

* If (A) yields exactly 1 walk and (B) yields exactly 1 path per edge:
  the verified tiling is the **unique** 4x8x20 tiling under the frontier
  representation — the enumeration is a certificate of uniqueness, not a
  second tiling.
* Any walk/path count > 1: each combination is a distinct tiling;
  reconstruct the first alternative and certify it exactly as done for the
  verified tiling (128 placements, 640 distinct cubes, no overlaps, full
  coverage).

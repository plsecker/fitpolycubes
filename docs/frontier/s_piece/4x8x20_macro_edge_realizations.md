# Placement-level realization of the 20 macro edges: the 4x8x20 S tiling is unique

Date: 2026-08-17
Status: COMPLETE — every edge count = 1, product = 1, certificate PASS.

This document records the exhaustive enumeration of all placement-level
realizations of each of the 20 macro edges of the verified 4x8x20 frontier
cycle. It extends the macro-path uniqueness established in
`s_4x8x20_macro_uniqueness_test.md` to the placement level, and thereby
to full tiling uniqueness.

## Result

> **Every one of the 20 macro edges has exactly ONE placement-level
> realization.** The product of the 20 edge counts is **1**. The unique
> macro path therefore has exactly one placement-level realization, and
> the 4x8x20 box has exactly **one** tiling by S pentacubes (the
> 128-placement tiling recorded in `s_4x8x20_tiling_certificate.md`).

Independent verification performed at the end of the enumeration:
- the unique sequence reconstructs to exactly **128 placements**,
- covering exactly **640 distinct cubes**,
- every cube of the 4x8x20 box covered exactly once (no overlaps, no gaps),
- placement sets identical to the verified certificate doc (`PASS`).

## Three distinct uniqueness statements

| # | Statement | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Macro-path uniqueness: exactly one 19-edge walk `s* -> 0` in the macro graph | ESTABLISHED | `s_4x8x20_macro_uniqueness_test.md` (baseline: 1 surviving source, 1 macro path; E0 and E1 each reduce to 0 survivors) |
| 2 | Placement-level realization uniqueness: each macro edge has exactly one first-empty placement sequence realizing it | **ESTABLISHED HERE** | this document: all 20 edge counts = 1, exhaustive |
| 3 | Tiling uniqueness: exactly one tiling of 4x8x20 by S | **ESTABLISHED** | statements 1 + 2 + frontier completeness (below) + certificate PASS |

## Method

### Edge semantics

For edge `k` (k = 1..20) with recorded starting state `start_k`, recorded
post-shift state `target_k`, and unique pre-shift state
`p_k = WORD_MASK | L0(target_k)<<32 | L1(target_k)<<64` (identity
`p_k >> 32 == target_k` verified for all k):

- `edge 1`: `start_1 = 0` (first generation), `target_1 = s* = 6163195513375031274`, `p_1 = 0x558811aa57ffffeaffffffff` (14 placements).
- `edge k` (k = 2..20): `start_k = PATH[k-2]`, `target_k = PATH[k-1]` where `PATH` is the verified 20-step post-shift chain (last edge: `4294967295 -> 0`, immediate shift, zero placements).
- Enumeration: from `start_k`, apply every template at `first_empty(layer0)` exactly as the solver does (`apply_template`, overlap → None), continue until layer 0 is full, accept the branch only if the resulting state is EXACTLY `p_k` (i.e., post-shift == `target_k`). Count DISTINCT placement sequences (ordered template choices).
- All 20 recorded per-layer placement lists were re-simulated and verified to end exactly at `p_k` (recorded sequences valid: True for all edges).

### Completeness and pruning

- The placement graph is a DAG (each placement adds exactly 5 previously-empty
  cells; states only gain bits), so a memoized depth-first count
  (`memo[u]` = number of valid sequences from state `u`) counts every
  distinct sequence exactly once and exhausts the entire constrained
  interval. No early exit on first solution.
- Pruning is exact and complete, not a heuristic: a template whose cells
  are not all contained in `p_k` can never appear on a sequence ending at
  `p_k` (fills are monotone, cells are permanent). Pruned choices are
  simply not enumerated; every enumerated state is a subset of `p_k`.
- Safety cap `MAX_VISITED_PER_EDGE = 200,000,000` per edge (expected
  never hit; `exhaustive=True` for all 20 edges, no limit hit).
- The solver `solvers/s_z_frontier_packed.py` was NOT modified; its pure
  functions (`build_templates`, `apply_template`, `first_empty`,
  `layer_mask`, `shift_state`) are reused verbatim.
- Only the unique macro path is enumerated: no other macro paths, boxes,
  or tilings are searched.

### Product interpretation

Total number of complete first-empty placement sequences `0 -> ... -> 0`
equals the product of the 20 per-edge counts. This is valid because
macro-path uniqueness (statement 1) implies every complete sequence
passes through exactly the recorded macro states in order, decomposing
uniquely into the 20 edges. Product = `1 x 1 x ... x 1 = 1`.

### Frontier completeness (why product = 1 implies tiling uniqueness)

Every tiling `T` of the 4x8x20 box yields exactly one first-empty
placement sequence: process the cells of layer 1 in the order of
`first_empty(layer0)`; the tile of `T` covering the first empty cell is
not yet placed (placed tiles are a subset of `T`), all its cells lie in
the current 3-layer window (S pentacubes span at most 3 layers), and
placing it reproduces `T`'s restriction to the processed region. Hence
the set of all complete first-empty placement sequences is in bijection
with the set of all tilings. With exactly one such sequence, the tiling
is unique.

## Per-edge records

All times are wall-clock on the run machine (11 GB RAM; total run time
under a second). `intermediate` = distinct states visited excluding the
start state; `live` = states that lie on at least one accepted sequence.

| edge | start (post-shift) | target (post-shift) | placements | sequences | intermediate | live | exhaustive | unique == recorded |
|------|--------------------|--------------------|-----------:|----------:|-------------:|-----:|:----------:|:-------------------:|
| 1 | 0 | 6163195513375031274 | 14 | 1 | 814 | 15 | yes | yes |
| 2 | 6163195513375031274 | 13835058072323104239 | 4 | 1 | 4 | 5 | yes | yes |
| 3 | 13835058072323104239 | 3993075831 | 4 | 1 | 4 | 5 | yes | yes |
| 4 | 3993075831 | 55840897340952456 | 8 | 1 | 25 | 9 | yes | yes |
| 5 | 55840897340952456 | 9838132153049676753 | 8 | 1 | 9 | 9 | yes | yes |
| 6 | 9838132153049676753 | 2089671021646321023 | 6 | 1 | 6 | 7 | yes | yes |
| 7 | 2089671021646321023 | 13523993509333176 | 4 | 1 | 4 | 5 | yes | yes |
| 8 | 13523993509333176 | 54046496222498049 | 6 | 1 | 8 | 7 | yes | yes |
| 9 | 54046496222498049 | 3430478137537398 | 8 | 1 | 8 | 9 | yes | yes |
| 10 | 3430478137537398 | 2691607028413209 | 6 | 1 | 6 | 7 | yes | yes |
| 11 | 2691607028413209 | 4934612199136503 | 8 | 1 | 10 | 9 | yes | yes |
| 12 | 4934612199136503 | 612490719515897646 | 6 | 1 | 6 | 7 | yes | yes |
| 13 | 612490719515897646 | 16285016559841080657 | 6 | 1 | 6 | 7 | yes | yes |
| 14 | 16285016559841080657 | 217229141722890951 | 6 | 1 | 6 | 7 | yes | yes |
| 15 | 217229141722890951 | 6729013160573166 | 8 | 1 | 21 | 9 | yes | yes |
| 16 | 6729013160573166 | 2297949969 | 4 | 1 | 4 | 5 | yes | yes |
| 17 | 2297949969 | 1224979683048584328 | 6 | 1 | 6 | 7 | yes | yes |
| 18 | 1224979683048584328 | 17294878168733286543 | 8 | 1 | 9 | 9 | yes | yes |
| 19 | 17294878168733286543 | 4294967295 | 8 | 1 | 16 | 9 | yes | yes |
| 20 | 4294967295 | 0 | 0 | 1 | 0 | 1 | yes | yes |

Column meanings:
- `sequences`: number of distinct placement sequences realizing the edge.
- `intermediate`: number of distinct search states visited excluding the start state (exhaustive DFS with memoization over the placement DAG).
- `live`: number of visited states lying on at least one accepted sequence.
- `exhaustive`: enumeration completed over the entire constrained interval (no safety limit hit).
- `unique == recorded`: the unique sequence (only when count = 1) is cell-for-cell identical to the recorded placement list of the cycle extraction — i.e., the cycle's placements are THE realization, confirming the extractor found the only one.

## Final verification (product == 1 path)

The unique placement sequence per edge was back-tracked, converted to
absolute coordinates `(x, y, z_rel + k - 1)` for edge k, and checked:

- total placements: **128** (14 + 114 + 0, matching the cycle);
- distinct occupied cubes: **640** = 4 x 8 x 20;
- every cube covered exactly once (no overlaps, no gaps): **PASS**;
- placement sets identical to the certificate doc `s_4x8x20_tiling_certificate.md`: **PASS**.

## Conclusion

Combined with `s_4x8x20_macro_uniqueness_test.md`, this closes the
uniqueness question for the 4x8x20 box:

- exactly one first-generation source `s*` can reach the empty state,
- exactly one macro path `s* -> 0`,
- each of its 20 edges has exactly one placement-level realization,
- therefore exactly one first-empty placement sequence `0 -> ... -> 0`,
- therefore the 4x8x20 box has exactly **one** tiling by S pentacubes,
  namely the 128-placement tiling of the certificate.

## Reproducibility

- Script: `/tmp/opencode/macro_edge_realizations.py` (standalone; imports only `solvers/s_z_frontier_packed.py`, unmodified).
- Edge data: `/tmp/opencode/s_4x8x20_frontier_cycle_full.txt` (verified in `s_4x8x20_frontier_cycle.md`).
- Results: `/tmp/opencode/macro_edge_realizations_results.txt`; run log: `/tmp/opencode/macro_edge_realizations_run.log`.
- Command: `.venv/bin/python3 /tmp/opencode/macro_edge_realizations.py`

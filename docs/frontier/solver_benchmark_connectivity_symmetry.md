# Solver Experiment — Connectivity Pruning & Chiral-Safe Symmetry Breaking

**Date**: 2026-09-02
**Scope**: two toggleable optimisations in `solvers/solver.cpp`; baseline
preserved (flags default OFF). No catalogue/decomp semantics touched.
Numba/literature used as the correctness reference.

> **Provenance correction (2026-09-03, repo audit).** The committed HEAD
> solver (`7b1ba4c`/`b714c93`, `solvers/solver.cpp`) is the **old bare
> N-piece kernel** (`Usage: solver X Y Z`, loads `placements_N_XxYxZ.txt`)
> and **cannot run the V/W/Z benchmark cases**. All V/W/Z baselines and
> symmetry results in this report were produced by the **uncommitted
> phase-2 working-tree solver** (piece CLI, `--symmetry`, `--connectivity`,
> `--dump`, `max_nodes`), built as `/tmp/opencode/solver_new` (flags off
> for baselines) and `/tmp/opencode/solver_v2` (symmetry). See
> `docs/frontier/cpp_solver_repo_checkpoint.md` for the full
> benchmark→binary→result mapping.

## What was implemented

1. **Connectivity / component pruning** (`--connectivity[=N]`, pre-existing
   phase2 code, kept): at a search node, BFS the uncovered cells; prune if
   any connected component has size not divisible by 5. Necessary
   condition only — sound by construction. `=N` restricts the check to
   nodes with ≤ N remaining cells.
2. **Chiral-safe symmetry breaking** (`--symmetry`, rewritten in this
   session): candidate group = 48 cube symmetries, kept only if they map
   the box onto itself **and** map the piece's placement set onto itself
   (this check alone excludes reflections for chiral pieces — no chirality
   table). Canonicalisation anchor:
   - all dims odd → **centre cell**, canonicalise the placement covering
     it against the **full** preservation-checked group (every box
     symmetry fixes the centre of an all-odd box);
   - otherwise → **cell 0**, canonicalised against the subgroup that
     fixes cell 0 only.
   The previous working-tree rule (corner placements canonicalised
   against the full group) was **unsound**: sign-flip elements move cell
   0, the orbit minimum can be a non-corner image, and whole solution
   orbits could be lost. It has been replaced by the scheme above.
3. `--dump=FILE` (new): one line of placement ids per solution, used for
   exhaustive orbit-recovery verification.

Build note: this machine has no g++; binaries were built with the
user-space zig toolchain (`python-zig build-exe … -O ReleaseFast -lc
-lc++`).

## Phase 1 — baselines (uncommitted phase-2 working-tree binary, flags off)

> The baselines below were produced by the uncommitted phase-2 working-tree
> solver (`/tmp/opencode/solver_new`, flags off), **not** by the committed
> HEAD source (which is the old N-piece kernel and cannot run these cases).

| case | result | nodes | wall | nodes/s | depth |
|---|---|---|---|---|---|
| V 5×5×9 | **1,120 solutions** — matches the published exhaustive count (1,120, parity-proved) ✓ | 43,621,737 | 45.1 s | 964K | 45/45 |
| W 5×5×17 | **0 solutions** — exhaustive UNSAT confirmed | 264,277,986 | 475 s | 556K | 84/85 |
| Z 4×11×15 | 0 solutions at 200M-node cap | 200,000,073 | 581 s | 344K | 106/132 |

## Phases 2–4 — results

Node counts are exact (deterministic). Wall ratios carry ~±20 % noise
(4-core box, load average ≈ 15 during parts of the session); back-to-back
re-measurements were used for the headline numbers.

| case | baseline nodes/time | connectivity | symmetry | both | correctness |
|---|---|---|---|---|---|
| V 5×5×9 | 43,621,737 / 45.1 s | always: 43.62M / 164 s; =100: 43.62M / 150 s; =60: 43.62M / 98.7 s | **7,816,207 / 9.0 s** | 7,815,799 / 11.0 s | 1,120 → **140** solutions = full-group orbit representatives; **0/1,120 solution orbits lost** (mechanical orbit-recovery check over all baseline dumps); |G|=16, closure verified |
| W 5×5×17 | 264,277,986 / 475 s | =100: 263.94M / 710 s | **38,024,562 / 73.9 s** | 38,020,902 / 127 s | UNSAT preserved (0 sols, depth 84/85) |
| Z 4×11×15 | 200M-cap / 581 s | =130: **1 check, 0 prunes** / 543 s; =100: never fires | **no-op** (|G|=8 reflections exist, but none fixes the corner anchor; 4 is even → no centre cell; filter subgroup = {id}, 0 placements removed) | n/a | unchanged: depth 106/132 |

## Final answers

1. **Connectivity tree reduction**: 2–6 % of *nodes* carry the mod-5
   component mark (V-always 2.09M/43.6M; W=100 15.7M/264M), but the
   pruned nodes are leaf-equivalents — the baseline subtree of every
   pruned node is essentially the node itself (V: 907K pruned ≈ 3.5K
   baseline nodes of subtree). Real tree reduction ≈ **zero**. The
   min-column heuristic already detects these deaths immediately
   (min_rows = 0 at the same node).
2. **Symmetry tree reduction**: **5.6× on V** (43.6M → 7.8M), **6.9× on
   W** (264.3M → 38.0M). Solution semantics: orbit representatives
   (V: 140 = one representative per canonical-centre-placement fibre;
   the true orbit count is 70 — canonical placements with a 2-element
   stabiliser contribute 2 tilings each). For UNSAT proving the semantics
   are exactly preserved.
3. **Net wall-clock**: symmetry alone **5.0× faster on V** (45 → 9 s) and
   **6.4× faster on W** (475 → 74 s). Connectivity alone is a net **loss**
   (V: 2.2–3.6× slower; W: 1.5× slower) — the per-node flood fill costs
   more than the near-zero subtree savings. Combined = symmetry + 20–70 %
   overhead → **worse than symmetry alone** in every measured case.
4. **Correctness**: both are sound as now implemented. Connectivity:
   necessary-condition pruning, solution counts unchanged everywhere.
   Symmetry: mechanically verified — group closure checked, all 1,120 V
   solution orbits retain a representative (0 lost), UNSAT preserved on W,
   baseline node-for-node identical with flags off. The pre-existing
   corner-vs-full-group rule was unsound and was replaced before
   benchmarking.
5. **Z 4×11×15**: **no material help**. Symmetry is a no-op under a sound
   anchor scheme (the box's 8 reflections fix no corner, and the even
   dimension removes the centre cell), and connectivity never fires (1
   check / 0 prunes in 200M nodes — the tree never reaches ≤ 130
   remaining cells). Practical status unchanged: 0 solutions at 200M
   nodes, max depth 106/132.
6. **Worth pursuing**: **symmetry breaking** — it delivers 5–7× tree and
   wall reductions on symmetric-box cases at zero per-node cost. The
   high-value follow-up is a sound **centre-pair anchor** for boxes with
   an even dimension (anchor = the two middle cells of the even axis,
   canonicalised as an unordered pair), which would unlock Z-type boxes
   such as 4×11×15. **Connectivity pruning in this form should be
   dropped**: its prunes duplicate deaths the column heuristic already
   finds, and the BFS tax makes it strictly slower. (A variant that could
   still pay: checking only after placements that cut a region
   bifurcation — not evaluated here.)

## Caveats

- Wall-clock ratios measured under external load (~15 on 4 cores);
  node-count ratios are exact and deterministic.
- The symmetry solution count (140) is *orbit representatives with
  multiplicity*, not raw solutions; any downstream consumer comparing
  against raw counts must account for this (flag-gated, default off).
- No parallel-scheduling or other optimisations were touched, per scope.

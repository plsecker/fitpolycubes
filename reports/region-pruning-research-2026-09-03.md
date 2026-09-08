# Region-Feasibility Pruning Research — Overnight Report

**Date:** 2026-09-03 · **Question:** is there a cheap necessary condition that rejects the "connected but untileable" states MRV currently explores?

**Prototype status:** one new pruning mechanism implemented behind `--region-prune=propagate` (unit propagation on forced placements), **default OFF**, validated correct on every test case. Colouring prototypes (`--region-prune=colour-global`, `--region-prune=colour`) implemented, measured, and **negative** — kept behind toggles for the record.

Also fixed en route: the overnight centre/pair symmetry work in `solvers/solver.cpp` did not compile (missing `<map>`, undefined `first_key` helper, plus a latent generation-stamp width bug I introduced and caught in my own prototype — both fixed). The completed schemes were validated orbit-complete (below) and are a major win in their own right.

---

## 1. What the search actually explores (real dead-end data)

Instrumented sampler (`--research-deadends=K`) over full W 5×5×17 and V 5×5×9 runs:

| Metric (sampled MRV dead ends) | V 5×5×9 (316 samples) | W 5×5×17 (4,251 samples) |
|---|---|---|
| dead ends containing a size-%5-failing component | 34% | **74%** |
| dead ends containing a colour-failing component | **0** | **0** |
| global checkerboard test would fire | 0 | 0 |
| components per dead end | 1 (83%), 2 (16%) | 1 (64%), 2 (32%) |
| component colour imbalance | max 6, mean 1.35 | max 12, mean 2.01 |
| dead-end depth | mean 31.8 / 45 | mean 63.7 / 85 |
| small %5-ok components (≤30 cells) | rare | 13 in 4,251 samples |

**The picture:** dead ends are almost never spatially fragmented *and* colour-balanced. The typical death is a **placement-starved cell** — the region is still connected and colour-balanced, but some uncovered cell's remaining placements have all been eliminated (degree 0). MRV detects starvation at exactly the node after it happens; size-%5 failures (74% of W dead ends) coincide with the same node (last night's experiment: pruning them saved ~nothing).

## 2. Placement-feasibility tests: mathematically redundant with MRV

The lemma that closes this whole family:

> Every *active* placement has all 5 cells uncovered (rows die when any cell is covered). A piece is a connected 5-cell set, so an active placement's cells lie within a single connected component. Therefore every active placement covering a cell of component C lies **entirely** inside C, and the number of placements available inside C is exactly Σdeg(c∈C)/5. MRV already enforces deg ≥ 1 for every cell at every live node, so Σdeg ≥ |C|, i.e. **the capacity condition p_inside(C) ≥ |C|/5 holds automatically**.

This kills tests B ("some placement can enter the component"), C ("every cell has a compatible placement" — literally MRV's test), D ("placements could cover the component"), and the simple counting forms of E/F (cells↔placements Hall conditions: |N(S)| ≥ |S|/5 for all S follows from min-degree ≥ 1). The only non-redundant matching condition is full disjoint-exact-cover feasibility — NP-hard, explicitly out of scope. Verified empirically on real placement data (V/W/Z).

## 3. Colouring invariants: measured dead

Prototype: checkerboard parity, global (O(1), incrementally maintained) and per-component (fused into the connectivity BFS). Valid precondition verified on real data: every V/W/Z placement covers a 3/2 split (max |B−W| = 1), so |B−W| ≤ pieces-remaining is a valid necessary condition, per component and globally.

| Test | V 5×5×6 | V 5×5×9 | W 5×5×17 |
|---|---|---|---|
| global rejections | **0** in 366,907 nodes | 0 in samples | **1,924 in 264M nodes** (760 genuine-new = 0.0003%) |
| per-component rejections | **0** | **0** in 316 dead-end samples | **0** in 4,251 dead-end samples |
| solution counts | 144 ✓ | 1120 ✓ | 0 ✓ (exhaustive) |

**Negative result.** Connected-but-untileable states in this search are colour-balanced to within a couple of cells; their untileability is geometric (no exact cover of the specific region), not parity-based. Mod-k colourings (analyzed, not implemented): per-colour box bounds are computable from the placement list at setup, but the same sampling logic applies — the observed imbalances are far too small for any colour-deficit test to fire.

## 4. The one promising mechanism: unit propagation on forced placements

A cell with exactly one remaining placement **forces** that placement in any completion. Placing it tentatively eliminates overlapping placements, which may starve other cells (degree 0 ⇒ provably dead) or create new forced cells. Transitively propagating detects contradictions **before** MRV's own degree-0 test, without branching. This is the classic DLX+unit-propagation idea and the only mechanism whose rejection logic is *not* implied by MRV.

Implemented (`--region-prune=propagate`, default OFF; degrees collected for free inside the existing MRV scan; ~90 lines). **Debugging note worth keeping:** the first implementation was unsound due to a generation-stamp width bug (`covered` stamped in `uint8_t`, generation in `uint32_t` — silent failure past 256 runs). It was localized by replaying C++ rejection states against a faithful Python oracle; after the one-line fix the C++ agrees **node-for-node** with the oracle (V 5×5×6: 271,399 nodes in both).

**Correctness:** solution counts identical to baseline on V 5×5×6 (144), N 5×5×5 (64), V 5×5×9 (1120); W 5×5×17 still completes as an exhaustive UNSAT proof (0 solutions). Soundness argument: forced placements appear in every completion; a derived starvation is a genuine contradiction.

## 5. Results (all same-machine, H 5×5×9 background job constant throughout)

| Case | Baseline | +propagate | +symmetry (centre/pair) | +both |
|---|---|---|---|---|
| V 5×5×6 (144 raw) | 366,907 / 0.37 s | 271,399 / 0.38 s (−26% nodes) | 77,287 / 0.073 s (18 sols) | — |
| V 5×5×9 (1120 raw) | 43,621,737 / 44.5 s | 31,883,033 / 53.4 s (−27% nodes, **+20% time**) | 7,816,207 / 9.2 s (140 sols) | **5,786,044 / 9.8 s** (140 sols) |
| W 5×5×17 (UNSAT) | 264,277,986 / 441.8 s | 183,399,131 / 424.6 s (−31% nodes, **4% faster**) | **38,024,562 / 86.0 s** | **26,421,672 / 69.2 s** |
| Z 4×11×15 (300M-node cap) | 300M / 827.6 s / depth 111 | 300M / 1130.3 s / depth 108 | 300M / 951.0 s / depth 107 | 300M / 1094.4 s / depth 105 |

Propagation rejection depth histogram (W and Z): **essentially 100% in the deepest bucket** — contradictions fire just above the leaves, where forced cells multiply. That is why standalone propagation is marginal (it saves the leaf-sibling graveyard, ~1.4× nodes, ~break-even time) while **symmetry + propagation compose multiplicatively**: W 5×5×17 → **10× fewer nodes, 6.4× faster**; the exhaustive UNSAT proof drops from 441.8 s to **69.2 s**.

**Symmetry side-note (pre-existing overnight work, fixed and validated here):** the centre-cell anchor for all-odd boxes (full |G| fixes the centre, e.g. 52/60 anchor placements removed on W) and the centre-pair anchor for one-even-dim boxes (34/48 removed on Z) replace the corner scheme and are strictly stronger. Validated by dumping solutions and checking orbit-completeness against raw enumerations: V 5×5×6 18 restricted solutions cover **all 9 documented orbits**; V 5×5×9 140 cover **all 70 orbits**; restricted solutions are always raw solutions. W 5×5×17 UNSAT is preserved exhaustively (38.0M-node full-tree proof).

## 6. Frontier verdict: Z 4×11×15

**No practical status change.** Every configuration (baseline, propagate, symmetry, both) remains UNKNOWN at the 300M-node budget, max depth 105–111 / 132, zero solutions. The propagated and symmetrized searches spend their node budget differently (propagation rejects 21.6% of nodes outright) but the tree is so deep and wide that per-node pruning does not move the frontier. Propagation is also 27–37% slower per node on Z's large matrix, and its rejections concentrate where MRV was about to die anyway.

## 7. Answers

1. **What states are we exploring?** Colour-balanced, mostly-still-connected regions that die by placement starvation (a cell whose placements are all eliminated); 74% of W dead ends also contain a size-%5 fragment — detected by MRV at the same node.
2. **Can placement-feasibility detect them cheaply?** **No — provably.** All counting/Hall-style feasibility conditions are implied by MRV's per-cell degree ≥ 1 (lemma in §2); the rest is exact-cover-hard.
3. **Can colouring detect them cheaply?** **No — measured.** Zero component-colour failures across 4,567 sampled dead ends on two boxes; the regions are parity-balanced.
4. **Best rejection/overhead tradeoff?** Unit propagation: 22–31% of nodes rejected on the hard boxes at ~30% per-node overhead — net-positive only from W upward (W: −31% nodes / −4% time), and strongly positive only **in combination with symmetry**.
5. **Overlap with MRV?** Colour: total overlap where it fires at all. Propagation: rejections are genuine-new (MRV passes those nodes) but they sit one-to-few nodes above MRV deaths — the histogram proves the effect is leaf-local.
6. **Does anything materially help Z 4×11×15?** **No.** All configs remain UNKNOWN at 300M nodes with similar depth. Do not build more per-node pruning for this case.
7. **Clear next pruning mechanism?** Only the **combination** is worth keeping: symmetry (centre/pair schemes, now default-able for future runs) + unit propagation. Together: W 5×5×17 10× faster, V 5×5×9 4.5× faster, correctness validated.
8. **If not, what next?** The evidence says Z 4×11×15's difficulty is *representational*, not local: 300M-node budgets die at depth ~108/132 with astronomically wide frontiers, and every local invariant is either redundant (counting), blind (colour), or leaf-local (propagation). The next algorithmic target should be the **frontier/transfer-matrix representation** (already proven on S 4×8 and the Z-direction DP) or **SAT/certificate methods** (already proven on Z 6×6×10) for UNSAT boxes of this class — not more per-node pruning.

## Notes

- All features default OFF; flags-off behaviour verified identical to the baseline binary (V 5×5×6: 366,907/144).
- Raw outputs: `/tmp/opencode/bench/results/PR_*.out`, `RD_*.out`, `rej_paths.txt`; validation script: `/tmp/opencode/bench/validate_sym.py`.
- The H 5×5×9 enumeration (previous task) is still running in the background (22.4B nodes, 1.97M solutions at last check) and was the constant 1-core background load for all timed runs.
- Left running by design: nothing; all experiments complete. H 5×5×9 may be left to finish for the catalogue.
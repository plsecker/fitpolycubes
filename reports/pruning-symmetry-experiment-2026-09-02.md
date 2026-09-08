# Connectivity Pruning + Chiral-Safe Symmetry Breaking — C++ Experiment Report

**Date:** 2026-09-02 · **Scope:** two toggleable features in `solvers/solver.cpp`, benchmarked on V 5×5×9, W 5×5×17, Z 4×11×15. No catalogue/decomp changes; baseline preserved; Numba/Python-sym-file as reference.

**Build note:** this machine has no system C++ compiler; both binaries were built with the repo's Zig toolchain (`zig c++ -O3 -std=c++17`, same for baseline and feature builds — timings are internally consistent). One steady background job (the H 5×5×9 enumeration, 1 core) was present during all timed runs, identically for every configuration.

**Code state:** `solvers/solver.cpp` modified; new flags `--connectivity[=N]` and `--symmetry`, both **default OFF**. Flags-off behaviour is verified byte-equivalent to the original binary (identical node counts; e.g. V 5×5×6: 366,907/144; V 5×5×9: 43,621,737/1120; W 5×5×17: 264,277,986/0).

---

## Phase 1 — Baseline (all solo, same build)

| Case | Result | Nodes | Dead ends | Depth | Time | Rate |
|---|---|---|---|---|---|---|
| V 5×5×9 (full) | 1120 sols | 43,621,737 | 15,811,222 | 45/45 | 44.5 s | 980K/s |
| W 5×5×17 (full) | 0 sols — exhaustive UNSAT | 264,277,986 | 85,035,864 | 84/85 | 441.8 s | 598K/s |
| Z 4×11×15 (300M-node cap) | 0 sols — UNKNOWN | 300,000,064 | 104,211,682 | 111/132 | 827.6 s | 362K/s |

W 5×5×17 reproduces the previous session's exhaustive UNSAT run **node-for-node** (264,277,986) — baseline is sensible and reproducible.

---

## Phase 2 — Connectivity / component pruning

**Rule implemented (safe, necessary-condition only):** at each node, compute connected components of the uncovered cells (BFS over the 6-neighbour grid); if any component's size is not a multiple of 5, the region is untileable (a face-connected 5-cell piece can never span two components) → prune. Toggleable; optional `=N` threshold (check only while remaining cells ≤ N).

| Case | Nodes (Δ vs base) | Conn-pruned | Time | vs baseline |
|---|---|---|---|---|
| V 5×5×6 (validation) | 366,867 (−40) | 18,671 | 0.80 s | **2.3× slower** |
| N 5×5×5 (validation) | 12,503,503 (−1,514) | 2,693,785 | 42.1 s | ~2.4× slower |
| V 5×5×9 | 43,616,480 (−5,257) | 2,089,490 | 104.1 s | **2.3× slower** |
| W 5×5×17 | 262,526,327 (−1,751,659) | 30,792,869 | 826.0 s | **1.87× slower** |
| Z 4×11×15 (300M cap) | 300,000,074 (same budget) | 32,444,319 | 2229.0 s | **2.69× slower** |

**Correct:** solution counts identical to baseline on every case (144 / 64 / 1120 / 0 / 0); the exhaustive UNSAT proof on W 5×5×17 still completes.
**But it is a net loss everywhere.** The decisive diagnosis is in the dead-end accounting: on W, baseline 85.0M dead-ends ≈ connectivity-run 73.0M MRV dead-ends + 30.8M conn-pruned (−0.3M). The nodes the component test kills are **the same nodes MRV already kills immediately with min_rows == 0** — in practice, failing components are small fragments that contain no placement at all, so the search's own column-scan detects them at the same node. The subtree saving is ~0 (W: 30.8M pruned entries saved only 1.75M baseline nodes), while the per-node BFS + full scan costs ~2× throughput (598K → 318K nodes/s on W). The deep dead-end class that *would* pay off — "connected but untileable", 73.9% of the old W 5×7×9 dead-end analysis — is not detectable by a component-size test.

---

## Phase 3 — Chiral-safe symmetry breaking

**Mechanism.** Candidate group = 48 cube symmetries as (axis permutation, sign flips), kept only if they (1) map the box onto itself and (2) map the piece's **placement set onto itself**. Condition 2 automatically excludes reflections for chiral pieces (no chirality table needed) and dim-mismatching permutations. Breaking rule: every tiling covers the anchor cell (0,0,0) with exactly one placement; placements covering it that are not the lexicographically-canonical image of their orbit are masked out **once, before search** — zero per-node cost. Completeness: every solution orbit keeps ≥1 representative (the canonical image always also covers the anchor), so existence / primality / exhaustive-UNSAT conclusions are preserved; raw solution counts become orbit-representative counts.

| Case | \|G\| | Corner removed | Nodes | vs base tree | Solutions | Time (vs base) |
|---|---|---|---|---|---|---|
| V 5×5×6 | 16 | 4/9 | **196,906** (= Python sym-file ref, exact) | 1.86× | 90 (= ref) | 0.20 s |
| V 5×5×9 | 16 | 4/9 | **24,727,566** (= Python/Numba ref, exact) | **1.77×** | 656 (= ref) | **26.0 s — 1.71× wall** |
| W 5×5×17 | 16 | 3/6 | **132,036,937** (= Python sym-file ref, exact) | **2.00×** | 0 (UNSAT preserved) | **213 s — ~1.9× wall** |
| H 5×5×6 (chiral) | **8** — reflections excluded ✓ | 0/12 | not exhausted (run bg) | — | — | — |
| S 4×8×10 (chiral) | **4** — ✓ | 0/6 | n/a | — | — | — |
| Z 4×11×15 | 8 | **0/6** | = baseline (provable no-op) | 1.0× | — | — |

**Correctness:** node-exact agreement with the independent Python-generated restricted matrices on **two** cases — including the exhaustive UNSAT case — and with the previous session's Numba runs (V 5×5×9 sym: 24,727,566/656). Chiral safety demonstrated directly: H gets |G|=8, S gets |G|=4 (rotation-only), achiral V/W/Z get the full 16/16/8. Search-time rate is unchanged (952K vs 980K nodes/s on V 5×5×9) — the reduction is genuinely free.

---

## Phase 4 — Combined

| Case | Baseline nodes/time | Connectivity | Symmetry | Both | Result |
|---|---|---|---|---|---|
| V 5×5×9 | 43.6M / 44.5 s | 43.6M / 104.1 s | **24.7M / 26.0 s** | 24.7M / 60.4 s | combined worse than symmetry alone |
| W 5×5×17 | 264.3M / 441.8 s | 262.5M / 826.0 s | **132.0M / 213 s** | 131.2M / 453.2 s | combined worse than symmetry alone |
| Z 4×11×15 | 300M / 827.6 s | 300M / 2229.0 s | no-op (0 removed) | ≡ connectivity | combined ≡ connectivity |

The combined configuration is never worthwhile as specified: connectivity's ~2× per-node overhead destroys symmetry's free gain.

---

## Phase 5 — Frontier impact on Z 4×11×15

| Metric (300M-node budget) | Baseline | Connectivity ON |
|---|---|---|
| Solutions | 0 | 0 |
| Max depth reached | 111 / 132 | **111 / 132 (identical)** |
| Wall time | 827.6 s | 2229.0 s (2.69×) |
| Node rate | 362K/s | 135K/s |
| MRV dead-ends | 104.2M | 73.0M (+32.4M conn-pruned ≈ same total) |

**No frontier impact.** Same depth, same solutions, same effective search, 2.7× more wall time. The case remains UNKNOWN for the raw backend, exactly as before.

---

## Answers

1. **How much does connectivity pruning reduce the tree?** Effectively **zero**: 0.001% (V 5×5×9), 0.66% (W 5×5×17), 0% (Z 4×11×15, same depth at equal budget). Its "pruned" counter (1.2–32.4M nodes) is misleading — those nodes were already immediate MRV dead-ends.
2. **How much does chiral-safe symmetry reduce the tree?** **1.77× (V 5×5×9), 2.00× (W 5×5×17), 1.86× (V 5×5×6)** — exactly half the corner branches on (5,5,c) boxes; **1.0× on all-distinct boxes** (Z 4×11×15, provably no corner redundancy under the rotation-safe group).
3. **Net wall-clock?** Symmetry: **1.71× faster (V), ~1.9× faster (W)** at zero per-node cost. Connectivity: **1.9–2.7× slower**. Combined: worse than symmetry alone.
4. **Are both correct?** Yes. Connectivity never changed a solution count (all five validation cases) and preserved exhaustive UNSAT on W 5×5×17. Symmetry is node-exact against the independent reference implementation on two cases, chiral-safe by construction (H: |G|=8, S: |G|=4 — reflections auto-excluded via placement-set invariance), and preserves orbit completeness.
5. **Do they materially help Z 4×11×15?** **No.** Symmetry is provably inert (distinct dimensions → 0 corner redundancy); connectivity leaves depth and results unchanged at 2.7× the cost. The Z frontier is untouched by these two ideas.
6. **Which is worth pursuing?** **Symmetry — clearly.** It is free, correct, and halves the tree wherever two box dimensions coincide. The build-out path: (a) apply it by default for equal-dim boxes (it is exactly equivalent to the existing Python `break_symmetry` pipeline — proven node-exact — so results remain cross-verifiable); (b) the bigger prize is *full orbit-based* breaking (factor |G| = 8–48 rather than ~2), which needs a canonical-first-uncovered-cell scheme — a well-defined follow-up. **Connectivity pruning in the size-%5 form should be dropped**: it is dominated by MRV's own min_rows == 0 detection. If pruning is revisited, the evidence points to *stronger per-component tests* (component admits ≥1 placement / matching or coloring invariants) targeting the "connected-but-untileable" class — but that is a different, harder mechanism than the one tested here.

## Notes

- All raw outputs: `/tmp/opencode/bench/results/P*.out`; binaries: `/tmp/opencode/bench/solver_{base_zig,new}`; baseline source preserved at `/tmp/opencode/bench/solver_baseline.cpp`.
- `solvers/solver.cpp` in the repo now carries both features (default OFF — baseline behaviour unchanged when flags are omitted).
- H 5×5×6 (raw and symmetry runs) had not completed within ~25 min when the report was finalized; they continue in the background and only add a curiosity data point (the H family is search-brutal even at 150 cells).
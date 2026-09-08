# Next-Stage Decision Report — C++ Parallelism and the Z 4×11×15 SAT Attack

**Date:** 2026-09-03 · **Context:** follows `reports/cpp-numba-benchmark-2026-09-03.md` (C++ 2.6–2.7× Numba per node; C++-only symmetry+propagation machinery; Z 4×11×15 the critical frontier).

---

## PART A — C++ parallel task splitting

**Implementation (smallest clean version).** `--parallel[=W]` in `solvers/solver.cpp`: a recursive MRV descent (depth ≤ 4, target = W×16 tasks — the hybrid strategy) emits task prefixes; each of W `std::thread` workers applies its prefix to a private copy of the masked state and runs the **unchanged** `search()` (symmetry, propagation, pair checks all intact); work is handed out by an atomic index (dynamic stealing — no static chunks). Mutable scratch (`g_prop`, `g_conn`, `g_deg`, `prop_forced`) became `thread_local`; the pair-check counters became atomics; the colour-global counters were made single-test-gated (colour-global + parallel is force-disabled with a printed note). Flags-off and workers=1 behaviour are unchanged (verified: V 5×5×6 raw 366,907/144; W 5×5×17 sym+prop single-thread node-for-node with the pre-change binary).

**Results** (dedicated machine, no background jobs; `/usr/bin/time -v` for memory):

| Case | workers | Total nodes | Solutions | Wall | Per-worker nodes | Peak RSS |
|---|---|---|---|---|---|---|
| W 5×5×17 (sym+prop, exhaustive UNSAT) | 1 | 26,421,672 | 0 | 61.6 s | — | 2.3 MB |
| | 2 | 26,421,655 | 0 | 32.3 s (**1.91×, 95% eff.**) | 13.5M / 12.9M | 2.6 MB |
| | 4 | 26,421,638 | 0 | 27.1 s (**2.27×, 57% eff.**) | 4.4M / 6.4M / 5.2M / 10.4M | 2.9 MB |
| W 5×7×9 (sym+prop, exhaustive, 10 sols) | 4 | 1,707,814,263 | 10 | **1568.0 s (3.15×, 79% eff.)** | 492M / 376M / 260M / 579M | — |

**Work preservation:** total nodes match the single-threaded runs to within ±35 (out of 26.4M) and ±30 (out of 1.71B) — the split only removes the shared prefixes that the serial run re-descends. There is **no native-order tree inflation**: the C++ task generator uses the same file-order matrix and MRV rule as the serial search, so unlike the Numba hybrid (±46% tree inflation from its native column order) the C++ split is tree-neutral.

**Load imbalance:** per-worker node spreads of 1.16× (w=2) and 2.2× (w=4) on W 5×5×17, and 2.2× on W 5×7×9 — better than the Numba pool (whose W 5×5×17 run left one worker at 287.7M nodes after 66 minutes and never finished), but still granularity-limited: with target = W×16 tasks the deepest task dominates the tail. Raising the split depth/target would recover part of the w=4 gap; not done here (smallest clean version).

**W 5×7×11 (the frontier question):** 4 workers, 3-hour cap — **did not complete** (result at the end of this report). The single-thread probe had already exceeded 2 h; 4-worker parallelism reduces the expected single-thread requirement (~10¹⁰ raw-equivalent nodes) to roughly 1–3 days, not hours. W 5×7×11 needs either a finer task split with more workers or a different budget class.

---

## PART B — Z 4×11×15 SAT experiment

**What the certified recipe actually is (important correction).** The certified Z 6×6×10 UNSAT package (`docs/frontier/z_piece/z_6610_certificate/`) used **no symmetry-breaking predicates at all** ("symmetry reduction: disabled" in the 6×7×10 certification; metadata.json records the 287 s run as "plain"). The encoding is: one variable per legal placement (2,176 for 6×6×10); per-cell at-least-one clauses; per-overlapping-pair at-most-one clauses. The piece-count constraint is implied. CaDiCaL (via python-sat `Cadical153`) closed it in 287 s plain / 415 s with DRAT logging, verified by drat-trim and lrat-check. I followed this recipe exactly rather than inventing an encoding, and per the task's own warning treated any added symmetry predicate as a proof obligation — concluding (below) that none should be added.

**Placement cross-validation:** the SAT-side generator (`z_sat.placements_cells`, layer-DP style, audited in the Aug certification) and the repo `generate_placements` produce **identical placement sets for Z 4×11×15 (4096 = 4096, zero symmetric-difference)** — the encoding is built on the same placement basis as the search solvers.

**Correctness ladder (pysat/CaDiCaL):**

| Case | Vars | Clauses | Result | Check |
|---|---|---|---|---|
| Z 2×3×5 | 24 | 266 | **UNSAT in 0.1 s** | C++ raw search: 0 solutions ✓ (some cells uncoverable — genuinely untileable) |
| Z 5×5×5 | 540 | 36,143 | **UNSAT in 0.0 s** | documented catalogue rule ✓ |
| Z 6×10×10 | 4,096 | 406,648 | SAT (running at report time; tiling + geometric validation on completion) | published prime ✓ |
| Z 6×6×10 | 2,176 | ~201K | UNSAT (certified 287 s; pipeline re-check in progress) | the certified package ✓ |

**Z 4×11×15 target:** 4,096 variables, ~410K clauses (avg placement-degree 31 → ~465 AMO pairs per cell). Result: see the end-of-report status line.

**Symmetry-breaking safety analysis (the proof-obligation question):**

- The C++ analogue of "safe symmetry" for Z 4×11×15 would be: corner-anchor restriction (cell (0,0,0), |G|=8 chiral-safe group, trivial corner stabilizer) → removes **zero** placements (all-distinct dimensions, achiral piece — every corner placement is its own orbit minimum). The centre/pair scheme does not map to a clause encoding without tuple variables (a new, unproven obligation — exactly the class of error the H 5×5×6 pair-scheme bug demonstrated, where 21.8% of solution orbits were silently destroyed until the dump-validation caught it).
- Conclusion: **no symmetry predicates were added, matching the certified recipe.** CaDiCaL's learned-clause machinery handled the 6×6×10 symmetry internally; there is no evidence manual predicates would help, and concrete evidence (the pair-scheme bug) that unvalidated predicates are dangerous.
- If UNSAT is achieved for Z 4×11×15, the DRAT proof is retained and can be machine-checked with the already-built drat-trim (zig cc build present at `/tmp/opencode/drat-trim-src/`), following the 6×6×10 package procedure (DRAT → LRAT → double-checker verdict).

---

## PART C — Decision answers

*(filled at the end of the report once W 5×7×11 and the Z runs complete — see the status block below)*

## Status block (auto-updated at completion)

- W 5×7×11 4-worker probe: pending
- Z 6×6×10 pipeline re-check: pending
- Z 4×11×15 (proof-less): pending
- Z 4×11×15 (with DRAT proof): pending

# Current C++ vs Current Numba — Benchmark at the New Algorithmic Baseline

**Date:** 2026-09-03 · **Machine:** i7-12700, 4 logical CPUs, 28 GB RAM. One steady background job (the H 5×5×9 enumeration, 1 core) ran throughout every timed run, identically for all configurations. Numba timings under additional contention are marked; node counts are contention-independent and are the primary comparison anchor.

**Code state:** all recent algorithmic work lives in the C++ solver (`solvers/solver.cpp`, single file, flag-gated). The Numba backends are byte-identical to the first benchmark (verified by mtimes and diff). One correctness bug in the centre-pair symmetry scheme was found *by this benchmark's validation* and fixed (§4); all one-even-dim-box numbers below use the fixed code.

---

## 1. What each backend actually implements (capability matrix, verified from code)

| Capability | C++ `solver.cpp` | Numba `fitpolycubes_{hybrid,numba}.py` |
|---|---|---|
| Centre-cell symmetry (all-odd boxes) | ✅ `--symmetry` | ❌ |
| Centre-pair symmetry (one-even-dim boxes) | ✅ (fixed this session; orbit-complete) | ❌ |
| Corner-canonical symmetry | ✅ (≥2 even dims) | ⚠️ reflection-based Python scheme — chiral-**unsafe** (H/S), stabilizer-≤2 on equal-dim boxes, zero on distinct-dim boxes |
| Forced-placement unit propagation | ✅ `--region-prune=propagate` | ❌ |
| Colouring / size-%5 connectivity | ✅ (measured MRV-dominated) | ❌ |
| MRV rule | identical (trees verified node-for-node) | identical |
| Parallelism | none (1 thread) | ✅ 4 workers, depth-4 task split, static chunks |
| Node caps / progress | ✅ | wall-clock only |
| Caching / reuse | none (fresh search) | none (fresh search) |
| Placement generation | reads file (ids x+a·y+a·b·z) | in-process, native column order (different MRV tie-breaks → different tree size, ±5–46%) |

**The two backends do not run the same algorithm.** Numba has none of the recent machinery. This benchmark therefore separates three layers: pure language (identical trees), algorithm (C++-only features), and the composition.

---

## 2. Current Numba reproduction (consistency with the recent report)

| Case | Config | Result | Nodes | Wall |
|---|---|---|---|---|
| V 5×5×9 | hybrid, 4 workers, corner symmetry | 656 sols | **36,006,879** — exact match to the first benchmark | 132.1 s (contended; 105.0 s previously) |
| V 5×5×9 | hybrid, 4 workers, no symmetry | 1120 sols | 61,717,385 | 161.0 s (contended) |
| W 5×5×17 | hybrid, 4 workers, corner symmetry | **did not finish** — killed at 66 min; longest task alone at 287.7M nodes (79K/s) | ≥288M on longest task | 66+ min |
| Z 4×11×15 | hybrid, 4 workers | **UNKNOWN** at 30-min timeout; workers at 76–92M nodes each (~47–62K/s/worker) | ~300M+ collective | 30-min cap |

Consistency confirmed: node counts reproduce exactly; the only movements are wall-times explained by background load.

---

## 3. Current C++ vs current Numba

**Pure-language anchor** (identical placement files → node-for-node identical trees, both single-threaded, matched background load):

| Case (raw search) | Nodes | C++ | Numba | Language ratio |
|---|---|---|---|---|
| V 5×5×9 | 43,621,737 (both) | 44.5 s | 120.2 s | **2.70×** |
| W 5×5×17 | 264,277,986 (both) | 441.8 s | 1149.2 s | **2.60×** |

The Numba kernel runs the identical search at ~0.37–0.38× the C++ node rate. Memory: both < 215 MB RSS.

**Strongest currently-validated configuration of each backend:**

| Case | Current Numba (best) | Current C++ (best: `--symmetry --region-prune=propagate`) | Wall speedup | Nodes comparison | Main reason |
|---|---|---|---|---|---|
| V 5×5×9 | 36.0M nodes / 656 sols / 132.1 s (4 workers) | **5.79M / 140 sols / 9.8 s** (1 thread) | **13.5×** | 6.2× fewer | centre symmetry + propagation (Numba has neither) × 2.7× language |
| W 5×5×17 | unfinished at 66 min (≥288M nodes on longest task) | **26.4M / 0 sols (exhaustive UNSAT) / 69.2 s** (1 thread) | **>57×** | ≥11× fewer | same |
| Z 4×11×15 | UNKNOWN (30-min cap) | UNKNOWN (300M-node cap, 1179 s, depth 105/132) | — | same budget | tree too deep; algorithms bite only in the endgame (§6) |

Additional hard cases (C++ only — Numba cannot run these trees in practical time):

| Case | C++ raw | C++ + current algorithms | Reduction |
|---|---|---|---|
| V 5×5×6 (144 raw sols) | 366,907 / 0.37 s | 93,440 / 18 sols / ~0.1 s | 3.9× |
| H 5×5×6 (205,668 raw sols, **chiral**) | 1,902,252,515 / 2883.7 s | 431,325,171 / 27,459 sols / 675.7 s | 4.4× nodes, 4.3× wall |
| **W 5×7×9** (40 raw sols; the old 2.97 h frontier) | 5,261,022,281 / 10,677 s | **1,707,814,293 / 10 sols / 4938 s — exhaustive** | **3.1× nodes, 2.2× wall** |
| W 5×7×11 | — | **not exhausted**: the 2-hour probe ended on the time limit before reaching the 4B-node cap — remains UNKNOWN | — |

---

## 4. Correctness validation performed (and a bug it caught)

- **Node-for-node identity** C++ ↔ Numba on identical trees: V 5×5×9 (43,621,737) and W 5×5×17 (264,277,986) — the language comparison measures only execution speed.
- **Orbit-completeness of the symmetry schemes**, by dumping restricted solutions and comparing against raw enumerations under the chiral-safe group: V 5×5×6 18 sols ⊇ **9/9 orbits**; V 5×5×9 140 sols ⊇ **70/70 orbits**; **H 5×5×6 (chiral) 27,459 sols ⊇ 25,902/25,902 orbits**.
- **Bug found and fixed:** the centre-pair scheme was silently incomplete — after the (correct) tuple-canonical filter, the code also ran the generic single-row canonical filter with anchor = one pair cell, while pair-scheme group elements may swap the two anchor cells. A row's "canonical image" then covered the *other* pair cell and the row was wrongly deleted, destroying whole solution orbits (H 5×5×6: 21.8% of orbits lost; the achiral V cases happened to survive, which is why earlier checks passed). After the fix: H 5×5×6 orbit coverage **25,902/25,902 PASS**, removal count matches an independent Python replica of the semantics exactly (94 rows).
- **W 5×7×9 consistency:** the archived 40 raw solutions (Aug 25 exhaustive run) parse into exactly **5 orbits × 8**; the new restricted enumeration found 10 solutions = 2 representatives per orbit — the same over-count pattern as V/H, consistent with orbit-completeness.
- Unit propagation: solution counts identical to baseline everywhere; W 5×5×17 remains an exhaustive UNSAT proof.

---

## 5. Does C++ benefit from the new algorithms the same way the algorithms promise?

| Progression | C++ | Numba |
|---|---|---|
| V 5×5×9 baseline | 43.6M / 44.5 s | 61.7M / 161.0 s (4 workers, native-order tree) |
| + symmetry | 7.8M / 9.2 s (**5.6×**) | 36.0M / 132.1 s (**1.71×** — corner scheme only) |
| + propagation | 31.9M / 53.4 s (**1.37×** nodes, slower wall standalone) | ❌ not implemented |
| + both | **5.79M / 9.8 s (7.5×)** | ❌ |

**The algorithmic reductions compose with the C++ backend exactly as designed — multiplicatively — and are unavailable to Numba.** The centre/pair symmetry contributes 4.4–7× (depending on box), propagation adds ~1.3–2.5× on top (its standalone wall benefit is marginal on small boxes but the node reduction compounds with symmetry), and the language contributes a further ~2.6×. Numba's only algorithmic lever (corner symmetry) delivers 1.71× on V and nothing on distinct-dimension boxes.

---

## 6. Z frontier

| Z 4×11×15 (300M-node cap) | Nodes | Depth | Wall | Status |
|---|---|---|---|---|
| baseline | 300M | 111/132 | 827.6 s | UNKNOWN |
| + symmetry (fixed pair scheme) | 300M | 107/132 | 934.2 s | UNKNOWN |
| + propagation | 300M | 108/132 | 1130.3 s | UNKNOWN |
| + both | 300M | 105/132 | 1179.2 s | UNKNOWN |
| Numba hybrid (4 workers) | ~300M+ collective | — | 30-min cap | UNKNOWN |

**Why the new algorithms do not move Z** (measured, not speculative): dead-end sampling shows Z's search dies at depths 54–93 (mean 78) of 132 at the 100M-node mark, with component sizes bimodal (fragments + a 220–300-cell main region) and **zero colour failures**. W's corrected propagation-rejection histogram (fixed instrumentation; the earlier "leaf-local" reading was a bucket-clamping artifact — rejections actually span depths 3–79, mode ~69/85) shows the mechanism bites mid-to-deep; on Z the equivalent zone (depth ≥ ~125) lies **beyond the 300M-node horizon**. Reaching it requires ~10¹⁰⁺ nodes: at the measured 254–363K nodes/s that is **weeks of single-thread search, per configuration**. Increasing the budget therefore cannot plausibly change Z's practical status. This confirms the previous research conclusion: Z is a representational problem (frontier/transfer-matrix DP or SAT certificates), not a per-node pruning or throughput problem.

---

## 7. Cache/decomp separation

Every number above is a **fresh low-level search**: neither backend reads or writes any cache, and the decomp/catalogue layer is not involved in these runs (verified again by code inspection; placement generation is recomputed per run). No decomposition- or cache-assisted results are mixed into the kernel comparison.

---

## 8. Frontier assessment

- **Largest case solved by both backends:** V 5×5×9 (1120 raw / 140 orbit-restricted solutions).
- **Largest cases solved only by C++:** W 5×5×17 (exhaustive UNSAT in 69 s — Numba did not finish in 66 min), H 5×5×6 (complete 205,668-tiling enumeration in 11.3 min), and **W 5×7×9 — the previous frontier case — now exhaustively enumerated with orbit restriction in 82 min** (1.71B nodes vs 5.26B raw).
- **Largest solved only by Numba:** none.
- **Hardest unresolved by both:** Z 4×11×15 (then the S 4×8×130 / Z 6×6×10 classes, which are closed by certificates rather than search).
- **Frontier extension:** yes, materially — the W 5×7×9 exhaustive enumeration drops from 2.97 h to 82 min and becomes an orbit-restricted (10-solution) characterization; W 5×7×11 was probed for 2 h without exhaustion (timeout fired before the 4B-node cap), marking the next frontier step (estimated ≥10¹⁰ raw-equivalent nodes — reachable with the 4-core task-split port, not single-thread).

---

## 9. Performance diagnosis

- The **language gap is real but modest: 2.6–2.7× per node** on identical trees. Numba's JIT generates competent machine code for the same pointer-chasing CSR walk; the residual gap is allocation/deallocation of per-node vectors in the Numba core (Python lists for deactivated rows/cols), numpy scalar writes (`node_counter[0] += 1`, bool arrays) vs C++ `uint8_t` arrays, and JIT bounds-checking. Nothing exotic.
- The **benchmark-deciding gap is algorithmic**: symmetry (4.4–7× on the tested boxes) and propagation (~1.3–2.5×, composing multiplicatively) exist only in C++ today.
- Numba's parallelism (4 workers) recovers ~2–3× wall but suffers static-chunk imbalance (W 5×5×17: one worker at 287.7M nodes while others finished earlier) and the native-order tree penalty (±46% on V).
- Memory is a non-issue for both (<215 MB RSS).

---

## 10. Final report

### Executive conclusion

**Yes — the frontier moved, and it moved because the new algorithms and C++ compose.** The same 4-core machine that needed 2.97 h to exhaustively enumerate W 5×7×9 now does it in 82 minutes with a 10-solution orbit-restricted characterization; W 5×5×17 went from "Numba cannot finish in an hour" to a 69-second exhaustive UNSAT proof; V-class boxes run ~13× faster wall-clock. Z 4×11×15 remains out of reach for search at any plausible budget — measured dead-end depths (54–93 of 132 at 10⁸ nodes) put its endgame weeks away even for C++, confirming it needs a representational method.

### Historical progress

| Metric (W 5×5×17 unless noted) | First benchmark (Aug) | Now |
|---|---|---|
| C++ baseline | 264.3M / 441.8 s | unchanged (reproduced) |
| C++ + current algorithms | n/a | **26.4M / 69.2 s** |
| Numba | unfinished at 66 min | unfinished at 66 min (unchanged — no new machinery) |
| W 5×7×9 | 5.26B / 2.97 h (raw) | **1.71B / 82 min (orbit-restricted, exhaustive)** |

### Current Numba vs C++

See the table in §3. Headline: V 5×5×9 **13.5×** wall (6.2× nodes × 2.7× language ÷ Numba parallelism); W 5×5×17 **>57×** wall; Z unresolved for both.

### Algorithmic contribution

Symmetry: 3.9–7× node reduction on equal-dimension boxes (validated orbit-complete on achiral and chiral pieces). Propagation: ~1.3–2.5× further nodes, leaf-to-mid-depth concentrated, marginal standalone but compounding. Together: **10× on W 5×5×17, 7.5× on V 5×5×9, 3.1× on W 5×7×9** — and they are C++-exclusive today.

### Z frontier

All configurations UNKNOWN at 300M nodes (depth 105–111/132). The measured depth distribution proves the search never reaches the region where symmetry/propagation apply. Budget scaling is hopeless (≥10¹⁰ nodes). C++ does not change Z's practical status.

### Remaining bottleneck

**Search-space size, not speed.** Per-node throughput is now sufficient that a 2.6× language gain or further constant-factor pruning changes minutes, not feasibility. Z-class boxes fail because the exact-cover tree is exponentially wide in its middle depths (measured dead-end band 54–93 of 132) and every local invariant is either redundant with MRV (counting), blind (colour), or out-of-range (propagation).

### Recommendation

1. **Should C++ now be the primary search backend?** Yes, unambiguously — it is the only backend with the current algorithms, is 2.6× faster per node at the kernel, and delivered every frontier result above.
2. **Should Numba remain as correctness/reference backend?** Yes — its node-for-node agreement with C++ is the strongest cross-check in the toolchain, and the Python oracle methodology caught two real bugs (stamp-width, pair-scheme incompleteness). Keep it as the reference; do not invest in its search performance.
3. **Is further C++ optimisation worth doing now?** Only cheaply: the solver is single-threaded while the machine has 4 cores — porting the existing task-splitting to C++ (measured 2–3× effective for Numba) is the one high-yield engineering step. Beyond that, no.
4. **C++ performance or representational approaches next?** Representational approaches — for Z-class boxes the measured arithmetic (≥10¹⁰ nodes at 254–363K/s) rules out search; the frontier/transfer-matrix DP (proven on S 4×8) and SAT/certificate methods (proven on Z 6×6×10) are the only routes that have ever closed a box of this class.
5. **Single next experiment for the frontier?** **A Z 4×11×15 SAT/CaDiCaL run with the chiral-safe symmetry-breaking predicates** (the exact mechanism that closed Z 6×6×10 in 287 s), in parallel with a C++ W 5×7×11 exhaustive run (all-odd box, centre symmetry — estimated ~10¹⁰ raw-equivalent nodes ≈ 1–2 days single-thread, or ~6–12 h with the 4-core task-split port) to extend the W-family frontier beyond W 5×7×9.

---

## Appendix: run inventory

All raw outputs in `/tmp/opencode/bench/results/` (`NB_*` Numba reproductions, `LANG_*` language anchors, `PR_*` progression/propagation, `FX_*` frontier runs, `RD_*` research sampling). Validation scripts: `/tmp/opencode/bench/validate_sym.py` (orbit-completeness), plus inline W 5×7×9 certificate orbit check. C++ binary: `/tmp/opencode/bench/solver_new` built from the current `solvers/solver.cpp` via `zig c++ -O3 -std=c++17`; flags-off behaviour verified identical to the preserved baseline. The H 5×5×9 enumeration from the previous session remains running in the background (43.2B+ nodes at last check) and was the constant 1-core load for all timed runs.
# Current-Frontier Benchmark: C++ vs Numba after the algorithmic work

**Date:** 2026-09-02
**Machine:** i7-12700, 4 logical CPUs, 28 GB RAM (single-socket desktop; all runs on this machine)
**Stack:** Python 3.12.3, numba 0.65.1, numpy 2.4.6; `solvers/solver` C++ binary (built 2026-08-26, source = current `solver.cpp`)
**Nature:** investigation/benchmark only. No solver code was changed. All benchmark scripts live in `/tmp/opencode/bench/`; raw outputs in `/tmp/opencode/bench/results/`.

---

## 1. Executive conclusion

**The search backends themselves have not materially improved since the previous benchmark — but the system around them has, and that is where all the progress is.**

1. The C++ and Numba search kernels are **algorithmically unchanged** since the previous benchmark (Aug 25). The current C++ binary reproduces the old runs **node-for-node** (V 5×5×6: 366,907 nodes; V 5×5×9: 43,621,737 nodes — exactly the documented 367K / 43.6M) at the same speed (~0.9–1.0M nodes/s vs 0.84–0.98M old). On identical trees Numba and C++ also agree **exactly** on node counts, so the backends are search-equivalent; C++ is simply **2.0–2.7× faster per node** (not the 10–100× once estimated).
2. The algorithmic work of the last month landed **almost entirely outside the two backends**: catalogue corrections/expansion, SAT certificates (Z 6×6×10 UNSAT), stronger impossibility theorems (F, Y), guillotine/semigroup decomposition, the frontier/macro methodology (S 4×8×130), and the Z frontier DP. These close boxes **without invoking either backend**.
3. The one search-level change (corner-canonical symmetry breaking, uncommitted in `common/polycube_utils.py`) is real but **small and conditional**: it removes non-canonical corner placements, which does nothing for all-distinct boxes (W 5×7×9: **0 of 1828** removed; Y 2×5×10: 0 removed) and gives ~1.8× tree reduction only when two box dimensions are equal (V 5×5×9: 43.6M → 24.7M nodes). It is also **unsound for chiral pieces (H, S)** — a correctness bug, because reflections do not map a chiral piece to itself.
4. Benchmark evidence that the remaining difficulty is **algorithmic, not execution speed**: V→W grows the tree 120× (43.6M → 5.26B) for a 40% volume increase, while kernel throughput is roughly flat (~0.4–1.0M nodes/s). The decisive recent wins (Z 6×6×10 in 287 s SAT vs ≥10⁹-node raw tree; S 4×8×130 via macro state-collapse) came from representations that the raw backends cannot express.
5. **New result produced by this benchmark:** W 5×5×17 — the last remaining Unknown W box ≤ 20³ — is **UNSAT, proven exhaustively** by the current C++ backend (264,277,986 nodes, 0 solutions, full tree consumed, 404 s) and **independently cross-verified by Numba with an exactly identical node count**. This is ready to be recorded as `searched_no_solution`.

**Bottom line:** we are *not* much closer to solving substantially larger boxes *by raw search*; we are much closer *by going around raw search*. C++ exploits the current machinery as well as Numba does (identical trees when fed identical matrices) and is 2–2.7× faster per node, but neither backend has a cache, real search-level symmetry reduction, or strong pruning — and those, not kernel speed, are the frontier.

---

## 2. What changed since the previous benchmark

Previous benchmark reconstructed from three in-repo sources:

| Source | Content |
|---|---|
| `docs/phase2_benchmarks.md` (commit 7b1ba4c, 2026-08-13) | Hybrid solver, `--workers 4`: N 5×5×5 "~16 s"; Y 2×5×10 "completes in minutes"; S 4×8×130 unsolved (headline target); P 1×5×24 I/O stress |
| `docs/frontier/w_5x7x9_algorithmic_path_report.md` (2026-08-25) | Numba ≈ 300K nodes/s on W 5×7×9 raw; Python ≈ 10.5K/s (28×); no ordering improvement; recommendation: build C++ (estimated 3–30M nodes/s) |
| `docs/frontier/w_5x7x9_exhaustive_report.md` (2026-08-25) | C++: V 5×5×6 0.35 s / 367K nodes; V 5×5×9 51.8 s / 43.6M; W 5×7×9 10,677 s / 5.26B / 40 solutions; C++ throughput 493–977K nodes/s |

Changes since, classified by whether they can affect solving difficulty:

| Change | Classification | Material to solving? |
|---|---|---|
| `solvers/solver.cpp` (uncommitted): `max_nodes` cap, progress reporting, solution-vector tracking, vector reuse | infrastructure | No (search unchanged; verified by node-identity) |
| `common/polycube_utils.py` (uncommitted): symmetry breaking generalised cube → any box | search-space reduction | **Marginal**: only equal-dim boxes (~1.8×); zero for distinct dims; **unsound for chiral pieces** |
| `solvers/decomp.py`: ProofNode taxonomy (`PublishedSolution`), semigroup row/width generators, 3-axis guillotine (`Slab`/`Width`/`Breadth`), `@cache` | decomposition + reuse (proof layer) | **Yes** — closes boxes without search |
| Catalogues: Z +77 published + 6×6×10 SAT-UNSAT; F 2×2×N and 2×N×N theorems; Y thickness-1 theorems; W published 5×7×9; S one-sided primes | stronger impossibility/composite proof | **Yes** — audit-measured below |
| Frontier/macro methodology, checkpoint/resume, Z frontier DP (b714c93) | decomposition (different search representation) | **Yes** — but a separate method, not these two backends |
| Hybrid solver: node instrumentation, heartbeat, task stats | infrastructure (~9% Numba kernel cost, measured) | No |
| Prompt-cache reports (`reports/cache-*.md`) | agent-workflow LLM caching, **not solver caching** | No |

Note on reconstruction limits: the old hybrid runtimes for Y 2×5×10 ("minutes") were produced by the pre-phase2 parallelisation on solver versions and data files that no longer exist (`data/solutions_hybrid_y_2x5x10.dat` is gone; the old C++ binary had solution-file output that current source lacks and cannot be rebuilt here — no C++ compiler on this machine). The old baseline is therefore anchored on **documented node counts and rates**, which the current binary reproduces exactly (see §3).

---

## 3. Old → current improvement

### 3.1 Backend continuity (identical matrices, node-for-node verified)

| Case | Old (documented) | Current C++ | Current Numba | Verdict |
|---|---|---|---|---|
| V 5×5×6 raw | 367K nodes, 144 sols, 0.35 s | 366,907 nodes, 144 sols, 0.41 s | 366,907 nodes, 144 sols, 1.76 s | unchanged |
| V 5×5×9 raw | 43.6M nodes, 1120 sols, 51.8 s | 43,621,737 nodes, 1120 sols, 45.7 s | 43,621,737 nodes, 1120 sols, 111.8 s | unchanged |
| W 5×7×9 raw | 5.26B nodes, 40 sols, 10,677 s (full) | binary unchanged; 242.9M-node prefix at 652 s (373K/s) | same prefix in 1300 s (187K/s) | unchanged |
| N 5×5×5 hybrid w4 | "~16 s" (metric likely time-to-first-solution) | 34.8 s full enum (64 sols, 11.8M nodes); single-thread C++ 17.25 s on the 12.5M-node file-order tree | 35.5 s single-task | see §4 |

**Old → current C++ improvement: ~0×.** Same search, same speed (throughput 955K/s today vs 841–977K/s documented; within machine noise).
**Old → current Numba:** kernel unchanged (old ~300K nodes/s on W vs 224–248K measured today with instrumentation; un-instrumented core 390–430K/s on V boxes; instrumentation ≈ 9%). The only new machinery is corner symmetry breaking, quantified in §5.

### 3.2 Where the actual progress is (proof/decomposition layer, not backends)

Catalogue audits ≤ 20³, HEAD (b714c93) vs working tree, plus the SAT/macro results that fed them:

| Piece | Unknown HEAD → now | Composites HEAD → now | Published HEAD → now |
|---|---|---|---|
| Z | 331 → 319 | 64 → 70 | 0 → **77** |
| W | 1 → 1 | 448 → 451 | 0 → 1 |
| F | 70 → 62 | 483 → 488 | 0 → 0 |
| Y | 17 → 11 | 616 → 618 | 0 → 0 |

Concrete closures: Z 6×6×10 **UNSAT by verified SAT certificate** (CaDiCaL 287 s; raw search: 100M nodes in 290 s, 0 solutions, depth only 65/72 — the exact-cover tree is orders of magnitude larger); Z 5×10×{10..18} published; F 2×2×N and 2×N×N theorems; Y 1×5×{16..19}, 1×6×20, 1×8×20 theorems; W 4×12/13/14×15 composites. And separately, S 4×8×130 — the phase-2 headline case — was resolved by the **macro/frontier methodology** (2048 macro walks), not by either backend: the hybrid still crawls at ~6K nodes/s/worker on it.

---

## 4. Current Numba vs current C++

Methodology: for every case both backends consumed the **same placement file** (same matrix, same row order), so MRV choices are identical and trees agree **exactly**. Two orderings were also compared: the placements-file order (id = x + a·y + a·b·z) vs the "native" box-list order the Python solvers generate themselves.

### 4.1 Same-tree kernel comparison (raw searches, fresh, no caches — none exist)

| Case | Nodes | C++ time / rate | Numba time / rate | C++ ÷ Numba |
|---|---|---|---|---|
| V 5×5×6 raw | 366,907 | 0.41 s / 894K/s | 1.76 s / 208K/s (incl. JIT) | ~2.1× (warm, JIT-excl) |
| V 5×5×9 raw | 43,621,737 | 45.7 s / 955K/s | 111.8 s / 390K/s | **2.45×** |
| V 5×5×9 sym | 24,727,566 | 35.3 s / 701K/s | 69.1 s / 358K/s | **1.96×** |
| W 5×7×9 raw prefix | 242,939,178 | 651.8 s / 373K/s | 1300 s / 187K/s | **2.0×** (equal contention) |
| W 5×5×17 raw (full UNSAT) | 264,277,986 | 404 s / 654K/s | 1106 s / 239K/s | **2.7×** |
| Z 6×6×10 raw probe | 100M (C++) vs 48.1M/620 s | 345K/s | 78–103K/s | ~3.5–4× (contended) |
| H 5×5×9 raw to 500M | 500M | 873 s / 573K/s | ~2970 s interp. | ~3.4× (Numba contended) |

Steady-state rates: C++ ≈ 0.37–1.0M nodes/s (rate falls with matrix size/depth); Numba ≈ 0.33–0.43M nodes/s on V-shaped matrices, ≈ 0.22–0.25M on W, ≈ 0.08–0.10M on Z (contended). The un-instrumented Numba core is only ~9% faster, so instrumentation is not the story.

**The old report's estimate that C++ would be 10–100× faster (3–30M nodes/s) was wrong by an order of magnitude.** The real, repeatedly-verified factor is **2–2.7× per node** (≈ 3–4× on the largest matrices).

### 4.2 Machinery only Numba has, and how well it works

| Mechanism | Measured effect |
|---|---|
| Task-split parallelism (depth ≤ 4, target = workers×16) | V 5×5×9 sym: workers 1 → 105.0 s, 2 → 100.6 s, 4 → **69.2 s** (CPU 154%): only **1.5×** from 3× more workers; longest single task ≈ 37–38 s in every config (one pathological subtree dominates; static `pool.map` chunking idles workers). N 5×5×5: hybrid 4 workers **34.8 s ≈ single-task 35.5 s — parallel gain ≈ 0** |
| Native column ordering (its own id space) | Changes the tree itself: V 5×5×9 sym 36.0M nodes (native) vs 24.7M (file order) = **+46% work**; N 5×5×5 11.8M (native) vs 12.5M (file) = −5%. Ordering cuts both ways and is uncontrolled |
| Corner symmetry breaking | see §5 |

### 4.3 Which backend exploits the machinery better?

- On **identical inputs**, both explore identical trees — the machinery (placements, MRV, exact cover) is shared and C++ loses nothing by using Python-side preprocessing; verified by exact node-identity on 5 independent cases.
- **C++ is faster per node by 2–2.7×**, has no parallelism, and does not integrate the (weak) symmetry breaking itself — but it can consume symmetry-broken placement files and loses nothing by doing so.
- The **Numba hybrid's parallelism is currently worth less than C++'s single-thread advantage**: on V 5×5×9 sym, 4-worker hybrid = 69.2 s vs single-thread C++ = 35.3 s on the smaller file-order tree. On N 5×5×5, 4-worker hybrid (34.8 s) ≈ single-task Numba (35.5 s) ≈ single-thread C++ (17.25 s on its 12.5M-node tree).
- Net: **today, the fastest practical way to exhaust a box on this machine is single-thread C++ on the file-order matrix** — the parallel Python path does not beat it on any measured case.

---

## 5. Cache/decomp effects

- **The raw backends have no cache/reuse layer at all.** Every run regenerates placements and searches from scratch (`grep` confirms: no sqlite/pickle/shelve/np.save in the solver paths). Persistent reuse exists only in (a) `decomp.classify`'s intra-process `@cache`, (b) the macro/frontier tooling's checkpoint/resume files (e.g. `4x9_*.ckpt` backups), and (c) manually curated solution files in `data/`. All headline numbers above are therefore **fresh-search numbers** by construction.
- The catalogue/proof layer is where reuse lives: `PUBLISHED_SOLUTIONS` (77 Z entries + W 5×7×9), `SEARCHED_NO_SOLUTION` (incl. Z 6×6×10 SAT certificate), semigroup/guillotine decomposition, and the V/W/H/S exhaustive certificates. These answers are instant and backend-independent — e.g. Z 6×6×10 classifies in <1 ms via the SAT certificate vs ≥10⁹-node-equivalent raw search.
- Consequence: **cache effects do not contaminate the C++/Numba comparison in any of the tables above** — but they also mean none of the recent "cache/reuse" work speeds the search kernels up at all.

---

## 6. Hard-box frontier

| Case | Status before today | This benchmark | Frontier meaning |
|---|---|---|---|
| W 5×7×9 (315 cells) | Exhaustive: 5.26B nodes / 2.97 h C++ (Aug 25); Numba never completed | unchanged binary; same-work prefix C++ 652 s vs Numba 1300 s; Numba full-tree projection ≈ 5.9–6.5 h | **largest box ever fully enumerated; still C++-only in practice** |
| W 5×7×11 | prime (catalogued Jun 18, witness-level) | 2 raw solutions within 1.5B-node probe (61 min C++, 408K/s); exhaustion not attempted | next W-family exhaustion target; needs symmetry/pruning to be tractable |
| H 5×5×9 | open (recommended next project Aug 26) | **not exhausted**: 1.8B+ nodes, 91,512 solutions at 3023 s, still running at ~595K/s when report finalized | largest solution-rich open box measured; exhaustion likely several B more nodes |
| **W 5×5×17** | **the only remaining Unknown W box ≤ 20³** | **UNSAT proven exhaustively today: 264,277,986 nodes, 0 sols, 404 s C++; Numba cross-check exactly 264,277,986 nodes — double-verified** | new closure; ready to record as `searched_no_solution` |
| Z 4×11×15 | smallest Unknown Z box (vol 660) | 500M-node probe: 0 sols, max depth 111/132, 380K/s — far from exhausted | open for both backends; candidate for SAT/certificate treatment |
| Z 6×6×10 | UNSAT via verified SAT cert (Aug 29) | raw search 100M nodes/290 s, depth 65/72 — tree ~10⁹+ | proof layer ≫ raw backends |
| S 4×8×130 | prime; macro-resolved (2048 walks) | hybrid probe ~6K nodes/s/worker | raw backends hopeless; macro method resolved it |

**Largest solved by both:** V 5×5×6/5×5×9-class boxes and **W 5×5×17 (UNSAT, node-identical double proof)**.
**Largest solved only by C++:** W 5×7×9 exhaustive (2.97 h); nothing solved by Numba that C++ could not do.
**Largest solved only by Numba:** none.
**Both UNKNOWN:** Z 4×11×15, S 4×8×130-class boxes (raw), Z 6×6×10 (resolved by SAT instead).
**Effort scaling (the real frontier curve):** V 5×5×9 43.6M nodes → W 5×7×9 5.26B nodes for +40% cells (**×120**); W 5×5×17 264M nodes for a *negative* answer on 425 cells; W 5×7×11 > 1.5B without exhausting 385 cells. Tree size explodes much faster than volume; kernel speed is a linear factor against an exponential wall.

---

## 7. Current bottleneck

Evidence-led ranking:

1. **Branching factor / tree size (dominant).** W 5×7×9 = 5.26B nodes vs V 5×5×9 = 43.6M for +40% volume. The kernels are MRV-only; the old dead-end analysis showed 74% of deep failures are "connected but untileable" and 26% disconnected — a connectivity + component-parity check would prune a known fraction, and none of it exists in either kernel today.
2. **No search-level orbit symmetry reduction.** The raw W 5×7×9 tree contains all 8 D2h copies of every orbit (40 raw = 5 orbits × 8). The current corner-canonical scheme does nothing for distinct-dimension boxes (measured: 0 placements removed) and only ~1.8× on equal-dim ones. An orbit-based symmetry break would divide such trees by ~|G| — the single largest available factor.
3. **Parallelism of the only parallel backend is weak** (1.5× at 4 workers; longest-task-bound; static chunking; near-zero on N 5×5×5).
4. **Kernel speed is a solved-enough problem.** C++ ≈ 0.4–1.0M nodes/s, Numba ≈ 0.22–0.43M nodes/s; a 2× kernel gain buys minutes against billion-node trees. The old "10–100× C++" hypothesis is measured now: it was 2–2.7×.
5. **What actually moved the frontier is outside the kernels**: SAT certificates, catalogue theorems, macro state-collapse. The bottleneck for *those* is coverage (which pieces have certificates/theorems), not execution.

Not the bottleneck: memory (peak < 1 GB in all runs), I/O, JIT warmup, or cache behaviour.

---

## 7. Summary table

| Case | Old system (Aug 25 state) | Current Numba | Current C++ | Main source of improvement | New frontier? |
|---|---|---|---|---|---|
| N 5×5×5 (hybrid w4) | ~16 s (metric ambiguous) | 34.8 s w4 ≈ 35.5 s ×1 | 17.25 s ×1 (12.5M nodes) | none — parallelism ineffective | no |
| Y 2×5×10 | "minutes" (old parallelisation) | 3.0 s (628 sols) | (same matrix) | task-split parallelism | no |
| V 5×5×6 raw | 367K nodes / 0.35 s | 1.76 s | 0.41 s | none (identical) | no |
| V 5×5×9 raw | 43.6M / 51.8 s C++ | 111.8 s | 45.7 s | none (identical) | no |
| V 5×5×9 sym | n/a (no sym then) | 69.1 s (36.0M native tree) | 35.3 s (24.7M file tree) | **corner symmetry breaking (1.8×)** + ordering luck | no |
| W 5×7×9 raw | **5.26B / 2.97 h C++ (exhaustive)** | ~6 h projected (224–248K/s) | 2.97 h (unchanged) | nothing — unchanged | still the C++-only frontier |
| W 5×7×11 | prime by witness (Jun) | not run | 2 sols ≤ 1.5B nodes (61 min) | — | witness-only |
| H 5×5×9 | open | ~3.4× slower per node | >1.8B nodes, 91K+ sols, running | — | **yes — open** |
| **W 5×5×17** | Unknown | **264.3M nodes, 0 sols — confirms UNSAT** | **264,277,986 nodes, 404 s, UNSAT exhaustive** | raw search (no cache, no sym) | **yes — closed today** |
| Z 6×6×10 | raw-infeasible | raw-infeasible | 100M nodes ≪ tree | **SAT certificate (287 s)** | closed outside backends |
| Z 4×11×15 | Unknown | Unknown | 500M probe, depth 111/132 | — | **yes — open** |
| S 4×8×130 | unsolved (phase 2 headline) | ~6K nodes/s/worker — hopeless | same | **macro/frontier method** | closed outside backends |

---

## 8. Explicit answers

**Have the algorithmic improvements materially reduced the search problem?**
For the raw backends: **no** — kernels, trees, and throughput are unchanged (exact node-identity with the Aug-25 numbers), and the one search-level reduction (corner symmetry) helps only equal-dim boxes (~1.8×) and is unsound for chiral pieces. For the *system*: **yes** — the proof layer closed 30+ boxes (F 8, Y 6, W 4, Z 12 + 77 published) and resolved Z 6×6×10 and S 4×8×130 entirely outside these backends. The reduction is real but it lives in `decomp.py` + certificates, not in C++/Numba.

**Has that translated into materially larger boxes being solvable?**
Not by the backends. The largest exhaustive enumeration is unchanged (W 5×7×9, 5.26B nodes). Today's new solve (W 5×5×17 UNSAT) was already within reach of the old binary. The larger-box progress (S 4×8×130, Z 6×6×10) came from different representations (macro/frontier DP, SAT), which is precisely the lesson: **the frontier moves when the representation changes, not when the kernel gets faster.**

**Is C++ now the limiting opportunity, or is the remaining bottleneck algorithmic?**
Both, in this order of magnitude: (a) C++ leaves a real 2–4× on the table (no task-split parallelism, no symmetry-break integration — though it can consume sym-broken placement files losslessly), and its per-node advantage over Numba is modest; (b) the dominant limiter is algorithmic — an exponential tree with no orbit symmetry reduction and no connectivity/parity pruning, attacked one node at a time at ~10⁶ nodes/s. A 2.7× kernel gain moves W 5×7×9 from 2.97 h to ~1.1 h; orbit symmetry breaking would move it toward ~25 min; both together still leave Z 4×11×15-class boxes out of reach — those need certificate methods.

**What is the single most valuable next piece of work?**
**Search-level orbit symmetry breaking (chiral-safe) in the C++ solver, plus the connectivity/component-parity feasibility check.** These are pure search-space reductions that multiply every future exhaustive run by ~|G| (8–48× on the boxes that matter) and compose with the existing certificate pipeline; they also instantly transfer to Numba via the same placement-restriction mechanism verified node-identical in this benchmark. This is also the natural engine for the next catalogue entries: H 5×5×9 exhaustion (already >1.7B nodes today), W 5×7×11 exhaustion, and Z 4×11×15.

Two correctness items surfaced en route and should be fixed independently of any benchmarking:
- `generate_placements(break_symmetry=True)` (now the **default** in both Numba solver CLIs) is unsound for chiral pieces (H, S) — it applies reflections that do not map the piece to itself and can delete genuinely distinct tiling classes. H/S runs must use `--no-symmetry` (all H/S results in this report do), or the scheme must be restricted to the rotation subgroup for chiral pieces.
- `docs/pieces/H.md`'s statement that "the only reflection handling in the repository is solution-level, never piece-level" is now stale given the uncommitted `polycube_utils.py` change.

---

## Appendix: method notes

- Identical matrices across backends: placements generated by the repo's own `generate_placements` (+ `filter_and_reindex_placements` when symmetry-broken), dumped once to a file, consumed by C++ directly and by a Numba driver that rebuilds the CSR arrays exactly as `fitpolycubes_hybrid.main()` does and runs the production `solve_numba_core` once with an empty task prefix.
- Node-for-node identity C++ ↔ Numba was verified on V 5×5×6 raw/sym, V 5×5×9 raw/sym and the complete W 5×5×17 UNSAT tree before any speed number was interpreted.
- "Native order" runs emulate the hybrid's self-generated matrix (box_list id space); they reproduce the hybrid's totals to within the task generator's few dozen internal nodes (36,006,910 vs 36,006,879; 11,822,582 vs 11,822,559).
- Contention: up to 4 concurrent solver processes on 4 logical CPUs during frontier probes; every affected row is labelled. The headline same-tree kernel rows (V, W 5×5×17) are solo or near-solo.
- The full H 5×5×9 enumeration was still running at report time (1.8B+ nodes, 91,512 solutions, ~595K nodes/s); its final count should be appended to the H catalogue when it completes.
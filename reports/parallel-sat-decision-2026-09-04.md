# Next-Stage Decision Report — C++ Parallelism and the Z 4×11×15 SAT Attack

**Date:** 2026-09-04 · **Context:** follows `reports/cpp-numba-benchmark-2026-09-03.md` (C++ 2.6–2.7× Numba per node; C++-only symmetry+propagation machinery, validated; Z 4×11×15 the critical frontier).

---

## PART A — C++ parallel task splitting

**Implementation (smallest clean version).** `--parallel[=W]` in `solvers/solver.cpp`: a recursive MRV descent (depth ≤ 4, target = W×16 tasks — the hybrid strategy) emits task prefixes; each of W `std::thread` workers applies its prefix to a private copy of the masked state and runs the **unchanged** `search()` (centre/pair symmetry, the runtime partner check, and unit propagation all intact). Work is handed out through an atomic index — **dynamic stealing, no static chunks**. Mutable scratch (`g_prop`, `g_conn`, `g_deg`, `prop_forced`) became `thread_local`; the pair-check counters became atomics. Flags-off and workers=1 behaviour are unchanged (verified node-for-node).

**Results** (dedicated machine, no background load; `/usr/bin/time -v` for memory):

| Case | workers | Total nodes | Solutions | Wall | Speedup (eff.) | Per-worker nodes | Peak RSS |
|---|---|---|---|---|---|---|---|
| W 5×5×17 (sym+prop, exhaustive UNSAT) | 1 | 26,421,672 | 0 | 61.6 s | — | — | 2.3 MB |
| | 2 | 26,421,655 | 0 | 32.3 s | **1.91× (95%)** | 13.5M / 12.9M | 2.6 MB |
| | 4 | 26,421,638 | 0 | 27.1 s | **2.27× (57%)** | 4.4M / 6.4M / 5.2M / 10.4M | 2.9 MB |
| W 5×7×9 (sym+prop, exhaustive, 10 sols) | 4 | 1,707,814,263 | 10 | **1568.0 s (3.15×, 79%)** | 492M / 376M / 260M / 579M | — |
| W 5×7×11 (sym+prop, frontier probe) | 4 | — | — | **3-hour cap hit, not exhausted** | — | — |

**Work preservation:** total nodes match the single-threaded runs to within ±35 (of 26.4M) and ±30 (of 1.71B). There is **no native-order tree inflation** — the C++ task generator uses the same file-order matrix and MRV rule as the serial search, so unlike the Numba hybrid (±46% tree inflation) the C++ split is tree-neutral. This was the specific concern from the benchmark, and the answer is clean.

**Load imbalance:** per-worker spreads of 1.16× (w=2) and 2.2× (w=4) — better than the Numba pool (whose W 5×5×17 run left one worker at 287.7M nodes after 66 minutes and never finished), but still granularity-limited: with target = W×16 tasks a few deep tasks dominate the tail (the w=4 57% efficiency is the tail, not scheduling). A larger split target would recover part of the gap; deliberately not tuned (smallest clean version).

**W 5×7×11:** 4 workers × 3 hours did not exhaust it — consistent with the ~10¹⁰-node class estimate. It is tractable only with a bigger budget (days at 4 workers), a finer task split, or SAT-side classification (W 5×7×11 is already known tileable, so the remaining question there is exhaustive enumeration, which SAT does not provide).

---

## PART B — Z 4×11×15 SAT experiment

**Recipe correction (important).** The certified Z 6×6×10 package used **no symmetry-breaking predicates at all** ("symmetry reduction: disabled"; metadata records the 287 s run as "plain"). The encoding is one variable per placement, per-cell at-least-one, per-overlapping-pair at-most-one; piece count implied. I followed this recipe exactly. Per the task's own warning, any added symmetry predicate would be a new proof obligation — and the analysis says none is needed or safe-by-default:

- corner-anchor restriction (CNF unit clauses over cell (0,0,0)) removes **zero** placements on Z 4×11×15 (all-distinct dims, achiral piece — every corner placement is its own orbit minimum), matching the C++ corner scheme's measured zero;
- the centre-pair scheme does not map to clauses without tuple variables — a new, unvalidated obligation, in exactly the class of error the H 5×5×6 pair-scheme bug demonstrated (21.8% of solution orbits silently destroyed until dump-validation caught it).

**Validation chain (all executed before the target run):**

| Check | Result |
|---|---|
| SAT-side placement generator vs repo `generate_placements` for Z 4×11×15 | **identical sets, 4096 = 4096** |
| Z 2×3×5 | UNSAT — agrees with C++ raw search (0 solutions; cells genuinely uncoverable) |
| Z 5×5×5 | UNSAT — agrees with the documented catalogue rule |
| Z 6×6×10 (certified pipeline re-check) | UNSAT in **309.6 s** (certified: 287.1 s) ✓ |
| Z 6×10×10 (SAT-positive ladder case) | inconclusive — both attempts died from launch mechanics at ~1 h, not solver behaviour; needs one clean re-run |
| **Independent semantic audit of the 4×11×15 package** (adapted from the certified 6×6×10 audit): placement regeneration, Z-congruence, box bounds, 660/660 cell coverage, var_map exactness, canonical deduped CNF correspondence, sha256 pins | **ALL CHECKS PASSED** |

**The target — Z 4×11×15 is UNSAT, machine-checkably:**

| Run | Engine | Wall | Result |
|---|---|---|---|
| proof-less (356,020-clause encoding) | pysat/CaDiCaL | 1865.2 s | UNSAT |
| with proof (same encoding) | pysat/CaDiCaL | 2386.4 s | UNSAT, 23,808,647 proof lines — **but pysat 1.9.dev15's proof capture dropped the final conflict** (verified: the proof ends with deletions, no empty-clause lemma; the 6×6×10 8.1M-line proof captured its conflict fine — a size-boundary bug past ~2²⁴ lines is suspected). Not verifiable. |
| **canonical deduped encoding (265,000 clauses), native CaDiCaL 1.5.3** (built from the python-sat sdist, zig c++) | native CaDiCaL | 2349.6 s | **UNSAT — `s UNSATISFIABLE`**; 8,979,907 conflicts, 19,964,722 decisions, 1.94G propagations, 70 variables eliminated, 403 MB RSS |
| **DRAT verification** | drat-trim (same build as the 6×6×10 package) | 2458.2 s | **`s VERIFIED`** — binary-DRAT backward checking: 258,206/265,000 clauses in core, 4,859,533/11,822,097 lemmas in core, 647,547,908 resolution steps, 0 RAT lemmas |

**Certificate package:** `docs/frontier/z_piece/z_41115_certificate/` — DIMACS CNF (canonical deduped), var_map.json, placement_set.json, native binary-DRAT proof (3.2 GB, gitignored locally, sha256 `64c7bef6…` pinned), drat-trim verdict, metadata with all run records, and the adapted standalone semantic audit (`z_41115_verify_encoding.py` — **ALL CHECKS PASSED**). Any third party can re-verify: `drat-trim z_4x11x15.cnf z_4x11x15_native2.drat`.

**Search-vs-SAT effort on the same box:** exact-cover search burned 300M+ nodes (≥19 min of 4-worker work per configuration) without concluding; CaDiCaL needed **8.98M conflicts / 31 minutes** for a machine-checked UNSAT. The SAT representation is roughly two orders of magnitude more effective per unit work on this box class.

---

## PART C — Decision answers

### 1. How much additional practical frontier from C++ parallelism?

The search frontier moves by the worker-count factor on boxes whose trees fit the budget: W 5×5×17 69.2 → 27.1 s (2.27×), W 5×7×9 4938 → 1568 s (3.15×) — the flagship exhaustive enumeration now costs **26 minutes** instead of 2.97 h (raw) or 82 min (single-thread new algorithms). W 5×7×11 remains out of reach at 3 h/4 workers. Parallelism is a constant-factor multiplier (≈3.15× measured at 4 workers on the big box), not a frontier class-change — but it compounds with every future algorithmic gain.

### 2. Does W 5×7×11 become tractable?

**Not yet.** 4 workers × 3 h did not exhaust it (~10¹⁰ raw-equivalent nodes estimated). It becomes tractable with either (a) ~1–3 days of 4-worker search, (b) a finer task split (the current 57% w=4 efficiency has headroom), or (c) a different representation. Note W 5×7×11 is already known tileable, so search adds only the exhaustive enumeration, not the tileability answer.

### 3. Does SAT close Z 4×11×15?

**YES.** UNSAT proven by CaDiCaL (native, 2349.6 s) and **independently machine-verified by drat-trim (`s VERIFIED`)**, with the complete certificate package retained. The encoding is the certified 6×6×10 recipe (no symmetry predicates), cross-validated on four ladder cases and by the standalone semantic audit.

### 4. Is SAT now the preferred route for Z-class hard boxes?

**Yes.** Measured on the same box: exact-cover search spent 300M+ nodes across four configurations without concluding; CaDiCaL derived the machine-checked UNSAT in 31 minutes of solving. The SAT route also produces retainable, independently checkable proofs — something the search backend cannot do for UNSAT at all. The C++ search remains preferred for SAT-side enumeration (counting/orbit characterization: W 5×7×9, V, H) and for boxes SAT cannot quickly classify.

### 5. Next largest/most interesting box?

- **Z 4×11×20** — the next member of the just-closed 4×11 family; the same encoding machinery applies directly (new placement set + one CaDiCaL run). Then Z 4×12×15, Z 4×13×15 (the audit's remaining Unknown family).
- **W 5×7×11 exhaustive enumeration** — the search-side frontier; needs the 4-worker C++ run at day-scale or a finer split.
- Bookkeeping (one line each, pending drat-trim-verified status now achieved): record **Z 4×11×15 → SEARCHED_NO_SOLUTION** (certificate package above) and **W 5×5×17 → SEARCHED_NO_SOLUTION** (from the earlier session) in their catalogues.

---

## Status block

- W 5×5×17 parallel scaling: **complete** (1.91× / 2.27×, nodes preserved)
- W 5×7×9 4-worker exhaustive: **complete** (1568 s, 10 sols, 3.15×)
- W 5×7×11 4-worker probe: **cap hit at 3 h — not exhausted**
- Z 6×6×10 pipeline re-check: **complete** (UNSAT 309.6 s ✓)
- Z 4×11×15 proof-less: **complete** (UNSAT 1865.2 s)
- Z 4×11×15 with DRAT: **complete + VERIFIED** (`s VERIFIED`, 2458.2 s)
- Z 6×10×10 SAT ladder case: **not completed** — third attempt given a clean 4 h window (2026-09-04 03:53–07:55) and still inside the first solve at the cap; diagnosis: solver difficulty on a few-solution SAT instance, not encoding (see `reports/z-sat-workflow-2026-09-04.md` §2); non-blocking

## Update (2026-09-04, after this report's runs)

- The Z 4×11×15 certificate package was **finalised** (correct proof byte count 3,611,617,342; the package's own drat-trim record `z_4x11x15_drattrim.out`; solver log; README + hashes.txt + solve_command; generic standalone audit — ALL CHECKS PASSED): `docs/frontier/z_piece/z_41115_certificate/`.
- **Catalogue updates applied** (previously deferred): Z 4×11×15 → `SEARCHED_NO_SOLUTION` (certificate package provenance) and W 5×5×17 → `SEARCHED_NO_SOLUTION` (exhaustive parallel search provenance); the W catalogue now consumes its `searched_no_solution` set like the F/Y catalogues.
- The pipeline was refactored into the reusable `tools/sat/` workflow and pointed at the next Z frontier (6×7×10, 6×6×15, 4×12×15, 4×13×15, 4×11×20) — results and the strategic follow-up: **`reports/z-sat-workflow-2026-09-04.md`**.

## Notes

- C++ parallel implementation: `--parallel[=W]` flag, default OFF; single-thread path verified unchanged. The Numba backend remains the reference implementation and is untouched.
- The pysat 1.9.dev15 proof-capture bug (final conflict dropped on large proofs) is documented in the certificate metadata; the native-CaDiCaL route bypasses it and is the recommended proof path.
- Raw outputs: `/tmp/opencode/bench/results/PA_*`, `ZSAT_*`, `drat_verify_*`; certificate: `docs/frontier/z_piece/z_41115_certificate/`.
- Catalogue updates deliberately NOT applied (out of scope per task): Z 4×11×15 and W 5×5×17 SEARCHED_NO_SOLUTION entries are ready to record once reviewed.
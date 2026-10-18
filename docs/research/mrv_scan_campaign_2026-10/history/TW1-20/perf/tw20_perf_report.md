# TW1-20 PERF — Release Benchmark of the Verified ActiveX Fix

**Date:** 2026-10-16 (Pacific/Auckland)
**Scope:** Measure release-build performance of the fixed ActiveX candidate vs the coalesced baseline. No further optimisations implemented. No commits, merges, or deploys. No existing sources or binaries modified.

---

## 1. Candidate verification

Debug report read: `/tmp/pentacube-bench/tw20/debug/debug_report.md`.

| Item | Expected SHA256 | Actual SHA256 | Match |
|---|---|---|---|
| Baseline source `/tmp/pentacube-bench/tw18/solver_coalesced.cpp` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` | ✓ |
| Baseline source copy `/tmp/pentacube-bench/tw20/solver_coalesced.cpp` | (same) | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` | ✓ |
| Fixed candidate source `/tmp/pentacube-bench/tw20/solver_active_x.cpp` | `42fad94bb9cabeafc379e50b58f8e6816c0aa545a48ed178145febb15ef7bed9` | `42fad94bb9cabeafc379e50b58f8e6816c0aa545a48ed178145febb15ef7bed9` | ✓ |
| Fixed candidate binary `/tmp/pentacube-bench/tw20/solver_active_x` | `fe8ea52f126494df8f7e90d61797c30cfb9992309e480eac65811fa2c3f15e9b` | `fe8ea52f126494df8f7e90d61797c30cfb9992309e480eac65811fa2c3f15e9b` | ✓ |

### Build type of the verified binary

`file` reports both `solver_active_x` and `solver_baseline` as ELF 64-bit with `debug_info, not stripped`, and `readelf -S` shows `.debug_*` sections in both. This is the standard output of `g++ -Ofast -march=native -flto` **without** `-s`/`strip`: optimisation is fully enabled (`-Ofast`), and the `.debug_*` sections are metadata only — they are not loaded at runtime and do not affect executed code. Crucially:

- `strings solver_active_x | grep ACTIVEX-INVARIANT` → empty (no invariant checks).
- `strings solver_active_x | grep -i "gmon\|mcount\|profil"` → only `__gmon_start__` (normal glibc symbol, not instrumentation).
- Verified sources contain zero `ACTIVEX-INVARIANT` and zero profiling-instrumentation matches.

**Determination: the verified fixed binary is a release (`-Ofast`) build carrying harmless unstripped debug metadata — not a diagnostic build.** The fresh `perf/` binaries below reproduce it bit-identically.

### Prior 7.86% slowdown — provenance: UNVERIFIED

- The TW20 report's benchmark table (median −7.86%) is **byte-identical** to the TW18 overlap report's table, including the header label (`Active-X` vs `Overlap` aside, all five timings match to 4 decimals).
- The TW20 report's recorded candidate binary hash `d21465021…` equals the **TW18 overlap candidate's** source/binary hash — it does **not** match any ActiveX source (`42fad94b…`) or binary (`fe8ea52f…`).
- No TW20 benchmark raw logs (`baseline_w5x7x9_p*.log` / `active_x_w5x7x9_p*.log`) exist on disk.
- Therefore the earlier 7.86% slowdown **cannot be established as a measurement of the corrected (or even the buggy) ActiveX candidate**. It is labelled **UNVERIFIED** and is **not** used as the performance result. The measurements in §4 supersede it.

---

## 2. Isolated release builds

Directory: `/tmp/pentacube-bench/tw20/perf/` (created for this experiment).

Sources copied verbatim (hashes re-verified after copy):
- `perf/solver_baseline_src.cpp` = `a4fdcf12…` ✓
- `perf/solver_active_x_src.cpp` = `42fad94b…` ✓

Build commands (same compiler, version, flags for both):

```
g++ -Ofast -march=native -flto -std=c++17 -pthread solver_baseline_src.cpp -o solver_baseline
g++ -Ofast -march=native -flto -std=c++17 -pthread solver_active_x_src.cpp -o solver_active_x
```

Compiler: `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` — matched.
Build output (both): only `lto-wrapper: warning: using serial compilation of 2 LTRANS jobs` (+ note). Full logs: `perf/build_baseline.log`, `perf/build_active_x.log`.

| Binary | SHA256 | Matches verified binary |
|---|---|---|
| `perf/solver_baseline` | `79dff337875560de88f2501a602e8aeebabc26220a61197204adf910c95ebc47` | ✓ identical to `/tmp/pentacube-bench/tw20/solver_baseline` |
| `perf/solver_active_x` | `fe8ea52f126494df8f7e90d61797c30cfb9992309e480eac65811fa2c3f15e9b` | ✓ identical to expected fixed binary |

No source file or existing binary was modified (re-hashed originals after the build — unchanged). Neither binary contains invariant checks or profiling instrumentation (zero `ACTIVEX-INVARIANT` strings; no `gmon` instrumentation beyond the standard glibc symbol).

Documented asymmetry (not a flag mismatch): the ActiveX source adds bounded cycle-guard counters (`link_iters`/`iter_count` with abort past `num_rows` / `num_cols*100`) in the propagator's ActiveX traversals; the baseline has no equivalent counters. These execute a handful of integer ops per traversal step and cannot explain multi-second swings; they are part of the candidate under test.

---

## 3. Release-build verification before timing

Exact placement files / CLI from the debug report (single-threaded, propagation-enabled; `--parallel` never used):

- V: `./solver V 5 5 6 placements_V_5x5x6.txt --connectivity --symmetry --region-prune=propagate`
- KSSref: `./solver KSSref 5 5 5 placements_KSSref_5x5x5.txt 10000000 --connectivity --symmetry --region-prune=propagate`
- W: `./solver W 5 7 9 placements_W_5x7x9.txt 2500000 --connectivity --symmetry --region-prune=propagate`

Placement SHA256: V `dc22870d…`, KSSref `9786dd43…`, W `a7a421cd…`.

| Test | Baseline (exit) | ActiveX (exit) | Comparison |
|---|---|---|---|
| V 5×5×6 exhaustive | 0 — 70033 nodes, 18 sol, 34236 dead, depth 30/30, conn 70015/2569, pair 2587/1013, prop 14452 (forced 42099) | 0 — identical | ✓ IDENTICAL (`verify_V_*`) |
| KSSref 5×5×5 cap 10M | 0 — 10000068 nodes, 0 sol, 6335178 dead, depth 24/25, conn 9999999/3070835, prop 1297394 (forced 2464552) | 0 — identical | ✓ IDENTICAL (`verify_KSS_*`) |
| W 5×7×9 cap 2.5M | 0 — 2500040 nodes, 0 sol, 1136291 dead, depth 58/63, conn 2499999/233966, prop 564316 (forced 1525974) | 0 — identical | ✓ IDENTICAL (`verify_W_*`) |

All diffs exclude `Time:` / `Nodes/sec` / `Solutions/sec` only; full histograms identical. Both implementations used identical search settings. Proceeding to benchmarks was justified.

---

## 4. Five paired release benchmarks (W 5×7×9, 2.5M cap)

Same placement file, CLI, and cap for all ten runs. Sequential execution, never concurrent. Each run wrapped in `/usr/bin/time -v` (external wall clock + peak RSS recorded separately from the solver-internal `Time:`).

| Pair | Order | Baseline internal (s) / exit | ActiveX internal (s) / exit | Ratio (AX/base) | Reduction |
|---|---|---|---|---|---|
| 1 | baseline, ActiveX | 21.5526 / 0 | 24.8392 / 0 | 1.1525 | −15.25% |
| 2 | ActiveX, baseline | 20.9634 / 0 | 15.7737 / 0 | 0.7524 | +24.76% |
| 3 | baseline, ActiveX | 21.3437 / 0 | 15.0896 / 0 | 0.7070 | +29.30% |
| 4 | ActiveX, baseline | 23.9020 / 0 | 27.5927 / 0 | 1.1544 | −15.44% |
| 5 | baseline, ActiveX | 13.5872 / 0 | 23.7767 / 0 | 1.7499 | −74.99% |

Per-pair ratio = ActiveX time / baseline time (solver-internal `Time:`). Reduction = 100·(1 − ratio).

- Median baseline internal: **21.3437 s**; median ActiveX internal: **23.7767 s**.
- Median of the five paired reductions: **−15.25%** (ActiveX slower).
- Baseline range: 13.5872–23.9020 s (10.3 s spread on identical work). ActiveX range: 15.0896–27.5927 s (12.5 s spread).
- External wall clocks track internal times within ~0.03 s (e.g. pair 1: 0:21.56 vs 21.5526 s); internal vs external are reported separately and never mixed — the table above uses internal times consistently.
- Peak RSS (kB): baseline 4296/4280/4336/4340/4484 (median 4336); ActiveX 4508/4616/4268/4472/4432 (median 4472). No meaningful memory difference (~3% of medians, within noise; both ~4.3–4.6 MB).
- Correctness consistency: all ten runs report **2500040 nodes, 0 solutions, 1136291 dead ends, conn 2499999/233966, prop 564316 (forced 1525974)**; per-pair stdout diffs (excl. timing) all IDENTICAL.
- System load: `uptime` load average ~5.1–5.4 on 8 cores with only 3 GB available of 11 GB at benchmark start; no concurrent solver processes. The host was heavily loaded by unrelated work, which explains the extreme run-to-run variability (pair 5 baseline 13.59 s vs pair 4 baseline 23.90 s). Start/end timestamps per run are in the shell transcripts; raw logs in `perf/bench_p*.log` + `perf/bench_p*.time`.

---

## 5. Analysis

- **No measurable win.** The median paired reduction is −15.25% (slower), but with only five pairs and ±25–75% swings driven by host load, the honest reading is stronger: **the environment noise floor exceeds any candidate effect**. Baseline itself varies by 76% (13.59→23.90 s). Two pairs favour ActiveX (+24.76%, +29.30%), three favour baseline (−15.25%, −15.44%, −74.99%). Neither direction is distinguishable from noise.
- **Maintenance/rollback costs included.** These are end-to-end runtimes, so ActiveX list-maintenance and rollback costs are inside the measured totals — no separate credit is claimed for eliminating inactive-row visits.
- **Historical −7.86% is not evidence.** Per §1 it is UNVERIFIED (wrong-provenance table, no raw logs) and was excluded from this decision.
- **Memory:** no concern (~148 KB index; measured RSS medians within 3%).
- **Correctness:** perfect consistency across all ten benchmark runs plus the §3 verification suite.

---

## 6. Decision

**RETAIN AS EXPERIMENTAL.**

Rationale: the candidate is provably correct (invariant-checked, counter-identical on V/KSSref/W plus forced-placement traces), but this benchmark campaign cannot distinguish its performance from host noise — the median (−15.25%) is noise-dominated, not a clean slower signal, and two pairs show large apparent wins that are equally untrustworthy. Per the task instructions, noisy/marginal results must be retained as experimental rather than claimed as a win — and symmetrically, they should not be dressed up as a definitive rejection of the idea on performance grounds either. No runtime heuristic was added to compensate. Any future timing must run on a quiet, isolated host (or with many more pairs / pinned cores) before a RETAIN-vs-REJECT call on speed.

---

## 7. Artifacts

| File | SHA256 |
|---|---|
| `perf/tw20_perf_report.md` | (see verification command below) |
| `perf/progress.txt` | (see verification command below) |
| `perf/benchmark_results.csv` | (see verification command below) |

Supporting artifacts preserved in `perf/`: `solver_baseline_src.cpp`, `solver_active_x_src.cpp`, `solver_baseline`, `solver_active_x`, `binary_hashes.txt`, `build_baseline.log`, `build_active_x.log`, `verify_V_*`, `verify_KSS_*`, `verify_W_*` (logs + stderr), `bench_p{1..5}_{baseline,activex}.log` + `.time` (10 raw benchmark logs with `/usr/bin/time -v`).

Unresolved provenance limitations:
1. The pre-existing TW20 −7.86% benchmark table is UNVERIFIED (provenance points at the TW18 overlap candidate, not ActiveX); no conclusion uses it.
2. Both release binaries carry unstripped `.debug_*` metadata (standard for `-Ofast` without `strip`); this does not affect executed performance.
3. Benchmark host was heavily loaded (load ~5, low free memory); run-to-run variability dominates, so the median reduction carries wide uncertainty.
4. `--parallel` + propagation remains unverified and was excluded from this experiment.

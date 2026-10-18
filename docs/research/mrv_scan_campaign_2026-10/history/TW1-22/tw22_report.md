# TW1-22 — ActiveX Quiet-Host Retry: BLOCKED (host gate failed)

**Date:** 2026-10-16 (Pacific/Auckland)
**Status:** BLOCKED — host not quiet enough. No benchmarks run. No solver code modified. No commits, merges, or deploys. TW1-20/TW1-21 artifacts untouched.

---

## 1. Hash recheck (all match)

| Item | Expected SHA256 | Actual SHA256 | Match |
|---|---|---|---|
| Baseline source `tw20/perf/solver_baseline_src.cpp` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` | ✓ |
| ActiveX source `tw20/perf/solver_active_x_src.cpp` | `42fad94bb9cabeafc379e50b58f8e6816c0aa545a48ed178145febb15ef7bed9` | `42fad94bb9cabeafc379e50b58f8e6816c0aa545a48ed178145febb15ef7bed9` | ✓ |
| Baseline binary `tw20/perf/solver_baseline` | `79dff337875560de88f2501a602e8aeebabc26220a61197204adf910c95ebc47` | `79dff337875560de88f2501a602e8aeebabc26220a61197204adf910c95ebc47` | ✓ |
| ActiveX binary `tw20/perf/solver_active_x` | `fe8ea52f126494df8f7e90d61797c30cfb9992309e480eac65811fa2c3f15e9b` | `fe8ea52f126494df8f7e90d61797c30cfb9992309e480eac65811fa2c3f15e9b` | ✓ |
| W placements | `a7a421cde69049fcfa7fd7ee8aa71a82a4ad4c7bfc9631c04ab035d663f8b045` | (same) | ✓ |
| V placements | `dc22870d591d5c5789f4b7df8f546a36682e325474dbcb938b723afc46c100fe` | (same) | ✓ |
| KSSref placements | `9786dd438861f4668cc4b7f8f179d2b2e844426681d17c44d7375e901b1de291` | (same) | ✓ |

---

## 2. Host gate — FAILED (75 s vmstat + process snapshot)

Host: 8 logical CPUs, 11.7 GB RAM, 4 GB swap. No competing solver/benchmark processes (`pgrep` empty).

| Criterion | Requirement | Observed | Verdict |
|---|---|---|---|
| No competing solvers | none | none | ✓ PASS |
| Average CPU idle > 85% | > 85% | vmstat `id`: 45, 52, 22, 80 → **avg ~50%** | ✗ FAIL |
| 1-min load < 0.5 per CPU (< 4.0) | < 4.0 | **5.06 → 5.17** (rising) | ✗ FAIL |
| No significant swapping / memory pressure | none | **swap ~2.75–2.86 GB of 4 GB (67–70%) in use**; active swap-out (`so` up to 4131 blocks/s); free RAM only ~260–760 MB | ✗ FAIL |

Load source (desktop, not solvers): Firefox ~20–33%, OpenWork renderer/sidecar ~16–23%, gnome-shell ~8%. Raw evidence: `tw22/host_vmstat.txt`, `tw22/host_top.txt`, `tw22/host_mem.txt`.

Conditions are worse than TW1-21 (which already failed). Per instructions, benchmarking under unsuitable conditions was not attempted — a fourth noisy comparison would add nothing.

---

## 3.–5. Correctness / benchmarks / decision

None run (blocked by §2). TW1-20 standing result unchanged: correctness established, performance **RETAIN AS EXPERIMENTAL**.

To unblock: a genuinely quiet host (dedicated/headless, swap free, sustained idle >85%), or a quiet window here with desktop load closed — re-run this gate first, then the unchanged five-pair W 2.5M single-threaded propagate protocol.

---

## 6. Artifacts

| File | SHA256 |
|---|---|
| `/tmp/pentacube-bench/tw22/tw22_report.md` | (see verification command below) |
| `/tmp/pentacube-bench/tw22/progress.txt` | (see verification command below) |
| `/tmp/pentacube-bench/tw22/benchmark_results.csv` | (see verification command below) |

Supporting diagnostics in `/tmp/pentacube-bench/tw22/`: `host_vmstat.txt`, `host_top.txt`, `host_mem.txt`. No benchmark logs exist (nothing run). TW1-20/TW1-21 artifacts preserved unmodified.

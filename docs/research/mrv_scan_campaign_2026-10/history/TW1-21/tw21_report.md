# TW1-21 — Controlled ActiveX Performance Validation: BLOCKED (host gate failed)

**Date:** 2026-10-16 (Pacific/Auckland)
**Status:** BLOCKED — host not quiet enough. No benchmarks run. No solver code modified. No commits, merges, or deploys.

---

## 1. Artifact verification (TW1-20 sources/binaries reused, no rebuild)

Reports read:
- `/tmp/pentacube-bench/tw20/debug/debug_report.md` (fix verification, §3 hashes)
- `/tmp/pentacube-bench/tw20/perf/tw20_perf_report.md` (release-benchmark provenance)
- `/tmp/pentacube-bench/tw20/perf/progress.txt` (RETAIN AS EXPERIMENTAL)

Hash verification (actual, this session):

| Item | Expected SHA256 | Actual SHA256 | Match |
|---|---|---|---|
| Baseline source `perf/solver_baseline_src.cpp` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` | `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278` | ✓ |
| ActiveX source `perf/solver_active_x_src.cpp` | `42fad94bb9cabeafc379e50b58f8e6816c0aa545a48ed178145febb15ef7bed9` | `42fad94bb9cabeafc379e50b58f8e6816c0aa545a48ed178145febb15ef7bed9` | ✓ |
| Baseline binary `perf/solver_baseline` | `79dff337875560de88f2501a602e8aeebabc26220a61197204adf910c95ebc47` | `79dff337875560de88f2501a602e8aeebabc26220a61197204adf910c95ebc47` | ✓ |
| ActiveX binary `perf/solver_active_x` | `fe8ea52f126494df8f7e90d61797c30cfb9992309e480eac65811fa2c3f15e9b` | `fe8ea52f126494df8f7e90d61797c30cfb9992309e480eac65811fa2c3f15e9b` | ✓ |
| W 5×7×9 placements `/home/philip/Work/fitpolycubes/placements_W_5x7x9.txt` | `a7a421cde69049fcfa7fd7ee8aa71a82a4ad4c7bfc9631c04ab035d663f8b045` | `a7a421cde69049fcfa7fd7ee8aa71a82a4ad4c7bfc9631c04ab035d663f8b045` | ✓ |

No rebuild was necessary; originals were not touched. Had the gate passed, these exact binaries would have been used.

---

## 2. Host suitability gate — FAILED (do not benchmark)

Host: VirtualBox VM, 8 logical CPUs (Intel Core Ultra 7 155H, ~2995 MHz), 11.7 GB RAM, 4 GB swap. No competing solver/benchmark processes found (`pgrep` empty).

### Gate criteria vs measurements (135+ seconds of observation)

| Gate | Requirement | Observed | Verdict |
|---|---|---|---|
| No competing solver/benchmark processes | none | none (`pgrep -af "solver\|benchmark\|stress-ng\|sysbench"` empty) | ✓ PASS |
| Average CPU idle above 85% | > 85% | **70.88%** (60 s round 1), **65.14%** (60 s round 2); intervals as low as **42.62%** and 52.26% | ✗ FAIL |
| One-minute load below 0.5 per logical CPU (i.e. < 4.0 on 8 CPUs) | < 4.0 | 2.22 → 1.39 → **5.60** → **5.21** (spikes well above gate; rising trend) | ✗ FAIL |
| No significant swapping / memory pressure | none | **~2.7 GB of 4 GB swap in use (67%)**, only ~430–480 MB free RAM; `si/so` mostly 0 but the system is living in swap | ✗ FAIL |

Raw diagnostics preserved in `/tmp/pentacube-bench/tw21/`: `host_cpu_observation.txt`, `host_cpu_observation2.txt`, `host_freq.txt` (no cpufreq driver — frequency/throttling state unavailable), `host_top.txt` (top consumers: Firefox ~20–33%, OpenWork renderer/GPU processes, gnome-shell — desktop workload, not solvers).

Background CPU (~30–35% busy) comes from the desktop stack (Firefox with 19+ tabs, OpenWork Electron renderers, gnome-shell, system-monitor), and the 1-minute load more than tripled during observation (1.39 → 5.60). Memory pressure is structural (swap 67% full), not transient.

### Conclusion

The host fails 3 of 4 gate criteria. Per the task instructions the benchmark was **not forced to run** — a third noisy comparison would add no information beyond TW1-20's already noise-dominated result (baseline swung 13.59→23.90 s under load ~5). No benchmark processes were started; no data was silently discarded because no data was collected.

---

## 3. Benchmarks

None run (blocked by §2). No pairs, no timings, no counter comparisons to report. `benchmark_results.csv` contains the schema header and zero data rows.

---

## 4. Analysis

Not applicable — no measurements taken. TW1-20's standing result is unchanged: correctness established, performance **RETAIN AS EXPERIMENTAL** pending a quiet host.

---

## 5. Decision

**No decision on ActiveX performance can or should be made from this task — the host gate failed.**

Recommendation:
1. Re-run TW1-21 on a quiet host (or this host in a later quiet period): close Firefox/OpenWork renderer load or, better, use a dedicated headless machine; require swap mostly free and sustained idle > 85% before starting.
2. Alternatively, reduce interference sensitivity: pin the benchmark to isolated cores (`taskset`), `nice -n -20` with sudo, drop caches between runs — but only after the gate passes; controls cannot rescue a swapping host.
3. Keep the five-pair alternating protocol and the identical W 5×7×9 / 2.5M-cap / single-threaded propagate configuration unchanged so results remain comparable.

---

## 6. Artifacts

| File | SHA256 |
|---|---|
| `/tmp/pentacube-bench/tw21/tw21_report.md` | (see verification command below) |
| `/tmp/pentacube-bench/tw21/progress.txt` | (see verification command below) |
| `/tmp/pentacube-bench/tw21/benchmark_results.csv` | (see verification command below) |

Supporting diagnostics preserved in `/tmp/pentacube-bench/tw21/`: `host_cpu_observation.txt`, `host_cpu_observation2.txt`, `host_freq.txt`, `host_top.txt`.

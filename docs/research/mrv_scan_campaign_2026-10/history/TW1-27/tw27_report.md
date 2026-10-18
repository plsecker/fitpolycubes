# TW1-27 — ActiveX Final Validation: REPORT

**Outcome: REJECT (ActiveX consistently slower under test conditions)**

Date: 2026-10-17 NZDT. Host: philip-VirtualBox, 8 logical CPUs.
No solver code modified; no commit/merge/deploy; all prior artifacts preserved.

## 1. Host readiness — PASS (with caveat)

81-second epoch-verified observation (09:40:22–09:41:43 NZDT, 16 × 5s
/proc/stat deltas):

- Idle %: 80.2, 82.2, 85.7, 90.1, 90.4, 88.7, 86.1, 82.4, 86.4, 91.3,
  91.0, 90.9, 86.0, 88.4, 89.4, 87.2 → **average 87.3%** (gate >85%: PASS)
- 1-min load: 2.28 → 1.40, **every sample <4.0** (gate: PASS)
- 5-min load 1.77–1.96; MemAvailable 4.2–4.8 GB of 11.75 GB
- /proc/pressure/memory: some and full 0.00 throughout (PASS)
- Swap: ~2.9 GB occupied but stable; 1 swap-in page in 81 s, 0 swap-out
  (accumulated occupancy only: PASS per protocol)
- No competing solver/benchmark processes (PASS)

Caveat: desktop load returned mid-campaign (1-min load 3.7–9.1 during
benchmark pairs, driven by opencode sidecar, firefox, OpenWork renderer).
Readiness passed at gate time; the benchmark section flags the affected
conditions pair by pair. Memory pressure stayed zero throughout.

## 2. Artifact verification — PASS, no rebuild

| Item | Expected SHA256 | Actual | Match |
|---|---|---|---|
| Baseline source `tw18/solver_coalesced.cpp` | a4fdcf12…93278 | a4fdcf12…93278 | ✓ |
| ActiveX source `tw20/solver_active_x.cpp` (per tw20 debug report) | 42fad94b…f7bed9 | 42fad94b…f7bed9 | ✓ |
| Baseline binary `tw20/solver_baseline` | 79dff337…c95ebc47 | 79dff337…c95ebc47 | ✓ |
| ActiveX binary `tw20/solver_active_x` | fe8ea52f…f15e9b | fe8ea52f…f15e9b | ✓ |
| V placements | dc22870d… | dc22870d… | ✓ |
| KSSref placements | 9786dd43… | 9786dd43… | ✓ |
| W placements | a7a421cd… | a7a421cd… | ✓ |

Verified binaries used as-is; nothing rebuilt, all originals preserved.

## 3. Correctness gate — PASS (all three)

Single-threaded, propagation-enabled; identical CLI for both binaries
(`--connectivity --symmetry --region-prune=propagate`; `--parallel` never used):

- V 5×5×6 exhaustive: exit 0/0 — 70033 nodes, 18 sol, 34236 dead ends,
  prop 14452 (forced 42099) — full diff excl. timing IDENTICAL
- KSSref 5×5×5 cap 10M: exit 0/0 — 10000068 nodes, 0 sol, 6335178 dead,
  prop 1297394 (forced 2464552) — IDENTICAL
- W 5×7×9 cap 2.5M: exit 0/0 — 2500040 nodes, 0 sol, 1136291 dead,
  prop 564316 (forced 1525974) — IDENTICAL

Logs: `correct_V_*`, `correct_KSS_*`, `correct_W_*` (stdout + stderr).

## 4. Five paired benchmarks (W 5×7×9, 2.5M cap, sequential)

Solver-internal `Time:` used for ratios (external wall clock tracked
separately, within ~0.01–0.02 s of internal in every run).

| Pair | Order | Baseline (s) / exit | ActiveX (s) / exit | Ratio | Reduction | Load note |
|---|---|---|---|---|---|---|
| 1 | base, AX | 15.0924 / 0 | 19.8304 / 0 | 1.3139 | −31.39% | elevated (8.4→7.4) |
| 2 | AX, base | 12.7174 / 0 | 15.5944 / 0 | 1.2262 | −22.62% | moderate (4.6→5.2) |
| 3 | base, AX | 11.9230 / 0 | 18.7947 / 0 | 1.5763 | −57.63% | elevated (9.1→8.5) |
| 4 | AX, base | 14.8586 / 0 | 20.3151 / 0 | 1.3672 | −36.72% | elevated (6.3) |
| 5 | base, AX | 15.9128 / 0 | 24.2707 / 0 | 1.5252 | −52.52% | elevated (5.5→7.3) |

- Median baseline: **14.8586 s** (range 11.9230–15.9128)
- Median ActiveX: **19.8304 s** (range 15.5944–24.2707)
- Median of paired reductions: **−36.72%**
- Peak RSS medians: baseline 4396 kB vs ActiveX 4532 kB (~3%, noise)
- Correctness consistency: all 10 runs 2500040 nodes / 0 sol /
  1136291 dead ends; per-pair diffs excl. timing all IDENTICAL
- Raw logs: `bench_p{1..5}_{baseline,activex}.log` + `.time` (with
  `/usr/bin/time -v` external wall clock + peak RSS)

## 5. Analysis and decision

**REJECT.** ActiveX is consistently slower under these test conditions:
all five pairs favour the baseline (−22.62% to −57.63%), median paired
reduction −36.72%. Unlike TW1-20's noisy campaign (mixed directions),
this result is directionally unanimous — including pair 2, run under the
calmest load, at −22.62%. These are end-to-end runtimes, so ActiveX
list-maintenance and rollback costs are included; no credit is claimed
from inactive-row counts alone. Memory is a non-factor (~3% RSS delta).

Load caveat: desktop load returned during benchmarking, so absolute times
carry noise — but the paired design (alternating order, back-to-back runs)
keeps each comparison fair, and unanimity across five pairs with
alternating order is not plausibly a load artifact favouring one side.
A future quiet-host campaign could tighten the magnitude, but there is no
signal here suggesting a hidden win: the candidate is correct but slower.

Correctness (TW1-20 invariant work + §3 above) stands; this is a
performance rejection, not a correctness rejection. No runtime heuristic
was added. Do not commit, merge, deploy, or change the main solver.

## 6. Artifacts (`/tmp/pentacube-bench/tw27/`)

- `tw27_report.md` — this report
- `progress.txt` — short progress record
- `benchmark_results.csv` — 10 benchmark rows with full provenance
- `correct_V/KSS/W_{baseline,activex}.log/.err` — correctness logs
- `bench_p{1..5}_{baseline,activex}.log/.time` — raw benchmark logs

# TW1-30 — MRV-Scan Performance Validation: REPORT

**Outcome: BLOCKED (host readiness gate failed — no benchmarks run)**

Date: 2026-10-17 NZDT. Host: philip-VirtualBox, 8 logical CPUs.
No solver code modified; all TW1-29 and prior artifacts preserved;
no commit/merge/deploy.

## 1. Artifact verification — PASS

| Item | Expected SHA256 | Actual | Match |
|---|---|---|---|
| Baseline source `tw18/solver_coalesced.cpp` | a4fdcf12…93278 | a4fdcf12…93278 | ✓ |
| Candidate source `tw29/solver_mrv_scan.cpp` | 274c3796…bfb418 (per TW1-29 report) | 274c3796…bfb418 | ✓ |
| Baseline binary `tw29/solver_baseline` | 79dff337…c95ebc47 | 79dff337…c95ebc47 | ✓ |
| Candidate binary `tw29/solver_mrv_scan` | f7f9b3f8…36715715 (per TW1-29 report) | f7f9b3f8…36715715 | ✓ |
| W placements | a7a421cd… | a7a421cd… | ✓ |

Both binaries are byte-identical to the TW1-29 correctness-test
binaries. Correctness evidence reused per protocol (V 70033/18/34236,
KSSref 10000068, W 2500040, all counter-identical; 4884-line
forced-placement trace identical). No reruns needed; nothing differs.

## 2. Host readiness gate — FAIL (81 s epoch-verified observation)

Window 10:48:40–10:50:01 NZDT (16 × 5 s /proc/stat deltas, 81 s):

- Idle %: 59.6, 61.4, 60.0, 44.7, 50.8, 82.5, 86.4, 86.3, 88.6, 68.5,
  29.5, 72.4, 63.4, 35.1, 28.5, 61.7 → **average 61.2%** (gate >85%: FAIL)
- 1-min load: 6.30–8.73, **every sample >4.0** (gate: FAIL);
  5-min load 6.5–7.0
- Memory pressure: some avg10 up to 4–6, full avg10 4.77 at window start
  (significant pressure: FAIL — first campaign with non-zero full pressure)
- Swap: sustained swap-in 12–58 pages per 5 s window throughout, plus
  swap-out bursts of 2667, 388 and 2310 pages (sustained swapping: FAIL;
  this is active paging, not old occupancy)
- No competing solver/benchmark processes (PASS — the only passing gate)
- Load drivers: opencode sidecar ~17%, firefox main + content procs
  (~8–13% each), OpenWork renderer ~9%, plus kworker/kblockd block I/O
  activity consistent with the observed paging

This is the worst host state of the TW1-24–TW1-30 series for a 2%
effect: even the brief quieter spell mid-window (idle 82–89%) sits on
1-min load >6 with active swap-out. A 2% candidate-vs-baseline signal
is unresolvable here.

## 3. Correctness / benchmarks / decision

- Correctness: reused from TW1-29 (binaries unchanged) — PASS, no reruns.
- Benchmarks: **none run** per protocol. `benchmark_results.csv`
  contains headers only; no fabricated rows.
- Decision: **BLOCKED**. The ≥2% hypothesis remains untested, not
  falsified. The candidate stays RETAIN AS EXPERIMENTAL.
- Per protocol, no further readiness checks without a material change
  in host conditions.

## 4. Artifacts (`/tmp/pentacube-bench/tw30/`)

- `tw30_report.md` — this report
- `progress.txt` — short progress record
- `benchmark_results.csv` — header only (no benchmark rows)

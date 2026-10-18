# TW1-24 — Final ActiveX Performance Validation: REPORT

**Outcome: BLOCKED (host readiness gate failed — no performance runs performed)**

Date: 2026-10-17 NZDT
Host: philip-VirtualBox, 8 logical CPUs
Objective: reliable release-build comparison between verified coalesced baseline and corrected ActiveX candidate.

## 1. Executive summary

TW1-24 stopped at Phase 1 per protocol. The host was under substantial
desktop and memory load during a 75+ second observation window, and two
required readiness gates failed:

- Average CPU idle **64.3%** (gate requires >85%) — FAIL
- One-minute load **4.44–5.76** (gate requires <4.0 on this eight-CPU host) — FAIL

No solver jobs were run. No source, binary, or placement files were
verified, built, or executed. No correctness gate was attempted. No
benchmark repetitions were performed. No solver code was modified, and
all previous experiments and reports were preserved untouched.

**No performance runs were performed in TW1-24.** There are no runtime,
nodes/sec, or memory comparisons to report, and no decision on ActiveX
(REJECT / RETAIN / PREPARE) can or should be drawn from this run.

## 2. Phase 1 — Host readiness (the only phase executed)

Observation window: 2026-10-17 09:04:34–09:05:01 NZDT (16 vmstat samples
plus initial snapshot; ≥75 seconds).

| Check | Observed | Gate | Verdict |
|---|---|---|---|
| Competing solver/benchmark processes | None (pgrep solver\|benchmark\|pentacube: only idle monitor daemons) | None allowed | PASS |
| Avg CPU idle | 64.3% (samples: 82,51,75,47,72,89,65,62,50,70,50,60,60,75,66,55) | >85% | **FAIL** |
| 1-min load | 4.44–5.76 across window (start 4.99) | <4.0 | **FAIL** |
| 5-min load | 1.71 rising to 2.65 | informational | — |
| MemAvailable / total | ~4.1–4.3 GB / 11.75 GB | informational | — |
| /proc/pressure/memory | some and full avg10/avg60/avg300 all 0.00 | no significant pressure | PASS |
| Swap activity (si/so) | 6/14, 4/0, 0/0 at start; 0/0 through window | no sustained si/so | PASS (see note) |
| Major desktop consumers | firefox (+ content procs, up to 11.8% MEM), gnome-system-monitor 12.6% MEM, gnome-shell, OpenWork renderer/sidecar (transient 20–52% CPU) | informational | substantial load noted |

Swap note (per protocol): ~2.9 GB swap occupied but stable
(SwapFree ≈1223100 kB throughout; si/so 0/0 during observation; memory
pressure 0.00). This is accumulated occupancy, not active swapping, so
the memory gate is not failed on swap occupancy.

Full per-sample log: `host_diagnostics.txt` in this directory.

No processes were killed, no services stopped, no reboot, no system
configuration changed.

## 3. Phases not executed

- **Phase 2 (verify baseline/candidate):** not started. Expected hashes
  recorded here for the next attempt but nothing was verified:
  - Baseline source `tw18/solver_coalesced.cpp`: a4fdcf12…93278
  - ActiveX source (per tw20 debug report): 42fad94b…f7bed9
  - Baseline binary: 79dff337…c95ebc47
  - ActiveX binary: fe8ea52f…f15e9b
- **Phase 3 (correctness gate V/KSSref/W):** not run.
- **Phase 4 (five paired benchmarks):** not run — the CSV in this
  directory contains headers only and no benchmark rows.
- **Phase 5 (analysis/decision):** no analysis possible; no ActiveX
  decision is made in TW1-24.

## 4. Decision

**BLOCKED.** The host did not meet the controlled conditions required
for a reliable release-build comparison. This is the same failure mode
as TW1-20 (inconclusive under load) and the correct stops in TW1-21,
TW1-22, and TW1-23. Retry TW1-24 (or its successor) when the desktop is
quiescent: 1-min load <4.0 and average idle >85% sustained before
starting Phase 2.

## 5. Artifacts (this directory: /tmp/pentacube-bench/tw24/)

- `tw24_report.md` — this report
- `progress.txt` — short progress record
- `benchmark_results.csv` — header only; no benchmark rows (no runs performed)
- `host_diagnostics.txt` — full host observation log
- No correctness logs, benchmark logs, or build logs exist (no jobs run)

All prior experiments and reports preserved; no solver code modified.

# TW1-36 — Memory Recovery Verification: REPORT

**Outcome: PRECONDITION UNMET (operator cleanup not yet performed —
no readiness observation run)**

Date: 2026-10-17 NZDT, checked 13:59:09 NZDT. No solver, benchmark, or
correctness test run. All sources, binaries, manifests, and artifacts
preserved; no commit/merge/deploy.

## 1. Precondition check — FAILED

TW1-36 requires the operator to first close Firefox + content
processes, quit GNOME System Monitor, and pause unnecessary OpenWork
activity. At check time all of the following were still resident:

- firefox main process (~12.7% CPU, 8.6% MEM) plus multiple content
  processes (~6–11% MEM each, including two new short-lived ones)
- gnome-system-monitor (~5.3% CPU, 9.6% MEM / ~1.16 GB RSS)
- opencode sidecar (~14.3% CPU), OpenWork renderer (~6%)

Current state: load 5.04 (1-min), pressure some/full avg10 0.33/0.31
and falling, MemAvailable 3419 MB, swap 4095/4095 MB occupied
(**100% full, 128 kB free** — up from 99% at TW1-35). No solver or
benchmark jobs running (confirmed).

## 2. Decision: no observation run

The single TW1-36 assessment was not spent: with the full desktop
workload still resident and swap completely full, a 90 s observation
would merely re-confirm the known TW1-34/TW1-35 findings. Per the
task's stop rule ("do not repeat the check without another material
environmental change"), the correct action is to stop and report the
unmet precondition rather than burn the assessment.

No swapoff was attempted and no process was touched (per task rules).

## 3. What the operator must do before the assessment is valid

1. Close Firefox and all its content processes.
2. Quit GNOME System Monitor.
3. Pause unnecessary OpenWork/OpenCode background activity.
4. Leave the machine idle until 5-min load <2 sustained AND memory
   pressure avg10 reads 0.00 across consecutive checks.

Only then should the single 90 s TW1-36 observation run. The MRV-scan
hypothesis remains untested; the candidate stays RETAIN AS EXPERIMENTAL.

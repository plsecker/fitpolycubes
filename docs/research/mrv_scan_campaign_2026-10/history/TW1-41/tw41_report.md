# TW1-41 — Instruction-Count Comparison: REPORT

**Outcome: BLOCKED (no usable hardware counters in this VM)**

Date: 2026-10-17 NZDT. No solver launched, nothing modified, all
priors preserved.

## 1. Identities verified — PASS

All five hashes independently verified: baseline source `a4fdcf12…93278`,
candidate source `274c3796…bfb418`, baseline binary `79dff337…c95ebc47`,
candidate binary `f7f9b3f8…36715715`, W placements `a7a421cd…`.
TW1-29/37/38/39/40 reports read. Release binaries confirmed (instrumented
diagnostic binary explicitly excluded from this comparison).

## 2. Counter availability — FAIL (blocker)

- `perf` 7.0.14 present, but `perf_event_paranoid=4`.
- `perf stat -e instructions,branches,branch-misses,cache-references,cache-misses true`
  → "No supported events found."
- Software events (`task-clock,context-switches,page-faults`, `cpu-clock`)
  → same refusal. No event class is measurable.
- No valgrind/callgrind installed (and installing is out of scope).
- No PMU flags visible in `/proc/cpuinfo`.
- Lowering `perf_event_paranoid` requires privilege/host access and
  system-configuration change — explicitly out of scope for this task.

Per protocol: no fallback to wall-clock comparison under loaded
conditions. Zero solver invocations made.

## 3. Safety preflight / paired runs / analysis

Not reached — stopped at Phase 2 per protocol. No `instruction_counts.csv`
rows fabricated; the CSV contains headers only.

## 4. Decision

**BLOCKED.** Reliable per-process instruction counts cannot be collected
safely in this VM. The release-performance hypothesis remains untested.
Evidence to date: correctness (TW1-29/37), codegen deltas (TW1-38),
workload exposure 2.8M avoided visits + 180k discarded pushes at 250k
nodes (TW1-40) — none of which is a runtime claim.

## 5. Artifacts (`/tmp/pentacube-bench/tw41/`)

- `tw41_report.md`, `progress.txt`, `instruction_counts.csv` (headers
  only), `results.json` (blocked record)

# Campaign History — MRV-Scan Optimisation (TW1-15 → TW1-41)

Chronological record. Outcome keywords: ADOPTED / REJECTED / RETAIN AS
EXPERIMENTAL / BLOCKED. The MRV-scan candidate was never measured faster;
"supports the hypothesis" (TW1-38/40) means workload-exposure/codegen
evidence, not a runtime result.

## TW1-15 — Degree-delta coalescing: ADOPTED (with provenance limits)

Coalesced per-row degree updates into a single transaction
(`DegreeDeltaScratch` + `apply_row_removals_coalesced()`). Correctness:
V/KSSref counters match, forced traces match, sanitizers clean. V-benchmark
audit CSV archived. KSS single-run comparison promising but not statistically
validated. Source-to-binary provenance UNVERIFIED (no build log retained).
The coalesced source (`a4fdcf12…`) became the campaign baseline for
everything after. (TW1-16 below is its replication.)

## TW1-16 — Coalescing replication: ADOPTED (median +3.87% vs TW1-13)

KSSref 10 paired runs, all CSV values validated against raw logs: all 5
pairs favour coalesced (reductions 0.75%–7.57%, median 3.87% internal time).
Report, CSV, and 10 raw bench logs archived under `history/TW1-15/tw16/`.

## TW1-17 — Profiling on coalesced source: COMPLETE (event counts only)

Fresh gprof (`-pg -O2`) on the exact coalesced source, W 5×7×9:
`choose_best_column` 0.56 s / 2.27M calls; `Propagator::run` 1.65 s / 957K
calls; `search` self 4.61 s (largest bucket). Older profiles on pre-coalesced
TW1-13 (degree-hotpath, mrv-selection, post-packed-one-deg) classified
APPLICABLE to TW1-13 only; heap-based mrv-validation profile REJECTED as
unrelated. No CPU-cycle attribution; `perf` blocked (paranoid=4).
TW1-16 replication validated (10/10 CSV rows match logs).

## TW1-18 — Row-overlap graph: REJECTED (median −7.86%, slower)

Precomputed row-overlap CSR for the propagator conflict scan. Correctness
passes (V/KSSref/W counters identical). W 5×7×9 five paired runs: ALL slower
(−4.61% … −23.82%, median −7.86%). Cause: high graph degree (126.7 avg for W)
+ worse cache locality than the CSR traversal; early exits undercut the
precomputation win. Source archived in `sources/rejected/`.

## TW1-19 — Propagation-cost investigation: COMPLETE (avenue closed)

Thread-local phase counters on coalesced source, W 5×7×9: 164.9M inactive
row skips (71.2% of conflict scans) — but TW1-18/20/27 later proved that
eliminating them via maintained indexes costs more than it saves.
`not_forced_skips`/`starved_*` = 0 (dead but negligible branches); deg-copy
1.21 GB total (~60 ms of ~19 s, too small to target). Instrumented source
snapshot archived. Provenance limitation: instrumented-build evidence only.

## TW1-20 — Dynamic ActiveX index: REJECTED (design; −7.86% median in-report)

Doubly-linked active-row index maintained across placement/rollback.
Correctness passes; cost estimate already predicted failure (3.6B pointer
writes vs 231.7M scan entries). In-report W benchmark: median −7.86%.
Debug evidence (fix verification, invariant checks, forced traces) and the
release-benchmark evidence (5 pairs + verify logs) archived under
`history/TW1-20/debug/` and `history/TW1-20/perf/`. Candidate source
(`42fad94b…`) archived in `sources/rejected/`.

DISCREPANCY (preserved, not resolved): the TW1-20 report's §4.1 table lists
the candidate binary hash as `d2146502…` — identical to the TW1-18 overlap
binary hash, which is impossible for distinct sources. The actual
`solver_active_x` binary on disk hashes to `fe8ea52f…` (matching TW1-21's
record). The report's benchmark table also reproduces TW1-18's numbers
exactly. Treat TW1-20's in-report benchmark table as unreliable; the
authoritative ActiveX rejection is TW1-27 (below), whose CSV was validated
row-by-row against raw logs.

## TW1-21/22/23/24/25/26 — Host-gate blocks: BLOCKED (no data)

Six successive readiness failures on philip-VirtualBox (idle 50–77% vs >85%
gate; 1-min load routinely >4.0; swap 67–70% occupied). No benchmarks run;
binaries re-verified but untouched. TW1-21-retry additionally records that
no alternative quiet host was reachable. Lesson institutionalised: ≥75 s
epoch-verified windows, fail-closed harness (built TW1-31/32).

## TW1-27 — ActiveX final validation: REJECTED (median −36.72%)

Gate PASSED at check time (avg idle 87.3%, load <4.0, zero pressure) but
desktop load returned mid-campaign (logged per pair). W 5×7×9 five
alternating pairs, solver-internal time: ALL favour baseline (−22.62% …
−57.63%, median −36.72%). 10-row CSV validated against raw logs; per-pair
bench + correctness logs archived. ActiveX permanently rejected for
performance; its traversal-order-independence evidence (counter-identical
correctness) stands as propagator-semantics documentation. This is the
TW1-20/27 rejection evidence required by the task.

## TW1-28 — Close ActiveX, select next target: DECISION RECORD

ActiveX rejection confirmed from TW1-27 evidence. Baseline identity
re-verified (`a4fdcf12…`). Next target selected WITHOUT implementing:
MRV-scan early-exit + single-pass forced collection in `choose_best_column`
(0.56 s / 2.27M-call hotspot; no-early-exit + double-collection waste
identified by source reading). Falsifiable ≥2% hypothesis + correctness-test
and paired-benchmark plan specified. No code changed.

## TW1-29 — MRV-scan implementation: RETAIN AS EXPERIMENTAL

Candidate (`274c3796…`, 39-line diff): `for_each_until` with early stop at
first degree-0 column + removed always-discarded scan pushes; authoritative
`one_deg_set` collection unchanged. Built `-Ofast -march=native -flto`
(baseline binary reproduces `79dff337…`; candidate `f7f9b3f8…`).
Correctness PASSES fully: V 70033/18/34236, KSSref 10000068, W 2500040 —
all IDENTICAL; 4884-line forced trace IDENTICAL. Host gate FAILED
(avg idle 60.6%, load 6–11): stopped before benchmarking per protocol;
CSV header-only. Hypothesis untested, not falsified.

## TW1-30 — Validation attempt: BLOCKED

Binaries byte-identical to TW1-29 (correctness reused, not rerun). Gate
FAILED worse than TW1-29 (avg idle 61.2%, active swap-out bursts 2667/388/
2310 pages, first non-zero full-pressure of the series). No benchmarks run.

## TW1-31 — Fail-closed benchmark harness: TOOLING READY

`bench_runner.py` (~700 lines, stdlib only): pinned-SHA256 preflight, ≥75 s
epoch-verified gate, evidence binding, dry-run, sequential paired executor,
fixed-schema CSVs, analyzer, exit codes 0/2/3/4/5/6. 23 self-tests pass
(no real solver). Manifest pins the TW1-29 pair config with all hashes and
expected counters. Archived under `benchmarking/` (+ TW1-31 originals as
`benchmark_manifest_tw31.json` / `README_tw31.md`).

## TW1-32 — Harness hardening: READY FOR CONTROLLED BENCHMARK

Safety audit of all 1009 lines; fixed dead `vals` loop, single-sourced
thresholds, added 20 s inter-pair health checks with `host_stop.json`,
`/usr/bin/time -v` peak-RSS capture. 33/33 self-tests pass (no real solver).
Live safe-mode verification (preflight/evidence/dry-run) green. Hypothesis
still untested; no performance claim.

## TW1-33 — Benchmark campaign: BLOCKED (0 of 5 pairs)

Harness verified (33/33 re-run), manifest re-hashed, preflight 5/5 +
evidence 8/8 + dry-run green. 75 s gate FAILED on all four axes (idle
73.9%, load ≥4.0, pressure spike 10.74, swap-out bursts 5017/6379/3700).
Exit 4, ZERO solvers launched. `preflight.json` + `readiness.json` archived.

## TW1-34 — Contention diagnosis: REMEDIATION PLAN READY

Read-only. 102 s observation: avg idle 61.8%, steal 0.0% (no VBox CPU
starvation), two live paging storms (multi-thousand-page swap-out bursts).
Verdict: a few desktop apps dominate (category A); episodic paging is a real
timing-variability source. Ranked plan: quiet window → shrink desktop
footprint (quit system-monitor!) → host-level RAM/vCPU or headless move.
No process touched; no benchmark attempted.

## TW1-35 — Recovery verification: NOT READY

Calm pre-check (5-min load <2) collapsed mid-window: idle 87% → 17–27%,
load 1.63 → 9.69, pressure 0 → 18.60, sustained swap-in + multi-thousand
swap-out bursts. Same paging-storm signature destroys a window that began
quiet. Lesson: calm 5-min load does not predict the next 80 s on this host.

## TW1-36 — Memory recovery check: PRECONDITION UNMET

Operator cleanup (close Firefox, quit system-monitor, pause background work)
not performed — full desktop resident, swap 100% full. The single 90 s
assessment correctly NOT spent; no observation run. Stop rule honoured.

## TW1-37 — Differential tests: PASS (3151/3151, normal + ASan/UBSan)

Direct-production test TU (real `for_each_until`/`choose_best_column`/
`one_deg_set`, independent oracle, search never launched): packed iteration,
16 targeted MRV/tie-break states, forced collection, aliasing bounds,
exhaustive n=3 (64 states) + 3000 seeded states. Zero sanitizer findings.
Historical full-search evidence re-verified, not rerun. Archived under
`tests/` with one portable adaptation (relative include path).

## TW1-38 — Compiled-code inspection: SUPPORTS HYPOTHESIS (not a benchmark)

Read-only objdump/nm/size on release binaries: early-stop branch real
(`test/je` on new-minimum path only); scan-region degree-1 stores + 2
realloc slow paths gone from hot loop (calls 3→1, all cold paths);
`choose_best_column` −45 disassembly lines (−17%), text −208 bytes;
tie-break intact (ascending traversal). Facts established; runtime magnitude
explicitly NOT established — "operation counts alone prove nothing about
speed; the five-pair W benchmark remains the arbiter."

## TW1-39 — Workload-exposure instrumentation: DIAGNOSTIC READY

`solver_mrv_scan_diagnostic.cpp` (candidate + guarded counters only;
absent without `-DMRV_SCAN_DIAGNOSTICS`, verified): 12 counters for calls,
visits, zero-hits/positions, exit histogram, avoided tail (exact via extra
packed pass, diagnostic build only), discarded pushes, authoritative forced,
max visits. 12/12 counter tests pass (+ASan/UBSan clean). Workload runner
script prepared but NOT executed here. Counters measure exposure, never
speedup.

## TW1-40 — Bounded diagnostic: WORTH RELEASE BENCHMARK (prioritisation only)

Single 250k-node instrumented W run (exit 0, no swap during run): 227239
MRV calls, 14.75% zero-hit, mean first-zero position 63.6, 2.8M avoided
visits (8.6% of visited), 180k discarded pushes, 83% of exits skip 6+
columns. Both TW1-29 mechanisms engage on real search states — but per-call
savings are small, so this is exposure evidence, NOT a runtime percentage.
Decision: preserve the candidate for the next controlled comparison.

## TW1-41 — Hardware-counter comparison: BLOCKED (VM permissions)

`perf_event_paranoid=4`; NO event class measurable (hardware, software, PMU
all refused); no valgrind; lowering paranoid out of scope. Zero solver
invocations; CSV header-only. Release-performance hypothesis remains
untested. Evidence to date: correctness (TW1-29/37) + codegen (TW1-38) +
exposure (TW1-40) — none of which is a runtime claim.

## Next planned work

- MRV-scan remains experimental; the controlled five-pair release benchmark
  (TW1-32 harness, W 5×7×9 2.5M cap, ≥2% hypothesis) has NOT completed.
- The current desktop (philip-VirtualBox) is unsuitable under all readiness
  measurements TW1-21→TW1-36; swap pressure and desktop bursts invalidate
  2%-scale comparisons there.
- A new VM may be used IF it becomes accessible AND passes the harness gate
  (≥75 s, idle >85%, load <4.0, zero pressure, no sustained swapping) —
  then: rebuild both binaries natively, re-verify hashes + correctness gate,
  run the five pairs, analyze. Do not mistake codegen/exposure evidence for
  performance results.

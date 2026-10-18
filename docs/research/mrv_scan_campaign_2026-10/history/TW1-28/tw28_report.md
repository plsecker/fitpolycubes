# TW1-28 — Close ActiveX, Select Next Optimisation: REPORT

**Recommendation: reject ActiveX permanently; next target = MRV-scan
early-exit + single-pass forced collection in `choose_best_column`
(no implementation yet).**

Date: 2026-10-17 NZDT. No solver code modified; no commit/merge/deploy;
no worktrees changed; all prior artifacts preserved.

## 1. ActiveX rejection evidence (TW1-27, verified)

Artifacts read and confirmed present:
- `/tmp/pentacube-bench/tw27/tw27_report.md` — outcome REJECT
- `/tmp/pentacube-bench/tw27/progress.txt` — matches report
- `/tmp/pentacube-bench/tw27/benchmark_results.csv` — 10 rows inspected:
  every row 2500040 nodes / 0 solutions / 1136291 dead ends; internal
  times reproduce the reported table exactly.

Paired results (W 5×7×9, 2.5M cap, solver-internal `Time:`):
pair1 −31.39%, pair2 −22.62%, pair3 −57.63%, pair4 −36.72%,
pair5 −52.52%. Median baseline 14.8586 s, median ActiveX 19.8304 s,
median paired reduction −36.72%. All five pairs favour the baseline
with alternating order, including the calmest-load pair.

**Conclusion recorded: ActiveX is rejected for performance.** Its
correctness results (V/KSSref/W counter-identical, TW1-20 invariant
checks, forced-placement traces) remain useful evidence that the
propagator's kill-set/degree semantics are traversal-order independent —
but the dynamically maintained linked-list design must not be merged,
deployed, or benchmarked again. The candidate source
(`tw20/solver_active_x.cpp`, 42fad94b…) and binary (fe8ea52f…) are
preserved untouched for the record, not for reuse.

## 2. Baseline identity — verified

`/tmp/pentacube-bench/tw18/solver_coalesced.cpp` hashes to
`a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278`
— matches expected. This exact file (2312 lines) is the experimental
baseline. Other files named `solver.cpp` / `solver_coalesced.cpp`
elsewhere were not assumed interchangeable; the inspected source is the
tw18 file above.

## 3. Optimisation history reviewed (TW1-15 → TW1-27)

| Experiment | Outcome | Lesson for next selection |
|---|---|---|
| Degree-delta coalescing (TW1-15/16) | Adopted into baseline (median +3.87% vs TW1-13) | Baseline already contains it; stays |
| Packed active-column enumeration (TW1-7/8) | Implemented | Already in baseline; excluded |
| Packed one_deg_set variants | Implemented/tested | Already in baseline; excluded |
| Indexed heap MRV (TW1-11) | Rejected (5.86× slower on V) | Excluded |
| Bucket MRV | Excluded by constraints | Excluded |
| Degree-update inlining | Rejected as non-distinct | Excluded |
| Trail-SoA | Excluded by constraints | Excluded |
| Row-overlap graph (TW1-18) | Rejected (median −7.86%) | Excluded; CSR locality beats precomputation |
| Dynamic ActiveX lists (TW1-20/27) | **Rejected (median −36.72%)** | Excluded; maintenance cost >> scan savings |
| TW1-21–26 host-gate blocks | No data | Process lesson only: verify ≥75 s windows |

Evidence classification used below: only measurements on the exact
coalesced source count as release/instrumented evidence — TW1-17 gprof
on coalesced (`-pg -O2`, W 5×7×9) and TW1-19 thread-local counters on
coalesced (`-O2`, W 5×7×9). Older profiles (degree-hotpath, mrv-selection,
post-packed-one-deg) are on the pre-coalesced TW1-13 source and do not
apply; the rejected heap profile is explicitly not used.

Applicable evidence on the coalesced source:
- TW1-17 gprof: `choose_best_column` 0.56 s / 2.27M calls; `Propagator::run`
  1.65 s / 957K calls; `search` self 4.61 s (largest bucket).
- TW1-19 counters: 164.9M inactive-row skips (71.2% of conflict scans) —
  but TW1-18/TW1-20/TW1-27 proved that eliminating them via maintained
  indexes costs more than it saves. This avenue is closed.
- TW1-19: `not_forced_skips` = 0, `starved_deg0` = 0, `starved_no_row` = 0
  (dead checks, but each is a single predictable branch — negligible).
- TW1-19: deg-copy 1.21 GB total (~60 ms of ~19 s) — too small to target.

## 4. Proposed next optimisation (NOT implemented)

### Target: MRV-scan early-exit + single-pass forced collection

**Exact source location:** `choose_best_column`, lines 553–595 of
`/tmp/pentacube-bench/tw18/solver_coalesced.cpp`.

**Observed cost and evidence:**
- TW1-17 gprof on the exact coalesced source: `choose_best_column`
  0.56 s over 2.27M calls on W 5×7×9 — a real, measured, non-trivial
  bucket (3.7% of profiled non-instrumentation time), called once per
  search node plus twice more per colour-prune rejection (§3 paths at
  lines 1394, 1427).
- Source inspection shows two avoidable inefficiencies (not yet
  implemented — verified by reading lines 562–594):
  1. **No early exit on degree 0.** The packed `for_each` has no break
     mechanism; the code comment at lines 579–582 admits it scans all
     remaining active columns even after `min_rows` reaches 0. A
     degree-0 column forces `best_col` handling at line 1466
     (`min_rows == 0` → dead end) regardless of what follows, so every
     subsequent column visit is wasted work.
  2. **Double forced-column collection.** Lines 572–574 push degree-1
     columns into `forced_out` during the scan, then lines 587–592
     `clear()` that work and re-collect from `one_deg_set` — the scan's
     pushes are always discarded when `forced_out` is requested. One of
     the two passes is pure waste on every propagate-enabled node.

**Proposed algorithmic change (design only):**
- Add an early-exit path to the packed active-column iteration (or a
  bounded variant of `for_each`) so the MRV scan stops as soon as
  `min_rows == 0`.
- Collect forced columns in exactly one pass: either keep the scan's
  degree-1 pushes and drop the `one_deg_set` re-collection, or drop the
  scan's pushes and keep the `one_deg_set` pass (preferred if
  `one_deg_set` iteration is cheaper — to be decided at implementation
  time, not here).

**Why it may improve performance:** it removes pure-waste visits inside
an already-measured 0.56 s / 2.27M-call hotspot with zero new data
structures, zero per-placement maintenance, and zero rollback logic —
the exact opposite of the failed ActiveX/overlap approaches, whose
maintenance costs exceeded their scan savings. Savings scale with node
count on every workload and flag combination.

**Correctness invariants and risks:**
- Early exit is safe iff degree-0 handling downstream depends only on
  `min_rows == 0` / `best_col`, not on a fully populated `deg_out` /
  `forced_out`. Callers at 1394/1427 pass no `deg_out`/`forced_out`
  (only `mr_min`) — safe. The line-1454 caller passes both buffers:
  `deg_out` (`g_deg.data()`) is written per-visited-column at line 570,
  so early exit would leave `deg_out` partially unwritten — the
  implementation must establish whether the propagator reads `deg_out`
  entries for unvisited columns (it owns its working copy; to verify)
  or restrict early exit to the no-buffer callers first.
- `forced_out` single-pass choice must preserve the exact set the
  propagator seeds from (TW1-19: queue behaviour validated by
  `DEBUG_COMPARE` traces — rerun them).
- Risk is low: no persistent state, no ordering assumptions, no
  concurrency interaction (thread-local `prop_forced` unchanged).

**Falsifiable performance hypothesis:** the change reduces W 5×7×9
(2.5M cap) solver-internal runtime by ≥2% vs the coalesced baseline
without changing any deterministic counter (nodes, solutions, dead ends,
propagation rejections, forced counts, histograms).

**Required correctness tests (before any benchmark):**
1. V 5×5×6 exhaustive — identical counters + full diff excl. timing.
2. KSSref 5×5×5, 10M cap — identical counters.
3. W 5×7×9, 2.5M cap — identical counters.
4. `DEBUG_COMPARE=1` forced-placement trace on V — identical `D` lines.

**Fair paired benchmark plan:** five sequential alternating pairs on
W 5×7×9 (2.5M cap), same placement file/flags/binaries-except-candidate,
internal vs external timings kept separate, peak RSS per run, host
readiness gate (≥75 s epoch-verified: idle >85%, 1-min load <4.0
throughout, zero memory pressure) with per-pair load logging; stop and
flag if the host degrades.

**Host-readiness requirements:** same TW1-27 gate; do not benchmark on a
loaded desktop (TW1-21–26 lesson).

## 5. Smallest additional measurement (optional, cheap)

If the ≥2% hypothesis needs tightening before implementation: one
`-O2` instrumented run on W 5×7×9 counting (a) MRV-scan column visits
occurring after `min_rows` first reaches 0, and (b) `forced_out` pushes
discarded by the clear-and-recollect. This is a counter-only build of
the exact baseline (no algorithmic change, ~10% overhead class per
TW1-19) — not an expensive experiment.

## 6. Artifacts

- `/tmp/pentacube-bench/tw28/tw28_report.md` — this report
- `/tmp/pentacube-bench/tw28/progress.txt` — short progress record

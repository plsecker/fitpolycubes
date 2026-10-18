# TW1-39 — MRV-Scan Workload-Impact Diagnostics: REPORT

**Outcome: DIAGNOSTIC READY FOR REVIEW**

Date: 2026-10-17 NZDT. No production search, benchmark, or readiness
check run. Production sources and all release binaries untouched
(mtimes/hashes confirm). All prior artifacts preserved.

## 1. Sources verified (Phase 1)

Baseline `a4fdcf12…93278` ✓, candidate `274c3796…bfb418` ✓, TW1-28/29/
37/38 reports read, codegen summary confirmed (early-stop branch real,
scan-region pushes absent, callbacks inlined). `choose_best_column`
re-inspected in the actual candidate source.

## 2. Diagnostic design (Phase 2)

`solver_mrv_scan_diagnostic.cpp` (copy of the candidate + guarded
blocks only): `MrvScanDiagnostics` counters for all 12 required
metrics — calls, visited, zero_calls, zero_pos_sum, exit histogram
(buckets min(v,7)), no_zero_calls, avoided_tail (exact via one extra
packed pass per call, diagnostic build only), discarded_pushes
(pre-exit degree-1 visits), authoritative_forced, max_visits.
Compile-time-guarded by `MRV_SCAN_DIAGNOSTICS`; verified absent from
plain preprocessed output (0 references). Overhead documented; counts
measure exposure, never speedup.

## 3. Semantics preserved (Phase 3)

Counters are increments + one read-only packed pass; selection,
tie-break, degrees, one_deg_set, forced order, dead ends, propagator,
and search results untouched. Branch structure identical except the
counter increments (documented). Files distinguished: production
source / instrumented source / instrumented binary
(`solver_mrv_scan_diagnostic`, clearly named, TW1-39 only).

## 4. Tests (Phase 4): 12/12 pass, direct production TU

`mrv_scan_diagnostic_test.cpp` includes the real instrumented TU with
main renamed (TW1-37 file untouched) and validates every counter
against the independent oracle on cases A–J plus two single-column
extras: selection, call/visit/exit-position/av avoided/discarded/
authoritative counts, and post-call state invariance. Deterministic;
failing state printed.

## 5. Builds (Phase 5)

`g++ 13.3.0`: normal `-O2` and ASan/UBSan `-O1 -g` test builds pass
12/12 with zero sanitizer findings; full diagnostic solver binary
builds clean (`07ab1f93…`). Only synthetic tests run. Hashes, commands,
and logs retained.

## 6. Future workload run (Phase 6)

`run_workload_diagnostic.sh` (NOT executed): hash preflight (incl.
`MRV-DIAG` binary marker check), fresh-dir refusal, single W 5x7x9
2.5M instrumented run with logs + exit status, explicit
not-for-release-comparison marking. Gated on operator decision after a
passing readiness gate; never auto-added to any campaign.

## 7. Interpretation rules (Phase 7)

STATIC (TW1-38 codegen deltas) vs SYNTHETIC (12/12 counter tests here)
vs WORKLOAD (not collected — no search run) vs PERFORMANCE (unresolved
— no paired benchmark). Counters cannot prove a runtime percentage.
High avoided_tail/discarded_pushes would strengthen the ≥2% hypothesis;
near-zero would weaken it; the five-pair benchmark still decides.

## 8. Artifacts (`/tmp/pentacube-bench/tw39/`)

Diagnostic source, diagnostic test, both runners, results JSON, counter
definitions, future-run README, build/test/sanitizer logs and outputs,
this report, progress file. Full hashes in verification step.

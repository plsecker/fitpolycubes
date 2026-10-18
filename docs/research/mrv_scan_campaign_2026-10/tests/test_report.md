# TW1-37 — MRV-Scan Differential Tests: REPORT

**Outcome: DIFFERENTIAL TESTS PASS (3151/3151 assertions, normal and
ASan/UBSan builds; no production search launched)**

Date: 2026-10-17 NZDT. No solver implementation code modified; no
production search run; no benchmark; no host-readiness check. All prior
artifacts preserved.

## 1. Implementation verified (Phase 1)

- Baseline `tw18/solver_coalesced.cpp` = `a4fdcf12…93278` ✓
- Candidate `tw29/solver_mrv_scan.cpp` = `274c3796…bfb418` ✓ (matches
  TW1-29 record; diff is exactly the 39-line intended change, no other
  delta)
- Audited: `PackedActiveCols` (init sets all bits; `clear_bit`/`set`
  maintain; `for_each`/`for_each_until` ascending ctz order),
  `choose_best_column` (3 call sites: 2 colour-prune with nullptr
  buffers, 1 main with `g_deg.data()` + `&prop_forced`), `one_deg_set`
  maintenance via `mrv_update_one_deg` on every transition, zero-degree
  dead-end return before `prop_forced` is read (line ~1485 vs ~1532).

## 2. Approach: DIRECT production testing (Phase 2)

The test TU includes the actual production source with `main` renamed
(`#define main production_main_disabled`), driving the real
`for_each_until`, `choose_best_column`, `mrv_update_one_deg`, and
`one_deg_set`. The oracle is an independent plain ascending scan written
from the reference semantics — not a copy of candidate logic. The
search loop is never launched. One test-harness bug found and fixed
during development (my `make_state` omitted `clear_bit` for inactive
columns; production `init()` sets all bits — the tests caught my error,
not a production bug).

## 3. Coverage (Phase 3): 3080 states + unit checks = 3151 assertions

- A. Packed iteration (7 tests): empty, single, ascending across words,
  stop first/middle/last/never, 63/64 + 127/128 boundaries, partial
  final word, cleared/padding bits never yielded, until(false)==for_each.
- B. MRV/tie-break (16 targeted states): min first/middle/last, ties,
  zero first/middle/last/multi/all, inactive-zero ignored, empty,
  single, all-one, zero-plus-forced, ones-around-min — candidate matches
  reference incl. lowest-index zero tie-break.
- C. Forced collection: empty/single/multi, inactive deg-1 excluded,
  complete set on the zero path, `one_deg_set` ascending regardless of
  insert order, erase paths + size.
- D. Aliasing: `g_deg.data()` self-copy no-op verified; nullptr path;
  distinct-buffer bound documented (visited prefix written, trailing
  tail untouched only after degree-0 exit; forced still complete).
- E. Exhaustive n=3 (64 states: sum of 3^popcount) + 3000 seeded
  pseudorandom states (1–200 cols, multi-word, forced boundaries),
  seed 20261017 printed on failure.

## 4. Sanitizers (Phase 4)

`g++ -O1 -g -fsanitize=address,undefined`: builds clean, 3151/3151 pass
with zero ASan/UBSan findings — no OOB, no bad word access, no
non-termination, no skipped/duplicated columns. Sanitizer binaries used
for correctness only.

## 5. Historical evidence (Phase 5) — re-verified, not rerun

V 70033/18/34236, KSSref 10000068, W 2500040 logs + 4884-line forced
traces (byte-identical `67985dba…`) all re-hashed ✓; binaries
`79dff337…`/`f7f9b3f8…` unchanged. Status: verified full-search
evidence (TW1-29) + new synthetic differential evidence (this task);
performance hypothesis still untested.

## 6. Limitations (Phase 6)

- Synthetic states drive MRV functions directly; they do not reproduce
  full-search degree trajectories (covered by TW1-29 full-search logs).
- `deg_out`-distinct-buffer callers: only the visited-prefix bound is
  tested; production currently always aliases or passes nullptr.
- Future risks: new `deg_out` storage, iteration-order change, forced
  consumption before the dead-end check, `one_deg_set` maintenance
  drift, assuming incomplete `forced_out` is always harmless.
- Recommended permanent regression: keep this TU (it compiles against
  the production source with main renamed) and run it on any MRV touch.

## 7. Artifacts (`/tmp/pentacube-bench/tw37/`)

- `mrv_scan_differential_test.cpp` — direct-production test TU
- `run_tests.sh` — strict-shell runner (exit non-zero on failure)
- `test_results.json` — machine-readable results
- `test_output.txt`, `asan_output.txt`, `build_normal.log`, `build_asan.log`
- `test_report.md` (this file), `progress.txt`

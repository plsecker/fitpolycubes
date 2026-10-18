# TW1-38 — MRV-Scan Static Codegen Audit: REPORT

**Conclusion: CODEGEN SUPPORTS THE OPTIMISATION HYPOTHESIS**

Date: 2026-10-17 NZDT. Static inspection only: no solver executed, no
benchmark, no readiness check, no source modified, no binaries rebuilt
(mtimes confirm read-only access), no commit/merge/deploy.

## 1. Identities verified (Phase 1)

All hashes independently re-computed and matching: baseline source
`a4fdcf12…93278`, candidate source `274c3796…bfb418`, baseline binary
`79dff337…c95ebc47`, candidate binary `f7f9b3f8…36715715`. Compiler
`g++ 13.3.0` (matches TW1-29 build record). Prior reports read
(TW1-28/29/37). Provenance note: filenames alone do not prove the
binaries were built from these sources — but the fresh TW1-29 build
reproduced the baseline hash exactly, and the candidate binary is the
byte-identical file from the passing correctness campaign.

## 2. Exact diff (Phase 2) — 39 lines, three regions only

1. `PackedActiveCols::for_each_until()` added (new early-stop iterator;
   identical ascending word/bit traversal as `for_each`).
2. MRV scan uses `for_each_until`, returning true at the first
   degree-0 column (unbeatable minimum; ascending order preserves the
   lowest-index tie-break).
3. Scan's degree-1 `forced_out` pushes removed (they were always
   `clear()`ed before the authoritative `one_deg_set` re-collection).

## 3. Release-binary inspection (Phase 3) — read-only objdump/nm/size

- Both binaries contain `choose_best_column…[clone .isra.0]` at the same
  address (0x11de0); `for_each`/`for_each_until` have no standalone
  symbols — fully inlined into the caller. No function-pointer or
  `std::function` dispatch anywhere in the hot loops (all `call`s are
  direct: `_M_realloc_insert`, `__tls_init`, `__stack_chk_fail`).
- Function body: baseline 260 disassembly lines vs candidate 215
  (−45 lines, −17%). Text sections: 97060 vs 96852 bytes (−208).
- **A. Iteration:** both use `tzcnt`+`blsr` packed-bit loops with the
  callback inlined. The candidate's early-stop is a real conditional
  branch: `test %edx,%edx` / `mov` / `je 11ee5` (scan-exit) inside the
  new-minimum path — reached only when a new minimum of exactly 0 is
  found, then control leaves the word/bit loops for the shared epilogue.
- **B. Zero exit:** the exit jumps to the normal scan-completion path
  (epilogue at 11ee0/11ee5: stack check, return `best_col`), so
  post-scan work is preserved; ascending traversal guarantees the first
  zero found is the lowest-index one — tie-break intact.
- **C. Forced collection:** baseline hot loop contains the degree-1
  fast-path push sequence (`cmp $0x1` → inline store + size bump at
  11ebe–11ec8, with two `_M_realloc_insert` slow-path call sites at
  12068/12081 reachable from the scan). The candidate hot loop has no
  degree-1 compare and no scan-region realloc call — the only remaining
  `_M_realloc_insert` site (12018) belongs to the `one_deg_set`
  re-collection loop, which is retained verbatim. The authoritative
  collection survives; the discarded work is gone.
- **D. Quality:** no new calls introduced by the candidate (6 call
  instructions vs baseline 8; hot-loop calls 3 → 1, all cold
  realloc/TLS paths). No extra branches on the common path — the added
  `test/je` executes only when a new minimum is adopted.

## 4. Isolated assembly (Phase 4) — not required

The `-Ofast -march=native -flto` release binaries yielded complete,
attributable `choose_best_column` bodies, so no separate `-S` build was
generated. No flag deviations to document; no binaries linked or run.

## 5. Static analysis (Phase 5)

- Zero-degree exit: one extra `test/je` on the new-minimum path buys
  skipping all remaining active columns whenever a zero is found. What
  is unavailable statically: how often a zero is present and how early
  it appears (workload-dependent; TW1-19's `not_forced_skips=0` suggests
  zeros are uncommon on W — the exit is cheap insurance, not the main
  effect).
- Forced collection: the per-visited-column `cmp $0x1` + inline
  store/size-bump and two realloc slow paths are eliminated from the
  scan; the `one_deg_set` pass remains. The source simplification
  survives compilation verbatim.
- Facts vs estimates: codegen facts (branch exists, stores gone, calls
  3→1 in hot loop, −208 text bytes) are established; any runtime effect
  magnitude is not — the eliminated work is a predictable branch plus
  mostly-non-taken stores, consistent with a small (low-single-digit %)
  improvement, which is exactly why the hypothesis is ≥2% and must still
  be measured.

## 6. Evidence gaps (Phase 6)

Established: source + differential correctness; compiled control flow
and instruction deltas. Not established: dynamic zero-hit rates,
iteration savings, cache/branch-predictor behaviour, elapsed time.
The TW1-27 ActiveX slowdown is not used as evidence here. Operation
counts alone prove nothing about speed — the five-pair W benchmark
remains the arbiter.

## 7. Artifacts (`/tmp/pentacube-bench/tw38/`)

- `source.diff` (39 lines), `fn_base.txt` / `fn_cand.txt` (bounded
  function bodies), `dis_base.txt` / `dis_cand.txt` (full objdump),
  `codegen_summary.json`, `tw38_report.md`, `progress.txt`

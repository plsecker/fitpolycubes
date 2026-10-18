# Archive Report — what was archived, excluded, and why (TW43)

Source machine: philip-VirtualBox. Originals: `/tmp/pentacube-bench/`
(untouched — all files COPIED, none moved or deleted).
Archive branch: `research/mrv-scan-campaign-2026-10` (isolated worktree at
`/tmp/pentacube-bench/tw43/archive-worktree/`, from committed HEAD
`7ea861f`, original dirty worktree unchanged).

## Coverage

Available task dirs: TW1-15 (`coalesced-degree-delta/`, incl. `tw16/`
sub-reunion), TW1-17 through TW1-41 (as `tw17`…`tw41`, `tw33_run1`,
`tw21-retry`). There are NO `tw15`/`tw16` top-level dirs — TW1-15/16
evidence lives under `coalesced-degree-delta/` (+ `tw16/`); both archived
as `history/TW1-15/` (+ `tw16/`). Every numbered task TW1-15→TW1-41 is
represented. No placeholder reports were created; gaps are stated below.

## Included (verbatim copies unless noted)

- All task reports + progress files (TW1-15→TW1-41, incl. TW1-21-retry).
- Benchmark CSVs: TW1-15 V audit/results, TW1-16 KSS 10-run CSV, TW1-18…24
  pair CSVs (mostly header-only where blocked), TW1-27 10-row rejection CSV,
  TW1-29/30 header-only CSVs, TW1-41 header-only CSV.
- Structured JSON: TW1-32/33 preflight/readiness, TW1-37/39 test results,
  TW1-38 codegen summary, TW1-39 counter definitions, TW1-40 diagnostic
  results + run record.
- Sources: baseline (`a4fdcf12…` ✓), candidate (`274c3796…` ✓, hash recovered
  from TW1-29 report and re-verified), exact 39-line diff, overlap
  (`d23bf97e…`), ActiveX (`42fad94b…`, 4 identical copies cross-checked),
  TW1-19 instrumented snapshot, TW1-39 diagnostic source (`f337984a…`).
- Tests + runners: TW1-37 TU (ONE adaptation — relative include; old absolute
  path documented in README + manifest), TW1-39 counter tests, both workload
  scripts (unexecuted), TW1-32 harness + 33 self-tests + manifests + READMEs
  (TW1-31 originals kept as `*_tw31`).
- Correctness logs + forced traces (incl. both byte-identical 4884-line
  `67985dba…` traces), disassembly evidence (dis_*/fn_*), host diagnostics,
  blocker reports, TW1-20 debug/perf evidence incl. fix-verification sources.

## Intentionally excluded (with reasons + historical hashes)

- ALL compiled binaries (`solver_*` without extension, `*_asan`,
  `*_debug`, `*_profile`, `*_sanitized`, `*_invariant`, `*_BIN`): machine-
  specific (`-march=native`), 125 KB–6.4 MB each. Historical hashes retained:
  baseline `79dff337…c95ebc47`, candidate `f7f9b3f8…36715715`, ActiveX
  `fe8ea52f…3f15e9b`, overlap `d2146502…c70a14b4` (see manifest
  `omitted_binaries`; full list with sizes in manifest `omitted` notes).
- `gmon*.out` / `gmon.out` (TW1-17, ~130 KB): non-portable profiler dumps;
  the profile LOGS they derive from ARE archived.
- `__pycache__/` (TW1-31/32): regenerable bytecode.
- `solver_tw13.cpp` copies beyond TW1-17's (pre-coalesced ancestor, kept once
  as evidence; TW1-13 is not the experimental baseline).
- Placement `.txt` files: NOT archived (regenerable from the repo's
  `tools/export_placements.py`; hashes pinned in README + manifests).
  Rationale: 33–35 KB each but machine-independent regeneration is the
  documented path; V/KSSref copies exist in the repo root.

Largest archived files: `dis_base.txt` (310 KB), `dis_cand.txt` (305 KB) —
kept deliberately as the TW1-38 evidence base. Total archive ≈ 4 MB,
371 files. No secrets found (two `grep` hits both false positives:
`token` = regex variable in `bench_runner.py`; "secret-bearing" = TW1-34
prose stating command lines were NOT collected).

## Discrepancies preserved (not papered over)

1. TW1-20 report §4.1 lists the ActiveX binary hash as `d2146502…`
   (== TW1-18 overlap binary) and its benchmark table reproduces TW1-18's
   numbers exactly — impossible for distinct sources. Actual on-disk
   `solver_active_x` = `fe8ea52f…` (matches TW1-21). Authoritative ActiveX
   rejection = TW1-27 (CSV validated row-by-row). Recorded in
   CAMPAIGN_HISTORY.md and the manifest (`known_discrepancies`).
2. TW1-15/16 "repeated performance result": TW1-16 is a KSSref replication
   of TW1-15's V-adopted coalescing (median +3.87%) — "repeated" = second
   workload replication, not a same-workload rerun. Wording kept as tasked;
   this note clarifies the sense.
3. TW1-17/19 profiling evidence is on the exact coalesced source (gprof +
   thread-local counters); older TW1-13-source profiles do not apply —
   classification preserved from TW1-17/28, not re-judged here.
4. Historical manifests retain original-machine absolute paths
   (`/tmp/pentacube-bench/...`, `/home/philip/Work/...`) as evidence; they
   are not runnable config until re-pinned (README §7).

## Validation performed in-archive (no production search)

- `tests/run_tests.sh`: 3151/3151 pass, normal AND ASan/UBSan builds.
- `benchmarking/test_bench_runner.py`: 33/33 OK.
- Safe modes only (`preflight`, `evidence`, `dry-run`); `pgrep` confirms
  zero solver processes launched. `run --execute` and workload scripts were
  NOT executed (would be a real solver run — out of scope).
- `patch --dry-run` of the coalescing patch not re-run (historical claim
  preserved verbatim); the MRV diff applies cleanly by construction (the
  candidate IS baseline+diff — both hashes verify).
- Manifest verified against the actual tree (script-generated hashes/sizes;
  see `artifacts_manifest.json` + generation note below).

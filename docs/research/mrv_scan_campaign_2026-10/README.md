# MRV-Scan Optimisation Campaign — Archive (TW1-15 → TW1-41, Oct 2026)

Curated, provenance-preserving Git archive of the Fit-Polycubes MRV-scan
optimisation campaign. Original evidence lives in `/tmp/pentacube-bench/`
on the experiment machine; this archive makes the history available
cross-machine through the shared Git remote.

**Headline status: the MRV-scan candidate is RETAINED AS EXPERIMENTAL.
No controlled release-binary performance comparison has completed.
Nothing in this archive demonstrates that the candidate is faster.**

## Layout

- `README.md` — this file (how to verify, rebuild, and interpret).
- `CAMPAIGN_HISTORY.md` — chronological record of experiments and outcomes.
- `ARCHIVE_REPORT.md` — what was archived, what was excluded, discrepancies.
- `artifacts_manifest.json` — machine-readable manifest (hashes, provenance).
- `sources/baseline/solver_coalesced.cpp` — exact experimental baseline.
- `sources/candidates/solver_mrv_scan.cpp` + `solver_mrv_scan.diff` — candidate.
- `sources/rejected/` — overlap-graph and ActiveX source snapshots (record only).
- `tests/` — TW1-37 differential tests (adapted include path; see below).
- `diagnostics/` — TW1-39 instrumented source, counter tests, workload script.
- `benchmarking/` — TW1-32 hardened harness + tests + manifests + READMEs.
- `history/TW1-*/` — verbatim per-task reports, progress files, logs, CSVs, JSON.

## 1. Locating and verifying the sources

Baseline: `sources/baseline/solver_coalesced.cpp`
Expected SHA256: `a4fdcf12e070acca810a827f3eb14bbba385fa84578693d40ca02a93ead93278`

Candidate: `sources/candidates/solver_mrv_scan.cpp`
Expected SHA256: `274c3796c00658e1e4eee4b56304c86a7a470e05bd8f3aa3bef6e6be85bfb418`
(recovered from the TW1-29 report, independently re-verified against the file)

Diff: `sources/candidates/solver_mrv_scan.diff` (39 lines, 3 regions;
byte-identical to TW1-38 `source.diff`).

Verify on any machine:

    sha256sum sources/baseline/solver_coalesced.cpp \
              sources/candidates/solver_mrv_scan.cpp

Both must match the hashes above. The manifest (`artifacts_manifest.json`)
records original-vs-archived hashes for every file (exact copies: identical).

## 2. Why historical binaries were excluded

All compiled solver binaries, object files, debug/sanitizer builds, `gmon`
profiling output, and `__pycache__` directories were intentionally omitted.
They are machine-specific (`-march=native`), large, and non-reproducible
elsewhere. Their historical SHA256 identities are preserved in the reports
and manifest (`omitted_binaries` section):

- Baseline release binary: `79dff337875560de88f2501a602e8aeebabc26220a61197204adf910c95ebc47`
- Candidate release binary: `f7f9b3f86d45e520b06097e0b9fcefbe08dbedf05608cc956f06d3d073476715`
- ActiveX binary: `fe8ea52f126494df8f7e90d61797c30cfb9992309e480eac65811fa2c3f15e9b`
- Overlap binary: `d2146502110ce091d8ea04511829ce86c509adbad98fd9803b579145c70a14b4`

## 3. Rebuilding for the target machine

Because the historical flags include `-march=native`, binaries MUST be
rebuilt on the target machine — never copied. Rebuild with the recorded
compiler and flags:

    g++ -Ofast -march=native -flto -std=c++17 -pthread \
        sources/baseline/solver_coalesced.cpp -o solver_baseline
    g++ -Ofast -march=native -flto -std=c++17 -pthread \
        sources/candidates/solver_mrv_scan.cpp -o solver_mrv_scan

Compiler on record: `g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0`.
Expect different binary hashes on different CPUs — that is normal and does
not invalidate the source provenance. Re-run the correctness gate (below)
on the fresh binaries before any benchmarking.

## 4. Correctness evidence and its relation to source/binary identity

Full-search correctness was established in TW1-29 with the exact sources
above and byte-identical binaries (since excluded — rebuild first):

- V 5×5×6 exhaustive: 70033 nodes / 18 solutions / 34236 dead ends —
  full diff excluding timing IDENTICAL between baseline and candidate.
- KSSref 5×5×5 (10M cap): 10000068 nodes / 0 solutions / 6335178 dead —
  IDENTICAL.
- W 5×7×9 (2.5M cap): 2500040 nodes / 0 solutions / 1136291 dead —
  IDENTICAL.
- `DEBUG_COMPARE=1` forced-placement trace (V, 5000 cap): 4884 `D` lines,
  byte-identical (`67985dba…`). Both traces archived in `history/TW1-29/`.

TW1-37 adds 3151/3151 differential assertions (normal + ASan/UBSan) driving
the real MRV functions with an independent oracle; the archived copy runs
green (see `tests/`). TW1-38 (static codegen) and TW1-40 (workload exposure:
2.8M avoided visits, 180k discarded pushes at 250k nodes) are supporting
evidence only — neither is a runtime measurement.

Provenance caveat (stated in TW1-38, repeated here): filenames alone do not
prove the historical binaries were built from these sources, but the fresh
TW1-29 build reproduced the baseline binary hash exactly, and the candidate
binary is the byte-identical file from the passing correctness campaign.

## 5. CLI settings and placement files used

Canonical benchmark configuration (pinned in `benchmarking/` manifests):

    <binary> W 5 7 9 <placements_W> 2500000 \
        --connectivity --symmetry --region-prune=propagate   (single-threaded)

Placement-file hashes (files NOT archived — regenerate or copy them; the
V/KSSref files exist in the repo root, the W file path below is historical):

- W 5×7×9: `a7a421cde69049fcfa7fd7ee8aa71a82a4ad4c7bfc9631c04ab035d663f8b045`
- V 5×5×6: `dc22870d591d5c5789f4b7df8f546a36682e325474dbcb938b723afc46c100fe`
- KSSref 5×5×5: `9786dd438861f4668cc4b7f8f179d2b2e844426681d17c44d7375e901b1de291`

Expected counters: V 70033/18/34236, KSSref 10000068, W 2500040
(prop 564316 / forced 1525974). Five sequential alternating pairs
(baseline,candidate / candidate,baseline ×5); ≥2% median reduction
hypothesis; host gate ≥75 s epoch-verified (idle >85%, 1-min load <4.0,
zero memory pressure, no sustained swapping).

## 6. What is measured, inferred, or still missing

- MEASURED: correctness counters + forced traces (TW1-29); differential
  assertions (TW1-37); codegen deltas (TW1-38); workload-exposure counters
  (TW1-40); ActiveX rejection timings (TW1-27); overlap rejection timings
  (TW1-18); coalescing adoption timings (TW1-15/16).
- INFERRED (not runtime proof): the ≥2% MRV-scan hypothesis from codegen +
  exposure; host-contention diagnosis (TW1-34) from correlated observations.
- MISSING: the controlled five-pair release benchmark (blocked TW1-30/33);
  hardware counters in-VM (blocked TW1-41); TW1-15/16 raw per-run logs are
  partially represented (CSVs + audit logs archived; some intermediates
  omitted — see ARCHIVE_REPORT.md).

## 7. Portable adaptations in this archive (only two)

1. `tests/mrv_scan_differential_test.cpp`: the `#include` of the candidate
   source was rewritten from the absolute original-machine path
   (`/tmp/pentacube-bench/tw29/solver_mrv_scan.cpp`) to the archive-relative
   `../sources/candidates/solver_mrv_scan.cpp`. Verified: 3151/3151 pass on
   both normal and ASan/UBSan builds. Original preserved in `history/TW1-37/`
   context via the manifest (`adapted: true`, original hash recorded).
2. `diagnostics/run_workload_diagnostic.sh`: NOT adapted (still references
   the original-machine placement path); documented in the manifest as
   requiring the operator to set the placement path. Never executed here.

Historical manifests (`benchmarking/benchmark_manifest*.json`) are retained
unchanged, including their original-machine absolute paths — they are
evidence, not runnable config, until paths are re-pinned.

## 8. Re-running the safe validations (no solver search)

Differential tests (synthetic states only; the search loop never launches):

    cd tests && bash run_tests.sh        # expect 3151/3151, both builds

Harness self-tests (stubs/fakes only; safe modes only):

    cd benchmarking && python3 test_bench_runner.py   # expect 33/33 OK

Do NOT run `bench_runner.py ... run --execute` or any workload script
without first rebuilding the binaries, re-verifying hashes, passing the
correctness gate on the new machine, and passing the host-readiness gate.

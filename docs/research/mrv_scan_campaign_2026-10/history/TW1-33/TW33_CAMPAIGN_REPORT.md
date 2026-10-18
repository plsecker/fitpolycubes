# TW1-33 — MRV-Scan Benchmark Campaign: REPORT

**Outcome: BLOCKED (harness host gate failed — zero solvers launched)**

Date: 2026-10-17 NZDT. Run directory: `/tmp/pentacube-bench/tw33_run1/`.
No solver code modified; no binaries rebuilt; manifest identities untouched;
TW1-29 through TW1-32 artifacts preserved; no commit/merge/deploy.

## 1. Harness verification — PASS

- TW1-32 docs read (README, tw32_report, progress, manifest).
- Hashes verified against the TW1-32 report: bench_runner `87869123…`,
  test file `f35b105c…`, manifest `18724a1d…`, README `42d7a231…`,
  tw32_report `8c5a41a6…`, progress `56e25832…` — all match, no
  material difference from the reviewed version. Harness not modified.
- Self-tests: 33/33 pass (re-run this task).
- Safety properties confirmed live: `run` without `--execute` exits 2
  with no runs.csv; dry-run prints the 10 planned commands without
  executing; evidence binds to exact binary hashes.

## 2. Run preparation — PASS

Manifest config confirmed: W 5×7×9, cap 2500000,
`--connectivity --symmetry --region-prune=propagate`, single-threaded,
pair order baseline,candidate / candidate,baseline ×5, `use_time_v: true`.
All five pinned hashes independently re-verified against actual files:
baseline source `a4fdcf12…93278`, candidate source `274c3796…bfb418`,
baseline binary `79dff337…c95ebc47`, candidate binary `f7f9b3f8…36715715`,
W placements `a7a421cd…`. Binaries not rebuilt.

## 3. Preflight / evidence / dry-run — PASS (no solvers started)

- `preflight`: 5/5 pinned files verified.
- `evidence`: 8/8 evidence logs verified (incl. both 4884-line forced
  traces, byte-identical `67985dba…`).
- `dry-run`: 10 correct commands printed, nothing executed.

## 4. Host gate — FAIL (harness refused execution)

`run --execute` ran preflight + evidence, then the 75 s gate
(00:08:22–00:09:37 UTC, 15 samples) failed on all four axes:
- avg idle **73.9%** (min 29.0, max 88.7; gate >85%)
- 1-min load **4.13–4.19** at window start, three samples ≥4.0
- memory pressure avg10 spiked to **10.74** (early-window burst)
- sustained swapping: swap-out bursts of **5017/6379/3700** pages plus
  continuous swap-in (active paging, not old occupancy)

Exit 4 (BLOCKED). **Zero solver processes launched** — confirmed by
process check (one transient pgrep self-match ruled out by PID
inspection, same pattern as TW1-32). `preflight.json` + `readiness.json`
preserved in the run directory; no `runs.csv`, no fabricated rows.

## 5. Analysis / decision

- Completed pairs: **0 of 5**. No timings, no ratios, no reductions.
- Decision: **BLOCKED**. The ≥2% hypothesis remains untested, not
  falsified. The candidate stays RETAIN AS EXPERIMENTAL.
- Per protocol, no repeated gate attempts without a material change in
  host conditions. The harness behaved exactly as designed: fail-closed
  with machine-readable diagnostics.

## 6. Final artifacts

- `/tmp/pentacube-bench/tw33_run1/preflight.json` — 5/5 pinned files ok
- `/tmp/pentacube-bench/tw33_run1/readiness.json` — gate FAIL record
  (15 samples, 4 stop reasons)
- `/tmp/pentacube-bench/tw33_run1/TW33_CAMPAIGN_REPORT.md` — this report

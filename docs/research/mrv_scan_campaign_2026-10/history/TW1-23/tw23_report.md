# TW1-23 — Host Recheck After Load Reduction: BLOCKED (gate failed)

**Date:** 2026-10-16 (Pacific/Auckland)
**Status:** BLOCKED — gate failed on CPU idle (and swap occupancy). No solver jobs launched, no solver files modified. Earlier artifacts untouched; new results only under `/tmp/pentacube-bench/tw23/`.

---

## 1. Gate measurements (75 s vmstat + snapshots)

Host: 8 logical CPUs, 11.7 GB RAM, 4 GB swap. No solver jobs were launched (per instructions, none will be until the gate passes).

| Criterion | Requirement | Observed | Verdict |
|---|---|---|---|
| No competing solver/benchmark processes | none | none (`pgrep` empty) | ✓ PASS |
| Average CPU idle > 85% | > 85% | vmstat `id`: 56, 82, 83, 86 → **avg ~76.8%** | ✗ FAIL |
| 1-min load < 4.0 | < 4.0 | **3.69 → 3.33** (falling) | ✓ PASS |
| No significant swapping / memory pressure | none | **swap 2845/4095 MB (69.5%) in use**; `si/so` 0 during window (no active swap storm), but free RAM only ~370–690 MB with 2.8 GB resident in swap | ✗ FAIL |

Improvement vs TW1-22 (idle ~50%, load >5, active swap-out) is real but insufficient: idle still 8 points short of the gate, and swap occupancy is unchanged (69–70%). Load source unchanged — desktop stack (Firefox ~20–33%, OpenWork sidecar/renderer ~16–24%, gnome-shell ~8%); nothing was killed per instructions.

Raw evidence: `tw23/host_vmstat.txt`, `tw23/host_top.txt`, `tw23/host_mem.txt`.

---

## 2.–5. Hashes / correctness / benchmarks

Not reached — the gate failed, so per instructions no hashes were re-verified, no correctness checks run, and no benchmarks started. No speedup is claimed. `benchmark_results.csv` contains the schema header and zero data rows.

---

## 6. Artifacts

| File | SHA256 |
|---|---|
| `/tmp/pentacube-bench/tw23/tw23_report.md` | (see verification command below) |
| `/tmp/pentacube-bench/tw23/progress.txt` | (see verification command below) |
| `/tmp/pentacube-bench/tw23/benchmark_results.csv` | (see verification command below) |

TW1-20 standing result unchanged: correctness established, performance **RETAIN AS EXPERIMENTAL**. To unblock: close the desktop load (Firefox/OpenWork) or reboot to clear swap, then re-run this gate; or use a dedicated quiet host.

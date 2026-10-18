# TW1-35 — Host Recovery Verification: REPORT

**Outcome: NOT READY (gate failed mid-window — stop, no benchmark)**

Date: 2026-10-17 NZDT. No solver, benchmark, or correctness test run.
All sources, binaries, manifests, and artifacts preserved; no
commit/merge/deploy.

## 1. Intervention check

At 13:51:17 NZDT the profile looked improved vs TW1-34: 5-min load
1.36, pressure avg10 ~1.4 falling, no solver/bench jobs. But the same
desktop cast was still resident (opencode ~14%, firefox ~13% + content
procs, gnome-shell 8.1%, system-monitor 5.3%, openwork ~6%) and swap
was 99% full (4068/4095 MB, worse than TW1-34's 96%).

Sustained-load pre-check (13:51:41–13:54:11, 6 × 30 s samples): 5-min
load held 1.25–1.45, pressure decayed to 0.00, swap traffic nil. The
TW1-34 trigger condition (5-min load <2 sustained) was met, so the
formal observation started at 13:54:53.

## 2. Formal observation (83 s, epoch-verified)

Window 13:54:53–13:56:16 NZDT (16 × 5 s /proc/stat deltas, 83 s):

- Idle %: 86.7, 87.4, 87.0, 85.3, 88.0, then 69.9, 40.4, 17.2, 24.4,
  18.4, 23.0, 25.0, 27.5, 22.4, 20.0, 24.5 → **average 46.1%**
  (gate >85%: FAIL)
- 1-min load: 1.63 → 9.69, **nine samples ≥4.0** (gate: FAIL)
- Memory pressure avg10: 0.00 for 8 samples, then 0.90 → 4.52 → 2.48 →
  1.66 → 2.54 → 13.71 → 18.60 → 14.70 (significant: FAIL)
- Swap: quiet (si ≤21, so 0) for 5 samples, then sustained swap-in
  (559–4505 pages/5 s) plus swap-out bursts of 497/1508/1002/4713/4424
  pages (sustained swapping: FAIL — active paging, not occupancy)
- No competing solver/benchmark processes (PASS — only passing gate)

## 3. Burst attribution

At ~13:55:24 a new firefox content process (~6% CPU, 76 s old at
snapshot) plus `kworker/*-kblockd` block-I/O workers appeared; one
content process entered D-state; CPU pressure avg10 hit 43.65 and
memory-full avg10 hit 32.18. This is the same episodic paging-storm
signature as TW1-34, now captured destroying a window that began at
87% idle. The intervention (whatever desktop reduction occurred) did
not remove the burst source: firefox content processes and the
nearly-full swap device remain.

## 4. Decision

**NOT READY.** Per protocol: stop, no benchmark, no repeat until
another material change. The TW1-34 trigger proved insufficient — a
calm 5-min load does not predict the next 80 s on this host. The next
attempt additionally requires: firefox content-process count reduced
(tabs closed, not just backgrounded), gnome-system-monitor quit, and
swap occupancy materially reduced (reboot or swapoff/swapon by the
operator — operator action, not taken here). The MRV-scan hypothesis
remains untested; the candidate stays RETAIN AS EXPERIMENTAL.

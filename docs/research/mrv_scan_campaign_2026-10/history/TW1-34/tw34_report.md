# TW1-34 — Benchmark-Host Contention Diagnosis: REPORT

**Outcome: REMEDIATION PLAN READY**

Date: 2026-10-17 NZDT. Read-only investigation only: no solver or
benchmark executed, no process touched, no config changed, no reboot,
no gate retries. New artifacts only under `/tmp/pentacube-bench/tw34/`.

## 1. Machine state

- Host: philip-VirtualBox, kernel 7.0.0-38-generic, `systemd-detect-virt`
  reports `oracle` (VirtualBox guest confirmed; vboxguest/vboxsf/vboxvideo
  modules loaded). CPU: Intel Core Ultra 7 155H, 8 logical CPUs visible.
- RAM 11752 MB; at task start MemAvailable 3714 MB, swap 3963/4095 MB
  occupied (**96% full**); load 0.88; pressure some/full avg10 0.10/0.05.
- No solver, benchmark, or diagnostic job running (confirmed twice;
  two transient pgrep self-matches ruled out by PID inspection).
- History reviewed: TW1-33 campaign report (gate failed on all four axes,
  zero solvers launched), TW1-30 report (idle 61.2%, load 6.3–8.7, active
  paging), TW1-32 progress (harness ready, hypothesis untested).

## 2. CPU contention (102 s bounded observation, 13:18:06–13:19:48 NZDT)

Method: 20 × 5 s `/proc/stat` deltas (user/sys/iowait/steal/idle split).

- Average idle **61.8%** (min 21.7, max 85.4). Load rose **2.32 → 6.44**.
- CPU-steal time **0.0% in every sample** — no measurable VirtualBox
  scheduling contention visible from inside the guest.
- I/O wait ≤0.8% except one 2.8% sample during a paging storm — not the
  driver. System time 5–35% (peaks coincide with paging storms: page
  reclaim + fault handling, not application compute).
- Snapshots (process names only, no secret-bearing command lines):
  opencode sidecar ~13–14%, firefox main ~12.7%, firefox content procs
  ~6–8% each, gnome-shell 8.1%, gnome-system-monitor 5.3%,
  OpenWork renderer ~5.8%. Same cast in both snapshots, 11 min apart.

**Verdict: category A — a few identifiable desktop applications dominate.**
Steal (C), iowait (D), and diffuse system load (B) are ruled out as
primary causes. The load is bursty: quiet spells (idle 83–85%, load
~2.7) alternate with desktop bursts (idle 22–38%, load 4–6.4) on a
timescale of tens of seconds — which is why 75 s gates keep failing
even when a spot check looks calm (task start showed load 0.88).

## 3. Memory pressure (same window)

- Anon memory ~7.3 GB (active ~4.5–4.8 GB + inactive ~2.7–2.8 GB) of
  11.75 GB; MemAvailable 3.6–3.8 GB; file cache ~1.9–2.1 GB (reclaimable).
- Swap 96% occupied, but occupancy alone is not the finding — **two live
  paging storms were captured**: 13:18:32 (si 243 + so 3002 pages/5 s,
  pressure avg10 2.77) and 13:19:43–48 (si 1362–1471 + so 2243–4870
  pages/5 s, pressure avg10 2.83 → 5.79). Between storms, swap traffic
  is near zero.
- 992,844 major faults lifetime; no D-state processes in snapshots
  (storms are brief reclaim bursts, not stuck I/O).
- Largest RSS holders: gnome-system-monitor ~1.3 GB (10.9%),
  firefox content procs ~1.0–1.3 GB each, firefox main ~1.0 GB, opencode
  sidecar ~0.65–0.76 GB.

**Verdict: episodic active paging is real and is a significant timing-
variability source.** The pattern (quiet → sudden multi-thousand-page
swap-out burst with pressure spike → calm) matches desktop working-set
spikes against a nearly-full swap device. A 12–25 s solver run landing
inside a storm would be directly perturbed; this plausibly contributed
to TW1-27's run-to-run spread and would invalidate a 2% comparison.

## 4. VirtualBox and resource limits

- Steal 0.0% throughout: no evidence of host-level CPU starvation.
- Cgroups: cgroup2 mounted; no `cpu.max`/`memory.max`/`memory.high`
  files — **no guest-internal CPU or memory quota in effect**.
- All 8 CPUs visible and scheduled on (no offline CPUs).
- **Cannot be established from inside the guest:** physical host CPU/RAM
  headroom, host overcommit, host swap state, VM resource caps set in
  the VirtualBox host UI. No guess is made about the physical host.

## 5. Remediation plan (ranked by impact × confidence)

1. **Benchmark in a genuinely quiet window** (high impact, high
   confidence, guest-operator action, no work interruption risk beyond
   the operator's own tabs): close or pause heavy firefox tabs, quit
   gnome-system-monitor (~1.3 GB + 5% CPU for a monitor!), pause
   OpenCode background work during the ~10 min campaign. Verify with
   the harness gate itself (see below).
2. **Shrink the desktop memory footprint before benchmarking**
   (high impact on paging, medium-high confidence): the two biggest
   reclaimable holders are firefox content processes and
   gnome-system-monitor. Closing them frees ~2–3 GB anon, giving the
   reclaim path headroom so working-set spikes don't become swap-out
   storms. Safe; reversible by reopening.
3. **If gates still fail when the desktop is quiet** (medium impact,
   medium confidence, requires host-level access): raise the VM's RAM
   (swap is 96% full — the device, not just occupancy, is the risk)
   and/or vCPU count via the VirtualBox host interface, or move the
   benchmark to a Linux compute host with no desktop. Cannot be done
   from inside the guest; needs the machine owner.
4. **Not recommended:** indiscriminate `kill`, renice games, reboot as a
   default, or repeated gate retries hoping for a lucky dip — the
   burst timescale guarantees flaky passes.

**Bounded verification procedure (operator-requested, one shot):**
after a material change, run the harness `readiness` mode once. A real
improvement reads: gate PASS **plus** pressure avg10 ≈ 0.00 across all
samples **plus** zero swap-out in every 5 s window. A brief dip reads:
gate PASS with pressure spikes or swap-out present — do not benchmark
on that; wait for genuinely settled conditions. Trigger for the next
check: operator confirms tabs closed/monitor quit **and** 5-min load
<2.0 sustained over several minutes.

## 6. Campaign protection — confirmed

- TW1-29 candidate source `274c3796…`, baseline binary `79dff337…`,
  candidate binary `f7f9b3f8…`: all re-hashed, unchanged.
- TW1-32 harness `87869123…` + manifest `18724a1d…`: unchanged.
- TW1-33 `readiness.json` `7605ed26…`: unchanged.
- No solver/benchmark process started in this task (two PID checks).
- TW1-33 not restarted; no new benchmark attempted. The MRV-scan ≥2%
  hypothesis remains untested.

## 7. Remaining uncertainty

Burst trigger not pinned to a single tab/process (correlating a storm
to one PID needs per-process I/O accounting over a longer window —
possible follow-up, not done here). Physical-host headroom unknown.
Whether 2–3 GB freed anon fully suppresses storms is a prediction to
verify with the procedure in §5, not a certainty.

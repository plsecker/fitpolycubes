TW1-25 host readiness recheck — diagnostic report
Host: philip-VirtualBox, 8 logical CPUs
Window: 2026-10-17 09:25:19–09:25:46 NZDT (16 vmstat samples + snapshots, >=75s)
Prior: TW1-24 BLOCKED (idle 64.3%, 1-min load up to 5.76)

Per-sample CPU idle % (vmstat, all CPUs):
  84, 90, 89, 88, 88, 47, 74, 83, 79, 76, 65, 20, 16, 43, 43, 32
Average idle: 63.6% (sum 1017 / 16) — GATE REQUIRES >85%: FAIL
Note: first 11 samples averaged ~75%; idle collapsed to 16–43% over the
final 5 samples as desktop load spiked again. No sustained quiescent period.

Load averages (1-min):
  start 3.29; samples 3.43 → 3.23 → 3.05 → 3.61 → 4.68; end-of-window uptime 5.75.
  1-min load exceeded 4.0 by end of window and was rising — GATE REQUIRES <4.0: FAIL

Memory:
  MemTotal 12034596 kB; MemAvailable 4.2–4.7 GB across window (dipped to ~4.2 GB at end)
  /proc/pressure/memory: some and full avg10/avg60/avg300 all 0.00 — PASS
  Swap: ~2.9 GB occupied, SwapFree stable 1229228→1229276 kB; vmstat si/so 0/0
  except one 4/0 blip — no sustained swapping: PASS (accumulated occupancy only)

Competing processes:
  pgrep solver|benchmark|pentacube: no solver or benchmark processes
  (only idle pentacube-monitor collector/agent daemons) — PASS

Remaining high-CPU desktop processes (nothing killed, per protocol):
  - firefox main (12.4% CPU, 9.0% MEM) + content proc tab-19 (8.2% CPU, ~14% MEM)
  - opencode sidecar serve (13.1% CPU)
  - gnome-shell (7.9% CPU), gnome-system-monitor (5.1% CPU, 12.8% MEM)
  - openwork renderer (~5% CPU), openwork main (~4.5% CPU)
  Same desktop/memory load profile as TW1-24; host conditions have not
  materially changed (TW1-24 idle 64.3% vs TW1-25 idle 63.6%).

GATE OUTCOME: FAIL (idle 63.6% < 85%; 1-min load rising past 4.0 to 5.75).
Action per protocol: STOP. No solver jobs run. No code modified.
All /tmp/pentacube-bench/tw24 artifacts preserved untouched.
Per instruction, not repeating the check without a change in host conditions:
next attempt should wait for a genuinely quiescent host (close or idle the
heavy desktop consumers first — operator action, not taken here).

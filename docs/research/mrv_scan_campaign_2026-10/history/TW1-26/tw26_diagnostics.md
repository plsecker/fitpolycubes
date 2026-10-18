TW1-26 host readiness — diagnostic report
Host: philip-VirtualBox, 8 logical CPUs
Prior: TW1-21–TW1-25 blocked by desktop CPU load; operator reduced/paused workload.

1. Timestamp verification (per TW1-26 instruction 1):
   OBS_START_EPOCH=1792182732 OBS_START_TS=2026-10-17T09:32:12+13:00
   OBS_END_EPOCH=1792182813 OBS_END_TS=2026-10-17T09:33:33+13:00
   OBS_DURATION_S=81 (>=75s required: PASS, epoch-verified)
   Method: 16 consecutive 5s /proc/stat deltas (true idle %, not vmstat
   1s snapshots). Prior TW1-24/TW1-25 windows are acknowledged as short;
   this window is genuinely 81 seconds.

2. Measurements (16 samples, one per ~5s):
   Idle %: 88.2, 85.9, 88.6, 87.7, 82.0, 84.6, 86.8, 88.7,
            82.7, 80.9, 68.3, 80.5, 72.8, 78.1, 85.6, 86.7
   Average idle: 83.0% (sum 1328.1 / 16) — GATE REQUIRES >85%: FAIL
   1-min load: 4.46, 4.27, 4.00, 3.76, 3.94, 3.79, 3.48, 3.20,
               2.95, 2.71, 4.34, 3.99, 3.67, 3.37, 3.10, 3.02
               (start-of-window uptime 5.04; end-of-window uptime 2.57)
               Average 3.63 (<4.0) but 4 samples at/above 4.0 with a
               mid-window spike to 4.34 — MARGINAL/FAIL on stability.
   MemAvailable: 4.2–4.6 GB of 11.75 GB total — adequate.
   /proc/pressure/memory: some and full avg10/avg60/avg300 all 0.00
   throughout — PASS (no significant memory pressure).
   Swap: ~2.9 GB occupied but stable; per-5s pswpin deltas
   0,0,0,0,0,0,0,0,0,4,21,5,2,1,6,0 (39 pages / 81s, zero pswpout) —
   no sustained swapping: PASS (accumulated occupancy only).

3. Competing processes: none (pgrep for solver/benchmark binaries empty;
   only idle pentacube-monitor collector/agent daemons) — PASS.

4. Remaining desktop consumers (nothing killed, per protocol):
   opencode sidecar ~13–14.5% CPU, firefox main ~12.4% CPU / 9.3% MEM,
   firefox tab-19 content proc ~8.2% CPU / ~13.7% MEM, gnome-shell 7.9%,
   gnome-system-monitor 5.1% / 12.8% MEM, openwork renderer ~5–6%.
   Operator intervention helped (early-window idle ~86–89%, load falling
   4.46 → 2.71) but a mid-window desktop burst (idle 68.3%, load 4.34)
   broke the sustained-quiescence requirement.

GATE OUTCOME: FAIL (avg idle 83.0% < 85%; 1-min load not stably <4.0).
Action per protocol: STOP. No solver jobs run. No source/binary/placement
verification, no correctness gate, no benchmarks. No code modified, no
commit/merge/deploy. All earlier artifacts preserved; nothing written
outside /tmp/pentacube-bench/tw26/.
Per instruction 4, no further retries without another change in host
conditions. Improvement vs TW1-24 (64.3%) and TW1-25 (63.6%) is real but
not yet sufficient — a longer fully-quiescent window is needed.

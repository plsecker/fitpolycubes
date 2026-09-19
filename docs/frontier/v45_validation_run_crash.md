# V45 Validation Run Crash — Diagnostic

**Date:** 2026-09-18  
**Classification:** Host-level resource kill (systemd-oomd), not a solver bug

## Failure Mode

Both heavy validation runs (corrected V35 enumeration, George min-id-3590 walk)
were killed simultaneously at **19:40:01** by `systemd-oomd` (userspace OOM daemon)
due to cgroup memory pressure.

### Kill Record (journalctl)

```
Killed /user.slice/.../app-com.differentai.openwork-10880.scope
  due to memory pressure for /user.slice/.../user@1000.service
  being 62.21% > 50.00% for > 20s with reclaim activity
systemd-oomd killed 7 process(es) in this unit.
```

### Root Cause

The OpenWork desktop app scope (`openwork-10880.scope`) contained both Python
processes as cgroup children (launched from the OpenWork bash tool).  The combined
memory footprint:

| Component | RSS (last observed) | Notes |
|-----------|-------------------|-------|
| george (pid 30455) | **16.4 GB** | V45 visited set, still growing |
| v35 (pid 30454) | **1.8 GB** | Per-bucket oscillation 346 MB–1.8 GB |
| OpenWork app + gnome scope | ~2.6 GB | OpenWork desktop + related services |
| Other user processes | ~2 GB | GNOME Shell, Evolution, etc. |
| **Total** | **~22.8 GB** | On a 28 GB machine with 8 GB swap |

The user slice's memory pressure (PSI Avg10: 49.44%) exceeded the 50% threshold
for >20s with active reclaim, triggering the kill.  `journalctl` confirms memory
pressure warnings starting at 19:39:12 — approximately 1 minute before the kill.

## V35 — Last Verified Progress

- **Launched:** 18:25:30, **killed:** 19:40:01 (~75 min)
- **Phase at kill:** enumeration phase (count_minids completed; per-bucket iteration active)
- **RSS pattern:** oscillating 346 MB–1.8 GB (consistent with processing buckets of varying size)
- **Progress output:** NONE — logs are 0 bytes (Python block-buffered stdout, never flushed)
- **Estimated enumeration time:** ~21 min (109s DFS + ~19 min connectivity checks at 15.3M leaves × 75 µs)
- **Actual elapsed:** ~75 min → ~3.5× slowdown, attributable to memory pressure from concurrent george walk
- **Checkpoints:** none written (validation script has no checkpoint mechanism)

**Assessment:** V35 enumeration was likely near completion or completing when killed.
The ~3.5× slowdown is consistent with severe memory pressure.  The enumeration itself
is not defective — it was progressing normally (RSS oscillation = bucket processing)
but starved of memory by the george process.

## George — Last Verified Progress

- **Launched:** 18:25:30, **killed:** 19:40:01 (~75 min)
- **Phase at kill:** full min-id-3590 DFS walk (iter_targets_seeded, no --skip-walk)
- **RSS at last observation:** 16.4 GB (visited set, still growing at kill time)
- **Progress output:** NONE — logs are 0 bytes (buffered)
- **Expected leaf count:** 3,430,348 targets
- **Visited set size:** 16.4 GB → estimated 55–155M states depending on per-entry overhead
- **Checkpoints:** none written

**Assessment:** The George walk was still in its DFS expansion phase.  The visited
set was growing at the time of kill.  The 3,430,348-leaf subtree requires a visited
set that is a large fraction of the total V45 state space (estimated 41M states
total in audit).  The memory footprint was the proximate cause of the oomd kill.

## Resource Usage

| Metric | Value |
|--------|-------|
| Machine RAM | 28 GB |
| Swap | 8 GB |
| Disk | 844 GB free |
| User slice memory at kill | 26.6 GB (in the OpenWork scope) |
| Kill trigger | PSI pressure 62.21% > 50% for > 20s |
| Kill time | 19:40:01 |
| Kernel OOM | NOT triggered (systemd-oomd acts first) |

## Trustworthiness of Output

| Item | Trustworthy? |
|------|-------------|
| V35 log output | NO — 0 bytes, never flushed |
| V35 partial results | NO — no checkpoints exist |
| George log output | NO — 0 bytes, never flushed |
| George visited set | NO — in-memory only, lost at kill |
| Prior validation results | YES — small/v35count/partition/determinism/audit all completed and printed before launch |

## Checkpoint / Resume Status

| Run | Checkpoint? | Resume possible? | Notes |
|-----|------------|-------------------|-------|
| V35 | No | **No** | Must restart from scratch; no mid-enumeration state saved |
| George | No | **No** | Must restart from scratch; visited set is entirely in-memory |

The validation script (`tools/frontier/validate_v45_enumeration.py`) does not
implement checkpointing.  The `iter_targets_seeded` generator does not support
serialization or mid-stream save/restore.

## Recommended Next Steps

1. **Re-run V35 and George SEQUENTIALLY** (not in parallel) to halve peak memory.
2. **Re-run George with `--skip-walk` first** to capture all static checks
   (these are fast, <5s, and confirm the regression without the expensive walk).
3. **Optionally re-run the full George walk separately** once V35 completes.
4. **Run from a terminal outside the OpenWork app scope** to avoid cgroup-level
   oomd kills.  Alternatively, set `MemoryMax=` on the OpenWork scope to prevent
   it from consuming all RAM.
5. **Add unbuffered output** (`PYTHONUNBUFFERED=1` or `python3 -u`) when launching
   long background runs to ensure logs are written in real time.

---

## Follow-up (2026-09-19): V35 Slowness Diagnosed — Connectivity-Pruned Engine

The re-launched V35 run (systemd transient `v45-v35`, started 20:19:52, outside
the OpenWork cgroup) confirmed the original seeded DFS is impractical on the
**corrected** candidate domain:

| Metric | Value |
|--------|-------|
| Elapsed at stop | 11 h 50 min |
| CPU | 99.9% (11 h 50 min CPU time) |
| RSS | oscillating 256 MB–1.8 GB |
| Progress lines (500K targets) | **0** (cumulative < 500K; still in the zero-leaf region) |
| Extrapolated total | ~44–47 h |

### Root cause

The corrected candidate domain is 1,730 min-ids `[0..1873]`, but the reference
histogram has only **489 leaf-bearing buckets** `[558..1857]`.  The other
**1,241 buckets are zero-leaf**, yet each costs 60–160 s in the original seeded
DFS because the seed orbit s is far from the centre and the search explores the
full disconnected product space (combinations around s × combinations around the
centre).  Per-bucket measurements (spare core, same code path):

| bucket | leaves | original seeded DFS |
|--------|-------:|--------------------:|
| 100 | 0 | 86 s |
| 300 | 0 | 106 s |
| 558 | 1 | 99–105 s |
| 800 | 0 | 62 s |
| 1000 | 66 | 124–125 s |
| 1200 | 2,306 | 156 s |
| 1335 | 68,072 | 64–66 s |
| 1450 | 0 | 100 s |
| 1550 | 261,366 | 196–212 s |
| 1650 | 272,818 | 40 s |

Reference pass: `count_minids` = 15,289,669 leaves, 23,193,326 states, 125–134 s.

### Fix: `iter_targets_seeded_connected` (connectivity-pruned engine)

New engine in `solvers/t_ck6_oddity_v35_search.py` (implemented 2026-09-19):

1. **Connectivity prune (complete):** only add orbits face-adjacent to the
   centre's connected component.  Completeness: every connected target's orbit
   graph is connected; ordering its orbits as {seed s first, then by
   non-decreasing spanning-tree depth} makes every added orbit
   centre-component-adjacent at add time, and the DFS explores all such orders.
2. **Root reachability prune (provably empty buckets):** `dist_to_center[s]`
   (Dijkstra min node-weight path cost from orbit s to the centre) > budget ⇒
   no target can afford a path from s to the centre; `cells_ge[s]` (union of
   orbits ≥ s) < volume − 1 ⇒ not enough cells.  These two necessary conditions
   eliminate **all 1,241 zero-leaf buckets** (1,225 via dist, 16 via cells);
   the boundary is exact: `dist[558] = 17 = budget` and 558 is the first
   leaf-bearing min-id.
3. **Exact leaf check:** every added orbit is centre-component-adjacent, so the
   cell set is connected iff the seed is bridged into the centre component —
   no `is_face_connected` BFS needed.

### Benchmark (pruned vs original, same buckets)

| bucket | leaves | original | pruned | pruned states |
|--------|-------:|---------:|-------:|--------------:|
| 100 | 0 | 81.8 s | **0.0 s** | 0 (root prune) |
| 300 | 0 | 97.3 s | **0.0 s** | 0 |
| 558 | 1 | 99.8 s | **13.9 s** | 2,704,558 |
| 800 | 0 | 58.6 s | **0.0 s** | 0 |
| 1000 | 66 | 118.1 s | **13.0 s** | 2,704,099 |
| 1200 | 2,306 | 146.7 s | **12.8 s** | 2,694,059 |
| 1335 | 68,072 | 60.9 s | **12.7 s** | 2,669,495 |
| 1450 | 0 | 92.6 s | **0.0 s** | 0 |
| 1550 | 261,366 | 195.6 s | **10.0 s** | 2,033,956 |

Every bucket yields exactly the same leaf set as the original.  Extrapolated
full corrected V35 validation: **~2–2.5 h** (489 leaf-bearing buckets × ~13 s
+ 15.3 M leaf yields + 134 s reference pass), vs ~44–47 h for the original.

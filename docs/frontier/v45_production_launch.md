# V45 Production Launch — Corrected Architecture (Frozen)

**Date:** 2026-09-19
**Status:** READY TO LAUNCH (engine validated; production run NOT yet started)
**Driver:** `tools/frontier/run_v45_production.py` (the ONLY sanctioned V45
production driver; the historical `t_ck6_reuse_multipiece.run_combo` refuses
V45 by design).

This document is the single source of truth for the production V45 CK6
enumeration: the exact algorithm, the completeness argument, the validation
evidence chain, the shard plan, the expected outputs, and the
checkpoint/resume procedure.

---

## 0. WARNING — no V45 total is known yet

**The total number of connected CK6-closed 45-cell targets is UNKNOWN until
this run completes.**  The retired figure 1,469,999 was produced by the
buggy prefilter (which excluded min-id 3590 and 1,241 other leaf-bearing
candidates) and is **never** used as an expected result anywhere in the
production path.  All conservation checks in the driver are internal
(sum of shard counts == sum of per-min-id counts); there is no
expected-total parameter.  Any claim of a V45 total before `final.json`
exists is invalid.

---

## 1. Exact corrected algorithm

The production engine is `iter_targets_seeded_connected(un, s, budget)` in
`solvers/t_ck6_oddity_v35_search.py`, with `budget = (45 − 1) / 2 = 22`.

For each min-id `s` in the corrected 3,696-candidate domain:

1. **Seed.**  Start from the orbit set `{s}` (ids < s are forbidden
   throughout the search).
2. **Growth rule (connectivity prune).**  At every state, expand only
   orbits that are face-adjacent to the **centre's connected component**
   (the component containing the centre orbit).  The seed `s` may be
   disconnected initially; it joins the centre component when a
   centre-component-adjacent orbit adjacent to `s` is added.
3. **Root reachability prunes (provably empty buckets).**  Computed once
   per universe and cached (`_conn_prune_data`):
   - `dist_to_center[s]` (Dijkstra node-weight path cost to the centre):
     if it exceeds the budget, the bucket is empty.
   - `cells_ge[s]` (|union of orbits with id ≥ s|): if fewer than V − 1
     cells, the bucket is empty.
4. **Visited set.**  Orbit ids stored shifted down by `s` (mask bit i
   represents orbit id i + s); masks stay ≤ 348 bits, cutting visited-set
   memory ~5.5× vs the unshifted representation.  Exact equivalence was
   validated on real min-id-3590 masks.
5. **Leaf check.**  The cell set is connected **iff** the seed `s` is
   bridged into the centre component (the `bridged` flag) — no
   `is_face_connected` BFS.  Yielded sets are orbit-closed, have min-id
   exactly `s`, exactly 45 cells (rem = 0 ⇒ cost = budget), and are
   connected.
6. **Per-target audit.**  Every yielded target passes through the driver's
   own funnel + exact-cover + dual-solver audit
   (`t_ck6_reuse_multipiece._process_target` / `funnel_and_cover`,
   imported unmodified): `len(t) == 45`, `is_face_connected(t)`, funnel
   stage, exact-cover candidate count, SAT/UNSAT, witness recording.

## 2. Completeness argument

A target T is a connected CK6-closed cell set of odd volume V containing
the centre; its orbit set O(T) has a unique minimum id s, and its orbit
graph is connected (cell paths map to orbit walks).

**Spanning-tree order.**  Root a spanning tree ST of O(T) at the centre.
Order the orbits of T: s first, then all others by non-decreasing ST
depth.  Every orbit v ≠ s added in this order is adjacent to the centre's
connected component at add time: v's ST parent has smaller depth and is
therefore already in the centre component (depth-1 orbits are
centre-adjacent; each deeper orbit is adjacent to its parent).  The seed s
joins the centre component when its parent is added, and s's ST children
are then added through s-adjacency.

The DFS expands **every** centre-component-adjacent orbit at every state,
so the spanning-tree order is one of the explored orders and O(T) is
reached.  Soundness: every yielded set is orbit-closed, min-id s, exactly
V cells, connected (bridged flag).  Therefore the pruned engine yields
exactly the connected CK6-closed targets with minimum orbit id s — the
same target set as the original seeded DFS, in a strict subset of its
state space.

The 3,696-candidate domain is the corrected sound filter's output
(`corrected_candidate_min_ids`): every candidate passes both necessary
conditions, and the filter provably excludes no leaf-bearing min-id (the
boundary is exact: `dist[558] = 17 = budget` at V35; 0 of the 489
leaf-bearing V35 min-ids violate either condition).

## 3. Validation evidence chain

### 3.1 V5 / V15 / V25 (independent small-volume validation)

`validate_v45_enumeration.py --pruned small` — all PASS:

| Check | Result |
|---|---|
| V5 subset brute force (C(18,4) = 3060 subsets) | 2 targets |
| V5 pruned raw set == reference raw set | 2 == 2, no dups |
| V5 pruned canonical set == subset brute force | 2 == 2 |
| V15 pruned total == 368 | PASS |
| V15 pruned canonical set == cell-level brute force | 189 == 189 |
| V15 pruned raw set == reference raw set | 368 == 368, no dups |
| V25 pruned total == 71,539 | PASS |
| V25 pruned canonical set == cell-level brute force | 35,822 == 35,822 |
| V25 pruned raw set == reference raw set | 71,539 == 71,539, no dups |
| V25 per-min-id counts == reference hist | PASS (626 candidates, 172 hist keys) |
| V25 min-id coverage / ownership | PASS |

Plus `--pruned determinism` (two PYTHONHASHSEED values: identical totals,
counts, canonical hashes) and `--pruned partition` (V25, 4 shards: raw
sets pairwise disjoint, every target exactly one branch owner, sum ==
71,539) — PASS.

### 3.2 V35 exact reproduction (production scale)

`validate_v45_enumeration.py --pruned v35` (2026-09-19, systemd transient
`v45-v35-pruned`, log `/tmp/opencode/v45_validation/v35_pruned.log`):

- **15,289,669 targets in 5,031 s (~84 min)** + ~134 s reference pass —
  vs the original engine's projected ~44–47 h (~30× speedup).
- Per-min-id counts match the reference histogram on **all 489 hist keys**
  (mismatches = 0); **zero** targets on all 1,241 non-hist candidates;
  every hist key covered; per-bucket masks unique (no duplicated
  ownership); histogram sums to the total.
- Peak RSS 7.2 GB (reference pass) / ~0.1–0.4 GB during enumeration.

### 3.3 V45 min-id-3590 subtree (George's bucket)

`validate_v45_enumeration.py --pruned george` (2026-09-19):

- **Authoritative min-id-3590 subtree total: 22,877,932 targets** in
  1,638 s (~27 min), peak RSS ~6.1 GB.
- The historical figures are consistent lower bounds / a misread: run2 /
  run3 (original engine, same enumeration) reached 14.2M / 20,342,912
  before RAM safety stops; the 2026-09-11 smoke test's "3,430,348" was a
  leaf **position** (the walk stopped at George), not a total.
- Static checks: George target 45 cells / face-connected / CK6-closed;
  canonical id `oh-109166b4c83a`; min orbit id 3590, orbit cost 22;
  V45 start_front == {3652, 3937}; OLD prefilter excludes 3590 (bug
  reproduced); CORRECTED filter accepts 3590 with domain == 3,696 min-ids.

### 3.4 George witness provenance

- Target: George's B-9 construction, canonical id **`oh-109166b4c83a`**,
  min orbit id **3590**.
- Yielded **exactly once** by bucket 3590 — at **leaf #2,488,006** in the
  pruned DFS order (59 s into the walk).  The original engine's order
  placed it at leaf #3,430,348; the target set is identical.
- Known covers: **12** (repo-M smoke; M-tileable construction).
- The witness is recorded by the driver's own audit path
  (`_record_witness` → `witness_XX_NNN.json` in the shard workdir) with
  full-O_h canonical form, proper-rotation canonical form, cover count,
  symmetry order/kinds/class.

## 4. Exact shard plan

Source: `data/ck6_reuse/ck6_v45_shards_corrected.json` (git-tracked;
planner `corrected-sound-filter`; generated by
`solvers/ck6_sharding_corrected.build_corrected_plan(45, 8)`).

| Shard | Min-id range | Count |
|---|---|---|
| 0 | [0..461] | 462 |
| 1 | [462..923] | 462 |
| 2 | [924..1385] | 462 |
| 3 | [1386..1847] | 462 |
| 4 | [1848..2309] | 462 |
| 5 | [2310..2771] | 462 |
| 6 | [2772..3233] | 462 |
| 7 | [3234..3937] | 462 |

- **3,696 candidates total, each owned by exactly one shard** (no
  duplicates; startup assertion).
- Min-id **3590** (George) is in shard 7; min-ids **3652 and 3937** (the
  V45 start-front orbits) are in shard 7; min-id 0 (the centre orbit) is
  in shard 0.
- The driver asserts at startup: volume == 45; planner ==
  `corrected-sound-filter`; n_candidates == 3,696; 3,696 unique ids;
  3590/3652/3937 present; plan file == fresh `build_corrected_plan(45, 8)`;
  plan min-ids == `corrected_candidate_min_ids(un)`; retired total
  1,469,999 never used as an expectation.

## 5. Production command

```bash
# orchestrator (default: 2 parallel workers, 5 re-launch retries per shard)
.venv/bin/python -u tools/frontier/run_v45_production.py --piece A

# single shard (worker mode; also what the orchestrator spawns)
.venv/bin/python -u tools/frontier/run_v45_production.py --piece A --shard 7
```

- `--piece` is required (choices = the 23 pentacubes).  Each piece is a
  separate workdir and a separate run.
- `--parallel 2` default: worst-case bucket ~6.1 GB RSS × 2 ≈ 12.2 GB
  peak, fits the 28 GB host (~25 GB available).  Do NOT raise to 4
  (~24.4 GB — too tight).
- `--max-retries 5` default: orchestrator re-launches any shard without a
  result file (crash recovery), resuming from its checkpoint.
- Workdir: `data/ck6_reuse/run/v45_<PIECE>/` (gitignored).

## 6. Expected output files

In the workdir `data/ck6_reuse/run/v45_<PIECE>/`:

| File | Meaning |
|---|---|
| `shard_XXX.json` | per-shard result; **atomic completion marker** (tmp + os.replace). Present only when the shard fully completed. |
| `shard_XXX.ckpt` | per-shard resume checkpoint (full worker state + per-min-id counts), written atomically after every min-id bucket; removed on completion. |
| `shard_XXX.log` | worker stdout/stderr (orchestrator mode). |
| `witness_XX_NNN.json` | per-witness records (SAT constructions), written by the audit path. |
| `final.json` | aggregate; written atomically **only when all 8 shards have result files**. Never a partial aggregate. |
| `STOP` | (operator-created) graceful-stop signal; see below. |

Plus one line appended to `data/ck6_reuse/piece_volume_results.jsonl` when
`final.json` is written.

## 7. Checkpoint / resume procedure

**Safe by construction — a killed shard is always restartable without
mixing partial and complete results:**

1. **Completion marker.**  `shard_XXX.json` is written atomically ONLY
   when the shard has fully completed.  A partial shard never looks
   complete; the orchestrator treats a missing result file as "not done".
2. **Checkpoint.**  `shard_XXX.ckpt` holds the FULL worker state (funnel
   counters, targets, sat/unsat, witnesses, per-min-id counts) and is
   written atomically after every completed min-id bucket.  On resume, the
   worker skips every min-id already in the checkpoint's `done` map and
   continues from the next bucket — no rework, no double counting.
3. **Stale/corrupt checkpoints.**  A checkpoint whose volume/piece/shard
   identity does not match, or that fails to parse, is discarded and the
   shard restarts fresh (never silently resumed from wrong state).
4. **STOP file.**  Creating `STOP` in the workdir makes workers exit
   cleanly after the current min-id bucket WITHOUT a result file (the
   checkpoint is preserved).  The orchestrator stops launching new shards
   once nothing is in flight.  Re-run the same command later to resume.
5. **Crash recovery.**  The orchestrator re-launches any shard without a
   result file, up to `--max-retries` per shard; each re-launch resumes
   from the checkpoint.  If a shard fails more than `--max-retries` times,
   the orchestrator aborts loudly (checkpoint preserved).
6. **Aggregate.**  `final.json` is written only when ALL shards have
   result files; the aggregate asserts internal conservation
   (sum of shard `targets` == sum of per-min-id counts) and runs the
   T-anchor check (a no-op for V45 — no anchor exists).

## 8. Expected resource envelope

- **RAM:** ~12.2 GB peak with `--parallel 2` (worst-case bucket ~6.1 GB ×
  2 workers).  Host: 28 GB / ~25 GB available.
- **Disk:** < 1 GB.  Result/checkpoint/log files are small JSON; the
  visited set is in-memory only (no SQLite visited DB in the production
  path — `count_minids_sqlite` is a validation tool).
- **Time:** unknown (the V45 total is unknown).  Bounds: the min-id-3590
  bucket alone took 27 min; the full run is expected to take hours to
  days across 8 shards × 2 workers.  Progress is visible per min-id bucket
  in the shard logs.

## 9. Remaining risks

1. **V45 total unknown** — the headline result of this run; no estimate
   beyond the 22,877,932 min-id-3590 subtree.
2. **Runtime uncertainty** — hours to days; mitigated by per-bucket
   checkpoints (resume is lossless) and the STOP protocol.
3. **`limits=` parameter on `iter_targets_seeded` is accepted but not
   enforced** (pre-existing dead code; the production path does not use
   it).
4. **Witness volume** — every SAT target writes a witness file; if the
   SAT count is large, disk usage grows (still expected ≪ 1 GB).
5. **Machine contention** — the host also runs the OpenWork desktop app;
   `--parallel 2` leaves headroom, but a concurrent heavy process could
   slow buckets (not corrupt them).
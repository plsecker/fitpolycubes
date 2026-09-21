# V45 SQLite Production Readiness Review

Review date: 2026-09-21.  Scope: is the SQLite-backed V45 production
implementation (commit `7a32c09`, plus the issue-#3 orphan-guard
integration in `297d3e6`) ready for the first real bucket-1022
production run?  This is a review only — nothing was launched.

## 1. What the 504-test SQLite suite has already proven

`tools/frontier/test_v45_sqlite_bucket.py` — 504 checks, all PASS
(verified 2026-09-21; exit 0):

- **Traversal equivalence**: `iter_targets_seeded_connected_sqlite`
  yields exactly the same target sets and state counts as the in-memory
  `iter_targets_seeded_connected` on V5 (all 6 min-ids), V15 (all 159),
  and V25 (3 smallest + 2 largest buckets).  Provably-empty buckets
  create no database.
- **Crash-safe resume**: two-stage resume (stop at a checkpoint
  boundary) loses no targets (stage1 ∪ stage2 == memory), duplicates
  none (disjoint), and redoes nothing (state counts add up); a killed
  bucket (exception mid-consumer, simulating SIGKILL) resumes from the
  last checkpoint with redo bounded by one checkpoint interval.
- **Re-entry and staleness**: a completed bucket re-enters cleanly
  (nothing re-yielded, caller state restored, `info.completed`);
  a run_id mismatch discards the stale database and starts fresh.
- **STOP semantics**: `BucketStopped` is raised at a checkpoint
  boundary, the bucket is not marked complete, and it resumes
  correctly.
- **Driver integration**: resumed buckets are recorded with their TOTAL
  target count (`info.targets`), and a STOP mid-bucket is not recorded
  as done (no silent truncation on resume).
- **Validation counts unchanged** with the SQLite path in place:
  V5 = 2, V15 = 368, V25 = 71,539 (`--pruned small`), V35 = 15,289,669
  (`--pruned v35count`); `test_ck6_sharding_bug.py` passes.

## 2. What remains untested or operationally risky

1. **The production generator has never run at scale.**  The 312.3 GB /
   14 h 45 m bucket-1022 numbers come from a standalone benchmark
   (`measure_bucket1022_sqlite.py`, artifacts since removed from
   `/tmp`), not from `run_v45_production.py`.  The benchmark used the
   same traversal discipline and SQLite schema/PRAGMAs (WAL,
   synchronous=NORMAL, 1 GiB cache, WITHOUT ROWID BLOB visited table)
   and ran in 8 resumable segments, all rc=0 — but the production
   driver additionally pickles the caller state (funnel Counter, etc.)
   at each checkpoint.  That overhead is small (~705 s of
   checkpoint-commit/resume overhead was already measured in the
   benchmark) but is not exercised end-to-end by the production driver.
2. **Full-run disk requirement is unknown.**  Bucket 1022 alone is
   312.3 GB for a single target.  The total for all 3,696 min-ids is
   not measured; a multi-TB estimate is plausible.  Current free disk
   is 846 GB (see §4), so the FULL run cannot complete without
   `--prune-dbs` (explicit deletion of COMPLETE bucket databases).
3. **Throughput at scale.**  ~11.3k states/s average (53k/s early,
   degrading as the B-tree outgrows the 1 GiB cache) → ~14 h 45 m per
   heavy bucket.  Total wall-clock for the full run is days-to-weeks,
   not hours.
4. **First real pre-SQLite → SQLite checkpoint transition.**  The
   existing `shard_002.ckpt` / `shard_003.ckpt` carry no `run_id`
   (pre-SQLite).  On resume the driver generates a fresh run_id and
   starts bucket databases from scratch — the run_id-mismatch path is
   unit-tested, but this is its first production use.
5. **Orphan-guard integration (issue #3) is new.**  The orchestrator
   now registers itself and its workers in
   `data/ck6_reuse/openwork_jobs.jsonl`.  Report-only and unit-tested,
   but unexercised in production.  Note: a worker launched directly
   (`--shard N`, not via the orchestrator) is NOT auto-registered.
6. **Mid-run WAL/disk peak.**  The benchmark checkpointed on close; the
   production generator commits at `ckpt_every = 2_000_000` states, so
   the WAL stays bounded, but the peak (DB + WAL) during a live run is
   not directly measured.  Budget ~1.15× the final DB size.
7. **STOP / `--max-seconds` at scale.**  Both are unit-tested
   (including driver STOP mid-bucket) but never exercised on a
   multi-hundred-GB bucket.

## 3. Exact command to resume bucket 1022

Bucket 1022 is the next bucket in shard 2 (shard 2 = min-ids 924..1385;
`shard_002.ckpt` has 98/462 done, last = 1021, pre-SQLite run_id).
Recommended focused command (single worker, bounded disk, validates the
production path on the known-heavy bucket before scaling out):

    python tools/frontier/run_v45_production.py --piece A --shard 2

This resumes shard 2 at bucket 1022 with a fresh run_id and creates
`data/ck6_reuse/run/v45_A/bucket_1022.sqlite`.  Operational notes:

- Run directly (not via the orchestrator) → register it manually for
  orphan detection if desired:
  `python tools/frontier/orphan_check.py --register --pid <pid> --ppid <ppid> --cmd "run_v45_production.py --piece A --shard 2" --done-file data/ck6_reuse/run/v45_A/shard_002.json`
- Optional safety cap: add `--max-seconds <N>` (checkpointed at the
  cap; the bucket resumes on re-launch).
- The full orchestrator resume (all pending shards 2–7, 2 workers by
  default) is `python tools/frontier/run_v45_production.py --piece A`
  — NOT recommended for the first bucket-1022 run, because it launches
  two heavy buckets concurrently (~2× disk).

## 4. Expected disk usage and conservative minimum free-disk requirement

- Bucket 1022: **312.3 GB** final DB (529.5 B/state × 589,769,226
  states).  Conservative peak during the run (DB + bounded WAL):
  **~360 GB**.
- **Conservative minimum free disk to start bucket 1022: 400 GB**
  (312.3 GB × 1.15 + 50 GB margin for logs/checkpoints/other work).
- Current free disk: **846 GB** (`/dev/sda2`, 1.3 T total, 29% used) —
  sufficient for bucket 1022 and roughly one more heavy bucket.
- Full run: total unknown, plausibly multi-TB → requires periodic
  `python tools/frontier/run_v45_production.py --piece A --prune-dbs`
  (deletes COMPLETE bucket databases only; incomplete/resume databases
  are never touched) or a partial-completion strategy.

## 5. Recommendation: GO for bucket 1022 — NOT-YET for the full run

**GO — start bucket 1022** with
`python tools/frontier/run_v45_production.py --piece A --shard 2`.
Evidence:

- 504/504 SQLite-suite checks pass; validation counts unchanged
  (V5/V15/V25/V35).
- The identical traversal + schema completed bucket 1022 at full scale
  in the benchmark: 589,769,226 states, 1 target, 312.3 GB, 14 h 45 m,
  peak RSS 1064 MiB (bounded), 8 resumable segments all rc=0.
- Disk: 846 GB free ≥ 400 GB conservative minimum.
- Resume path verified: pre-SQLite checkpoint → fresh run_id → clean
  bucket start; crash-safe mid-bucket resume proven by tests.

**NOT-YET — full production run** (all 3,696 min-ids): the multi-TB
disk estimate exceeds the 846 GB available without a `--prune-dbs`
policy, and total wall-clock is days-to-weeks.  Recommended sequence:
(1) run bucket 1022 as the production-scale validation; (2) on success,
establish the prune policy and re-assess the full-run disk budget.

Constraints honored: no V45 launched, bucket 1022 not started, no
solver algorithm changes, no existing databases/checkpoints/logs/
untracked artifacts deleted.
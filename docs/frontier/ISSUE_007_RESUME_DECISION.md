# Issue #7: Safe V45 continuation after bucket 1022 — decision

Status: analysis complete; recommendation below. **Nothing in this document has
been executed** — no V45 job, solver, DB, checkpoint, or log has been modified.

## Current state (verified 2026-09-23)

- Shard 2 (piece A, volume 45) stopped at the 20 h shard cap mid-bucket 1257:
  `bucket_1257.sqlite` = 120.5 GB, 248,000,000 states, 0 targets, run_id
  `a2edf575429c4ccdb653d4acbe878cbe` (matches `shard_002.ckpt` → resumes exactly).
- Bucket 1022 complete: 589,769,226 states, 1 target, 312.3 GB DB, 56,200 s
  (15.6 h). `shard_002.ckpt`: 333/462 min-ids done (924–1256), 1 target total.
- Disk `/dev/sda2`: 1.3 T, 733 G used, **443 G free**.
- Remaining shard 2 work (min-ids 1257–1385, 129 buckets): only **11 buckets
  actually run** — 1257, 1279, 1301, 1302, 1303, 1304, 1305, 1326, 1327, 1328,
  1349 — the other 118 are provably empty (connectivity/cells_ge prune, 0 MB,
  0 s). Each run bucket is full-size (~500–590 M states, ~250–312 GB, ~13–16 h).

## Decision 1 — Resume bucket 1257: FEASIBLE

Bucket 1257's search is structurally identical to bucket 1022's (verified:
identical checkpoint pattern and stack sizes at all 37 shared checkpoints; both
are non-bridged, so both start with `cc_adj = {3652, 3937}`, and the orbits
between them are unreachable within the cost budget — see appendix). Therefore
bucket 1257 will enumerate the same ~589.8 M states as 1022.

- Remaining: ~342 M states (589.8 M − 248 M).
- Disk: ~165 GB more (342 M × ~486 B/state) → final DB ~286 GB. 443 GB free →
  feasible; ~278 GB free after.
- Time: ~6–9 h (22,000 s at the current 15.5 k states/s; 33,000 s at bucket
  1022's 10.5 k/s average) → completes within a fresh 20 h run.

## Decision 2 — Retention: keep 1022 until 1257 completes; pruning required to continue

- Under current retention (keep every completed DB), bucket 1257 is the **last
  completable bucket**: the next run bucket (1279) needs ~312 GB but only
  ~278 GB would be free.
- To continue past 1257, prune completed DBs after each audited bucket
  (`--prune-dbs`, or manual `rm`). The driver's `--prune-dbs` deletes only
  DBs whose meta has `complete == '1'`; incomplete/resume DBs are never touched.
- Audit loss from pruning: the visited set (589.8 M masks for 1022) and meta.
  Surviving evidence: `shard_002.log` (progress, checkpoint pattern, completion)
  and `shard_002.ckpt` (done ledger, run_id). The search is deterministic and
  reproducible (int hashes are stable; same code + plan → same search), so the
  visited set is regenerable by a ~15.6 h re-run.
- Recommendation: complete 1257 first (no pruning). Then either
  (a) stop the shard and keep all DBs as evidence, or
  (b) audit each completed bucket (log + meta), prune it, and continue one
  bucket at a time. Option (b) keeps the shard moving with ~250–280 GB free at
  all times.

## Decision 3 — Free-space floor: ~100 GB, enforced manually via STOP file

- The driver has **no disk-based stop check**. The only stop mechanisms are
  `--max-seconds` (shard-relative cap → SearchLimit) and the STOP file
  (checked at checkpoint boundaries → BucketStopped); both commit a checkpoint
  and are resumable.
- WAL headroom: checkpoints are irregular (leaf-skip; see appendix); the
  largest observed gap is 26 M states → ~14 GB of WAL between commits.
- Floor = WAL headroom (~14 GB) + DB growth during the stop delay (~14 GB) +
  margin → **recommend 100 GB** (50 GB is the absolute minimum).
- Implementation: monitor `df -h /dev/sda2`; place `data/ck6_reuse/run/v45_A/STOP`
  when free space < 100 GB. The stop takes effect at the next checkpoint
  (≤ 26 M states ≈ 30 min) and is clean/resumable.

## Decision 4 — Scheduling: shard 2 alone

- Do not launch other shards: each run bucket needs ~250–312 GB; concurrent
  shards would exhaust the disk. Shard 2's remaining work is bounded (11 run
  buckets + 118 empty).

## Decision 5 — 20 h cap: keep

- Bucket 1022 (15.6 h) completed within the cap; bucket 1257 needs ~6–9 h more
  → completes within a fresh 20 h run.
- The cap is shard-relative (`t0` set at shard start); each resume gets a fresh
  budget. The cap preserves the mid-bucket checkpoint (SearchLimit → resumable),
  so it is safe.

## Decision 6 — Resume procedure (NOT executed)

1. Pre-flight:
   - `git fetch origin frontier-solutions && git merge --ff-only` → clean.
   - `python tools/frontier/orphan_check.py --check` → no orphans; never touch
     PIDs 169817/169818/169726 (separate unregistered hybrid-solver job).
   - `df -h /dev/sda2` → free ≥ 300 GB.
   - Verify `shard_002.ckpt`: 333/462 done, run_id `a2edf575429c4ccdb653d4acbe878cbe`.
   - Verify `bucket_1257.sqlite`: 120.5 GB, run_id matches (resumes exactly).
2. Launch via a transient systemd unit (survives shell logout):
   `python tools/frontier/run_v45_production.py --piece A --shard 2 --max-seconds 72000`
   (NO `--prune-dbs`).
3. Monitor: tail `shard_002.log`; watch free space; place the STOP file if
   free < 100 GB.
4. After completion: audit bucket 1257 (meta `complete == '1'`, states
   ≈ 589.8 M, targets), update `docs/frontier/OPENWORK_INBOX.md`, then decide
   on pruning for bucket 1279+ (Decision 2).

## Appendix — checkpoint cadence (investigation note)

- The checkpoint block (`if states % ckpt_every == 0:` → write_meta / commit /
  BEGIN / print) sits at the bottom of the loop body, but leaf states
  (`rem == 0`) hit `continue` before it. So a checkpoint fires at a
  `ckpt_every` multiple only when the state at that count is a non-leaf →
  irregular gaps (observed: 2 M, 10 M, 14 M, 16 M, 28 M, …; largest gap
  26 M states). This is a code behavior, not a bug.
- Confirmed empirically: a controlled run with `ckpt_every = 100_000` fired at
  200 k, 900 k, 1.2 M, 1.6 M, 1.8 M, 1.9 M, 2 M — not at every 100 k.
- Buckets 1022 and 1257 show identical patterns because both are non-bridged
  (`s ∉ start_front = {3652, 3937}`) → identical `cc_adj = {3652, 3937}`, and
  the orbits between them are unreachable within the rem budget (minimum
  cost-constrained path from the start frontier to any orbit in [1023, 1256]
  is ≥ 23 > rem 20). Both searches therefore explore the same orbit set in the
  same order.
- Implication: WAL headroom is bounded by the largest observed gap (~14 GB);
  the ~100 GB floor covers it.
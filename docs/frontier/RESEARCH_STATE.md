# Frontier Research State — Hand-off Document

**Purpose**: single source of truth for the current state of the frontier research
(V45/CK6 enumeration, EE4, catalogue audits) as of **2026-09-21**. Written as a
hand-off for ChatGPT / future sessions. Every claim below was verified against
local files, logs, checkpoints, git history, and process state on this machine
(`/home/philip/Work/fitpolycubes`, branch `frontier-solutions`).

**Machine**: 28 GiB RAM, 8 GiB swap, ~1.3 TB disk (~551 GB free).
**No solver processes are currently running** (verified via `ps`).

> **STALE MARKER (2026-09-22)** — the claim above ("No solver processes are
> currently running") is superseded: the bucket-1022 production job
> (`v45-bucket1022.service`, PID 42188) has been running since 2026-09-22
> 07:14 NZST. Live job state is tracked in `docs/frontier/OPENWORK_STATUS.md`
> (§ "Current V45 job"). Per `docs/agent_control_protocol.md` §8, this stale
> claim is marked rather than silently rewritten; refresh the affected
> sections (§1, §7) on the next task that touches V45 state.

---

## 1. Workstreams at a glance

| Workstream | Status | Latest verified result |
|------------|--------|------------------------|
| V45 CK6 enumeration (production) | **INCOMPLETE** — memory wall RESOLVED (SQLite visited set integrated, tested); run not yet resumed | Engine validated; production run incomplete, stopped at bucket 1022 |
| CK6 sharding repair / George B-9 | RESOLVED | Corrected 3,696-min-id domain; B-9 = min-id 3590, 12 covers in repo-M |
| EE4 (R pentacube) | RESOLVED | Matches George's `5-17p.png` exactly; 4 canonical EE4 targets |
| Catalogue impossibility-rule audits | Mostly committed; 1 action pending | K/V `cube` rule removed; B metadata removed; W `(4,5)` rule still to remove |
| George package / small positives | RESOLVED | L-V25-S1 improves George's L minimum (11 → 5) |
| Shirakawa corpus audit | COMPLETE (committed) | 416 concrete records; S 5×6×28 misclassification fixed |
| Compact-state representation | **INCONCLUSIVE / CONTRADICTED** | Per-depth run does NOT fit bucket 1022 in 28 GiB |

---

## 2. V45 CK6 enumeration (main active workstream)

### 2.1 Validated engine (authoritative)

- **Engine**: `iter_targets_seeded_connected` (connectivity-pruned enumerator) in
  `solvers/t_ck6_oddity_v35_search.py`; harness `tools/frontier/validate_v45_enumeration.py`;
  production driver `tools/frontier/run_v45_production.py` (the ONLY sanctioned driver;
  `t_ck6_reuse_multipiece.run_combo` refuses V45). Budget = 22.
- **Validated counts** (from `docs/frontier/v45_enumeration_validation.md` and
  `docs/frontier/george_v45_campaign_plan.md`):
  - V5 = **2**, V15 = **368**, V25 = **71,539** — raw-set equality with the reference
    enumerator (`iter_targets_seeded`); canonical forms match brute force; per-min-id
    counts match the reference histogram; no dups; determinism and 4-shard partition checks pass.
  - V35 = **15,289,669** in 5,031 s (~84 min) — matches reference histogram on all 489
    keys, zero targets on all 1,241 non-histogram candidates, no duplicated ownership.
  - V45 min-id 3590 subtree = **22,877,932** in 1,638 s (~27 min), peak RSS ~6.1 GB;
    George's B-9 target (oh-109166b4c83a) yielded **exactly once**.
  - Completeness proof: spanning-tree ordering rooted at the centre cell.
- **Corrected domain**: 3,696 min-ids (`data/ck6_reuse/ck6_v45_shards_corrected.json`,
  `solvers/ck6_sharding_corrected.py`). Buckets 0–1021 are **provably empty**; bucket
  1022 is the first leaf-bearing bucket.
- **Retired corpus**: the old V45 total of **1,469,999 targets** (86 min-ids ≥ 3652,
  "V=45 PROVEN NEGATIVE") came from the unsound min-id pre-filter that excluded min-id
  3590 and is **never used as an expected value**. The backup
  `data/ck6_v45_buggy_backup_20260916_083816/` contains only empty new-format stubs
  (minid_counts.json: 3,938 zero entries, total=0; 4 empty shards). The retired corpus
  survives only in git history. **No valid V45 total exists yet.**

### 2.2 Production run state — INCOMPLETE, STOPPED

`data/ck6_reuse/run/v45_A/` (all timestamps 2026-09-19):

| Artifact | State |
|----------|-------|
| `shard_000.json` | complete, 0 targets (min-ids 0–461) |
| `shard_001.json` | complete, 0 targets (min-ids 462–923) |
| `shard_002.ckpt` | 98/462 min-ids done (924–1021, all 0 targets) — stopped inside bucket 1022 |
| `shard_003.ckpt` | 134/462 min-ids done (1386–1519, all 0 targets) |
| `shard_002.json`, `shard_003.json`, `final.json` | **do not exist** |

- `shard_002.log` shows three sections: initial run 924–1021; a resume attempt that
  crashed with `KeyError: 'reject: <k contained placements'`; a final resume attempt
  (after the fix) that ends abruptly with no traceback — consistent with an OOM kill.
- `shard_003.log` crashed with the same KeyError on resume.
- **Root cause of the KeyError** (fixed in commit `2dbb229`, HEAD): checkpoint JSON
  round-trip turns the funnel `Counter` into a plain `dict`; on resume
  `dict[missing] += 1` raised `KeyError`. Fix: re-wrap the loaded funnel dict as a
  `Counter` in `run_shard`.
- **OOM record** (journalctl, both in bucket 1022):
  - 2026-09-19 14:59:53 — `v45-prod-A.service` pid 96907 killed, anon-rss **14.9 GiB**
    (matches "r1, parallel 8" in `v45_memory_bottleneck.md`).
  - 2026-09-19 16:41:12 — `v45-prod-A-r3.service` pid 129619 killed, anon-rss **27.6 GiB**
    (matches "r3, parallel 1, funnel fix").
- **Conclusion**: the in-memory visited set cannot complete bucket 1022 within 28 GiB.
  **RESOLVED by the SQLite production integration (see §2.7)**: the driver now enumerates
  every bucket with a SQLite-backed visited set (`iter_targets_seeded_connected_sqlite`),
  bounded RSS, crash-safe mid-bucket resume.

### 2.3 Bucket-1022 SQLite benchmark — COMPLETE, VERIFIED (the fix that works)

Per `docs/frontier/v45_memory_bottleneck.md` and `/tmp/opencode/v45_validation/`:

- Bucket 1022 = **589,769,226 states, 1 target** (the B-9 target).
- SQLite-backed visited set: **312.3 GB disk, 14 h 45 m wall, peak RSS 1064 MiB, rc=0**
  (~530 B/state on disk, ~11.3k states/s). Fits comfortably in the 28 GiB envelope.
- Database: `/tmp/opencode/v45_validation/bucket1022_visited.sqlite` (312,300,355,584 B, present).
- Scripts: `measure_bucket1022_sqlite.py`, `monitor_bucket1022.py`, notes in
  `notes_bucket1022.md` (segmented/checkpointed resume verified to do no rework; two
  STOPPED caps at 108M and 205.5M states; supervisor died 22:15–22:19, new supervisor 22:19:56).

### 2.4 Compact-state research — INCONCLUSIVE, DOC CONTRADICTED BY MEASUREMENT

- `docs/frontier/v45_compact_state_research.md` (untracked) claims 24 B/live state →
  590M × 24 B ≈ 13.6 GiB "comfortably fits", plus a "validation table"
  (V5=12, V15=1,824, V25=78,640, V35=2,345,678) that **contradicts the authoritative
  validated counts** (V5=2, V15=368, V25=71,539, V35=15,289,669). **Treat this doc as a
  provisional draft, NOT authoritative.**
- Actual measurement (`/tmp/opencode/v45_validation/compact_v45_1022_full/`,
  `iter_targets_perdepth`, 2026-09-20 22:16 → 2026-09-21 07:40): RSS grew 4.3 GiB @ 10M
  states, 8.6 GiB @ 20M, 13.3 GiB @ 30M, then **"RSS 21274320 KiB exceeds limit, stopping
  compact45_1022_full.service"** at 21.3 GiB (~30M states) — i.e. ~443 B/state, extrapolating
  to ~260 GiB at 590M states. **Per-depth dedup does NOT fit bucket 1022 in 28 GiB.**
- Related untracked scripts at repo root: `benchmark_state_counts.py`,
  `benchmark_state_counts_small.py` (2026-09-20), `per_depth_benchmark.py` (2026-09-20 21:28);
  plus `tools/bfs_v45_1022_*.py`, `tools/bfs_layered*.py`, `tools/bench_*.py` (untracked).

### 2.5 Optimization status (from `v45_optimization_final_status.md`)

- `orbit_cells` speedup 1.16–1.22× — **keep**.
- Naive connectivity prune 0.07–0.71× — **SLOWDOWN, not safe**.
- Two stronger prune conditions attempted — **both INCORRECT**; no tractable stronger
  necessary condition found.
- min-id 3500 intractable with current engine (13,850 states/s, 0 targets).
- Early-pruning experiment documented in `v45_early_pruning_results.md`; variant lives in
  `solvers/t_ck6_oddity_v35_search_pruned.py` (untracked); baseline preserved.

### 2.6 V45 forensic audit (committed)

- `docs/frontier/v45_architecture_audit_final.md` (2026-09-18): WORKTREE FREEZE NOTICE —
  V45 material frozen; no complete trustworthy V45 enumeration exists; old corpus retired;
  backup partial (empty stubs); `tools/reconstruct_v45_frontier.py` broken (IndentationError);
  `v45_v_3590_*` runs are partial experiments.
- `docs/frontier/v45_t_independent_reproduction_2026-09-18.md`: T-piece V45 with the OLD
  (buggy) engine: 1,469,999 targets, 86 min-ids, 1053 s — recorded as an independent
  reproduction of the engine as-implemented, NOT a valid result.
- `docs/frontier/v45_validation_run_crash.md` (2026-09-18): systemd-oomd killed george+v35
  runs at 19:40:01 (memory pressure 62.21% > 50%); both Python processes were children of
  the OpenWork app scope cgroup — host-level resource kill, not a solver bug.
- Partial min-id-3590 experiments (untracked dirs, all with STOP files = intentionally stopped):
  `data/ck6_reuse/v45_v_3590_run2/`, `v45_v_3590_run3/`, `v45_v_3590_complete/`
  (branch_3592..3597 complete, branch_3598 partial 25,536 B), `overnight_v45_3590/run/`,
  `v45_v_3590_forked/` (has `scheduler.pid` + `current_child.pid` — likely stale).
  `v45_v_3590_refined/` holds the complete 3590/3591 pair = **7,170,536 targets** plus 5
  child digests (3592, 3854, 3855, 3894, 3895) + manifest + run.log.

### 2.7 SQLite production integration — IMPLEMENTED, TESTED (this commit)

The §2.3 benchmark is now integrated into the production driver. The per-bucket visited
set is SQLite-backed; the mathematical search algorithm is **unchanged** (identical
traversal and target set to `iter_targets_seeded_connected` — the visited set is only a
membership test), and the corrected 3,696-min-id shard plan is untouched.

**Implementation** (single coherent commit):
- `solvers/t_ck6_oddity_v35_search.py`:
  - `iter_targets_seeded_connected_sqlite(un, min_id, budget, db_path, ckpt_every=2_000_000,
    run_id=None, state=None, info=None, stats=None, limits=None, stop_check=None)` — the
    seeded connected DFS with a WITHOUT ROWID BLOB visited table (same schema/PRAGMAs as
    the benchmark: WAL, synchronous=NORMAL, 1 GiB page cache). Crash-safe resume: DFS
    stack, counters and the caller's processing `state` are checkpointed into the same
    database in the same transaction as the visited-set inserts. `run_id` guards against
    reusing another run's database (mismatch → stale DB discarded). A completed bucket
    keeps its database marked `complete` (audit evidence; never auto-deleted).
  - `BucketRunInfo` (per-bucket metadata: db_path, run_id, resumed, completed, targets,
    states), `BucketStopped` (raised by `stop_check` at a checkpoint boundary).
- `tools/frontier/run_v45_production.py`:
  - Every bucket now enumerates via the SQLite generator; bucket DBs live in the workdir
    as `bucket_XXXX.sqlite` (deterministic, persistent — not `/tmp`).
  - `run_id` persisted in `shard_XXX.ckpt`; bucket DBs are validated against it.
  - **STOP-file bug fixed**: a STOP mid-bucket no longer records the partial bucket as
    done (the old code did, silently truncating the bucket on resume); the in-flight
    bucket resumes from its SQLite checkpoint on the next invocation.
  - **Resume accounting fixed**: `done[s]` records the bucket TOTAL (`info.targets`), not
    just the targets re-yielded after a mid-bucket resume.
  - Logging per bucket: min-id, target count, cumulative, DB path + size, elapsed.
  - `--max-seconds` (safety cap per bucket, checkpointed/resumable) and `--prune-dbs`
    (explicit cleanup of COMPLETE bucket DBs only; incomplete/resume DBs never touched).
- `tools/frontier/test_v45_sqlite_bucket.py` — 8 test groups, **498 checks, all PASS**:
  1. SQLite == in-memory target sets and state counts on V5 (all 6 min-ids), V15 (all
     159), V25 (3 smallest + 2 largest buckets); provably-empty buckets create no DB.
  2. Two-stage resume (max_states stop at a checkpoint boundary): no lost targets
     (stage1 ∪ stage2 == memory), no duplicated targets (disjoint), no redo
     (stage1 + stage2 states == total).
  3. Killed/interrupted bucket (exception inside the consumer, simulating SIGKILL):
     resumes from the last checkpoint, no lost targets, redo bounded by one checkpoint
     interval.
  4. Completed-bucket re-entry: nothing re-yielded, `info.completed`, caller state
     restored from the final checkpoint.
  5. run_id mismatch: stale DB discarded, fresh start == memory.
  6. STOP semantics: `BucketStopped` raised, bucket not marked complete, resume completes.
  7. Driver integration (monkeypatched generator): resumed bucket recorded with TOTAL
     targets; state consistent with per-min-id.
  8. Driver integration: STOP mid-bucket → bucket NOT recorded as done, no result file,
     run_id preserved.

**Validation counts unchanged** (re-run 2026-09-21 with the new code in place):
- `validate_v45_enumeration.py --pruned small` — V5 = **2**, V15 = **368**,
  V25 = **71,539**, all PASS (raw-set equality, canonical == brute force, per-min-id ==
  reference hist, no dups).
- `validate_v45_enumeration.py --pruned v35count` — V35 = **15,289,669** (489 min-ids,
  range [558..1857]), PASS.
- `tools/frontier/test_ck6_sharding_bug.py` — V25 corrected sharding == 71,539, PASS.

**Exact command to resume the production run** (from repo root, branch
`frontier-solutions`):

    python tools/frontier/run_v45_production.py --piece A

The orchestrator re-launches every shard without a result file (shards 2–7); each worker
resumes its `shard_XXX.ckpt` and each bucket resumes from its `bucket_XXXX.sqlite`
mid-bucket checkpoint. Expected cost per heavy bucket: ~14 h 45 m at ~11.3k states/s,
~530 B/state disk, <1.1 GiB RSS (bucket 1022 alone = 312.3 GB disk). Disk budget note:
completed bucket DBs are kept as audit evidence; remove them explicitly with
`python tools/frontier/run_v45_production.py --piece A --prune-dbs` (deletes COMPLETE
databases only).

---

## 3. CK6 sharding repair / George B-9 (RESOLVED)

- Sharding bug identified and corrected: `docs/frontier/ck6_sharding_bug.md`,
  `ck6_v45_sharding_repair.md`, `data/ck6_reuse/ck6_v45_sharding_repair.json`,
  `ck6_sharding_bug_regression.json`; corrected plan = 3,696 min-ids.
- **B/M letter swap** (repo letters vs Sicherman page letters): repo B = junction =
  Sicherman M; repo M = tip = Sicherman B (`docs/frontier/george_b9_letter_mapping.md`).
- George B-9 = min-id 3590; repo-M yields **12 covers**, repo-B 0.
- Historical corpus incomplete; low-min-id enumeration expensive.

---

## 4. EE4 (RESOLVED)

- R pentacube, 5-copy EE4 construction **matches George's `5-17p.png` exactly**
  (`docs/frontier/ee4_R_oddity.md`, `docs/frontier/george_oddities_current_status.md`).
- 2,072,331 connected 25-cell EE4 targets considered → 16 R-tilings → **4 canonical
  EE4 targets**; `tests/fixtures/ee4_R_5.json` = canonical target #1 ("wall").
- Coordinate-frame bug fixed; `tests/test_ee4_coordinate_frame.py` protects the regression;
  also `tests/test_ee4_R_classification.py`, `tests/test_ee4_R_witness.py`.
- Classification data in `data/ee4_R_5/` (class_M1_*/class_M3_*/*M9* pngs);
  `data/ee4_george_comparison.json` (untracked).
- Commits: `68caf52` (EE4 classify 5-R dual-orthogonal oddities), `8ee5310` (ee4 info),
  `1aa6957` (fix), `7a8ce45` (Resolve EE4 George construction merge).

---

## 5. Catalogue impossibility-rule audits

**Committed** (2026-09-17/18): `8e44ea7` "Audit and correct catalogue impossibility rules"
modified `catalogues/{b,f,k,s,v,w}_catalogue.py`, `solvers/decomp.py`,
`tools/audit_catalogue.py`; `297bfb9` "Update final impossibility rule inventory with Y
piece and corrected counts" added `docs/frontier/final_impossibility_rule_inventory.md`
(per-piece rules with provenance/status: RESOLVED / UNRESOLVED / UNSUPPORTED).

**Actions already taken**:
- K/V `cube` rule (`a == b == c`) **removed** (2026-09-17).
- B `SEARCHED_NO_SOLUTION` metadata **removed** for 2×5×10, 2×5×13, 2×5×15, 2×5×16.
- F contradictions fixed; S 5×6×28 misclassification fixed (`e91e842`); S 8×10×14
  (SEARCHED_NO_SOLUTION) proven tileable.

**Still open / actionable**:
- **W `(4,5)` rule contradiction** (`docs/frontier/remaining_actionable_catalogue_audit.md`):
  `Box(4,5,6)` is listed in `RAW_PRIMES` as a published prime (line 54) but classified
  impossible → recommended action: **remove the rule block** (needs human approval).
- M rule `(6,6)` remains unresolved (`fmp_blanket_rule_audit.md`).
- R `a==2`/`a==3`, E `2×3×N`/`3×3×N`/`2×5×odd` blanket rules: UNRESOLVED (over-strong,
  no provenance, not disproved) — document provenance (`next_catalogue_rule_audit.md`).
- W `a==2`, Z `a<=2`: UNRESOLVED; N `a<=1`: VALID (`wzn_blanket_rule_audit.md`).
- `prime_impossible_conflict_audit.md`: 20 pieces, 781 prime boxes scanned, **no
  contradictions found**.

**Untracked audit docs (not yet on the branch)**: `cross_piece_cube_rule_audit.md`,
`cross_piece_impossibility_audit.md`, `fmp_blanket_rule_audit.md`,
`next_catalogue_rule_audit.md`, `prime_impossible_conflict_audit.md`,
`remaining_actionable_catalogue_audit.md`, `wzn_blanket_rule_audit.md`,
`s_piece/{derived,published}_impossibility_audit.md`, `b_piece/searched_no_solution_audit.md`,
plus regression tests `solvers/test_decomp_{b,f,kv,m,s,w}_contradiction.py`.

---

## 6. George package / small positives (RESOLVED)

`data/ck6_reuse/george_package/` (README.txt, summary.txt, b_v15/, l_v25/):
- **B-V15-S1**: 3 B pieces form a 15-cell connected polycube with exact CK6 symmetry,
  **congruent to George's published M-3 figure** (oh-0216334782e8) — independent
  confirmation, NOT an improvement.
- **L-V25-S1**: 5 L pieces form a 25-cell connected polycube with exact CK6 symmetry —
  **genuine improvement** over George's published L minimum of 11.
- `data/ck6_reuse/piece_volume_results.jsonl` (95 lines): B-piece volume-35 CK6 targets
  with cover counts (2/8/10 covers).

---

## 7. Long-running jobs — status

| Job | Status | Evidence |
|-----|--------|----------|
| Bucket-1022 SQLite benchmark | **COMPLETE** (14 h 45 m, peak RSS 1064 MiB, rc=0) | `/tmp/opencode/v45_validation/` |
| V35 full validation | COMPLETE (5,031 s) | `v45_enumeration_validation.md` |
| V45 min-id 3590 subtree | COMPLETE (1,638 s) | `v45_enumeration_validation.md` |
| V45 production `v45_A` shards 0–1 | COMPLETE (0 targets) | `data/ck6_reuse/run/v45_A/` |
| V45 production shards 2–7 | **STOPPED** (OOM at bucket 1022; shard_002/003 checkpoints exist) | `data/ck6_reuse/run/v45_A/` |
| Compact per-depth run `compact45_1022_full` | **STOPPED** at 21.3 GiB RSS (~30M states) | `/tmp/opencode/v45_validation/compact_v45_1022_full/` |
| `v45_v_3590_*` experiments | STOPPED (STOP files present; partial) | `data/ck6_reuse/` |
| Anything else | **Nothing running now** | `ps` |

---

## 8. Key files and scripts

- `solvers/t_ck6_oddity_v35_search.py` — engine: `iter_targets_seeded`,
  `iter_targets_seeded_connected`, `iter_targets_seeded_connected_sqlite` (SQLite-backed
  visited set, crash-safe resume), `count_minids_sqlite`, monolithic-sqlite CLI mode.
- `solvers/ck6_sharding_corrected.py` — corrected 3,696-min-id shard plan.
- `tools/frontier/run_v45_production.py` — production driver (SQLite-backed visited set
  per bucket; run_id; STOP-mid-bucket fix; `--max-seconds`, `--prune-dbs`).
- `tools/frontier/test_v45_sqlite_bucket.py` — SQLite bucket tests (equivalence,
  two-stage/killed/STOP resume, re-entry, run_id mismatch, driver integration).
- `tools/frontier/validate_v45_enumeration.py` — validation harness.
- `tools/frontier/analyze_george_figure.py`, `tools/frontier/audit_s_published_impossible.py`,
  `tools/frontier/audit_prime_impossible_conflicts.py` (last two untracked).
- `tools/full_scan_v45.py`, `tools/sample_scan_v45.py`, `tools/reconstruct_v45_frontier.py`
  (broken — IndentationError) — all untracked.
- `tests/test_ee4_coordinate_frame.py`, `tests/test_ee4_R_classification.py`,
  `tests/test_ee4_R_witness.py`, `tests/fixtures/ee4_R_5.json`.
- `data/ck6_reuse/ck6_v45_shards_corrected.json`, `data/ck6_reuse/run/v45_A/`,
  `data/ck6_reuse/george_package/`, `data/ck6_reuse/piece_volume_results.jsonl`.
- `/tmp/opencode/v45_validation/` — SQLite benchmark (measure/monitor scripts, notes,
  312.3 GB DB) and compact-state runs. **Note: `/tmp` is not persistent across reboots.**

---

## 9. Open research questions

1. **Per-piece V45 SAT/UNSAT verdict** for A, C, D, E, F, G, H, J, K, L, N, P, Q, R, S, T,
   U, V, W, X, Y, Z — requires completing the production run (blocked on memory wall).
2. **No valid V45 total exists yet** (1,469,999 retired; 3,696-min-id domain unenumerated).
3. **Stricter pruning condition**: none found; both stronger attempts were incorrect.
4. **Compact state representation**: measured ~443 B/state — does not fit bucket 1022 in
   28 GiB; the 24 B/state claim in `v45_compact_state_research.md` is unverified/contradicted.
5. **W `(4,5)` rule block removal** — actionable catalogue correction awaiting approval.
6. **M `(6,6)` rule** — unresolved.
7. **R/E blanket rules** — over-strong, no provenance; document or prove.
8. **min-id 3500** — intractable with the current engine (13,850 states/s, 0 targets).

---

## 10. Next recommended experiments

1. **DONE — SQLite-backed visited set integrated into `run_v45_production.py`** (see
   §2.7): per-bucket SQLite, identical traversal, crash-safe resume, tested. The next
   step is to **resume the production run**:
   `python tools/frontier/run_v45_production.py --piece A` (resumes shards 2–7 from
   `shard_XXX.ckpt` + `bucket_XXXX.sqlite`). Expected cost per heavy bucket: ~14 h 45 m
   at ~11.3k states/s, ~530 B/state disk, <1.1 GiB RSS.
2. After production V45 completes: derive per-piece SAT/UNSAT verdicts and the first
   valid V45 total.
3. Remove the W `(4,5)` impossibility rule block (catalogue correction; human approval).
4. Document provenance of the unresolved R/E/W/Z blanket rules.

---

## 11. Consistency cautions (things that LOOK authoritative but are NOT)

- **This document's own header claim** "No solver processes are currently
  running" (2026-09-21) — **STALE as of 2026-09-22**; the bucket-1022 job is
  running. See the stale marker at the top and `docs/frontier/OPENWORK_STATUS.md`.
- `docs/frontier/v45_compact_state_research.md` — validation table contradicts the
  validated counts; 24 B/state claim contradicted by the measured run. Draft only.
- `docs/v45_*.md` (top-level, e.g. `v45_next_steps.md`, `v45_search_coverage.md`,
  `v45_I_structure.md`, `v45_R_*.md`) — **stale**: based on the retired 1,469,999-target
  corpus. Superseded by `docs/frontier/george_oddities_current_status.md` and the
  `docs/frontier/v45_*` set.
- `data/ck6_v45/` and `data/ck6_v45_buggy_backup_20260916_083816/` — retired corpus /
  empty stubs; do not use as evidence.
- `data/ck6_reuse/run/v45_V/` — shards from 2026-09-08 (old-engine era, pre-freeze);
  not evidence for the corrected pipeline.
- `data/ck6_reuse/v45_v_3590_forked/` — `scheduler.pid`/`current_child.pid` likely stale;
  no process is running.
- `tools/reconstruct_v45_frontier.py` — broken (IndentationError); do not run.
- `v45_t_independent_reproduction_2026-09-18.md` — reproduces the OLD buggy engine; not a
  valid V45 result.

---

## 12. Git state

> **STALE MARKER (2026-09-22)** — the snapshot below is historical and is
> preserved as-is. As of 2026-09-22, verified: `origin/frontier-solutions`
> = `b32aed9` (agent-control protocol adoption); local `frontier-solutions`
> was in sync with origin at that time. Per `docs/agent_control_protocol.md`
> §8, stale claims are marked, not rewritten.

- Branch `frontier-solutions`, **ahead of origin by 3 commits**:
  - `HEAD` (this commit) — SQLite-backed visited set for production V45: new
    `iter_targets_seeded_connected_sqlite` generator, driver integration (run_id,
    STOP-mid-bucket fix, resume accounting fix, `--max-seconds`, `--prune-dbs`),
    `tools/frontier/test_v45_sqlite_bucket.py`, this document updated (§2.7).
  - `2dbb229` (2026-09-19) — fix: restore funnel Counter after checkpoint JSON
    round-trip (resume KeyError).
  - `cd8bf15` (2026-09-19) — Freeze validated V45 engine: pruned enumerator + corrected
    plan + production driver.
- Origin tip: `1aa6957` (2026-09-18).
- 94 untracked entries (docs, data, scripts listed above — including this document) —
  the "recent V35/V45/CK6 and EE4 work not yet in the GitHub branch".
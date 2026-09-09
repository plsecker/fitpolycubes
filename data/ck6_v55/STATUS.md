# V=55 CK6 Oddity Search — Archival Status

Status: **ABANDONED — search dead, zero results produced. V=55 remains an OPEN case.**
Recorded: 2026-09-10 (C3 final evidence freeze).

## What was attempted

Production launch of the V=55 (11 T pentacubes) CK6 oddity search,
`python3 solvers/t_ck6_v55_search.py run --volume 55 --shards 4 --parallel 1
--workdir data/ck6_v55` (detached via setsid).

- Launched: **2026-09-07 05:52 NZST** (`status.txt` mtime; `run.log` written
  08:04:52 NZST).
- Architecture: fixed min-id shard boundaries (contiguous orbit-id intervals,
  4 shards) over **all 7,139 orbit ids (0..7138)** — a complete partition with
  no gaps (see `shard_plan.json`). Parallelism reduced to 1 worker after a
  2-worker attempt OOM-crashed overnight (each heavy min-id DFS visited set
  reaches 8–12 GB; see `docs/frontier/ck6_oddity_design.md` §10.8e).
- The plan does **not** use the defective sharding prefilter and is **not
  affected** by the sharding bug (`docs/frontier/ck6_sharding_bug.md` §4); the
  symmetry audit confirms the plan remains mathematically valid
  (`docs/frontier/ck6_symmetry_definition_audit.md` §9).

## Why it stopped / current state

- The runner (pid 1557595, launched per `run.log`) died without producing any
  results: **no `shard_*.json`, no checkpoints, no `report.json` were ever
  written**; `shard_000.log` is 0 bytes.
- `status.txt` (2026-09-07, "V=55 production running") is a **stale marker**:
  no search process is alive (verified via `ps` on 2026-09-09 and 2026-09-10).
- Nothing was relaunched; the search is **incomplete** — it produced zero
  evidence in either direction.

## Consequence

**V=55 (11 T pentacubes) remains unresolved.** No negative result is claimed:
the search never ran to completion. The next unassessed case after the proven
V=45 negative is still V=55.

## Reusable files

| file | size | status |
|---|---|---|
| `shard_plan.json` | 70 KB | complete, valid partition of all 7,139 orbit ids — reusable as-is for a future run |
| `monitor.sh` | 1 KB | monitoring script, reusable |
| `run.log` | 131 B | launch record (pid 1557595) |
| `status.txt` | 65 B | stale marker, superseded by this file |

## Recommended next steps (when the search is resumed)

1. Land `tools/verify_ck6_oddity.py` (independent witness auditor) first —
   required by `docs/frontier/ck6_symmetry_definition_audit.md` §10.
2. Reuse `shard_plan.json` (or rebuild with the corrected sharding module
   `solvers/ck6_sharding_corrected.py`).
3. Consider the corrected V45 re-count/re-run
   (`docs/frontier/ck6_v45_sharding_repair.md` §6) before or alongside V=55.
# OpenWork Status & Polling Protocol

The authoritative task-hand-off protocol is
`docs/agent_control_protocol.md` (ADOPTED 2026-09-22): GitHub issues are
the single task queue; `docs/frontier/OPENWORK_INBOX.md` is the mirror
ledger. This document keeps the operational details (status fields,
orphan detection, current job) that the protocol references. It is
protocol/documentation only: it does not change solver code and never
launches V45 or any solver.

## Polling protocol

1. **Sync first**: before reading the queue, OpenWork must fetch and
   fast-forward `origin/frontier-solutions`
   (`git fetch origin frontier-solutions && git merge --ff-only origin/frontier-solutions`).
2. **Execute the first READY task**: the queue is GitHub issues, read via
   the inbox mirror (`docs/frontier/OPENWORK_INBOX.md`). OpenWork executes
   the lowest-numbered task with Status `READY`, changing it to `RUNNING`
   (issue comment + inbox entry) before substantive work and to `DONE`
   (completion comment with commit SHA + inbox entry) after successful
   completion. See `docs/agent_control_protocol.md` §3–§4.
3. **Safe handling of local uncommitted work**: never discard, reset, or
   force-update local work. A fast-forward-only update is the only
   permitted sync; if it fails, stop and report rather than force.
4. **Orphan check before expensive work**: before starting any expensive
   task, run `python tools/frontier/orphan_check.py`. If it reports
   likely orphans, stop and ask the human before proceeding; never
   blanket-kill processes.

## Status fields

Each task's status record uses the following minimal fields (needed for
later polling):

| Field | Meaning |
|-------|---------|
| task ID | Unique task identifier (e.g. `TASK-003`) |
| state | `READY` / `RUNNING` / `DONE` |
| start time | When execution of the task began |
| last heartbeat | Most recent liveness signal during execution |
| current operation | What the executor is doing right now |
| last checkpoint | Most recent durable progress point |
| last result | Outcome of the last completed step / the task |
| last error | Most recent error, if any |

## Orphan-process detection & recovery

Research jobs (V45 shard workers, validation runs, ...) are launched as
subprocesses that share the launcher's process group/session
(`subprocess.Popen` without `start_new_session`). When the OpenWork
session crashes, its children are reparented to init (pid 1) and keep
running, silently consuming CPU (incident 2026-09-21: four
`validate_bfs_packed.py --module tools.bfs_layered_external 35`
processes).

Mechanism (report-only, never auto-kills):

- Launchers record each job in `data/ck6_reuse/openwork_jobs.jsonl`
  (one JSON line per job: pid, ppid, cmd, start time, expected_s,
  done_file, workdir). `run_v45_production.py` registers its workers
  and itself (orchestrator mode). Ad-hoc jobs should be registered the
  same way before launch.
- `python tools/frontier/orphan_check.py` (default `--check`) reports
  jobs whose recorded launcher (ppid) is gone — likely orphans — plus
  jobs abandoned with an orphaned launcher. Exit code 2 when likely
  orphans are found, 0 otherwise. `--prune` drops entries for dead or
  finished jobs.
- Distinguishing intentional vs abandoned: a job whose `done_file`
  exists is finished; a job still within `expected_s` is likely
  intentional; a job far past `expected_s` with no progress marker is
  suspicious. Verify with the human before acting.

Recovery procedure after an OpenWork crash:

1. Run `python tools/frontier/orphan_check.py` and review the report.
2. For each likely orphan, confirm with the human that it is abandoned
   (check cmd, start time, elapsed, done_file).
3. Stop only confirmed abandoned jobs (e.g. `kill <pid>`); never use a
   blanket `pkill python`.
4. If an orphaned orchestrator is found, its registered workers are
   abandoned with it — confirm and stop them together.
5. Resume work: sync `frontier-solutions` (fast-forward only), then
   re-run the inbox task or production command; checkpoints make this
   safe.

## Current V45 job (issue #4 — bucket 1022 production validation)

**Status: STOPPED / RESUMABLE** — verified 2026-09-23 07:40 NZST from
`shard_002.log`, `shard_002.ckpt`, `ps`, and `systemctl --user status`.

- **Service**: `v45-bucket1022.service` — **GONE** (transient unit removed
  on process exit; `systemctl --user status` reports "could not be found")
- **PID**: 42188 — **exited** (no longer exists; verified via `ps`)
- **Command**: `python tools/frontier/run_v45_production.py --piece A
  --shard 2 --max-seconds 72000`
- **run_id**: `a2edf575429c4ccdb653d4acbe878cbe`
- **Log**: `data/ck6_reuse/run/v45_A/shard_002.log` (final write
  2026-09-23 03:18:28 NZST)
- **Bucket DBs**: `bucket_1022.sqlite` **312.3 GB — COMPLETE**;
  `bucket_1257.sqlite` **120.5 GB — in progress, checkpointed**
- **Started**: 2026-09-22 07:14:50 NZST
- **Safety cap**: 72000 s (20 h) hit → exited 2026-09-23 ~03:15 NZST
- **Result**:
  - Bucket 1022 **COMPLETE**: 589,769,226 states, **1 target** (rejected by
    funnel rule `reject: <k contained placements`), 56200 s, db 312310 MB,
    peak RSS 2043 MiB (settled ~1044–1060 MiB), 0 SAT witnesses, 0 covers.
  - Job continued to bucket 1257; cap hit mid-bucket at 248,000,000 states
    (16007 s in-bucket); checkpoint preserved; **bucket 1257 not recorded as
    done** (`shard 2: limit hit mid-bucket 1257 (max_seconds 72000)`).
- **Checkpoint**: `shard_002.ckpt` — 333/462 min-ids done (924–1256);
  min-id 1022 done (1 target); bucket 1257 in progress (not done).
- **Disk**: 443 GB free (below the 450 GB threshold; job already stopped at
  the cap, so no action was needed — note for the next launch).
- **Monitor**: no service to monitor — job is stopped. Next step is the
  resume/verification decision (issue #4 completion flow).

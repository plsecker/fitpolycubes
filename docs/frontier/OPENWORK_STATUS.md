# OpenWork Status & Polling Protocol

Minimal protocol for repository → OpenWork task hand-off via
`docs/frontier/OPENWORK_INBOX.md`. This is protocol/documentation only:
it does not change solver code and never launches V45 or any solver.

## Polling protocol

1. **Sync first**: before reading the inbox, OpenWork must fetch and
   fast-forward `origin/frontier-solutions`
   (`git fetch origin frontier-solutions && git merge --ff-only origin/frontier-solutions`).
2. **Execute the first READY task**: OpenWork executes the first task
   with Status `READY`, changing it to `RUNNING` before substantive work
   and to `DONE` after successful completion.
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

- **Service**: `v45-bucket1022.service` (user-level systemd transient,
  `systemd-run --user`; survives an OpenWork crash)
- **PID**: 42188 (Main PID; ppid = systemd user manager 2430)
- **Command**: `python tools/frontier/run_v45_production.py --piece A
  --shard 2 --max-seconds 72000`
- **run_id**: `a2edf575429c4ccdb653d4acbe878cbe` (fresh; pre-SQLite
  checkpoint had none)
- **Log**: `data/ck6_reuse/run/v45_A/shard_002.log` (append)
- **Bucket DB**: `data/ck6_reuse/run/v45_A/bucket_1022.sqlite`
- **Started**: 2026-09-22 07:14:50 NZST
- **Safety cap**: 20 h (72000 s) → checkpointed stop ~2026-09-23
  03:15 NZST if not complete (STOPPED / RESUMABLE, not failure)
- **Expected**: ~14 h 45 m wall, ~312 GB DB, <1.1 GiB RSS (benchmark)
- **Status**: RUNNING (initial; 98/462 min-ids done, bucket 1022 in
  progress)
- **Monitor**: `systemctl --user status v45-bucket1022` /
  `journalctl --user -u v45-bucket1022`; free disk must stay ≥ 450 GB
  (currently 846 GB free); on completion update this section with the
  final result.
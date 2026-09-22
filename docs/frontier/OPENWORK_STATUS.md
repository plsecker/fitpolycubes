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

**Status: RUNNING (resumed)** — verified 2026-09-23 11:56 NZST from
`shard_002.log`, `shard_002.ckpt`, and `systemctl --user status`.

- **Service**: `v45-shard2.service` — **ACTIVE** (transient systemd unit,
  launched 2026-09-23 11:55:55 NZST)
- **PID**: 411978 — running
- **Command**: `python tools/frontier/run_v45_production.py --piece A
  --shard 2 --max-seconds 72000` (no `--prune-dbs`)
- **run_id**: `a2edf575429c4ccdb653d4acbe878cbe` (unchanged across resumes)
- **Log**: `data/ck6_reuse/run/v45_A/shard_002.log` (append mode)
- **Bucket DBs**: `bucket_1022.sqlite` **312.3 GB — COMPLETE**;
  `bucket_1257.sqlite` **174.75 GB — in progress, checkpointed at
  358,000,000 states, 1 target** (funnel-rejected, like 1022's)
- **History**:
  - 2026-09-22 07:14 → 2026-09-23 03:15: original run (`v45-bucket1022.service`,
    PID 42188): bucket 1022 COMPLETE (589,769,226 states, 1 target, 56200 s,
    312310 MB), then 20 h cap hit mid-bucket 1257 at 248,000,000 states.
  - 2026-09-23 09:33 → 11:52: resumed (PID 390173) per issue #7 decision;
    reached 358,000,000 states (1 target); **STOPPED cleanly at 11:52** when a
    new directive ("do not resume immediately; assess first") arrived —
    checkpoint preserved, nothing deleted.
  - 2026-09-23 11:55: assessment complete (remaining search IS necessary for
    the V45 total and per-piece SAT/UNSAT verdicts; see
    `docs/frontier/ISSUE_007_RESUME_DECISION.md`); **resumed from the 358M
    checkpoint** (exact resume, zero rework).
- **Checkpoint**: `shard_002.ckpt` — 333/462 min-ids done (924–1256);
  min-id 1022 done (1 target); bucket 1257 in progress (not done);
  `targets: 2` (1022 + 1257), both funnel-rejected.
- **Disk**: 391 GB free at resume; bucket 1257 needs ~113 GB more (~4.6 h at
  ~14–23k/s) → ~278 GB free after; above the 100 GB floor.
- **Monitor**: tail `shard_002.log`; place `data/ck6_reuse/run/v45_A/STOP`
  if free space < 100 GB (not expected); 20 h cap will stop cleanly if the
  rate collapses. Remaining shard workload after 1257: 10 more run buckets
  (1279, 1301–1305, 1326–1328, 1349) + 118 provably-empty; continuing past
  1257 requires pruning completed DBs after audit.

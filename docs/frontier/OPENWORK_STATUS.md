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
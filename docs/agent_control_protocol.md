# Agent Control Protocol

**Status:** ADOPTED — 2026-09-22
**Source:** `docs/agent_architecture_audit.md` (§5 proposal)
**Scope:** task hand-off between ChatGPT, OpenWork, and GitHub for this
repository (`plsecker/fitpolycubes`, branch `frontier-solutions`).

This protocol is documentation/control only. It never authorizes changes to
solver algorithms, production jobs, run databases, checkpoints, or logs
(§10).

---

## 1. Roles

| Role | Who | Responsibilities |
|---|---|---|
| Task author | ChatGPT (or the human) | Creates GitHub issues; verifies completed work; closes issues |
| Executor | OpenWork | Polls the queue; executes tasks; commits; pushes; comments on issues; refreshes state docs |
| Verifier | ChatGPT (or the human) | Verifies commit SHAs and deliverables; closes issues or files follow-ups |
| Owner | Human (Philip) | Final authority; approves catalogue changes; closes issues when verification is delegated |

## 2. Single queue: GitHub issues

- The task queue is GitHub issues on `plsecker/fitpolycubes`.
- **OpenWork never creates issues.** ChatGPT (or the human) creates them.
- `docs/frontier/OPENWORK_INBOX.md` is a **mirror ledger, not a second
  queue**: one entry per issue, carrying `Issue: #N` and a Status that
  mirrors the issue's lifecycle. No task exists in the inbox without an
  issue number, except bootstrap tasks (§2.1).
- The queue is read in issue-number order; the lowest-numbered READY issue
  is executed first.

### 2.1 Bootstrap rule

Tasks that arrive before issue-mirroring is in place (e.g. this adoption
task) are recorded in the inbox with `Issue: none (bootstrap)` and are
executed exactly like issue tasks. The first issue-driven task after
adoption must be mirrored with its real issue number.

## 3. Lifecycle: READY → RUNNING → DONE

| State | Meaning | Set by |
|---|---|---|
| `READY` | Issue is open and its deliverable is not yet committed (no completion comment) | Task author (implicit on creation) |
| `RUNNING` | Execution has begun | OpenWork, before substantive work |
| `DONE` | Deliverable committed and pushed; completion reported | OpenWork, after push |

Transitions:

1. **READY → RUNNING**: OpenWork comments on the issue ("starting") and
   updates the inbox entry to `RUNNING` **before** substantive work.
2. **RUNNING → DONE**: OpenWork commits and pushes the deliverable, then
   comments on the issue with the completion report (§4) and updates the
   inbox entry to `DONE`.
3. **Blocked / STOPPED / RESUMABLE**: the task stays `RUNNING` with a
   comment explaining the blocker (e.g. "STOPPED / RESUMABLE — 20 h cap
   hit, checkpoint preserved"). It is **never** marked `DONE` while
   incomplete.

Only one task is `RUNNING` at a time.

## 4. Issue comments and commit SHAs

Every completion comment follows this shape:

```
Done. Commit: <sha> on frontier-solutions.

Result: <one paragraph: what was delivered, key numbers/verdicts>
State: <DONE | STOPPED/RESUMABLE | BLOCKED>
Files: <paths of the deliverable>
```

Rules:

- **Push first, comment second.** The SHA must exist on
  `origin/frontier-solutions` before the comment is written.
- One issue = one deliverable = one coherent commit (plus any ledger-only
  follow-up commit, e.g. recording the SHA in the inbox).
- The inbox entry's `Result` records the same SHA.

## 5. Refreshing RESEARCH_STATE.md

- RESEARCH_STATE.md is refreshed **in the same commit as the deliverable**,
  but only the sections the task touched, each with the current date.
- The header date is updated to the refresh date.
- Claims that are no longer verifiable are **marked stale (§8), not
  deleted** — provenance is preserved.
- A task that does not touch research state does not rewrite the research
  sections; it may still add stale markers (§8).

## 6. Refreshing OPENWORK_STATUS.md

- The "Current V45 job" (or any job) section is updated **only when the
  job's state actually changes**: started, stopped, completed, or
  re-launched.
- The update records: service/pid, command, run_id, log path, bucket DB,
  started time, safety cap, and the observed state with a timestamp.
- **Never update the job section from memory** — verify via
  `systemctl --user status`, `ps`, and the log before writing.
- Protocol sections (polling, status fields, orphan check) are updated only
  when the protocol itself changes.

## 7. Closing completed issues

- OpenWork closes an issue **only when the issue body explicitly says
  "close on completion"**.
- Otherwise the verifier (ChatGPT or human) closes after verification (§9).
- An issue with a completed deliverable and no completion comment must
  never be left silently open: either comment or close.

## 8. Marking stale state

- Any document that contradicts RESEARCH_STATE.md must carry a banner at
  the top:

  > **STALE / SUPERSEDED** — <date>. See <pointer to the authoritative doc>.

- RESEARCH_STATE.md §11 ("Consistency cautions") is the **index of stale
  docs**; every banner must be listed there.
- RESEARCH_STATE.md's own claims carry a header date; when a claim is known
  to be outdated it is marked inline with
  `[STALE <date>: <pointer>]` rather than silently rewritten.
- **A stale marker records the verified state at the time the marker was
  created — never "current" state.** Phrase the replacement state as a
  dated snapshot: `As of <date>, verified: <state>`. Do not write
  "current state is X": the act of committing the marker advances Git
  HEAD, so "current" is stale the moment the marker lands. The marker's
  date is the verification date; the recorded state is what was verified
  on that date, not a promise about later state.

## 9. ChatGPT verification of completed work

After each completion comment, ChatGPT:

1. Verifies the SHA exists on `origin/frontier-solutions`
   (`git fetch origin frontier-solutions && git rev-parse origin/frontier-solutions`).
2. Reads the deliverable file(s) named in the comment.
3. Checks the deliverable against the issue's acceptance criteria.
4. On success: closes the issue (unless "close on completion" was already
   handled) and confirms RESEARCH_STATE.md / OPENWORK_STATUS.md were
   refreshed if the task touched research or job state.
5. On failure: leaves the issue open and files a follow-up issue
   referencing the parent.

## 10. Standing constraints (never waived by this protocol)

1. **Sync first**: `git fetch origin frontier-solutions && git merge --ff-only origin/frontier-solutions` before reading the queue.
2. **Orphan check before expensive work**: `python tools/frontier/orphan_check.py`; report and ask, never blanket-kill.
3. Never modify solver algorithms or production jobs.
4. Never restart or stop a running production job without an explicit instruction.
5. Never alter run databases, checkpoints, or logs.
6. Never discard, reset, or force-update local work; fast-forward only.
7. Never commit secrets or private memory.
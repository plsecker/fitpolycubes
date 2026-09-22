# OpenWork Inbox

Mirror/bootstrapping ledger for the agent-control protocol
(`docs/agent_control_protocol.md`, ADOPTED 2026-09-22). The single task
queue is GitHub issues; entries below mirror issues (`Issue: #N`) or
bootstrap tasks without an issue number (`Issue: none (bootstrap)`).

## TEST-001

- ID: `TEST-001`
- Status: `DONE`
- Task: `Create a file named docs/frontier/OPENWORK_TEST.md containing the single line "OpenWork direct task test: PASS".`
- Result: `docs/frontier/OPENWORK_TEST.md` created containing the single line `OpenWork direct task test: PASS`.

## TEST-002

- ID: `TEST-002`
- Status: `DONE`
- Task: Create a file named docs/frontier/OPENWORK_TEST2.md containing the single line "OpenWork inbox test: PASS".
- Constraints: Do not run any solver. Do not modify or stage any other files. Commit only the inbox update and the new test file.
- Result: `docs/frontier/OPENWORK_TEST2.md` created containing the single line `OpenWork inbox test: PASS`.


## TASK-003

- ID: `TASK-003`
- Status: `DONE`
- Task: Establish the minimal OpenWork polling protocol for future repository tasks.
- Requirements:
  1. Document that OpenWork must first fetch/fast-forward `origin/frontier-solutions` before reading the inbox.
  2. Document that it then executes the first `READY` task, changing it to `RUNNING` before substantive work and `DONE` after successful completion.
  3. Document safe handling of local uncommitted work: never discard, reset, or force-update local work.
  4. Create `docs/frontier/OPENWORK_STATUS.md` describing the minimal status fields needed for later polling: task ID, state, start time, last heartbeat, current operation, last checkpoint, last result, and last error.
  5. Do not launch V45 or any solver.
  6. Do not change solver code.
  7. Keep the implementation minimal; this task is protocol/documentation only.
- Result: `docs/frontier/OPENWORK_STATUS.md` created with the polling protocol (sync-first, READY→RUNNING→DONE lifecycle, safe handling of local work) and the 8 minimal status fields. No solver code changed; no solver launched.

## TASK-004

- ID: `TASK-004`
- Issue: `none (bootstrap)`
- Status: `DONE`
- Task: Implement the minimal agent-control protocol from `docs/agent_architecture_audit.md` §5: GitHub issues as the single task queue with `docs/frontier/OPENWORK_INBOX.md` as mirror/bootstrapping ledger; explicit rules for READY→RUNNING→DONE, issue comments and commit SHAs, refreshing RESEARCH_STATE.md and OPENWORK_STATUS.md, closing completed issues, marking stale state, and ChatGPT verification of completed work. Create `docs/agent_control_protocol.md`. Do not modify solver code, production jobs, or run databases/checkpoints/logs; do not restart or stop bucket 1022.
- Result: `docs/agent_control_protocol.md` created (ADOPTED 2026-09-22); `docs/frontier/OPENWORK_STATUS.md` updated to reference the protocol and the issue queue; `docs/frontier/RESEARCH_STATE.md` updated with a stale marker for the outdated "no processes running" claim (indexed in §11). Commit: `4eee615` on `frontier-solutions`. No solver code, production jobs, databases, checkpoints, or logs touched; bucket 1022 untouched.

## ISSUE-006

- ID: `ISSUE-006`
- Issue: `#6`
- Status: `DONE`
- Task: Reconcile V45 bucket 1022 target identity: determine exactly what target was enumerated in bucket 1022, whether its identity can be established from the recorded artifacts, and whether the B-9 claim in the production documentation is an incorrect label. Correct affected documentation; preserve historical evidence; state what is proven/inferred/unknown; update RESEARCH_STATE.md and OPENWORK_STATUS.md only where necessary; add a correction comment to Issue #4; commit and push on frontier-solutions. Do not modify solver algorithms, production/research jobs, or databases/checkpoints/logs.
- Result: Reconciled — the bucket-1022 target is **NOT** the B-9 target. B-9 (`oh-109166b4c83a`) has intrinsic min-id 3590, owned by bucket 3590 (shard 7), SAT with 12 repo-M covers; the corrected sharding assigns min-id 1022 to bucket 2, so the sets are disjoint. Bucket 1022 enumerated exactly 1 target, rejected by funnel rule `reject: <k contained placements` (fewer than k=9 contained placements → not tileable by piece A); its identity is not recorded in any artifact (checkpoint `witnesses: []`, no log digest, no DB targets table). The "(the B-9 target)" label was an incorrect label; corrected in RESEARCH_STATE.md §2.2/§2.3 with proven/inferred/unknown stated. Commit: `2d0654b` on `frontier-solutions`. No solver code, jobs, databases, checkpoints, or logs touched. Issue #4 correction comment prepared (no GitHub API token available to post).

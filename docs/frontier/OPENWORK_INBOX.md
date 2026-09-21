# OpenWork Inbox

Repository → OpenWork task hand-off (issue-driven smoke test).

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
- Status: `READY`
- Task: Establish the minimal OpenWork polling protocol for future repository tasks.
- Requirements:
  1. Document that OpenWork must first fetch/fast-forward `origin/frontier-solutions` before reading the inbox.
  2. Document that it then executes the first `READY` task, changing it to `RUNNING` before substantive work and `DONE` after successful completion.
  3. Document safe handling of local uncommitted work: never discard, reset, or force-update local work.
  4. Create `docs/frontier/OPENWORK_STATUS.md` describing the minimal status fields needed for later polling: task ID, state, start time, last heartbeat, current operation, last checkpoint, last result, and last error.
  5. Do not launch V45 or any solver.
  6. Do not change solver code.
  7. Keep the implementation minimal; this task is protocol/documentation only.
- Result: Pending.

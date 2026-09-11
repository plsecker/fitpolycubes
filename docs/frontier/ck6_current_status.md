# CK6 Current Status

**Last updated:** 2026-09-11
**Branch:** `frontier-solutions`
**HEAD:** `b7ee0f8` (Add Shirakawa box parser)

---

## PROVEN

1. **Sharding bug identified and documented.**
   The historical V45 min-id prefilter excluded candidate minimum-orbit
   ids that are not reachable FROM a start-front orbit through
   id-nondecreasing chains. That criterion is unsound.
   See `docs/frontier/ck6_sharding_bug.md`.

2. **Corrected V45 shard plan exists: 3,696 candidate min-ids.**
   The corrected candidate domain for V45 is 3,696 min-ids (vs the
   historical plan which omitted a substantial subset).
   Plan file: `data/ck6_reuse/ck6_v45_shards_corrected.json`.
   Code: `solvers/ck6_sharding_corrected.py` (functions
   `corrected_candidate_min_ids`, `build_corrected_plan`).

3. **George's B-9 target: min-id 3590, repo-M has 12 covers.**
   George Sicherman's "B 9" target (centre-adjacent orbits 3652/3937)
   has minimum orbit id 3590 and yields exactly 12 repo-M covers via
   `funnel_and_cover`. The full min-id-3590 subtree walk enumerated
   3,430,348 CK6 targets; George's target was found at leaf #3,430,348.
   Evidence: `data/ck6_reuse/ck6_v45_sharding_repair.json` (field
   `smoke_test`); `docs/frontier/ck6_v45_sharding_repair.md`.

4. **Historical V45 corpus is incomplete.**
   The historical corpus generated under the old sharding plan is
   missing targets whose min-ids fall below the (incorrect) threshold.
   The corrected domain starts well below the historical cutoff.

5. **Low-min-id enumeration is extremely expensive.**
   The search is a generate-and-test DFS over orbit subsets.
   Low min-ids (e.g. 3500) admit exponentially many orbit subsets,
   nearly all of which produce disconnected cell sets.
   Connectivity is only tested at leaves (rem == 0), wasting ~58%
   of runtime on doomed branches.

6. **min-id 3500 benchmark: severe state growth / memory pressure.**
   138,508 states explored in 10s; 67.2% of iterations reached leaves
   (all disconnected); RSS ~793 MB. No targets found.
   See `docs/frontier/v45_architecture_audit_final.md`.

7. **`orbit_cells` precomputation is a safe modest optimization.**
   Precomputing orbit cell sets avoids repeated list-to-set conversion
   at each DFS state. Gives 1.16x-1.22x speedup on tractable min-ids
   with no correctness risk. This is the only safe optimization
   identified.

8. **Attempted stronger connectivity pruning produced false negatives.**
   Two stronger pruning strategies were tested:
   - Maximum pairwise minimum connection cost
   - (k-1) x min_frontier_orbit_cost lower bound
   Both failed exact set-equality tests (V5, V15, V45 min-ids).
   **These must NOT be used** — they silently drop valid targets.
   See `docs/frontier/v45_optimization_final_status.md`.

---

## INCOMPLETE

1. **Full corrected V45 target corpus NOT generated.**
   The corrected 3,696-min-id domain has not been exhaustively
   enumerated. The `count_corpus` infrastructure exists in
   `ck6_sharding_corrected.py` but has not been run to completion
   on V45. No full corpus file exists in the repository.

2. **Full V45 M/B validation NOT completed.**
   No repository-M or repository-B validation has been run against
   a complete corrected V45 corpus. The only validation evidence
   is the George B-9 smoke test (min-id 3590 only, repo-M only,
   12 covers confirmed).

3. **Remaining 461 min-ids of George's shard not walked.**
   Min-id 3590's subtree was fully enumerated (3.43M targets), but
   the other 461 min-ids in shard 7 were deliberately not run.

---

## NEXT RESEARCH QUESTION

1. **How many total CK6 V45 targets exist in the corrected domain?**
   The corrected 3,696-min-id plan is sound but unexecuted at scale.
   The full target count is unknown.

2. **How many corrected V45 targets are tileable by M or B?**
   Repository-M and repository-B validation against the full
   corrected corpus has not been established.

3. **Can the V45 enumeration be completed without solving
   intractable low-min-ids?**
   If the bulk of targets live in tractable high-min-ids, the
   enumeration may be feasible shard-by-shard. The hard low-min-ids
   (e.g. 3500) may be sparse enough to accept exponential time on
   a per-case basis, or may require a fundamentally different
   algorithm.

4. **Is there a safe tractable necessary condition stronger than
   simple connectivity?**
   All attempts so far produced false negatives. The only safe
   optimization remains `orbit_cells` precomputation (1.2x).

---

## CAUTION: Agent Integrity Note

During today's session, agent-generated claims stated that a
1,469,999-target corrected corpus had been completed and validated.
These claims were **not supported by the actual repository state**.
No such corpus file exists. The `count_corpus` command was not run
to completion on V45. Any future agent output referencing a completed
corrected V45 corpus should be verified against actual file artifacts
before being accepted as established fact.

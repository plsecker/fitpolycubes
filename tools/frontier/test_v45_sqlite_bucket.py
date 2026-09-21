#!/usr/bin/env python3
"""
Tests for the SQLite-backed seeded connected enumerator
(iter_targets_seeded_connected_sqlite) and its integration contract
with the production driver (tools/frontier/run_v45_production.py).

Run:  PYTHONPATH=. python3 tools/frontier/test_v45_sqlite_bucket.py

Covers:
  1. SQLite == in-memory on small volumes (V5 all min-ids, V15 all
     min-ids, V25 sampled min-ids): identical target sets, identical
     state counts, database kept after completion.
  2. Two-stage resume does no redo: a bucket stopped via max_states
     resumes and completes; stage1.states + stage2.states == the
     in-memory total (no overlap, no gap).
  3. Killed/interrupted bucket resume: a hard exception inside the
     consumer loop (simulating SIGKILL between checkpoints) leaves a
     resumable database; the bucket resumes and completes with the
     correct target set.
  4. Completed-bucket re-entry: re-running a completed bucket yields
     nothing, reports info.completed, and restores the caller state.
  5. run_id mismatch: a database from a different run is discarded and
     the bucket restarts fresh (no stale-state contamination).
  6. STOP semantics: stop_check at a checkpoint boundary raises
     BucketStopped and the bucket is resumable.
"""

import gc
import os
import shutil
import sys
import tempfile
import time
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "solvers"))

from t_ck6_oddity_v35_search import (  # noqa: E402
    BucketRunInfo,
    BucketStopped,
    SearchLimit,
    _conn_prune_data,
    build_universe,
    count_minids,
    iter_targets_seeded_connected,
    iter_targets_seeded_connected_sqlite,
)
from ck6_sharding_corrected import corrected_candidate_min_ids  # noqa: E402

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"  [PASS] {name}")
    else:
        FAILURES.append(name)
        print(f"  [FAIL] {name} {detail}")


def bucket_provably_empty(un, s, budget):
    """Root-level prune of the seeded connected engine: such buckets are
    skipped entirely (no database is created, info stays untouched)."""
    dist, cells_ge = _conn_prune_data(un)
    return (dist[s] > budget or cells_ge[s] < 2 * budget
            or budget - un["cost"][s] < 0)


def collect_memory(un, s, budget):
    """In-memory reference: target set + state count for one bucket."""
    stats = {}
    mem = set()
    for t in iter_targets_seeded_connected(un, s, budget, stats=stats):
        mem.add(frozenset(t))
    return mem, stats.get("states", 0)


def check_equivalence(volume, min_ids, tmpdir):
    un = build_universe(volume)
    budget = (volume - 1) // 2
    for s in min_ids:
        mem, mem_states = collect_memory(un, s, budget)
        db = os.path.join(tmpdir, f"v{volume}_s{s}.sqlite")
        sq = set()
        stats = {}
        info = BucketRunInfo()
        for t in iter_targets_seeded_connected_sqlite(
                un, s, budget, db, run_id="test", info=info, stats=stats):
            sq.add(frozenset(t))
        check(f"V{volume} min-id {s}: sqlite target set == memory",
              sq == mem, f"|sqlite|={len(sq)} |mem|={len(mem)}")
        check(f"V{volume} min-id {s}: sqlite states == memory",
              stats.get("states", 0) == mem_states,
              f"{stats.get('states', 0)} vs {mem_states}")
        if bucket_provably_empty(un, s, budget):
            check(f"V{volume} min-id {s}: provably empty -> no DB, "
                  f"no info", not info.completed and not os.path.exists(db))
        else:
            check(f"V{volume} min-id {s}: info.completed and targets match",
                  info.completed and info.targets == len(mem),
                  f"completed={info.completed} targets={info.targets}")
            check(f"V{volume} min-id {s}: database kept after completion",
                  os.path.exists(db), db)
        print(f"    V{volume} min-id {s}: {len(mem)} targets, "
              f"{mem_states} states")


def test_two_stage_resume(volume, s, tmpdir):
    un = build_universe(volume)
    budget = (volume - 1) // 2
    mem, mem_states = collect_memory(un, s, budget)
    db = os.path.join(tmpdir, f"resume_s{s}.sqlite")
    ckpt_every = 100
    # stage 1: stop after ~2.5 checkpoints via max_states
    limits = {"max_states": 250, "t0": time.time()}
    stats1 = {}
    info1 = BucketRunInfo()
    got1 = set()
    try:
        for t in iter_targets_seeded_connected_sqlite(
                un, s, budget, db, ckpt_every=ckpt_every, run_id="R",
                info=info1, stats=stats1, limits=limits):
            got1.add(frozenset(t))
        raise AssertionError("expected SearchLimit")
    except SearchLimit:
        pass
    check("two-stage: stage 1 stopped at a checkpoint boundary",
          stats1["states"] % ckpt_every == 0, str(stats1["states"]))
    check("two-stage: stage 1 did not mark the bucket complete",
          not info1.completed)
    # stage 2: resume to completion
    stats2 = {}
    info2 = BucketRunInfo()
    got2 = set()
    for t in iter_targets_seeded_connected_sqlite(
            un, s, budget, db, ckpt_every=ckpt_every, run_id="R",
            info=info2, stats=stats2):
        got2.add(frozenset(t))
    check("two-stage: stage 2 resumed from checkpoint", info2.resumed)
    check("two-stage: no lost targets (stage1 | stage2 == memory)",
          got1 | got2 == mem,
          f"|got1|={len(got1)} |got2|={len(got2)} |mem|={len(mem)}")
    check("two-stage: no duplicated targets (stage1 disjoint stage2)",
          got1.isdisjoint(got2))
    check("two-stage: no redo (stage1 + stage2 == total states)",
          stats1["states"] + stats2["states"] == mem_states,
          f"{stats1['states']} + {stats2['states']} vs {mem_states}")
    print(f"    two-stage resume V{volume} min-id {s}: "
          f"stage1 {stats1['states']} + stage2 {stats2['states']} "
          f"== {mem_states} states, no redo")


def test_killed_bucket_resume(volume, s, tmpdir):
    un = build_universe(volume)
    budget = (volume - 1) // 2
    mem, mem_states = collect_memory(un, s, budget)
    db = os.path.join(tmpdir, f"killed_s{s}.sqlite")
    ckpt_every = 100
    # simulate a hard kill: raise inside the consumer after ~150 targets
    stats1 = {}
    gen = iter_targets_seeded_connected_sqlite(
        un, s, budget, db, ckpt_every=ckpt_every, run_id="R",
        stats=stats1)
    got1 = set()
    n = 0
    try:
        for t in gen:
            got1.add(frozenset(t))
            n += 1
            if n == 150:
                raise KeyboardInterrupt("simulated kill")
    except KeyboardInterrupt:
        pass
    gen.close()
    del gen
    gc.collect()
    # resume to completion
    info = BucketRunInfo()
    stats2 = {}
    got2 = set()
    for t in iter_targets_seeded_connected_sqlite(
            un, s, budget, db, ckpt_every=ckpt_every, run_id="R",
            info=info, stats=stats2):
        got2.add(frozenset(t))
    check("killed: resumed from checkpoint", info.resumed)
    check("killed: no lost targets (stage1 | stage2 == memory)",
          got1 | got2 == mem,
          f"|got1|={len(got1)} |got2|={len(got2)} |mem|={len(mem)}")
    check("killed: redo bounded by one checkpoint interval",
          stats1["states"] + stats2["states"] <= mem_states + ckpt_every,
          f"{stats1['states']} + {stats2['states']} vs {mem_states}")
    print(f"    killed-bucket resume V{volume} min-id {s}: "
          f"{len(mem)} targets recovered, {mem_states} states")


def test_completed_reentry(volume, s, tmpdir):
    un = build_universe(volume)
    budget = (volume - 1) // 2
    db = os.path.join(tmpdir, f"complete_s{s}.sqlite")
    state = {"targets": 0, "funnel": Counter()}
    info = BucketRunInfo()
    for t in iter_targets_seeded_connected_sqlite(
            un, s, budget, db, run_id="R", state=state, info=info):
        state["targets"] += 1
    total = info.targets
    check("re-entry: first run completed", info.completed and total > 0,
          f"completed={info.completed} targets={total}")
    # re-enter with a fresh state dict
    state2 = {"targets": 0, "funnel": Counter()}
    info2 = BucketRunInfo()
    n = 0
    for _ in iter_targets_seeded_connected_sqlite(
            un, s, budget, db, run_id="R", state=state2, info=info2):
        n += 1
    check("re-entry: nothing re-yielded", n == 0, str(n))
    check("re-entry: info.completed and targets preserved",
          info2.completed and info2.targets == total,
          f"completed={info2.completed} targets={info2.targets}")
    check("re-entry: caller state restored from final checkpoint",
          state2["targets"] == total, f"{state2['targets']} vs {total}")
    print(f"    completed re-entry V{volume} min-id {s}: "
          f"no re-yield, state restored ({state2['targets']} targets)")


def test_run_id_mismatch(volume, s, tmpdir):
    un = build_universe(volume)
    budget = (volume - 1) // 2
    db = os.path.join(tmpdir, f"mismatch_s{s}.sqlite")
    # run A: partial
    limits = {"max_states": 150, "t0": time.time()}
    try:
        for _ in iter_targets_seeded_connected_sqlite(
                un, s, budget, db, ckpt_every=100, run_id="A",
                limits=limits):
            pass
    except SearchLimit:
        pass
    # run B: different run_id -> stale DB discarded, fresh start
    info = BucketRunInfo()
    stats = {}
    got = set()
    for t in iter_targets_seeded_connected_sqlite(
            un, s, budget, db, ckpt_every=100, run_id="B",
            info=info, stats=stats):
        got.add(frozenset(t))
    mem, mem_states = collect_memory(un, s, budget)
    check("run_id mismatch: stale DB discarded (fresh start)",
          not info.resumed)
    check("run_id mismatch: target set == memory", got == mem,
          f"|got|={len(got)} |mem|={len(mem)}")
    check("run_id mismatch: state count == memory",
          stats["states"] == mem_states, f"{stats['states']} vs {mem_states}")
    print(f"    run_id mismatch V{volume} min-id {s}: stale DB discarded, "
          f"fresh start == memory")


def test_stop_semantics(volume, s, tmpdir):
    un = build_universe(volume)
    budget = (volume - 1) // 2
    db = os.path.join(tmpdir, f"stop_s{s}.sqlite")
    info = BucketRunInfo()
    stats1 = {}
    got1 = set()
    try:
        for t in iter_targets_seeded_connected_sqlite(
                un, s, budget, db, ckpt_every=100, run_id="R",
                info=info, stats=stats1, stop_check=lambda: True):
            got1.add(frozenset(t))
        raise AssertionError("expected BucketStopped")
    except BucketStopped:
        pass
    check("STOP: BucketStopped raised, bucket not marked complete",
          not info.completed)
    # resume without the stop
    info2 = BucketRunInfo()
    stats2 = {}
    got2 = set()
    for t in iter_targets_seeded_connected_sqlite(
            un, s, budget, db, ckpt_every=100, run_id="R",
            info=info2, stats=stats2):
        got2.add(frozenset(t))
    mem, mem_states = collect_memory(un, s, budget)
    check("STOP: resumed from checkpoint", info2.resumed)
    check("STOP: no lost targets (stage1 | stage2 == memory)",
          got1 | got2 == mem,
          f"|got1|={len(got1)} |got2|={len(got2)} |mem|={len(mem)}")
    check("STOP: no duplicated targets (stage1 disjoint stage2)",
          got1.isdisjoint(got2))
    check("STOP: no redo (stage1 + stage2 == total states)",
          stats1["states"] + stats2["states"] == mem_states,
          f"{stats1['states']} + {stats2['states']} vs {mem_states}")
    print(f"    STOP semantics V{volume} min-id {s}: BucketStopped raised, "
          f"resume completes")


def test_driver_resume_accounting(tmpdir):
    """The driver records done[s] = info.targets (the bucket TOTAL) even
    when the generator resumed mid-bucket and only re-yielded the tail
    (targets processed before the checkpoint are restored into state)."""
    import json
    import run_v45_production as drv
    workdir = os.path.join(tmpdir, "work_resume")
    os.makedirs(workdir)
    plan = {"shards": [{"shard": 0, "min_ids": [1022]}]}
    stop = os.path.join(workdir, "STOP")
    orig = drv.iter_targets_seeded_connected_sqlite

    def fake(*a, **kw):
        # simulate a resumed bucket: nothing re-yielded, but the DB
        # reports 5 targets already processed (state restored in place)
        info = kw["info"]
        info.resumed = True
        info.db_path = a[3]  # db_path is the 4th positional arg
        info.run_id = kw["run_id"]
        info.completed = True
        info.targets = 5
        info.states = 12345
        kw["state"]["targets"] = 5  # simulate restore_state from the DB
        return iter(())

    drv.iter_targets_seeded_connected_sqlite = fake
    try:
        drv.run_shard("A", 0, plan, workdir, stop)
    finally:
        drv.iter_targets_seeded_connected_sqlite = orig
    # the single-min-id shard completes, so the result file carries the
    # per-min-id accounting (the ckpt is removed on completion)
    with open(os.path.join(workdir, "shard_000.json")) as f:
        res = json.load(f)
    check("driver: resumed bucket recorded with TOTAL targets",
          res["per_min_id"]["1022"] == 5, str(res["per_min_id"]))
    check("driver: state targets consistent with per-min-id",
          res["targets"] == sum(res["per_min_id"].values()),
          f"{res['targets']} vs {sum(res['per_min_id'].values())}")
    check("driver: shard marked complete",
          res["status"] == "complete", str(res["status"]))
    print(f"    driver resume accounting: per_min_id[1022] = "
          f"{res['per_min_id']['1022']} (bucket total, not tail)")


def test_driver_stop_mid_bucket(tmpdir):
    """STOP mid-bucket: the driver exits WITHOUT recording the in-flight
    bucket as done and WITHOUT a result file, so the bucket resumes from
    its SQLite checkpoint on the next invocation."""
    import json
    import run_v45_production as drv
    workdir = os.path.join(tmpdir, "work_stop")
    os.makedirs(workdir)
    plan = {"shards": [{"shard": 0, "min_ids": [1022]}]}
    stop = os.path.join(workdir, "STOP")
    orig = drv.iter_targets_seeded_connected_sqlite

    def fake(*a, **kw):
        def gen():
            raise BucketStopped()
            yield  # pragma: no cover
        return gen()

    drv.iter_targets_seeded_connected_sqlite = fake
    try:
        drv.run_shard("A", 0, plan, workdir, stop)
    finally:
        drv.iter_targets_seeded_connected_sqlite = orig
    with open(os.path.join(workdir, "shard_000.ckpt")) as f:
        ck = json.load(f)
    check("driver: STOP mid-bucket -> bucket NOT recorded as done",
          "1022" not in ck["done"], str(ck["done"]))
    check("driver: STOP mid-bucket -> no result file",
          not os.path.exists(os.path.join(workdir, "shard_000.json")))
    check("driver: STOP mid-bucket -> run_id preserved",
          isinstance(ck.get("run_id"), str) and len(ck["run_id"]) > 8)
    print(f"    driver STOP mid-bucket: bucket 1022 not recorded, "
          f"no result file, run_id preserved")


def main():
    tmpdir = tempfile.mkdtemp(prefix="v45_sqlite_test_")
    try:
        # 1. equivalence on small volumes
        for vol in (5, 15):
            un = build_universe(vol)
            cands = sorted(corrected_candidate_min_ids(un))
            print(f"V{vol}: {len(cands)} candidate min-ids")
            check_equivalence(vol, cands, tmpdir)
        # V25: 3 smallest + 2 largest buckets (largest ~10k states)
        un25 = build_universe(25)
        res25, _ = count_minids(un25, 25)
        hist = {int(k): v for k, v in res25["hist"].items()}
        cands25 = sorted(corrected_candidate_min_ids(un25))
        top = sorted(hist, key=lambda k: -hist[k])[:2]
        sample25 = cands25[:3] + [k for k in top if k not in cands25[:3]]
        print(f"V25: {len(cands25)} candidate min-ids; "
              f"sampled {sample25}")
        check_equivalence(25, sample25, tmpdir)
        # 2-6. resume semantics on the largest V25 bucket
        big = top[0]
        print(f"resume tests on V25 min-id {big} "
              f"({hist[big]:,} targets)")
        test_two_stage_resume(25, big, tmpdir)
        test_killed_bucket_resume(25, big, tmpdir)
        test_completed_reentry(25, big, tmpdir)
        test_run_id_mismatch(25, big, tmpdir)
        test_stop_semantics(25, big, tmpdir)
        # 7-8. driver integration (monkeypatched generator)
        test_driver_resume_accounting(tmpdir)
        test_driver_stop_mid_bucket(tmpdir)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    if FAILURES:
        print(f"FAILURES: {FAILURES}")
        return 1
    print("ALL SQLITE BUCKET TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
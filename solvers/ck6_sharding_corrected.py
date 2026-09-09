#!/usr/bin/env python3
"""
Corrected CK6 sharded-enumeration logic (repair for the V45 min-id
prefilter bug; see docs/frontier/ck6_sharding_bug.md and
docs/frontier/ck6_v45_sharding_repair.md).

The historical pipeline (t_ck6_oddity_v35_search.cmd_count, sharded
branch) excluded candidate minimum-orbit ids that are not reachable
FROM a start-front orbit through id-nondecreasing chains.  That
criterion is unsound; George Sicherman's "B 9" target (min orbit id
3590, centre-adjacent orbits 3652/3937) is the concrete counterexample.

This module provides:

  corrected_candidate_min_ids(un)
      Sound necessary condition: s can REACH a start-front orbit via
      adjacent orbits with ids >= s.  Over-approximates possible
      min-ids (harmless: empty shards yield 0 targets); never drops a
      realizable min-id.

  build_corrected_plan(volume, n_shards)
      Complete, disjoint shard plan over the corrected candidate domain,
      with hard assertions:
        - every candidate min-id in exactly one shard (no omission,
          no duplication);
        - George's min-id 3590 included (for V45);
        - corrected V45 domain == 3696 min-ids.

  validate_against_reference(volume)
      Corrected sharding vs the single-process reference enumerator
      (enumerate_connected_ck6_targets): exact totals AND set equality.

  smoke_george_b9(...)
      End-to-end smoke test: run the shard containing min-id 3590 of
      the V45 corpus for repo-M through the driver's own
      funnel_and_cover path, stopping when George's target is found;
      expect 12 covers.

Subcommands:
  validate [--quick]   V5/V15 (/V25) reference validation
  plan                 write the corrected V45 shard plan
  smoke                George B-9 shard smoke test (repo-M)

Nothing here modifies historical artefacts; corrected plans are written
to data/ck6_reuse/ with distinct names.
"""
import argparse
import json
import sys
import time
from collections import Counter, deque

sys.path.insert(0, "/home/philip/Work/fitpolycubes")
sys.path.insert(0, "/home/philip/Work/fitpolycubes/solvers")

from t_ck6_oddity_v35_search import build_universe, iter_targets_seeded, \
    funnel_and_cover
from common.fastfunnel import FastFunnel
from common.oddity import enumerate_connected_ck6_targets, \
    is_face_connected
from common.registry import PENTACUBES
from common.symmetry import ck6_affine_maps

REUSE = "/home/philip/Work/fitpolycubes/data/ck6_reuse"

GEORGE_B9_CORPUS_FRAME = [
    (-2, 1, -1), (-2, 1, 0), (-2, 2, -1), (-2, 2, 0), (-2, 2, 1),
    (-1, 0, -1), (-1, 0, 0), (-1, 0, 1), (-1, 0, 2), (-1, 1, -1),
    (-1, 1, 0), (-1, 1, 1), (-1, 1, 2), (-1, 1, 3), (-1, 2, -1),
    (-1, 2, 0), (0, -1, -2), (0, -1, -1), (0, -1, 0), (0, -1, 1),
    (0, 0, -2), (0, 0, -1), (0, 0, 0), (0, 0, 1), (0, 0, 2),
    (0, 1, -1), (0, 1, 0), (0, 1, 1), (0, 1, 2), (1, -2, 0),
    (1, -2, 1), (1, -1, -3), (1, -1, -2), (1, -1, -1), (1, -1, 0),
    (1, -1, 1), (1, 0, -2), (1, 0, -1), (1, 0, 0), (1, 0, 1),
    (2, -2, -1), (2, -2, 0), (2, -2, 1), (2, -1, 0), (2, -1, 1),
]
GEORGE_B9_MIN_ORBIT_ID = 3590
GEORGE_B9_OH_ID = "oh-109166b4c83a"
GEORGE_B9_M_COVERS = 12


def corrected_candidate_min_ids(un):
    """Sound candidate-min-id domain (see module docstring).

    Necessity: a target with minimum orbit id s is connected, contains
    the centre cell, and all its orbits have ids >= s; hence within the
    target there is a path from s to a centre-adjacent orbit using only
    ids >= s.
    """
    start_front = set(un["start_front"])
    adj = un["adj"]
    cands = set()
    for s in range(len(adj)):
        seen = {s}
        stack = [s]
        while stack:
            v = stack.pop()
            if v in start_front:
                cands.add(s)
                break
            for w in adj[v]:
                if w >= s and w not in seen:
                    seen.add(w)
                    stack.append(w)
    return cands


def build_corrected_plan(volume, n_shards):
    """Complete, disjoint corrected shard plan with hard assertions."""
    un = build_universe(volume)
    cands = sorted(corrected_candidate_min_ids(un))
    assert len(cands) == len(set(cands))
    if volume == 45:
        assert len(cands) == 3696, f"V45 corrected domain {len(cands)} != 3696"
        assert GEORGE_B9_MIN_ORBIT_ID in cands, "3590 omitted!"
    # partition contiguous, balanced by candidate count
    shards = []
    per = (len(cands) + n_shards - 1) // n_shards
    for i in range(0, len(cands), per):
        shards.append({"shard": len(shards), "min_ids": cands[i:i + per]})
    # assertions: no omission, no duplication
    covered = [m for sh in shards for m in sh["min_ids"]]
    assert sorted(covered) == cands, "omission or duplication in plan"
    assert len(covered) == len(set(covered)) == len(cands)
    return {"volume": volume, "planner": "corrected-sound-filter",
            "n_candidates": len(cands), "shards": shards}, un


def shard_for_min_id(plan, min_id):
    for sh in plan["shards"]:
        if min_id in sh["min_ids"]:
            return sh
    raise AssertionError(f"min-id {min_id} not in plan")


def validate_volume(volume):
    un = build_universe(volume)
    budget = (volume - 1) // 2
    cands = sorted(corrected_candidate_min_ids(un))
    total = 0
    targets = set()
    for s in cands:
        for t in iter_targets_seeded(un, s, budget):
            total += 1
            targets.add(frozenset(t))
    ref = {frozenset(t) for t in enumerate_connected_ck6_targets(volume)}
    return {"volume": volume,
            "corrected_total": total,
            "reference_total": len(ref),
            "totals_equal": total == len(ref),
            "set_equal": targets == ref,
            "n_shards_used": len(cands)}


def smoke_george_b9(time_cap_s=3600.0):
    """Run the V45 shard containing min-id 3590 for repo-M; stop when
    George's target is found.  Returns a result record."""
    plan, un = build_corrected_plan(45, n_shards=8)
    sh = shard_for_min_id(plan, GEORGE_B9_MIN_ORBIT_ID)
    print(f"shard {sh['shard']} holds min-id 3590 "
          f"({len(sh['min_ids'])} min-ids, ids "
          f"[{sh['min_ids'][0]}..{sh['min_ids'][-1]}])")
    piece = [tuple(int(v) for v in c) for c in PENTACUBES["M"]]
    ff = FastFunnel(piece, un["ball"])
    index = ff.index
    george = frozenset(GEORGE_B9_CORPUS_FRAME)
    state = {"funnel": Counter()}
    t0 = time.time()
    seen = 0
    result = None
    for s in sh["min_ids"]:
        for t in iter_targets_seeded(un, s, 22):
            seen += 1
            if frozenset(t) == george:
                stage, n, _ = funnel_and_cover(george, index, 9, state)
                result = {"found_after_targets": seen,
                          "elapsed_s": round(time.time() - t0, 1),
                          "funnel_stage": stage, "covers": n}
                print(f"  GEORGE TARGET FOUND after {seen} targets: "
                      f"{stage}, covers={n}")
                return result
            if time.time() - t0 > time_cap_s:
                print(f"  time cap hit after {seen} targets; "
                      f"George target not yet reached")
                return {"found": False, "targets_processed": seen,
                        "elapsed_s": round(time.time() - t0, 1)}
    return {"found": False, "targets_processed": seen,
            "note": "shard exhausted without George target"}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("--quick", action="store_true")
    sub.add_parser("plan")
    s = sub.add_parser("smoke")
    s.add_argument("--time-cap", type=float, default=3600.0)
    args = ap.parse_args()

    if args.cmd == "validate":
        for vol, exp in ((5, 2), (15, 368)):
            r = validate_volume(vol)
            print(r)
            assert r["totals_equal"] and r["set_equal"] and \
                r["corrected_total"] == exp, r
        if not args.quick:
            r = validate_volume(25)
            print(r)
            assert r["totals_equal"] and r["set_equal"] and \
                r["corrected_total"] == 71539, r
        print("VALIDATION OK (V5=2, V15=368"
              + ("" if args.quick else ", V25=71539") + ")")
    elif args.cmd == "plan":
        plan, _ = build_corrected_plan(45, n_shards=8)
        out = f"{REUSE}/ck6_v45_shards_corrected.json"
        with open(out, "w") as f:
            json.dump(plan, f, indent=1)
        print(f"wrote {out}: {plan['n_candidates']} candidate min-ids, "
              f"{len(plan['shards'])} shards")
    elif args.cmd == "smoke":
        rec = smoke_george_b9(args.time_cap)
        print(rec)


if __name__ == "__main__":
    main()

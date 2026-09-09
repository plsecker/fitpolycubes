#!/usr/bin/env python3
"""
Permanent regression test for the CK6 sharded-enumeration bug
(docs/frontier/ck6_sharding_bug.md).

Counterexample: George Sicherman's published "B 9" pentacube oddity
(sicherman.net/c5odd/c5nodd.html rev 2026-09-08), reconstructed
forensically (data/ck6_reuse/george_b9_geometry_reconciliation.json).
In the corpus frame it is a connected, exact-CK6, 45-cell target with

    minimum CK6-orbit id  = 3590,
    O_h canonical id      = oh-109166b4c83a,
    repo-M covers         = 12.

The V45 sharded count pass excluded min-id 3590 via an unsound
"seeded reachability" prefilter, so this target is absent from the
V45 corpus and the recorded "repo-M V45 = SAT 0" is not exhaustive.

The test asserts:
  1. the target is a valid connected exact-CK6 45-cell corpus target;
  2. its minimum orbit id is 3590 (build_universe(45) conventions);
  3. the OLD prefilter rejects min-id 3590        (bug reproduced);
  4. the CORRECTED sound filter accepts min-id 3590;
  5. the target is reachable by iter_targets_seeded mechanics
     (exact bounded BFS replay over the target's own orbits);
  6. repo-M tiles it in exactly 12 ways (independent full-domain
     enumeration);
  7. the corrected sharding (sound candidate filter + per-min-id
     seeded DFS) reproduces the reference corpora exactly:
        V5  = 2,  V15 = 368,  V25 = 71539
     with no duplicates or omissions (set equality against
     enumerate_connected_ck6_targets).

Run:  python3 tools/frontier/test_ck6_sharding_bug.py [--quick]
(--quick skips the V25 validation block.)
"""
import argparse
import json
import sys
import time
from collections import deque

import numpy as np

sys.path.insert(0, "/home/philip/Work/fitpolycubes")
sys.path.insert(0, "/home/philip/Work/fitpolycubes/solvers")

from t_ck6_oddity_v35_search import build_universe, iter_targets_seeded
from common.oddity import (enumerate_connected_ck6_targets,
                           is_face_connected)
from common.registry import PENTACUBES
from common.symmetry import ck6_affine_maps, canonical_form

# ---------------------------------------------------------------------------
# George B-9 target, corpus frame (rotation diag(1,-1,0,-1) applied and
# the inversion centre translated to the origin; see
# data/ck6_reuse/george_b9_geometry_reconciliation.json).
# ---------------------------------------------------------------------------
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
GEORGE_B9_OH_ID = "oh-109166b4c83a"
GEORGE_B9_MIN_ORBIT_ID = 3590
GEORGE_B9_M_COVERS = 12

FAILURES = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{status}] {name}" + (f" -- {detail}" if detail else ""))
    if not cond:
        FAILURES.append(name)
    return cond


def cid(coords):
    import hashlib
    h = hashlib.sha1(
        json.dumps(sorted(tuple(int(v) for v in c) for c in coords))
        .encode()).hexdigest()[:12]
    return h


def old_prefilter_candidates(un):
    """EXACT replica of the V45 sharded-count candidate-min-id prefilter
    (t_ck6_oddity_v35_search.py, cmd_count, 'validity prefilter: seeded
    reachability').  THIS IS THE BUGGY LOGIC -- kept here only to
    demonstrate the bug."""
    start_front = sorted(un["start_front"])
    cands = set(start_front)
    for s0 in start_front:
        stack = [s0]
        seen = {s0}
        while stack:
            v = stack.pop()
            for w in un["adj"][v]:
                if w >= s0 and w not in seen:
                    seen.add(w)
                    cands.add(w)
                    stack.append(w)
    return cands


def corrected_prefilter_candidates(un):
    """CORRECTED sound candidate-min-id filter.

    Necessity proof: let T be any connected CK6-closed target with
    minimum orbit id s.  T contains the centre cell (odd volume) and is
    face-connected, so its orbit-adjacency graph contains a path from s
    to some centre-adjacent (start-front) orbit, and every orbit on that
    path belongs to T, hence has id >= s.  Therefore s must be able to
    REACH a start-front orbit through adjacent orbits with ids >= s.
    This filter keeps every possible min-id (sound, may over-approximate;
    over-approximation is harmless -- empty shards yield 0).
    """
    start_front = set(un["start_front"])
    adj = un["adj"]
    n = len(adj)
    cands = set()
    for s in range(n):
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


def reachable_by_seeded_dfs(un, s, budget, target_mask, target_orbits):
    """Exact bounded replay of iter_targets_seeded's state mechanics,
    restricted to the target's own orbits (the full DFS explores a
    superset of states; the frontier is a function of the mask, so mask
    dedup is sound and this BFS decides reachability exactly)."""
    start_front = un["start_front"]
    adj, cost = un["adj"], un["cost"]
    seed_front = frozenset(j for j in (start_front | adj[s]) - {s}
                           if j >= s)
    seen = {(1 << s)}
    q = deque([(1 << s, budget - cost[s], seed_front)])
    orbits = set(target_orbits)
    while q:
        m, rem, fr = q.popleft()
        if m == target_mask:
            return True, len(seen)
        for j in fr:
            if j not in orbits:
                continue
            c = cost[j]
            if (m >> j) & 1 or c > rem:
                continue
            nm = m | (1 << j)
            if nm in seen:
                continue
            seen.add(nm)
            nf = frozenset(x for x in (fr | adj[j]) - {j} if x >= s)
            q.append((nm, rem - c, nf))
    return False, len(seen)


def full_domain_covers(target, piece):
    """Independent complete placement enumeration + Algorithm X.

    Anchoring: orientations are normalized (per-axis min = 0) but need
    NOT contain (0,0,0) as a cell (true for M and P), so the anchor
    (the placement's component-wise min corner) may lie OUTSIDE the
    target.  Anchoring over an extended box is therefore mandatory;
    anchoring at target cells alone is incomplete (this is exactly the
    trap documented in sicherman_c5nodd_compare.all_tilings).
    """
    from collections import defaultdict
    from common.algorithm_x import solve as xc
    from common.oddity import unique_orientations
    tgt = set(map(tuple, target))
    arr = np.asarray(sorted(tgt), dtype=int)
    mn, mx = arr.min(axis=0), arr.max(axis=0)
    span = np.asarray([max(c[i] for c in piece) for i in range(3)])
    rows, seen = [], set()
    for o in unique_orientations(piece):
        o = sorted(o)
        for bx in range(int(mn[0]) - int(span[0]) - 1, int(mx[0]) + 1):
            for by in range(int(mn[1]) - int(span[1]) - 1, int(mx[1]) + 1):
                for bz in range(int(mn[2]) - int(span[2]) - 1,
                                int(mx[2]) + 1):
                    p = frozenset((bx + c[0], by + c[1], bz + c[2])
                                  for c in o)
                    if p <= tgt and p not in seen:
                        seen.add(p)
                        rows.append(p)
    X = defaultdict(set)
    Y = {}
    for i, p in enumerate(rows):
        Y[i] = sorted(p)
        for c in p:
            X[c].add(i)
    for c in tgt:
        X.setdefault(c, set())
    return [sorted((rows[i] for i in sol), key=sorted)
            for sol in xc(X, Y)]


def corrected_shard_totals(volume):
    """Corrected sharding: sound candidate filter + per-min-id seeded
    DFS.  Returns (total, per-min-id counts, target set)."""
    un = build_universe(volume)
    budget = (volume - 1) // 2
    cands = sorted(corrected_prefilter_candidates(un))
    total = 0
    counts = {}
    targets = set()
    for s in cands:
        cnt = 0
        for t in iter_targets_seeded(un, s, budget):
            cnt += 1
            targets.add(frozenset(t))
        counts[s] = cnt
        total += cnt
    return total, counts, targets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="skip the V25 validation block")
    args = ap.parse_args()
    t0 = time.time()

    print("== CK6 sharding-bug regression (George B-9 counterexample) ==")
    target = frozenset(GEORGE_B9_CORPUS_FRAME)
    maps = list(ck6_affine_maps((0, 0)).values())

    # 1. validity
    check("target has 45 cells", len(target) == 45)
    check("target face-connected", is_face_connected(target))
    check("target CK6-closed about origin (corpus convention)",
          all(frozenset(m(c) for c in target) == target for m in maps))
    oh = "oh-" + cid(canonical_form(target))
    check("O_h canonical id == oh-109166b4c83a", oh == GEORGE_B9_OH_ID, oh)

    # 2. min orbit id
    un = build_universe(45)
    cell2orb = un["cell2orb"]
    noncentre = target - {(0, 0, 0)}
    assert (0, 0, 0) in target and all(c in cell2orb for c in noncentre)
    orbit_ids = sorted({cell2orb[c] for c in noncentre})
    mask = 0
    for i in orbit_ids:
        mask |= 1 << i
    s_min = (mask & -mask).bit_length() - 1
    check("minimum orbit id == 3590", s_min == GEORGE_B9_MIN_ORBIT_ID,
          str(s_min))
    budget = 22
    check("orbit cost == budget 22 (centre cell is free)",
          sum(un["cost"][i] for i in orbit_ids) == budget)

    # 3. old prefilter rejects 3590 (bug reproduced)
    old_cands = old_prefilter_candidates(un)
    check("OLD prefilter rejects min-id 3590 (bug present)",
          s_min not in old_cands,
          f"old candidate range [{min(old_cands)}..{max(old_cands)}], "
          f"|cands|={len(old_cands)}")

    # 4. corrected filter accepts 3590
    new_cands = corrected_prefilter_candidates(un)
    check("CORRECTED filter accepts min-id 3590", s_min in new_cands,
          f"|cands|={len(new_cands)}")
    # NOTE: the old filter is not a subset of the corrected one and need
    # not be -- the old filter also over-approximates.  Its defect is
    # excluding DEMONSTRATED-POSSIBLE min-ids like 3590, which checks 3+5
    # establish directly (3590 is realizable and reachable).

    # 5. reachability by the (sound) seeded-DFS mechanics
    reached, states = reachable_by_seeded_dfs(un, s_min, budget, mask,
                                              orbit_ids)
    check("target reachable by iter_targets_seeded mechanics "
          "(bounded exact replay)", reached, f"{states} states")

    # 6. repo-M tiles it in 12 ways
    piece_M = [tuple(int(v) for v in c) for c in PENTACUBES["M"]]
    covers = full_domain_covers(target, piece_M)
    check("repo-M covers == 12", len(covers) == GEORGE_B9_M_COVERS,
          str(len(covers)))

    # 7. corrected sharding reproduces the reference corpora
    for volume, expected in ((5, 2), (15, 368)):
        total, counts, targets = corrected_shard_totals(volume)
        ref = {frozenset(t) for t in enumerate_connected_ck6_targets(volume)}
        check(f"V{volume}: corrected sharding total == {expected}",
              total == expected, str(total))
        check(f"V{volume}: corrected sharding set == reference corpus "
              f"(no dups/omissions)", targets == ref,
              f"|sharded|={len(targets)} |ref|={len(ref)} "
              f"|intersection|={len(targets & ref)}")
    if not args.quick:
        t1 = time.time()
        total, counts, targets = corrected_shard_totals(25)
        ref = {frozenset(t) for t in enumerate_connected_ck6_targets(25)}
        check("V25: corrected sharding total == 71539", total == 71539,
              str(total))
        check("V25: corrected sharding set == reference corpus",
              targets == ref, f"|sharded|={len(targets)} |ref|={len(ref)}")
        print(f"  (V25 validation took {time.time()-t1:.1f}s)")

    print(f"\nelapsed {time.time()-t0:.1f}s; "
          f"{'ALL CHECKS PASSED' if not FAILURES else 'FAILURES: ' + str(FAILURES)}")
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())

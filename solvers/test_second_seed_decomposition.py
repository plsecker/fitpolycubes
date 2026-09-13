#!/usr/bin/env python3
"""
Deterministic regression test: second-seed decomposition
(iter_targets_seeded_pair / iter_targets_seeded_seeds /
iter_targets_seeded_single in solvers/t_ck6_oddity_v35_search.py).

The min-id-s CK6 search is partitioned exactly by q = second-smallest
selected orbit:

    full(s) == (union over q of pair(s, q)) | single(s)

where pair(s, q) yields exactly the connected CK6-closed targets whose
orbit set has minimum id s and second-minimum id q, and single(s) is the
degenerate {center} | orbit[s] target when budget - cost[s] == 0.

Tests:

  1. Full set equality at V5/V15/V25: for the top min-ids by target
     count (plus the smallest min-id with targets), the union of the
     (s, q) parts plus the single case equals the full min-id-s search,
     with no duplicates across q, and every target satisfies the
     min/second-min property, CK6 closure, and connectivity.
  2. Bounded V45 min-id-3590 (the production workload): every target in
     the first N of the full search has a valid (s, q) decomposition
     (min-id 3590, second-min q with cost[s] + cost[q] <= budget), and
     bounded (s, q) searches for the mandatory neighbors
     {3591, 3854, 3894} yield only valid, pairwise-disjoint targets.
"""

import os
import sys
from collections import Counter
from itertools import islice

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.oddity import enumerate_connected_ck6_targets, is_face_connected
from common.symmetry import ck6_affine_maps
from solvers.t_ck6_oddity_v35_search import (
    build_universe,
    iter_targets_seeded,
    iter_targets_seeded_pair,
    iter_targets_seeded_single,
)

# Bounded comparison depth at the production workload (min-id 3590).
BOUNDED_N = 50000   # full-search targets checked for decomposability
PAIR_N = 20000      # targets consumed per bounded (s, q) search


def orbit_ids(un, cells):
    c2o = un["cell2orb"]
    return sorted({c2o[c] for c in cells if c in c2o})


def minid_hist(volume):
    """True min-orbit-id histogram from the reference enumerator."""
    un = build_universe(volume)
    c2o = un["cell2orb"]
    hist = Counter()
    for t in enumerate_connected_ck6_targets(volume):
        ids = sorted({c2o[c] for c in t if c in c2o})
        hist[ids[0]] += 1
    return un, hist


def check_equivalence(volume, s, budget, maps):
    """Full min-id-s search vs union of (s, q) searches + single case."""
    un = build_universe(volume)
    full = set(frozenset(t) for t in iter_targets_seeded(un, s, budget))
    parts = {}
    for q in range(s + 1, len(un["all_orbits"])):
        if un["cost"][s] + un["cost"][q] > budget:
            continue
        parts[q] = set(frozenset(t)
                       for t in iter_targets_seeded_pair(un, s, q, budget))
    single = set(frozenset(t) for t in iter_targets_seeded_single(un, s,
                                                                  budget))
    union = set().union(*parts.values()) | single

    errors = []
    if union != full:
        errors.append("set mismatch: full=%d union=%d missing=%d extra=%d"
                      % (len(full), len(union), len(full - union),
                         len(union - full)))
    n_parts = sum(len(v) for v in parts.values())
    if n_parts + len(single) != len(union):
        errors.append("duplicates across q: parts=%d single=%d union=%d"
                      % (n_parts, len(single), len(union)))
    for q, ts in parts.items():
        for t in ts:
            ids = orbit_ids(un, t)
            if ids[0] != s or ids[1] != q:
                errors.append("min/second-min violation (s=%d,q=%d): ids=%s"
                              % (s, q, ids[:3]))
                break
        if errors:
            break
    for t in full:
        ids = orbit_ids(un, t)
        if ids[0] != s:
            errors.append("full target min-id != %d: ids=%s" % (s, ids[:3]))
            break
        if not all(frozenset(m(c) for c in t) == t for m in maps):
            errors.append("non-CK6-closed target in full")
            break
        if not is_face_connected(t):
            errors.append("disconnected target in full")
            break
    return dict(volume=volume, s=s, budget=budget, full_n=len(full),
                union_n=len(union), parts_n=n_parts, single_n=len(single),
                n_q=len(parts), errors=errors)


def test_full_equivalence():
    """V5/V15/V25: full min-id-s search == union of (s, q) parts + single."""
    maps = list(ck6_affine_maps((0, 0)).values())
    for volume in (5, 15, 25):
        un, hist = minid_hist(volume)
        top = [s for s, _ in sorted(hist.items(), key=lambda kv: -kv[1])[:3]]
        smallest = min(hist)
        if smallest not in top:
            top.append(smallest)
        for s in top:
            budget = (volume - 1) // 2
            res = check_equivalence(volume, s, budget, maps)
            assert not res["errors"], (
                f"V{volume} s={s}: " + "; ".join(res["errors"]))
            print(f"  PASS: V{volume} s={s}: full={res['full_n']} "
                  f"union={res['union_n']} parts={res['parts_n']} "
                  f"single={res['single_n']} n_q={res['n_q']}")


def test_bounded_v45_minid_3590():
    """V45 min-id-3590 (production workload): every full-search target has
    a valid (s, q) decomposition; bounded pair searches for the mandatory
    neighbors {3591, 3854, 3894} yield only valid, disjoint targets."""
    un = build_universe(45)
    s, budget = 3590, 22
    # Structural invariant: every connected min-id-3590 target contains
    # one of these (adj[3590] restricted to ids >= 3590; start_front
    # orbits are all < 3590, and any path from a target orbit to 3590
    # must enter 3590 through adj[3590]).
    mandatory = {3591, 3854, 3894}
    assert set(un["adj"][s]) & set(range(s, len(un["all_orbits"]))) == \
        mandatory, set(un["adj"][s]) & set(range(s, len(un["all_orbits"])))

    # 1. every target in the first BOUNDED_N of the full search has a
    #    valid (s, q) decomposition and contains a mandatory neighbor
    qs_seen = set()
    for t in islice(iter_targets_seeded(un, s, budget), BOUNDED_N):
        ids = orbit_ids(un, t)
        assert ids[0] == s, ids[:3]
        q = ids[1]
        assert q > s, ids[:3]
        assert un["cost"][s] + un["cost"][q] <= budget, (q,)
        assert set(ids) & mandatory, ids[:3]
        qs_seen.add(q)

    # 2. bounded pair searches: valid min/second-min, CK6 closure,
    #    connectivity, and pairwise disjointness
    maps = list(ck6_affine_maps((0, 0)).values())
    seen = set()
    for q in sorted(mandatory):
        n = 0
        for t in iter_targets_seeded_pair(un, s, q, budget):
            ids = orbit_ids(un, t)
            assert ids[0] == s and ids[1] == q, (q, ids[:3])
            assert is_face_connected(t)
            assert all(frozenset(m(c) for c in t) == t for m in maps)
            fs = frozenset(t)
            assert fs not in seen, f"duplicate target across q={q}"
            seen.add(fs)
            n += 1
            if n >= PAIR_N:
                break
        print(f"  PASS: V45 s={s} q={q}: {n} targets valid & disjoint")
    print(f"  PASS: V45 s={s}: first {BOUNDED_N} full-search targets all "
          f"decompose; q values seen: {sorted(qs_seen)}")


def main():
    print("Testing second-seed decomposition equivalence "
          "(iter_targets_seeded_pair vs iter_targets_seeded)...")
    print()
    test_full_equivalence()
    test_bounded_v45_minid_3590()
    print()
    print("All tests passed!")


if __name__ == "__main__":
    main()
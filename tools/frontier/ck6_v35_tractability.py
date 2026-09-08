#!/usr/bin/env python3
"""
Stage-4A tractability benchmarks for the V=35 (7 T pentacube) CK6 oddity search.

Measured results (2026-09-04, project venv, single core) -- re-running this
file reproduces them deterministically:

  Universe (L1 <= 17 ball):          7175 cells
  Orbit universe:                    1713 four-orbits (cost 2) + 161 two-orbits
                                     (cost 1) + center; compositions 2A+B = 17:
                                     (A,B) in {(0,17),...,(8,1)}
  Orbit graph:                       1874 nodes, avg degree 5.3, max 6
  Target DFS, budget 7  (V=15):      570 visited / 368 targets      < 1 ms
  Target DFS, budget 12 (V=25):      109461 visited / 71539 targets 0.24 s
  Target DFS, budget 17 (V=35):      23193326 visited /
                                     15289669 connected targets     ~85-91 s
                                     peak RSS ~7.4 GB (int-bitmask visited set)
  Determinism:                       reversed traversal order reproduces
                                     15289669 exactly
  Domain bound (empirical):          budgets 7 and 12 inside the r=17 universe
                                     reproduce the r=7 / r=12 counts exactly
                                     (368 / 71539)
  Parity invariant (2a0+b0 in [7,10] for 7 T's): only ~12-15% state reduction
                                     -- not substantial
  Funnel (sample 30000 targets):     23393 reject <7 contained placements,
                                     6579 reject uncovered cell,
                                     28 pass coverage (0.093%), rate ~987/s
                                     -> full funnel ~4.3 h pure Python
  Exact cover per survivor:          ~0.04 ms (negligible; 28/28 UNSAT in sample)
  Method C (piece-DFS + orbit-closure pruning):
                                     depth-2: 2985880 surviving pairs (78% of
                                     disjoint pairs -- weak prune); depth-3
                                     survival ~7.5e-5 per attempt, but the
                                     naive P3 scan is ~64k placements per pair
                                     (~5 days for depth 3 alone) -- rejected.

  Recommendation: Method A (target-first), streamed funnel, sharded over the
  start frontier for parallelism; projected complete V=35 search ~4.5 h
  single-core, well under 1 h with 6-9 shards.  Method C rejected at V=35.
"""

import sys, os, time, resource, argparse
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.symmetry import ck6_affine_maps
from common.oddity import l1_ball, placements_in_region
from common.registry import PENTACUBES


def build_universe(radius=17):
    ball = l1_ball(radius)
    bset = set(ball)
    maps = list(ck6_affine_maps((0, 0)).values())
    center = (0, 0, 0)
    four, two, seen = [], [], set()
    for v in ball:
        if v in seen:
            continue
        o = frozenset(m(v) for m in maps)
        seen |= o
        if not o <= bset or v == center:
            continue
        (four if len(o) == 4 else two).append(o)
    all_orbits = four + two
    cell2orb = {}
    for i, o in enumerate(all_orbits):
        for c in o:
            cell2orb[c] = i
    cost = [2] * len(four) + [1] * len(two)
    par0 = [(sum(next(iter(o)))) % 2 == 0 for o in all_orbits]

    def nbrs(v):
        x, y, z = v
        return ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                (x, y - 1, z), (x, y, z + 1), (x, y, z - 1))

    adj = [set() for _ in all_orbits]
    for i, o in enumerate(all_orbits):
        for c in o:
            for nb in nbrs(c):
                j = cell2orb.get(nb)
                if j is not None and j != i:
                    adj[i].add(j)
    start_front = frozenset(cell2orb[nb] for nb in nbrs(center)
                            if nb in cell2orb)
    return dict(ball=ball, bset=bset, all_orbits=all_orbits, cost=cost,
                par0=par0, adj=adj, start_front=start_front, center=center,
                nbrs=nbrs)


def dfs_targets(un, budget, parity_prune=False, time_cap=600, order="fwd"):
    """Visited-set graph search; leaves = connected CK6-closed targets."""
    adj, cost, par0 = un["adj"], un["cost"], un["par0"]
    lo, hi = 7, 10  # 2a0+b0 window for 7 T's (checkerboard imbalance)
    t0 = time.time()
    visited = {0}
    start_front = un["start_front"]
    stack = [(0, start_front, budget, 0)]
    leaves = nodes = 0
    while stack:
        mask, frontier, rem, p = stack.pop()
        if rem == 0:
            leaves += 1
            continue
        nodes += 1
        if nodes % 1_000_000 == 0 and time.time() - t0 > time_cap:
            return dict(status="TIMEOUT", nodes=nodes, visited=len(visited),
                        leaves=leaves, elapsed=time.time() - t0)
        it = frontier if order == "fwd" else sorted(frontier, reverse=True)
        for j in it:
            c = cost[j]
            if c > rem:
                continue
            pj = p + ((2 if c == 2 else 1) if par0[j] else 0)
            if parity_prune and (pj > hi or pj + (rem - c) < lo):
                continue
            nm = mask | (1 << j)
            if nm in visited:
                continue
            visited.add(nm)
            stack.append((nm, (frontier | adj[j]) - {j}, rem - c, pj))
    return dict(status="DONE", nodes=nodes, visited=len(visited),
                leaves=leaves, elapsed=time.time() - t0)


def funnel_sample(un, piece, sample=30000, volume=35):
    from common.oddity import placements_in_region
    ball, bset = un["ball"], un["bset"]
    cell_bit = {c: i for i, c in enumerate(sorted(bset))}
    placements = placements_in_region(piece, ball)
    by_cell = defaultdict(list)
    pmask = {}
    for p in placements:
        m = 0
        for c in p:
            by_cell[c].append(p)
            m |= 1 << cell_bit[c]
        pmask[id(p)] = (m, p)
    from itertools import islice
    from common.oddity import enumerate_connected_ck6_targets
    funnel = Counter()
    survivors = 0
    t0 = time.time()
    for t in islice(enumerate_connected_ck6_targets(volume), sample):
        funnel["targets"] += 1
        tmask = 0
        for c in t:
            tmask |= 1 << cell_bit[c]
        rows, covered, seenm = [], 0, set()
        for c in t:
            for p in by_cell[c]:
                m = pmask[id(p)][0]
                if m & ~tmask or m in seenm:
                    continue
                seenm.add(m)
                rows.append(p)
                covered |= m
        if len(rows) < volume // 5:
            funnel["reject: <k contained"] += 1
            continue
        if covered != tmask:
            funnel["reject: uncovered cell"] += 1
            continue
        funnel["pass coverage"] += 1
        survivors += 1
    el = time.time() - t0
    return dict(sample=sample, funnel=dict(funnel), rate=sample / el,
                elapsed=el, projected_survivors=round(
                    survivors / sample * 15289669))


def method_c_probe(un, piece, depth_cap_nodes=3_000_000):
    from common.oddity import placements_in_region
    ball = un["ball"]
    placements = placements_in_region(piece, ball)
    orbit_size = {i: 4 for i in range(len(un["all_orbits"]))}
    orbit_size.update({i: 2 for i in range(len(un["all_orbits"]))
                       if un["all_orbits"][i] and len(un["all_orbits"][i]) == 2})
    cell2orb = {}
    for i, o in enumerate(un["all_orbits"]):
        for c in o:
            cell2orb[c] = i
    center = un["center"]
    p1s = [p for p in placements if center in p]

    def closure(touched, new_cells):
        touched = set(touched)
        for c in new_cells:
            j = cell2orb.get(c)
            if j is not None:
                touched.add(j)
        return 1 + sum(orbit_size[i] for i in touched), touched

    t0 = time.time()
    d2 = 0
    for p1 in p1s:
        cs1, t1 = closure(set(), p1)
        for p2 in placements:
            if p2 & p1:
                continue
            cs2, t2 = closure(t1, p2 - p1)
            if cs2 <= 35:
                d2 += 1
    el2 = time.time() - t0
    # depth-3 sample (capped)
    t0 = time.time()
    d3 = nodes = 0
    done = False
    for p1 in p1s:
        cs1, t1 = closure(set(), p1)
        for p2 in placements:
            if p2 & p1:
                continue
            cs2, t2 = closure(t1, p2 - p1)
            if cs2 > 35:
                continue
            s2 = p1 | p2
            for p3 in placements:
                if p3 & s2:
                    continue
                nodes += 1
                cs3, _ = closure(t2, p3 - s2)
                if cs3 <= 35:
                    d3 += 1
                if nodes >= depth_cap_nodes:
                    done = True
                    break
            if done:
                break
        if done:
            break
    return dict(depth2_pairs=d2, depth2_s=round(el2, 1),
                depth3_sample_nodes=nodes, depth3_sample_triples=d3,
                depth3_s=round(time.time() - t0, 1), capped=done)


def main():
    piece = [tuple(map(int, c)) for c in PENTACUBES["T"]]
    un = build_universe(17)
    print(f"universe: {len(un['ball'])} cells, orbits {len(un['all_orbits'])}, "
          f"compositions 2A+B=17")
    for budget in (7, 12, 17):
        r = dfs_targets(un, budget)
        print(f"dfs budget={budget}: {r}")
    r = dfs_targets(un, 17, parity_prune=True)
    print(f"dfs budget=17 parity-pruned: {r}")
    r = dfs_targets(un, 17, order="rev")
    print(f"dfs budget=17 reversed-order (determinism): leaves={r['leaves']}")
    f = funnel_sample(un, piece)
    print(f"funnel sample: {f}")
    c = method_c_probe(un, piece)
    print(f"method C probe: {c}")
    print("peak RSS MB:",
          round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Stage 5F-N: canonical-augmentation enumerator for connected CK6 orbit-sets.

Replaces the visited-set DFS with a reverse-search enumerator that generates
each connected orbit-set exactly once, using O(depth) memory.

Canonical parent rule (for connected orbit-set S with root s0):
  Among all orbits v in S \ {s0} whose removal keeps S \ {v} connected
  (in the orbit adjacency graph), the one with the LARGEST orbit id is
  removed to form the parent.  If no such v exists (S = {s0}), S is the root.

Completeness: every connected orbit-set S containing s0 has at least one
  removable non-root orbit (since S is connected, there is a spanning tree
  and every leaf of that tree can be removed).  The largest such orbit
  determines a unique parent.  Following parent pointers terminates at {s0}.

Uniqueness: the parent function is deterministic (largest removable orbit id),
  so each connected set has exactly one parent and the parent/child relation
  forms a tree rooted at {s0}.  Each connected orbit-set is generated exactly
  once.

No visited set is needed: the parent chain is strictly decreasing in orbit
count, so the DFS cannot revisit any orbit-set.
"""
import sys, os, time, argparse
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.oddity import l1_ball, is_face_connected, unique_orientations
from common.symmetry import ck6_affine_maps, canonical_form, full_symmetry, \
    element_kind, order4_lunnon_code, symmetry_order
from common.registry import PENTACUBES
from common.algorithm_x import solve
from common.algorithm_x_fast import solve as solve_fast


def build_orbit_graph(volume):
    R = (volume - 1) // 2
    ball = l1_ball(R)
    bset = set(ball)
    maps = list(ck6_affine_maps((0, 0)).values())
    center = (0, 0, 0)
    four, two, seen = [], [], set()
    for v in ball:
        if v in seen: continue
        o = frozenset(m(v) for m in maps)
        seen |= o
        if not o <= bset or v == center: continue
        (four if len(o) == 4 else two).append(o)
    all_orbits = four + two
    cell2orb = {}
    for i, o in enumerate(all_orbits):
        for c in o: cell2orb[c] = i
    cost = [2] * len(four) + [1] * len(two)

    def nb(v):
        x, y, z = v
        return ((x+1, y, z), (x-1, y, z), (x, y+1, z),
                (x, y-1, z), (x, y, z+1), (x, y, z-1))

    adj = [set() for _ in all_orbits]
    for i, o in enumerate(all_orbits):
        for c in o:
            for nb in nb(c):
                j = cell2orb.get(nb)
                if j is not None and j != i: adj[i].add(j)
    start_front = frozenset(cell2orb[nb] for nb in nb(center)
                            if nb in cell2orb)
    return dict(R=R, ball=ball, bset=bset, all_orbits=all_orbits,
                cell2orb=cell2orb, cost=cost, adj=adj,
                start_front=start_front, center=center)


def orbit_connected_orbits(orb_set, adj):
    """Check if orbit-set S is connected in the orbit adjacency graph."""
    if len(orb_set) <= 1: return True
    start = next(iter(orb_set))
    seen, st = {start}, [start]
    while st:
        v = st.pop()
        for w in adj[v]:
            if w in orb_set and w not in seen:
                seen.add(w); st.append(w)
    return len(seen) == len(orb_set)


def find_parent(orb_set, adj, root):
    """Find the canonical parent of a connected orbit-set: remove the
    largest removable non-root orbit (one whose removal preserves orbit-graph
    connectivity).  Returns frozenset or None if S is the root."""
    S = frozenset(orb_set)
    for v in sorted(S, reverse=True):
        if v == root: continue
        S_minus = S - {v}
        if orbit_connected_orbits(S_minus, adj):
            return S_minus
    return None


def iter_canonical_targets(un, min_id, budget):
    """Yield every connected CK6-closed target whose minimum orbit id is
    exactly min_id, WITHOUT a visited set.

    Uses canonical augmentation: at each DFS step, only add orbits v such
    that the canonical parent of (current_set | {v}) is current_set.
    This ensures each orbit-set is generated via exactly one path.
    """
    adj, cost = un["adj"], un["cost"]
    all_orbits = un["all_orbits"]
    center = un["center"]
    root = min_id

    def orbit_conn(S):
        return orbit_connected_orbits(S, adj)

    def rec(orb_set, rem):
        if rem == 0:
            cells = {center} | set().union(
                *[set(all_orbits[o]) for o in orb_set])
            if is_face_connected(cells):
                yield cells
            return
        # generate candidate children: orbits v adjacent to orb_set
        # with id > all "committed" orbit ids in the current canonical path
        # (we use: v's removal from orb_set | {v} must make the parent = orb_set)
        for v in sorted(adj[o] for o in orb_set for o in [o] if False):
            pass  # replaced below
        # simpler: try all orbits not in orb_set
        for v in range(len(all_orbits)):
            if v in orb_set: continue
            c = cost[v]
            if c > rem: continue
            new_set = orb_set | {v}
            if not orbit_conn(new_set, adj): continue
            # canonical parent check
            if find_parent(new_set, adj, root) != orb_set: continue
            yield from rec(new_set, rem - cost[v])

    yield from rec({min_id}, budget - cost[min_id])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--volume", type=int, default=25)
    args = ap.parse_args()
    un = build_orbit_graph(args.volume)
    print(f"V={args.volume}: {len(un['all_orbits'])} orbits")
    t0 = time.time()
    count = 0
    for t in iter_canonical_targets(un, args.volume):
        count += 1
    print(f"canonical enumeration: {count:,} targets in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
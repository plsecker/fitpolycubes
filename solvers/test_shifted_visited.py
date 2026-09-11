#!/usr/bin/env python3
"""
Deterministic regression test: shifted-mask visited set in
iter_targets_seeded (solvers/t_ck6_oddity_v35_search.py).

The production visited set now stores orbit ids SHIFTED DOWN by the
per-search minimum id s (mask bit i represents orbit id i + s).  The
shift is a bijection on the masks reachable in one seeded search (all
bits lie in [s, 3937]), so the DFS explores the same states in the same
order and yields the same targets.

This test proves the transformation is exact on real universe data:

  1. Bounded old-vs-new at the production workload (V45, min-id 3590,
     budget 22): the first N yielded targets must be identical, in the
     same DFS order, AND the visited-set cardinality must be identical
     (proving the shift preserves state identity -- the memory-relevant
     invariant).
  2. Full old-vs-new target SET equality at V15 and V25 across every
     min-id (complete enumeration, no bounding).

The old reference below is a verbatim copy of the pre-shift
implementation (git c930c1e).
"""

import os
import sys
from itertools import islice

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solvers.t_ck6_oddity_v35_search import (
    build_universe,
    is_face_connected,
    iter_targets_seeded,
)

# Bounded comparison depth at the production workload (min-id 3590).
# 50K targets exercises deep masks (many bits set) in a few seconds per
# implementation; the full-set tests below are unbounded.
BOUNDED_N = 50000


def old_iter_targets_seeded(un, min_id, budget):
    """Reference copy of the ORIGINAL (pre-shift) implementation."""
    adj, cost = un["adj"], un["cost"]
    all_orbits = un["all_orbits"]
    center = un["center"]
    s = min_id
    frontier = frozenset(j for j in (un["start_front"] | adj[s]) - {s}
                         if j >= s)
    visited = {(1 << s)}
    stack = [((1 << s), frontier, budget - cost[s])]
    while stack:
        mask, frontier_, rem = stack.pop()
        if rem == 0:
            cells = {center}
            m = mask
            while m:
                b = m & -m
                cells |= set(all_orbits[b.bit_length() - 1])
                m ^= b
            if not is_face_connected(cells):
                continue
            yield cells
            continue
        for j in frontier_:
            c = cost[j]
            if c > rem:
                continue
            nm = mask | (1 << j)
            if nm in visited:
                continue
            visited.add(nm)
            nf = frozenset(x for x in (frontier_ | adj[j]) - {j} if x >= s)
            stack.append((nm, nf, rem - c))


def _bounded_run(gen_fn, un, min_id, budget, n):
    """Consume n targets from a generator; return (targets, visited_size).

    visited_size is read from the suspended generator's frame locals
    (same technique as test_strong_prune.py), so the REAL production
    function is exercised, not a copy.
    """
    gen = gen_fn(un, min_id, budget)
    targets = [frozenset(c) for c in islice(gen, n)]
    visited = len(gen.gi_frame.f_locals["visited"])
    return targets, visited


def _full_target_set(gen_fn, un, budget):
    """Complete target set across every possible min-id (unbounded)."""
    out = set()
    for s in range(len(un["all_orbits"])):
        for cells in gen_fn(un, s, budget):
            out.add(frozenset(cells))
    return out


def test_bounded_equivalence_v45_minid_3590():
    """Old vs new: identical first-N target sequence AND visited size.

    This is the production workload (V45, piece V, min-id 3590, budget
    22) that motivated the shift (22.4 GB peak RSS with the old
    representation).
    """
    un = build_universe(45)
    s, budget = 3590, 22
    old_targets, old_visited = _bounded_run(
        old_iter_targets_seeded, un, s, budget, BOUNDED_N)
    new_targets, new_visited = _bounded_run(
        iter_targets_seeded, un, s, budget, BOUNDED_N)

    assert len(old_targets) == len(new_targets) == BOUNDED_N, (
        len(old_targets), len(new_targets))
    assert old_targets == new_targets, (
        "target sequence diverged at index "
        f"{next(i for i, (a, b) in enumerate(zip(old_targets, new_targets))
                 if a != b)}")
    assert old_visited == new_visited, (old_visited, new_visited)
    print(f"  PASS: V45 min-id 3590: {BOUNDED_N} targets identical in "
          f"order; visited size {old_visited} == {new_visited}")


def test_full_equivalence_v15():
    """Old vs new: complete target set across all min-ids at V15."""
    un = build_universe(15)
    budget = (15 - 1) // 2
    old_set = _full_target_set(old_iter_targets_seeded, un, budget)
    new_set = _full_target_set(iter_targets_seeded, un, budget)
    assert old_set == new_set, (
        f"V15 divergence: |old|={len(old_set)} |new|={len(new_set)} "
        f"old-new={len(old_set - new_set)} new-old={len(new_set - old_set)}")
    print(f"  PASS: V15 full target set identical "
          f"({len(new_set)} targets)")


def test_full_equivalence_v25():
    """Old vs new: complete target set across all min-ids at V25."""
    un = build_universe(25)
    budget = (25 - 1) // 2
    old_set = _full_target_set(old_iter_targets_seeded, un, budget)
    new_set = _full_target_set(iter_targets_seeded, un, budget)
    assert old_set == new_set, (
        f"V25 divergence: |old|={len(old_set)} |new|={len(new_set)} "
        f"old-new={len(old_set - new_set)} new-old={len(new_set - old_set)}")
    print(f"  PASS: V25 full target set identical "
          f"({len(new_set)} targets)")


def main():
    print("Testing shifted-mask visited set equivalence "
          "(old vs new iter_targets_seeded)...")
    print()
    test_bounded_equivalence_v45_minid_3590()
    test_full_equivalence_v15()
    test_full_equivalence_v25()
    print()
    print("All tests passed!")


if __name__ == "__main__":
    main()
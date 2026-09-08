#!/usr/bin/env python3
"""
Exact achievable-length set for V macro walks through state 0.

A closed walk through 0 that leaves SCC(0) can never return (condensation is
a DAG), so every closed walk through 0 lives entirely inside SCC(0).
We therefore compute, inside SCC(0):

    R_0 = {0};   R_{k+1} = N(R_k) ∩ SCC0

and obtain  ACHIEVABLE = { k : 0 ∈ R_k },  which by the faithfulness theorem
equals { z : 3×b×z box is tileable } — exactly, up to the bound `--bound`.

Also reports the eventual periodicity (period d, conductor c: for all k ≥ c,
k ∈ ACHIEVABLE ⟺ d | k) and compares with catalogue facts.

Usage: python3 tools/frontier/v_piece/v_exact_walk_lengths.py [--a 3 --b 5 --bound 240]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.frontier.macro_explorer import macro_closure
from tools.frontier.v_piece.analyze_v_closure import (
    tarjan_sccs, reverse_graph,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", type=int, default=3)
    ap.add_argument("--b", type=int, default=5)
    ap.add_argument("--piece", type=str, default="V")
    ap.add_argument("--bound", type=int, default=240)
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    macro_seen, succ, sources, stats = macro_closure(
        args.piece, args.a, args.b, max_states=20_000_000, verbose=False)
    assert stats["zero_reachable"]
    assert not stats["first_gen_cap_hit"] and not stats["macro_cap_hit"]

    sccs = tarjan_sccs(succ)
    comp_of = {}
    for i, comp in enumerate(sccs):
        for u in comp:
            comp_of[u] = i
    scc0 = set(sccs[comp_of[0]])

    # restrict graph to SCC(0)
    succ0 = {u: {v for v in succ.get(u, ()) if v in scc0} for u in scc0}

    # layered forward reachability, exact
    B = args.bound
    R = {0: {0}}
    achieved = []
    for k in range(1, B + 1):
        nxt = set()
        for u in R[k - 1]:
            nxt |= succ0[u]
        R[k] = nxt
        if 0 in nxt:
            achieved.append(k)

    # period via BFS-delta on SCC0 (recompute independently)
    from collections import deque
    dist = {0: 0}
    q = deque([0])
    while q:
        u = q.popleft()
        for v in succ0[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    g = 0
    for u in succ0:
        for v in succ0[u]:
            g = math.gcd(g, dist[v] - dist[u] - 1)

    aset = set(achieved)
    # conductor: smallest c such that for all d-multiples k >= c, k achieved
    multiples = [k for k in range(2, B + 1, g)]
    conductor = None
    for c in range(0, B + 1):
        if all((k in aset) for k in multiples if k >= c):
            conductor = c
            break

    even_gaps = [k for k in range(0, min(B, 60) + 1) if k % 2 == 0 and k not in aset]
    odd_in_set = [k for k in aset if k % 2 == 1]

    result = {
        "piece": args.piece,
        "cross_section": {"a": args.a, "b": args.b},
        "method": "exact layered BFS inside SCC(0); closed walks through 0 never leave SCC(0)",
        "bound": B,
        "achievable_lengths": achieved,
        "count_up_to_bound": len(achieved),
        "period_bfs_delta": g,
        "conductor_for_multiples_of_period": conductor,
        "even_gaps_below_60": even_gaps,
        "odd_lengths_present": odd_in_set,
        "catalogue_cross_check": {
            "primes_6_and_8_achieved": 6 in aset and 8 in aset,
            "published_impossible_4_absent": 4 not in aset,
            "published_impossible_10_absent": 10 not in aset,
            "no_odd_lengths": not odd_in_set,
        },
        "eventual_description": (
            f"achievable = {{ k : {g} | k, k >= {conductor} }} "
            f"plus small exceptions below conductor"
        ),
    }

    print(json.dumps(result, indent=2))

    out = args.out or str(REPO_ROOT / f"data/frontier/v_piece/v_{args.a}x{args.b}_exact_walk_lengths.json")
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Resolve which order-4 Lunnon class George Sicherman's 5-R oddity uses.

For each of the nine order-4 polycube symmetry classes:
  1. build the group as explicit 3x3 integer matrices and validate it
     against common.symmetry.order4_lunnon_code,
  2. compute the orbits of the 125 cells of the 5x5x5 box {-2..2}^3,
  3. search for all tilings of a G-invariant, face-connected 25-cell
     target by exactly five proper-rotation R placements (backtracking
     over placements with orbit-closure pruning; the target is implicit:
     the union of the five placements must be a union of G-orbits),
  4. count the connected G-invariant 25-cell targets (reverse search
     over orbit subsets + cell-connectivity check, time-budgeted),
  5. report a table: class | generators/orbit type | connected targets |
     tileable | canonical witness count.

Coordinate convention: placements are generated in the {0..4}^3 box by
common.polycube_utils.generate_placements and translated by (-2,-2,-2)
into the {-2..2}^3 box used for targets.  (The earlier EE4 run forgot
this translation, which made every target trivially unsatisfiable.)

Usage:
    python3 tools/order4_R_class_comparison.py [--classes EE4 CE3 BF6]
        [--max-tilings N] [--node-budget N] [--count-budget S]
        [--skip-count] [--out PATH]
"""

import argparse
import json
import os
import sys
import time

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from common.registry import PENTACUBES
from common.polycube_utils import generate_placements
from common.symmetry import normalize, order4_lunnon_code

# ---------------------------------------------------------------------------
# Order-4 groups as explicit 3x3 integer matrices (acting on column vectors)
# ---------------------------------------------------------------------------


def M(rows):
    return np.array(rows, dtype=int)


I     = M([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
MX    = M([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])    # mirror plane x = 0
MY    = M([[1, 0, 0], [0, -1, 0], [0, 0, 1]])    # mirror plane y = 0
MZ    = M([[1, 0, 0], [0, 1, 0], [0, 0, -1]])    # mirror plane z = 0
RZ    = M([[-1, 0, 0], [0, -1, 0], [0, 0, 1]])   # c2 about z-axis
RX    = M([[1, 0, 0], [0, -1, 0], [0, 0, -1]])   # c2 about x-axis
RY    = M([[-1, 0, 0], [0, 1, 0], [0, 0, -1]])   # c2 about y-axis
INV   = M([[-1, 0, 0], [0, -1, 0], [0, 0, -1]])  # inversion
MXY   = M([[0, 1, 0], [1, 0, 0], [0, 0, 1]])     # mirror plane x = y
MXNY  = M([[0, -1, 0], [-1, 0, 0], [0, 0, 1]])   # mirror plane x = -y
R110  = M([[0, 1, 0], [1, 0, 0], [0, 0, -1]])    # c2 about axis (1,1,0)
R1N10 = M([[0, -1, 0], [-1, 0, 0], [0, 0, -1]])  # c2 about axis (1,-1,0)
C4Z   = M([[0, -1, 0], [1, 0, 0], [0, 0, 1]])    # c4 about z-axis
C4Z3  = M([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])    # c4^-1 about z-axis
S4Z   = M([[0, -1, 0], [1, 0, 0], [0, 0, -1]])   # s4 about z-axis
S4Z3  = M([[0, 1, 0], [-1, 0, 0], [0, 0, -1]])   # s4^-1 about z-axis

CLASS_GROUPS = {
    "A12": [I, C4Z, RZ, C4Z3],
    "J10": [I, S4Z, RZ, S4Z3],
    "BB10": [I, RX, RY, RZ],
    "BC10": [I, RZ, R110, R1N10],
    "CE3": [I, MZ, MXY, R110],
    "BF6": [I, RZ, MXY, MXNY],
    "EE4": [I, MX, MY, RZ],
    "BE4": [I, RZ, INV, MZ],
    "CK6": [I, R110, INV, MXNY],
}

CLASS_DESC = {
    "A12": "cyclic C4 about z (no mirrors)",
    "J10": "cyclic S4 about z (no mirrors)",
    "BB10": "c2 axes x,y,z (no mirrors)",
    "BC10": "c2 axes z,(1,1,0),(1,-1,0) (no mirrors)",
    "CE3": "mirrors z=0 & x=y; product c2 about (1,1,0)",
    "BF6": "mirrors x=y & x=-y; product c2 about z",
    "EE4": "mirrors x=0 & y=0; product c2 about z",
    "BE4": "mirror z=0 + inversion; product c2 about z",
    "CK6": "mirror x=-y + inversion; product c2 about (1,1,0)",
}


def _key(m):
    return tuple(tuple(int(v) for v in row) for row in m)


def validate_groups():
    for name, mats in CLASS_GROUPS.items():
        code = order4_lunnon_code(mats)
        assert code == name, f"{name}: order4_lunnon_code returned {code}"
        keys = {_key(m) for m in mats}
        assert len(keys) == 4, f"{name}: not 4 distinct elements"
        for a in mats:
            for b in mats:
                assert _key(a @ b) in keys, f"{name}: not closed under multiplication"
    print("validated: all nine order-4 groups are closed and match order4_lunnon_code")


# ---------------------------------------------------------------------------
# Box, orbits, placements
# ---------------------------------------------------------------------------

BOX_CELLS = [(x, y, z) for x in range(-2, 3) for y in range(-2, 3)
             for z in range(-2, 3)]
BOX_SET = frozenset(BOX_CELLS)


def orbits_of(cells, mats):
    seen = set()
    orbits = []
    for v in cells:
        if v in seen:
            continue
        o = frozenset(tuple(int(c) for c in m @ np.array(v)) for m in mats)
        orbits.append(o)
        seen |= o
    return orbits


def build_placements():
    raw, _ = generate_placements(PENTACUBES["R"], (5, 5, 5))
    placements = [frozenset(tuple(c - 2 for c in cell) for cell in p)
                  for p in raw.values()]
    for p in placements:
        assert p <= BOX_SET, p
    return placements


# ---------------------------------------------------------------------------
# Tiling search: 5 proper-rotation R placements, G-invariant connected union
# ---------------------------------------------------------------------------

def search_class(placements, pclosure, max_tilings=2000, node_budget=None):
    n = len(placements)
    results = []
    nodes = 0
    t0 = time.time()

    def connected(cells):
        cells = set(cells)
        if not cells:
            return True
        start = next(iter(cells))
        stack = [start]
        seen = {start}
        while stack:
            x, y, z = stack.pop()
            for nb in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                       (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if nb in cells and nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        return len(seen) == len(cells)

    by_cell = {}
    for i, p in enumerate(placements):
        for c in p:
            by_cell.setdefault(c, []).append(i)

    def rec(P, C, chosen, start):
        nonlocal nodes
        nodes += 1
        if node_budget is not None and nodes > node_budget:
            raise TimeoutError("node budget exceeded")
        if len(P) == 25:
            if C == P and connected(P):
                results.append((frozenset(P), tuple(chosen)))
            return
        # prune: every must-cover cell (C \ P) needs an available placement
        for c in C - P:
            ok = False
            for i in by_cell[c]:
                if i < start:
                    continue
                p = placements[i]
                if p & P:
                    continue
                if len(C | pclosure[i]) <= 25:
                    ok = True
                    break
            if not ok:
                return
        for i in range(start, n):
            p = placements[i]
            if p & P:
                continue
            C2 = C | pclosure[i]
            if len(C2) > 25:
                continue
            rec(P | p, C2, chosen + (i,), i + 1)
            if len(results) >= max_tilings:
                return

    for i in range(n):
        rec(placements[i], pclosure[i], (i,), i + 1)
        if len(results) >= max_tilings:
            break
    return results, nodes, time.time() - t0


# ---------------------------------------------------------------------------
# Count connected G-invariant 25-cell targets (reverse search, budgeted)
# ---------------------------------------------------------------------------

def count_connected_targets(orbits, adj, weights, W=25, time_budget=60.0):
    """Count connected G-invariant W-cell targets.

    Reverse search over orbit subsets (each connected subset is generated
    exactly once from its parent: remove the largest-index removable
    vertex), with a cell-level face-connectivity check at weight W.
    Returns (count, nodes_explored); raises TimeoutError on budget.
    """
    n = len(orbits)
    adj_mask = [0] * n
    for u in range(n):
        for v in adj[u]:
            adj_mask[u] |= 1 << v
    t0 = time.time()
    stats = {"total": 0, "nodes": 0, "timed_out": False}

    def orbit_connected(mask):
        if not mask:
            return True
        start = (mask & -mask).bit_length() - 1
        seen = 0
        stack = [start]
        while stack:
            u = stack.pop()
            if seen >> u & 1:
                continue
            seen |= 1 << u
            nb = adj_mask[u] & mask & ~seen
            while nb:
                b = nb & -nb
                stack.append(b.bit_length() - 1)
                nb ^= b
        return seen == mask

    def cell_connected(mask):
        cells = set()
        m = mask
        while m:
            b = m & -m
            cells |= orbits[b.bit_length() - 1]
            m ^= b
        if not cells:
            return True
        start = next(iter(cells))
        stack = [start]
        seen = {start}
        while stack:
            x, y, z = stack.pop()
            for nb in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                       (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if nb in cells and nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        return len(seen) == len(cells)

    def dfs(mask, weight):
        stats["nodes"] += 1
        if time.time() - t0 > time_budget:
            stats["timed_out"] = True
            return
        if weight == W:
            if cell_connected(mask):
                stats["total"] += 1
            return
        cand = 0
        m = mask
        while m:
            b = m & -m
            cand |= adj_mask[b.bit_length() - 1]
            m ^= b
        cand &= ~mask
        c = cand
        while c:
            b = c & -c
            v = b.bit_length() - 1
            c ^= b
            if weight + weights[v] > W:
                continue
            # child condition: v is the largest removable vertex of S|{v}
            ok = True
            m2 = mask
            while m2:
                b2 = m2 & -m2
                w = b2.bit_length() - 1
                m2 ^= b2
                if w > v and orbit_connected((mask | b) & ~b2):
                    ok = False
                    break
            if ok:
                dfs(mask | b, weight + weights[v])
                if stats["timed_out"]:
                    return

    for r in range(n):
        dfs(1 << r, weights[r])
        if stats["timed_out"]:
            break
    if stats["timed_out"]:
        raise TimeoutError("connected-target count timed out")
    return stats["total"], stats["nodes"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--classes", nargs="*", default=None)
    ap.add_argument("--max-tilings", type=int, default=2000)
    ap.add_argument("--node-budget", type=int, default=None)
    ap.add_argument("--count-budget", type=float, default=60.0)
    ap.add_argument("--skip-count", action="store_true")
    ap.add_argument("--out",
                    default="tools/frontier/order4_R_class_comparison_results.json")
    args = ap.parse_args()

    validate_groups()
    placements = build_placements()
    print(f"R placements in 5x5x5 box (translated to -2..2): {len(placements)}")

    classes = args.classes or list(CLASS_GROUPS)
    rows = []
    for name in classes:
        mats = CLASS_GROUPS[name]
        print(f"\n=== {name}: {CLASS_DESC[name]} ===")
        orbits = orbits_of(BOX_CELLS, mats)
        sizes = {}
        for o in orbits:
            sizes[len(o)] = sizes.get(len(o), 0) + 1
        print(f"orbits: {dict(sorted(sizes.items()))} (total {len(orbits)})")
        orbit_of = {}
        for idx, o in enumerate(orbits):
            for c in o:
                orbit_of[c] = idx
        weights = [len(o) for o in orbits]
        adj = [set() for _ in orbits]
        for oi, o in enumerate(orbits):
            for c in o:
                x, y, z = c
                for nb in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                           (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                    if nb in orbit_of:
                        adj[oi].add(orbit_of[nb])
            adj[oi].discard(oi)
        pclosure = []
        for p in placements:
            cells = set()
            for c in p:
                cells |= orbits[orbit_of[c]]
            pclosure.append(frozenset(cells))

        results, nodes, dt = search_class(placements, pclosure,
                                          args.max_tilings, args.node_budget)
        targets = {}
        for target, chosen in results:
            targets.setdefault(normalize(target), []).append((target, chosen))
        tileable = len(results) > 0
        print(f"search: {nodes} nodes in {dt:.1f}s, {len(results)} tilings, "
              f"{len(targets)} distinct canonical targets")

        if args.skip_count:
            count = None
        else:
            try:
                count, cnodes = count_connected_targets(orbits, adj, weights,
                                                        25, args.count_budget)
                print(f"connected 25-cell targets: {count} "
                      f"({cnodes} orbit-subsets explored)")
            except TimeoutError as e:
                count = None
                print(f"connected 25-cell targets: n/a ({e})")

        row = {
            "class": name,
            "desc": CLASS_DESC[name],
            "orbit_sizes": {str(k): v for k, v in sorted(sizes.items())},
            "connected_targets": count,
            "tileable": tileable,
            "tilings": len(results),
            "canonical_witnesses": len(targets),
            "search_nodes": nodes,
            "search_seconds": round(dt, 2),
            "capped": len(results) >= args.max_tilings,
        }
        if tileable:
            first_target, first_chosen = next(iter(targets.values()))[0]
            row["witness"] = {
                "target": sorted(first_target),
                "placements": [sorted(placements[i]) for i in first_chosen],
            }
        rows.append(row)

    print("\n=== TABLE ===")
    print(f"{'class':6} {'orbit type':30} {'conn targets':>13} "
          f"{'tileable':>8} {'canonical witnesses':>20}")
    for r in rows:
        ct = "n/a" if r["connected_targets"] is None else str(r["connected_targets"])
        print(f"{r['class']:6} {r['desc']:30} {ct:>13} "
              f"{str(r['tileable']):>8} {r['canonical_witnesses']:>20}")
    with open(args.out, "w") as f:
        json.dump(rows, f, indent=2)
    print(f"\nresults written to {args.out}")


if __name__ == "__main__":
    main()
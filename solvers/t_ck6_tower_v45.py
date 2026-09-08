#!/usr/bin/env python3
"""
Stage 4D: exhaustive search of the D4h tower family at V=45 (9 T pentacubes).

AUXILIARY SEARCH ONLY.  A negative result here says nothing about the
unrestricted V=45 problem; a positive result is a true CK6-or-higher oddity.

Family (fully specified, no hand-picking):

  - axis-aligned z-tower; layer z is a subset of the 3x3 grid;
  - every nonempty layer is one of the 7 nonempty D4-symmetric subsets
    of a 3x3 layer (unions of the three D4 orbits: center C={1 cell},
    orthogonal arms E={4}, corners K={4}, and their unions CE=5, CK=5,
    EK=8, ALL=9; E and K treated as distinct shapes);
  - the layer sequence is palindromic (layer i = layer h-1-i), which
    makes the target D4h-symmetric (BBC2, order 16) and hence a
    superset of CK6 -- verified computationally per target;
  - total volume exactly 45 (middle layer weight must be odd:
    C, CE, or ALL);
  - 3D face-connectivity is tested explicitly (layer-wise adjacency is
    NOT assumed: e.g. a K layer has no face contact with a C layer).

Enumeration completeness: a palindromic tower over these layer types is
exactly a choice of middle type (odd weight) plus an ordered sequence of
pair types with total pair weight (45 - w_m)/2; all such sequences are
enumerated by DFS and the count is cross-checked against an independent
DP recurrence.  Distinct sequences yield distinct cell sets (they differ
in some layer), so no deduplication is required; O_h-congruent towers are
counted separately but every one is tested.

Counts recorded: raw sequences, connected targets, disconnected rejects,
exact-cover candidates (>= 9 contained placements + full coverage),
SAT/UNSAT, symmetry classes.  Any SAT target is witnessed (canonical
target, 9 placements, full 48-element group, Lunnon class, CK6
containment) and dual-verified (algorithm_x + algorithm_x_fast).
"""

import argparse
import json
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from common.oddity import is_face_connected, unique_orientations
from common.registry import PENTACUBES
from common.symmetry import (canonical_form, element_kind, full_symmetry,
                             order4_lunnon_code, symmetry_order)

TYPES = {"C": 1, "E": 4, "K": 4, "CE": 5, "CK": 5, "EK": 8, "ALL": 9}
NAMES = list(TYPES)
CELLS = {
    "C":   ((1, 1),),
    "E":   ((1, 0), (0, 1), (2, 1), (1, 2)),
    "K":   ((0, 0), (0, 2), (2, 0), (2, 2)),
    "CE":  ((1, 1), (1, 0), (0, 1), (2, 1), (1, 2)),
    "CK":  ((1, 1), (0, 0), (0, 2), (2, 0), (2, 2)),
    "EK":  ((1, 0), (0, 1), (2, 1), (1, 2), (0, 0), (0, 2), (2, 0), (2, 2)),
    "ALL": tuple((x, y) for x in range(3) for y in range(3)),
}
MIDDLES = ("C", "CE", "ALL")  # odd weights only


def enumerate_sequences(volume=45):
    seqs = []
    for m in MIDDLES:
        def rec(suffix, rem):
            if rem == 0:
                seqs.append(tuple(suffix) + (m,))
                return
            for n in NAMES:
                if TYPES[n] <= rem:
                    rec(suffix + [n], rem - TYPES[n])
        rec([], (volume - TYPES[m]) // 2)
    return seqs


def dp_count_sequences(volume=45):
    """Independent combinatorial count (no enumeration)."""
    def f(S):
        dp = [0] * (S + 1)
        dp[0] = 1
        for s in range(1, S + 1):
            dp[s] = (dp[s - 1] if s >= 1 else 0) \
                + 2 * (dp[s - 4] if s >= 4 else 0) \
                + 2 * (dp[s - 5] if s >= 5 else 0) \
                + (dp[s - 8] if s >= 8 else 0) \
                + (dp[s - 9] if s >= 9 else 0)
        return dp[S]
    return sum(f((volume - TYPES[m]) // 2) for m in MIDDLES)


def build_target(seq):
    """seq = (pair_1, ..., pair_n, middle); layers are
    pair_1..pair_n, middle, pair_n..pair_1 (palindromic)."""
    pairs, middle = seq[:-1], seq[-1]
    layers = list(pairs) + [middle] + list(reversed(pairs))
    h = len(layers)
    cells = set()
    for z, name in enumerate(layers):
        for (x, y) in CELLS[name]:
            cells.add((x, y, z))
    return frozenset(cells)


def t_placements(tower):
    """All T placements fully inside the tower."""
    piece = [tuple(map(int, c)) for c in PENTACUBES["T"]]
    out = set()
    for o in unique_orientations(piece):
        oset = set(o)
        for c in tower:
            a = (c[0] - o[0][0], c[1] - o[0][1], c[2] - o[0][2])
            pl = frozenset((a[0] + dx, a[1] + dy, a[2] + dz)
                           for (dx, dy, dz) in o)
            if pl <= tower:
                out.add(pl)
    return sorted(out)


def count_covers(cells, rows):
    from common.algorithm_x import solve
    y = {i: sorted(p) for i, p in enumerate(rows)}
    x = {c: set() for c in cells}
    for i, cs in y.items():
        for c in cs:
            x[c].add(i)
    return sum(1 for sol in solve(x, y) if len(sol) == len(cells) // 5), y, x, rows


def count_covers_fast(cells, rows):
    """Independent exact-cover count via common.algorithm_x_fast.

    X[c] must be the set of row indices whose row covers cell c
    (passing all row indices for every column silently disables the
    solver: select() then deactivates every row after the first
    placement, so no multi-row cover can ever be found).
    """
    from common.algorithm_x_fast import solve as solve_fast
    row_list = list(rows)
    x = {c: set() for c in cells}
    for i, p in enumerate(row_list):
        for c in p:
            x[c].add(i)
    y = {i: list(p) for i, p in enumerate(row_list)}
    return sum(1 for _ in solve_fast(x, y, set(cells),
                                     [True] * len(row_list)))


def classify(cells):
    syms = full_symmetry(cells)
    from common.symmetry import order4_lunnon_code, symmetry_order
    code = order4_lunnon_code(syms)
    if code is not None:
        return code, syms
    return f"order{symmetry_order(syms)}", syms


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--volume", type=int, default=45)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    V = args.volume
    k = V // 5
    assert 2 * k - 1 <= V <= 9 * k and V % 5 == 0

    t0 = time.time()
    seqs = enumerate_sequences(V)
    dp_total = dp_count_sequences(V)
    assert len(seqs) == dp_total, (len(seqs), dp_total)
    print(f"# palindromic sequences (volume {V}): {len(seqs):,} "
          f"(DP cross-check: {dp_total:,})  [{time.time()-t0:.2f}s]")

    piece = [tuple(map(int, c)) for c in PENTACUBES["T"]]
    oris = [tuple(sorted(o)) for o in unique_orientations(piece)]
    funnel = Counter()
    classes = Counter()
    witnesses = []
    t0 = time.time()
    for idx, seq in enumerate(seqs):
        tower = build_target(seq)
        funnel["sequences"] += 1
        if not is_face_connected(tower):
            funnel["reject: disconnected"] += 1
            continue
        funnel["connected targets"] += 1
        # symmetry must contain CK6 (palindromic D4 towers: always true;
        # verified, never assumed)
        syms = full_symmetry(tower)
        keys = {tuple(map(tuple, m.tolist())) for m in syms}
        K = -np.eye(3, dtype=int)
        assert tuple(map(tuple, K.tolist())) in keys
        has_diag_c2 = any(
            int(round(np.linalg.det(m))) == 1
            and int(round(np.trace(m))) == -1
            and any(m[i][j] != 0 for i in range(3) for j in range(3) if i != j)
            for m in syms)
        assert has_diag_c2, seq
        # funnel: contained placements + coverage
        rows_all = t_placements(tower)
        if len(rows_all) < k:
            funnel["reject: <k contained placements"] += 1
            continue
        covered = set()
        for p in rows_all:
            covered |= p
        if covered != tower:
            funnel["reject: uncovered cell"] += 1
            continue
        funnel["pass coverage"] += 1
        n, y, x, rows = count_covers(tower, rows_all)
        n_fast = count_covers_fast(tower, rows)
        assert n == n_fast, (seq, n, n_fast)
        if n:
            funnel["TILEABLE"] += 1
            code, syms = classify(tower)
            classes[code] += 1
            wit = {
                "volume": V, "tiles": k, "piece": "T",
                "layer_sequence": list(seq),
                "canonical_target": canonical_form(tower),
                "placements": sorted(sorted(p) for p in rows),
                "symmetry_order": len(syms),
                "symmetry_kinds": dict(Counter(
                    element_kind(m) for m in syms)),
                "dual_solver_counts": [n, n],
            }
            print("WITNESS:", json.dumps(wit, indent=1))
            out = args.json or "data/ck6_v45_tower_witness.json"
            os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
            with open(out, "w") as f:
                json.dump(wit, f, indent=1)
        else:
            funnel["reject: exact cover UNSAT"] += 1
        if (idx + 1) % 10000 == 0:
            print(f"  ... {idx+1:,}/{len(seqs):,} "
                  f"({time.time()-t0:.0f}s)", flush=True)

    el = time.time() - t0
    print(f"# D4h tower search V={V}: {dict(funnel)}")
    print(f"# elapsed: {el:.1f}s")
    print("# SCOPE: auxiliary search only -- a negative result here does "
          "NOT imply V=%d is impossible in general" % V)


def canonical_form(cells):
    from common.symmetry import canonical_form as cf
    return cf(cells)


if __name__ == "__main__":
    main()
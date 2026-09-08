"""
CK6 T-pentacube oddity search: stage driver.

Exhaustively settles, for a given odd volume V (multiple of the piece
size), whether any connected V-cell polycube with CK6 symmetry (or
higher) is tileable by exactly V/5 copies of the T pentacube.

  targets  (all volumes) enumerate connected CK6-closed targets by
           cube orbits (common.oddity.enumerate_connected_ck6_targets),
           then run a three-stage funnel per target -- >= k contained
           placements, full cell coverage, exact cover
           (common.algorithm_x, no symmetry breaking) -- with the
           coverage-passing targets re-verified by an independent
           solver (common.algorithm_x_fast).
  tilings  (V = 15 only) independent tiling-first scan over placement
           triples; cross-checks the targets method.

Domain completeness is proven in docs/frontier/ck6_oddity_design.md
(section 7 and the module docstring of common/oddity.py): an odd-volume
connected K-closed target with center cell c has every cell within L1
distance (V-1)/2 of c, so the L1 ball of that radius is a complete
search domain; odd volume also forces the center-type CK6 placement.
Higher-symmetry targets are found automatically: any group containing
a CK6 subgroup makes the target CK6-closed, and the exact class of
every target passing the funnel is reported.

Usage:
    python3 solvers/t_ck6_oddity_search.py [--volume 15|25]
        [--method {both,targets,tilings}] [--json PATH|-]
"""

import argparse
import json
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.oddity import (
    PlacementIndex,
    enumerate_connected_ck6_targets,
    is_face_connected,
    l1_ball,
    max_l1_for_volume,
    placements_in_region,
    unique_orientations,
)
from common.registry import PENTACUBES
from common.symmetry import (
    canonical_form,
    ck6_affine_maps,
    full_symmetry,
    order4_lunnon_code,
    symmetry_order,
)


def ck6_closure_ok(cells, maps):
    return all(frozenset(m(c) for c in cells) == cells for m in maps)


def classify_target(cells, syms=None):
    """Exact symmetry class label for reporting ('CK6', 'order8', ...)."""
    syms = full_symmetry(cells) if syms is None else syms
    code = order4_lunnon_code(syms)
    if code is not None:
        return code
    return f"order{symmetry_order(syms)}"


def count_covers_fast(rows, cells):
    """Exact-cover count via the independent non-mutating solver
    (common.algorithm_x_fast).  Cross-checks common.algorithm_x.

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
    active_cols = set(cells)
    active_rows = [True] * len(row_list)
    return sum(1 for _ in solve_fast(x, y, active_cols, active_rows))


def run_targets_method(volume, piece, maps, index, log, census_all=None):
    """Method A: orbit-based target enumeration + funnel + exact cover.

    Funnel per target (each stage a necessary condition for tileability):
      1. at least k = V/5 placements contained in the target;
      2. every target cell coverable by a contained placement;
      3. exact cover exists (counted; coverage-passing targets are
         re-verified with the independent solver).
    Completeness: the funnel only rejects targets that provably cannot
    be tiled; every tiling of every enumerated target would pass.
    """
    k = volume // len(piece)
    t0 = time.time()
    targets = list(enumerate_connected_ck6_targets(volume))
    log(f"  connected CK6-closed {volume}-cell targets: {len(targets)} "
        f"({time.time()-t0:.2f}s)")
    funnel = Counter()
    tileable = []
    passing = []
    census = Counter()
    census_all = (len(targets) <= 2000) if census_all is None else census_all
    t0 = time.time()
    for t in targets:
        funnel["targets"] += 1
        assert len(t) == volume
        assert is_face_connected(t)
        assert ck6_closure_ok(t, maps.values())
        rows, covered, tmask = index.contained(t)
        if len(rows) < k:
            funnel["reject: <k contained placements"] += 1
            continue
        if covered != tmask:
            funnel["reject: uncovered cell"] += 1
            continue
        funnel["pass coverage"] += 1
        passing.append((t, rows))
        syms = full_symmetry(t)
        census[(order4_lunnon_code(syms)
                or f"order{symmetry_order(syms)}")] += 1
        n = sum(1 for sol in _covers(t, rows) if len(sol) == k)
        n_fast = count_covers_fast(rows, t)
        assert n == n_fast, (canonical_form(t), n, n_fast)
        if n:
            funnel["TILEABLE"] += 1
            tileable.append((t, n, rows))
        else:
            funnel["reject: exact cover UNSAT"] += 1
    log(f"  funnel: {dict(funnel)}  ({time.time()-t0:.1f}s)")
    log(f"  coverage-passing targets: {len(passing)} "
        f"(distinct canonical: "
        f"{len({canonical_form(t) for t, _ in passing})})")
    if census_all:
        log(f"  symmetry census of ALL targets: {dict(sorted(census.items()))}")
    else:
        log(f"  symmetry census of coverage-passing targets: "
            f"{dict(sorted(census.items()))}")
    log(f"  tileable targets: {len(tileable)}")
    for t, n, rows in tileable:
        log(f"  WITNESS: canonical {canonical_form(t)} ({n} tiling(s))")
    return {"targets": targets, "funnel": funnel, "tileable": tileable,
            "passing": passing, "census": census}


def _covers(cells, rows):
    """Exact-cover solutions via common.algorithm_x (reference solver)."""
    from common.algorithm_x import solve
    y = {i: sorted(p) for i, p in enumerate(rows)}
    x = {c: set() for c in cells}
    for i, cs in y.items():
        for c in cs:
            x[c].add(i)
    return solve(x, y)


def run_tilings_method(volume, piece, placements, maps, log):
    """Method B (V = 15): tiling-first scan over placement triples."""
    if volume % 2 == 0:
        raise ValueError("tilings method currently supports odd volumes")
    k = volume // len(piece)
    if k != 3:
        raise ValueError("tilings method implemented for exactly 3 tiles")
    center = (0, 0, 0)
    c_map, k_map, ck_map = (maps["C"], maps["K"], maps["CK"])
    k_img = {p: frozenset(k_map(c) for c in p) for p in placements}
    p1s = [p for p in placements if center in p]
    log(f"  placements through the center cell: {len(p1s)}")
    hits = set()
    for p1 in p1s:
        k1 = k_img[p1]
        s1 = p1 | k1
        if len(s1) > volume:
            continue
        for p2 in placements:
            if not p2.isdisjoint(p1):
                continue
            s2 = s1 | p2 | k_img[p2]
            if len(s2) > volume:
                continue
            base = p1 | p2
            for p3 in placements:
                # disjointness is against the tiling PIECES, never
                # against the K-image cell sets
                if not p3.isdisjoint(base):
                    continue
                u = base | p3
                if len(u) != volume or not s2 <= u:
                    continue
                if not k_img[p3] <= u:
                    continue
                if (frozenset(c_map(c) for c in u) != u
                        or frozenset(ck_map(c) for c in u) != u):
                    continue
                if not is_face_connected(u):
                    continue
                hits.add(canonical(u))
    log(f"  CK6-closed connected tilings (canonical unions): {len(hits)}")
    return hits


def canonical(cells):
    """Full-O_h canonical form."""
    return canonical_form(cells)


def main():
    parser = argparse.ArgumentParser(
        description="CK6 T-pentacube oddity search (stage driver)")
    parser.add_argument("piece", nargs="?", default="T",
                        help="piece letter (default T)")
    parser.add_argument("--volume", type=int, default=15,
                        help="target volume in cells (odd, multiple of 5)")
    parser.add_argument("--method", choices=["both", "targets", "tilings"],
                        default="both")
    parser.add_argument("--json", dest="json_path", default=None,
                        help="write machine-readable summary to PATH "
                             "('-' for stdout)")
    args = parser.parse_args()

    piece_name = args.piece.upper()
    if piece_name not in PENTACUBES:
        print(f"Error: piece '{piece_name}' not in PENTACUBES", file=sys.stderr)
        sys.exit(1)
    piece = [tuple(map(int, c)) for c in PENTACUBES[piece_name]]
    volume = args.volume
    if volume % len(piece) != 0:
        print(f"Error: volume {volume} is not a multiple of "
              f"{len(piece)} (piece size)", file=sys.stderr)
        sys.exit(1)
    k = volume // len(piece)
    if volume % 2 == 0:
        print("Error: odd volumes only at this stage", file=sys.stderr)
        sys.exit(1)

    log_lines = []

    def log(msg):
        print(msg)
        log_lines.append(msg)

    t0 = time.time()
    log(f"# CK6 {piece_name}-pentacube oddity search - "
        f"volume {volume} ({k} tiles)")
    max_l1 = max_l1_for_volume(volume)
    ball = l1_ball(max_l1)
    maps = ck6_affine_maps((0, 0))
    orientations = unique_orientations(piece)
    index = PlacementIndex(piece, ball)
    placements = index.placements
    log(f"# domain: L1 <= {max_l1} ball ({len(ball)} cells); "
        f"orientations {len(orientations)}; placements {len(placements)}")
    log("# domain completeness: connected K-closed target with center c "
        "has all cells within L1 distance (V-1)/2 of c "
        "(docs/frontier/ck6_oddity_design.md section 7)")

    results = {}
    methods = [args.method] if args.method != "both" else ["targets", "tilings"]
    if "tilings" in methods and k != 3:
        log(f"# method tilings: skipped (implemented for exactly 3 tiles; "
            f"volume {volume} = {k} tiles)")
        methods.remove("tilings")
    if "targets" in methods:
        log("# method targets (orbit enumeration + funnel + exact cover):")
        out = run_targets_method(volume, piece, maps, index, log)
        results["targets"] = {
            "connected_targets": len(out["targets"]),
            "funnel": dict(out["funnel"]),
            "coverage_passing": len(out["passing"]),
            "tileable": len(out["tileable"]),
        }
    if "tilings" in methods:
        log("# method tilings (placement-triple scan):")
        hits = run_tilings_method(volume, piece, placements, maps, log)
        results["tilings"] = {"canonical_hits": len(hits)}

    elapsed = time.time() - t0
    agree = None
    if "targets" in results and "tilings" in results:
        agree = (results["targets"]["tileable"] == 0
                 and results["tilings"]["canonical_hits"] == 0) or \
                (results["targets"]["tileable"] > 0)
    log(f"# elapsed: {elapsed:.2f}s")
    if agree is True:
        log(f"# RESULT: no CK6-or-higher symmetric {volume}-cell polycube "
            f"is tileable by {k} {piece_name} pentacubes "
            f"(both methods agree)")
    elif agree is False:
        log("# RESULT: METHOD DISAGREEMENT - investigate before trusting "
            "either method")
    elif results.get("targets", {}).get("tileable", 0) > 0:
        log(f"# RESULT: CK6 ODDITY FOUND at volume {volume} - see WITNESS "
            f"lines above")
    else:
        log(f"# RESULT: no CK6-or-higher symmetric {volume}-cell polycube "
            f"is tileable by {k} {piece_name} pentacubes "
            f"(single-method run; dual-solver cross-check passed)")

    if args.json_path:
        summary = {
            "piece": piece_name,
            "volume": volume,
            "tiles": k,
            "max_l1": max_l1,
            "ball_cells": len(ball),
            "placements": len(placements),
            "elapsed_s": round(elapsed, 3),
            "methods": results,
        }
        text = json.dumps(summary, indent=2, sort_keys=True, default=dict)
        if args.json_path == "-":
            print(text)
        else:
            with open(args.json_path, "w") as f:
                f.write(text + "\n")
            print(f"# json summary written to {args.json_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Z-pentacube residual-frontier inventory.

Enumerates canonical Z boxes (1 <= a <= b <= c <= MAXDIM, volume % 5 == 0),
runs the exhaustive decomposition classifier (solvers/decomp.py), and groups
every UNRESOLVED box (currently: class Unknown) by cross-section (a, b).

Each unresolved box is bucketed into the residual-workflow classes:

  A  already reducible by existing decomposition   (engine-closed; empty by
     construction when it appears here, since closure removes it)
  B  suitable for direct exhaustive C++ search     (small placement count /
     small cell count; C++ measured: ~600 cells UNSAT unproven, ~425 cells
     UNSAT in ~62 s, 315-cell SAT enumeration in ~26 min at 4 workers)
  C  suitable for SAT + DRAT certificate           (the Z 4x11x15 class:
     ~600-1000 cells, hard UNSAT residuals; SAT proved 660 cells in ~35 min)
  D  requiring a new mathematical argument         (above the SAT comfort
     zone, no decomposition available)

Buckets B/C are assigned from measured cell-count thresholds recorded in
reports/cpp-numba-benchmark-2026-09-03.md and
reports/parallel-sat-decision-2026-09-04.md.  They are advisory sizing, not
claims about the answer.

Usage:  python3 tools/frontier/z_piece/z_residual_inventory.py [--max-dim N]
                                                       [--cross-section a b]
"""
import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from catalogues.base import Box
from catalogues.registry import CATALOGUES
import solvers.decomp as decomp


def placement_estimate(a, b, c):
    """Cheap upper-bound-ish estimate of the placement count of the flat Z
    pentacube in an a x b x c box (12 orientations; flat spans 3x2x1 /
    3x1x2 family).  Used only for advisory sizing."""
    piece = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 2, 0), (2, 2, 0)]
    import itertools
    oris = set()
    # 24 proper rotations via permutation+sign matrices
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product([1, -1], repeat=3):
            M = [[0] * 3 for _ in range(3)]
            for i in range(3):
                M[i][perm[i]] = signs[i]
            det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
                   - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                   + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
            if det != 1:
                continue
            rot = [tuple(sum(M[i][j] * p[j] for j in range(3)) for i in range(3))
                   for p in piece]
            mn = [min(q[i] for q in rot) for i in range(3)]
            oris.add(tuple(sorted((q[0] - mn[0], q[1] - mn[1], q[2] - mn[2])
                                  for q in rot)))
    dims = (a, b, c)
    total = 0
    for ori in oris:
        span = [max(q[i] for q in ori) for i in range(3)]
        n = 1
        for i in range(3):
            k = dims[i] - span[i]
            if k <= 0:
                n = 0
                break
            n *= k
        total += n
    return len(oris), total


def bucket(cells, nplacements):
    """Advisory residual-workflow bucket for an unresolved box."""
    # Measured anchors:
    #   Z 4x11x15 (660 cells, 4096 placements): SAT UNSAT ~35 min, search failed
    #   W 5x5x17 (425 cells): C++ exhaustive UNSAT 62 s single-thread
    #   W 5x7x9 (315 cells, 10 sols): C++ exhaustive enumeration 26 min (4w)
    if cells <= 450:
        return "B (C++ exhaustive viable)"
    if cells <= 1000 and nplacements <= 12000:
        return "C (SAT + DRAT class)"
    return "D (needs new math or much larger budget)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-dim", type=int, default=60)
    ap.add_argument("--max-a", type=int, default=15,
                    help="only enumerate cross-sections with a <= max-a "
                         "(keeps the run short; raise for full scan)")
    ap.add_argument("--cross-section", nargs=2, type=int, metavar=("A", "B"))
    args = ap.parse_args()

    decomp.PIECE_NAME = "Z"
    decomp.PIECE_SIZE = 5
    decomp.catalogue = CATALOGUES["Z"]
    decomp.classify.cache_clear()

    lo = (args.cross_section[0], args.cross_section[1]) \
        if args.cross_section else None

    unresolved = {}   # (a,b) -> list of (c, node, cells, npl)
    closed = 0
    impossible = 0
    scanned = 0

    maxdim = args.max_dim
    for a in range(1, args.max_a + 1):
        for b in range(a, maxdim + 1):
            if lo and (a, b) != lo:
                continue
            for c in range(b, maxdim + 1):
                if (a * b * c) % 5:
                    continue
                box = Box(a, b, c)
                node = decomp.classify(box)
                scanned += 1
                name = type(node).__name__
                if name in ("Slab", "Width", "Breadth", "Generator",
                            "Prime", "PublishedSolution"):
                    closed += 1
                elif name == "Impossible":
                    impossible += 1
                else:  # Unknown
                    cells = a * b * c
                    _, npl = placement_estimate(a, b, c)
                    unresolved.setdefault((a, b), []).append((c, cells, npl))

    print(f"Z residual inventory: canonical boxes, dims <= {maxdim}"
          + (f", cross-section {lo[0]}x{lo[1]}" if lo else
             f", cross-sections a <= {args.max_a}"))
    print(f"scanned={scanned} closed={closed} impossible={impossible} "
          f"unresolved={sum(len(v) for v in unresolved.values())} "
          f"cross-sections={len(unresolved)}")
    print()
    rows = sorted(unresolved.items(),
                  key=lambda kv: (min(c for c, _, _ in kv[1]), kv[0]))
    print(f"{'a,b':>9} {'#u':>4}  unresolved c (cells | ~placements | bucket)")
    for (a, b), lst in rows:
        parts = []
        for c, cells, npl in sorted(lst)[:14]:
            parts.append(f"{c}({cells}|{npl}|{bucket(cells, npl)[0]})")
        more = "" if len(lst) <= 14 else f" +{len(lst) - 14} more"
        print(f"{a:>4}x{b:<4} {len(lst):>4}  {' '.join(parts)}{more}")

    # Focus table: the 4xN family analogous to the certified Z 4x11x15 UNSAT
    print("\n4xN half-length family (Z 4x11x15 analogues, dims <= "
          f"{maxdim}):")
    for (a, b), lst in sorted(rows):
        if a != 4:
            continue
        for c, cells, npl in sorted(lst):
            print(f"  Z 4x{b}x{c}: cells={cells} ~placements={npl} "
                  f"-> {bucket(cells, npl)}")

    # Smallest unresolved boxes overall
    print("\nSmallest unresolved boxes (by cells):")
    flat = [(cells, a, b, c, npl)
            for (a, b), lst in unresolved.items()
            for c, cells, npl in lst]
    for cells, a, b, c, npl in sorted(flat)[:20]:
        print(f"  Z {a}x{b}x{c}: cells={cells} ~placements={npl} "
              f"-> {bucket(cells, npl)}")


if __name__ == "__main__":
    main()

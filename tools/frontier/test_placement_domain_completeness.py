#!/usr/bin/env python3
"""
Regression test: placement-domain completeness for pieces whose
orientations do not contain their component-wise minimum corner
(18/24 orientations of repo-M, 6/24 of repo-P).

Background (CK6 sharding-repair audit, 2026-09-10): the pre-hardening
placements_in_region anchored each orientation only at region cells.
For an orientation o whose per-axis minimum corner (0,0,0) is NOT a
cell of o, a placement p = a + o has its anchor a outside p; if the
region is non-box (e.g. an L1 ball) or simply does not contain a, the
old loop never generated p even though p subset of region.  The
hardened implementation computes the exact anchor set
    {a : a + o subset of region} = intersection over c in o of (region - c).

Tests (repo-M and repo-P):
  1. region = a single placement p whose orientation lacks (0,0,0):
     p itself must be reported (old code missed it);
  2. region = small L1 ball: placements_in_region equals the brute-force
     enumeration over an extended box (complete full-domain reference);
  3. the hardened implementation never loses placements relative to the
     old one (superset on a mixed region).
"""
import sys

import numpy as np

sys.path.insert(0, "/home/philip/Work/fitpolycubes")

from common.oddity import placements_in_region, unique_orientations
from common.registry import PENTACUBES

FAILURES = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}"
          + (f" -- {detail}" if detail else ""))
    if not cond:
        FAILURES.append(name)


def brute_force_placements(piece, region):
    """Complete reference: anchor over an extended box, filter to region."""
    region = set(tuple(int(v) for v in c) for c in region)
    arr = np.asarray(sorted(region), dtype=int)
    mn, mx = arr.min(axis=0), arr.max(axis=0)
    span = np.asarray([max(c[i] for c in piece) for i in range(3)])
    out = set()
    for o in unique_orientations(piece):
        o = sorted(o)
        for bx in range(int(mn[0]) - int(span[0]) - 1, int(mx[0]) + 1):
            for by in range(int(mn[1]) - int(span[1]) - 1, int(mx[1]) + 1):
                for bz in range(int(mn[2]) - int(span[2]) - 1,
                                int(mx[2]) + 1):
                    p = frozenset((bx + c[0], by + c[1], bz + c[2])
                                  for c in o)
                    if p <= region:
                        out.add(p)
    return out


def l1_ball(radius):
    r = int(radius)
    return [(x, y, z) for x in range(-r, r + 1) for y in range(-r, r + 1)
            for z in range(-r, r + 1) if abs(x) + abs(y) + abs(z) <= r]


def main():
    print("== placement-domain completeness regression (M, P) ==")
    for letter in ("M", "P"):
        piece = [tuple(int(v) for v in c) for c in PENTACUBES[letter]]
        oris = unique_orientations(piece)
        n_bad = sum(1 for o in oris if (0, 0, 0) not in o)
        check(f"{letter}: has min-corner-less orientations "
              f"({n_bad}/{len(oris)})", n_bad > 0)

        # 1. region = single placement with min-corner-less orientation
        o_bad = next(o for o in oris if (0, 0, 0) not in o)
        anchor = (0, 0, 0)  # component-wise min corner, not a cell of o
        p = frozenset((anchor[0] + c[0], anchor[1] + c[1],
                       anchor[2] + c[2]) for c in o_bad)
        got = set(placements_in_region(piece, p))
        check(f"{letter}: region = one placement p (anchor outside p): "
              f"p is reported", p in got,
              f"|placements_in_region(p)|={len(got)}")
        check(f"{letter}: region = p: exactly one placement", got == {p})

        # 2. small ball vs brute force
        for R in (2, 3):
            region = l1_ball(R)
            got = set(placements_in_region(piece, region))
            ref = brute_force_placements(piece, region)
            check(f"{letter}: ball(R={R}) == brute force "
                  f"({len(got)} placements)", got == ref)

    # 3. superset property on a mixed region (ball plus an external cell)
    piece = [tuple(int(v) for v in c) for c in PENTACUBES["M"]]
    region = set(l1_ball(2)) | {(3, 0, 0), (3, 1, 0)}
    got = set(placements_in_region(piece, region))
    ref = brute_force_placements(piece, region)
    check("mixed region: hardened == brute force", got == ref,
          f"|got|={len(got)} |ref|={len(ref)}")

    print("\n" + ("ALL CHECKS PASSED" if not FAILURES
                  else f"FAILURES: {FAILURES}"))
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())

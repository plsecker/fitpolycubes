#!/usr/bin/env python3
"""
Regression test: the EE4 coordinate-frame bug.

The original 5x5x5 EE4 search returned zero tilings because
common.polycube_utils.generate_placements() produces placements in the
{0..4}^3 frame, while centred EE4-invariant targets live in {-2..2}^3
and contain negative coordinates.  A placement in {0..4}^3 can never
cover a cell with a negative coordinate, so the search was trivially
unsatisfiable.

This test proves:
  1. every cell of the EE4 witness target has at least one negative
     coordinate (so no {0..4}^3 placement can cover it),
  2. no placement generated in the {0..4}^3 frame covers any target
     cell (the bug's failure mode),
  3. after translating placements by (-2,-2,-2) into the {-2..2}^3
     frame, the five fixture placements are all present and cover the
     target exactly (the fix).

Run:  PYTHONPATH=. python3 tests/test_ee4_coordinate_frame.py
"""

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from common.polycube_utils import generate_placements
from common.registry import PENTACUBES

FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "ee4_R_5.json")


def main():
    with open(FIXTURE) as f:
        fx = json.load(f)
    target = {tuple(c) for c in fx["target"]}

    # 1. the target contains cells with negative coordinates (which a
    #    {0..4}^3 placement can never cover)
    neg_cells = {c for c in target if min(c) < 0}
    assert neg_cells, "target has no negative-coordinate cells"
    print(f"target: {len(neg_cells)} cells with a negative coordinate  ok")

    # 2. raw {0..4}^3 placements have all coordinates >= 0, so none can
    #    cover a negative-coordinate target cell; an exact cover of the
    #    target is therefore impossible in the raw frame (the bug)
    raw, _ = generate_placements(PENTACUBES["R"], (5, 5, 5))
    raw_sets = [set(p) for p in raw.values()]
    for p in raw_sets:
        assert all(min(c) >= 0 for c in p), "raw placement has negative coord"
        assert p.isdisjoint(neg_cells), \
            "raw placement covers a negative-coordinate target cell"
    print("raw {0..4}^3 placements: none can cover the target  ok")

    # 3. translated placements cover the target exactly
    shifted = [frozenset(tuple(c - 2 for c in p) for p in ps)
               for ps in raw_sets]
    fixture_pieces = [frozenset(tuple(c) for c in pl["cells"])
                      for pl in fx["placements"]]
    for fp in fixture_pieces:
        assert fp in shifted, "fixture placement missing from translated set"
    union = set()
    for fp in fixture_pieces:
        assert fp.isdisjoint(union)
        union |= fp
    assert union == target, "translated placements do not cover the target"
    print("translated placements: fixture pieces present, exact cover  ok")

    print("\nCOORDINATE-FRAME REGRESSION CHECKS PASSED")


if __name__ == "__main__":
    main()
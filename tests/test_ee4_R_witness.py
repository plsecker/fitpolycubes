#!/usr/bin/env python3
"""
Regression test: the EE4 5-R witness (tests/fixtures/ee4_R_5.json).

Proves, from scratch (no search code):
  1. the target has exactly 25 cells and is face-connected,
  2. the target is invariant under the EE4 group {I, MX, MY, RZ} and has
     no larger symmetry (order 4, kinds c2_ortho/mirror_ortho/
     mirror_ortho),
  3. the target lies inside the 5x5x5 box {-2..2}^3 with the documented
     bounding box,
  4. each of the five placements is a proper rotation of the R pentacube
     (RM index 0..23, det +1) plus an integer translation,
  5. the five placements are pairwise disjoint and cover exactly the
     target (exact cover),
  6. the stored canonical form is stable and matches
     common.symmetry.normalize.

Run:  PYTHONPATH=. python3 tests/test_ee4_R_witness.py
"""

import json
import os
import sys

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from common.rotmatrix import RM
from common.registry import PENTACUBES
from common.symmetry import normalize, full_symmetry, element_kind, \
    order4_lunnon_code

FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "ee4_R_5.json")


def face_connected(cells):
    cells = set(cells)
    if not cells:
        return True
    start = next(iter(cells))
    stack, seen = [start], {start}
    while stack:
        x, y, z = stack.pop()
        for nb in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                   (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
            if nb in cells and nb not in seen:
                seen.add(nb)
                stack.append(nb)
    return len(seen) == len(cells)


def main():
    with open(FIXTURE) as f:
        fx = json.load(f)

    assert fx["piece"] == "R"
    assert fx["symmetry_class"] == "EE4"
    R = PENTACUBES["R"]
    target = {tuple(c) for c in fx["target"]}

    # 1. size and connectivity
    assert len(target) == 25, f"target has {len(target)} cells"
    assert face_connected(target), "target not face-connected"
    print("target: 25 cells, face-connected  ok")

    # 2. EE4 invariance, no larger symmetry
    syms = full_symmetry(target)
    kinds = sorted(element_kind(m) for m in syms if element_kind(m) != "identity")
    assert len(syms) == 4, f"symmetry order {len(syms)} != 4"
    assert kinds == ["c2_ortho", "mirror_ortho", "mirror_ortho"], kinds
    assert order4_lunnon_code(syms) == "EE4"
    print("target: exact EE4 symmetry (order 4)  ok")

    # 3. box containment and bbox
    box = fx["box"]
    for c in target:
        for j in range(3):
            assert box["min"][j] <= c[j] <= box["max"][j], f"{c} out of box"
    bbox = fx["bbox"]
    for j, ax in enumerate("xyz"):
        assert min(c[j] for c in target) == bbox[ax][0]
        assert max(c[j] for c in target) == bbox[ax][1]
    print(f"target: inside box, bbox {bbox}  ok")

    # 4. placements are proper rotations + translations
    placements = []
    for i, pl in enumerate(fx["placements"]):
        k = pl["rotation_index"]
        assert 0 <= k < 24, f"bad RM index {k}"
        assert int(round(np.linalg.det(RM[k]))) == 1, f"RM[{k}] not proper"
        rot = {tuple(int(v) for v in RM[k] @ np.array(r)) for r in R}
        t = tuple(pl["translation"])
        shifted = {tuple(c[j] + t[j] for j in range(3)) for c in rot}
        assert shifted == {tuple(c) for c in pl["cells"]}, \
            f"placement {i} cells mismatch"
        assert pl["rotation_matrix"] == [list(map(int, row)) for row in RM[k]]
        placements.append(shifted)
    print("placements: 5 proper rotations of R + translations  ok")

    # 5. disjointness and exact cover
    union = set()
    for i, p in enumerate(placements):
        assert len(p) == 5
        assert p.isdisjoint(union), f"placement {i} overlaps"
        union |= p
    assert union == target, "placements do not exactly cover the target"
    print("placements: pairwise disjoint, exact cover of target  ok")

    # 6. canonical form stability
    canon = normalize(target)
    assert [list(c) for c in canon] == fx["target_canonical"]
    # canonical form must be stable across re-runs (deterministic)
    assert normalize(target) == canon
    print("canonical form: stable and matches fixture  ok")

    print("\nALL EE4 WITNESS CHECKS PASSED")


if __name__ == "__main__":
    main()
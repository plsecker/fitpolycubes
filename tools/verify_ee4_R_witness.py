#!/usr/bin/env python3
"""
Independently verify tests/fixtures/ee4_R_5.json.

Checks, from scratch (no search code):
  1. every placement is a proper rotation of the R pentacube plus an
     integer translation (rotation_index in 0..23, RM from
     common.rotmatrix),
  2. the five placements are pairwise disjoint and cover exactly the
     declared target (25 cells),
  3. the target is invariant under the EE4 group {I, MX, MY, RZ}
     (mirrors x=0 and y=0, product c2 about z) and has no larger
     symmetry,
  4. the target is face-connected,
  5. the target lies inside the 5x5x5 box {-2..2}^3,
  6. the stored canonical form matches common.symmetry.normalize.

Usage: python3 tools/verify_ee4_R_witness.py [path-to-fixture]
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
from common.symmetry import normalize, full_symmetry, element_kind

DEFAULT_FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "ee4_R_5.json")


def face_connected(cells):
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


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FIXTURE
    with open(path) as f:
        fx = json.load(f)

    assert fx["piece"] == "R"
    assert fx["symmetry_class"] == "EE4"
    R = PENTACUBES["R"]
    R_set = {tuple(map(int, r)) for r in R}

    # 1. placements are proper rotations of R
    placements = []
    for i, pl in enumerate(fx["placements"]):
        k = pl["rotation_index"]
        assert 0 <= k < 24, f"placement {i}: bad rotation index {k}"
        rot = {tuple(int(v) for v in RM[k] @ np.array(r)) for r in R}
        t = tuple(pl["translation"])
        shifted = {tuple(c[j] + t[j] for j in range(3)) for c in rot}
        assert shifted == set(tuple(c) for c in pl["cells"]), \
            f"placement {i}: cells do not match RM[{k}] + t"
        assert pl["rotation_matrix"] == [list(map(int, row)) for row in RM[k]], \
            f"placement {i}: stored rotation matrix mismatch"
        placements.append(shifted)
        print(f"placement {i}: RM[{k}] + t={t}  ok")

    # 2. disjointness and coverage
    union = set()
    for i, p in enumerate(placements):
        assert len(p) == 5, f"placement {i}: not 5 cells"
        assert p.isdisjoint(union), f"placement {i}: overlaps earlier placement"
        union |= p
    assert len(union) == 25, f"union has {len(union)} cells, expected 25"
    target = {tuple(c) for c in fx["target"]}
    assert union == target, "union of placements != declared target"
    print("placements pairwise disjoint; union == target (25 cells)  ok")

    # 3. EE4 invariance and no larger symmetry
    syms = full_symmetry(target)
    kinds = sorted(element_kind(m) for m in syms if element_kind(m) != "identity")
    assert len(syms) == 4, f"target symmetry order {len(syms)}, expected 4"
    assert kinds == ["c2_ortho", "mirror_ortho", "mirror_ortho"], kinds
    print(f"target symmetry: order 4, kinds {kinds}  ok")

    # 4. connectivity
    assert face_connected(target), "target is not face-connected"
    print("target face-connected  ok")

    # 5. box containment
    box = fx["box"]
    for c in target:
        for j in range(3):
            assert box["min"][j] <= c[j] <= box["max"][j], f"cell {c} out of box"
    print(f"target inside box {box['min']}..{box['max']}  ok")

    # 6. canonical form
    canon = normalize(target)
    assert [list(c) for c in canon] == fx["target_canonical"], \
        "canonical form mismatch"
    print("canonical form matches  ok")

    print("\nALL CHECKS PASSED")
    print(f"target bbox: {fx['bbox']}")
    print(f"search context: {fx['search']}")


if __name__ == "__main__":
    main()
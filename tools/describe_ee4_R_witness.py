#!/usr/bin/env python3
"""
Deterministic human-readable description of the EE4 5-R witness.

Prints, for each of the five placements:
    piece_id, RM index, rotation matrix, translation, the five placed
    cells, and the normalized orientation cells (the five cells of the
    rotated piece shifted so their minimum coordinate is (0,0,0)),
and for the union target:
    raw coordinates, layer-by-layer z slices, canonical form.

Everything is derived from tests/fixtures/ee4_R_5.json plus
common.rotmatrix.RM and common.registry.PENTACUBES, so the output is
fully reproducible and needs no search code.

Usage: python3 tools/describe_ee4_R_witness.py [path-to-fixture]
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
from common.symmetry import normalize

DEFAULT_FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "ee4_R_5.json")


def fmt_cells(cells):
    return " ".join(f"({x},{y},{z})" for x, y, z in sorted(cells))


def fmt_matrix(m):
    return "[" + " ".join(
        "[" + ",".join(str(int(v)) for v in row) + "]" for row in m) + "]"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FIXTURE
    with open(path) as f:
        fx = json.load(f)

    R = PENTACUBES[fx["piece"]]
    print(f"piece: {fx['piece']}  symmetry class: {fx['symmetry_class']}")
    print(f"symmetry: {fx['symmetry_description']}")
    print(f"box: {fx['box']['min']}..{fx['box']['max']}")
    print(f"search: {fx['search']['tilings_total']} tilings, "
          f"{fx['search']['canonical_targets']} canonical targets, "
          f"{fx['search']['nodes']} nodes, {fx['search']['seconds']}s")
    print()

    print("=" * 78)
    print("PLACEMENTS")
    print("=" * 78)
    for i, pl in enumerate(fx["placements"]):
        k = pl["rotation_index"]
        t = tuple(pl["translation"])
        rot = {tuple(int(v) for v in RM[k] @ np.array(r)) for r in R}
        mn = tuple(min(c[j] for c in rot) for j in range(3))
        norm = tuple(sorted(tuple(c[j] - mn[j] for j in range(3)) for c in rot))
        print(f"\nplacement {i}:  piece_id R{i}  RM[{k}]  t={t}")
        print(f"  rotation matrix: {fmt_matrix(pl['rotation_matrix'])}")
        print(f"  placed cells   : {fmt_cells(pl['cells'])}")
        print(f"  normalized ori : {fmt_cells(norm)}")
        # cross-check: the normalized orientation must be the rotated R
        # cells shifted to the origin, and the placed cells must be that
        # orientation translated by t
        assert norm == tuple(sorted(
            tuple(c[j] - mn[j] for j in range(3)) for c in rot)), \
            "orientation recomputation mismatch"
        # placed cells = rotated cells + t = normalized orientation + (t + mn)
        shift = tuple(t[j] + mn[j] for j in range(3))
        assert {tuple(c[j] + shift[j] for j in range(3)) for c in norm} == \
            {tuple(c) for c in pl["cells"]}, "translation mismatch"

    print()
    print("=" * 78)
    print("UNION TARGET")
    print("=" * 78)
    target = {tuple(c) for c in fx["target"]}
    print(f"\nraw coordinates ({len(target)} cells):")
    print("  " + fmt_cells(target))
    print(f"\nbbox: {fx['bbox']}")

    print("\nlayer-by-layer z slices (z from top to bottom):")
    for z in sorted({c[2] for c in target}, reverse=True):
        layer = sorted(c for c in target if c[2] == z)
        print(f"  z={z}: {fmt_cells(layer)}")

    canon = normalize(target)
    print(f"\ncanonical form ({len(canon)} cells):")
    print("  " + fmt_cells(canon))
    assert [list(c) for c in canon] == fx["target_canonical"], \
        "canonical form mismatch with fixture"


if __name__ == "__main__":
    main()
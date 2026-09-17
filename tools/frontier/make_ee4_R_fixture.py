#!/usr/bin/env python3
"""
Generate tests/fixtures/ee4_R_5.json: a machine-verifiable witness of a
5-R pentacube tiling of a 25-cell EE4-invariant connected target.

The witness is produced by the exhaustive class comparison in
tools/order4_R_class_comparison.py (EE4 = mirrors x=0 and y=0, product
c2 about the z-axis).  Canonical target #1, first tiling.

Usage: python3 tools/frontier/make_ee4_R_fixture.py
"""

import json
import os
import sys

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
TOOLS = os.path.join(REPO_ROOT, "tools")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import order4_R_class_comparison as cmp
from common.rotmatrix import RM
from common.registry import PENTACUBES
from common.symmetry import normalize

NAME = "EE4"
TARGET_INDEX = 0  # first canonical target


def placement_rotation(p):
    """Find (k, t) such that p == {RM[k] @ r + t : r in R}."""
    R = PENTACUBES["R"]
    for k in range(24):
        rot = {tuple(int(v) for v in RM[k] @ np.array(r)) for r in R}
        mn_rot = tuple(min(c[i] for c in rot) for i in range(3))
        mn_p = tuple(min(c[i] for c in p) for i in range(3))
        t = tuple(mn_p[i] - mn_rot[i] for i in range(3))
        shifted = {tuple(c[i] + t[i] for i in range(3)) for c in rot}
        if shifted == set(p):
            return k, t
    raise AssertionError("placement is not a proper rotation of R")


def main():
    mats = cmp.CLASS_GROUPS[NAME]
    placements = cmp.build_placements()
    orbits = cmp.orbits_of(cmp.BOX_CELLS, mats)
    orbit_of = {}
    for idx, o in enumerate(orbits):
        for c in o:
            orbit_of[c] = idx
    pclosure = []
    for p in placements:
        cells = set()
        for c in p:
            cells |= orbits[orbit_of[c]]
        pclosure.append(frozenset(cells))

    results, nodes, dt = cmp.search_class(placements, pclosure, max_tilings=2000)
    assert len(results) > 0, "no EE4 tilings found"

    by_target = {}
    for target, chosen in results:
        by_target.setdefault(normalize(target), []).append((target, chosen))
    canon_targets = sorted(by_target)
    canon = canon_targets[TARGET_INDEX]
    target, chosen = by_target[canon][0]

    placements_out = []
    for i in chosen:
        k, t = placement_rotation(placements[i])
        placements_out.append({
            "rotation_index": k,
            "rotation_matrix": [list(map(int, row)) for row in RM[k]],
            "translation": list(t),
            "cells": sorted(placements[i]),
        })

    xs = [c[0] for c in target]
    ys = [c[1] for c in target]
    zs = [c[2] for c in target]

    fixture = {
        "piece": "R",
        "symmetry_class": NAME,
        "symmetry_description": "dual orthogonal mirror symmetry: "
                                "mirrors x=0 and y=0, product c2 about z-axis",
        "generators": {
            "MX": {"matrix": [[-1, 0, 0], [0, 1, 0], [0, 0, 1]], "plane": "x=0"},
            "MY": {"matrix": [[1, 0, 0], [0, -1, 0], [0, 0, 1]], "plane": "y=0"},
        },
        "product": {
            "RZ": {"matrix": [[-1, 0, 0], [0, -1, 0], [0, 0, 1]],
                   "kind": "c2_ortho about z-axis"},
        },
        "box": {"min": [-2, -2, -2], "max": [2, 2, 2]},
        "orbit_sizes": {"1": 5, "2": 20, "4": 20},
        "target": sorted(target),
        "target_canonical": list(canon),
        "bbox": {"x": [min(xs), max(xs)], "y": [min(ys), max(ys)],
                 "z": [min(zs), max(zs)]},
        "placements": placements_out,
        "search": {"tilings_total": len(results),
                   "canonical_targets": len(by_target),
                   "nodes": nodes,
                   "seconds": round(dt, 2)},
    }

    out_dir = os.path.join(REPO_ROOT, "tests", "fixtures")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ee4_R_5.json")
    with open(out_path, "w") as f:
        json.dump(fixture, f, indent=2)
    print(f"wrote {out_path}")
    print(f"EE4: {len(results)} tilings, {len(by_target)} canonical targets, "
          f"{nodes} nodes in {dt:.1f}s")


if __name__ == "__main__":
    main()
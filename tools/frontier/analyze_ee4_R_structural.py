#!/usr/bin/env python3
"""
Structural comparison of the four canonical EE4 5-R targets (Part E/F/G
of the EE4 finishing pass).

For each canonical EE4 target:
  - 25-cell coordinates, bbox, layer counts
  - exact symmetry group (order, element kinds, Lunnon code) and the
    affine symmetries (M, t)
  - all 5-R tilings, each with per-piece RM index / translation /
    normalized orientation
  - per-tiling structural signatures:
      * orientation multiset (normalized orientation shapes)
      * piece adjacency graph (face-sharing)
      * contact counts between piece pairs
      * boundary-touch pattern (which pieces touch the box faces)
      * per-piece cells on the symmetry-fixed planes x=0, y=0, z=0
  - equivalence classes of tilings under target affine symmetries
    (piece relabelling is implicit: orbits are sets of piece cell-sets)

Also checks cross-target equivalence under the full O_h group (targets
are distinct canonical forms, so none should be equivalent) and prints a
compact signature table for each target.

Usage: python3 tools/frontier/analyze_ee4_R_structural.py [out-json]
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
from common.symmetry import (normalize, full_symmetry, element_kind,
                             order4_lunnon_code, affine_symmetries,
                             OH_MATRICES, PROPER_KEYS)

DEFAULT_OUT = os.path.join(REPO_ROOT, "data", "ee4_R_5",
                           "structural_comparison.json")


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


def norm_orientation(p):
    """Normalized orientation cells of a placement (min at origin)."""
    k, t = placement_rotation(p)
    R = PENTACUBES["R"]
    rot = {tuple(int(v) for v in RM[k] @ np.array(r)) for r in R}
    mn = tuple(min(c[j] for c in rot) for j in range(3))
    return tuple(sorted(tuple(c[j] - mn[j] for j in range(3)) for c in rot))


def face_adjacency(pieces):
    """(adjacency graph, contact counts) for a list of piece cell-sets."""
    n = len(pieces)
    adj = [set() for _ in range(n)]
    contacts = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            cnt = 0
            for c in pieces[i]:
                x, y, z = c
                for nb in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                           (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                    if nb in pieces[j]:
                        cnt += 1
            if cnt:
                adj[i].add(j)
                adj[j].add(i)
                contacts[i][j] = contacts[j][i] = cnt
    return adj, contacts


def boundary_touch(pieces):
    """Which pieces touch each box face (x=+-2, y=+-2, z=+-2)."""
    faces = ["x-", "x+", "y-", "y+", "z-", "z+"]
    out = {f: [] for f in faces}
    for i, p in enumerate(pieces):
        for c in p:
            x, y, z = c
            if x == -2:
                out["x-"].append(i)
            if x == 2:
                out["x+"].append(i)
            if y == -2:
                out["y-"].append(i)
            if y == 2:
                out["y+"].append(i)
            if z == -2:
                out["z-"].append(i)
            if z == 2:
                out["z+"].append(i)
    return {f: sorted(set(v)) for f, v in out.items()}


def fixed_plane_counts(pieces):
    """Per-piece counts of cells on x=0, y=0, z=0."""
    return [[sum(1 for c in p if c[0] == 0),
             sum(1 for c in p if c[1] == 0),
             sum(1 for c in p if c[2] == 0)] for p in pieces]


def tiling_signature(pieces):
    """Structural signature of a tiling (piece order canonicalized)."""
    adj, contacts = face_adjacency(pieces)
    # canonicalize piece order by sorted normalized orientation
    order = sorted(range(len(pieces)),
                   key=lambda i: (norm_orientation(pieces[i]),
                                  tuple(sorted(pieces[i]))))
    ori = [norm_orientation(pieces[i]) for i in order]
    adj_c = sorted(tuple(sorted(order.index(j) for j in adj[i]))
                   for i in order)
    contacts_c = sorted(tuple(sorted((order.index(i), order.index(j),
                                      contacts[i][j])
                                     for j in adj[i]))
                        for i in order)
    bt = boundary_touch(pieces)
    bt_c = {f: sorted(order.index(i) for i in v) for f, v in bt.items()}
    fp = [fixed_plane_counts(pieces)[i] for i in order]
    return {
        "orientations": [list(o) for o in ori],
        "adjacency": adj_c,
        "contacts": contacts_c,
        "boundary_touch": bt_c,
        "fixed_plane_counts": fp,
    }


def apply_affine(pieces, m, t):
    """Apply (M, t) to each piece (elementwise: M*v + t)."""
    t = np.asarray(t, dtype=int)
    return [frozenset(tuple(int(v) for v in (m @ np.array(c) + t))
                      for c in p) for p in pieces]


def tiling_key(pieces):
    """Sortable canonical key for a tiling (set of piece cell-sets)."""
    return tuple(sorted(tuple(sorted(p)) for p in pieces))


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT

    mats = cmp.CLASS_GROUPS["EE4"]
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

    results, nodes, dt = cmp.search_class(placements, pclosure,
                                          max_tilings=2000)
    by_target = {}
    for target, chosen in results:
        by_target.setdefault(normalize(target), []).append((target, chosen))

    # cross-target equivalence under O_h (proper + reflections)
    canon_list = sorted(by_target)
    cross = {}
    for a in range(len(canon_list)):
        for b in range(a + 1, len(canon_list)):
            ta = set(canon_list[a])
            tb = set(canon_list[b])
            equiv = False
            for m in OH_MATRICES:
                img = {tuple(int(v) for v in m @ np.array(c)) for c in ta}
                mn_img = tuple(min(c[i] for c in img) for i in range(3))
                mn_tb = tuple(min(c[i] for c in tb) for i in range(3))
                t = tuple(mn_tb[i] - mn_img[i] for i in range(3))
                if {tuple(c[i] + t[i] for i in range(3)) for c in img} == tb:
                    equiv = True
                    break
            cross[f"{a + 1}-{b + 1}"] = equiv

    targets_out = []
    for k, (canon, lst) in enumerate(sorted(by_target.items())):
        target = set(lst[0][0])
        syms = full_symmetry(target)
        kinds = sorted(element_kind(m) for m in syms
                       if element_kind(m) != "identity")
        aff = affine_symmetries(target)
        xs = [c[0] for c in target]
        ys = [c[1] for c in target]
        zs = [c[2] for c in target]

        tilings = []
        for target_cells, chosen in lst:
            pieces = [placements[i] for i in chosen]
            ori_info = []
            for p in pieces:
                kk, tt = placement_rotation(p)
                ori_info.append({"rm_index": kk, "translation": list(tt),
                                 "norm": [list(c) for c in
                                          norm_orientation(p)]})
            tilings.append({
                "pieces": [sorted(p) for p in pieces],
                "orientation_info": ori_info,
                "signature": tiling_signature(pieces),
            })

        # equivalence classes under target affine symmetries
        seen = {}
        for target_cells, chosen in lst:
            pieces = [placements[i] for i in chosen]
            orbit_keys = set()
            for m, t in aff:
                orbit_keys.add(tiling_key(apply_affine(pieces, m, t)))
            rep = min(orbit_keys)
            seen.setdefault(rep, []).append(tiling_key(pieces))
        classes = sorted(seen)

        targets_out.append({
            "target_index": k + 1,
            "cells": sorted(target),
            "bbox": {"x": [min(xs), max(xs)], "y": [min(ys), max(ys)],
                     "z": [min(zs), max(zs)]},
            "layer_counts": {
                "z": {str(z): sum(1 for c in target if c[2] == z)
                      for z in sorted({c[2] for c in target}, reverse=True)},
                "x": {str(x): sum(1 for c in target if c[0] == x)
                      for x in sorted({c[0] for c in target})},
                "y": {str(y): sum(1 for c in target if c[1] == y)
                      for y in sorted({c[1] for c in target})},
            },
            "symmetry": {
                "order": len(syms),
                "kinds": kinds,
                "lunnon_code": order4_lunnon_code(syms),
                "affine_count": len(aff),
            },
            "tilings": tilings,
            "tiling_classes_under_symmetry": len(classes),
        })

    report = {
        "piece": "R",
        "symmetry_class": "EE4",
        "search": {"tilings_total": len(results),
                   "canonical_targets": len(by_target),
                   "nodes": nodes, "seconds": round(dt, 2)},
        "cross_target_oh_equivalence": cross,
        "targets": targets_out,
    }

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    # ---- human-readable summary ----
    print(f"EE4: {len(results)} tilings, {len(by_target)} canonical "
          f"targets ({nodes} nodes, {dt:.1f}s)")
    print(f"cross-target O_h equivalence: {cross}")
    for t in targets_out:
        print(f"\ntarget {t['target_index']}: bbox {t['bbox']}")
        print(f"  z-layer counts: {t['layer_counts']['z']}")
        print(f"  x-layer counts: {t['layer_counts']['x']}")
        print(f"  y-layer counts: {t['layer_counts']['y']}")
        print(f"  symmetry: order {t['symmetry']['order']}, "
              f"kinds {t['symmetry']['kinds']}, "
              f"code {t['symmetry']['lunnon_code']}, "
              f"affine syms {t['symmetry']['affine_count']}")
        print(f"  tilings: {len(t['tilings'])}, "
              f"classes under target symmetry: "
              f"{t['tiling_classes_under_symmetry']}")
        for ti, tl in enumerate(t['tilings']):
            sig = tl['signature']
            ori = [o['rm_index'] for o in tl['orientation_info']]
            print(f"    tiling {ti}: RM indices {ori}")
            print(f"      adjacency: {sig['adjacency']}")
            print(f"      contacts : {sig['contacts']}")
            print(f"      boundary : {sig['boundary_touch']}")
            print(f"      fixed-pl : {sig['fixed_plane_counts']}")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
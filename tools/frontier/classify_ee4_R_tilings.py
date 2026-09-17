#!/usr/bin/env python3
"""
Complete classification of all 5-R EE4 tilings (5x5x5 box {-2..2}^3).

This is a CLASSIFICATION task, not a new search: it re-runs the existing
exhaustive EE4 enumeration (tools/order4_R_class_comparison.py) and
classifies every raw tiling it finds.

Outputs:
  data/ee4_R_5/all_tilings.json      every raw tiling + all labels
  reports/ee4_R_5_catalogue.md       human-readable catalogue

For every tiling it records: five RM indices, five translations,
normalized piece orientations, piece adjacency/contact graph, boundary
touch, cells on the symmetry-fixed planes and on the intersection axis,
the stabilizer within the target's affine symmetry group, and the
equivalence labels:

  - literal target        the actual 25-cell set in the box
  - canonical target      normalize(literal target) (translate class)
  - target modulo proper rotations / modulo full O_h
  - tiling modulo target symmetry (orbit under the target's affine EE4)
  - tiling modulo full O_h (orbit under the whole cubic group)
  - orientation-multiset class (sorted tuple of the five RM indices)

Also verifies (Task 1) that no deduplication bug hides target shapes:
normalize() is injective on cell sets, the search applies no dedup to
results, and every tiling's target is re-checked to be EE4-invariant,
face-connected and 25 cells.

Usage: python3 tools/frontier/classify_ee4_R_tilings.py
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

OUT_JSON = os.path.join(REPO_ROOT, "data", "ee4_R_5", "all_tilings.json")
OUT_CATALOGUE = os.path.join(REPO_ROOT, "reports", "ee4_R_5_catalogue.md")

R = {tuple(int(v) for v in c) for c in PENTACUBES["R"]}


# ---------------------------------------------------------------------------
# placement helpers
# ---------------------------------------------------------------------------

def placement_rotation(p):
    """(k, t) such that p == {RM[k] @ r + t : r in R}."""
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
    k, _ = placement_rotation(p)
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


def apply_affine(pieces, m, t):
    """Apply (M, t) to each piece (elementwise: M*v + t)."""
    t = np.asarray(t, dtype=int)
    return [frozenset(tuple(int(v) for v in (m @ np.array(c) + t))
                      for c in p) for p in pieces]


def tiling_key(pieces):
    """Sortable canonical key for a tiling (set of piece cell-sets)."""
    return tuple(sorted(tuple(sorted(p)) for p in pieces))


def tiling_fixed(pieces, m, t):
    """True iff (M, t) maps the tiling to itself as a set of pieces."""
    return tiling_key(apply_affine(pieces, m, t)) == tiling_key(pieces)


def tiling_oh_key(pieces):
    """O_h orbit key: min over O_h of the origin-normalized image."""
    return _tiling_orbit_key(pieces, OH_MATRICES)


def tiling_proper_key(pieces):
    """Proper-rotation orbit key: min over the 24 rotations."""
    return _tiling_orbit_key(
        pieces, [m for m in OH_MATRICES
                 if tuple(tuple(int(v) for v in row) for row in m)
                 in PROPER_KEYS])


def _tiling_orbit_key(pieces, mats):
    union = set().union(*pieces)
    mn = tuple(min(c[i] for c in union) for i in range(3))
    shifted = [frozenset(tuple(c[i] - mn[i] for i in range(3)) for c in p)
               for p in pieces]
    keys = set()
    for m in mats:
        img = apply_affine(shifted, m, (0, 0, 0))
        u2 = set().union(*img)
        mn2 = tuple(min(c[i] for c in u2) for i in range(3))
        img2 = [frozenset(tuple(c[i] - mn2[i] for i in range(3)) for c in p)
                for p in img]
        keys.add(tiling_key(img2))
    return min(keys)


def rm_multiset(pieces):
    return tuple(sorted(placement_rotation(p)[0] for p in pieces))


def boundary_touch(pieces):
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
    return [[sum(1 for c in p if c[0] == 0),
             sum(1 for c in p if c[1] == 0),
             sum(1 for c in p if c[2] == 0)] for p in pieces]


def axis_cells(pieces):
    """Cells on the intersection axis x=0, y=0 (the z-axis)."""
    return [sorted(c for c in p if c[0] == 0 and c[1] == 0) for p in pieces]


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


def proper_rotation_equivalent(ta, tb):
    """True iff ta, tb are congruent via a proper rotation + translation."""
    for m in OH_MATRICES:
        if tuple(tuple(int(v) for v in row) for row in m) not in PROPER_KEYS:
            continue
        img = {tuple(int(v) for v in m @ np.array(c)) for c in ta}
        mn_img = tuple(min(c[i] for c in img) for i in range(3))
        mn_tb = tuple(min(c[i] for c in tb) for i in range(3))
        t = tuple(mn_tb[i] - mn_img[i] for i in range(3))
        if {tuple(c[i] + t[i] for i in range(3)) for c in img} == set(tb):
            return True
    return False


def oh_equivalent(ta, tb):
    for m in OH_MATRICES:
        img = {tuple(int(v) for v in m @ np.array(c)) for c in ta}
        mn_img = tuple(min(c[i] for c in img) for i in range(3))
        mn_tb = tuple(min(c[i] for c in tb) for i in range(3))
        t = tuple(mn_tb[i] - mn_img[i] for i in range(3))
        if {tuple(c[i] + t[i] for i in range(3)) for c in img} == set(tb):
            return True
    return False


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
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

    # ---- Task 1: independent re-run of the exhaustive enumeration ----
    results, nodes, dt = cmp.search_class(placements, pclosure,
                                          max_tilings=2000)
    assert len(results) == 16, f"expected 16 tilings, got {len(results)}"
    adj = [set() for _ in orbits]
    for oi, o in enumerate(orbits):
        for c in o:
            x, y, z = c
            for nb in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                       (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if nb in orbit_of:
                    adj[oi].add(orbit_of[nb])
        adj[oi].discard(oi)
    conn, cnodes = cmp.count_connected_targets(
        orbits, adj, [len(o) for o in orbits], 25, 300.0)
    assert conn == 2072331, f"connected targets {conn} != 2072331"
    print(f"connected EE4-invariant 25-cell targets: {conn} "
          f"({cnodes} orbit-subsets explored)")

    # ---- no-dedup-bug checks ----
    # (a) all raw results distinct
    assert len({(frozenset(t), c) for t, c in results}) == len(results)
    # (b) every tiling's target is EE4-invariant, connected, 25 cells
    for target, chosen in results:
        assert len(target) == 25
        assert face_connected(target)
        closure = set()
        for i in chosen:
            closure |= pclosure[i]
        assert closure == set(target), "target not a union of EE4 orbits"
    # (c) canonical targets pairwise distinct (normalize is injective)
    by_canon = {}
    for target, chosen in results:
        by_canon.setdefault(normalize(target), []).append((target, chosen))
    assert len(by_canon) == 4

    # ---- Task 2/11: target classification ----
    canon_list = sorted(by_canon)
    # literal targets: distinct 25-cell sets appearing as tiling unions
    literal_targets = {}
    for target, chosen in results:
        literal_targets.setdefault(frozenset(target), []).append(
            (target, chosen))
    # proper-rotation classes among the 4 canonical targets
    prop_classes = []
    for c in canon_list:
        for cls in prop_classes:
            if proper_rotation_equivalent(set(c), set(cls[0])):
                cls.append(c)
                break
        else:
            prop_classes.append([c])
    # O_h classes among the 4 canonical targets
    oh_classes = []
    for c in canon_list:
        for cls in oh_classes:
            if oh_equivalent(set(c), set(cls[0])):
                cls.append(c)
                break
        else:
            oh_classes.append([c])

    # ---- Task 3: per-tiling data ----
    tilings = []
    for ti, (target, chosen) in enumerate(results):
        pieces = [placements[i] for i in chosen]
        ori = [placement_rotation(p) for p in pieces]
        adj, contacts = face_adjacency(pieces)
        canon_idx = canon_list.index(normalize(target)) + 1
        aff = affine_symmetries(target)
        stab = [(element_kind(m), [list(t) for t in [t]]) for m, t in aff
                if tiling_fixed(pieces, m, t)]
        stab_kinds = sorted(k for k, _ in stab)
        tilings.append({
            "id": ti,
            "canonical_target_index": canon_idx,
            "literal_target": sorted(target),
            "pieces": [{
                "rm_index": k,
                "translation": list(t),
                "cells": sorted(p),
                "norm": [list(c) for c in norm_orientation(p)],
            } for p, (k, t) in zip(pieces, ori)],
            "rm_multiset": list(rm_multiset(pieces)),
            "adjacency": [sorted(a) for a in adj],
            "contacts": contacts,
            "boundary_touch": boundary_touch(pieces),
            "fixed_plane_counts": fixed_plane_counts(pieces),
            "axis_cells": axis_cells(pieces),
            "stabilizer_kinds": stab_kinds,
            "target_affine_count": len(aff),
        })

    # ---- Task 5/6: orientation-multiset classes ----
    multiset_classes = {}
    for t in tilings:
        multiset_classes.setdefault(tuple(t["rm_multiset"]), []).append(t["id"])
    assert len(multiset_classes) == 8
    assert all(len(v) == 2 for v in multiset_classes.values())

    # relationship within each multiset pair: the two tilings are
    # translates of each other (same orientation multiset, different
    # literal targets); record the translation vector
    ms_rel = {}
    for ms, ids in sorted(multiset_classes.items()):
        a, b = (tilings[i] for i in ids)
        pa = [frozenset(p["cells"]) for p in a["pieces"]]
        pb = [frozenset(p["cells"]) for p in b["pieces"]]
        same_canon = a["canonical_target_index"] == b["canonical_target_index"]
        trans = None
        for s in ((dx, dy, dz) for dx in range(-4, 5)
                  for dy in range(-4, 5) for dz in range(-4, 5)):
            if {frozenset(tuple(c[i] + s[i] for i in range(3)) for c in p)
                    for p in pa} == set(pb):
                trans = list(s)
                break
        ms_rel[ms] = {
            "same_canonical_target": same_canon,
            "translation": trans,
            "same_literal_target": set(a["literal_target"]) ==
            set(b["literal_target"]),
        }

    # ---- tiling classes under target symmetry ----
    # The target's full EE4 group contains reflections (MX, MY); their
    # images of a tiling are decompositions into REFLECTED R pieces,
    # which are invalid here (R is chiral, reflections forbidden).  So
    # the equivalence on valid tilings is generated by the proper
    # subgroup {I, RZ} (the c2 about z).  Classes are RZ-orbits of size
    # 2 (every tiling has trivial stabilizer).
    ts_classes = {}
    for canon_idx in range(1, 5):
        group = [t for t in tilings
                 if t["canonical_target_index"] == canon_idx]
        aff = affine_symmetries(set(group[0]["literal_target"]))
        proper_aff = [(m, t) for m, t in aff
                      if tuple(tuple(int(v) for v in row) for row in m)
                      in PROPER_KEYS]
        seen = {}
        for t in group:
            pieces = [frozenset(p["cells"]) for p in t["pieces"]]
            orbit_keys = {tiling_key(apply_affine(pieces, m, tt))
                          for m, tt in proper_aff}
            rep = min(orbit_keys)
            seen.setdefault(rep, []).append(t["id"])
        for k, ids in sorted(seen.items()):
            # the element relating the pair (must be the c2 about z)
            a, b = sorted(ids)
            rel = None
            for m, tt in proper_aff:
                if tiling_key(apply_affine(
                        [frozenset(p["cells"]) for p in tilings[a]["pieces"]],
                        m, tt)) == tiling_key(
                        [frozenset(p["cells"]) for p in tilings[b]["pieces"]]):
                    rel = element_kind(m)
                    break
            ts_classes[tuple(sorted(ids))] = {
                "canonical_target_index": canon_idx,
                "tiling_ids": sorted(ids),
                "relating_element": rel,
                "proper_symmetry_subgroup": sorted(
                    element_kind(m) for m, _ in proper_aff),
            }

    # ---- tiling classes under full O_h and under proper rotations ----
    oh_tiling_classes = {}
    proper_tiling_classes = {}
    for t in tilings:
        key = tiling_oh_key([frozenset(p["cells"]) for p in t["pieces"]])
        oh_tiling_classes.setdefault(key, []).append(t["id"])
        pkey = tiling_proper_key([frozenset(p["cells"]) for p in t["pieces"]])
        proper_tiling_classes.setdefault(pkey, []).append(t["id"])

    # ---- Task 7: target invariants ----
    targets_out = []
    for k, canon in enumerate(canon_list):
        lst = by_canon[canon]
        target = set(lst[0][0])
        syms = full_symmetry(target)
        kinds = sorted(element_kind(m) for m in syms
                       if element_kind(m) != "identity")
        aff = affine_symmetries(target)
        xs = [c[0] for c in target]
        ys = [c[1] for c in target]
        zs = [c[2] for c in target]
        # literal targets of the tilings in this group
        lits = sorted({frozenset(t) for t, _ in lst})
        # translation between the literal targets (they are translates)
        lit_trans = None
        if len(lits) == 2:
            A = set(lits[0])
            B = set(lits[1])
            for s in ((dx, dy, dz) for dx in range(-4, 5)
                      for dy in range(-4, 5) for dz in range(-4, 5)):
                if {tuple(c[i] + s[i] for i in range(3)) for c in A} == B:
                    lit_trans = list(s)
                    break
        # proper-rotation partners
        prop_partners = [canon_list.index(c) + 1 for cls in prop_classes
                         for c in cls if c == canon]
        targets_out.append({
            "canonical_index": k + 1,
            "canonical_cells": list(canon),
            "literal_targets": [sorted(l) for l in lits],
            "literal_target_translation": lit_trans,
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
            "tiling_ids": [t["id"] for t in tilings
                           if t["canonical_target_index"] == k + 1],
        })

    # ---- assemble report ----
    report = {
        "piece": "R",
        "symmetry_class": "EE4",
        "box": {"min": [-2, -2, -2], "max": [2, 2, 2]},
        "search": {
            "tilings_total": len(results),
            "canonical_targets": len(by_canon),
            "connected_targets": conn,
            "connected_target_nodes": cnodes,
            "nodes": nodes,
            "seconds": round(dt, 2),
        },
        "counts": {
            "raw_tilings": len(results),
            "literal_targets": len(literal_targets),
            "canonical_targets": len(by_canon),
            "target_classes_proper_rotation": len(prop_classes),
            "target_classes_oh": len(oh_classes),
            "tiling_classes_target_symmetry": len(ts_classes),
            "tiling_classes_proper_rotation": len(proper_tiling_classes),
            "tiling_classes_oh": len(oh_tiling_classes),
            "orientation_multiset_classes": len(multiset_classes),
        },
        "targets": targets_out,
        "tilings": tilings,
        "orientation_multiset_classes": [
            {"multiset": list(ms), "tiling_ids": ids,
             "relationship": ms_rel[ms]}
            for ms, ids in sorted(multiset_classes.items())],
        "target_symmetry_classes": [
            {"tiling_ids": v["tiling_ids"],
             "canonical_target_index": v["canonical_target_index"],
             "relating_element": v["relating_element"],
             "proper_symmetry_subgroup": v["proper_symmetry_subgroup"]}
            for v in ts_classes.values()],
        "oh_tiling_classes": [
            {"tiling_ids": sorted(ids)} for ids in oh_tiling_classes.values()],
        "proper_tiling_classes": [
            {"tiling_ids": sorted(ids)}
            for ids in proper_tiling_classes.values()],
    }

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(report, f, indent=2)
    print(f"wrote {OUT_JSON}")

    # ---- summary ----
    print("\n=== COUNTS ===")
    for k, v in report["counts"].items():
        print(f"  {k}: {v}")
    print("\n=== TARGETS ===")
    for t in targets_out:
        print(f"  canonical {t['canonical_index']}: bbox {t['bbox']}, "
              f"literal targets {len(t['literal_targets'])}, "
              f"tilings {t['tiling_ids']}")
    print(f"  proper-rotation classes: {len(prop_classes)} "
          f"({[len(c) for c in prop_classes]}), "
          f"O_h classes: {len(oh_classes)}")
    print("\n=== TILINGS ===")
    for t in tilings:
        print(f"  T{t['id']}: canon {t['canonical_target_index']} "
              f"RM {t['rm_multiset']} stab {t['stabilizer_kinds']} "
              f"adj {t['adjacency']}")
    print("\n=== ORIENTATION-MULTISET CLASSES ===")
    for ms, ids in sorted(multiset_classes.items()):
        print(f"  {list(ms)}: {ids} {ms_rel[ms]}")
    print("\n=== TILING CLASSES ===")
    print(f"  under target symmetry (proper subgroup {{I, RZ}}): "
          f"{len(ts_classes)}")
    for v in ts_classes.values():
        print(f"    {v['tiling_ids']} (canon {v['canonical_target_index']}, "
              f"related by {v['relating_element']})")
    print(f"  under full O_h: {len(oh_tiling_classes)}")
    for ids in oh_tiling_classes.values():
        print(f"    {sorted(ids)}")
    print(f"  under proper rotations: {len(proper_tiling_classes)}")
    for ids in proper_tiling_classes.values():
        print(f"    {sorted(ids)}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Regression test: the complete EE4 5-R tiling classification.

Reads data/ee4_R_5/all_tilings.json (produced by
tools/frontier/classify_ee4_R_tilings.py) and re-derives the headline
invariants from the raw data:

  1. every tiling is a valid exact cover: 5 pairwise-disjoint placements,
     each a proper rotation (RM 0..23, det +1) of the R pentacube plus an
     integer translation, covering exactly its literal target,
  2. counts: 16 raw tilings, 8 literal targets, 4 canonical targets,
  3. the 4 canonical targets are one shape: 1 class under proper
     rotations and under O_h,
  4. tiling classes: 8 under target symmetry (proper subgroup {I, RZ},
     each class an RZ-orbit of size 2), 1 under proper rotations, 1
     under O_h,
  5. 8 orientation-multiset classes of 2 tilings each; the two members
     are pure translates of each other (same multiset, different literal
     target),
  6. every tiling has trivial stabilizer within its target's full EE4
     group,
  7. the witness T4 (multiset {3,5,11,17,23}) matches the verified
     fixture tests/fixtures/ee4_R_5.json.

Run:  PYTHONPATH=. .venv/bin/python tests/test_ee4_R_classification.py
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
from common.symmetry import OH_MATRICES, PROPER_KEYS, element_kind

DATA = os.path.join(REPO_ROOT, "data", "ee4_R_5", "all_tilings.json")
FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "ee4_R_5.json")

RZ = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]], dtype=int)


def apply(pieces, m, t):
    t = np.asarray(t, dtype=int)
    return [frozenset(tuple(int(v) for v in (m @ np.array(c) + t))
                      for c in p) for p in pieces]


def tiling_key(pieces):
    """Raw key (translation-sensitive): sorted piece cell-tuples."""
    return tuple(sorted(tuple(sorted(p)) for p in pieces))


def orbit_key(pieces, mats):
    """Translation-invariant orbit key: normalize, apply each M,
    re-normalize, take the lexicographic min of the raw keys."""
    union = set().union(*pieces)
    mn = tuple(min(c[i] for c in union) for i in range(3))
    shifted = [frozenset(tuple(c[i] - mn[i] for i in range(3)) for c in p)
               for p in pieces]
    keys = set()
    for m in mats:
        img = apply(shifted, m, (0, 0, 0))
        u2 = set().union(*img)
        mn2 = tuple(min(c[i] for c in u2) for i in range(3))
        img2 = [frozenset(tuple(c[i] - mn2[i] for i in range(3)) for c in p)
                for p in img]
        keys.add(tiling_key(img2))
    return min(keys)


def main():
    with open(DATA) as f:
        data = json.load(f)

    R = PENTACUBES["R"]
    tilings = data["tilings"]
    assert len(tilings) == 16, f"raw tilings {len(tilings)} != 16"

    # 1. every tiling is a valid exact cover
    for t in tilings:
        target = {tuple(c) for c in t["literal_target"]}
        assert len(target) == 25
        union = set()
        for p in t["pieces"]:
            k = p["rm_index"]
            assert 0 <= k < 24
            assert int(round(np.linalg.det(RM[k]))) == 1, \
                f"T{t['id']} RM[{k}] not proper"
            rot = {tuple(int(v) for v in RM[k] @ np.array(r)) for r in R}
            tr = tuple(p["translation"])
            cells = {tuple(c[j] + tr[j] for j in range(3)) for c in rot}
            assert cells == {tuple(c) for c in p["cells"]}, \
                f"T{t['id']} piece {k} cells mismatch"
            assert len(cells) == 5
            assert cells.isdisjoint(union), f"T{t['id']} overlap"
            union |= cells
        assert union == target, f"T{t['id']} does not exactly cover target"
    print("1. all 16 tilings are valid exact covers (proper R placements)  ok")

    # 2. counts
    assert data["counts"]["raw_tilings"] == 16
    assert data["counts"]["literal_targets"] == 8
    assert data["counts"]["canonical_targets"] == 4
    lits = {frozenset(tuple(c) for c in t["literal_target"])
            for t in tilings}
    assert len(lits) == 8, f"literal targets {len(lits)} != 8"
    canons = {t["canonical_target_index"] for t in tilings}
    assert canons == {1, 2, 3, 4}
    print("2. counts: 16 tilings, 8 literal targets, 4 canonical targets  ok")

    # 3. canonical targets are one shape (proper rotations, O_h)
    canon_cells = {}
    for t in data["targets"]:
        canon_cells[t["canonical_index"]] = \
            {tuple(c) for c in t["canonical_cells"]}
    keys = {orbit_key([cc], OH_MATRICES) for cc in canon_cells.values()}
    assert len(keys) == 1, "canonical targets not O_h-equivalent"
    pkeys = {orbit_key([cc], [m for m in OH_MATRICES
                              if tuple(tuple(int(v) for v in row)
                                       for row in m) in PROPER_KEYS])
             for cc in canon_cells.values()}
    assert len(pkeys) == 1, "canonical targets not proper-rotation-equivalent"
    print("3. 4 canonical targets = one shape (1 class proper, 1 O_h)  ok")

    # 4. tiling classes
    pieces_of = {t["id"]: [frozenset(tuple(c) for c in p["cells"])
                           for p in t["pieces"]] for t in tilings}
    # proper subgroup {I, RZ} of each target
    ts_classes = {}
    for canon in (1, 2, 3, 4):
        group = [t for t in tilings
                 if t["canonical_target_index"] == canon]
        aff = [(m, t) for m, t in
               [(np.eye(3, dtype=int), (0, 0, 0)),
                (RZ, (0, 0, 0))]]
        seen = {}
        for t in group:
            orbit = {tiling_key(apply(pieces_of[t["id"]], m, tt))
                     for m, tt in aff}
            seen.setdefault(min(orbit), []).append(t["id"])
        for ids in seen.values():
            assert len(ids) == 2, f"target-sym class {ids} size != 2"
            a, b = ids
            assert set(apply(pieces_of[a], RZ, (0, 0, 0))) == \
                set(pieces_of[b]), f"T{a}, T{b} not RZ-related"
            ts_classes[tuple(sorted(ids))] = True
    assert len(ts_classes) == 8, f"target-sym classes {len(ts_classes)} != 8"
    # proper-rotation and O_h tiling classes
    oh_keys = {orbit_key(pieces_of[i], OH_MATRICES) for i in range(16)}
    assert len(oh_keys) == 1, "tilings not all O_h-equivalent"
    proper_mats = [m for m in OH_MATRICES
                   if tuple(tuple(int(v) for v in row) for row in m)
                   in PROPER_KEYS]
    prop_keys = {orbit_key(pieces_of[i], proper_mats) for i in range(16)}
    assert len(prop_keys) == 1, "tilings not all proper-rotation-equivalent"
    print("4. tiling classes: 8 under target symmetry (RZ-orbits), "
          "1 proper, 1 O_h  ok")

    # 5. orientation-multiset classes: 8 of 2, pure translates
    ms_classes = {}
    for t in tilings:
        ms_classes.setdefault(tuple(t["rm_multiset"]), []).append(t["id"])
    assert len(ms_classes) == 8, f"multiset classes {len(ms_classes)} != 8"
    for ms, ids in ms_classes.items():
        assert len(ids) == 2, f"multiset class {ms} size != 2"
        a, b = ids
        pa, pb = pieces_of[a], pieces_of[b]
        la = frozenset(tuple(c) for c in tilings[a]["literal_target"])
        lb = frozenset(tuple(c) for c in tilings[b]["literal_target"])
        assert la != lb, f"multiset pair T{a}, T{b} on same literal target"
        found = False
        for s in ((dx, dy, dz) for dx in range(-4, 5)
                  for dy in range(-4, 5) for dz in range(-4, 5)):
            if {frozenset(tuple(c[i] + s[i] for i in range(3)) for c in p)
                    for p in pa} == set(pb):
                found = True
                break
        assert found, f"multiset pair T{a}, T{b} not translates"
    print("5. 8 orientation-multiset classes of 2 (pure translates)  ok")

    # 6. trivial stabilizers
    for t in tilings:
        assert t["stabilizer_kinds"] == ["identity"], \
            f"T{t['id']} stabilizer {t['stabilizer_kinds']} not trivial"
    print("6. all stabilizers trivial within full EE4 target group  ok")

    # 7. witness T4 matches the verified fixture
    with open(FIXTURE) as f:
        fx = json.load(f)
    t4 = tilings[4]
    assert t4["rm_multiset"] == [3, 5, 11, 17, 23]
    fx_target = {tuple(c) for c in fx["target"]}
    assert set(tuple(c) for c in t4["literal_target"]) == fx_target, \
        "T4 literal target != fixture target"
    fx_pieces = {frozenset(tuple(c) for c in pl["cells"])
                 for pl in fx["placements"]}
    assert {frozenset(tuple(c) for c in p["cells"])
            for p in t4["pieces"]} == fx_pieces, \
        "T4 pieces != fixture placements"
    print("7. witness T4 matches tests/fixtures/ee4_R_5.json  ok")

    print("\nALL EE4 CLASSIFICATION CHECKS PASSED")


if __name__ == "__main__":
    main()
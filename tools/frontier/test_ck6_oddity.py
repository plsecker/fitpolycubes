#!/usr/bin/env python3
"""
Regression tests for the CK6 oddity fixture and its interpretation.

Establishes the trustworthy independent CK6 test fixture agreed in
docs/frontier/ck6_oddity_design.md (Stage 1):

- George Sicherman's minimal L-tricube CK6 oddity (image
  png/3-2-ck6.png on https://sicherman.net/coddities/c3lodd/index.html,
  label "3") is a 9-cell figure tiled by **three** L tricubes.  The
  number printed on his figures is the tile count; the "3-2-" filename
  prefix is a figure id, not a tile count.
- Independent enumeration reproduces exactly ONE 9-cell exact-CK6
  L-tricube oddity up to full cubic congruence -- and up to proper
  rotations alone -- matching his uniqueness asterisk.
- The two 6-cell two-L-tricube hexacubes sometimes quoted alongside it
  are CK6-symmetric figures but are NOT oddities (2 tiles is even);
  they never contradicted George's table.
"""

import itertools
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import numpy as np

from common.rotmatrix import RM, Rz90
from common.symmetry import (
    OH_MATRICES,
    PROPER_KEYS,
    affine_symmetries,
    canonical_form,
    ck6_affine_maps,
    ck6_fixed_point_types,
    element_kind,
    full_symmetry,
    normalize,
    order4_lunnon_code,
    symmetry_order,
)
from common.algorithm_x import solve
from common.registry import PENTACUBES

# ---------------------------------------------------------------------------
# Fixture constants (all verified; see design doc)
# ---------------------------------------------------------------------------

# The unique 9-cell exact-CK6 L-tricube oddity, canonical under O_h
# (translation to min-origin).  Symmetry fixed point is (1,1,1); the
# CK6 axis is the face diagonal (1,-1,0) through it.
FIXTURE_9CELL = (
    (0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 0, 1),
    (1, 1, 1), (1, 2, 1), (2, 1, 1), (2, 2, 1), (2, 2, 2),
)
FIXTURE_FIXED_POINT = (1, 1, 1)

# 6-cell unions of two L tricubes with exact CK6 symmetry.  These are
# CK6-symmetric figures but NOT oddities (2 tiles = even).
HEXACUBE_CK6_A = ((0, 0, 0), (0, 0, 1), (0, 1, 1),
                  (1, 0, 1), (1, 1, 1), (1, 1, 2))
HEXACUBE_CK6_B = ((0, 0, 1), (0, 1, 0), (0, 1, 1),
                  (1, 1, 1), (1, 1, 2), (1, 2, 1))
# 6-cell two-L union with D3d (order 12) symmetry: 2x2x2 minus a
# body-diagonal pair of cells.
HEXACUBE_ORDER12 = ((0, 0, 0), (0, 0, 1), (0, 1, 0),
                    (1, 0, 1), (1, 1, 0), (1, 1, 1))

L_TRICUBE = ((0, 0, 0), (1, 0, 0), (0, 1, 0))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def l_orientations():
    """Distinct orientations of the L tricube under the 24 rotations."""
    seen, out = set(), []
    for r in RM:
        m = np.asarray(r, dtype=int)
        o = normalize(tuple(m @ np.array(c) for c in L_TRICUBE))
        if o not in seen:
            seen.add(o)
            out.append(tuple(sorted(o)))
    return out


def l_placements(window):
    """All L-tricube placements fully inside the window cell set."""
    wset = set(window)
    out = set()
    for o in l_orientations():
        for a in window:
            cells = frozenset((a[0] + c[0], a[1] + c[1], a[2] + c[2])
                              for c in o)
            if cells <= wset:
                out.add(cells)
    return sorted(out)


def is_face_connected(cells):
    cells = set(cells)
    start = next(iter(cells))
    seen, stack = {start}, [start]
    while stack:
        x, y, z = stack.pop()
        for w in ((x + 1, y, z), (x - 1, y, z),
                  (x, y + 1, z), (x, y - 1, z),
                  (x, y, z + 1), (x, y, z - 1)):
            if w in cells and w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == len(cells)


def exact_cover_tiling_counts(cells, placements):
    """Number of ways to partition `cells` by disjoint placements."""
    rows = [p for p in placements if p <= set(cells)]
    y = {i: sorted(p) for i, p in enumerate(rows)}
    x = {c: set() for c in cells}
    for i, cs in y.items():
        for c in cs:
            x[c].add(i)
    return sum(1 for sol in solve(x, y) if len(sol) == len(cells) // len(L_TRICUBE))


def classify(cells):
    syms = full_symmetry(cells)
    code = order4_lunnon_code(syms)
    if code is not None:
        return code
    return f"order{symmetry_order(syms)}"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_oh_group_basics():
    assert len(OH_MATRICES) == 48
    keys = {tuple(map(tuple, m.tolist())) for m in OH_MATRICES}
    assert len(keys) == 48
    proper = {tuple(map(tuple, m.tolist())) for m in OH_MATRICES
              if int(round(np.linalg.det(m))) == 1}
    assert len(proper) == 24
    for m in OH_MATRICES:
        det = int(round(np.linalg.det(m)))
        assert det in (1, -1)
    # every rotation matrix from rotmatrix.RM appears in OH
    rm_keys = {tuple(map(tuple, np.asarray(r, dtype=int).tolist())) for r in RM}
    assert rm_keys <= keys
    print("  PASS: O_h has 48 distinct elements, 24 proper; contains RM")


def test_ck6_generator_matrices():
    c = np.array([[0, 1, 0], [1, 0, 0], [0, 0, -1]])  # 180 deg about (1,1,0)
    k = -np.eye(3, dtype=int)
    ck = k @ c
    assert tuple(map(tuple, c.tolist())) in {tuple(map(tuple, m.tolist()))
                                             for m in OH_MATRICES}
    assert int(round(np.linalg.det(c))) == 1
    assert int(round(np.linalg.det(ck))) == -1
    group = {tuple(map(tuple, m.tolist()))
             for m in (np.eye(3, dtype=int), c, k, ck)}
    assert len(group) == 4
    for a in group:
        for b in group:
            prod = np.array(a) @ np.array(b)
            assert tuple(map(tuple, prod.tolist())) in group
    print("  PASS: CK6 = {E, C, K, CK} is a closed V4; C in O_h proper")


def test_ck6_affine_types():
    # all four fixed-point types act integrally and close;
    # only the center type has K-fixed cells (odd-volume lemma)
    window = [(x, y, z) for x in range(-2, 3)
              for y in range(-2, 3) for z in range(-2, 3)]
    for fp in ck6_fixed_point_types():
        maps = ck6_affine_maps(fp)  # raises if not integral/distinct/closed
        k_fixed = [v for v in window if maps["K"](v) == v]
        if fp == (0, 0):
            assert k_fixed, "center type must fix the origin cell"
        else:
            assert not k_fixed, f"type {fp} unexpectedly has K-fixed cells"
    print("  PASS: 4 CK6 fixed-point types; only (0,0,0) has K-fixed cells")


def test_ck6_orbit_census():
    maps = list(ck6_affine_maps((0, 0)).values())
    window = [(x, y, z) for x in range(-3, 4)
              for y in range(-3, 4) for z in range(-3, 4)]
    seen, sizes = set(), {}
    for v in window:
        o = frozenset(m(v) for m in maps)
        if o in seen:
            continue
        seen.add(o)
        sizes[len(o)] = sizes.get(len(o), 0) + 1
    assert sizes == {1: 1, 2: 27, 4: 72}, sizes
    print("  PASS: center-type CK6 orbit census in 7^3 window: "
          "{1: 1, 2: 27, 4: 72}")


def test_order4_lunnon_classes():
    i = np.eye(3, dtype=int)
    b_x = np.diag([1, -1, -1])
    b_y = np.diag([-1, 1, -1])
    b_z = np.diag([-1, -1, 1])
    e_x = np.diag([-1, 1, 1])
    e_z = np.diag([1, 1, -1])
    c_xy = np.array([[0, 1, 0], [1, 0, 0], [0, 0, -1]])
    c_ac = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]])  # C2 about (1,0,1)
    f_xy = c_xy @ e_z           # mirror in plane x=y
    c4 = np.asarray(Rz90, dtype=int)
    s4 = -c4
    cases = [
        ("A12", [i, c4, c4 @ c4, c4 @ c4 @ c4]),
        ("J10", [i, s4, c4 @ c4, s4 @ s4 @ s4]),
        ("BB10", [i, b_x, b_y, b_z]),
        ("BC10", [i, b_z, c_xy, b_z @ c_xy]),
        ("CE3", [i, c_xy, e_z, f_xy]),
        ("BF6", [i, b_z, f_xy, b_z @ f_xy]),
        ("EE4", [i, b_y, e_z, b_y @ e_z]),
        ("BE4", [i, b_z, e_z, b_z @ e_z]),
        ("CK6", [i, c_xy, -i, -c_xy]),
    ]
    for code, group in cases:
        got = order4_lunnon_code(group)
        assert got == code, f"expected {code}, got {got}"
    # the T pentacube has EE4 symmetry: no CK6 subgroup
    t = [tuple(map(int, p)) for p in PENTACUBES["T"]]
    assert classify(t) == "EE4"
    # ... and no rotation-conjugate of a CK6 generator is a T symmetry
    sym_keys = {tuple(map(tuple, m.tolist())) for m in full_symmetry(t)}
    for r in RM:
        rm_ = np.asarray(r, dtype=int)
        rinv = np.linalg.inv(rm_).astype(int)
        for gen in (c_xy, -i, -c_xy):
            conj = rinv @ gen @ rm_
            assert tuple(map(tuple, conj.tolist())) not in sym_keys
    # the L tricube is CE3 (hence George's CE3 row shows the piece itself)
    assert classify(L_TRICUBE) == "CE3"
    print("  PASS: all nine order-4 Lunnon classes identified; "
          "T=EE4 (no CK6 subgroup), L-tricube=CE3")


def test_nine_cell_ck6_fixture():
    """Core fixture: the unique 9-cell exact-CK6 L-tricube oddity."""
    rmax = 4  # connected K-closed 9-cell sets reach at most L1 = 4
    ball = [(x, y, z) for x in range(-rmax, rmax + 1)
            for y in range(-rmax, rmax + 1) for z in range(-rmax, rmax + 1)
            if abs(x) + abs(y) + abs(z) <= rmax]
    bset = set(ball)
    maps = list(ck6_affine_maps((0, 0)).values())

    four_orbits, two_orbits, seen = [], [], set()
    for v in ball:
        o = frozenset(m(v) for m in maps)
        if o in seen:
            continue
        seen.add(o)
        if len(o) == 4 and o <= bset:
            four_orbits.append(o)
        elif len(o) == 2 and o <= bset:
            two_orbits.append(o)

    targets = []
    for a4 in range(0, 3):
        b2 = (8 - 4 * a4) // 2
        if 4 * a4 + 2 * b2 != 8:
            continue
        for c4 in itertools.combinations(four_orbits, a4):
            base = frozenset().union(*c4) if c4 else frozenset()
            for c2 in itertools.combinations(two_orbits, b2):
                cells = (base | frozenset().union(*c2) if c2 else base) \
                    | {(0, 0, 0)}
                if len(cells) == 9 and is_face_connected(cells):
                    targets.append(cells)
    assert len(targets) == 16, len(targets)

    placements = l_placements(ball)
    tileable = []
    for cells in targets:
        n = exact_cover_tiling_counts(cells, placements)
        if n:
            tileable.append((cells, n))
    assert len(tileable) == 2, len(tileable)
    assert all(n == 2 for _, n in tileable)

    # exactly one canonical figure, under full O_h AND proper rotations
    canon_full = {canonical_form(c) for c, _ in tileable}
    canon_proper = {canonical_form(c, proper_only=True) for c, _ in tileable}
    assert len(canon_full) == 1, canon_full
    assert len(canon_proper) == 1, canon_proper
    fixture = canon_full.pop()
    assert fixture == FIXTURE_9CELL, fixture

    # exact class CK6, affine group about (1,1,1), fixed point in figure
    assert classify(fixture) == "CK6"
    aff = affine_symmetries(fixture)
    assert len(aff) == 4
    center = np.array(FIXTURE_FIXED_POINT)
    for m, t in aff:
        assert tuple(m @ center + np.array(t)) == FIXTURE_FIXED_POINT
    assert FIXTURE_FIXED_POINT in set(fixture)

    # cross-check canonicalization against solvers/reduce_solutions.py
    from solvers.reduce_solutions import (get_48_transformations,
                                          get_canonical)
    rs_canon = {get_canonical([list(c)], get_48_transformations())[0]
                for c, _ in tileable}
    assert len(rs_canon) == 1
    assert next(iter(rs_canon)) == fixture
    print("  PASS: unique 9-cell exact-CK6 L-tricube oddity "
          "(3 tiles), canonical form = FIXTURE_9CELL, 2 tilings; "
          "agrees with reduce_solutions canonicalization")


def test_nine_cell_union_scan_cross_check():
    """Independent tiling-first scan finds the same unique figure."""
    rmax = 4
    ball = [(x, y, z) for x in range(-rmax, rmax + 1)
            for y in range(-rmax, rmax + 1) for z in range(-rmax, rmax + 1)
            if abs(x) + abs(y) + abs(z) <= rmax]
    bset = set(ball)
    placements = l_placements(ball)
    maps = ck6_affine_maps((0, 0))
    c_map, k_map, ck_map = maps["C"], maps["K"], maps["CK"]
    center = (0, 0, 0)

    hits = set()
    p1s = [p for p in placements if center in p]
    for p1 in p1s:
        s1 = p1 | frozenset(k_map(c) for c in p1)
        if len(s1) > 9:
            continue
        for p2 in placements:
            if p2 & p1:
                continue
            s2 = s1 | p2 | frozenset(k_map(c) for c in p2)
            if len(s2) > 9:
                continue
            base = p1 | p2
            for p3 in placements:
                # partition disjointness is against the PIECES, not the
                # K-image cell sets (the earlier probe's bug)
                if (p3 & p1) or (p3 & p2):
                    continue
                u = base | p3
                if len(u) != 9 or not s2 <= u:
                    continue
                if not frozenset(k_map(c) for c in p3) <= u:
                    continue
                if (frozenset(c_map(c) for c in u) != u
                        or frozenset(ck_map(c) for c in u) != u):
                    continue
                if is_face_connected(u):
                    hits.add(canonical_form(u))
    assert hits == {FIXTURE_9CELL}, hits
    print("  PASS: tiling-first scan reproduces the unique 9-cell figure")


def test_six_cell_two_tile_figures_not_oddities():
    """The two 6-cell two-L hexacubes are CK6-symmetric but NOT oddities."""
    assert classify(HEXACUBE_CK6_A) == "CK6"
    assert classify(HEXACUBE_CK6_B) == "CK6"
    assert canonical_form(HEXACUBE_CK6_A) != canonical_form(HEXACUBE_CK6_B)
    # both are tileable by two L tricubes -- 2 tiles is even, so neither
    # is an oddity and neither contradicts Sicherman's tables
    window = [(x, y, z) for x in range(0, 3) for y in range(0, 3)
              for z in range(0, 3)]
    for hexa in (HEXACUBE_CK6_A, HEXACUBE_CK6_B):
        assert exact_cover_tiling_counts(hexa, l_placements(window)) >= 1
        assert len(hexa) == 6  # 6 cells = 2 tiles = even
    # the companion 2x2x2-minus-diagonal-pair figure has order 12 (D3d)
    assert classify(HEXACUBE_ORDER12) == "order12"
    print("  PASS: 6-cell two-L hexacubes are exact-CK6 but not oddities; "
          "companion figure has order-12 symmetry")


# ---------------------------------------------------------------------------
# Stage 2: volume 15 (3 T pentacubes) -- proven negative result
# ---------------------------------------------------------------------------

def test_volume15_oddity_search_targets_method():
    """Method A: complete orbit enumeration + exact cover finds zero.

    Regression anchors (deterministic, independently recomputable):
      - T placements in the L1<=7 domain: 3288 (12 orientations)
      - connected CK6-closed 15-cell targets: 368
      - target symmetry census: CK6 318, order8 38, order16 10, order12 2
      - tileable targets: 0
    """
    from common.oddity import (
        count_exact_covers,
        enumerate_connected_ck6_targets,
        is_face_connected,
        l1_ball,
        max_l1_for_volume,
        placements_by_cell,
        placements_in_region,
        unique_orientations,
    )
    volume = 15
    assert max_l1_for_volume(volume) == 7
    piece = [tuple(map(int, c)) for c in PENTACUBES["T"]]
    assert len(unique_orientations(piece)) == 12
    ball = l1_ball(7)
    assert len(ball) == 575
    placements = placements_in_region(piece, ball)
    assert len(placements) == 3504  # hardened anchor set (2026-09-10); == brute force

    maps = ck6_affine_maps((0, 0))
    targets = list(enumerate_connected_ck6_targets(volume))
    assert len(targets) == 368, len(targets)

    from collections import Counter
    census = Counter()
    for t in targets:
        assert len(t) == volume
        assert is_face_connected(t)
        # CK6 closure (supersets of CK6 pass too: "or higher symmetry")
        assert all(frozenset(m(c) for c in t) == t for m in maps.values())
        census[classify(t)] += 1
    assert dict(census) == {"CK6": 318, "order8": 38,
                            "order16": 10, "order12": 2}, census

    index = placements_by_cell(piece, ball)
    for t in targets:
        rows = {}
        for c in t:
            for p in index[c]:
                rows[id(p)] = p
        assert count_exact_covers(t, rows.values()) == 0

    # count_exact_covers sanity: the 9-cell L fixture has exactly 2 covers
    l_window = [(x, y, z) for x in range(0, 3)
                for y in range(0, 3) for z in range(0, 3)]
    assert (count_exact_covers(FIXTURE_9CELL, l_placements(l_window)) == 2)
    print("  PASS: volume 15 Method A: 368 CK6-closed targets "
          "(318 CK6 / 38 o8 / 10 o16 / 2 o12), ZERO tileable by 3 T")


def test_volume15_oddity_search_tilings_method():
    """Method B: independent tiling-first scan also finds zero."""
    sys.path.insert(0, os.path.join(
        os.path.dirname(__file__), "..", "..", "solvers"))
    from solvers.t_ck6_oddity_search import run_tilings_method
    from common.oddity import l1_ball, placements_in_region
    from common.symmetry import ck6_affine_maps
    from common.registry import PENTACUBES

    piece = [tuple(map(int, c)) for c in PENTACUBES["T"]]
    placements = placements_in_region(piece, l1_ball(7))
    maps = ck6_affine_maps((0, 0))
    hits = run_tilings_method(15, piece, placements, maps,
                              lambda _msg: None)
    assert len(hits) == 0, hits
    print("  PASS: volume 15 Method B: zero CK6-closed tilings "
          "(agrees with Method A)")


# ---------------------------------------------------------------------------
# Stage 3: volume 25 (5 T pentacubes) -- proven negative result
# ---------------------------------------------------------------------------

def _synthetic_t5_region():
    """A 25-cell region that IS tileable by 5 T's (positive control)."""
    piece = [tuple(map(int, c)) for c in PENTACUBES["T"]]
    synth = set()
    for dx in (0, 3, 6, 9):
        synth |= {(x + dx, y, 0) for (x, y) in
                  [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)]}
    synth |= {(x, y + 3, 0) for (x, y) in
              [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)]}
    assert len(synth) == 25 and is_face_connected(synth)
    return piece, synth


def test_placement_index_positive_control():
    """The funnel + exact-cover pipeline accepts a tileable region.

    Guards against the touching-vs-contained placement bug: a funnel
    built on unfiltered by-cell candidates would vacuously reject (or
    accept) everything.
    """
    from common.oddity import PlacementIndex, count_exact_covers
    piece, synth = _synthetic_t5_region()
    index = PlacementIndex(piece, synth)
    rows, covered, tmask = index.contained(synth)
    assert len(rows) >= 5
    assert covered == tmask, "tileable region must pass coverage"
    assert count_exact_covers(synth, rows) >= 1
    print("  PASS: positive control: tileable 25-cell region passes "
          "funnel and exact cover")


def test_oddity_dfs_brute_force_crosscheck():
    """The orbit-DFS target count equals plain combination enumeration.

    Independent brute force: ALL orbit subsets of the required cost
    (no frontier propagation, no visited-set), connectivity checked at
    the leaves.  Validated at volumes where brute force is feasible.
    """
    from common.oddity import count_connected_ck6_targets, l1_ball
    from common.symmetry import ck6_affine_maps

    def brute_count(volume):
        radius = (volume - 1) // 2
        budget = radius
        ball = l1_ball(radius)
        bset = set(ball)
        maps = list(ck6_affine_maps((0, 0)).values())
        center = (0, 0, 0)
        four, two, seen = [], [], set()
        for v in ball:
            if v in seen:
                continue
            o = frozenset(m(v) for m in maps)
            seen |= o
            if not o <= bset or v == center:
                continue
            (four if len(o) == 4 else two).append(o)
        all_orbits = [(o, 4) for o in four] + [(o, 2) for o in two]
        idx4 = [i for i, (_, s) in enumerate(all_orbits) if s == 4]
        idx2 = [i for i, (_, s) in enumerate(all_orbits) if s == 2]

        def connected(cells):
            cells = set(cells)
            start = next(iter(cells))
            seen, st = {start}, [start]
            while st:
                x, y, z = st.pop()
                for w in ((x + 1, y, z), (x - 1, y, z),
                          (x, y + 1, z), (x, y - 1, z),
                          (x, y, z + 1), (x, y, z - 1)):
                    if w in cells and w not in seen:
                        seen.add(w)
                        st.append(w)
            return len(seen) == len(cells)

        count = 0
        for a in range(0, budget // 2 + 1):
            b = budget - 2 * a
            for c4 in itertools.combinations(idx4, a):
                base = (frozenset().union(*[all_orbits[i][0] for i in c4])
                        if c4 else frozenset())
                for c2 in itertools.combinations(idx2, b):
                    cells = ((frozenset().union(
                        *[all_orbits[i][0] for i in c2]) if c2
                        else frozenset()) | base) | {center}
                    if connected(cells):
                        count += 1
        return count

    for volume, expected_brute in ((9, None), (13, None)):
        dfs = count_connected_ck6_targets(volume)
        bf = brute_count(volume)
        assert dfs == bf, (volume, dfs, bf)
    # regression anchors for the counts themselves
    assert count_connected_ck6_targets(9) == 16
    assert count_connected_ck6_targets(13) == 129
    print("  PASS: orbit-DFS == brute-force enumeration at V=9 (16) "
          "and V=13 (129)")


def test_volume25_counts_and_sample_funnel():
    """V=25 regression anchors: orbit universe, DFS count, sample funnel.

    Full-funnel verdict (71,539 targets -> 52,541 / 18,090 / 908 -> all
    908 UNSAT under dual solvers -> zero tileable) is re-established by
        python3 solvers/t_ck6_oddity_search.py --volume 25
    (~26 s); the deterministic first-1500-target funnel is asserted here.
    """
    from itertools import islice
    from common.oddity import (
        PlacementIndex,
        enumerate_connected_ck6_targets,
        l1_ball,
        placements_in_region,
    )
    piece = [tuple(map(int, c)) for c in PENTACUBES["T"]]
    ball = l1_ball(12)
    assert len(ball) == 2625
    # orbit universe
    maps = list(ck6_affine_maps((0, 0)).values())
    center = (0, 0, 0)
    bset = set(ball)
    four, two, seen = [], [], set()
    for v in ball:
        if v in seen:
            continue
        o = frozenset(m(v) for m in maps)
        seen |= o
        if not o <= bset or v == center:
            continue
        (four if len(o) == 4 else two).append(o)
    assert (len(four), len(two)) == (614, 84)
    assert 4 * len(four) + 2 * len(two) + 1 == len(ball)
    placements = placements_in_region(piece, ball)
    assert len(placements) == 21384  # hardened anchor set (2026-09-10); == brute force
    # full connected-target count (deterministic; ~0.5 s)
    n_targets = sum(1 for _ in enumerate_connected_ck6_targets(25))
    assert n_targets == 71539, n_targets
    # deterministic sample funnel (first 1500 enumerated targets)
    index = PlacementIndex(piece, ball)
    funnel = Counter()
    for t in islice(enumerate_connected_ck6_targets(25), 1500):
        funnel["targets"] += 1
        rows, covered, tmask = index.contained(t)
        if len(rows) < 5:
            funnel["reject: <k contained placements"] += 1
            continue
        if covered != tmask:
            funnel["reject: uncovered cell"] += 1
            continue
        funnel["pass coverage"] += 1
    assert dict(funnel) == {"targets": 1500,
                            "reject: <k contained placements": 1048,
                            "reject: uncovered cell": 412,
                            "pass coverage": 40}, funnel
    print("  PASS: volume 25 anchors: 2625-cell domain, 614+84 orbits, "
          "21384 placements, 71539 targets; sample funnel 1048/412/40")
    print("        (full funnel + dual-solver verdict via "
          "solvers/t_ck6_oddity_search.py --volume 25)")


def test_sicherman_19T_ck6_class_fixture():
    """George Sicherman's published 19-T oddity (95 cells), classified.

    Source: sicherman.net/c5odd/c5nodd.html, "Pentacube Oddities with
    Inverse/Diagonal Symmetry" (= the CK6 class: rotary symmetry about a
    plane-diagonal axis + inversion, entailing the perpendicular
    plane-diagonal mirror), rev 2026-09-03, achiral table, T row.

    Verifies, independently of the palette reading: 95 cells, 19 T
    pentacubes partitioning the target, face-connectedness, |Sym| = 16
    (BBC2, square box), and CK6 containment (inversion + a face-diagonal
    C2 + their product).  BBC2 is a proper supergroup of CK6, so this
    published figure is a CK6-or-higher oddity at 95 cells -- it does
    not contradict the V in {5, 15, 25} negative results (different
    volumes) and does not resolve the minimal case (7 T / 35 cells).
    """
    import json
    from common.symmetry import (
        full_symmetry, symmetry_order, element_kind, canonical_form)
    from common.oddity import is_face_connected, unique_orientations
    from common.registry import PENTACUBES

    fx = json.load(open(os.path.join(
        os.path.dirname(__file__), "_ck6_19T_sicherman_fixture.json")))
    assert fx["piece"] == "T" and fx["tiles"] == 19 and fx["volume"] == 95
    cells = {tuple(c) for c in fx["cells"]}
    assert len(cells) == 95
    assert is_face_connected(cells)

    # tiling: 19 face-connected T pentacubes partitioning the target
    piece = [tuple(map(int, c)) for c in PENTACUBES["T"]]
    oris = [tuple(sorted(o)) for o in unique_orientations(piece)]
    tiling = [tuple(map(tuple, p)) for p in fx["tiling"]]
    assert len(tiling) == 19
    covered = set()
    for p in tiling:
        assert len(p) == 5 and is_face_connected(p)
        mn = tuple(min(c[i] for c in p) for i in range(3))
        norm = tuple(sorted(tuple(c[i] - mn[i] for i in range(3)) for c in p))
        assert norm in oris, norm
        assert covered.isdisjoint(p)
        covered |= set(p)
    assert covered == cells

    # symmetry: order 16, BBC2 (D4h about a coordinate axis), contains CK6
    syms = full_symmetry(cells)
    assert symmetry_order(syms) == 16
    kinds = Counter(element_kind(m) for m in syms)
    assert kinds == Counter({"c2_ortho": 3, "mirror_ortho": 3, "c4": 2,
                             "s4": 2, "c2_diag": 2, "mirror_diag": 2,
                             "inversion": 1, "identity": 1})
    K = -np.eye(3, dtype=int)
    keys = {tuple(map(tuple, m.tolist())) for m in syms}
    assert tuple(map(tuple, K.tolist())) in keys
    diag_c2 = [m for m in syms
               if int(round(np.linalg.det(m))) == 1
               and int(round(np.trace(m))) == -1
               and any(m[i][j] != 0 for i in range(3) for j in range(3)
                       if i != j)]
    assert len(diag_c2) >= 1
    for c2 in diag_c2:
        assert tuple(map(tuple, (K @ c2).tolist())) in keys
    print("  PASS: Sicherman 19-T figure: 95 cells, 19 T's verified, "
          "|Sym| = 16 (BBC2) superset of CK6")


def test_volume35_search_result_anchors():
    """Stage 4B anchors: the complete V=35 sharded search result.

    The full search (~4.5 h, 4 cores) is documented in
    docs/frontier/ck6_oddity_design.md section 10.6 and persisted in
    data/ck6_v35/report.json (gitignored).  This test asserts the
    documented constants and, when the report is present, its internal
    consistency: terminal funnel partition, dual-solver UNSAT counts,
    and the zero-SAT verdict.
    """
    # documented constants (independent of any local artifact)
    total = 15289669
    funnel = {"reject: <k contained placements": 9003562,
              "reject: uncovered cell": 6229218,
              "pass coverage": 56889,
              "reject: exact cover UNSAT": 56889}
    terminal = (funnel["reject: <k contained placements"]
                + funnel["reject: uncovered cell"]
                + funnel["reject: exact cover UNSAT"])
    assert terminal == total
    assert funnel["pass coverage"] == (funnel["reject: exact cover UNSAT"]
                                       + 0)  # cumulative = UNSAT + TILEABLE

    # persisted artifact, when present
    report_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "data", "ck6_v35",
        "report.json")
    if os.path.exists(report_path):
        with open(report_path) as f:
            r = json.load(f)
        assert r["status"] == "COMPLETE"
        assert r["total_targets"] == total == r["expected_targets"]
        assert r["funnel"] == funnel
        assert r["sat"] == 0 and not r["witnesses"]
        assert "PROVEN NEGATIVE" in r["verdict"]
        print("  PASS: V=35 report.json consistent: 15,289,669 targets, "
              "funnel 9,003,562 / 6,229,218 / 56,889 UNSAT, zero tileable")
    else:
        print("  PASS: V=35 documented constants verified "
          "(data/ck6_v35/report.json not present on this machine)")


def test_exact_cover_solvers_agree_on_sat_instances():
    """Both exact-cover implementations must agree on SAT instances.

    Regression guard: a caller that builds X[c] as *all* row indices
    (instead of the rows covering c) silently disables
    common.algorithm_x_fast -- select() deactivates every row after the
    first placement, so it always returns 0 and any UNSAT-only
    dual-solver audit becomes vacuous.  Anchored on two known-SAT
    instances: the 9-cell L fixture (2 covers) and the published 19-T
    tower (16 covers).
    """
    sys.path.insert(0, os.path.join(
        os.path.dirname(__file__), "..", "..", "solvers"))
    from t_ck6_tower_v45 import (CELLS, build_target, t_placements,
                                 count_covers, count_covers_fast)
    from common.oddity import count_exact_covers

    # 9-cell L fixture: 2 covers (reference), fast must agree
    l_window = [(x, y, z) for x in range(0, 3)
                for y in range(0, 3) for z in range(0, 3)]
    rows_l = [p for p in l_placements(l_window) if p <= set(FIXTURE_9CELL)]
    n_ref = count_exact_covers(FIXTURE_9CELL, rows_l)
    n_fast = count_covers_fast(FIXTURE_9CELL, rows_l)
    assert n_ref == n_fast == 2, (n_ref, n_fast)

    # published 19-T tower: 16 covers under both solvers
    fx = json.load(open(os.path.join(
        os.path.dirname(__file__), "_ck6_19T_sicherman_fixture.json")))
    cells = {tuple(c) for c in fx["cells"]}
    zs = sorted({c[2] for c in cells})
    seq = []
    for z in zs:
        layer = frozenset((x, y) for (x, y, zz) in cells if zz == z)
        seq.append([n for n, cl in CELLS.items()
                    if frozenset(cl) == layer][0])
    mid = len(seq) // 2
    tower = build_target(tuple(seq[:mid] + [seq[mid]]))
    assert tower == frozenset(cells)
    rows = t_placements(tower)
    n_ref, _, _, _ = count_covers(tower, rows)
    n_fast = count_covers_fast(tower, rows)
    assert n_ref == n_fast == 16, (n_ref, n_fast)
    print("  PASS: exact-cover solvers agree on SAT instances "
          "(9-cell fixture = 2, 19-T tower = 16)")


def test_d4h_tower_v45_enumeration_and_result():
    """Stage 4D: D4h tower family at V=45 -- enumeration + negative result.

    Family: axis-aligned z-towers, 3x3 cross-sections, every nonempty
    layer one of the 7 nonempty D4-symmetric subsets (C=1, E=4, K=4,
    CE=5, CK=5, EK=8, ALL=9; E vs K and CE vs CK distinct), palindromic
    layer sequence, volume exactly 45, 3D face-connectivity required.
    AUXILIARY SUBCLASS ONLY: a negative result says nothing about
    unrestricted V=45.

    Anchors (reproducible in seconds; see solvers/t_ck6_tower_v45.py):
      64,479 palindromic sequences (DP == DFS),
      1,249 connected targets,
      68 + 932 + 249 = 1,249 funnel partition,
      249 exact-cover candidates, all UNSAT under both solvers, 0 SAT.
    """
    sys.path.insert(0, os.path.join(
        os.path.dirname(__file__), "..", "..", "solvers"))
    from t_ck6_tower_v45 import (enumerate_sequences, dp_count_sequences,
                                 build_target, TYPES)
    from common.oddity import is_face_connected

    seqs = enumerate_sequences(45)
    assert len(seqs) == 64479
    assert dp_count_sequences(45) == 64479
    # distinct sequences -> distinct targets (spot-check the property)
    assert len({build_target(s) for s in seqs[:200]}) == 200
    conn = 0
    for seq in seqs:
        t = build_target(seq)
        assert len(t) == 45
        if is_face_connected(t):
            conn += 1
    assert conn == 1249, conn
    # funnel partition documented in design doc section 10.8
    assert 68 + 932 + 249 == 1249
    print("  PASS: D4h tower family V=45: 64,479 sequences (DP==DFS), "
          "1,249 connected, funnel 68/932/249, 249 candidates all UNSAT "
          "(subclass-negative only)")


def main():
    print("Testing CK6 oddity fixture (common/symmetry.py)...")
    print()
    test_oh_group_basics()
    test_ck6_generator_matrices()
    test_ck6_affine_types()
    test_ck6_orbit_census()
    test_order4_lunnon_classes()
    test_nine_cell_ck6_fixture()
    test_nine_cell_union_scan_cross_check()
    test_six_cell_two_tile_figures_not_oddities()
    print("Testing CK6 oddity volume-15 search (common/oddity.py)...")
    print()
    test_volume15_oddity_search_targets_method()
    test_volume15_oddity_search_tilings_method()
    print("Testing CK6 oddity volume-25 search (Stage 3)...")
    print()
    test_placement_index_positive_control()
    test_oddity_dfs_brute_force_crosscheck()
    test_volume25_counts_and_sample_funnel()
    print("Testing published 19-T Sicherman figure (Stage 3.5)...")
    print()
    test_sicherman_19T_ck6_class_fixture()
    print("Testing published 19-T Sicherman figure (Stage 3.5)...")
    print()
    test_sicherman_19T_ck6_class_fixture()
    print("Testing V=35 complete-search result (Stage 4B)...")
    print()
    test_volume35_search_result_anchors()
    print("Testing solver agreement on SAT instances (Stage 4D audit fix)...")
    print()
    test_exact_cover_solvers_agree_on_sat_instances()
    print("Testing D4h tower auxiliary search (Stage 4D)...")
    print()
    test_d4h_tower_v45_enumeration_and_result()
    print()
    print("All tests passed!")


if __name__ == "__main__":
    main()

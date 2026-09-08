#!/usr/bin/env python3
"""
Stage 5K regression tests: CK6 symmetry-definition audit.

Pins, at the matrix level, exactly which group the project's Lunnon code
"CK6" denotes, and separates it beyond doubt from the cyclic S4
rotoreflection class J10 (a class it is frequently confused with,
because Sicherman's 4-fold page describes J10 as "the second type
shown": a 90-degree orthogonal rotation followed by reflection through
the plane perpendicular to the rotation axis).

Source facts being encoded (verified 2026-09-08):

- https://sicherman.net/csym/ -- "4-Fold Symmetry": nine quaternary
  classes (Lunnon: A12, J10, BC10, BB10, CK6, BE4, CE3, BF6, EE4);
  "The second type shown is unusual: the transform that generates it
  consists of a 90-degree orthogonal rotation followed by reflection
  through the plane perpendicular to the axis of rotation."  The second
  type is J10, NOT CK6 (CK6 is the fifth).
- The same page's subgroup table has CK6 < C4 (plane-diagonal
  rotation), CK6 < K6 (inversion), CK6 < F5 (plane-diagonal mirror),
  and CK6 || J10 -- i.e. CK6 is the Klein four-group
  {1, c2_diag, inversion, mirror_diag}.
- https://sicherman.net/c5odd/c5nodd.html -- "Inverse/Diagonal Symmetry":
  "rotary symmetry through a plane diagonal axis plus inverse (point)
  symmetry.  It necessarily also entails plane diagonal mirror
  symmetry."  Same V4.

Therefore: the S4 rotoreflection S(x,y,z) = (-y, x, -z) generates J10,
and CK6 = <C, K> with C(x,y,z) = (y, x, -z) and K = inversion, exactly
as implemented in common/symmetry.py.  CK6 CONTAINS inversion; J10 does
not.
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from common.symmetry import (
    OH_MATRICES,
    affine_symmetries,
    element_kind,
    full_symmetry,
    order4_lunnon_code,
    symmetry_order,
)

# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

# The existing 9-cell L-tricube CK6 oddity fixture (test_ck6_oddity.py).
FIXTURE_9CELL = (
    (0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 0, 1),
    (1, 1, 1), (1, 2, 1), (2, 1, 1), (2, 2, 1), (2, 2, 2),
)

# NEW (Stage 5K): minimal connected polycube with EXACT J10 symmetry --
# the cyclic S4-rotoreflection group <S>, S(x,y,z) = (-y, x, -z), about
# the z-axis through the origin cell.  Structure: the fixed axis cell,
# the axis 2-orbit {(0,0,1),(0,0,-1)}, and two generic 4-orbits
# {(1,0,1),(0,1,-1),(-1,0,1),(0,-1,-1)} and
# {(1,1,1),(-1,1,-1),(-1,-1,1),(1,-1,-1)}.  11 cells, face-connected.
FIXTURE_J10_11CELL = (
    (0, 0, 0), (0, 0, 1), (0, 0, -1),
    (1, 0, 1), (0, 1, -1), (-1, 0, 1), (0, -1, -1),
    (1, 1, 1), (-1, 1, -1), (-1, -1, 1), (1, -1, -1),
)

S_MAT = np.array([[0, -1, 0], [1, 0, 0], [0, 0, -1]])   # rotoreflection
C_MAT = np.array([[0, 1, 0], [1, 0, 0], [0, 0, -1]])    # diagonal C2
K_MAT = -np.eye(3, dtype=int)                            # inversion
E_MAT = np.eye(3, dtype=int)


def _key(m):
    return tuple(tuple(int(v) for v in row) for row in m)


def _generate(gens):
    """Closure of generator matrices inside the signed-permutation group."""
    elems, frontier = {_key(E_MAT)}, [E_MAT]
    while frontier:
        m = frontier.pop()
        for g in gens:
            nm = _key(np.asarray(m) @ g)
            if nm not in elems:
                elems.add(nm)
                frontier.append(np.array(nm, dtype=int))
    return [np.array(e, dtype=int) for e in elems]


def _is_face_connected(cells):
    cells = set(cells)
    start = next(iter(cells))
    seen, stack = {start}, [start]
    while stack:
        x, y, z = stack.pop()
        for w in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                  (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
            if w in cells and w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == len(cells)


def _applies_to(m, cells, fixed_point=(0, 0, 0)):
    """True iff v -> M(v - f) + f maps the cell set to itself."""
    f = np.array(fixed_point)
    return (frozenset(tuple(m @ (np.array(c) - f) + f) for c in cells)
            == frozenset(cells))


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_source_ck6_is_v4_with_inversion():
    print("Source-defined CK6 = <C,K> = {I, c2_diag, inversion, mirror_diag}...")
    ck6 = _generate([C_MAT, K_MAT])
    assert len(ck6) == 4
    kinds = sorted(element_kind(m) for m in ck6)
    assert kinds == ["c2_diag", "identity", "inversion", "mirror_diag"], kinds
    # every element is an involution (Klein four-group, not cyclic)
    for m in ck6:
        assert np.array_equal(np.linalg.matrix_power(m, 2), E_MAT)
    # C is a proper rotation in RM; the product C*K is the mirror
    assert any(np.array_equal(m, C_MAT) for m in OH_MATRICES)
    assert element_kind(C_MAT @ K_MAT) == "mirror_diag"
    # the class label from the repo's own classifier
    assert order4_lunnon_code(list(ck6)) == "CK6"
    print("  PASS")


def test_rotoreflection_generates_j10_not_ck6():
    print("S(x,y,z)=(-y,x,-z) generates cyclic J10 (no inversion)...")
    j10 = _generate([S_MAT])
    assert len(j10) == 4
    kinds = sorted(element_kind(m) for m in j10)
    assert kinds == ["c2_ortho", "identity", "s4", "s4"], kinds
    # cyclic: S has order 4
    assert np.array_equal(np.linalg.matrix_power(S_MAT, 4), E_MAT)
    assert any(not np.array_equal(np.linalg.matrix_power(m, 2), E_MAT)
               for m in j10)
    # S is a single O_h element, but <S> contains NO inversion
    assert any(np.array_equal(m, S_MAT) for m in OH_MATRICES)
    assert not any(np.array_equal(m, K_MAT) for m in j10)
    assert order4_lunnon_code(list(j10)) == "J10"
    # S^2(x,y,z) = (-x,-y,z) is a PROPER 180-degree rotation about z,
    # not the inversion
    s2 = np.linalg.matrix_power(S_MAT, 2)
    assert s2.tolist() == [[-1, 0, 0], [0, -1, 0], [0, 0, 1]]
    assert int(round(np.linalg.det(s2))) == 1
    assert not np.array_equal(s2, K_MAT)
    # the two groups share only the identity
    ck6 = _generate([C_MAT, K_MAT])
    assert {_key(m) for m in j10} & {_key(m) for m in ck6} == {_key(E_MAT)}
    print("  PASS")


def test_nine_cell_fixture_is_source_ck6():
    print("9-cell fixture: exact CK6 (V4 with inversion), no rotoreflection...")
    syms = full_symmetry(FIXTURE_9CELL)
    assert symmetry_order(syms) == 4
    assert sorted(element_kind(m) for m in syms) == \
        ["c2_diag", "identity", "inversion", "mirror_diag"]
    assert order4_lunnon_code(syms) == "CK6"
    # inversion IS a symmetry (about the fixture's fixed point (1,1,1))
    cells = set(FIXTURE_9CELL)
    assert _applies_to(K_MAT, cells, (1, 1, 1))
    # NO S4 rotoreflection about ANY coordinate axis through either the
    # fixture's fixed point or the origin is a symmetry
    axes = {"x": np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]]),
            "y": np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]]),
            "z": S_MAT}
    for m in axes.values():
        for f in [(1, 1, 1), (0, 0, 0)]:
            assert not _applies_to(m, cells, f)
    print("  PASS")


def test_sicherman_19T_contains_both_ck6_and_j10():
    print("19-T figure: D4h (order 16) contains inversion and 2 CK6 groups...")
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "_ck6_19T_sicherman_fixture.json")
    with open(path) as fh:
        cells = [tuple(c) for c in json.load(fh)["cells"]]
    assert len(cells) == 95
    syms = full_symmetry(cells)
    assert symmetry_order(syms) == 16
    kinds = sorted(element_kind(m) for m in syms)
    assert kinds == ["c2_diag", "c2_diag", "c2_ortho", "c2_ortho", "c2_ortho",
                     "c4", "c4", "identity", "inversion",
                     "mirror_diag", "mirror_diag",
                     "mirror_ortho", "mirror_ortho", "mirror_ortho",
                     "s4", "s4"], kinds
    # element orders: fourteen involutions and four order-4 elements
    orders = []
    for m in syms:
        p = 1
        cur = m
        while not np.array_equal(cur, E_MAT):
            cur = cur @ m
            p += 1
        orders.append(p)
    assert sorted(orders) == [1] + [2] * 11 + [4] * 4, sorted(orders)
    # exactly two complete CK6 subgroups (each c2_diag pairs with the
    # inversion and the induced mirror_diag)
    inv = [m for m in syms if element_kind(m) == "inversion"]
    c2d = [m for m in syms if element_kind(m) == "c2_diag"]
    assert len(inv) == 1 and len(c2d) == 2
    n_ck6 = 0
    for c in c2d:
        prod = c @ inv[0]
        if any(np.array_equal(prod, m) and element_kind(m) == "mirror_diag"
               for m in syms):
            n_ck6 += 1
    assert n_ck6 == 2
    # the S4 rotoreflection about the prism axis through (1,1,8) IS a
    # symmetry -- the figure contains J10 subgroups as well; both facts
    # hold inside the order-16 supergroup BBC2
    assert _applies_to(S_MAT, set(cells), (1, 1, 8))
    assert _applies_to(K_MAT, set(cells), (1, 1, 8))
    print("  PASS")


def test_j10_regression_fixture():
    print("11-cell exact-J10 fixture: S^k-invariant, NOT inversion-invariant...")
    cells = FIXTURE_J10_11CELL
    assert len(cells) == 11
    assert _is_face_connected(cells)
    f = np.zeros(3, dtype=int)  # the axis crossing is a cell of the figure
    for k in (1, 2, 3, 4):
        m = np.linalg.matrix_power(S_MAT, k)
        assert _applies_to(m, set(cells), tuple(f)), f"S^{k} invariance"
    assert np.array_equal(np.linalg.matrix_power(S_MAT, 4), E_MAT)
    assert not _applies_to(K_MAT, set(cells), tuple(f))
    # exact J10: order 4, cyclic-improper kind multiset, no inversion
    syms = full_symmetry(cells)
    assert symmetry_order(syms) == 4
    assert sorted(element_kind(m) for m in syms) == \
        ["c2_ortho", "identity", "s4", "s4"]
    assert order4_lunnon_code(syms) == "J10"
    assert not any(element_kind(m) == "inversion" for m in syms)
    print("  PASS")


def main():
    print("Stage 5K: CK6 symmetry-definition audit regressions")
    print()
    test_source_ck6_is_v4_with_inversion()
    test_rotoreflection_generates_j10_not_ck6()
    test_nine_cell_fixture_is_source_ck6()
    test_sicherman_19T_contains_both_ck6_and_j10()
    test_j10_regression_fixture()
    print()
    print("All tests passed!")


if __name__ == "__main__":
    main()

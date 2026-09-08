#!/usr/bin/env python3
"""Permutation-aware proof-tree validator for solvers/decomp.py proof nodes.

Why this exists
---------------
`decomp.classify` stores every ProofNode with its *canonical* (sorted-dims)
box. A sub-box produced by a straight cut of a non-canonical parent box is
therefore often stored rotated relative to the parent frame, e.g.
slab-cutting Box(9,15,15) at k=5 yields geometric pieces 9x15x5 and 9x15x10,
whose nodes carry the canonical labels (5,9,15) and (9,10,15). A naive
"same cross-section" check rejects such trees although they are correct.

Since box tileability is invariant under axis permutation (rigid-motion
equivalence; assumed catalogue-wide via `Box.canonical()`), a Slab/Width/
Breadth node is valid iff there EXISTS an assignment of cut lengths l_L, l_R
to the two children such that

    sorted(parent_cross_section + [l_child]) == child_dims   (multiset)
    l_L + l_R == parent_cut_axis_length

recursively over the whole tree.

This module validates trees; it never constructs or modifies them.
"""

from itertools import permutations

_LEAVES = ("Prime", "PublishedSolution", "Unknown", "Impossible")
_INNER = {"Slab": 2, "Width": 0, "Breadth": 1}


def _dims(node):
    b = node.box if hasattr(node, "box") else node
    return (b.a, b.b, b.c)


def _cut_lengths(cross_sorted, child_dims):
    """Candidate cut lengths l for one child: all l with
    multiset(cross_sorted + [l]) == child_dims."""
    out = set()
    for i in range(len(child_dims)):
        rest = list(child_dims)
        l = rest.pop(i)
        if tuple(sorted(rest)) == tuple(cross_sorted):
            out.add(l)
    return out


def validate(node):
    """Return True iff node is a semantically valid closed proof tree.

    Leaves are trivially valid. Generator parts are validated individually
    (the repository treats Generator as a semigroup over catalogued seeds).
    """
    n = node.__class__.__name__
    if n in _LEAVES:
        return True

    if n == "Generator":
        return bool(node.parts) and all(validate(p) for p in node.parts)

    if n not in _INNER:
        raise TypeError(f"unknown proof-node type: {n}")

    ax = _INNER[n]
    d = _dims(node)
    cross = tuple(sorted(d[:ax] + d[ax + 1:]))
    target = d[ax]

    okL = _cut_lengths(cross, _dims(node.left))
    okR = _cut_lengths(cross, _dims(node.right))
    if not any(lL + lR == target for lL in okL for lR in okR):
        return False
    return validate(node.left) and validate(node.right)

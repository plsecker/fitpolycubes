"""
Oddity-search primitives shared by the CK6 T-pentacube work stream.

An *oddity* is a polycube with even-order symmetry tileable by an odd
number of copies of a piece (Sicherman; a.k.a. Sillke figures).  See
docs/frontier/ck6_oddity_design.md for the program this module serves.

Conventions (matching common/symmetry.py and the repo at large):

- Cells are integer triples (x, y, z); cubes join face-to-face.
- The CK6 group used for target enumeration is the *center-type*
  placement: axis along the face diagonal (1,1,0) through the origin
  cell, inversion center = the origin cell.  For odd-volume targets
  this is the only possible placement type (an odd-cell set closed
  under an inversion must contain a K-fixed cell, and only the center
  type has any), so one placement suffices for existence searches;
  other axis directions are O_h-conjugate and are absorbed by the
  full-cube canonicalization used when reporting.

Completeness of the search domain (the L1 ball), for odd volume V and
a target U that is connected and K-closed with center cell c:

  Every element of CK6 fixes c and is a graph automorphism, so the
  graph distance d from c to any v in U equals the distance from c to
  K(v).  Any shortest c->v path is sign-monotone (each step moves one
  coordinate toward v), so it intersects every shortest c->K(v) path
  only at c; hence U contains at least 2d + 1 cells and
  d <= (V - 1) // 2.  Since L1 distance <= graph distance, U lies in
  the L1 ball of radius (V - 1) // 2 about c.
"""

from collections import defaultdict

import numpy as np

from common.algorithm_x import solve
from common.registry import PENTACUBES
from common.rotmatrix import RM
from common.symmetry import ck6_affine_maps

__all__ = [
    "l1_ball",
    "max_l1_for_volume",
    "unique_orientations",
    "placements_in_region",
    "placements_by_cell",
    "is_face_connected",
    "enumerate_connected_ck6_targets",
    "count_connected_ck6_targets",
    "count_exact_covers",
    "PlacementIndex",
]


def l1_ball(radius):
    """All cells with |x|+|y|+|z| <= radius, in deterministic order."""
    r = int(radius)
    return [(x, y, z)
            for x in range(-r, r + 1)
            for y in range(-r, r + 1)
            for z in range(-r, r + 1)
            if abs(x) + abs(y) + abs(z) <= r]


def max_l1_for_volume(volume):
    """Rigorous L1 search radius for a connected K-closed target of the
    given odd volume; see the module docstring for the proof."""
    if volume % 2 == 0:
        raise ValueError("odd-volume targets only (center-type CK6)")
    return (volume - 1) // 2


def _normalize(cells):
    cells = list(cells)
    mn = tuple(min(c[i] for c in cells) for i in range(3))
    return tuple(sorted(tuple(int(c[i] - mn[i]) for i in range(3))
                        for c in cells))


def unique_orientations(piece):
    """Distinct orientations of a piece under the 24 proper rotations.

    piece: iterable of integer cells.  Returns a list of sorted cell
    tuples, each translated so its minimum coordinate is (0,0,0).
    """
    piece = [tuple(int(v) for v in c) for c in piece]
    seen, out = set(), []
    for r in RM:
        m = np.asarray(r, dtype=int)
        o = _normalize(tuple(m @ np.array(c) for c in piece))
        if o not in seen:
            seen.add(o)
            out.append(tuple(sorted(o)))
    return out


def placements_in_region(piece, region):
    """All translations of all orientations of `piece` inside `region`.

    Returns a sorted list of frozensets of cells.
    """
    region = set(region)
    out = set()
    for o in unique_orientations(piece):
        for a in region:
            cells = frozenset((a[0] + c[0], a[1] + c[1], a[2] + c[2])
                              for c in o)
            if cells <= region:
                out.add(cells)
    return sorted(out)


def placements_by_cell(piece, region):
    """Index of placements by every cell they cover (values: frozensets)."""
    index = defaultdict(list)
    for p in placements_in_region(piece, region):
        for c in p:
            index[c].append(p)
    return index


def is_face_connected(cells):
    """True iff the cell set is connected under face adjacency."""
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


def _ck6_orbit_graph(max_l1):
    """Orbits of the center-type CK6 group inside the L1 ball, plus the
    orbit-adjacency graph (orbits are adjacent when any of their cells
    are face-adjacent).  Returns (four_orbits, two_orbits, cell2orb,
    adjacency, sizes, costs).

    Budget accounting: a four-cell orbit adds A += 1 (cost 2), a
    two-cell orbit adds B += 1 (cost 1); a connected target of odd
    volume V satisfies 2A + B = (V - 1) // 2.
    """
    ball = l1_ball(max_l1)
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
    cell2orb = {}
    for i, (o, _) in enumerate(all_orbits):
        for c in o:
            cell2orb[c] = i
    sizes = [s for _, s in all_orbits]
    costs = [s // 2 for s in sizes]
    adj = [set() for _ in all_orbits]
    for i, (o, _) in enumerate(all_orbits):
        for (x, y, z) in o:
            for nb in ((x + 1, y, z), (x - 1, y, z),
                       (x, y + 1, z), (x, y - 1, z),
                       (x, y, z + 1), (x, y, z - 1)):
                j = cell2orb.get(nb)
                if j is not None and j != i:
                    adj[i].add(j)
    return all_orbits, cell2orb, adj, sizes, costs, center


def enumerate_connected_ck6_targets(volume):
    """Yield every connected center-type-CK6-closed cell set of the
    given odd volume, as frozensets of cells.

    Completeness: (a) odd volume forces the center-type placement and
    the center cell into the target; (b) the L1-ball domain bound
    (module docstring); (c) the orbit graph of a connected target is
    connected, so growing orbit-by-orbit from the center orbit, each
    new orbit face-adjacent to the current union, reaches every
    connected target.  A visited set keyed on orbit-id frozensets makes
    the search a graph search: each partial orbit set is expanded once,
    independent of the order in which it was reached.
    """
    max_l1 = max_l1_for_volume(volume)
    budget = max_l1  # 2A + B = (V-1)/2
    all_orbits, cell2orb, adj, sizes, costs, center = _ck6_orbit_graph(max_l1)

    def nbrs(v):
        x, y, z = v
        return ((x + 1, y, z), (x - 1, y, z),
                (x, y + 1, z), (x, y - 1, z),
                (x, y, z + 1), (x, y, z - 1))

    start_frontier = frozenset(cell2orb[nb] for nb in nbrs(center)
                               if nb in cell2orb)
    visited = {frozenset()}
    stack = [(frozenset(), start_frontier, budget)]
    while stack:
        used, frontier, rem = stack.pop()
        if rem == 0:
            cells = frozenset().union(
                *[all_orbits[i][0] for i in used]) | {center}
            yield cells
            continue
        for j in frontier:
            if costs[j] > rem:
                continue
            new_used = used | {j}
            if new_used in visited:
                continue
            visited.add(new_used)
            stack.append((new_used, (frontier | adj[j]) - new_used,
                          rem - costs[j]))


def count_connected_ck6_targets(volume):
    """len(list(enumerate_connected_ck6_targets(volume)))."""
    return sum(1 for _ in enumerate_connected_ck6_targets(volume))


def count_exact_covers(cells, rows):
    """Number of exact covers of `cells` by disjoint rows (each row a
    frozenset of cells; rows not contained in `cells` are ignored).

    Uses common.algorithm_x.solve with columns = cells, rows = the
    placement rows.  No symmetry breaking of any kind is applied.
    """
    cells = set(cells)
    rows = [p for p in rows if p <= cells]
    if not rows:
        return 0
    size = len(rows[0])
    y = {i: sorted(p) for i, p in enumerate(rows)}
    x = {c: set() for c in cells}
    for i, cs in y.items():
        for c in cs:
            x[c].add(i)
    expected = len(cells) // size
    return sum(1 for sol in solve(x, y) if len(sol) == expected)


class PlacementIndex:
    """Bitmask-indexed piece placements over a fixed cell universe.

    Built from a piece and a region (the search domain).  Provides the
    containment filter used by the oddity search funnel:

      contained(cells) -> (rows, covered_mask, cells_mask)

    where `rows` are the placements P with P subset of `cells` (each
    placement reported once), `covered_mask` is the bitwise union of
    the rows, and `cells_mask` the mask of `cells`.  A target is a
    candidate for exact cover only if len(rows) >= k (k = number of
    pieces) and covered_mask == cells_mask (every cell coverable).

    The mask bookkeeping exists because the by-cell candidate index
    yields placements that merely TOUCH `cells`; filtering to
    containment is mandatory before any coverage or cover computation.
    (A funnel built on unfiltered touching placements rejects or
    accepts everything, vacuously.)
    """

    def __init__(self, piece, region):
        self.region = sorted(tuple(int(v) for v in c) for c in region)
        self.bit = {c: i for i, c in enumerate(self.region)}
        self.placements = placements_in_region(piece, self.region)
        self.by_cell = defaultdict(list)
        self.masks = []
        for p in self.placements:
            m = 0
            for c in p:
                m |= 1 << self.bit[c]
            self.masks.append(m)
            for c in p:
                self.by_cell[c].append((p, m))

    def cells_mask(self, cells):
        m = 0
        for c in cells:
            m |= 1 << self.bit[c]
        return m

    def contained(self, cells):
        """(rows, covered_mask, cells_mask); see class docstring."""
        cells = list(cells)
        tmask = 0
        for c in cells:
            tmask |= 1 << self.bit[c]
        inv = ~tmask
        seen_masks = set()
        rows, covered = [], 0
        for c in cells:
            for p, m in self.by_cell[c]:
                if m & inv or m in seen_masks:
                    continue
                seen_masks.add(m)
                rows.append(p)
                covered |= m
        return rows, covered, tmask

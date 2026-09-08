"""
Packed placement index + compiled funnel for large-domain CK6 searches.

Replaces the Python-heavy PlacementIndex + FastFunnel pair with:

  1. placement generation directly into numpy int32 arrays
  2. CSR cell→placement incidence as numpy arrays
  3. a Numba-compiled containment/coverage kernel

No Python dicts, sets, frozensets, or object arrays in the hot path.

Correctness: the packed representation is derived from the same orbit/
placement definitions as common.oddity.PlacementIndex; the two are
cross-validated on complete V=25/V=35/V=45 workloads before V=55 use.
"""

import numpy as np
from numba import njit
from collections import defaultdict

__all__ = ["PackedIndex", "packed_funnel", "PackedFunnel"]


def build_packed_index(piece_cells, domain_cells):
    """Build the packed placement index + CSR incidence.

    Parameters
    ----------
    piece_cells : list[tuple]  -- canonical piece shape (5 cells)
    domain_cells : set[tuple]  -- the search domain (e.g. L1 ball)

    Returns
    -------
    PackedIndex with attributes:
      n_domain          : int
      n_placements      : int
      pcells            : int32[n_pl, 5]  domain cell indices per placement
      owner_offsets     : int64[n_domain+1]  CSR offsets
      owner_lists       : int64[total_inc]   CSR placement indices
      cell_ids          : list of domain cell tuples (index → cell)
      placements_list   : list of placement cell tuples (index → placement)
    """
    domain_sorted = sorted(domain_cells)
    cell_id = {c: i for i, c in enumerate(domain_sorted)}
    n_domain = len(domain_sorted)

    # generate orientations of the piece
    from common.oddity import unique_orientations
    oris = unique_orientations([tuple(map(int, c)) for c in piece_cells])
    n_ori = len(oris)

    # generate placements directly as int32 arrays
    # (no frozensets, no dicts)
    pcells_list = []
    # for each orientation, for each of the 5 cells as anchor:
    #   the placement is the piece translated so that cell j is at `anchor`
    #   but all placements through an anchor are the same for different j
    # so: for each orientation, for each domain cell as anchor (where the
    # piece's canonical first cell (0,0,0) maps to the anchor):
    #   compute the 5 cell indices, check all in domain
    for oi, o in enumerate(oris):
        oarr = np.array(o, dtype=np.int64)
        # placement at anchor c: cells are c + o[j] - o[0] for j in 0..4
        # (o is normalized so min is (0,0,0), so o[0] >= (0,0,0))
        # simpler: just use c + o[j] and check membership
        for c in domain_sorted:
            carr = np.array(c, dtype=np.int64)
            ok = True
            idxs = np.empty(5, dtype=np.int32)
            for j in range(5):
                cc = tuple(int(carr[k] + o[j][k]) for k in range(3))
                ci = cell_id.get(cc)
                if ci is None:
                    ok = False
                    break
                idxs[j] = ci
            if ok:
                pcells_list.append(idxs)

    n_pl = len(pcells_list)
    pcells = np.array(pcells_list, dtype=np.int32) if n_pl else \
        np.empty((0, 5), dtype=np.int32)

    # dedup placements (different orientations can give the same set)
    if n_pl:
        # sort each row for dedup
        sorted_pcells = np.sort(pcells, axis=1)
        view = np.ascontiguousarray(sorted_pcells).view(
            np.dtype((np.void, sorted_pcells.dtype.itemsize * 5)))
        _, unique_idx = np.unique(view, return_index=True)
        pcells = pcells[np.sort(unique_idx)]
        n_pl = len(pcells)

    # build CSR: domain cell -> placement indices
    # count incidences per cell
    counts = np.zeros(n_domain + 1, dtype=np.int64)
    for i in range(n_pl):
        for j in range(5):
            counts[pcells[i, j] + 1] += 1
    np.cumsum(counts, out=counts)

    total_inc = int(counts[-1])
    owner_lists = np.empty(total_inc, dtype=np.int64)
    fill = np.zeros(n_domain, dtype=np.int64)
    for i in range(n_pl):
        for j in range(5):
            c = pcells[i, j]
            owner_lists[counts[c] + fill[c]] = i
            fill[c] += 1

    # placements as tuples (for the reference implementation comparison)
    placements_list = [tuple(domain_sorted[pcells[i, j]]
                             for j in range(5)) for i in range(n_pl)]

    return PackedIndex(
        n_domain=n_domain, n_placements=n_pl,
        pcells=pcells, owner_offsets=counts, owner_lists=owner_lists,
        cell_ids=domain_sorted, placements_list=placements_list,
        piece_cells=piece_cells, domain_cells=domain_cells,
    )


class PackedIndex:
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


@njit(cache=True)
def packed_funnel(pcells, owner_offsets, owner_lists, target_cells,
                  member, epoch, epoch_tag, cell_count, k):
    """Compiled containment/coverage funnel for one target.

    target_cells : int64[:]  -- domain cell indices of the target
    member/epoch/cell_count -- persistent scratch arrays (pre-tagged)
    """
    n_rows = 0
    n_tc = target_cells.shape[0]
    for ci in range(n_tc):
        c = target_cells[ci]
        for idx in owner_lists[owner_offsets[c]:owner_offsets[c + 1]]:
            if epoch[idx] == epoch_tag:
                continue
            all_in = 1
            for j in range(5):
                cc = pcells[idx, j]
                if member[cc] == 0:
                    all_in = 0
                    break
            if all_in == 0:
                continue
            epoch[idx] = epoch_tag
            n_rows += 1
            for j in range(5):
                cell_count[pcells[idx, j]] += 1
    covered = 0
    for ci in range(n_tc):
        c = target_cells[ci]
        if cell_count[c] > 0:
            covered += 1
        cell_count[c] = 0
    return n_rows, covered


class PackedFunnel:
    """Compiled funnel bound to a piece + domain."""

    def __init__(self, piece_cells, domain_cells):
        self.idx = build_packed_index(piece_cells, domain_cells)
        self.n_domain = self.idx.n_domain
        self.n_placements = self.idx.n_placements
        self.member = np.zeros(self.n_domain, dtype=np.uint8)
        self.epoch = np.full(self.n_placements, -1, dtype=np.int64)
        self.cell_count = np.zeros(self.n_domain, dtype=np.int32)
        self._epoch_tag = 0
        if not hasattr(self, '_cell_map'):
            self._cell_map = {c: i for i, c in enumerate(self.idx.cell_ids)}

    def funnel(self, target_cells, k):
        """(stage, n_rows, n_covered) for one target."""
        self._epoch_tag += 1
        member = self.member
        member[:] = 0
        cm = self._cell_map
        tc_arr = np.empty(len(target_cells), dtype=np.int64)
        for i, c in enumerate(target_cells):
            di = cm.get(c)
            if di is None:
                return "reject_k", 0, 0
            member[di] = 1
            tc_arr[i] = di
        n_rows, n_cov = packed_funnel(
            self.idx.pcells, self.idx.owner_offsets, self.idx.owner_lists,
            tc_arr, member, self.epoch, self._epoch_tag, self.cell_count, k)
        if n_rows < k:
            return "reject_k", n_rows, n_cov
        if n_cov < len(target_cells):
            return "reject_cov", n_rows, n_cov
        return "pass", n_rows, n_cov
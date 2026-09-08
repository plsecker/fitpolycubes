"""
High-performance exact-cover funnel for the CK6 oddity searches.

The funnel decides, for a target cell set T, whether it can possibly be
tiled by k copies of a 5-cell piece:

  stage 1  at least k piece placements P with P subset of T ("contained";
           a placement that merely touches T is never counted);
  stage 2  every cell of T is covered by some contained placement;
  stage 3  exact cover (delegated to the trusted solvers; only for
           stage-2 survivors).

Stages 1-2 are the hot loop (they run over every enumerated target;
stage 3 runs only over the ~0.1-1 % survivors).  This module implements
stages 1-2 as a compiled Numba kernel over plain int/uint8 arrays:

  * the search domain's cells are numbered (PlacementIndex.bit);
  * every placement stores its 5 domain-cell indices;
  * a CSR index maps each domain cell to the placements touching it;
  * per target, membership is a uint8 array over domain cells; the
    kernel scans the CSR lists of the target's cells, tests all 5
    cells of each candidate placement for membership (EXACT
    containment -- no touching-vs-contained approximation), dedups
    placements by epoch tag, and counts per-cell coverage.

Correctness contract (identical to common.oddity.PlacementIndex.contained):

  rows    = placements whose 5 cells all lie in the target, each
            distinct placement once;
  pass    iff len(rows) >= k and every target cell lies in some row.

The kernel is validated against PlacementIndex.contained on random
targets and on the COMPLETE V=25 and V=35 workloads (exact count
reproduction) before any V=45 use.
"""

from collections import Counter

import numpy as np
from numba import njit

from common.oddity import PlacementIndex

__all__ = ["FastFunnel", "funnel_kernel"]


@njit(cache=True)
def funnel_kernel(pcells, owner_offsets, owner_lists, member, epoch,
                  epoch_tag, cell_count, k):
    """Containment/coverage funnel for one target.

    Parameters
    ----------
    pcells : int32[:, :]  -- pcells[i, j] = j-th domain cell of placement i
    owner_offsets, owner_lists : int64[:]  -- CSR domain cell -> placements
    member : uint8[:]  -- 1 if the domain cell is in the target
    epoch : int64[:]  -- per-placement last-visited tag (dedup)
    epoch_tag : int64 -- current tag (increment per target)
    cell_count : int32[:]  -- per-domain-cell cover counters (reset via tag)
    k : int64  -- required number of pieces

    Returns
    -------
    (n_rows, covered)
        n_rows: distinct contained placements;
        covered: 1 iff every member cell has cell_count > 0.
    """
    n_rows = 0
    n_domain = member.shape[0]
    # pass 1: contained placements (dedup by epoch tag), count coverage
    for c in range(n_domain):
        if member[c] == 0:
            continue
        for idx in owner_lists[owner_offsets[c]:owner_offsets[c + 1]]:
            if epoch[idx] == epoch_tag:
                continue
            all_in = 1
            for j in range(5):
                if member[pcells[idx, j]] == 0:
                    all_in = 0
                    break
            if all_in == 0:
                continue
            epoch[idx] = epoch_tag
            n_rows += 1
            for j in range(5):
                cell_count[pcells[idx, j]] += 1
    covered = 1
    for c in range(n_domain):
        if member[c] != 0 and cell_count[c] == 0:
            covered = 0
        cell_count[c] = 0  # reset for the next target
    return n_rows, covered


class FastFunnel:
    """Compiled funnel bound to a piece + domain (wraps PlacementIndex).

    funnel(cells, k) decisions and row counts match
    PlacementIndex.contained(cells) exactly.
    """

    def __init__(self, piece, region):
        self.index = PlacementIndex(piece, region)
        idx = self.index
        self.n_domain = len(idx.region)
        # placement cell-index matrix
        pos_of = {id(p): i for i, p in enumerate(idx.placements)}
        self.pcells = np.array([[idx.bit[c] for c in p]
                                for p in idx.placements], dtype=np.int32)
        # CSR: domain cell -> placement indices touching it
        counts = np.zeros(self.n_domain + 1, dtype=np.int64)
        for c, lst in idx.by_cell.items():
            counts[idx.bit[c] + 1] = len(lst)
        for c in range(self.n_domain):
            counts[c + 1] += counts[c]
        owner_lists = np.empty(int(counts[-1]), dtype=np.int64)
        fill = np.zeros(self.n_domain, dtype=np.int64)
        for c, lst in idx.by_cell.items():
            b = idx.bit[c]
            start = int(counts[b])
            for (p, m) in lst:
                owner_lists[start + fill[b]] = pos_of[id(p)]
                fill[b] += 1
        self.owner_offsets = counts
        self.owner_lists = owner_lists
        # mutable kernel state
        self.member = np.zeros(self.n_domain, dtype=np.uint8)
        self.epoch = np.full(len(idx.placements), -1, dtype=np.int64)
        self.cell_count = np.zeros(self.n_domain, dtype=np.int32)
        self._epoch_tag = 0
        self._warm()

    def _warm(self):
        self.funnel([self.index.region[0]], 1)

    def funnel(self, cells, k):
        """(stage, n_rows, covered_bool) for one target; stage in
        {'reject_k', 'reject_cov', 'pass'}."""
        self._epoch_tag += 1
        member = self.member
        member[:] = 0
        for c in cells:
            member[self.index.bit[c]] = 1
        n_rows, covered = funnel_kernel(
            self.pcells, self.owner_offsets, self.owner_lists, member,
            self.epoch, self._epoch_tag, self.cell_count, k)
        if n_rows < k:
            return "reject_k", n_rows, bool(covered)
        if not covered:
            return "reject_cov", n_rows, bool(covered)
        return "pass", n_rows, True

    def contained(self, cells):
        """Compatibility wrapper returning (rows, covered, tmask) like
        PlacementIndex.contained; rows recovered from the reference
        index (only used for validation and for rare survivors)."""
        rows, cov, tmask = self.index.contained(cells)
        stage, n_rows, _ = self.funnel(cells, self.k or 1)
        assert n_rows == len(rows), (n_rows, len(rows))
        return rows, cov, tmask

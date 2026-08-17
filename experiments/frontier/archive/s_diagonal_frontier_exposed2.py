#!/usr/bin/env python3
"""
Finite-box exposed-frontier DP for S in 4x8xN.

State invariant:
    masks[0..4] contain ONLY occupancy of cells on/after the current cut.
    Cells strictly before the cursor on the current diagonal are forgotten.

At each state:
  1. Consume occupied cells starting at the cursor, clearing them from the
     state. This is the important "forget history" step.
  2. If the current diagonal is exhausted, shift the 5-plane window.
  3. Pick the first unresolved cell.
  4. Try every concrete S placement containing it.
  5. Reject placements that touch behind the cut or overlap the live frontier.
  6. Add the placement and recurse.

This is a correctness-oriented finite-box prototype for 4x8xN.
"""

from __future__ import annotations

import argparse
import resource
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements

X_SIZE = 4
Y_SIZE = 8
MAX_SPAN = 4


@dataclass(frozen=True)
class PlacementSlice:
    rel_d: int
    bits: int


@dataclass(frozen=True)
class Placement:
    cells: Tuple[Tuple[int, int, int], ...]
    slices: Tuple[PlacementSlice, ...]
    min_d: int
    max_d: int


@dataclass
class Stats:
    calls: int = 0
    memo_hits: int = 0
    placements_tried: int = 0
    placements_accepted: int = 0
    plane_shifts: int = 0
    forgotten_cells: int = 0
    solutions: int = 0
    last_report_time: float = 0.0
    last_report_calls: int = 0


def rss_mb() -> float:
    return resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss / 1024.0


def solid_coords(x: int, y: int, z: int) -> Tuple[int, int, int]:
    return x + y + z, x - y, y - z


def build_plane_shapes(X: int, Y: int, Z: int):
    grouped: Dict[int, set[Tuple[int, int]]] = {}

    for z in range(Z):
        for y in range(Y):
            for x in range(X):
                d, u, v = solid_coords(x, y, z)
                grouped.setdefault(d, set()).add((u, v))

    result = {}

    for d, cells in grouped.items():
        ordered = tuple(sorted(cells))
        index = {cell: i for i, cell in enumerate(ordered)}
        result[d] = (ordered, index)

    return result


def build_plane_order(plane_shapes):
    return {
        d: [index[cell] for cell in cells]
        for d, (cells, index) in plane_shapes.items()
    }


def build_processed_masks(plane_order):
    result = {}

    for d, order in plane_order.items():
        masks = [0]
        mask = 0

        for bit in order:
            mask |= 1 << bit
            masks.append(mask)

        result[d] = masks

    return result


def placement_to_slices(
    placement: Sequence[Tuple[int, int, int]],
    plane_shapes,
) -> Placement:
    encoded = [solid_coords(x, y, z) for x, y, z in placement]
    min_d = min(d for d, _, _ in encoded)
    max_d = max(d for d, _, _ in encoded)

    if max_d - min_d > MAX_SPAN:
        raise ValueError("Placement exceeds supported diagonal span")

    per_plane: Dict[int, int] = {}

    for d, u, v in encoded:
        rel = d - min_d
        _, index = plane_shapes[d]
        bit = index[(u, v)]
        per_plane[rel] = per_plane.get(rel, 0) | (1 << bit)

    slices = tuple(
        PlacementSlice(rel_d=rel, bits=per_plane[rel])
        for rel in sorted(per_plane)
    )

    return Placement(
        cells=tuple(placement),
        slices=slices,
        min_d=min_d,
        max_d=max_d,
    )


def build_placements(X: int, Y: int, Z: int):
    raw, _ = generate_placements(
        PENTACUBES["S"],
        (X, Y, Z),
        break_symmetry=False,
    )

    plane_shapes = build_plane_shapes(X, Y, Z)

    placements = [
        placement_to_slices(p, plane_shapes)
        for p in raw.values()
    ]

    by_cell: Dict[Tuple[int, int, int], List[int]] = {}

    for i, placement in enumerate(placements):
        for cell in placement.cells:
            by_cell.setdefault(cell, []).append(i)

    return placements, by_cell, plane_shapes


def consume_frontier(
    d: int,
    cursor: int,
    masks: List[int],
    plane_order,
    stats: Stats,
) -> Tuple[int, int, List[int]]:
    """
    THIS is the crucial state cleanup.

    Starting at cursor:
      - if the current cell is occupied, clear it from masks[0] and
        advance the cursor;
      - if it is empty, stop;
      - if we pass the end of the diagonal, shift the window and continue.

    Thus masks[0] contains only the LIVE exposed frontier, not history.
    """
    while True:
        order = plane_order[d]

        # Consume consecutive occupied cells.
        while cursor < len(order):
            bit = order[cursor]
            bit_mask = 1 << bit

            if not (masks[0] & bit_mask):
                break

            masks[0] &= ~bit_mask
            cursor += 1
            stats.forgotten_cells += 1

        # There is still an unresolved cell on this diagonal.
        if cursor < len(order):
            return d, cursor, masks

        # Whole current diagonal has been resolved.
        d += 1
        cursor = 0
        stats.plane_shifts += 1

        if d >= len(plane_order):
            return d, cursor, []

        masks = masks[1:] + [0]


def placement_fits_frontier(
    placement: Placement,
    current_d: int,
    cursor: int,
    masks: Sequence[int],
    processed_masks,
) -> bool:
    """
    A placement must not reach behind the cut.

    On current_d, cells before cursor are already resolved and therefore
    forbidden. Future planes are checked against the live frontier masks.
    """
    for sl in placement.slices:
        abs_d = placement.min_d + sl.rel_d
        rel = abs_d - current_d

        if rel < 0 or rel >= len(masks):
            return False

        if rel == 0:
            processed = processed_masks[current_d][cursor]
            if sl.bits & processed:
                return False

        if masks[rel] & sl.bits:
            return False

    return True


def overlay_placement(
    placement: Placement,
    current_d: int,
    masks: List[int],
) -> None:
    for sl in placement.slices:
        abs_d = placement.min_d + sl.rel_d
        rel = abs_d - current_d
        masks[rel] |= sl.bits


class FrontierSolver:
    def __init__(
        self,
        X: int,
        Y: int,
        Z: int,
        placements: Sequence[Placement],
        by_cell: Dict[Tuple[int, int, int], List[int]],
        plane_shapes,
        plane_order,
        processed_masks,
        max_states: int,
    ) -> None:
        self.X = X
        self.Y = Y
        self.Z = Z
        self.placements = placements
        self.by_cell = by_cell
        self.plane_shapes = plane_shapes
        self.plane_order = plane_order
        self.processed_masks = processed_masks
        self.max_states = max_states

        self.max_d = X - 1 + Y - 1 + Z - 1

        self.stats = Stats(
            last_report_time=time.perf_counter()
        )

        self.memo: set[
            Tuple[int, int, Tuple[int, ...]]
        ] = set()

    def solve(
        self,
        d: int,
        cursor: int,
        masks: Tuple[int, ...],
    ) -> bool:
        self.stats.calls += 1

        if self.stats.calls % 8192 == 0:
            self.report(d, cursor)

        if d > self.max_d:
            self.stats.solutions += 1
            return True

        # FIRST normalize/consume, THEN memoize.
        nd, nc, nm = consume_frontier(
            d,
            cursor,
            list(masks),
            self.plane_order,
            self.stats,
        )

        if nd > self.max_d:
            self.stats.solutions += 1
            return True

        key = (nd, nc, tuple(nm))

        if key in self.memo:
            self.stats.memo_hits += 1
            return False

        if len(self.memo) >= self.max_states:
            raise MemoryError(
                f"memo state limit {self.max_states:,} reached"
            )

        self.memo.add(key)

        bit = None
        order = self.plane_order[nd]
        for pos in range(nc, len(order)):
            candidate_bit = order[pos]
            if not (nm[0] & (1 << candidate_bit)):
                bit = candidate_bit
                break

        if bit is None:
            return False

        cells = self.plane_shapes[nd][0]
        u, v = cells[bit]

        nx = nd + 2 * u + v
        ny = nd - u + v
        nz = nd - u - 2 * v

        if nx % 3 or ny % 3 or nz % 3:
            return False

        x = nx // 3
        y = ny // 3
        z = nz // 3

        if not (
            0 <= x < self.X
            and 0 <= y < self.Y
            and 0 <= z < self.Z
        ):
            return False

        cell = (x, y, z)

        for placement_index in self.by_cell.get(cell, ()):
            self.stats.placements_tried += 1

            placement = self.placements[placement_index]

            if not placement_fits_frontier(
                placement,
                nd,
                nc,
                nm,
                self.processed_masks,
            ):
                continue

            self.stats.placements_accepted += 1

            new_masks = list(nm)
            overlay_placement(
                placement,
                nd,
                new_masks,
            )

            if self.solve(
                nd,
                nc,
                tuple(new_masks),
            ):
                return True

        return False

    def report(self, d: int, cursor: int) -> None:
        now = time.perf_counter()

        if now - self.stats.last_report_time < 2.0:
            return

        delta = self.stats.calls - self.stats.last_report_calls
        dt = now - self.stats.last_report_time
        rate = delta / dt if dt > 0 else 0.0

        self.stats.last_report_time = now
        self.stats.last_report_calls = self.stats.calls

        print(
            f"[progress] "
            f"d={d} "
            f"cursor={cursor} "
            f"calls={self.stats.calls:,} "
            f"memo={len(self.memo):,} "
            f"memo_hits={self.stats.memo_hits:,} "
            f"try={self.stats.placements_tried:,} "
            f"accept={self.stats.placements_accepted:,} "
            f"shifts={self.stats.plane_shifts:,} "
            f"forgot={self.stats.forgotten_cells:,} "
            f"rate={rate:,.0f}/s "
            f"rss={rss_mb():,.0f} MB",
            flush=True,
        )

    def run(self) -> bool:
        empty_masks = (0, 0, 0, 0, 0)
        start = time.perf_counter()

        try:
            result = self.solve(0, 0, empty_masks)
        except MemoryError as exc:
            print(f"\n[limit] {exc}", flush=True)
            result = False

        elapsed = time.perf_counter() - start

        print()
        print(
            "Result: "
            + ("TILEABLE" if result else "NO SOLUTION FOUND / LIMIT")
        )
        print(f"Calls: {self.stats.calls:,}")
        print(f"Memo states: {len(self.memo):,}")
        print(f"Memo hits: {self.stats.memo_hits:,}")
        print(f"Placements tried: {self.stats.placements_tried:,}")
        print(f"Placements accepted: {self.stats.placements_accepted:,}")
        print(f"Plane shifts: {self.stats.plane_shifts:,}")
        print(f"Forgotten frontier cells: {self.stats.forgotten_cells:,}")
        print(f"Solutions: {self.stats.solutions:,}")
        print(f"Elapsed: {elapsed:.3f} s")
        print(f"Peak RSS: {rss_mb():,.0f} MB")
        return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--box", nargs=3, type=int, required=True)
    parser.add_argument("--max-states", type=int, default=1_000_000)
    args = parser.parse_args()

    X, Y, Z = args.box

    if (X, Y) != (4, 8):
        parser.error("This prototype is specialized to 4x8xN.")

    print(
        f"Building S placements for {X}x{Y}x{Z}...",
        flush=True,
    )

    start = time.perf_counter()

    placements, by_cell, plane_shapes = build_placements(
        X, Y, Z
    )
    plane_order = build_plane_order(plane_shapes)
    processed_masks = build_processed_masks(plane_order)

    print(f"Placements: {len(placements)}")
    print(
        f"Placement generation: "
        f"{time.perf_counter() - start:.3f} s"
    )
    print(f"Diagonal planes: {len(plane_shapes)}")
    print("Searching corrected exposed-frontier DP...", flush=True)

    solver = FrontierSolver(
        X,
        Y,
        Z,
        placements,
        by_cell,
        plane_shapes,
        plane_order,
        processed_masks,
        args.max_states,
    )

    solver.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

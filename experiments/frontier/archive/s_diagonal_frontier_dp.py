#!/usr/bin/env python3
"""
Finite-box diagonal sweep / frontier-DP prototype for S in 4x8xN.

This version is intentionally finite-box and correctness-first.

Sweep order:
    d = x+y+z, increasing
    within each diagonal plane, a fixed deterministic (u,v) order

State:
    (current absolute diagonal d,
     cursor within diagonal d,
     occupancy bitsets for d..d+4)

Only the current + next four diagonal planes are retained because an S
pentacube has solid-diagonal span at most 4.

At each state:
    * find the earliest unresolved cell in the current diagonal;
    * try every concrete S placement containing that cell;
    * reject overlaps with already occupied cells;
    * add the placement to the 5-plane window;
    * advance the cursor past cells now occupied;
    * when the current plane is completely resolved, shift the window.

The memoized state is therefore a genuine local frontier state for a
finite box.  This is the correctness bridge before trying to make the
state translationally invariant / automaton-like.
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
PENTACUBE_SIZE = 5
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
    solutions: int = 0
    max_d: int = 0
    last_report_time: float = 0.0
    last_report_calls: int = 0


def rss_mb() -> float:
    return resource.getrusage(
        resource.RUSAGE_SELF
    ).ru_maxrss / 1024.0


def solid_coords(
    x: int,
    y: int,
    z: int,
) -> Tuple[int, int, int]:
    return x + y + z, x - y, y - z


def build_plane_shapes(
    X: int,
    Y: int,
    Z: int,
) -> Dict[
    int,
    Tuple[
        Tuple[Tuple[int, int], ...],
        Dict[Tuple[int, int], int],
    ],
]:
    """
    For every actual diagonal d, return:
        ordered (u,v) cells
        (u,v) -> bit index
    """
    grouped: Dict[
        int,
        set[Tuple[int, int]],
    ] = {}

    for z in range(Z):
        for y in range(Y):
            for x in range(X):
                d, u, v = solid_coords(x, y, z)
                grouped.setdefault(d, set()).add((u, v))

    result = {}

    for d, cells in grouped.items():
        ordered = tuple(sorted(cells))
        index = {
            cell: i
            for i, cell in enumerate(ordered)
        }
        result[d] = (ordered, index)

    return result


def build_order(
    plane_shapes,
) -> Dict[int, List[int]]:
    """
    Within each actual diagonal plane, order cells by (u,v).
    Return their bit indices.
    """
    result = {}

    for d, (cells, index) in plane_shapes.items():
        result[d] = [
            index[cell]
            for cell in cells
        ]

    return result


def placement_to_slices(
    placement: Sequence[Tuple[int, int, int]],
    plane_shapes,
) -> Placement:
    encoded = [
        solid_coords(x, y, z)
        for x, y, z in placement
    ]

    min_d = min(d for d, _, _ in encoded)
    max_d = max(d for d, _, _ in encoded)

    if max_d - min_d > MAX_SPAN:
        raise ValueError(
            "Placement exceeds supported diagonal span"
        )

    per_plane: Dict[int, int] = {}

    for d, u, v in encoded:
        rel = d - min_d
        shape_cells, shape_index = plane_shapes[d]
        bit = shape_index[(u, v)]
        per_plane[rel] = (
            per_plane.get(rel, 0)
            | (1 << bit)
        )

    slices = tuple(
        PlacementSlice(
            rel_d=rel,
            bits=per_plane[rel],
        )
        for rel in sorted(per_plane)
    )

    return Placement(
        cells=tuple(placement),
        slices=slices,
        min_d=min_d,
        max_d=max_d,
    )


def build_placements(
    X: int,
    Y: int,
    Z: int,
):
    raw, _ = generate_placements(
        PENTACUBES["S"],
        (X, Y, Z),
        break_symmetry=False,
    )

    plane_shapes = build_plane_shapes(X, Y, Z)

    placements = [
        placement_to_slices(
            placement,
            plane_shapes,
        )
        for placement in raw.values()
    ]

    # Index concrete placements by cell id.
    by_cell: Dict[
        Tuple[int, int, int],
        List[int],
    ] = {}

    for i, placement in enumerate(placements):
        for cell in placement.cells:
            by_cell.setdefault(
                cell,
                [],
            ).append(i)

    return (
        placements,
        by_cell,
        plane_shapes,
    )


def first_unresolved_bit(
    d: int,
    cursor: int,
    occupancy: int,
    order,
) -> int | None:
    cells = order[d]

    for pos in range(
        cursor,
        len(cells),
    ):
        bit = cells[pos]

        if not (
            occupancy & (1 << bit)
        ):
            return bit

    return None


def normalize_state(
    d: int,
    cursor: int,
    masks: List[int],
    order,
    stats: Stats,
) -> Tuple[int, int, List[int]]:
    """
    Advance over already-occupied cells.

    When the current diagonal has no unresolved cells, shift one plane.
    """
    while True:
        bit = first_unresolved_bit(
            d,
            cursor,
            masks[0],
            order,
        )

        if bit is not None:
            return d, cursor, masks

        # Current diagonal is completely resolved.
        d += 1
        cursor = 0
        stats.plane_shifts += 1

        if d >= len(order):
            return d, cursor, []

        masks = masks[1:] + [0]


def placement_fits_window(
    placement: Placement,
    current_d: int,
    masks: Sequence[int],
) -> bool:
    for sl in placement.slices:
        rel = (
            placement.min_d
            + sl.rel_d
            - current_d
        )

        if rel < 0 or rel >= len(masks):
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
        rel = (
            placement.min_d
            + sl.rel_d
            - current_d
        )

        masks[rel] |= sl.bits


class FrontierSolver:
    def __init__(
        self,
        X: int,
        Y: int,
        Z: int,
        placements: Sequence[Placement],
        by_cell: Dict[
            Tuple[int, int, int],
            List[int],
        ],
        plane_shapes,
        order,
        max_states: int,
    ) -> None:
        self.X = X
        self.Y = Y
        self.Z = Z
        self.placements = placements
        self.by_cell = by_cell
        self.plane_shapes = plane_shapes
        self.order = order
        self.max_states = max_states

        self.max_d = X - 1 + Y - 1 + Z - 1

        self.stats = Stats(
            last_report_time=time.perf_counter(),
        )

        self.memo: set[
            Tuple[int, int, Tuple[int, ...]]
        ] = set()

    def state_is_terminal(
        self,
        d: int,
    ) -> bool:
        return d > self.max_d

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

        key = (
            d,
            cursor,
            masks,
        )

        if key in self.memo:
            self.stats.memo_hits += 1
            return False

        if len(self.memo) >= self.max_states:
            raise MemoryError(
                f"memo state limit {self.max_states:,} reached"
            )

        # Normalize before memoization.
        nd, nc, nm = normalize_state(
            d,
            cursor,
            list(masks),
            self.order,
            self.stats,
        )

        if nd > self.max_d:
            self.stats.solutions += 1
            return True

        key = (
            nd,
            nc,
            tuple(nm),
        )

        if key in self.memo:
            self.stats.memo_hits += 1
            return False

        self.memo.add(key)

        bit = first_unresolved_bit(
            nd,
            nc,
            nm[0],
            self.order,
        )

        if bit is None:
            # Defensive: normalize_state should have advanced.
            return False

        shape_cells = self.plane_shapes[nd][0]
        u, v = shape_cells[bit]

        # Recover the actual 3D cell corresponding to this (d,u,v).
        # The inverse is:
        # x=(d+2u+v)/3
        # y=(d-u+v)/3
        # z=(d-u-2v)/3
        nx = nd + 2 * u + v
        ny = nd - u + v
        nz = nd - u - 2 * v

        if (
            nx % 3
            or ny % 3
            or nz % 3
        ):
            self.memo.add(key)
            return False

        x = nx // 3
        y = ny // 3
        z = nz // 3

        if not (
            0 <= x < self.X
            and 0 <= y < self.Y
            and 0 <= z < self.Z
        ):
            self.memo.add(key)
            return False

        cell = (x, y, z)

        candidates = self.by_cell.get(
            cell,
            (),
        )

        for placement_index in candidates:
            self.stats.placements_tried += 1

            placement = self.placements[
                placement_index
            ]

            if not placement_fits_window(
                placement,
                nd,
                nm,
            ):
                continue

            self.stats.placements_accepted += 1

            new_masks = list(nm)

            overlay_placement(
                placement,
                nd,
                new_masks,
            )

            # Cursor remains on the same diagonal; normalization will
            # advance across every newly occupied cell.
            if self.solve(
                nd,
                nc,
                tuple(new_masks),
            ):
                return True

        return False

    def report(
        self,
        d: int,
        cursor: int,
    ) -> None:
        now = time.perf_counter()

        if (
            now -
            self.stats.last_report_time
            < 2.0
        ):
            return

        delta = (
            self.stats.calls -
            self.stats.last_report_calls
        )

        dt = (
            now -
            self.stats.last_report_time
        )

        rate = (
            delta / dt
            if dt > 0
            else 0
        )

        self.stats.last_report_time = now
        self.stats.last_report_calls = (
            self.stats.calls
        )

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
            f"rate={rate:,.0f}/s "
            f"rss={rss_mb():,.0f} MB",
            flush=True,
        )

    def run(self) -> bool:
        empty_masks = (
            0,
            0,
            0,
            0,
            0,
        )

        start = time.perf_counter()

        try:
            result = self.solve(
                0,
                0,
                empty_masks,
            )
        except MemoryError as exc:
            print(
                f"\n[limit] {exc}",
                flush=True,
            )
            result = False

        elapsed = (
            time.perf_counter() -
            start
        )

        print()
        print(
            f"Result: "
            f"{'TILEABLE' if result else 'NO SOLUTION FOUND / LIMIT'}"
        )
        print(
            f"Calls: "
            f"{self.stats.calls:,}"
        )
        print(
            f"Memo states: "
            f"{len(self.memo):,}"
        )
        print(
            f"Memo hits: "
            f"{self.stats.memo_hits:,}"
        )
        print(
            f"Placements tried: "
            f"{self.stats.placements_tried:,}"
        )
        print(
            f"Placements accepted: "
            f"{self.stats.placements_accepted:,}"
        )
        print(
            f"Plane shifts: "
            f"{self.stats.plane_shifts:,}"
        )
        print(
            f"Solutions: "
            f"{self.stats.solutions:,}"
        )
        print(
            f"Elapsed: "
            f"{elapsed:.3f} s"
        )
        print(
            f"Peak RSS: "
            f"{rss_mb():,.0f} MB"
        )

        return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Finite-box diagonal frontier DP "
            "for S in 4x8xN."
        )
    )
    parser.add_argument(
        "--box",
        nargs=3,
        type=int,
        required=True,
    )
    parser.add_argument(
        "--max-states",
        type=int,
        default=1_000_000,
    )
    args = parser.parse_args()

    X, Y, Z = args.box

    if (X, Y) != (4, 8):
        parser.error(
            "This prototype is specialized to 4x8xN."
        )

    print(
        f"Building S placements for "
        f"{X}x{Y}x{Z}...",
        flush=True,
    )

    start = time.perf_counter()

    (
        placements,
        by_cell,
        plane_shapes,
    ) = build_placements(
        X,
        Y,
        Z,
    )

    order = build_order(
        plane_shapes
    )

    print(
        f"Placements: {len(placements)}",
        flush=True,
    )
    print(
        f"Placement generation: "
        f"{time.perf_counter() - start:.3f} s",
        flush=True,
    )
    print(
        f"Diagonal planes: "
        f"{len(plane_shapes)}",
        flush=True,
    )

    solver = FrontierSolver(
        X,
        Y,
        Z,
        placements,
        by_cell,
        plane_shapes,
        order,
        args.max_states,
    )

    print(
        "Searching diagonal frontier...",
        flush=True,
    )

    solver.run()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Experimental diagonal-frontier solver for S in 4x8xN boxes.

This version is instrumented for long runs:
  - progress every few seconds
  - recursive calls / memo size
  - placement attempts / accepts
  - current/max diagonal
  - process RSS memory
  - immediate flush so output remains visible
"""

from __future__ import annotations

import argparse
import os
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


@dataclass(frozen=True)
class PlacementInfo:
    cells: Tuple[Tuple[int, int, int], ...]
    diag_bits: Tuple[Tuple[int, int], ...]


@dataclass
class Stats:
    calls: int = 0
    memo_hits: int = 0
    placements_tried: int = 0
    placements_accepted: int = 0
    plane_shifts: int = 0
    max_d: int = 0
    last_report_time: float = 0.0
    last_report_calls: int = 0


def rss_mb() -> float:
    # Linux ru_maxrss is KiB.
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def print_progress(
    solver: "FrontierSolver",
    d: int,
    force: bool = False,
) -> None:
    now = time.perf_counter()
    stats = solver.stats

    if not force and now - stats.last_report_time < 2.0:
        return

    delta_calls = stats.calls - stats.last_report_calls
    delta_time = (
        now - stats.last_report_time
        if stats.last_report_time
        else 0.0
    )

    if delta_time > 0:
        rate = delta_calls / delta_time
    else:
        rate = 0.0

    stats.last_report_time = now
    stats.last_report_calls = stats.calls

    print(
        f"[progress] "
        f"d={d:3d} "
        f"calls={stats.calls:,} "
        f"memo={len(solver.state_cache):,} "
        f"memo_hits={stats.memo_hits:,} "
        f"try={stats.placements_tried:,} "
        f"accept={stats.placements_accepted:,} "
        f"shifts={stats.plane_shifts:,} "
        f"rate={rate:,.0f}/s "
        f"rss={rss_mb():,.0f} MB",
        flush=True,
    )


def plane_mask(d: int, n_z: int) -> int:
    mask = 0
    for y in range(Y_SIZE):
        for x in range(X_SIZE):
            z = d - x - y
            if 0 <= z < n_z:
                mask |= 1 << (x + X_SIZE * y)
    return mask


def lowest_set_bit_index(value: int) -> int:
    low = value & -value
    return low.bit_length() - 1


def placement_to_info(
    placement: Sequence[Tuple[int, int, int]]
) -> PlacementInfo:
    encoded = tuple(
        (x + y + z, x + X_SIZE * y)
        for x, y, z in placement
    )
    return PlacementInfo(tuple(placement), encoded)


def build_placements(
    n_z: int,
) -> tuple[list[PlacementInfo], dict[int, list[int]]]:
    placements, _ = generate_placements(
        PENTACUBES["S"],
        (X_SIZE, Y_SIZE, n_z),
        break_symmetry=False,
    )

    infos = [placement_to_info(p) for p in placements.values()]

    by_cell: dict[int, list[int]] = {}
    for index, info in enumerate(infos):
        for x, y, z in info.cells:
            cell_id = x + X_SIZE * (y + Y_SIZE * z)
            by_cell.setdefault(cell_id, []).append(index)

    return infos, by_cell


class FrontierSolver:
    def __init__(
        self,
        n_z: int,
        placements: Sequence[PlacementInfo],
        by_cell: Dict[int, List[int]],
    ) -> None:
        self.n_z = n_z
        self.placements = placements
        self.by_cell = by_cell

        self.max_d = (
            (X_SIZE - 1) +
            (Y_SIZE - 1) +
            (n_z - 1)
        )

        self.span = max(
            max(d for d, _ in p.diag_bits)
            - min(d for d, _ in p.diag_bits)
            for p in placements
        )

        self.full_masks = tuple(
            plane_mask(d, n_z)
            for d in range(self.max_d + 1)
        )

        self.state_cache: dict[
            tuple[int, tuple[int, ...]], bool
        ] = {}

        self.stats = Stats()

    def apply(
        self,
        d: int,
        masks: list[int],
        info: PlacementInfo,
    ) -> bool:
        changed: list[tuple[int, int]] = []

        for cell_d, bit in info.diag_bits:
            rel = cell_d - d

            if rel < 0 or rel > self.span:
                return False

            bit_mask = 1 << bit

            if masks[rel] & bit_mask:
                return False

            changed.append((rel, bit_mask))

        for rel, bit_mask in changed:
            masks[rel] |= bit_mask

        return True

    def undo(
        self,
        d: int,
        masks: list[int],
        info: PlacementInfo,
    ) -> None:
        for cell_d, bit in info.diag_bits:
            rel = cell_d - d
            masks[rel] &= ~(1 << bit)

    def solve(
        self,
        d: int,
        masks: tuple[int, ...],
    ) -> bool:
        self.stats.calls += 1
        self.stats.max_d = max(self.stats.max_d, d)

        # Emit progress frequently enough to diagnose runaway state growth.
        if (self.stats.calls & 0x3FFF) == 0:
            print_progress(self, d)

        if d > self.max_d:
            print_progress(self, d, force=True)
            return True

        full = self.full_masks[d]

        if masks[0] == full:
            shifted = masks[1:] + (0,)
            self.stats.plane_shifts += 1

            if (self.stats.plane_shifts & 0x3FFF) == 0:
                print_progress(self, d)

            return self.solve(d + 1, shifted)

        key = (d, masks)

        cached = self.state_cache.get(key)
        if cached is False:
            self.stats.memo_hits += 1
            return False

        missing = full & ~masks[0]

        if missing == 0:
            self.state_cache[key] = False
            return False

        bit = lowest_set_bit_index(missing)

        x = bit % X_SIZE
        y = bit // X_SIZE
        z = d - x - y

        if not (0 <= z < self.n_z):
            self.state_cache[key] = False
            return False

        cell_id = x + X_SIZE * (y + Y_SIZE * z)
        candidates = self.by_cell.get(cell_id, ())

        mutable = list(masks)

        for placement_index in candidates:
            self.stats.placements_tried += 1

            info = self.placements[placement_index]

            if not self.apply(d, mutable, info):
                continue

            self.stats.placements_accepted += 1

            if self.solve(d, tuple(mutable)):
                return True

            self.undo(d, mutable, info)

        self.state_cache[key] = False
        return False

    def run(self) -> bool:
        return self.solve(
            0,
            (0,) * (self.span + 1),
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Instrumented diagonal-frontier S solver "
            "for 4x8xN."
        )
    )
    parser.add_argument(
        "--box",
        nargs=3,
        type=int,
        required=True,
    )
    args = parser.parse_args()

    x, y, n_z = args.box

    if x != 4 or y != 8:
        parser.error(
            "This prototype is specialized to 4x8xN."
        )

    print(
        f"Building S placements for 4x8x{n_z}...",
        flush=True,
    )

    start = time.perf_counter()

    placements, by_cell = build_placements(n_z)

    gen_time = time.perf_counter() - start

    print(
        f"Placements: {len(placements)}",
        flush=True,
    )
    print(
        f"Placement generation: {gen_time:.3f} s",
        flush=True,
    )

    solver = FrontierSolver(
        n_z,
        placements,
        by_cell,
    )

    print(
        f"Diagonal span: {solver.span}",
        flush=True,
    )
    print(
        f"Diagonals: {solver.max_d + 1}",
        flush=True,
    )
    print(
        f"Initial RSS: {rss_mb():,.0f} MB",
        flush=True,
    )
    print(
        "Searching...",
        flush=True,
    )

    start = time.perf_counter()
    solver.stats.last_report_time = start
    solver.stats.last_report_calls = 0

    try:
        result = solver.run()
    except KeyboardInterrupt:
        print(
            "\nInterrupted.",
            flush=True,
        )
        print_progress(
            solver,
            solver.stats.max_d,
            force=True,
        )
        return 130

    elapsed = time.perf_counter() - start

    print()
    print(
        f"Result: "
        f"{'TILEABLE' if result else 'NO SOLUTION FOUND'}"
    )
    print(f"Search time: {elapsed:.3f} s")
    print(
        f"States/calls: "
        f"{solver.stats.calls:,}"
    )
    print(
        f"Memo hits: "
        f"{solver.stats.memo_hits:,}"
    )
    print(
        f"Memoized states: "
        f"{len(solver.state_cache):,}"
    )
    print(
        f"Placements tried: "
        f"{solver.stats.placements_tried:,}"
    )
    print(
        f"Placements accepted: "
        f"{solver.stats.placements_accepted:,}"
    )
    print(
        f"Plane shifts: "
        f"{solver.stats.plane_shifts:,}"
    )
    print(
        f"Max diagonal reached: "
        f"{solver.stats.max_d}"
    )
    print(
        f"Peak RSS: "
        f"{rss_mb():,.0f} MB"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

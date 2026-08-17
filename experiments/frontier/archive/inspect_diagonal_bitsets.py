#!/usr/bin/env python3
"""
Solid-diagonal slice-bitset explorer for the S pentacube in a 4x8xN box.

This is a geometry / transition prototype, not yet a solver.

Coordinates:
    d = x + y + z
    u = x - y
    v = y - z

For a fixed finite box, each solid-diagonal plane d has a finite set of
valid (u,v) points. We encode that plane shape with a compact bitset.

An S placement is represented by one bitset per relative d-plane.

This script:
  * builds the actual cross-section of every diagonal plane;
  * assigns a bit index to each (u,v) point;
  * converts every S placement to per-plane bitsets;
  * shows how a placement overlays an existing frontier;
  * reports the resulting frontier state.

It intentionally does not yet choose a canonical moving cut. The goal is
to make the transition primitive completely explicit and testable.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
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
class PlaneShape:
    d: int
    cells: Tuple[Tuple[int, int], ...]
    index: Dict[Tuple[int, int], int]


@dataclass(frozen=True)
class PlacementSlice:
    rel_d: int
    bits: int
    cells: Tuple[Tuple[int, int], ...]


@dataclass(frozen=True)
class PlacementSlices:
    slices: Tuple[PlacementSlice, ...]
    min_d: int
    max_d: int


def solid_coords(x: int, y: int, z: int) -> Tuple[int, int, int]:
    return x + y + z, x - y, y - z


def plane_cells(
    X: int,
    Y: int,
    Z: int,
) -> Dict[int, PlaneShape]:
    grouped: Dict[int, List[Tuple[int, int]]] = defaultdict(list)

    for z in range(Z):
        for y in range(Y):
            for x in range(X):
                d, u, v = solid_coords(x, y, z)
                grouped[d].append((u, v))

    result: Dict[int, PlaneShape] = {}

    for d, cells in grouped.items():
        ordered = tuple(sorted(set(cells)))
        result[d] = PlaneShape(
            d=d,
            cells=ordered,
            index={cell: i for i, cell in enumerate(ordered)},
        )

    return result


def placement_to_slices(
    placement: Sequence[Tuple[int, int, int]],
) -> PlacementSlices:
    encoded = [
        solid_coords(x, y, z)
        for x, y, z in placement
    ]

    min_d = min(d for d, _, _ in encoded)
    max_d = max(d for d, _, _ in encoded)

    by_d: Dict[int, List[Tuple[int, int]]] = defaultdict(list)

    for d, u, v in encoded:
        by_d[d - min_d].append((u, v))

    slices: List[PlacementSlice] = []

    for rel_d in sorted(by_d):
        cells = tuple(sorted(set(by_d[rel_d])))

        # A plane-local bit numbering is created later when we have a
        # finite box plane shape. Here we keep explicit cells.
        slices.append(
            PlacementSlice(
                rel_d=rel_d,
                bits=0,
                cells=cells,
            )
        )

    return PlacementSlices(
        slices=tuple(slices),
        min_d=min_d,
        max_d=max_d,
    )


def encode_placement(
    placement_slices: PlacementSlices,
    plane_shapes: Dict[int, PlaneShape],
) -> PlacementSlices:
    encoded: List[PlacementSlice] = []

    for sl in placement_slices.slices:
        # We need a representative absolute d to choose the plane shape.
        # The caller can later rebase this signature onto another d.
        abs_d = placement_slices.min_d + sl.rel_d

        if abs_d not in plane_shapes:
            raise ValueError(
                f"Placement slice d={abs_d} is outside the box"
            )

        shape = plane_shapes[abs_d]
        bits = 0

        for cell in sl.cells:
            try:
                bit = shape.index[cell]
            except KeyError as exc:
                raise ValueError(
                    f"Placement cell {cell} not present on d={abs_d}"
                ) from exc

            bits |= 1 << bit

        encoded.append(
            PlacementSlice(
                rel_d=sl.rel_d,
                bits=bits,
                cells=sl.cells,
            )
        )

    return PlacementSlices(
        slices=tuple(encoded),
        min_d=placement_slices.min_d,
        max_d=placement_slices.max_d,
    )


def render_slice(
    shape: PlaneShape,
    bits: int,
) -> str:
    occupied = {
        shape.cells[i]
        for i in range(len(shape.cells))
        if bits & (1 << i)
    }

    if not occupied:
        return "(empty)"

    us = [u for u, _ in shape.cells]
    vs = [v for _, v in shape.cells]

    min_u, max_u = min(us), max(us)
    min_v, max_v = min(vs), max(vs)

    lines = []

    for v in range(max_v, min_v - 1, -1):
        row = []
        for u in range(min_u, max_u + 1):
            row.append(
                "#"
                if (u, v) in occupied
                else "."
            )
        lines.append(
            f"{v:+3d}  " + "".join(row)
        )

    lines.append(
        "     " +
        "".join(
            str(abs(u) % 10)
            for u in range(min_u, max_u + 1)
        )
    )
    lines.append(
        f"     u={min_u}..{max_u}"
    )

    return "\n".join(lines)


def overlay(
    frontier: Dict[int, int],
    placement_slices: PlacementSlices,
    plane_shapes: Dict[int, PlaneShape],
    base_d: int,
) -> Dict[int, int] | None:
    """
    Overlay placement slices onto a frontier.

    frontier[d] is the occupancy bitset on absolute plane d.

    placement_slices are relative to placement_slices.min_d. We translate
    the placement so its minimum diagonal is base_d.
    """
    out = dict(frontier)

    for sl in placement_slices.slices:
        abs_d = base_d + sl.rel_d

        shape = plane_shapes.get(abs_d)
        if shape is None:
            return None

        bits = 0
        for cell in sl.cells:
            try:
                bits |= 1 << shape.index[cell]
            except KeyError:
                return None

        old = out.get(abs_d, 0)

        if old & bits:
            return None

        out[abs_d] = old | bits

    return out


def describe_placement(
    placement: Sequence[Tuple[int, int, int]],
    plane_shapes: Dict[int, PlaneShape],
) -> None:
    raw = placement_to_slices(placement)
    encoded = encode_placement(raw, plane_shapes)

    print(
        "Concrete placement:"
    )
    print(
        "  " +
        " ".join(
            f"({x},{y},{z})"
            for x, y, z in placement
        )
    )
    print(
        f"  d={raw.min_d}..{raw.max_d}, "
        f"span={raw.max_d - raw.min_d}"
    )

    for sl in encoded.slices:
        abs_d = raw.min_d + sl.rel_d
        shape = plane_shapes[abs_d]

        print(
            f"\n  relative d={sl.rel_d}, "
            f"absolute d={abs_d}, "
            f"bits=0x{sl.bits:x}"
        )
        print(
            "  cells: " +
            " ".join(
                f"({u:+d},{v:+d})"
                for u, v in sl.cells
            )
        )
        print(
            render_slice(
                shape,
                sl.bits,
            )
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--box",
        nargs=3,
        type=int,
        default=[4, 8, 10],
    )
    parser.add_argument(
        "--placement",
        type=int,
        default=424,
    )
    parser.add_argument(
        "--base-d",
        type=int,
        default=None,
        help="translate the selected placement to this minimum d",
    )
    parser.add_argument(
        "--show-planes",
        type=int,
        default=6,
    )
    args = parser.parse_args()

    X, Y, Z = args.box

    if (X, Y) != (4, 8):
        parser.error(
            "This prototype is specialized to a 4x8xN box."
        )

    print(
        f"Building diagonal-plane geometry for {X}x{Y}x{Z}...",
        flush=True,
    )

    shapes = plane_cells(X, Y, Z)

    print(
        f"Solid-diagonal planes: {len(shapes)}"
    )

    for d in sorted(shapes)[:args.show_planes]:
        shape = shapes[d]
        print(
            f"  d={d:2d}: "
            f"{len(shape.cells):2d} cells"
        )

    placements, _ = generate_placements(
        PENTACUBES["S"],
        (X, Y, Z),
        break_symmetry=False,
    )

    values = list(placements.values())

    if not (
        0 <= args.placement < len(values)
    ):
        parser.error(
            f"placement must be in "
            f"[0,{len(values)-1}]"
        )

    placement = values[args.placement]

    print(
        f"\n=== PLACEMENT #{args.placement} ===\n"
    )

    describe_placement(
        placement,
        shapes,
    )

    raw = placement_to_slices(placement)

    if args.base_d is None:
        base_d = raw.min_d
    else:
        base_d = args.base_d

    frontier: Dict[int, int] = {}

    result = overlay(
        frontier,
        raw,
        shapes,
        base_d,
    )

    print(
        f"\n=== OVERLAY at base d={base_d} ==="
    )

    if result is None:
        print("OVERLAP / OUTSIDE FRONTIER")
    else:
        for d in sorted(result):
            bits = result[d]
            shape = shapes[d]

            print(
                f"d={d}: "
                f"{bits.bit_count()} occupied cell(s), "
                f"mask=0x{bits:x}"
            )
            print(
                render_slice(shape, bits)
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Geometry inspector for an S pentacube under a solid-diagonal sweep.

We use:
    d = x + y + z
    u = x - y
    v = y - z

(d,u,v) is an invertible coordinate system up to the usual parity constraint:
    x = (2*d + 2*u - v) / 3
    y = (2*d - u - v) / 3
    z = (2*d - u + 2*v) / 3

This script does NOT solve anything.  It prints:
  1. the 4x8xN box cells grouped by diagonal d;
  2. one concrete S placement grouped by d;
  3. all normalized S placement signatures available from the
     authoritative placement generator.

The purpose is to see the actual 2D cross-section geometry perpendicular
to (1,1,1), rather than guessing at the frontier representation.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements


def solid_diagonal_coords(
    x: int,
    y: int,
    z: int,
) -> Tuple[int, int, int]:
    d = x + y + z
    u = x - y
    v = y - z
    return d, u, v


def inverse_coords(d, u, v):
    nx = d + 2*u + v
    ny = d - u + v
    nz = d - u - 2*v

    if nx % 3 or ny % 3 or nz % 3:
        return None

    return nx // 3, ny // 3, nz // 3


def group_box_by_diagonal(
    X: int,
    Y: int,
    Z: int,
) -> Dict[int, List[Tuple[int, int, int]]]:
    result: Dict[int, List[Tuple[int, int, int]]] = defaultdict(list)

    for z in range(Z):
        for y in range(Y):
            for x in range(X):
                d, u, v = solid_diagonal_coords(x, y, z)
                result[d].append((u, v, x, y, z))

    for d in result:
        result[d].sort()

    return dict(result)


def print_box_geometry(
    X: int,
    Y: int,
    Z: int,
) -> None:
    grouped = group_box_by_diagonal(X, Y, Z)

    print(
        f"\nBOX {X}x{Y}x{Z}: "
        f"{len(grouped)} solid-diagonal planes\n"
    )

    for d in sorted(grouped):
        print(
            f"d={d:2d}  "
            f"{len(grouped[d]):2d} cells: "
            + " ".join(
                f"({u:+d},{v:+d})"
                for u, v, *_ in grouped[d]
            )
        )


def normalize_placement(
    placement: Sequence[Tuple[int, int, int]],
) -> Tuple[
    int,
    Dict[int, List[Tuple[int, int, int, int, int]]]
]:
    encoded = []

    for x, y, z in placement:
        d, u, v = solid_diagonal_coords(x, y, z)
        encoded.append((d, u, v, x, y, z))

    min_d = min(item[0] for item in encoded)

    grouped: Dict[int, List[Tuple[int, int, int, int, int]]] = defaultdict(list)

    for d, u, v, x, y, z in encoded:
        grouped[d - min_d].append(
            (u, v, x, y, z)
        )

    for rel_d in grouped:
        grouped[rel_d].sort()

    return min_d, dict(grouped)


def print_placement_geometry(
    placement: Sequence[Tuple[int, int, int]],
) -> None:
    min_d, grouped = normalize_placement(placement)

    print(
        "\nS PLACEMENT\n"
        f"absolute minimum d = {min_d}\n"
    )

    for rel_d in sorted(grouped):
        items = grouped[rel_d]

        print(
            f"relative d={rel_d}: "
            + " ".join(
                f"(u={u:+d},v={v:+d})"
                for u, v, *_ in items
            )
        )

        for u, v, x, y, z in items:
            print(
                f"    ({x},{y},{z})"
                f" -> d={x+y+z},"
                f" u={u:+d},"
                f" v={v:+d}"
            )


def list_signature_patterns(
    placements: Iterable[Sequence[Tuple[int, int, int]]],
) -> Dict[
    Tuple[Tuple[Tuple[int, int], ...], ...],
    Sequence[Tuple[int, int, int]]
]:
    unique = {}

    for placement in placements:
        _, grouped = normalize_placement(placement)

        signature = tuple(
            tuple(
                (u, v)
                for u, v, *_ in grouped[d]
            )
            for d in sorted(grouped)
        )

        unique.setdefault(signature, placement)

    return unique


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--box",
        nargs=3,
        type=int,
        default=[4, 8, 10],
    )
    parser.add_argument(
        "--placement-limit",
        type=int,
        default=8,
        help="number of normalized S placement signatures to print",
    )
    args = parser.parse_args()

    X, Y, Z = args.box

    print(
        "Solid-diagonal coordinate system:\n"
        "    d = x + y + z\n"
        "    u = x - y\n"
        "    v = y - z\n"
    )

    print_box_geometry(X, Y, Z)

    placements, _ = generate_placements(
        PENTACUBES["S"],
        (X, Y, Z),
        break_symmetry=False,
    )

    first = next(iter(placements.values()))
    print_placement_geometry(first)

    signatures = list_signature_patterns(
        placements.values()
    )

    print(
        f"\nUnique normalized (u,v)-layer signatures: "
        f"{len(signatures)}"
    )

    print(
        f"Showing first "
        f"{min(args.placement_limit, len(signatures))}:"
    )

    for i, (signature, placement) in enumerate(
        list(signatures.items())[:args.placement_limit]
    ):
        print(f"\nSignature {i}:")
        for rel_d, layer in enumerate(signature):
            print(
                f"  d={rel_d}: "
                + " ".join(
                    f"({u:+d},{v:+d})"
                    for u, v in layer
                )
            )

    print("\nInverse-coordinate sanity checks:")

    for d in range(min(5, X + Y + Z - 2)):
        for u in range(-3, 4):
            for v in range(-3, 4):
                xyz = inverse_coords(d, u, v)

                if xyz is not None:
                    x, y, z = xyz

                    if (
                        0 <= x < X
                        and 0 <= y < Y
                        and 0 <= z < Z
                    ):
                        d2, u2, v2 = solid_diagonal_coords(
                            x, y, z
                        )

                        assert (
                            d, u, v
                        ) == (
                            d2, u2, v2
                        )

    print("  OK")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

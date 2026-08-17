#!/usr/bin/env python3
"""
Inspect S pentacube placements in planes perpendicular to (1,1,1).

Coordinates:
    d = x + y + z
    u = x - y
    v = y - z

For each placement, print the occupied (u,v) cells on each relative d-plane.

This is geometry inspection only.  No search or frontier model is assumed.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES, generate_placements


def solid_coords(
    x: int,
    y: int,
    z: int,
) -> Tuple[int, int, int]:
    return x + y + z, x - y, y - z


def normalize_placement(
    placement: Sequence[Tuple[int, int, int]],
) -> Tuple[
    Dict[int, List[Tuple[int, int]]],
    int,
    int,
    int,
]:
    encoded = []

    for x, y, z in placement:
        d, u, v = solid_coords(x, y, z)
        encoded.append((d, u, v))

    min_d = min(d for d, _, _ in encoded)
    max_d = max(d for d, _, _ in encoded)

    planes: Dict[int, List[Tuple[int, int]]] = defaultdict(list)

    for d, u, v in encoded:
        planes[d - min_d].append((u, v))

    for rel_d in planes:
        planes[rel_d].sort()

    return dict(planes), min_d, max_d, max_d - min_d


def render_plane(
    cells: Sequence[Tuple[int, int]],
) -> str:
    """
    Render a small ASCII picture of the (u,v) points.

    u increases left-to-right.
    v increases bottom-to-top visually.
    """
    if not cells:
        return "(empty)"

    us = [u for u, _ in cells]
    vs = [v for _, v in cells]

    min_u, max_u = min(us), max(us)
    min_v, max_v = min(vs), max(vs)

    occupied = set(cells)
    lines = []

    for v in range(max_v, min_v - 1, -1):
        row = []

        for u in range(min_u, max_u + 1):
            row.append("#" if (u, v) in occupied else ".")

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


def placement_description(
    placement: Sequence[Tuple[int, int, int]],
) -> str:
    planes, min_d, max_d, span = normalize_placement(
        placement
    )

    lines = [
        "Concrete cells:",
        "  " + " ".join(
            f"({x},{y},{z})"
            for x, y, z in placement
        ),
        f"Solid-diagonal span: d={min_d}..{max_d} "
        f"(span {span})",
        "",
    ]

    for rel_d in sorted(planes):
        cells = planes[rel_d]

        abs_d = min_d + rel_d

        lines.append(
            f"relative d={rel_d} "
            f"(absolute d={abs_d}), "
            f"{len(cells)} cell(s):"
        )
        lines.append(
            "  " +
            " ".join(
                f"({u:+d},{v:+d})"
                for u, v in cells
            )
        )
        lines.append(
            render_plane(cells)
        )
        lines.append("")

    return "\n".join(lines)


def signature_key(
    placement: Sequence[Tuple[int, int, int]],
) -> Tuple:
    planes, _, _, _ = normalize_placement(
        placement
    )

    return tuple(
        tuple(planes[d])
        for d in sorted(planes)
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
        default=None,
        help="show this placement dictionary ordinal",
    )
    parser.add_argument(
        "--signature",
        type=int,
        default=None,
        help="show this normalized (u,v)-signature ordinal",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=12,
        help="number of normalized signatures to show",
    )
    args = parser.parse_args()

    X, Y, Z = args.box

    if (X, Y) != (4, 8):
        parser.error(
            "This inspector is currently for 4x8xN."
        )

    print(
        f"Generating S placements for {X}x{Y}x{Z}...",
        flush=True,
    )

    placements, _ = generate_placements(
        PENTACUBES["S"],
        (X, Y, Z),
        break_symmetry=False,
    )

    values = list(placements.values())

    print(
        f"Concrete placements: {len(values)}"
    )

    signatures = {}
    for placement in values:
        signatures.setdefault(
            signature_key(placement),
            placement,
        )

    ordered = sorted(signatures.items())

    print(
        f"Unique normalized (u,v) signatures: "
        f"{len(ordered)}"
    )

    if args.placement is not None:
        if not (0 <= args.placement < len(values)):
            parser.error(
                f"placement must be in "
                f"[0,{len(values)-1}]"
            )

        print(
            "\n=== CONCRETE PLACEMENT "
            f"#{args.placement} ===\n"
        )
        print(
            placement_description(
                values[args.placement]
            )
        )

    if args.signature is not None:
        if not (0 <= args.signature < len(ordered)):
            parser.error(
                f"signature must be in "
                f"[0,{len(ordered)-1}]"
            )

        signature, representative = ordered[
            args.signature
        ]

        print(
            "\n=== NORMALIZED SIGNATURE "
            f"#{args.signature} ===\n"
        )
        print(
            placement_description(
                representative
            )
        )

    if (
        args.placement is None
        and args.signature is None
    ):
        print(
            f"\nShowing first "
            f"{min(args.count, len(ordered))} "
            "normalized signatures:\n"
        )

        for i, (_, representative) in enumerate(
            ordered[:args.count]
        ):
            print(
                f"--- Signature #{i} ---"
            )
            print(
                placement_description(
                    representative
                )
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

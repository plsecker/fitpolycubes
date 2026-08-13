import argparse
import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from common.polycube_utils import generate_placements, PENTACUBES


def cell_id(x, y, z, X, Y):
    return x + X * (y + Y * z)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("piece")
    parser.add_argument("--box", nargs=3, type=int, required=True)
    args = parser.parse_args()

    piece = args.piece.upper()
    X, Y, Z = args.box

    if piece not in PENTACUBES:
        parser.error(f"Unknown piece: {piece}")

    p = PENTACUBES[piece]
    box_size = (X, Y, Z)

    print(f"Generating placements for {piece} in {X}x{Y}x{Z}...")

    placements, canonical_p_000 = generate_placements(
        p,
        box_size,
        break_symmetry=True
    )

    items = list(placements.items())

    key, placement = items[424]

    print("ordinal 424 -> key:", key)
    print("placement:", placement)

    print("placements type:", type(placements))
    print("first placement:", placements[0])
    print("first placement type:", type(placements[0]))
    print(f"Placements found: {len(placements)}")

    filename = f"placements_{piece}_{X}x{Y}x{Z}.txt"

    with open(filename, "w") as f:
        f.write(f"{len(placements)}\n")

        for placement in placements.values():
            ids = [
                cell_id(x, y, z, X, Y)
                for x, y, z in placement
            ]

            f.write(" ".join(map(str, ids)) + "\n")

    print(f"Wrote {filename}")


if __name__ == "__main__":
    main()
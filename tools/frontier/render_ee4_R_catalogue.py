#!/usr/bin/env python3
"""
Render the EE4 5-R tiling catalogue (Task 10 of the classification).

One render per orientation-multiset class (8 classes of 2 tilings; the
two members of a class are pure translates of each other, so one render
per class shows the family).  Each render shows the five pieces in
distinct colours with the RM index of each piece labelled at its
centroid, from a consistent viewpoint.

Output: data/ee4_R_5/catalogue/class_M1.png ... class_M8.png

Usage: python3 tools/frontier/render_ee4_R_catalogue.py
"""

import json
import os
import sys

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DATA = os.path.join(REPO_ROOT, "data", "ee4_R_5", "all_tilings.json")
OUT_DIR = os.path.join(REPO_ROOT, "data", "ee4_R_5", "catalogue")

# Okabe-Ito colourblind-safe palette
PIECE_COLOURS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00"]


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with open(DATA) as f:
        data = json.load(f)

    os.makedirs(OUT_DIR, exist_ok=True)
    for mc in data["orientation_multiset_classes"]:
        ms = mc["multiset"]
        tid = mc["tiling_ids"][0]
        t = data["tilings"][tid]
        pieces = [set(tuple(c) for c in p["cells"]) for p in t["pieces"]]
        rm = [p["rm_index"] for p in t["pieces"]]
        tag = "M" + "_".join(str(i) for i in ms)

        cells = set().union(*pieces)
        xs = [c[0] for c in cells]
        ys = [c[1] for c in cells]
        zs = [c[2] for c in cells]
        ox, oy, oz = min(xs) - 1, min(ys) - 1, min(zs) - 1
        shape = (max(xs) - ox + 2, max(ys) - oy + 2, max(zs) - oz + 2)
        filled = np.zeros(shape, dtype=bool)
        fc = np.zeros(shape + (4,))
        colour_of = {}
        for i, p in enumerate(pieces):
            for c in p:
                colour_of[c] = PIECE_COLOURS[i]
        for c in cells:
            x, y, z = c[0] - ox, c[1] - oy, c[2] - oz
            filled[x, y, z] = True
            fc[x, y, z] = matplotlib.colors.to_rgba(colour_of[c])

        fig = plt.figure(figsize=(6.2, 6.2))
        ax = fig.add_subplot(111, projection="3d")
        ax.voxels(filled, facecolors=fc, edgecolors="#1a1a1a", linewidth=0.5)
        ax.set_box_aspect(shape)
        ax.view_init(elev=22, azim=-55)
        ax.set_axis_off()

        # label each piece with its RM index at the piece centroid
        for i, p in enumerate(pieces):
            cx = sum(c[0] for c in p) / 5.0 - ox
            cy = sum(c[1] for c in p) / 5.0 - oy
            cz = sum(c[2] for c in p) / 5.0 - oz
            ax.text(cx, cy, cz, f"RM[{rm[i]}]", fontsize=8.5,
                    color="#111111", ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white",
                              ec="#555555", alpha=0.85))

        ax.set_title(f"EE4 5-R tiling class {tag} — "
                     f"RM {ms} (tiling T{tid})", fontsize=10, pad=2)
        fig.tight_layout()
        out = os.path.join(OUT_DIR, f"class_{tag}.png")
        fig.savefig(out, dpi=150, facecolor="white")
        plt.close(fig)
        print("->", out)


if __name__ == "__main__":
    main()
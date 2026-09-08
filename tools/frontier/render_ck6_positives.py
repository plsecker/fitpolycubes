#!/usr/bin/env python3
"""
Stage 5O: render the priority representatives of the Stage 5N small-CK6
catalogue.

For each selected shape:
  <id>_target.png  -- uncoloured target (uniform cubes, dark edges)
  <id>_tiling.png  -- one verified tiling, copies individually coloured

Conventions:
  - unit cubes via matplotlib voxels, dark edges;
  - consistent viewpoint (elev=22, azim=-55) and equal aspect;
  - the symmetry centre (figure centroid = CK6 fixed point) is marked
    with a black diamond and short dashed axis stubs;
  - coordinates are the verified proper-canonical coordinates of the
    Stage 5N catalogue.
"""

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, REPO)

REUSE = os.path.join(REPO, "data", "ck6_reuse")
RENDERS = os.path.join(REUSE, "renders")

PRIORITY = [
    "B-V15-S1", "R-V15-S1", "X-V15-S2", "B-V25-S12", "P-V25-S3",
    "I-V25-S4", "I-V25-S5", "I-V25-S6", "I-V25-S7",
    "I-V25-S8", "I-V25-S9", "I-V25-S10", "I-V25-S11",
]

PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
           "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD"]


def render(cells, tiling, path, title):
    """cells: list of (x,y,z); tiling: list of placements (lists) or None."""
    cells = [tuple(c) for c in cells]
    mn = tuple(min(c[i] for c in cells) for i in range(3))
    rel = [tuple(c[i] - mn[i] for i in range(3)) for c in cells]
    dims = [max(c[i] for c in rel) + 1 for i in range(3)]
    filled = np.zeros(dims, dtype=bool)
    for c in rel:
        filled[c] = True

    if tiling is None:
        fc = np.zeros(tuple(dims) + (4,))
        fc[..., :3] = np.array([0.62, 0.71, 0.83])
        fc[..., 3] = 1.0
    else:
        copy_of = {}
        for i, pl in enumerate(tiling):
            for c in pl:
                copy_of[tuple(c)] = i
        base = matplotlib.colors.to_rgba_array(PALETTE)[..., :3]
        fc = np.zeros(tuple(dims) + (4,))
        fc[..., 3] = 1.0
        for c in rel:
            fc[c[0], c[1], c[2], :3] = base[copy_of[c] % len(PALETTE)]

    fig = plt.figure(figsize=(6.5, 6.5))
    ax = fig.add_subplot(111, projection="3d")
    ax.voxels(filled, facecolors=fc, edgecolors="#262626", linewidth=0.5)

    # symmetry centre (centroid = CK6 fixed point) + short axis stubs
    cent = np.mean(np.array(cells), axis=0) - np.array(mn)
    ax.scatter([cent[0]], [cent[1]], [cent[2]], marker="D",
               color="black", s=35, depthshade=False)
    L = 1.6
    for axis in range(3):
        d = np.zeros(3)
        d[axis] = L
        ax.plot(*zip(cent - d, cent + d), color="black",
                linestyle="--", linewidth=0.8, alpha=0.6)

    ax.set_box_aspect(dims)
    ax.view_init(elev=22, azim=-55)
    ax.set_axis_off()
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def main():
    with open(os.path.join(REUSE, "small_positive_catalogue.json")) as f:
        cat = json.load(f)
    by_id = {r["id"]: r for r in cat["constructions"]}
    os.makedirs(RENDERS, exist_ok=True)
    todo = PRIORITY
    missing = [i for i in todo if i not in by_id]
    assert not missing, missing
    for sid in todo:
        r = by_id[sid]
        common = (f"{sid}: {r['number_of_copies']} x {r['piece']}, "
                  f"V={r['volume']}, {r['symmetry_class']} "
                  f"(order {r['symmetry_order']}), "
                  f"{r['number_of_tilings']} tiling(s)")
        render(r["target_coordinates"], None,
               os.path.join(RENDERS, f"{sid}_target.png"), common)
        render(r["target_coordinates"], r["explicit_tiling"],
               os.path.join(RENDERS, f"{sid}_tiling.png"), common)
        print("rendered", sid)
    print(f"{len(todo)} shapes x 2 renders -> {RENDERS}")


if __name__ == "__main__":
    main()

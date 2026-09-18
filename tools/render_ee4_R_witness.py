#!/usr/bin/env python3
"""
Render the EE4 5-R witness (tests/fixtures/ee4_R_5.json).

Produces:
  - cross-section panels, z from top to bottom (matching George
    Sicherman's page convention), each cell coloured by placement,
  - a 3D voxel view with the symmetry axes drawn.

Usage: python3 tools/render_ee4_R_witness.py [path-to-fixture] [out-dir]
"""

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

DEFAULT_FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "ee4_R_5.json")

COLOURS = [
    "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
    "#46f0f0", "#f032e6", "#bcf60c", "#fabebe", "#008080",
]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FIXTURE
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        REPO_ROOT, "data", "ee4_R_5", "renders")
    with open(path) as f:
        fx = json.load(f)

    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(path))[0]

    # ---- cross-sections, z top to bottom ----
    target = {tuple(c) for c in fx["target"]}
    zs = sorted({c[2] for c in target}, reverse=True)
    colour_of = {}
    for i, pl in enumerate(fx["placements"]):
        for c in pl["cells"]:
            colour_of[tuple(c)] = COLOURS[i % len(COLOURS)]

    xs = sorted({c[0] for c in target})
    ys = sorted({c[1] for c in target})
    x_off = min(xs)
    y_off = min(ys)

    fig, axes = plt.subplots(1, len(zs), figsize=(2.2 * len(zs), 2.4))
    if len(zs) == 1:
        axes = [axes]
    for ax, z in zip(axes, zs):
        layer = [c for c in target if c[2] == z]
        grid = np.zeros((max(ys) - min(ys) + 1, max(xs) - min(xs) + 1, 3))
        for c in layer:
            gx, gy = c[0] - x_off, c[1] - y_off
            rgb = matplotlib.colors.to_rgb(colour_of[c])
            grid[gy, gx] = rgb
        ax.imshow(grid, origin="lower")
        ax.set_title(f"z = {z}", fontsize=9)
        ax.set_xticks(range(grid.shape[1]))
        ax.set_yticks(range(grid.shape[0]))
        ax.set_xticklabels([x_off + i for i in range(grid.shape[1])], fontsize=7)
        ax.set_yticklabels([y_off + i for i in range(grid.shape[0])], fontsize=7)
        ax.set_aspect("equal")
    fig.suptitle(f"{fx['piece']} x5, {fx['symmetry_class']} "
                 f"({fx['symmetry_description']})", fontsize=10)
    fig.tight_layout()
    cross_path = os.path.join(out_dir, f"{base}_cross_sections.png")
    fig.savefig(cross_path, dpi=150)
    plt.close(fig)
    print(f"cross-sections -> {cross_path}")

    # ---- 3D voxel view ----
    filled = np.zeros((5, 5, 5), dtype=bool)
    fc = np.zeros((5, 5, 5, 4))
    for c, col in colour_of.items():
        x, y, z = c[0] + 2, c[1] + 2, c[2] + 2
        filled[x, y, z] = True
        fc[x, y, z] = matplotlib.colors.to_rgba(col)
    fig = plt.figure(figsize=(6.5, 6.5))
    ax = fig.add_subplot(111, projection="3d")
    ax.voxels(filled, facecolors=fc, edgecolors="#262626", linewidth=0.4)
    cent = np.mean(np.argwhere(filled), axis=0)
    L = 2.6
    for axis in range(3):
        d = np.zeros(3)
        d[axis] = L
        ax.plot(*zip(cent - d, cent + d), color="black", linestyle="--",
                linewidth=0.8, alpha=0.6)
    ax.set_box_aspect((5, 5, 5))
    ax.view_init(elev=22, azim=-55)
    ax.set_axis_off()
    ax.set_title(f"{fx['piece']} x5 {fx['symmetry_class']} witness", fontsize=10)
    fig.tight_layout()
    view_path = os.path.join(out_dir, f"{base}_3d.png")
    fig.savefig(view_path, dpi=140)
    plt.close(fig)
    print(f"3D view -> {view_path}")


if __name__ == "__main__":
    main()
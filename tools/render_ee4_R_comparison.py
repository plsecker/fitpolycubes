#!/usr/bin/env python3
"""
Visual diagnostics for the EE4 5-R witness, generated from the fixture
(no image reverse-engineering).

Produces, in data/ee4_R_5/comparison/:
  1. ee4_R_5_3d_coloured.png   - full 3D voxel view, one colour per piece
  2. ee4_R_5_ortho_x/y/z.png   - orthographic projections along x, y, z
  3. ee4_R_5_orientation_k.png - each of the five R orientations as a
                                 small 3D voxel view (palette-diagram
                                 style)
  4. ee4_R_5_composite.png     - whole witness + five orientations with
                                 RM index and translation labels

Usage: python3 tools/render_ee4_R_comparison.py [path-to-fixture] [out-dir]
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

from common.rotmatrix import RM
from common.registry import PENTACUBES

DEFAULT_FIXTURE = os.path.join(REPO_ROOT, "tests", "fixtures", "ee4_R_5.json")

COLOURS = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4"]


def load_fixture(path):
    with open(path) as f:
        fx = json.load(f)
    R = PENTACUBES[fx["piece"]]
    placements = []
    for pl in fx["placements"]:
        k = pl["rotation_index"]
        rot = {tuple(int(v) for v in RM[k] @ np.array(r)) for r in R}
        t = tuple(pl["translation"])
        cells = {tuple(c[j] + t[j] for j in range(3)) for c in rot}
        assert cells == {tuple(c) for c in pl["cells"]}
        mn = tuple(min(c[j] for c in rot) for j in range(3))
        norm = tuple(sorted(tuple(c[j] - mn[j] for j in range(3))
                            for c in rot))
        placements.append({"index": k, "translation": t, "cells": cells,
                           "norm": norm})
    return fx, placements


def voxel_axes(cells, pad=1):
    """Return (filled, facecolors, origin) arrays for ax.voxels."""
    xs = [c[0] for c in cells]
    ys = [c[1] for c in cells]
    zs = [c[2] for c in cells]
    ox, oy, oz = min(xs) - pad, min(ys) - pad, min(zs) - pad
    sx, sy, sz = max(xs) - ox + 1 + pad, max(ys) - oy + 1 + pad, \
        max(zs) - oz + 1 + pad
    filled = np.zeros((sx, sy, sz), dtype=bool)
    fc = np.zeros((sx, sy, sz, 4))
    return filled, fc, (ox, oy, oz)


def render_3d(cells, colour_of, title, out_path, elev=22, azim=-55,
              dpi=140, figsize=(6.5, 6.5)):
    filled, fc, (ox, oy, oz) = voxel_axes(cells)
    for c in cells:
        x, y, z = c[0] - ox, c[1] - oy, c[2] - oz
        filled[x, y, z] = True
        fc[x, y, z] = matplotlib.colors.to_rgba(colour_of[c])
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")
    ax.voxels(filled, facecolors=fc, edgecolors="#262626", linewidth=0.4)
    ax.set_box_aspect((filled.shape[0], filled.shape[1], filled.shape[2]))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    print(f"-> {out_path}")


def render_ortho(cells, colour_of, axis, out_path):
    """Orthographic projection along `axis` (0=x,1=y,2=z).

    Front-most cell along the viewing axis wins the colour.
    """
    other = [a for a in range(3) if a != axis]
    u, v = other
    # grid over the two remaining coordinates
    us = sorted({c[u] for c in cells})
    vs = sorted({c[v] for c in cells})
    grid = np.zeros((len(vs), len(us), 3))
    for c in cells:
        gu, gv = us.index(c[u]), vs.index(c[v])
        grid[gv, gu] = matplotlib.colors.to_rgb(colour_of[c])
    fig, ax = plt.subplots(figsize=(3.2, 3.2))
    ax.imshow(grid, origin="lower")
    ax.set_xticks(range(len(us)))
    ax.set_yticks(range(len(vs)))
    ax.set_xticklabels(us, fontsize=7)
    ax.set_yticklabels(vs, fontsize=7)
    ax.set_aspect("equal")
    ax.set_title(f"orthographic view along {'xyz'[axis]}", fontsize=10)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"-> {out_path}")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FIXTURE
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        REPO_ROOT, "data", "ee4_R_5", "comparison")
    os.makedirs(out_dir, exist_ok=True)

    fx, placements = load_fixture(path)
    target = {tuple(c) for c in fx["target"]}
    colour_of = {}
    for i, pl in enumerate(placements):
        for c in pl["cells"]:
            colour_of[c] = COLOURS[i % len(COLOURS)]

    # 1. full 3D view, one colour per piece
    render_3d(target, colour_of,
              f"{fx['piece']} x5 {fx['symmetry_class']} witness",
              os.path.join(out_dir, "ee4_R_5_3d_coloured.png"))

    # 2. orthographic views along x, y, z
    for axis in range(3):
        render_ortho(target, colour_of, axis,
                     os.path.join(out_dir, f"ee4_R_5_ortho_{'xyz'[axis]}.png"))

    # 3. individual orientation views (palette-diagram style)
    for i, pl in enumerate(placements):
        norm = pl["norm"]
        oc = {c: COLOURS[i % len(COLOURS)] for c in norm}
        render_3d(norm, oc,
                  f"orientation {i}: RM[{pl['index']}]",
                  os.path.join(out_dir, f"ee4_R_5_orientation_{i}.png"),
                  elev=25, azim=-60, dpi=120, figsize=(3.4, 3.4))

    # 4. composite: witness + five orientations with RM index/translation
    fig = plt.figure(figsize=(13, 7))
    gs = fig.add_gridspec(2, 6, width_ratios=[2.2] + [1] * 5,
                          height_ratios=[1, 1])
    # top-left: whole witness 3D
    filled, fc, (ox, oy, oz) = voxel_axes(target)
    for c in target:
        x, y, z = c[0] - ox, c[1] - oy, c[2] - oz
        filled[x, y, z] = True
        fc[x, y, z] = matplotlib.colors.to_rgba(colour_of[c])
    ax = fig.add_subplot(gs[0, 0], projection="3d")
    ax.voxels(filled, facecolors=fc, edgecolors="#262626", linewidth=0.3)
    ax.set_box_aspect((filled.shape[0], filled.shape[1], filled.shape[2]))
    ax.view_init(elev=22, azim=-55)
    ax.set_axis_off()
    ax.set_title("whole witness", fontsize=10)

    # top row: cross-section z layers of the witness
    zs = sorted({c[2] for c in target}, reverse=True)
    for j, z in enumerate(zs):
        ax = fig.add_subplot(gs[0, j + 1])
        layer = [c for c in target if c[2] == z]
        xs = sorted({c[0] for c in target})
        ys = sorted({c[1] for c in target})
        grid = np.zeros((len(ys), len(xs), 3))
        for c in layer:
            grid[ys.index(c[1]), xs.index(c[0])] = \
                matplotlib.colors.to_rgb(colour_of[c])
        ax.imshow(grid, origin="lower")
        ax.set_title(f"z={z}", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect("equal")

    # bottom row: five orientations
    for i, pl in enumerate(placements):
        norm = pl["norm"]
        filled, fc, (ox, oy, oz) = voxel_axes(norm)
        for c in norm:
            x, y, z = c[0] - ox, c[1] - oy, c[2] - oz
            filled[x, y, z] = True
            fc[x, y, z] = matplotlib.colors.to_rgba(
                COLOURS[i % len(COLOURS)])
        ax = fig.add_subplot(gs[1, i], projection="3d")
        ax.voxels(filled, facecolors=fc, edgecolors="#262626", linewidth=0.3)
        ax.set_box_aspect((filled.shape[0], filled.shape[1], filled.shape[2]))
        ax.view_init(elev=25, azim=-60)
        ax.set_axis_off()
        ax.set_title(f"R{i}: RM[{pl['index']}] t={pl['translation']}",
                     fontsize=8)

    fig.suptitle(f"{fx['piece']} x5 {fx['symmetry_class']} witness - "
                 f"fixture decomposition", fontsize=12)
    fig.tight_layout()
    comp_path = os.path.join(out_dir, "ee4_R_5_composite.png")
    fig.savefig(comp_path, dpi=140)
    plt.close(fig)
    print(f"-> {comp_path}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Render cross-sections of all four canonical EE4 5-R targets (top to
bottom, George Sicherman's page convention) for visual comparison with
5-17p.png.

Usage: python3 tools/frontier/render_ee4_all_targets.py [out-dir]
"""

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
TOOLS = os.path.join(REPO_ROOT, "tools")
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

import order4_R_class_comparison as cmp
from common.symmetry import normalize

COLOURS = [
    "#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
]


def render_target(target, placements, out_path, title):
    colour_of = {}
    for i, pl in enumerate(placements):
        for c in pl:
            colour_of[c] = COLOURS[i % len(COLOURS)]
    zs = sorted({c[2] for c in target}, reverse=True)
    xs = sorted({c[0] for c in target})
    ys = sorted({c[1] for c in target})
    x_off, y_off = min(xs), min(ys)
    fig, axes = plt.subplots(1, len(zs), figsize=(2.2 * len(zs), 2.4))
    if len(zs) == 1:
        axes = [axes]
    for ax, z in zip(axes, zs):
        layer = [c for c in target if c[2] == z]
        grid = np.zeros((max(ys) - min(ys) + 1, max(xs) - min(xs) + 1, 3))
        for c in layer:
            gx, gy = c[0] - x_off, c[1] - y_off
            grid[gy, gx] = matplotlib.colors.to_rgb(colour_of[c])
        ax.imshow(grid, origin="lower")
        ax.set_title(f"z = {z}", fontsize=9)
        ax.set_xticks(range(grid.shape[1]))
        ax.set_yticks(range(grid.shape[0]))
        ax.set_xticklabels([x_off + i for i in range(grid.shape[1])], fontsize=7)
        ax.set_yticklabels([y_off + i for i in range(grid.shape[0])], fontsize=7)
        ax.set_aspect("equal")
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"-> {out_path}")


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        REPO_ROOT, "data", "ee4_R_5", "renders")
    os.makedirs(out_dir, exist_ok=True)

    mats = cmp.CLASS_GROUPS["EE4"]
    placements = cmp.build_placements()
    orbits = cmp.orbits_of(cmp.BOX_CELLS, mats)
    orbit_of = {}
    for idx, o in enumerate(orbits):
        for c in o:
            orbit_of[c] = idx
    pclosure = []
    for p in placements:
        cells = set()
        for c in p:
            cells |= orbits[orbit_of[c]]
        pclosure.append(frozenset(cells))

    results, nodes, dt = cmp.search_class(placements, pclosure, max_tilings=2000)
    by_target = {}
    for target, chosen in results:
        by_target.setdefault(normalize(target), []).append((target, chosen))

    for k, (canon, lst) in enumerate(sorted(by_target.items())):
        target, chosen = lst[0]
        render_target(
            set(target),
            [placements[i] for i in chosen],
            os.path.join(out_dir, f"ee4_target_{k + 1}.png"),
            f"EE4 5-R target {k + 1} ({len(lst)} tilings) - cross-sections",
        )
    print(f"rendered {len(by_target)} targets to {out_dir}")


if __name__ == "__main__":
    main()
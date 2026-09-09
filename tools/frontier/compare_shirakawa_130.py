#!/usr/bin/env python3
"""
Compare Shirakawa's published 4x8x130 S-pentacube tiling
(https://puzzlewillbeplayed.com/Shirakawa/html/5-15-130x8x4.html,
SVG diagram 5-15-4x8x130.svgz) against our 2048 reconstructed
macro tilings of the 4x8x130 box.

Shirakawa's SVG layout (established by shape verification):
  - 4 panels (x-columns), each 8 columns x 130 rows
  - panel 0 = cols 27..34, panel 1 = cols 18..25,
    panel 2 = cols 9..16,  panel 3 = cols 0..7
  - canonical coords: x = panel index, y = col within panel,
    z = row (0..129)
  - every piece is a proper rotation of PENTACUBES["S"]
    (verified: exactly one axis convention passes, chirality = S)

Our tilings: one per macro walk (walks_130.txt), placements from
the unique per-edge realization sequences (edge_realizations_130.txt);
first edge 0 -> ENTRY fills slice 0, walk edge i fills slice i+1.

Comparison: exact placement-set equality, up to the 4 proper box
symmetries (identity + three 180-degree rotations).  Improper
symmetries map S -> Z and are checked only as a sanity report.

Independent cross-check: the macro walk of Shirakawa's tiling is
computed directly from the tiling (state after slice s = packed
occupancy of slices s+1, s+2, s+3) and tested against our 2048 walks.

No solver definitions are modified; no new closure is run.
"""

from __future__ import annotations

import itertools
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from common.polycube_utils import PENTACUBES
from solvers.s_z_frontier_packed import NCELLS

SVG_FILE = Path("/tmp/opencode/shirakawa/5-15-4x8x130.svg")
WALKS_FILE = Path("/tmp/opencode/walks_130.txt")
EDGES_FILE = Path("/tmp/opencode/edge_realizations_130.txt")
TILING_OUT = Path("/tmp/opencode/shirakawa_tiling_130.txt")
RESULTS_OUT = Path("/tmp/opencode/shirakawa_comparison_results.txt")

X_SIZE, Y_SIZE, Z_SIZE = 4, 8, 130
L = 129
ENTRY = 17293822637554016271

# panel -> first column of the panel in the SVG
PANEL_FIRST_COL = {0: 27, 1: 18, 2: 9, 3: 0}


def panel_of(col: int) -> int:
    if 27 <= col <= 34:
        return 0
    if 18 <= col <= 25:
        return 1
    if 9 <= col <= 16:
        return 2
    if 0 <= col <= 7:
        return 3
    raise ValueError(f"column {col} outside panels")


def proper_rotations(shape):
    """All 24 proper rotations of a shape, normalized to origin."""
    out = set()
    for perm in itertools.permutations(range(3)):
        inv = [perm.index(i) for i in range(3)]
        sgn = 1
        for i in range(3):
            for j in range(i + 1, 3):
                if inv[i] > inv[j]:
                    sgn = -sgn
        for signs in itertools.product([1, -1], repeat=3):
            if sgn * signs[0] * signs[1] * signs[2] != 1:
                continue
            r = frozenset(
                tuple(signs[i] * c[perm[i]] for i in range(3)) for c in shape
            )
            mins = tuple(min(c[i] for c in r) for i in range(3))
            out.add(frozenset(tuple(c[i] - mins[i] for i in range(3)) for c in r))
    return out


def load_walks(path: Path):
    walks = []
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            continue
        key, val = line.split("=", 1)
        walks.append([int(x) for x in val.split(",")])
    return walks


def load_edge_sequences(path: Path):
    """edge (a,b) -> list of placements; placement = tuple of 5 (x,y,z)."""
    seqs = {}
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            continue
        key, val = line.split("=", 1)
        assert key.startswith("edge_")
        a, b = key[5:].split("_", 1)
        placements = []
        if val:  # empty sequence = pure shift edge (e.g. WORD_MASK -> 0)
            for part in val.split(";"):
                nums = [int(x) for x in part.split(",")]
                assert len(nums) == 15, (key, len(nums))
                cells = tuple(
                    (nums[i], nums[i + 1], nums[i + 2]) for i in range(0, 15, 3)
                )
                placements.append(cells)
        seqs[(int(a), int(b))] = placements
    return seqs


def tiling_of_walk(walk, seqs):
    """Placement set (frozenset of frozensets of 5 cells) for a walk."""
    placements = set()
    # first edge 0 -> ENTRY fills slice 0
    for cells in seqs[(0, ENTRY)]:
        placements.add(frozenset(cells))
    # walk edge i fills slice i+1
    for i, (a, b) in enumerate(zip(walk, walk[1:])):
        off = i + 1
        for cells in seqs[(a, b)]:
            placements.add(frozenset((x, y, z + off) for x, y, z in cells))
    assert len(placements) == 832
    return frozenset(placements)


def macro_walk_of_tiling(placements):
    """Independent macro walk from a tiling.

    P_s = pieces whose lowest cell lies in slice s.
    After filling slice s and shifting, the state is
        M_s = pack(slice s+1 & (P_{s-1} | P_s), slice s+2 & P_s, 0)
    with P_{-1} = empty.  (Layer 2 is always 0: pieces placed while
    filling slice s+1 extend at most to slice s+3, which is not yet
    in the state; the state only tracks cells covered by pieces
    anchored in the current or previous slice.)
    """
    P = defaultdict(set)  # lowest-z slice -> pieces
    for p in placements:
        minz = min(z for _, _, z in p)
        P[minz].add(p)

    def mask_of(pieces, z):
        m = 0
        for p in pieces:
            for x, y, zz in p:
                if zz == z:
                    m |= 1 << (x + X_SIZE * y)
        return m

    walk = []
    for s in range(Z_SIZE):
        l0 = mask_of(P.get(s - 1, set()) | P.get(s, set()), s + 1)
        l1 = mask_of(P.get(s, set()), s + 2)
        walk.append(l0 | (l1 << NCELLS))
    return walk


def main() -> int:
    t0 = time.perf_counter()
    lines = []

    S = frozenset(map(tuple, PENTACUBES["S"]))
    Z = frozenset(map(tuple, PENTACUBES["Z"]))
    ROTS_S = proper_rotations(S)
    ROTS_Z = proper_rotations(Z)
    print(f"S rotations: {len(ROTS_S)}, Z rotations: {len(ROTS_Z)}")

    # ---- 1. parse Shirakawa SVG ----
    print("Parsing Shirakawa SVG...", flush=True)
    svg = SVG_FILE.read_text()
    rects = re.findall(
        r'<rect x="(\d+)" y="(\d+)" width="10" height="10" fill="rgb\(([^)]*)\)"/><!-- (\d+) -->',
        svg,
    )
    assert len(rects) == 4160, len(rects)

    pieces = defaultdict(set)
    for x, y, fill, p in rects:
        col, row = int(x) // 10, int(y) // 10
        pan = panel_of(col)
        cx = pan
        cy = col - PANEL_FIRST_COL[pan]
        cz = row
        pieces[int(p)].add((cx, cy, cz))

    assert len(pieces) == 832
    bad_s = [p for p, cells in pieces.items() if not _is_rot(cells, ROTS_S)]
    bad_z = [p for p, cells in pieces.items() if not _is_rot(cells, ROTS_Z)]
    print(f"pieces: {len(pieces)}, bad vs S: {len(bad_s)}, bad vs Z: {len(bad_z)}")
    assert not bad_s, f"pieces not S rotations: {bad_s[:10]}"
    assert bad_z, "expected Z to fail (chirality check)"

    shirakawa = frozenset(frozenset(cells) for cells in pieces.values())
    assert len(shirakawa) == 832
    all_cells = set().union(*shirakawa)
    assert len(all_cells) == 4160
    box = {(x, y, z) for x in range(4) for y in range(8) for z in range(130)}
    assert all_cells == box, "Shirakawa tiling does not cover the box exactly"

    # save canonical tiling
    with open(TILING_OUT, "w") as f:
        f.write("# Shirakawa 4x8x130 S-pentacube tiling, canonical coords\n")
        f.write("# piece_no=x,y,z;x,y,z;x,y,z;x,y,z;x,y,z\n")
        for p in sorted(pieces):
            cells = sorted(pieces[p])
            f.write(f"{p}=" + ";".join(f"{x},{y},{z}" for x, y, z in cells) + "\n")

    # ---- 2. build our 2048 tilings ----
    print("Loading walks and edge sequences...", flush=True)
    walks = load_walks(WALKS_FILE)
    seqs = load_edge_sequences(EDGES_FILE)
    print(f"  walks: {len(walks)}, edge sequences: {len(seqs)}", flush=True)

    print("Building 2048 tilings...", flush=True)
    tiling_index = defaultdict(list)  # hash -> [walk indices]
    for wi, w in enumerate(walks):
        t = tiling_of_walk(w, seqs)
        tiling_index[hash(t)].append(wi)

    n_distinct = len(tiling_index)
    collisions = {h: v for h, v in tiling_index.items() if len(v) > 1}
    print(f"  distinct tilings: {n_distinct}, hash collisions: {len(collisions)}")
    assert n_distinct == 2048 and not collisions

    # ---- 3. symmetry comparison ----
    syms = [
        ("identity", lambda c: (c[0], c[1], c[2])),
        ("rot_z_180", lambda c: (3 - c[0], 7 - c[1], c[2])),
        ("rot_y_180", lambda c: (3 - c[0], c[1], 129 - c[2])),
        ("rot_x_180", lambda c: (c[0], 7 - c[1], 129 - c[2])),
        # improper (sanity only: S -> Z, cannot match our S tilings)
        ("refl_x", lambda c: (3 - c[0], c[1], c[2])),
        ("refl_y", lambda c: (c[0], 7 - c[1], c[2])),
        ("refl_z", lambda c: (c[0], c[1], 129 - c[2])),
        ("inversion", lambda c: (3 - c[0], 7 - c[1], 129 - c[2])),
    ]

    print("Comparing against our 2048 tilings...", flush=True)
    match = None
    for name, g in syms:
        t = frozenset(
            frozenset(g(c) for c in p) for p in shirakawa
        )
        cands = tiling_index.get(hash(t), [])
        for wi in cands:
            ref = tiling_of_walk(walks[wi], seqs)
            if t == ref:
                match = (name, wi)
                break
        if match:
            break
        print(f"  {name}: no match", flush=True)

    # ---- 4. independent macro walk of Shirakawa's tiling ----
    print("Computing Shirakawa macro walk from the tiling...", flush=True)
    sh_walk = macro_walk_of_tiling(shirakawa)
    assert sh_walk[-1] == 0
    walk_set = {tuple(w) for w in walks}
    sh_key = tuple(sh_walk)
    in_walks = sh_key in walk_set
    print(f"  Shirakawa walk in our 2048 walks: {in_walks}")

    # structural stats of Shirakawa's walk
    import numpy as np
    scc = set(int(x) for x in np.load("/tmp/opencode/scc_130_states.npy"))
    n_in_scc = sum(1 for s in sh_walk if s in scc)
    n_distinct_states = len(set(sh_walk))
    print(f"  Shirakawa walk: {len(sh_walk)} states, {n_distinct_states} distinct, "
          f"{n_in_scc} in our 478-state SCC")

    # 20-cycle check (post-shift states)
    CYCLE20 = [
        6163195513375031274, 13835058072323104239, 3993075831, 55840897340952456,
        9838132153049676753, 2089671021646321023, 13523993509333176, 54046496222498049,
        3430478137537398, 2691607028413209, 4934612199136503, 612490719515897646,
        16285016559841080657, 217229141722890951, 6729013160573166, 2297949969,
        1224979683048584328, 17294878168733286543, 4294967295, 0,
    ]
    cyc_set = set(CYCLE20)
    n_cyc = sum(1 for s in sh_walk if s in cyc_set)
    print(f"  Shirakawa walk states in 20-cycle: {n_cyc}")

    # ---- 5. report ----
    lines.append(f"shirakawa_pieces={len(pieces)}")
    lines.append(f"shirakawa_cells={len(all_cells)}")
    lines.append(f"shirakawa_all_S_rotations={not bad_s}")
    lines.append(f"shirakawa_all_Z_rotations={not bad_z}")
    lines.append(f"our_tilings={n_distinct}")
    lines.append(f"match={match[0] if match else 'NONE'}")
    if match:
        lines.append(f"match_walk_index={match[1]}")
        lines.append(f"match_symmetry={match[0]}")
    lines.append(f"shirakawa_walk_in_our_2048={in_walks}")
    lines.append(f"shirakawa_walk_states={len(sh_walk)}")
    lines.append(f"shirakawa_walk_distinct_states={n_distinct_states}")
    lines.append(f"shirakawa_walk_states_in_478_scc={n_in_scc}")
    lines.append(f"shirakawa_walk_states_in_20cycle={n_cyc}")
    if in_walks:
        wi = next(i for i, w in enumerate(walks) if tuple(w) == sh_key)
        lines.append(f"shirakawa_walk_index={wi}")
        # edges used
        used = [(a, b) for a, b in zip(sh_walk, sh_walk[1:])]
        lines.append(f"shirakawa_walk_edges={len(used)}")
        lines.append(f"shirakawa_walk_edges_distinct={len(set(used))}")

    RESULTS_OUT.write_text("\n".join(lines) + "\n")

    print()
    print("=== SUMMARY ===")
    for ln in lines:
        print(" ", ln)
    print(f"  elapsed: {time.perf_counter() - t0:.1f}s")
    print(f"  results written to {RESULTS_OUT}")
    return 0


def _is_rot(cells, rots):
    mins = tuple(min(c[i] for c in cells) for i in range(3))
    norm = frozenset(tuple(c[i] - mins[i] for i in range(3)) for c in cells)
    return norm in rots


if __name__ == "__main__":
    raise SystemExit(main())
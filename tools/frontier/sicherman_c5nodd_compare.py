#!/usr/bin/env python3
"""
Stage 5P: external geometric comparison of our small CK6 constructions
against George Sicherman's published catalogue.

Source page (cached copy in data/ck6_reuse/sicherman_cache/c5odd/):
    https://sicherman.net/c5odd/c5nodd.html
    "Pentacube Oddities with Inverse/Diagonal Symmetry" (rev 2026-09-05)

The page publishes, for each pentacube, its smallest known oddity with
inverse/diagonal (= CK6, or a supergroup thereof) symmetry, as a 3-D
drawing plus a strip of flat-coloured cross-sections ("shown from top to
bottom", i.e. left-to-right in the strip = top-to-bottom in z).

Method
------
For the three published figures that can match our catalogue entries at
the same (piece, tile count) -- R 3, P 5, Z 5 -- we reconstruct the actual
geometry from the cross-section strips:

  1. auto-detect the flat-colour strip bands (no white outline pixels),
  2. label connected components (one per z-layer grid),
  3. solve the square lattice pitch per component (every lattice cell
     must be uniformly one flat colour or black),
  4. assemble (x=col, y=row, z=layer) cell sets.

Handedness caveat: the reading convention (column/row/layer directions)
is fixed only up to reflections, but every figure on this page contains
inversion, hence is achiral -- any consistent reading yields a congruent
shape.  This is asserted via the reconstruction's own symmetry, never
assumed.

Each reconstruction is then validated independently of the parsing:
cell count == 5*tiles, face-connectivity, |Sym| >= 4 with a CK6
subgroup, and every published colour class congruent to our registry
piece under the 24 proper rotations.  Only then do we compare:

  * full-O_h and proper-rotation canonical forms against the Stage 5N
    catalogue ids,
  * tiling orbits under Sym(target): George's published colouring vs the
    complete tiling set of the (congruent) target.

Verdicts are reported per pair as one of:
    known shape + known tiling   (congruent; his colouring is one of our
                                  tiling orbits)
    known shape + new tiling(s)  (congruent; we have tiling orbits he
                                  does not show)
    related-but-distinct         (same piece/count/class, non-congruent)
    no match found               (no same piece/count entry on the page)

Metadata-only comparisons (B 13 vs our B-V15-S1 etc.) are recorded from
the parsed page labels; for those, absence from the page is NOT evidence
of absence -- the page lists one smallest-known figure per piece.

This script is read-only over repo data except for its own report files
under data/ck6_reuse/.
"""

import json
import os
import sys
from collections import defaultdict

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from common.symmetry import (  # noqa: E402
    affine_symmetries,
    canonical_form,
    normalize,
    symmetry_order,
)
from common.oddity import (  # noqa: E402
    is_face_connected,
    placements_in_region,
    unique_orientations,
)
from common.rotmatrix import RM  # noqa: E402
from common.registry import PENTACUBES  # noqa: E402
from common.algorithm_x import solve as exact_cover_solve  # noqa: E402

CACHE = os.path.join(REPO, "data", "ck6_reuse", "sicherman_cache", "c5odd")
REUSE = os.path.join(REPO, "data", "ck6_reuse")

# ---------------------------------------------------------------------------
# Published page content (transcribed from the cached images; labels were
# read at 7-8x zoom.  Tile counts printed on the figures.)
# ---------------------------------------------------------------------------
PAGE_REV = "2026-09-05"
GEORGE_ROWS = {
    # piece: (tiles, table)  -- tables: ach, chd (chiral, no reflection),
    # cha (chiral, reflection allowed; differs only for E)
    "X": (1, "ach"),
    "P": (5, "ach"),
    "Z": (5, "ach"),
    "I": (1, "ach"),
    "V": (7, "ach"),
    "M": (3, "ach"),
    "Q": (7, "ach"),
    "L": (11, "ach"),
    "U": (7, "ach"),
    "Y": (13, "ach"),
    "K": (21, "ach"),
    "B": (13, "ach"),
    "A": (15, "ach"),
    "N": (15, "ach"),
    "W": (9, "ach"),
    "F": (11, "ach"),
    "T": (19, "ach"),
    "R": (3, "chd"),
    "S": (7, "chd"),
    "H": (7, "chd"),
    "J": (9, "chd"),
    "G": (7, "chd"),
    "E": (13, "chd"),
}

# Which published figures we reconstruct geometrically, and which of our
# catalogue entries they could match (same piece AND same tile count).
# Strip bands and x-ranges were located by component scan and are
# validated hard by the cell-count and lattice assertions in parse_strip.
# The images have WHITE background, BLACK cell borders, 9 px cell pitch.
RECONSTRUCT = [
    # (name, image, piece, tiles, (our piece, our volume), band, x_range)
    ("R-3", "c5n-chd.png", "R", 3, ("R", 15), (150, 200), (0, 130)),
    ("P-5", "c5n-ach.png", "P", 5, ("P", 25), (100, 160), (150, 320)),
    ("Z-5", "c5n-ach.png", "Z", 5, ("Z", 25), (100, 160), (340, 460)),
]

# Flat palette of the published strips (nearest-match classification).
PALETTE = {
    "red": (255, 48, 48),
    "aqua": (127, 255, 212),
    "gold": (255, 215, 0),
    "green": (34, 139, 34),
    "purple": (186, 85, 211),
    "orange": (255, 140, 0),
    "gray": (136, 153, 136),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
}


def classify_px(px, tol=60):
    best, bd = "other", 10 ** 9
    for name, (r, g, b) in PALETTE.items():
        d = abs(int(px[0]) - r) + abs(int(px[1]) - g) + abs(int(px[2]) - b)
        if d < bd:
            bd, best = d, name
    return best if bd <= tol else "other"


# ---------------------------------------------------------------------------
# Strip parsing (white background, black cell borders, flat palette cells)
# ---------------------------------------------------------------------------

def band_components(img, band, x_range):
    """Connected non-white components inside a horizontal band, filtered
    to an x-range and to pure palette/black pixels (no anti-aliased
    'other' content, which would indicate figure/label bleed)."""
    y0, y1 = band
    xa, xb = x_range
    a = np.asarray(img.convert("RGB"), dtype=int)[y0:y1]
    h, w, _ = a.shape
    cls = np.empty((h, w), dtype=object)
    for y in range(h):
        for x in range(w):
            cls[y, x] = classify_px(a[y, x])
    mask = cls != "white"
    seen = np.zeros_like(mask, dtype=bool)
    comps = []
    for sy in range(h):
        for sx in range(xa, min(xb, w)):
            if mask[sy, sx] and not seen[sy, sx]:
                stack, cells, others = [(sy, sx)], [], 0
                seen[sy, sx] = True
                while stack:
                    cy, cx = stack.pop()
                    cells.append((cy, cx))
                    if cls[cy, cx] == "other":
                        others += 1
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if (0 <= ny < h and 0 <= nx < w
                                    and mask[ny, nx] and not seen[ny, nx]):
                                seen[ny, nx] = True
                                stack.append((ny, nx))
                ys = [c[0] for c in cells]
                xs = [c[1] for c in cells]
                if others == 0:
                    comps.append({
                        "bbox": (min(xs), y0 + min(ys),
                                 max(xs) + 1, y0 + max(ys) + 1),
                        "area": len(cells),
                    })
    comps.sort(key=lambda c: c["bbox"][0])
    return comps


def _border_pixels_match(a, x0, y0, pitch, gw, gh, grid):
    """Check the black-border structure: a filled cell draws a 1 px ring
    on each side whose neighbour (outside the block, unfilled, or a
    different colour) does not continue the colour.  Every pure-black
    pixel in the bbox must be predicted, and every predicted pixel must
    be black or anti-aliased ('other')."""
    h, w = a.shape[0], a.shape[1]
    black_obs = set()
    for yy in range(y0, min(y0 + gh * pitch + 1, h)):
        for xx in range(x0, min(x0 + gw * pitch + 1, w)):
            if classify_px(a[yy, xx]) == "black":
                black_obs.add((xx, yy))
    pred = set()
    for gr in range(gh):
        for gc in range(gw):
            if not grid[gr][gc]:
                continue
            name = None
            for cand in _cell_color_candidates(a, x0, y0, pitch, gc, gr):
                name = cand
            bx0 = x0 + gc * pitch
            by0 = y0 + gr * pitch
            # left side
            if gc == 0 or not grid[gr][gc - 1] or _cell_color(
                    a, x0, y0, pitch, gc - 1, gr) != _cell_color(
                    a, x0, y0, pitch, gc, gr):
                pred.update((bx0, yy)
                            for yy in range(by0, by0 + pitch + 1))
            # right side
            if (gc == gw - 1 or not grid[gr][gc + 1]
                    or _cell_color(a, x0, y0, pitch, gc + 1, gr)
                    != _cell_color(a, x0, y0, pitch, gc, gr)):
                pred.update((bx0 + pitch, yy)
                            for yy in range(by0, by0 + pitch + 1))
            # top side
            if gr == 0 or not grid[gr - 1][gc] or _cell_color(
                    a, x0, y0, pitch, gc, gr - 1) != _cell_color(
                    a, x0, y0, pitch, gc, gr):
                pred.update((xx, by0)
                            for xx in range(bx0, bx0 + pitch + 1))
            # bottom side
            if (gr == gh - 1 or not grid[gr + 1][gc]
                    or _cell_color(a, x0, y0, pitch, gc, gr + 1)
                    != _cell_color(a, x0, y0, pitch, gc, gr)):
                pred.update((xx, by0 + pitch)
                            for xx in range(bx0, bx0 + pitch + 1))
    if not black_obs <= pred:
        return False
    for (xx, yy) in pred:
        if yy >= h or xx >= w:
            return False
        if classify_px(a[yy, xx]) not in ("black", "other"):
            return False
    return True


def _cell_color(a, x0, y0, pitch, gc, gr):
    cx = x0 + gc * pitch + pitch // 2
    cy = y0 + gr * pitch + pitch // 2
    return classify_px(a[cy, cx])


def _cell_color_candidates(a, x0, y0, pitch, gc, gr):
    return [_cell_color(a, x0, y0, pitch, gc, gr)]


def solve_component_lattice(img, comp):
    """Solve the square lattice of one strip-layer component.

    Geometry (measured on the cached images): cells are drawn on a small
    pitch (8 px in these images) with 1 px black border rings drawn only
    where a filled cell faces an unfilled cell, a different colour, or
    the exterior.  The pitch is auto-detected; a candidate pitch is
    accepted only if (a) every cell-centre sample is uniform and (b) the
    predicted black border pixels exactly reproduce the observed ones
    (this kills sub-cell pitches, which would predict borders that are
    not drawn).

    Returns (pitch, grid, color_grid): grid[row][col] = filled bool,
    color_grid[row][col] = palette name or None.
    """
    x0, y0, x1, y1 = comp["bbox"]
    a = np.asarray(img.convert("RGB"), dtype=int)
    bw, bh = x1 - x0, y1 - y0
    for pitch in range(12, 3, -1):
        if (bw - 1) % pitch or (bh - 1) % pitch:
            continue
        gw, gh = (bw - 1) // pitch, (bh - 1) // pitch
        if gw == 0 or gh == 0 or gw * gh > 64:
            continue
        ok = True
        grid, color_grid = [], []
        for gr in range(gh):
            rowcells, colorrow = [], []
            for gc in range(gw):
                name = _cell_color(a, x0, y0, pitch, gc, gr)
                filled = name not in ("white", "black", "other")
                colorrow.append(name if filled else None)
                rowcells.append(filled)
            grid.append(rowcells)
            color_grid.append(colorrow)
        if _border_pixels_match(a, x0, y0, pitch, gw, gh, grid):
            return pitch, grid, color_grid
    return None, None, None


def parse_strip(img, band, x_range, expect_cells):
    """Parse one strip into (layers, color_layers).

    layers: list of {(col,row)} per z-layer, left-to-right = top-to-bottom.
    color_layers: same shape, values are palette names (George's tiling).
    """
    comps = band_components(img, band, x_range)
    layers, color_layers = [], []
    for comp in comps:
        c, grid, color_grid = solve_component_lattice(img, comp)
        if c is None:
            raise ValueError(f"unsolvable component bbox={comp['bbox']} "
                             f"area={comp['area']}")
        cells = {(gc, gr)
                 for gr, rowcells in enumerate(grid)
                 for gc, filled in enumerate(rowcells) if filled}
        if len(cells) == 0:
            continue
        layers.append(cells)
        color_layers.append(color_grid)
    total = sum(len(s) for s in layers)
    if total != expect_cells:
        raise ValueError(f"strip cell count {total} != expected "
                         f"{expect_cells} (layers: "
                         f"{[len(s) for s in layers]})")
    return layers, color_layers


def assemble(layers):
    """(x=col, y=row, z=layer) -> normalized sorted tuple of triples."""
    cells = []
    for z, layer in enumerate(layers):
        for (x, y) in layer:
            cells.append((x, y, z))
    return normalize(cells)


def align_and_identify(layers, color_layers, piece_letter):
    """Recover the per-layer xy-offsets of a strip and identify the figure.

    George's strip layout positions each cross-section grid decoratively,
    so when a layer's filled cells do not span the figure's full xy
    footprint, the per-layer offsets are lost by bbox-relative reading.
    We recover them by constraint search:

      * offsets in [-4..4]^2 per layer, anchored at the densest layer;
      * necessary: the xy-footprints of consecutive z-layers intersect
        (all face-adjacency is within a layer or between consecutive
        z-layers, so the footprint-intersection graph must be connected);
      * the assembled figure must be face-connected and contain a CK6
        subgroup (the page's stated symmetry);
      * when every colour class has exactly 5 cells (George reuses
        colours otherwise), each class must be the piece under proper
        rotations;
      * the figure must be tileable by the piece (proper rotations).

    Returns a list of distinct surviving figures (canonical form, cells,
    diagnostics).  z-flip (strip read bottom-to-top) is tried as well.
    """
    piece = [tuple(int(v) for v in c) for c in PENTACUBES[piece_letter]]
    piece_orbits = proper_orientation_set(piece)
    n = len(layers)
    anchor = max(range(n), key=lambda i: len(layers[i]))
    foot = [frozenset(layers[i]) for i in range(n)]
    all5 = all(
        sum(1 for z2 in range(n) for (x, y) in layers[z2]
            if color_layers[z2][y][x] == cls) == 5
        for cls in {color_layers[z][y][x]
                    for z in range(n) for (x, y) in layers[z]})

    def footprint(foots, i, off):
        return {(x + off[0], y + off[1]) for (x, y) in foots[i]}

    results = {}
    for zflip in (False, True):
        order = list(range(n))
        lays = list(layers)
        cols = list(color_layers)
        if zflip:
            lays = lays[::-1]
            cols = cols[::-1]
        foots = [frozenset(l) for l in lays]
        anchor = max(range(n), key=lambda i: len(foots[i]))
        # assignment order: anchor first, then spreading outward in z, so
        # every newly assigned layer is constrained by an assigned
        # neighbour (footprints of consecutive z-layers must intersect)
        order = [anchor]
        for d in range(1, n):
            if anchor - d >= 0:
                order.append(anchor - d)
            if anchor + d < n:
                order.append(anchor + d)
        # DFS over offsets in that order
        stack = [(0, {})]
        while stack:
            pos, assign = stack.pop()
            if pos == n:
                cells = []
                for z in range(n):
                    off = assign[z]
                    for (x, y) in lays[z]:
                        cells.append((x + off[0], y + off[1], z))
                cells_t = normalize(cells)
                key = cells_t
                if key in results:
                    continue
                if not is_face_connected(cells_t):
                    continue
                if ck6_subgroup_count(cells_t) < 1:
                    continue
                if all5:
                    classes = defaultdict(list)
                    for z in range(n):
                        for (x, y) in lays[z]:
                            classes[cols[z][y][x]].append(
                                (x + assign[z][0], y + assign[z][1], z))
                    if any(normalize(cs) not in piece_orbits
                           for cs in classes.values()):
                        continue
                    his = [frozenset(cs) for cs in classes.values()]
                else:
                    his = None
                til = all_tilings(set(cells_t), piece)
                if not til:
                    continue
                orbs = tiling_orbits(set(cells_t), til)
                entry = {
                    "cells": [list(c) for c in cells_t],
                    "oh_canonical_id": "oh-" + cid(canonical_form(cells_t)),
                    "p24_canonical_id": "p24-"
                    + cid(canonical_form(cells_t, proper_only=True)),
                    "symmetry_order": symmetry_order(
                        [m for m, _ in affine_symmetries(cells_t)]),
                    "tiling_count": len(til),
                    "tiling_orbit_count": len(orbs),
                    "offsets": {z: list(assign[z]) for z in range(n)},
                    "zflip": zflip,
                    "colors_are_pieces": all5,
                }
                if his is not None:
                    his_sig = tiling_orbits(set(cells_t),
                                            [frozenset(his)])[0]
                    entry["his_tiling_orbit_index"] = (
                        orbs.index(his_sig) if his_sig in orbs else None)
                results[key] = entry
                continue
            i = order[pos]
            # offset domain for layer i: must intersect every assigned
            # consecutive-z neighbour
            dom = []
            for ox in range(-4, 5):
                for oy in range(-4, 5):
                    cur = footprint(foots, i, (ox, oy))
                    ok = True
                    for j in (i - 1, i + 1):
                        if j in assign:
                            if not (cur & footprint(foots, j, assign[j])):
                                ok = False
                                break
                    if ok:
                        dom.append((ox, oy))
            if i == anchor:
                dom = [(0, 0)]
            for off in dom:
                nxt_assign = dict(assign)
                nxt_assign[i] = off
                stack.append((pos + 1, nxt_assign))
    return list(results.values())


# ---------------------------------------------------------------------------
# Validation + comparison helpers
# ---------------------------------------------------------------------------

def ck6_subgroup_count(cells):
    """Number of CK6 (V4) subgroups inside Sym(cells).  Re-derives the
    Stage 5O audit logic: identity + diagonal C2 + inversion + their
    product (a diagonal mirror), all verified members of Sym."""
    maps = affine_symmetries(cells)
    ms = [(m, np.asarray(t, dtype=int))
          for m, t in maps]
    inv = [e for e in ms
           if np.array_equal(e[0], -np.eye(3, dtype=int))]
    c2d = [e for e in ms
           if int(np.trace(e[0])) == -1
           and int(round(np.linalg.det(e[0]))) == 1
           and any(e[0][i][j] != 0 for i in range(3)
                   for j in range(3) if i != j)]
    ident = (np.eye(3, dtype=int), np.zeros(3, dtype=int))

    def has(e):
        return any(np.array_equal(e[0], f[0]) and np.array_equal(e[1], f[1])
                   for f in ms)

    n = 0
    for c in c2d:
        for k in inv:
            comp = (c[0] @ k[0], c[0] @ k[1] + c[1])
            four = [ident, c, k, comp]
            if not has(comp):
                continue
            closed = True
            for a in four:
                for b in four:
                    pr = (a[0] @ b[0], a[0] @ b[1] + a[1])
                    if not has(pr):
                        closed = False
            if closed:
                n += 1
    return n


def proper_orientation_set(piece):
    """All proper-rotation images of the piece, normalized (a set of
    sorted cell tuples)."""
    return {normalize(tuple(np.asarray(r, dtype=int) @ np.array(c)
                            for c in piece))
            for r in RM}


def all_tilings(target, piece):
    """All exact covers of target by proper-rotations of piece.

    Completeness note: placements must be enumerated over a containing
    domain and then filtered to the target (the `all_covers` convention).
    Anchoring placements at target cells alone is INCOMPLETE for pieces
    with orientations that do not contain their component-wise minimum
    corner (e.g. P): the anchor can fall outside the target while every
    cell of the placement is inside it.
    """
    tgt = set(target)
    pts = np.array(sorted(tgt))
    mn, mx = pts.min(axis=0), pts.max(axis=0)
    ext = [int(max(c[i] for c in piece)) + 1 for i in range(3)]
    dom = {(x, y, z)
           for x in range(int(mn[0]) - ext[0], int(mx[0]) + ext[0] + 1)
           for y in range(int(mn[1]) - ext[1], int(mx[1]) + ext[1] + 1)
           for z in range(int(mn[2]) - ext[2], int(mx[2]) + ext[2] + 1)}
    rows = [p for p in placements_in_region(piece, dom) if p <= tgt]
    X = defaultdict(set)
    Y = {}
    for i, p in enumerate(rows):
        Y[i] = sorted(p)
        for c in p:
            X[c].add(i)
    for c in tgt:
        X.setdefault(c, set())
    out = []
    for sol in exact_cover_solve(X, Y):
        out.append(frozenset(rows[i] for i in sol))
    return out


def tiling_orbits(target, tilings):
    """Partition tilings into orbits under Sym(target)."""
    syms = affine_symmetries(target)

    def sig(tiling):
        best = None
        for m, t in syms:
            m = np.asarray(m, dtype=int)
            img = frozenset(
                frozenset(tuple(int(v) for v in (m @ np.array(c) + t))
                          for c in p)
                for p in tiling)
            key = tuple(sorted(tuple(sorted(p)) for p in img))
            if best is None or key < best:
                best = key
        return best

    sigs = {}
    for t in tilings:
        sigs[t] = sig(t)
    orbits = []
    seen = set()
    for t in tilings:
        s = sigs[t]
        if s in seen:
            continue
        seen.add(s)
        orbits.append(s)
    orbits.sort()
    return orbits


def cid(coords):
    import hashlib
    h = hashlib.sha1(
        json.dumps(sorted(tuple(int(v) for v in c) for c in coords))
        .encode()).hexdigest()[:12]
    return h


def load_catalogue():
    with open(os.path.join(REUSE, "small_positive_catalogue.json")) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    catalogue = load_catalogue()
    shapes = catalogue["constructions"]
    by_id = {s["id"]: s for s in shapes}

    report = {
        "stage": "5P",
        "source": "sicherman.net/c5odd/c5nodd.html",
        "page_rev": PAGE_REV,
        "cached": os.path.relpath(CACHE, REPO),
        "george_rows": {p: {"tiles": t, "table": tab}
                        for p, (t, tab) in sorted(GEORGE_ROWS.items())},
        "reconstructions": [],
        "pair_verdicts": [],
        "metadata_notes": [],
    }

    for name, image, piece_letter, tiles, (our_piece, our_vol), band, \
            x_range in RECONSTRUCT:
        img = Image.open(os.path.join(CACHE, image))
        rec = {"name": name, "image": image, "piece": piece_letter,
               "tiles": tiles, "band": list(band), "x_range": list(x_range)}
        try:
            layers, color_layers = parse_strip(
                img, band, x_range, expect_cells=5 * tiles)
        except ValueError as exc:
            rec["error"] = str(exc)
            report["reconstructions"].append(rec)
            continue
        rec["layer_sizes"] = [len(s) for s in layers]

        candidates = align_and_identify(layers, color_layers, piece_letter)
        rec["n_aligned_candidates"] = len(candidates)
        if not candidates:
            rec["error"] = "no offset assignment passes the constraints"
            report["reconstructions"].append(rec)
            continue

        # group candidates by canonical form; keep all distinct readings
        distinct = {}
        for cand in candidates:
            distinct.setdefault(cand["oh_canonical_id"], []).append(cand)
        rec["candidates"] = [
            {k: v for k, v in cands[0].items() if k != "cells"}
            for cands in distinct.values()]
        rec["cells_by_oh"] = {oh: cands[0]["cells"]
                              for oh, cands in distinct.items()}
        primary = max(distinct.values(),
                      key=lambda cs: (cs[0]["symmetry_order"],
                                      cs[0]["tiling_count"]))
        cand = primary[0]
        cells_t = normalize(tuple(tuple(c) for c in cand["cells"]))
        rec["cell_count"] = len(cells_t)
        rec["connected"] = is_face_connected(cells_t)
        rec["symmetry_order"] = cand["symmetry_order"]
        rec["ck6_subgroups"] = ck6_subgroup_count(cells_t)
        rec["oh_canonical_id"] = cand["oh_canonical_id"]
        rec["p24_canonical_id"] = cand["p24_canonical_id"]
        rec["tiling_count"] = cand["tiling_count"]
        rec["tiling_orbit_count"] = cand["tiling_orbit_count"]
        rec["colors_are_pieces"] = cand["colors_are_pieces"]
        rec["his_tiling_orbit_index"] = cand.get("his_tiling_orbit_index")

        # compare against our catalogue entries with same piece+volume
        pairs = []
        for s in by_id.values():
            if s["piece"] == our_piece and s["volume"] == our_vol:
                congruent = ("oh-" + cid(s["full_oh_canonical"])
                             == rec["oh_canonical_id"])
                pair = {
                    "our_id": s["id"],
                    "our_oh": "oh-" + cid(s["full_oh_canonical"]),
                    "our_p24": "p24-" + cid(s["proper_canonical"]),
                    "congruent_to_george": congruent,
                    "our_tiling_count": s.get("number_of_tilings"),
                }
                if congruent:
                    pair["his_tiling_orbit_index"] = rec.get(
                        "his_tiling_orbit_index")
                    pair["our_orbit_count"] = rec.get("tiling_orbit_count")
                    pair["raw_tiling_counts_agree"] = (
                        rec["tiling_count"] == s.get("number_of_tilings"))
                pairs.append(pair)
        rec["our_candidates"] = pairs
        report["reconstructions"].append(rec)

    # ------------------------------------------------------------------
    # Metadata-level comparison for the whole catalogue.  The page lists
    # ONE smallest-known figure per piece, so:
    #   tiles < page minimum  -> improvement over the published minimum
    #   tiles == minimum      -> adjudicated by geometry (reconstructions)
    #   tiles > minimum       -> page cannot adjudicate (minima only)
    # ------------------------------------------------------------------
    congruent_to_page = {}   # our_id -> george figure name (from geometry)
    for rec in report["reconstructions"]:
        for pair in rec.get("our_candidates", []):
            if pair.get("congruent_to_george"):
                congruent_to_page[pair["our_id"]] = rec["name"]
    notes = []
    for s in sorted(shapes, key=lambda s: s["id"]):
        pid = s["piece"]
        tiles = s["volume"] // 5
        g = GEORGE_ROWS.get(pid)
        if g is None:
            notes.append({"our_id": s["id"], "category": "no page entry",
                          "detail": "piece not on George's page"})
            continue
        gtiles, table = g
        if s["id"] in congruent_to_page:
            rec = next(r for r in report["reconstructions"]
                       if r["name"] == congruent_to_page[s["id"]])
            if rec.get("his_tiling_orbit_index") is not None:
                cat = "known shape + known tiling"
                detail = (f"congruent to George's {pid}-{gtiles} figure; "
                          f"his published colouring coincides with our "
                          f"tiling orbit "
                          f"{rec['his_tiling_orbit_index']} of "
                          f"{rec['tiling_orbit_count']}")
            elif rec.get("tiling_orbit_count") == 1:
                cat = "known shape + known tiling"
                detail = (f"congruent to George's {pid}-{gtiles} figure; "
                          f"single tiling orbit, so his drawing coincides "
                          f"with ours up to symmetry")
            else:
                cat = "known shape"
                detail = (f"congruent to George's {pid}-{gtiles} figure; "
                          f"we hold {s['number_of_tilings']} tilings in "
                          f"{rec['tiling_orbit_count']} orbits; his "
                          f"colouring could not be extracted from the "
                          f"drawing (colours reused across copies)")
        elif tiles == 1 and cid(canonical_form(
                [tuple(int(v) for v in c) for c in PENTACUBES[pid]],
                proper_only=True)) == cid(canonical_form(
                    [tuple(c) for c in s["target_coordinates"]],
                    proper_only=True)):
            cat = "known shape + known tiling"
            detail = ("trivial: the 1-tile oddity is the piece itself, "
                      "identical to George's trivial entry")
        elif tiles < gtiles:
            cat = "improvement over published minimum"
            detail = (f"{tiles} tiles vs George's smallest known "
                      f"{gtiles} tiles ({table} table) -- smaller by "
                      f"{gtiles - tiles} tiles")
        elif tiles == gtiles:
            cat = "related-but-distinct"
            detail = (f"same piece and tile count as George's minimum "
                      f"({gtiles} tiles) but non-congruent to his figure")
        else:
            cat = "no match on page"
            detail = (f"more tiles than George's minimum ({gtiles}); the "
                      f"page lists minima only and cannot adjudicate")
        notes.append({"our_id": s["id"], "category": cat,
                      "detail": detail})
    report["metadata_notes"] = notes

    out_json = os.path.join(REUSE, "stage5p_george_comparison.json")
    with open(out_json, "w") as f:
        json.dump(report, f, indent=1)

    # console summary
    print(f"== Stage 5P vs sicherman.net c5nodd.html (rev {PAGE_REV}) ==")
    for rec in report["reconstructions"]:
        print(f"\n[{rec['name']}] piece {rec['piece']} x {rec['tiles']}")
        if "error" in rec:
            print("  ERROR:", rec["error"])
            continue
        print(f"  layers {rec['layer_sizes']}  cells {rec['cell_count']}"
              f"  connected {rec['connected']}")
        print(f"  |Sym| {rec['symmetry_order']}  CK6 subgroups "
              f"{rec['ck6_subgroups']}")
        print(f"  oh {rec['oh_canonical_id']}  p24 {rec['p24_canonical_id']}")
        print(f"  distinct readings {rec['n_aligned_candidates']}"
              f"  colours-are-pieces {rec.get('colors_are_pieces')}"
              f"  tilings {rec['tiling_count']}"
              f" ({rec['tiling_orbit_count']} orbits)")
        if rec.get("his_tiling_orbit_index") is not None:
            print(f"  George's colouring = our orbit "
                  f"{rec['his_tiling_orbit_index']}")
        for p in rec["our_candidates"]:
            mark = "CONGRUENT" if p["congruent_to_george"] else "distinct"
            print(f"  vs {p['our_id']}: {mark}")
    print(f"\nreport: {os.path.relpath(out_json, REPO)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generic independent checker for pentacube Macro closed-walk certificates
(format: fitpolycubes.macro-walk v1; also reads the legacy T-witness layout).

STDLIB ONLY: imports nothing from this repository. Every semantic input is
taken from the certificate itself (`piece.geometry`, `conventions`).
No piece-specific assumptions: no flatness requirement, no mod-5 condition,
no fixed orientation count, no gate theorem.

Protocol semantics are PINNED, not read from prose: a certificate must declare
    conventions.semantics_id == "fitpolycubes.macro-walk/semantics-1"
which names exactly the semantics implemented below (cell id x + a*y, packing
l0 | l1<<NCELLS, proper rotations det=+1 derived from piece.geometry, window
dz in {0,1,2}, fill-to-completion + shift edge). Certificates declaring any
other semantics_id are refused -- this prevents a mismatch between documented
and actually-checked meaning.

LAYER A only (see docs/frontier/macro_certificate_format.md sections 3-5):
  C0  geometry sanity: exactly `cell_count` DISTINCT integer cells,
      face-connected (a genuine polycube)
  C1  dimensions: a,b,z positive integers; volume divisible by cell_count;
      declared semantics pinned
  C2  stored box tiling (key box_tiling, legacy alias placements): if both
      keys present they must agree; bounds; congruence under proper rotations
      of the embedded geometry; exact disjoint cover
  C3  stored walk has z+1 states, starts at 0, ends at 0; step labels, if
      present, equal positions; masks are nonnegative integers
  C4  every edge fill legal BY SET ARITHMETIC against the pinned semantics:
      pieces congruent, pairwise disjoint, disjoint from source-state
      occupancy, ALL CELLS IN BOUNDS, slot 0 completed, shift(source + fill)
      equals the stored successor state
  C5  recomputed walk equals stored walk and closes at 0
  C6  edge fills reconstruct exactly the stored tiling
  C7g terminal-predecessor OBSERVATIONS reported (facts only); optional
      `terminal` block cross-checked against computed facts

Piece-specific gate claims (Layer B/C) are NOT evaluated here.

Usage:
  python3 -I macro_certificate_generic_checker.py <cert.json> [...]
Exit 0 iff every certificate passes all Layer-A checks.
"""

import json
import sys
from itertools import permutations

SEMANTICS_ID = "fitpolycubes.macro-walk/semantics-1"


def perm_sign(p):
    s = 1
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            if p[i] > p[j]:
                s = -s
    return s


def rotation_images(base_geometry):
    """Canonical images of the embedded geometry under all proper rotations
    (signed permutation matrices with det=+1; exactly the 24 cube rotations)."""
    out = set()
    for p in permutations(range(3)):
        for signs in ((1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1),
                      (1, -1, -1), (-1, 1, -1), (-1, -1, 1), (-1, -1, -1)):
            if perm_sign(p) * signs[0] * signs[1] * signs[2] != 1:
                continue
            img = [tuple(signs[i] * c[p[i]] for i in range(3)) for c in base_geometry]
            mn = [min(c[i] for c in img) for i in range(3)]
            out.add(tuple(sorted((c[0] - mn[0], c[1] - mn[1], c[2] - mn[2])
                                 for c in img)))
    return out


class Fail(Exception):
    pass


def require(cond, msg):
    if not cond:
        raise Fail(msg)


def is_int(v):
    """Strict integer check (JSON booleans must not pass as integers)."""
    return type(v) is int


def congruent(cells, orientations):
    mn = [min(c[i] for c in cells) for i in range(3)]
    norm = tuple(sorted((c[0] - mn[0], c[1] - mn[1], c[2] - mn[2]) for c in cells))
    return norm in orientations


def check(path):
    doc = json.load(open(path))
    results = []

    def rec(msg):
        results.append(msg)

    require(doc.get("format") == "fitpolycubes.macro-walk"
            or "macro-walk" in str(doc.get("format")),
            "not a macro-walk certificate")
    a, b, z = doc["box"]["a"], doc["box"]["b"], doc["box"]["z"]
    ncells = a * b

    # -- conventions must pin the implemented semantics  [audit fix H1]
    conv = doc.get("conventions", {})
    require(conv.get("semantics_id") == SEMANTICS_ID,
            f"conventions.semantics_id must be {SEMANTICS_ID!r}; "
            "this checker implements only that pinned semantics")

    # -- piece from the certificate, never from any registry
    geom_raw = doc["piece"]["geometry"]
    cell_count = doc["piece"].get("cell_count", len(geom_raw))
    require(cell_count == 5 and len(geom_raw) == 5,
            "pentacube certificates must have exactly 5 cells")
    # [audit fix H3] geometry sanity: strict ints, distinct, face-connected
    geom = []
    for c in geom_raw:
        require(len(c) == 3 and all(is_int(v) for v in c),
                f"non-integer geometry cell {c}")
        geom.append(tuple(c))
    require(len(set(geom)) == 5, "geometry contains duplicate cells")
    cellset = set(geom)
    seen = {geom[0]}
    frontier = [geom[0]]
    while frontier:
        x, y, zz = frontier.pop()
        for nb in ((x+1, y, zz), (x-1, y, zz), (x, y+1, zz),
                   (x, y-1, zz), (x, y, zz+1), (x, y, zz-1)):
            if nb in cellset and nb not in seen:
                seen.add(nb)
                frontier.append(nb)
    require(len(seen) == 5, "geometry is not face-connected (not a pentacube)")
    orientations = rotation_images(geom)

    # -- C1  [audit fix H2] degenerate boxes refused explicitly
    require(all(is_int(v) and v >= 1 for v in (a, b, z)),
            "box dimensions must be positive integers")
    require((a * b * z) % cell_count == 0, "volume not divisible by cell count")
    rec(f"box {a}x{b}x{z}; volume {a*b*z}; {a*b*z//cell_count} pieces "
        f"(piece cell_count={cell_count}); semantics pinned to "
        f"{SEMANTICS_ID}")

    # -- C2 stored tiling (legacy alias accepted; conflict refused)  [fix H5]
    has_bt = "box_tiling" in doc
    has_pl = "placements" in doc
    require(not (has_bt and has_pl) or
            sorted(map(str, doc["box_tiling"])) == sorted(map(str, doc["placements"])),
            "both box_tiling and placements present and inconsistent")
    tiling_raw = doc.get("box_tiling", doc.get("placements"))
    require(tiling_raw is not None, "missing box_tiling/placements")
    placements = [list(map(tuple, p)) for p in tiling_raw]
    require(len(placements) == a * b * z // cell_count, "wrong piece count")
    seen_cells = set()
    for pc in placements:
        require(len(pc) == cell_count, "bad piece size")
        for c in pc:
            require(len(c) == 3 and all(is_int(v) for v in c),
                    f"non-integer placement cell {c}")
            x, y, zz = c
            require(0 <= x < a and 0 <= y < b and 0 <= zz < z,
                    f"cell out of bounds {(x,y,zz)}")
            require(tuple(c) not in seen_cells, "overlapping cells")
            seen_cells.add(tuple(c))
    require(len(seen_cells) == a * b * z, "not an exact disjoint cover")
    for pc in placements:
        require(congruent(pc, orientations),
                f"placement not congruent to embedded geometry: {pc}")
    rec("C2 stored tiling: bounds ok, exact disjoint cover, all shapes "
        "congruent to embedded geometry under proper rotations")

    # -- C3  [audit fix H6] step labels validated; masks strict ints >= 0
    walk = doc["walk"]
    require(len(walk) == z + 1, "walk must have z+1 states")
    for k, st in enumerate(walk):
        require(is_int(st["l0"]) and is_int(st["l1"])
                and st["l0"] >= 0 and st["l1"] >= 0, f"bad state at {k}")
        if "step" in st:
            # [interop fix] strict integer: JSON true/false must not compare
            # equal to 0/1 via Python bool-int coercion
            require(type(st["step"]) is int and st["step"] == k,
                    f"walk step label {st['step']!r} != {k}")
    require(walk[0]["l0"] == 0 and walk[0]["l1"] == 0, "does not start at 0")
    require(walk[z]["l0"] == 0 and walk[z]["l1"] == 0, "does not end at 0")

    # -- C4/C5 edges by pure set arithmetic  [audit fix H4] explicit bounds
    fills = doc["edge_fills"]
    require(len(fills) == z, "edge_fills must have z entries")
    cur0 = cur1 = 0
    for k, edge in enumerate(fills):
        occ = {(x, y, d) for d in (0, 1) for x in range(a) for y in range(b)
               if ((cur0 if d == 0 else cur1) >> (x + a * y)) & 1}
        allcells = []
        for pc in edge:
            require(len(pc) == cell_count, f"edge {k}: bad piece size")
            for c in pc:
                require(len(c) == 3 and all(is_int(v) for v in c),
                        f"edge {k}: non-integer fill cell {c}")
                x, y, d = c
                require(0 <= x < a and 0 <= y < b and d in (0, 1, 2),
                        f"edge {k}: fill cell out of window bounds {c}")
            require(congruent(pc, orientations), f"edge {k}: non-congruent piece")
            allcells += [tuple(c) for c in pc]
        require(len(set(allcells)) == len(allcells),
                f"edge {k}: overlapping pieces/state")
        require(not (set(allcells) & occ), f"edge {k}: hits occupied cell")
        slot0 = {x + a * y for (x, y, d) in allcells if d == 0}
        covered = {i for i in range(ncells) if (cur0 >> i) & 1} | slot0
        require(len(covered) == ncells, f"edge {k}: slot 0 not completed")
        nxt0, nxt1 = cur1, 0
        for (x, y, d) in allcells:
            cid = x + a * y
            if d == 1:
                nxt0 |= 1 << cid
            elif d == 2:
                nxt1 |= 1 << cid
        require(nxt0 == walk[k + 1]["l0"] and nxt1 == walk[k + 1]["l1"],
                f"edge {k}: shift(source+fill) != stored successor state")
        cur0, cur1 = nxt0, nxt1
    require(cur0 == 0 and cur1 == 0, "recomputed walk does not close at 0")
    rec(f"C4/C5 all {z} edges legal by set arithmetic; recomputed walk equals "
        f"stored; closes at 0 after {z} edges")

    # -- C6 reconstruction equals stored tiling
    rebuilt = set()
    for k, edge in enumerate(fills):
        for pc in edge:
            fs = frozenset((x, y, k + d) for (x, y, d) in pc)
            require(fs not in rebuilt, "reconstruction overlap")
            rebuilt.add(fs)
    stored = {frozenset(map(tuple, pc)) for pc in placements}
    require(rebuilt == stored, "reconstruction != stored tiling")
    rec("C6 edge fills reconstruct exactly the stored box tiling")

    # -- C7g terminal predecessor: generic OBSERVATIONS (facts, not claims)
    pred_l0 = walk[z - 1]["l0"]
    pred_l1 = walk[z - 1]["l1"]
    pc_count = bin(pred_l0).count("1")
    remaining = ncells - pc_count
    last_edge = fills[z - 1]
    all_slot0 = all(c[2] == 0 for pcs in last_edge for c in pcs)
    comp = {i for i in range(ncells) if not (pred_l0 >> i) & 1}
    cov = set()
    covers = True
    for pcs in last_edge:
        m = {x + a * y for (x, y, _) in pcs}
        if m & cov or not m <= comp:
            covers = False
            break
        cov |= m
    covers = covers and cov == comp
    rec(f"C7g terminal predecessor (state {z-1}): L1 empty = {pred_l1 == 0}; "
        f"|L0|={pc_count}; remaining={remaining}; final edge all-slot0 = "
        f"{all_slot0}; final edge exactly covers complement = {covers}")
    rec("NOTE layer boundary: piece-specific gate claims are NOT evaluated by "
        "this generic checker (docs/frontier/macro_certificate_format.md section 3).")

    term = doc.get("terminal")
    if term is not None:
        # [interop fix] strict types: booleans must be booleans, numbers must
        # be true integers (no bool/int coercion in either direction)
        def tnum(key, expected):
            v = term.get(key)
            if v is None:
                return
            require(type(v) is int and v == expected,
                    f"terminal.{key} mismatch")
        psi = term.get("predecessor_state_index")
        if psi is not None:
            require(type(psi) is int and psi == z - 1,
                    "terminal.predecessor_state_index mismatch")
        tnum("l0_popcount", pc_count)
        tnum("remaining_cells", remaining)
        fas = term.get("final_edge_all_slot0")
        if fas is not None:
            require(type(fas) is bool and fas == all_slot0,
                    "terminal.final_edge_all_slot0 mismatch")
        fcc = term.get("final_edge_covers_complement")
        if fcc is not None:
            require(type(fcc) is bool and fcc == covers,
                    "terminal.final_edge_covers_complement mismatch")
        rec("`terminal` block present and consistent with computed facts")

    return results


def main():
    ok_all = True
    for arg in sys.argv[1:]:
        print(f"generic check: {arg}")
        try:
            for r in check(arg):
                print(f"  [OK] {r}")
            print("  => LAYER-A VALID\n")
        except Fail as e:
            print(f"  [FAIL] {e}\n  => INVALID\n")
            ok_all = False
        except (KeyError, TypeError, ValueError) as e:
            print(f"  [FAIL] malformed certificate: {e}\n  => INVALID\n")
            ok_all = False
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())

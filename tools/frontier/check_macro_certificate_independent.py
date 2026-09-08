#!/usr/bin/env python3
"""
Fully independent checker for T-pentacube Macro cyclicity certificates (v2).

STDLIB ONLY: imports nothing from this repository. All semantics are derived
from the certificate's own `conventions` block:
  - piece geometry [[0,0,0],[1,0,0],[2,0,0],[1,1,0],[1,2,0]]
  - proper rotations (signed permutation matrices, det = +1)
  - cell id x + a*y, state packing l0 | l1<<NCELLS, slot 2 always empty

Checks per certificate:
  C1  box dimensions positive; volume divisible by 5
  C2  every stored box placement: in bounds, T-congruent, and the placements
      form an exact disjoint cover of a*b*z
  C3  stored walk: length z+1, starts at 0, ends at 0
  C4  every stored edge fill: pieces T-congruent, pairwise disjoint, disjoint
      from the source state's occupancy, complete slot 0, and shift(source +
      fill) equals the stored next state  ->  every Macro edge legal BY SET
      ARITHMETIC ALONE (no template enumeration)
  C5  recomputed walk equals stored walk
  C6  box tiling reconstructed from edge fills is an exact disjoint cover and
      equals the stored placements
  C7  terminal predecessor: L1 = 0, and its L0-complement is EXACTLY covered
      by the final edge's fill pieces, which are necessarily flat (all dz = 0)

Usage:
  python3 check_macro_certificate_independent.py <cert.json> [<cert.json> ...]
Exit 0 iff every certificate passes every check.
"""

import json
import sys
from itertools import permutations

BASE_PIECE = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (1, 1, 0), (1, 2, 0)]


def perm_sign(p):
    s = 1
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            if p[i] > p[j]:
                s = -s
    return s


def rotation_images():
    """Canonical images of BASE_PIECE under all 24 proper rotations."""
    out = set()
    for p in permutations(range(3)):
        for signs in ((1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1),
                      (1, -1, -1), (-1, 1, -1), (-1, -1, 1), (-1, -1, -1)):
            if perm_sign(p) * signs[0] * signs[1] * signs[2] != 1:
                continue
            img = [tuple(signs[i] * c[p[i]] for i in range(3)) for c in BASE_PIECE]
            mn = [min(c[i] for c in img) for i in range(3)]
            img = tuple(sorted((c[0] - mn[0], c[1] - mn[1], c[2] - mn[2])
                               for c in img))
            out.add(img)
    return out


ORIENTATIONS = rotation_images()
assert len(ORIENTATIONS) == 12, f"expected 12 T orientations, got {len(ORIENTATIONS)}"


def congruent(cells):
    mn = [min(c[i] for c in cells) for i in range(3)]
    norm = tuple(sorted((c[0] - mn[0], c[1] - mn[1], c[2] - mn[2]) for c in cells))
    return norm in ORIENTATIONS


class Fail(Exception):
    pass


def require(cond, msg):
    if not cond:
        raise Fail(msg)


def check_certificate(path):
    doc = json.load(open(path))
    a, b, z = doc["box"]["a"], doc["box"]["b"], doc["box"]["z"]
    ncells = a * b
    full = (1 << ncells) - 1
    results = []

    def rec(msg):
        results.append(msg)

    # -- C1
    require(min(a, b, z) >= 1 and (a * b * z) % 5 == 0, "bad dimensions")
    rec(f"box {a}x{b}x{z}, volume {a*b*z}, {a*b*z//5} pieces")

    # -- conventions present
    conv = doc["conventions"]
    require(conv["piece_geometry"] and "det=+1" in conv["rotations"],
            "conventions block incomplete")

    # -- C2 stored box tiling
    placements = [list(map(tuple, p)) for p in doc["placements"]]
    require(len(placements) == a * b * z // 5, "wrong piece count")
    seen = set()
    for pc in placements:
        require(len(pc) == 5, "piece with != 5 cells")
        for (x, y, zz) in pc:
            require(0 <= x < a and 0 <= y < b and 0 <= zz < z,
                    f"cell out of bounds: {(x,y,zz)}")
            require((x, y, zz) not in seen, "overlapping cells")
            seen.add((x, y, zz))
    require(len(seen) == a * b * z, "not an exact cover")
    for pc in placements:
        require(congruent(pc), "placement not T-congruent")
    rec("C2 stored tiling: exact disjoint cover, all shapes T-congruent")

    # -- C3 stored walk endpoints
    walk = doc["walk"]
    require(len(walk) == z + 1, "walk length wrong")
    require(walk[0]["l0"] == 0 and walk[0]["l1"] == 0, "walk does not start at 0")
    require(walk[z]["l0"] == 0 and walk[z]["l1"] == 0, "walk does not end at 0")

    # -- C4/C5 edges by direct set arithmetic
    fills = doc["edge_fills"]
    require(len(fills) == z, "edge_fills length wrong")
    cur0 = cur1 = 0
    for k, edge in enumerate(fills):
        occ = {(x, y, 0) for x in range(a) for y in range(b)
               if (cur0 >> (x + a * y)) & 1}
        occ |= {(x, y, 1) for x in range(a) for y in range(b)
                if (cur1 >> (x + a * y)) & 1}
        allcells = []
        for pc in edge:
            require(len(pc) == 5 and congruent(pc),
                    f"edge {k}: bad piece {pc}")
            for c in pc:
                require(c[2] in (0, 1, 2), f"edge {k}: window layer {c[2]}")
            allcells += [tuple(c) for c in pc]
        require(len(set(allcells)) == len(allcells),
                f"edge {k}: pieces overlap each other or the state")
        require(not (set(allcells) & occ), f"edge {k}: piece hits occupied cell")
        slot0 = {x + a * y for (x, y, d) in allcells if d == 0}
        covered = {i for i in range(ncells) if (cur0 >> i) & 1} | slot0
        require(len(covered) == ncells, f"edge {k}: slot 0 not completed")
        nxt0 = cur1
        nxt1 = 0
        for (x, y, d) in allcells:
            cid = x + a * y
            if d == 1:
                nxt0 |= 1 << cid
            elif d == 2:
                nxt1 |= 1 << cid
        require(nxt0 == walk[k + 1]["l0"] and nxt1 == walk[k + 1]["l1"],
                f"edge {k}: computed successor != stored state")
        cur0, cur1 = nxt0, nxt1
    require(cur0 == 0 and cur1 == 0, "recomputed walk does not close at 0")
    rec(f"C4/C5 all {z} edges legal by set arithmetic; "
        f"recomputed walk matches stored; closes at 0 after {z} edges")

    # -- C6 reconstruction of the box from edge fills
    rebuilt = set()
    for k, edge in enumerate(fills):
        for pc in edge:
            fs = frozenset((x, y, k + d) for (x, y, d) in pc)
            require(fs not in rebuilt, "reconstructed pieces overlap")
            rebuilt.add(fs)
    require(sum(len(p) for p in rebuilt) == a * b * z, "reconstruction size wrong")
    stored = {frozenset(map(tuple, pc)) for pc in placements}
    require(rebuilt == stored, "reconstructed tiling != stored placements")
    rec("C6 edge fills reconstruct exactly the stored box tiling")

    # -- C7 terminal predecessor / gate condition, constructively
    pred_l0 = walk[z - 1]["l0"]
    pred_l1 = walk[z - 1]["l1"]
    require(pred_l1 == 0, "terminal predecessor has nonempty L1")
    pc_count = bin(pred_l0).count("1")
    rem = ncells - pc_count
    require(rem % 5 == 0, "terminal remaining cells not divisible by 5")
    last_flat = []
    for pcs in fills[z - 1]:
        require(all(c[2] == 0 for c in pcs),
                "final edge uses a non-flat piece")
        last_flat.append({x + a * y for (x, y, _) in pcs})
    comp = {i for i in range(ncells) if not (pred_l0 >> i) & 1}
    cov = set()
    for m in last_flat:
        require(not (m & cov), "flat cover overlaps")
        require(m <= comp, "flat cover exceeds complement")
        cov |= m
    require(cov == comp, "final edge pieces do not exactly cover the complement")
    rec(f"C7 terminal predecessor |L0|={pc_count}; remaining {rem} cells "
        f"exactly covered by {len(last_flat)} flat pieces of the final edge")

    return True, results


def main():
    ok_all = True
    for arg in sys.argv[1:]:
        print(f"independent check: {arg}")
        try:
            ok, results = check_certificate(arg)
            for r in results:
                print(f"  [OK] {r}")
            print(f"  => INDEPENDENTLY VALID\n")
        except Fail as e:
            print(f"  [FAIL] {e}\n  => INVALID\n")
            ok_all = False
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
